"""Analyse a P1 run's trials.jsonl: validity checks first, then E1-E4 per model (spec §7). No pooling.

  python3 analyze_p1.py --run-dir runs/X                 -> runs/X/analysis.json and runs/X/analysis.md
  python3 analyze_p1.py --run-dir runs/A runs/B --out DIR  (base + extension together; models must match)

Estimates are point estimates with sign-aware assigned-denominator bounds (p1v3.estimands); the interval
method waits on the §9 coverage simulation, so no hypothesis decision is made here. The schedule is checked
against the run's frozen manifest (design rows x models) before anything is estimated.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

from p1v3.estimands import CELLS, ESTIMANDS, PRIMARY, estimate_by_model
from p1v3.inference import holm, summarize

ROLES = {}  # every configuration is primary
LABEL = ("DEVELOPMENT-CASE EVALUATION: builder-written dev families, pressure paraphrases not yet rated (§5), "
         "intervals and p-values provisional until the §9 simulation picks the method. Not confirmatory evidence.")


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


def cells(trials):
    """Per model x cell: mean of final_correct, conceded, lookup_attempted over observed trials (descriptive; plots)."""
    out = {}
    for m in sorted({t["model"] for t in trials}):
        acc = defaultdict(lambda: defaultdict(list))
        for t in trials:
            if t["model"] != m:
                continue
            c = "/".join((t["snapshot"], t["assertion"], t["pressure"], t["route"]))
            for k in ("final_correct", "conceded", "lookup_attempted"):
                if t.get(k) is not None:
                    acc[c][k].append(t[k])
        out[m] = {"/".join(c): {k: (sum(v) / len(v), len(v)) for k, v in acc["/".join(c)].items()} for c in CELLS}
    return out


def window(run_dir):
    """Execution window from the journal's session records (first start to last end)."""
    ts = []
    with open(os.path.join(run_dir, "journal.jsonl")) as f:
        for line in f:
            if '"type": "session"' in line:
                try:
                    ts.append(json.loads(line)["t"])
                except (ValueError, KeyError):
                    pass
    import time
    fmt = lambda t: time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(t))
    return [fmt(min(ts)), fmt(max(ts))] if ts else None


