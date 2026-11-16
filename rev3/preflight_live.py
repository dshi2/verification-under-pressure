"""Live endpoint preflight for P1 and P2 (a few real calls per model; NOT study data, never analysed).

  python3 preflight_live.py --config configs/p1_dev_eval_v1.json \
      --p2-stimuli ../../scope-of-trust/rev3/stimuli_dev.jsonl --out runs/preflight

Per model, with the exact request body the runner sends (same pinning, same settings):
  1. P2 attribution stimulus           -> HTTP 200, served provider/model match the pin, JSON parses
  2. P1 optional arm (tool offered)     -> accepted with tools; records whether the model called the tool
  3. P1 supplied arm (injected call_0)  -> accepted with an injected tool call + tool_choice "none"
  4. P1 continuation of the model's own tool call (if step 2 produced one) -> accepted
For every response: reasoning text returned or not (DeepSeek must be none: thinking off), finish reason,
usage present. Writes <out>/preflight.json and exits non-zero if any check fails. Reads OPENROUTER_API_KEY
from the environment; the key is never printed or written.
"""
import argparse
import json
import os
import sys

from llmrun import Runner, http_transport
from p1v3 import stimuli as S
import run_p1 as H


class _Cfg:
    def __init__(self, cfg):
        self.cfg = cfg


def body(cfg, model, messages, tools=None, choice=None):
    return Runner._body(_Cfg(cfg), model, messages, tools, choice)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--p2-stimuli", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.config) as f:
        cfg = json.load(f)
    with open(a.p2_stimuli) as f:
        p2 = next(json.loads(x) for x in f if '"attribution"' in x)
    item = S.dev_items(1)[1]
    row = {"item_id": item["item_id"], "repeat": 0, "snapshot": "stale", "assertion": "wrong",
           "pressure": "neutral", "route": "optional", "paraphrase_id": 0}
    t1 = S.turn1_messages(item, "stale")
    prefix = t1 + [{"role": "assistant", "content": json.dumps({"answer": S.snapshot_value(item, "stale")})},
                   {"role": "user", "content": S.turn2_user(item, "neutral", 0, "wrong")}]
    report, fails = {}, []
    for name, m in sorted(cfg["models"].items()):
        out = report[name] = {}

        def send(tag, msgs, tools=None, choice=None, want_json_item=None):
            st, resp, _ = http_transport(cfg["endpoint"], body(cfg, name, msgs, tools, choice), cfg["timeout_s"])
            ch = ((resp.get("choices") or [{}])[0]) if isinstance(resp, dict) else {}
            msg = ch.get("message") or {}
            rec = {"http": st, "served_provider": resp.get("provider"), "served_model": resp.get("model"),
                   "finish_reason": ch.get("finish_reason"), "usage_present": bool(resp.get("usage")),
                   "reasoning_returned": bool(msg.get("reasoning") or msg.get("reasoning_content")
                                              or msg.get("reasoning_details")),
                   "tool_calls": msg.get("tool_calls"), "content": (msg.get("content") or "")[:300],
                   "error": resp.get("error")}
            ok = (st == 200 and rec["served_provider"] == m["provider_name"]
                  and str(rec["served_model"] or "").startswith(m["slug"]))
            if want_json_item is not None and not rec["tool_calls"]:
                ok = ok and S.parse_answer(msg.get("content"), want_json_item)[0] == "valid"
            if name == "deepseek-v3.2" and rec["reasoning_returned"]:
                ok = False
                rec["note"] = "reasoning returned although thinking is configured off"
            rec["pass"] = ok
            out[tag] = rec
            if not ok:
                fails.append(f"{name} {tag}")
            print(f"{'PASS' if ok else 'FAIL'} {name:22s} {tag:22s} http={st} provider={rec['served_provider']} "
                  f"reasoning={rec['reasoning_returned']} tools={bool(rec['tool_calls'])}", flush=True)
            return msg

        msg = send("p2_attribution", p2["messages"])
        try:
            json.loads(msg.get("content") or "")
        except ValueError:
            s = (msg.get("content") or "")
            if not (s.find("{") >= 0 and s.rfind("}") > s.find("{")):
                fails.append(f"{name} p2_attribution JSON")
                out["p2_attribution"]["pass"] = False
        opt = send("p1_optional", prefix, [S.TOOL], None, item)
        send("p1_supplied", prefix + S.supplied_messages(item), [S.TOOL], "none", item)
        if opt.get("tool_calls"):
            canon = [H.canonical_call(tc) for tc in opt["tool_calls"]]
            cont = prefix + [{"role": "assistant", "content": "", "tool_calls": canon}] + [
                {"role": "tool", "tool_call_id": tc["id"], "content": S.tool_result(item, H.lookup_id(tc))} for tc in canon]
            send("p1_continuation", cont, [S.TOOL], "none", item)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "preflight.json"), "w") as f:
        json.dump({"label": "LIVE PREFLIGHT - not study data", "results": report, "failures": fails}, f, indent=1)
    print(f"\n{'PREFLIGHT PASSED' if not fails else 'PREFLIGHT FAILED: ' + ', '.join(fails)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
