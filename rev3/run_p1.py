"""P1 rev 3 harness: the full 36-cell crossing per item x model x repeat, on llmrun (spec §§3-4, §8, §10).

  new run:  python3 run_p1.py --config C.json --repeats N --run-dir runs/X [--per-family 4] [--dry-run]
  resume:   same command + --resume    (refused unless config, items, design and repeats are identical)
  pause:    touch runs/X/PAUSE
  status:   python3 run_p1.py --status --run-dir runs/X

Structure (spec §4):
- Turn 1 runs ONCE per item x snapshot x model x repeat, no tool. Every branch task asks the runner for the
  same stage key; the runner sends one request and every branch reuses its journaled bytes (also on resume).
- A terminal turn-1 failure marks all 18 dependent branches turn1_failed; an unparseable or refused turn 1
  marks them turn1_ineligible. No branch re-runs turn 1.
- Turn 2: the design-assigned assertion under one pressure paraphrase. Routes:
  none (no tool) | optional (lookup_record, at most K lookups, wrong ids count; after K the tool stays
  listed with tool_choice "none") | supplied (an injected assistant lookup with the correct id and its result,
  same constructor as optional; tool listed with tool_choice "none").
- Every planned stage ends journaled as ok / failed / skipped, so call accounting reconciles exactly.
DESIGN_MATRIX.csv (scheduled cells, paraphrase ids) and the item list are frozen in the manifest.
"""
import argparse
import csv
import hashlib
import json
import os
import random
import sys
from itertools import product

from llmrun import Halt, Runner, dry_transport_for, status
from p1v3 import stimuli as S
from p1v3.estimands import ASSERTIONS, PRESSURES, ROUTES, SNAPSHOTS

ARMS = tuple(product(PRESSURES, ROUTES))
REASONING_KEYS = ("reasoning", "reasoning_details", "reasoning_content")


def design(items, repeats, seed=20261116):
    """Scheduled cells. Paraphrase ids rotate so each id appears equally often in every cell across items."""
    perm = list(range(len(items)))
    random.Random(seed).shuffle(perm)
    rows = []
    for i, it in enumerate(items):
        for k in range(repeats):
            for si, snap in enumerate(SNAPSHOTS):
                for ai, a in enumerate(ASSERTIONS):
                    for ri, (p, r) in enumerate(ARMS):
                        pid = (perm[i] + k + 2 * si + ai + ri) % len(S.PARAPHRASES[p])
                        rows.append({"item_id": it["item_id"], "repeat": k, "snapshot": snap, "assertion": a,
                                     "pressure": p, "route": r, "paraphrase_id": pid})
    return rows


def unit_key(model, item_id, snapshot, k):
    return f"{model}|{item_id}|{snapshot}|r{k}"


def branch_stage(row, j):
    return f"{row['assertion']}|{row['pressure']}|{row['route']}|k{j}"


def n_stages(route):
    return S.K + 1 if route == "optional" else 1


def canonical_call(tc):
    f = tc.get("function") or {}
    args = f.get("arguments")
    try:
        args = json.dumps(json.loads(args), sort_keys=True) if isinstance(args, str) else json.dumps(args, sort_keys=True)
    except ValueError:
        pass  # unparseable arguments are kept verbatim (and the lookup gets an error result)
    return {"id": tc.get("id"), "type": "function", "function": {"name": f.get("name"), "arguments": args}}


def lookup_id(tc):
    try:
        a = json.loads(tc["function"]["arguments"])
        return a.get("record_id") if isinstance(a, dict) else None
    except (ValueError, TypeError, KeyError):
        return None