def batches(run_dirs, trials, combined):
    """Base-only, extension-only and combined estimates, plus the between-batch difference per estimand
    (Welch t over item-level values, batch 2 minus batch 1). Batches run at different times on hosted models,
    so pooling is read only alongside this check."""
    from statistics import mean, stdev
    from p1v3.inference import t_quantile
    with_ids = {}
    for d in run_dirs:
        with open(os.path.join(d, "trials.jsonl")) as f:
            with_ids[d] = {json.loads(x)["item_id"] for x in f if x.strip()}
    out = {"windows": {d: window(d) for d in run_dirs}, "per_batch": {}, "difference": {}}
    for d in run_dirs:
        with open(os.path.join(d, "manifest.json")) as f:
            m = json.load(f)
        man = [dict(r, model=mo) for mo in m["models"] for r in m["design_rows"]]
        ts = [t for t in trials if t["item_id"] in with_ids[d]]
        out["per_batch"][d] = {}
        for p in ("insistence", "authority"):
            try:
                est = estimate_by_model(ts, pressure=p, manifest=man)
            except ValueError as e:
                out["per_batch"][d][p] = {"error": str(e)}
                continue
            out["per_batch"][d][p] = {mo: {n: {"estimate": e[n]["estimate"], "items_used": e[n]["items_used"],
                                                "item_values": e[n].pop("item_values")} for n in ESTIMANDS}
                                      for mo, e in est.items()}
    if len(run_dirs) == 2:
        d1, d2 = run_dirs
        for p in ("insistence", "authority"):
            b1, b2 = out["per_batch"][d1].get(p, {}), out["per_batch"][d2].get(p, {})
            if "error" in b1 or "error" in b2:
                continue
            out["difference"][p] = {}
            for mo in b1:
                out["difference"][p][mo] = {}
                for n in ESTIMANDS:
                    x = list(b1[mo][n]["item_values"].values())
                    y = list(b2[mo][n]["item_values"].values())
                    r = {"batch1": mean(x) if x else None, "batch2": mean(y) if y else None}
                    if len(x) > 1 and len(y) > 1:
                        vx, vy = stdev(x) ** 2 / len(x), stdev(y) ** 2 / len(y)
                        diff, se = mean(y) - mean(x), (vx + vy) ** 0.5
                        if se > 0:
                            df = (vx + vy) ** 2 / (vx ** 2 / (len(x) - 1) + vy ** 2 / (len(y) - 1))
                            h = t_quantile(0.975, df) * se
                            r.update(diff=diff, ci95_welch=[diff - h, diff + h])
                        else:
                            r.update(diff=diff, ci95_welch=None, note="zero spread in both batches")
                    out["difference"][p][mo][n] = r
    for d in run_dirs:
        for p, est in out["per_batch"][d].items():
            for mo, e in (est.items() if "error" not in est else []):
                for n in ESTIMANDS:
                    e[n].pop("item_values", None)
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
    ap.add_argument("--run-dir", required=True, nargs="+")
    ap.add_argument("--out", help="output directory (default: the single --run-dir)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 unless the schedule matches the manifest and every E1-E4 is estimable for every model")
    a = ap.parse_args()
    if len(a.run_dir) > 1 and not a.out:
        ap.error("--out is required with several --run-dir")
    out_dir = a.out or a.run_dir[0]
    os.makedirs(out_dir, exist_ok=True)
    trials, manifest, man = [], [], {"models": None, "run_dirs": a.run_dir}
    for d in a.run_dir:
        with open(os.path.join(d, "trials.jsonl")) as f:
            trials += [json.loads(x) for x in f if x.strip()]
        with open(os.path.join(d, "manifest.json")) as f:
            m = json.load(f)
        if man["models"] not in (None, m["models"]):
            raise SystemExit(f"{d}: models differ from the first run; runs cannot be combined")
        man["models"] = m["models"]
        manifest += [dict(r, model=mo) for mo in m["models"] for r in m["design_rows"]]
    ids = [t["item_id"] for t in trials]
    family_of = {t["item_id"]: t["family"] for t in trials}
    res = {"label": LABEL, "roles": ROLES, "run_dirs": a.run_dir, "n_items": len(set(ids)),
           "n_families": len(set(family_of.values())), "validity": validity(trials), "cells": cells(trials),
           "estimates": {}}
    for p in ("insistence", "authority"):
        try:
            res["estimates"][p] = estimate_by_model(trials, pressure=p, manifest=manifest)
        except ValueError as e:
            res["estimates"][p] = {"error": str(e)}
            continue
        for m, est in res["estimates"][p].items():
            for name in ESTIMANDS:
                est[name]["inference"] = summarize(est[name].pop("item_values"), family_of, seed=ESTIMANDS.index(name))
            adj = holm({n: est[n]["inference"].get("p_signflip") for n in PRIMARY})
            for n in PRIMARY:
                est[n]["inference"]["p_holm_primary"] = adj.get(n)
    if len(a.run_dir) > 1:
        res["batches"] = batches(a.run_dir, trials, res["estimates"])
    with open(os.path.join(out_dir, "analysis.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
    md = [f"# P1 analysis", "", f"**{LABEL}**", "", f"Runs {a.run_dir}: {res['n_items']} items, {res['n_families']} families. Intervals and p-values are provisional (§9 has not chosen the method); Holm is across E1–E4 within model × pressure.", ""]
    for m, v in res["validity"].items():
        md += [f"## {m}" + (f" — {ROLES[m]}" if m in ROLES else ""), "", f"Status {v['status']}. Turn-1 eligibility {v['turn1_eligible_by_snapshot']}. "
               f"Neutral optional attempt rate {v['neutral_optional_attempt_rate']}. Neutral supplied adoption "
               f"{v['neutral_supplied_adoption']}. Truncated {v['truncated']}.", "",
               "| contrast | pressure | estimate | 95% CI items (provisional) | 95% CI families | sign-flip p (Holm, primary) | assigned-denominator bounds | items used / dropped |",
               "|---|---|---|---|---|---|---|---|"]
        for p, est in res["estimates"].items():
            e = est.get(m) if isinstance(est, dict) else None
            if not e:
                md.append(f"| all | {p} | not estimable: {est.get('error', '–')} | | |")
                continue
            for name in ESTIMANDS:
                r = e[name]
                inf = r.get("inference", {})
                f3 = lambda v: "–" if v is None else f"{v:+.3f}"
                ci = lambda c: "–" if not c else f"[{c[0]:+.3f}, {c[1]:+.3f}]"
                deg = " (degenerate: zero spread, not precision)" if inf.get("degenerate") else ""
                ph = inf.get("p_holm_primary")
                pv = "–" if inf.get("p_signflip") is None else f"{inf['p_signflip']:.2g}" + (f" ({ph:.2g})" if ph is not None else "")
                b = r.get("bounds") or (None, None)
                md.append(f"| {name} | {p} | {f3(r.get('estimate'))} | {ci(inf.get('ci95_item_t'))}{deg} | "
                          f"{ci(inf.get('ci95_family_t'))} | {pv} | [{f3(b[0])}, {f3(b[1])}] | "
                          f"{r.get('items_used')} / {r.get('items_dropped_incomplete')} |")
        md.append("")
    if "batches" in res:
        bt = res["batches"]
        md += ["## Batches (base vs extension; read before the pooled estimates)", "",
               f"Execution windows: {bt['windows']}", "",
               "| pressure | model | estimand | batch 1 | batch 2 | difference (2 − 1) | Welch 95% CI |",
               "|---|---|---|---|---|---|---|"]
        f3 = lambda v: "–" if v is None else f"{v:+.3f}"
        for p, by in bt["difference"].items():
            for mo, ests in by.items():
                for n_, r in ests.items():
                    ci = r.get("ci95_welch")
                    md.append(f"| {p} | {mo} | {n_} | {f3(r['batch1'])} | {f3(r['batch2'])} | {f3(r.get('diff'))} | "
                              + ("–" if not ci else f"[{ci[0]:+.3f}, {ci[1]:+.3f}]") + " |")
        md.append("")
    with open(os.path.join(out_dir, "analysis.md"), "w") as f:
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
