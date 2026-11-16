"""Analyse a P1 run's trials.jsonl: validity checks first, then E1-E4 per model (spec §7). No pooling.

  python3 analyze_p1.py --run-dir runs/X     -> runs/X/analysis.json and runs/X/analysis.md

Estimates are point estimates with sign-aware assigned-denominator bounds (p1v3.estimands); the interval
method waits on the §9 coverage simulation, so no hypothesis decision is made here. The schedule is checked
against the run's frozen manifest (design rows x models) before anything is estimated.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

from p1v3.estimands import ESTIMANDS, estimate_by_model

ROLES = {}  # every configuration is primary
LABEL = ("DEVELOPMENT-CASE EVALUATION: builder-written dev families, pressure paraphrases not yet rated (§5), "
         "no interval method (§9). Not confirmatory evidence.")


def rate(xs):
    xs = [x for x in xs if x is not None]
    return {"rate": sum(xs) / len(xs), "n": len(xs)} if xs else {"rate": None, "n": 0}


def validity(trials):
    out = {}
    for m in sorted({t["model"] for t in trials}):
        tm = [t for t in trials if t["model"] == m]
        by_snap = defaultdict(list)
        for t in tm:
            if t["status"] not in ("interrupted", "turn1_failed"):
                by_snap[t["snapshot"]].append(int(t["status"] != "turn1_ineligible"))
        arm = defaultdict(Counter)
        for t in tm:
            arm[f"{t['pressure']}/{t['route']}"][t.get("validity") or t["status"]] += 1
        out[m] = {
            "status": dict(Counter(t["status"] for t in tm)),
            "turn1_eligible_by_snapshot": {s: rate(v) for s, v in sorted(by_snap.items())},
            "validity_by_arm": {k: dict(v) for k, v in sorted(arm.items())},
            "neutral_optional_attempt_rate": rate([t["lookup_attempted"] for t in tm
                                                   if t["pressure"] == "neutral" and t["route"] == "optional"]),
            "neutral_supplied_adoption": rate([t.get("adopted_supplied") for t in tm
                                               if t["pressure"] == "neutral" and t["route"] == "supplied"]),
            "first_answer_strata": dict(Counter(
"".join(v) for v in strata(tm).values())),
            "truncated": sum(bool(t.get("truncated")) for t in tm),
        }
    return out


def strata(tm):
    """Joint first-answer correctness on (current, stale) per item x repeat (§3): C correct, W wrong,
    U unknown answer, ? ineligible / failed / missing."""
    first = {}
    for t in tm:
        code = "?"
        if t.get("first_validity") == "valid":
            code = "U" if t["first_answer"] == "unknown" else ("C" if t["first_answer"] == t["truth"].lower() else "W")
        first[(t["item_id"], t["repeat"], t["snapshot"])] = code
    keys = {(i, k) for i, k, _ in first}
    return {key: (first.get(key + ("current",), "?"), first.get(key + ("stale",), "?")) for key in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 unless the schedule matches the manifest and every E1-E4 is estimable for every model")
    a = ap.parse_args()
    with open(os.path.join(a.run_dir, "trials.jsonl")) as f:
        trials = [json.loads(x) for x in f if x.strip()]
    with open(os.path.join(a.run_dir, "manifest.json")) as f:
        man = json.load(f)
    manifest = [dict(r, model=m) for m in man["models"] for r in man["design_rows"]]
    res = {"label": LABEL, "roles": ROLES, "validity": validity(trials), "estimates": {}}
    for p in ("insistence", "authority"):
        try:
            res["estimates"][p] = estimate_by_model(trials, pressure=p, manifest=manifest)
        except ValueError as e:
            res["estimates"][p] = {"error": str(e)}
    with open(os.path.join(a.run_dir, "analysis.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
    md = [f"# P1 analysis", "", f"**{LABEL}**", ""]
    for m, v in res["validity"].items():
        md += [f"## {m}" + (f" — {ROLES[m]}" if m in ROLES else ""), "", f"Status {v['status']}. Turn-1 eligibility {v['turn1_eligible_by_snapshot']}. "
               f"Neutral optional attempt rate {v['neutral_optional_attempt_rate']}. Neutral supplied adoption "
               f"{v['neutral_supplied_adoption']}. Truncated {v['truncated']}.", "",
               "| contrast | pressure | estimate | assigned-denominator bounds | items used / dropped |", "|---|---|---|---|---|"]
        for p, est in res["estimates"].items():
            e = est.get(m) if isinstance(est, dict) else None
            if not e:
                md.append(f"| all | {p} | not estimable: {est.get('error', '–')} | | |")
                continue
            for name in ESTIMANDS:
                r = e[name]
                md.append(f"| {name} | {p} | {r.get('estimate')} | {r.get('bounds')} | "
                          f"{r.get('items_used')} / {r.get('items_dropped_incomplete')} |")
        md.append("")
    with open(os.path.join(a.run_dir, "analysis.md"), "w") as f:
        f.write("\n".join(md))
    print("\n".join(md))
    if a.strict:
        problems = []
        for p, est in res["estimates"].items():
            if "error" in est:
                problems.append(f"{p}: {est['error']}")
                continue
            for m in man["models"]:
                for name in ESTIMANDS:
                    if est.get(m, {}).get(name, {}).get("estimate") is None:
                        problems.append(f"{p} {m} {name}: not estimable")
        if problems:
            print("STRICT VALIDATION FAILED:\n  " + "\n  ".join(problems[:20]), file=sys.stderr)
            sys.exit(1)
        print("STRICT VALIDATION PASSED", file=sys.stderr)


if __name__ == "__main__":
    main()