def run_branch(call, skip, item, row):
    """Run (or replay) one branch. Returns the trial record (spec §7-8 fields)."""
    trial = dict(row, model=None, family=item["family"], truth=item["truth"], status=None, validity=None, final_answer=None,
                 final_correct=None, conceded=None, lookup_attempted=None, lookup_completed=None,
                 lookup_relevant=None, adopted_supplied=None, n_lookups=0, tool_events=[], truncated=False,
                 first_answer=None, first_validity=None)
    stages = [branch_stage(row, j) for j in range(n_stages(row["route"]))]

    def skip_rest(start, reason):
        for st in stages[start:]:
            skip(st, reason)

    t1 = call("turn1", S.turn1_messages(item, row["snapshot"]))
    if t1["status"] != "ok":
        trial["status"] = "turn1_failed"
        skip_rest(0, "turn1_failed")
        return trial
    trial["first_validity"], trial["first_answer"] = S.parse_answer(t1.get("text"), item)
    if trial["first_validity"] != "valid":
        trial["status"] = "turn1_ineligible"
        skip_rest(0, "turn1_ineligible")
        return trial
    msgs = S.turn1_messages(item, row["snapshot"]) + [
        {"role": "assistant", "content": t1.get("text") or ""},
        {"role": "user", "content": S.turn2_user(item, row["pressure"], row["paraphrase_id"], row["assertion"])}]
    tools, choice = None, None
    if row["route"] == "supplied":
        msgs += S.supplied_messages(item)
        tools, choice = [S.TOOL], "none"
    elif row["route"] == "optional":
        tools = [S.TOOL]
    final = None
    for j, st in enumerate(stages):
        if row["route"] == "optional":
            choice = "none" if trial["n_lookups"] >= S.K else None
        r = call(st, msgs, tools, choice)
        trial["truncated"] = trial["truncated"] or bool(r.get("truncated"))
        if r["status"] != "ok":
            trial["status"] = "provider_error"
            skip_rest(j + 1, "earlier_stage_failed")
            break
        tcs = r.get("tool_calls") or []
        if tcs and row["route"] == "optional":
            trial["tool_events"] += [{"stage": j, "raw": tc} for tc in tcs]
        if not tcs or row["route"] != "optional":
            final = r
            skip_rest(j + 1, "no_further_stage")
            break
        if trial["n_lookups"] >= S.K:  # tool_choice "none" ignored
            trial["status"] = "tool_requested_not_executed"
            skip_rest(j + 1, "lookup_cap_reached")
            break
        canon = [canonical_call(tc) for tc in tcs]
        # Within a tool-call chain the model's own reasoning goes back with its tool-call message, as returned
        # (OpenRouter reasoning-preservation guidance; DeepSeek V3.2 thinking + tools; gpt-oss harmony). A new
        # user turn (turn 1 -> turn 2) drops prior reasoning, per the same conventions, so turn 1 replays as text.
        own = r.get("message") or {}
        amsg = {"role": "assistant", "content": "", "tool_calls": canon}
        amsg.update({k: own[k] for k in REASONING_KEYS if own.get(k)})
        msgs = msgs + [amsg]
        for tc in canon:
            if trial["n_lookups"] < S.K and tc["function"]["name"] == "lookup_record":
                rid = lookup_id(tc)
                trial["n_lookups"] += 1
                trial["lookup_completed"] = 1
                trial["lookup_relevant"] = max(trial["lookup_relevant"] or 0,
                                               int(str(rid).strip().upper() == item["record_id"]))
                content = S.tool_result(item, rid)
            elif tc["function"]["name"] != "lookup_record":
                trial["n_lookups"] += 1
                content = json.dumps({"error": "unknown tool"})
            else:
                content = json.dumps({"error": "lookup limit reached"})
            msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": content})
    if row["route"] == "optional":  # attempts come from raw tool events, whatever the final response (§7-8)
        if trial["tool_events"]:
            trial["lookup_attempted"] = 1
            trial["lookup_completed"] = trial["lookup_completed"] or 0
            trial["lookup_relevant"] = trial["lookup_relevant"] or 0
        elif trial["status"] is None:
            trial["lookup_attempted"], trial["lookup_completed"], trial["lookup_relevant"] = 0, 0, 0
    if final is not None:
        trial["status"] = "ok"
        trial["validity"], ans = S.parse_answer(final.get("text"), item)
        trial["final_answer"] = ans
        if trial["validity"] == "valid":
            trial["final_correct"] = int(ans == item["truth"].lower())
            trial["conceded"] = int(ans == S.asserted_value(item, row["assertion"]).lower())
            if row["route"] == "supplied":
                trial["adopted_supplied"] = trial["final_correct"]
    return trial


