"""Concurrent, resumable model runner shared by P1 and P2. Stdlib only.

Contract
- A run directory holds one frozen config. The journal header binds the config hash; resuming with a
  different config is refused, so settings never change mid-run. One runner per directory (lock file).
- A task is (key, model, fn). fn(call, skip) runs the task's stages: call(stage, messages, tools=None)
  returns a journaled result; skip(stage, reason) journals an adapter-declared skip (e.g. P1 branches
  after a turn-1 failure). Every result is appended and fsynced before fn sees it. On resume, journaled
  stages are replayed from disk with no API call, so dependent stages continue exactly.
- Terminal results are journaled once and never retried: "ok" (truncation flagged), "failed"
  (non-retryable HTTP error, empty choices, or the served provider/model differs from the pin), "skipped".
- Transient errors (429, 5xx, timeouts, connection) are retried with backoff. If retries run out the task
  is aborted, NOT journaled, and runs again on resume. halt_transient_aborts aborts halt the run, as does a
  terminal-failure rate above halt_error_rate over the last 50 results (once 20 exist).
- Concurrency per model starts at concurrency_start (set it to the maximum: start high, back off): halved
  on a 429 and after 4 infrastructure errors in a row (timeout, connection, 5xx, damaged envelope); grows
  +25% only after limit/2 straight definitive responses, capped at concurrency_max. A 429 from two or more
  models within 10 s is treated as the shared account limit and halves every model. Once stopping, a
  request waiting for a slot is never dispatched; calls already in flight finish (stop_info in the summary
  records how many and their reserved worst case).
- Spend is tracked, never used to cut a design short. spend_cap_usd null (the default in our configs) = no
  cap: the OpenRouter balance is the only stop, and running out (HTTP 402) halts with nothing journaled,
  so a top-up plus --resume continues the identical design. A numeric cap is optional: run() then refuses
  to start unless it covers spent + the worst case of every remaining planned
  call, ONE billed attempt each (input bounded by UTF-8 bytes + template overhead, output by max_tokens).
  Each attempt writes an intent with that reservation and settles to the billed cost after. An HTTP error
  response (never billed) voids its intent. An attempt whose billing is unknown (timeout, dropped
  connection, damaged envelope, provider error inside a 200) is counted as spent at its reservation
  immediately and stays so on resume. Retries of billed-unknown attempts are not in the pre-flight bound:
  the in-run cap check halts the run if they accumulate (runaway guard), and the summary reports them.
  Resume guarantees no duplicate COUNTED observation; an ambiguous network failure can still cause a
  duplicate BILLED attempt, since the API offers no idempotency key.
- Order: tasks are shuffled with the config seed (execution order randomized within each model).
- Routing (per "Not Pinning Your OpenRouter Provider Might Invalidate Your Research", LessWrong 2026):
  endpoint pinned by tag, quantization pinned, allow_fallbacks=false, require_parameters=true,
  data_collection=deny. The served provider name and model are journaled with every result and checked
  against provider_name and slug; a mismatch is a terminal failure. A provider outage halts the run;
  switching provider means a new config, hence a new run directory, never a silent substitution.
- The API key comes only from OPENROUTER_API_KEY and is never written anywhere.
- Resume / pause / status. A run is (config, manifest); the manifest lists every planned call key and the
  design metadata, is written to manifest.json at creation, and its hash sits in the journal header.
  A new run needs an empty directory; resume=True (--resume) needs an existing run with identical config
  and manifest hashes, and run() checks the planned calls equal the manifest: resume continues the same
  experiment, never a new one. Any design or settings change is a separately versioned run.
  Pause: `touch <run_dir>/PAUSE` (or Ctrl-C) stops scheduling; in-flight calls finish and are journaled.
  An explicit resume removes PAUSE. Every start / resume / end is a journaled session record.
  status(run_dir) is a read-only report: per-model counts, calls pending, spend, sessions.
"""
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

RUN_KEYS = {"run_id", "allow_live", "endpoint", "spend_cap_usd", "seed", "timeout_s", "max_retries",
            "halt_error_rate", "halt_transient_aborts", "models"}
