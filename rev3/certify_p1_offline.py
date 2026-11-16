"""Offline certification of the full P1 development matrix (no network, no cost). Exits non-zero on any failure.

  python3 certify_p1_offline.py --config configs/p1_dev_eval_v1.json --repeats 5 --out DIR [--restarts 3]

1. Runs the whole design (24 dev items x 36 cells x repeats x 4 models) through PlantedModel.
2. Asserts: every scheduled trial exported exactly once; every planned stage journaled once (ok/failed/skipped);
   one turn-1 request per item x snapshot x model x repeat; injected faults carry the right labels;
   attempted / completed / relevant lookups as planted; strict analysis passes and E1-E4 recover the planted
   values exactly for every model and both pressure contrasts.
3. Re-runs the design with `--restarts` random interruptions (each resumed) and asserts the exported trials
   are identical to the uninterrupted run.
"""
import argparse
import json
import os
import random
import subprocess
import sys
from collections import Counter

import run_p1 as H
from llmrun import Runner
from p1v3 import offline as O
from p1v3 import stimuli as S


def run(cfg, items, rows, d, restarts=0, seed=0):
    models = sorted(cfg["models"])
    tasks, planned = H.build(models, items, rows, cfg)
    manifest = {"experiment": "P1 offline certification", "models": models, "design_rows": rows,
                "planned_keys": sorted(p[0] for p in planned)}
    fake = O.PlantedModel(items, cfg)
    rng = random.Random(seed)
    cuts = sorted(rng.sample(range(100, len(planned) // 2), restarts)) if restarts else []
    resume, sent0 = False, 0
    for cut in cuts + [None]:
        r = Runner(d, cfg, manifest, fake, resume=resume)
        if cut is not None:
            orig = fake.__call__

            class Cut:
                def __init__(s):
                    s.fired = False

                def __call__(s, url, body, timeout):
                    out = orig(url, body, timeout)
                    if fake.n >= cut and not s.fired:
                        s.fired = True
                        r._halt("certification interruption")
                    return out
            r.transport = Cut()
        s = r.run(tasks, planned)
        resume = True
        if cut is not None and s["complete"]:
            raise SystemExit(f"interruption at {cut} did not interrupt")
    return s, H.export(d, models, items, rows), planned, fake, manifest


def check(cond, msg, fails):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--per-family", type=int, default=4)
    ap.add_argument("--item-set", choices=("base", "ext"), default="base")
    ap.add_argument("--restarts", type=int, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    Runner.progress_every = 0
    with open(a.config) as f:
        cfg = json.load(f)
    items = S.item_set(a.item_set, a.per_family)
    rows = H.design(items, a.repeats)
    models = sorted(cfg["models"])
    fails = []
    d1 = os.path.join(a.out, "uninterrupted")
    s, trials, planned, fake, manifest = run(cfg, items, rows, d1)
    with open(os.path.join(d1, "manifest.json"), "w") as f:
        json.dump(manifest, f)
    n_trials = len(rows) * len(models)
    check(s["complete"] and len(trials) == n_trials, f"{n_trials} scheduled trials exported", fails)
    keys = [(t["model"], t["item_id"], t["snapshot"], t["assertion"], t["pressure"], t["route"], t["repeat"]) for t in trials]
    check(len(set(keys)) == len(keys), "every scheduled trial exactly once", fails)
    with open(os.path.join(d1, "journal.jsonl")) as f:
        res = [json.loads(x) for x in f if '"type": "result"' in x]
    check(sorted(r["key"] for r in res) == sorted(p[0] for p in planned),
          f"all {len(planned)} planned stages journaled exactly once", fails)
    n_units = len(items) * 2 * a.repeats * len(models)
    t1 = [r for r in res if r["key"].endswith("|turn1") and r["status"] == "ok"]
    check(len(t1) == n_units, f"{n_units} turn-1 requests (one per item x snapshot x repeat x model)", fails)
    st = Counter(t["status"] for t in trials)
    per_model_reps = a.repeats * len(models)
    check(st["turn1_ineligible"] == 18 * per_model_reps, f"refusal -> turn1_ineligible x18 per unit ({st['turn1_ineligible']})", fails)
    check(st["provider_error"] == 2 * per_model_reps, f"HTTP 400 -> provider_error ({st['provider_error']})", fails)
    check(sum(t["validity"] == "malformed" for t in trials) == 12 * per_model_reps,
          "non-JSON final -> validity malformed", fails)
    check(set(st) == {"ok", "turn1_ineligible", "provider_error"}, f"no other statuses {dict(st)}", fails)
    opt = [t for t in trials if t["route"] == "optional" and t["status"] == "ok"]
    check(all((t["lookup_attempted"], t["lookup_completed"], t["lookup_relevant"]) ==
              ((0, 0, 0) if t["pressure"] == "insistence" else (1, 1, 1)) for t in opt),
          "attempted / completed / relevant lookups as planted", fails)
    sup = [t for t in trials if t["route"] == "supplied" and t["status"] == "ok"]
    check(all(t["adopted_supplied"] == 1 for t in sup), "supplied evidence adopted as planted", fails)
    proc = subprocess.run([sys.executable, "analyze_p1.py", "--run-dir", d1, "--strict"], capture_output=True, text=True)
    check(proc.returncode == 0, "analyze_p1.py --strict passes", fails)
    with open(os.path.join(d1, "analysis.json")) as f:
        an = json.load(f)
    for p, truth in O.PLANTED.items():
        for m in models:
            got = {k: an["estimates"][p][m][k]["estimate"] for k in truth}
            check(all(abs(got[k] - v) < 1e-12 for k, v in truth.items()), f"{m} {p}: E1-E4 recover {truth}", fails)
            want = 2 if p == "insistence" else 1  # the HTTP-400 fault sits in an insistence cell only
            check(an["estimates"][p][m]["E4_moderation"]["items_dropped_incomplete"] == want,
                  f"{m} {p}: exactly the {want} faulted item(s) touching its cells dropped from E4", fails)
    if a.restarts:
        d2 = os.path.join(a.out, "interrupted")
        s2, trials2, _, _, _ = run(cfg, items, rows, d2, restarts=a.restarts, seed=7)
        norm = lambda ts: sorted(json.dumps(t, sort_keys=True) for t in ts)
        check(s2["complete"] and norm(trials2) == norm(trials),
              f"{a.restarts} random interruptions + resume -> identical trials", fails)
        with open(os.path.join(d2, "journal.jsonl")) as f:
            res2 = [json.loads(x) for x in f if '"type": "result"' in x]
        check(len({r["key"] for r in res2}) == len(res2) == len(res), "no duplicate counted stage after restarts", fails)
    print(f"\n{'CERTIFIED' if not fails else 'NOT CERTIFIED'}: {len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