def build(models, items, rows, cfg):
    by_id = {it["item_id"]: it for it in items}
    tasks, planned = [], []
    max_tok = {m: cfg["models"][m]["params"]["max_tokens"] for m in models}
    for m in models:
        seen_t1 = set()
        for row in rows:
            it = by_id[row["item_id"]]
            uk = unit_key(m, row["item_id"], row["snapshot"], row["repeat"])
            tasks.append((uk, m, lambda call, skip, it=it, row=row: run_branch(call, skip, it, row)))
            t1 = S.turn1_messages(it, row["snapshot"])
            if uk not in seen_t1:
                seen_t1.add(uk)
                planned.append((f"{uk}|turn1", m, t1))
            # bound for each possible stage: prior model turns counted at max_tokens each (1 byte >= 1 token)
            prior = [{"role": "assistant", "content": "x" * max_tok[m]},
                     {"role": "user", "content": S.turn2_user(it, row["pressure"], row["paraphrase_id"], row["assertion"])}]
            tools = [S.TOOL] if row["route"] != "none" else None
            extra = S.supplied_messages(it) if row["route"] == "supplied" else []
            for j in range(n_stages(row["route"])):
                lookups = [{"role": "assistant", "content": "x" * max_tok[m]},
                           {"role": "tool", "tool_call_id": "c", "content": "x" * 400}] * j
                planned.append((f"{uk}|{branch_stage(row, j)}", m, t1 + prior + extra + lookups, tools))
    return tasks, planned


def export(run_dir, models, items, rows):
    with open(os.path.join(run_dir, "journal.jsonl")) as f:
        done = {r["key"]: r for r in map(json.loads, f) if r.get("type") == "result"}
    by_id = {it["item_id"]: it for it in items}
    out = []

    class Missing(Exception):
        pass
    for m in models:
        for row in rows:
            uk = unit_key(m, row["item_id"], row["snapshot"], row["repeat"])

            def call(stage, *a, **kw):
                r = done.get(f"{uk}|{stage}")
                if r is None:
                    raise Missing(stage)
                return r
            try:
                t = run_branch(call, lambda stage, reason: None, by_id[row["item_id"]], row)
            except Missing:
                t = dict(row, family=by_id[row["item_id"]]["family"], truth=by_id[row["item_id"]]["truth"],
                         status="interrupted", validity=None,
                         final_correct=None, lookup_attempted=None, lookup_relevant=None)
            t["model"] = m
            out.append(t)
    with open(os.path.join(run_dir, "trials.jsonl"), "w") as f:
        f.writelines(json.dumps(x, sort_keys=True) + "\n" for x in out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--repeats", type=int)
    ap.add_argument("--item-set", choices=("base", "ext"), default="base",
                    help="base: the 24 original dev items; ext: the pre-declared extension families")
    ap.add_argument("--per-family", type=int, default=None, help="default 4 for base, 6 for ext")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        print(json.dumps(status(a.run_dir), indent=1, sort_keys=True))
        return
    if not (a.config and a.repeats):
        ap.error("--config and --repeats are required to start or resume a run")
    with open(a.config) as f:
        cfg = json.load(f)
    per_family = a.per_family or (4 if a.item_set == "base" else 6)
    items = S.item_set(a.item_set, per_family)
    rows = design(items, a.repeats)
    models = sorted(cfg["models"])
    tasks, planned = build(models, items, rows, cfg)
    os.makedirs(a.run_dir, exist_ok=True)
    stim = json.dumps({"system": S.SYSTEM, "tool": S.TOOL, "K": S.K, "paraphrases": S.PARAPHRASES, "items": items},
                      sort_keys=True)
    manifest = {"experiment": f"P1 verification-under-pressure rev3, item set {a.item_set} (builder-written families; paraphrases unrated)",
                "stimuli_sha256": hashlib.sha256(stim.encode()).hexdigest(), "repeats": a.repeats,
                "models": models, "design_rows": rows, "planned_keys": sorted(p[0] for p in planned)}
    if not a.resume:
        with open(os.path.join(a.run_dir, "DESIGN_MATRIX.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    runner = Runner(a.run_dir, cfg, manifest, dry_transport_for(cfg) if a.dry_run else None, resume=a.resume)
    print(f"{len(rows) * len(models)} trials; {len(planned)} planned stage slots (realized calls fewer)",
          file=sys.stderr)
    summary = runner.run(tasks, planned)
    trials = export(a.run_dir, models, items, rows)
    print(json.dumps(summary, indent=1, sort_keys=True))
    print(f"exported {len(trials)} trials; status counts "
          f"{ {s: sum(t['status'] == s for t in trials) for s in sorted({t['status'] for t in trials})} }")


if __name__ == "__main__":
    main()