MODEL_KEYS = {"slug", "provider", "provider_name", "quantization", "params", "price_in_per_m", "price_out_per_m",
              "concurrency_start", "concurrency_max"}
TRANSIENT = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}
ACCOUNT = {401, 402, 403}  # auth / credit / permission: infrastructure, never a model outcome -> halt, no journal


class Halt(Exception):
    pass


class Deferred(Exception):
    """A shared stage this task depends on was aborted by the task that owned it; this task runs on resume."""


class Transient(Exception):
    def __init__(self, msg, retry_after=None, billed_unknown=False):
        super().__init__(msg)
        self.retry_after, self.billed_unknown = retry_after, billed_unknown


def validate_config(cfg):
    if set(cfg) != RUN_KEYS:
        raise ValueError(f"config keys must be exactly {sorted(RUN_KEYS)}; diff {sorted(set(cfg) ^ RUN_KEYS)}")
    for name, m in cfg["models"].items():
        if set(m) != MODEL_KEYS:
            raise ValueError(f"model {name}: keys must be exactly {sorted(MODEL_KEYS)}")
        if "max_tokens" not in m["params"] or {"model", "messages", "provider", "tools"} & set(m["params"]):
            raise ValueError(f"model {name}: params needs max_tokens and must not set model/messages/provider/tools")
        if not 1 <= m["concurrency_start"] <= m["concurrency_max"]:
            raise ValueError(f"model {name}: need 1 <= concurrency_start <= concurrency_max")
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def http_transport(url, body, timeout):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise Halt("OPENROUTER_API_KEY is not set")
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw), r.headers.get("Retry-After")
            except ValueError:  # damaged API envelope (not model JSON): retry, billing unresolved
                return r.status, {"_malformed_envelope": True, "raw_prefix": raw[:200].decode("utf-8", "replace")}, None
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read())
        except Exception:
            payload = {"error": str(e)}
        return e.code, payload, e.headers.get("Retry-After")


def dry_transport_for(cfg):
    """Offline stand-in that answers as the pinned endpoint would; no network call, zero cost."""
    names = {m["slug"]: m["provider_name"] for m in cfg["models"].values()}

    def t(url, body, timeout):
        return 200, {"provider": names[body["model"]], "model": body["model"],
                     "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "{}"}}],
                     "usage": {"prompt_tokens": 100, "completion_tokens": 10, "cost": 0.0}}, None
    return t


class Limiter:
    def __init__(self, start, cap):
        self.limit, self.cap, self.active, self.streak, self.errors = start, cap, 0, 0, 0
        self.cv = threading.Condition(threading.RLock())

    def acquire(self):
        with self.cv:
            while self.active >= self.limit:
                self.cv.wait()
            self.active += 1

    def release(self, outcome):
        """outcome: "ok" (a definitive HTTP response), "throttled" (429) or "error" (timeout, connection, 5xx,
        damaged envelope). Capacity grows only after real successes; 429 halves it; 4 errors in a row halve it."""
        with self.cv:
            self.active -= 1
            if outcome == "ok":
                self.errors = 0
                self.streak += 1  # +25% after limit/2 straight successes, up to cap
                if self.streak >= max(1, self.limit // 2) and self.limit < self.cap:
                    self.limit, self.streak = min(self.cap, self.limit + max(1, self.limit // 4)), 0
            elif outcome == "throttled":
                self.halve()
            else:
                self.streak, self.errors = 0, self.errors + 1
                if self.errors >= 4:
                    self.halve()
            self.cv.notify_all()

    def cancel(self):
        """Give back a slot that was never used for a request (no effect on the limit)."""
        with self.cv:
            self.active -= 1
            self.cv.notify_all()

    def halve(self):
        with self.cv:
            self.limit, self.streak, self.errors = max(1, self.limit // 2), 0, 0
            self.cv.notify_all()


class Runner:
    backoff = 1.0  # seconds scale for retry waits (tests set 0)
    progress_every = 10.0  # seconds between progress lines on stderr; 0 disables

    def __init__(self, run_dir, cfg, manifest, transport=None, resume=False):
        """manifest: {"planned_keys": [...], ...design metadata}. A new run needs an empty run_dir; resume=True
        needs an existing run whose config AND manifest hashes match exactly (same experiment, never a new one)."""
        self.cfg, self.dir, self.manifest = cfg, run_dir, manifest
        self.hash = validate_config(cfg)
        self.mhash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        exists = os.path.exists(os.path.join(run_dir, "journal.jsonl"))
        if resume and not exists:
            raise Halt(f"--resume: no run in {run_dir}")
        if not resume and exists:
            raise Halt(f"{run_dir} already holds a run: pass resume=True (--resume) to continue it")
        if transport is None:
            if not cfg["allow_live"]:
                raise Halt("allow_live is false: pass dry_transport_for(cfg) for an offline run")
            transport = http_transport
        self.transport = transport
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.done, self.spent, self.reserved, self.aborts, self.recent = {}, 0.0, 0.0, 0, []
        self.inflight, self.unsettled_prior, self.cooldown_until, self.account_throttles = {}, 0.0, 0.0, 0
        self.paused, self.planned, self.unsettled, self.stop_info, self.last429 = False, [], 0.0, None, {}
        self.limiters = {n: Limiter(m["concurrency_start"], m["concurrency_max"]) for n, m in cfg["models"].items()}
        os.makedirs(run_dir, exist_ok=True)
        self._lock_dir()
        self.path = os.path.join(run_dir, "journal.jsonl")
        self.pausefile = os.path.join(run_dir, "PAUSE")
        self._open()
        if resume and os.path.exists(self.pausefile):
            os.remove(self.pausefile)  # an explicit resume lifts an intentional pause
        self._write({"type": "session", "event": "resume" if resume else "start", "pid": os.getpid(),
                     "done": len(self.done), "spent_usd": self.spent, "t": time.time()})

    def _lock_dir(self):
        self.lockfile = os.path.join(self.dir, "run.lock")
        try:
            fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                pid = int(open(self.lockfile).read() or 0)
                os.kill(pid, 0)
                raise Halt(f"another runner (pid {pid}) holds {self.dir}")
            except (ValueError, ProcessLookupError):
                os.remove(self.lockfile)  # stale lock from a dead process
                fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)

    def close(self):
        f = getattr(self, "f", None)
        if f and not f.closed:
            f.close()
        if os.path.exists(self.lockfile):
            os.remove(self.lockfile)

    # ---- journal -------------------------------------------------------------------------------
    def _open(self):
        intents, fresh = {}, not os.path.exists(self.path) or os.path.getsize(self.path) == 0
        if not fresh:
            with open(self.path) as f:
                lines = [json.loads(x) for x in f if x.strip()]
            h = lines[0]
            if h.get("type") != "header" or h["config_sha256"] != self.hash or h.get("manifest_sha256") != self.mhash:
                self.close()
                raise Halt("run directory belongs to a different config or run matrix; a changed design is a "
                           "new, separately versioned run in a new directory")
            for r in lines[1:]:
                if r["type"] == "intent":
                    intents[r["iid"]] = r["reserve_usd"]
                elif r["type"] in ("result", "void"):
                    intents.pop(r.get("iid"), None)
                    if r["type"] == "result":
                        self.done[r["key"]] = r
                        self.spent += r.get("cost_usd") or 0.0
            self.unsettled_prior = sum(intents.values())
            self.spent += self.unsettled_prior  # possibly billed, never settled: count conservatively
        self.f = open(self.path, "a")
        if fresh:
            with open(os.path.join(self.dir, "manifest.json"), "w") as mf:
                json.dump(self.manifest, mf, indent=1, sort_keys=True)
            self._write({"type": "header", "config_sha256": self.hash, "config": self.cfg,
                         "manifest_sha256": self.mhash, "t": time.time()})

    def _write(self, rec):
        self.f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.f.flush()
        os.fsync(self.f.fileno())

    # ---- one stage -----------------------------------------------------------------------------
    def _body(self, model, messages, tools, tool_choice=None):
        m = self.cfg["models"][model]
        body = dict(m["params"], model=m["slug"], messages=messages, usage={"include": True},
                    provider={"order": [m["provider"]], "allow_fallbacks": False, "require_parameters": True,
                              "quantizations": [m["quantization"]], "data_collection": "deny"})
        if tools:
            body["tools"] = tools
            if tool_choice is not None:
                body["tool_choice"] = tool_choice
        return body

    def _reserve(self, model, body):
        m = self.cfg["models"][model]
        # Upper bound: a byte-level BPE token covers >= 1 UTF-8 byte, plus 64 template tokens per message/tool.
        tokens_in = (len(json.dumps(body["messages"], ensure_ascii=False).encode()) + len(json.dumps(body.get("tools") or []).encode())
                     + 64 * (len(body["messages"]) + len(body.get("tools") or [])))
        return (tokens_in * m["price_in_per_m"] + m["params"]["max_tokens"] * m["price_out_per_m"]) / 1e6

    def _halt(self, reason):
        """Set the stop flag once and record what was in flight then (those calls still finish and may bill)."""
        if not self.stop.is_set():
            self.stop_info = {"reason": reason, "in_flight": sum(l.active for l in self.limiters.values()),
                              "in_flight_reserved_usd": round(self.reserved, 6), "t": time.time()}
        self.stop.set()

    def _account_429(self, model, retry_after=None):
        """A 429 from two or more models within 10 s is treated as the shared account limit: every model halves
        its concurrency AND no model dispatches until a shared cooldown ends (Retry-After if given, else 5 s)."""
        now = time.time()
        with self.lock:
            self.last429[model] = now
            shared = sum(now - t < 10 for t in self.last429.values()) >= 2
            if shared:
                self.last429.clear()
                try:
                    wait = max(5.0, float(retry_after)) if retry_after else 5.0
                except ValueError:
                    wait = 5.0
                self.cooldown_until = max(self.cooldown_until, now + min(60.0, wait))
                self.account_throttles += 1
        if shared:
            for lim in self.limiters.values():
                lim.halve()

    def _wait_cooldown(self):
        while self.backoff and time.time() < self.cooldown_until and not self.stop.is_set():
            time.sleep(min(1.0, self.cooldown_until - time.time()))

    def _result(self, key, model, status, iid=None, **kw):
        rec = dict(type="result", key=key, model=model, status=status, iid=iid, t=time.time(), **kw)
        with self.lock:
            self._write(rec)
            self.done[key] = rec
            self.spent += rec.get("cost_usd") or 0.0
            if status != "skipped":
                self.recent = (self.recent + [status == "failed"])[-50:]
                if len(self.recent) >= 20 and sum(self.recent) / len(self.recent) > self.cfg["halt_error_rate"]:
                    self._halt("terminal-failure rate above halt_error_rate")
        return rec

    def call(self, key, model, messages, tools=None, tool_choice=None):
        """One stage. Concurrent calls with the same key (e.g. P1 branches sharing turn 1) send ONE request:
        the first caller owns it, the others wait for its journaled result."""
        if key in self.done:
            return self.done[key]
        with self.lock:
            if key in self.done:
                return self.done[key]
            ev = self.inflight.get(key)
            owner = ev is None
            if owner:
                ev = self.inflight[key] = threading.Event()
        if not owner:
            ev.wait()
            if key in self.done:
                return self.done[key]
            raise Deferred(key)
        try:
            return self._call(key, model, messages, tools, tool_choice)
        finally:
            with self.lock:
                self.inflight.pop(key, None)
            ev.set()

    def _call(self, key, model, messages, tools, tool_choice):
        if os.path.exists(self.pausefile):
            self.paused = True
            self._halt("PAUSE file")
        if self.stop.is_set():
            raise Halt("stopping")
        body = self._body(model, messages, tools, tool_choice)
        req_sha = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        lim = self.limiters[model]
        for attempt in range(self.cfg["max_retries"] + 1):
            reserve, iid = self._reserve(model, body), f"{key}#{attempt}#{time.time_ns()}"
            with self.lock:
                cap = self.cfg["spend_cap_usd"]
                if cap is not None and self.spent + self.reserved + reserve > cap:
                    self._halt("spend cap reached (runaway guard)")
                    raise Halt("spend cap reached")
                self.reserved += reserve
                self._write({"type": "intent", "iid": iid, "key": key, "reserve_usd": reserve, "t": time.time()})
            lim.acquire()
            self._wait_cooldown()  # shared account cooldown applies to every model
            if self.stop.is_set():  # re-check after waiting for a slot: nothing is dispatched once stopping
                with self.lock:
                    self._write({"type": "void", "iid": iid, "key": key, "t": time.time(), "why": "not sent"})
                    self.reserved -= reserve
                lim.cancel()
                raise Halt("stopping")
            status, outcome, billed_unknown, retry_after = None, "error", True, None
            try:
                status, resp, retry_after = self.transport(self.cfg["endpoint"], body, self.cfg["timeout_s"])
                if status in ACCOUNT:
                    billed_unknown, outcome = False, "ok"
                    with self.lock:
                        self._write({"type": "void", "iid": iid, "key": key, "t": time.time()})
                        self._halt(f"HTTP {status}")
                    raise Halt(f"HTTP {status} (auth/credit): run halted with nothing journaled; fix, then --resume")
                if status in TRANSIENT:
                    billed_unknown = False  # an HTTP error response is not billed
                    outcome = "throttled" if status == 429 else "error"
                    raise Transient(f"HTTP {status}", retry_after)
                if resp.get("_malformed_envelope"):
                    raise Transient(f"HTTP {status} with a damaged response envelope")  # generation may have billed
                if status == 200 and (resp.get("error") or not resp.get("choices")
                                      or (resp["choices"][0] or {}).get("finish_reason") == "error"):
                    raise Transient("provider error inside HTTP 200 body")  # may have billed partially
                outcome, billed_unknown = "ok", False
                return self._settle(key, model, iid, req_sha, status, resp, body)
            except (Transient, TimeoutError, ConnectionError, OSError) as e:
                with self.lock:
                    self._write({"type": "attempt_error", "iid": iid, "key": key, "http_status": status,
                                 "error": str(e)[:300], "billed_unknown": billed_unknown, "t": time.time()})
                    if billed_unknown:
                        self.unsettled += reserve  # stays counted as spent now, exactly as on resume
                        self.spent += reserve
                    else:
                        self._write({"type": "void", "iid": iid, "key": key, "t": time.time()})
                if attempt == self.cfg["max_retries"] or self.stop.is_set():
                    raise Transient(str(e), billed_unknown=billed_unknown) from e
                ra = getattr(e, "retry_after", None)
                wait = float(ra) if ra and str(ra).replace(".", "", 1).isdigit() else 2 ** attempt
                time.sleep(min(60.0, wait) * self.backoff * (0.5 + random.random()))
            finally:
                lim.release(outcome)
                if outcome == "throttled":
                    self._account_429(model, retry_after)
                with self.lock:
                    self.reserved -= reserve

    def _settle(self, key, model, iid, req_sha, status, resp, body=None):
        m = self.cfg["models"][model]
        usage = resp.get("usage") or {}
        cost, unresolved = usage.get("cost"), False
        if cost is None and "prompt_tokens" in usage and "completion_tokens" in usage:
            cost = (usage["prompt_tokens"] * m["price_in_per_m"] + usage["completion_tokens"] * m["price_out_per_m"]) / 1e6
        if cost is None:  # no billing evidence: recorded as unknown (None), never as $0
            unresolved = True
        sent = {k: v for k, v in (body or {}).items() if k not in ("messages", "tools")}  # exact settings sent
        if body and body.get("tools"):
            sent["tools"] = [t["function"]["name"] for t in body["tools"]]
        common = dict(iid=iid, request_sha256=req_sha, request_params=sent, http_status=status, response=resp, usage=usage,
                      cost_usd=cost, billing_unresolved=unresolved,
                      served_provider=resp.get("provider"), served_model=resp.get("model"))
        if status != 200 or not resp.get("choices"):
            return self._result(key, model, "failed", error=f"HTTP {status}", **common)
        if resp.get("provider") != m["provider_name"] or not str(resp.get("model", "")).startswith(m["slug"]):
            return self._result(key, model, "failed", error="served provider/model differs from pin", **common)
        ch = resp["choices"][0]
        msg = ch.get("message") or {}
        reasoning = msg.get("reasoning") or msg.get("reasoning_content") or msg.get("reasoning_details")
        return self._result(key, model, "ok", text=msg.get("content") or "", tool_calls=msg.get("tool_calls"),
                            reasoning_returned=bool(reasoning),
                            message=msg, truncated=ch.get("finish_reason") == "length", **common)

    def skip(self, key, model, reason):
        if key in self.done:
            return self.done[key]
        return self._result(key, model, "skipped", error=reason, cost_usd=0.0)

    # ---- tasks ---------------------------------------------------------------------------------
    def worst_case_usd(self, planned):
        """Worst-case cost of every planned call not yet journaled. planned: [(full_key, model, messages)],
        one entry per call the frozen design can make (P1: include every possible lookup continuation)."""
        return sum(self._reserve(p[1], self._body(p[1], p[2], p[3] if len(p) > 3 else None))
                   for p in planned if p[0] not in self.done)

    @staticmethod
    def _raise_fd_limit(need):
        """Sockets are file descriptors; macOS shells default to 256, far below 4 x 256 in flight."""
        try:
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            want = need if hard == resource.RLIM_INFINITY else min(need, hard)
            if soft != resource.RLIM_INFINITY and soft < want:
                resource.setrlimit(resource.RLIMIT_NOFILE, (want, hard))
        except (ImportError, ValueError, OSError):
            pass

    def run(self, tasks, planned):
        """tasks: iterable of (task_key, model, fn); planned: see worst_case_usd. Writes summary.json.

        Budget never truncates a design: the run refuses to START unless spend_cap_usd covers the money
        already spent plus the worst case of everything remaining. The in-run cap check then only fires on
        a runaway fault (retry storm, price change), never as a planned stopping rule."""
        if sorted(p[0] for p in planned) != sorted(self.manifest["planned_keys"]):
            self.close()
            raise Halt("planned calls differ from the run's frozen manifest; a changed design is a new run")
        self.planned, self.paused = planned, False
        need = self.spent + self.worst_case_usd(planned) if self.cfg["spend_cap_usd"] is not None else 0
        if self.cfg["spend_cap_usd"] is not None and need > self.cfg["spend_cap_usd"]:
            self.close()
            raise Halt(f"spend_cap_usd {self.cfg['spend_cap_usd']} < worst case for the full design {need:.2f}; "
                       "raise the cap or shrink the design BEFORE starting")
        tasks = list(tasks)
        random.Random(self.cfg["seed"]).shuffle(tasks)
        state = {"finished": 0, "aborted": 0}

        def one(task):
            tkey, model, fn = task
            if self.stop.is_set():
                return
            try:
                fn(lambda stage, messages, tools=None, tool_choice=None:
                   self.call(f"{tkey}|{stage}", model, messages, tools, tool_choice),
                   lambda stage, reason: self.skip(f"{tkey}|{stage}", model, reason))
                with self.lock:
                    state["finished"] += 1
            except Transient:
                with self.lock:
                    state["aborted"] += 1
                    self.aborts += 1
                    if self.aborts >= self.cfg["halt_transient_aborts"]:
                        self._halt("too many tasks aborted on transient errors")
            except (Halt, Deferred):
                pass

        t0, total = time.time(), len(planned)
        start_done = sum(p[0] in self.done for p in planned)
        ticker_stop = threading.Event()

        def ticker():  # one progress line every `progress_every` seconds, to stderr
            while not ticker_stop.wait(self.progress_every):
                d = sum(p[0] in self.done for p in planned)
                rate = (d - start_done) / max(1e-9, time.time() - t0)
                eta = (total - d) / rate if rate > 0 else float("inf")
                conc = " ".join(f"{n}={lim.active}/{lim.limit}" for n, lim in self.limiters.items())
                print(f"[{time.strftime('%H:%M:%S')}] {d}/{total} calls ({100 * d / total:.0f}%) | {rate:.1f}/s | "
                      f"ETA {eta / 60:.1f} min | ${self.spent:.2f} | in flight {conc}"
                      + (" | STOPPING" if self.stop.is_set() else ""), file=sys.stderr, flush=True)
        if self.progress_every:
            threading.Thread(target=ticker, daemon=True).start()
        workers = sum(m["concurrency_max"] for m in self.cfg["models"].values())
        self._raise_fd_limit(4 * workers + 256)
        ex = ThreadPoolExecutor(max_workers=workers)
        try:
            futures = [ex.submit(one, t) for t in tasks]
            for fu in futures:
                fu.result()
        except KeyboardInterrupt:
            self._halt("Ctrl-C")
            ex.shutdown(wait=True, cancel_futures=True)
            raise
        finally:
            ex.shutdown(wait=True)
            ticker_stop.set()
            summary = self._summary(state, len(tasks))
            self.close()
        return summary

    def _summary(self, state, n):
        by = {}
        for r in self.done.values():
            by.setdefault(r["model"], {}).setdefault(r["status"], 0)
            by[r["model"]][r["status"]] += 1
        s = dict(state, tasks=n, not_run=n - state["finished"] - state["aborted"], halted=self.stop.is_set(),
                 paused=getattr(self, "paused", False), complete=state["finished"] == n,
                 spent_usd=round(self.spent, 6),
                 account_throttles=self.account_throttles,
                 results_without_billing=sum(bool(r.get("billing_unresolved")) for r in self.done.values()),
                 confirmed_usd=round(self.spent - self.unsettled - self.unsettled_prior, 6),
                 unsettled_billing_usd=round(self.unsettled + self.unsettled_prior, 6),
                 stop_info=self.stop_info, journal_by_model=by,
                 calls_pending=sum(p[0] not in self.done for p in self.planned))
        with self.lock:
            self._write({"type": "session", "event": "end", "summary": s, "t": time.time()})
        with open(os.path.join(self.dir, "summary.json"), "w") as f:
            json.dump(s, f, indent=1, sort_keys=True)
        return s


def status(run_dir):
    """Read-only progress report (safe while a run is active): per-model journal counts, calls pending,
    spend, and the session history (start / resume / end). Pause a run with: touch <run_dir>/PAUSE."""
    with open(os.path.join(run_dir, "journal.jsonl")) as f:
        lines = [json.loads(x) for x in f if x.strip()]
    with open(os.path.join(run_dir, "manifest.json")) as f:
        planned = json.load(f)["planned_keys"]
    done, intents, spent, sessions = {}, {}, 0.0, []
    for r in lines[1:]:
        if r["type"] == "intent":
            intents[r["iid"]] = r["reserve_usd"]
        elif r["type"] in ("result", "void"):
            intents.pop(r.get("iid"), None)
            if r["type"] == "result":
                done[r["key"]] = r
                spent += r.get("cost_usd") or 0.0
        elif r["type"] == "session":
            sessions.append({k: r[k] for k in ("event", "t") if k in r})
    by = {}
    for r in done.values():
        by.setdefault(r["model"], {}).setdefault(r["status"], 0)
        by[r["model"]][r["status"]] += 1
    pending = [k for k in planned if k not in done]
    return {"calls_planned": len(planned), "calls_done": len(planned) - len(pending), "calls_pending": len(pending),
            "by_model": by, "spent_usd": round(spent + sum(intents.values()), 6), "in_flight_or_unsettled": len(intents),
            "paused": os.path.exists(os.path.join(run_dir, "PAUSE")), "sessions": sessions}
