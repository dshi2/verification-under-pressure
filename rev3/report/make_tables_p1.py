"""Render the P1 manuscript tables directly from an analysis.json (workstream D; no hand transcription).

Usage: python3 report/make_tables_p1.py runs/analysis_combined/analysis.json > report/tables_p1.md
Values are shown in percentage points (pp), 1 decimal. Missing keys are printed as "n/a", never as 0.
"""
import json
import sys

MODELS = [("gpt-oss-120b", "gpt-oss-120b"), ("deepseek-v3.2", "DeepSeek-V3.2"),
          ("qwen3-235b-a22b-2507", "Qwen3-235B-2507"), ("kimi-k2-0905", "Kimi-K2-0905")]
PRIMARY = [("E1_delta_attempt", "E1 Δattempt"), ("E2_delta_acc_supplied", "E2 Δacc supplied"),
           ("E3_delivery_effect", "E3 delivery"), ("E4_moderation", "E4 moderation")]
SECONDARY = [("E1b_delta_relevant", "E1b Δrelevant"), ("S2_delta_acc_none", "S2 Δacc none")]


def pp(x):
    return "n/a" if x is None else f"{100 * x:+.1f}".replace("-", "−")


def ci(c):
    return "n/a" if not c else f"[{pp(c[0])}, {pp(c[1])}]"


def pval(p):
    if p is None:
        return "n/a"
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def row(name, label, e):
    inf = e.get("inference", {})
    deg = " (degenerate)" if inf.get("degenerate") else ""
    item_only = inf.get("excludes0_item_t_only")
    if item_only is None and inf.get("ci95_item_t") and inf.get("ci95_family_cr1"):
        it, fa = inf["ci95_item_t"], inf["ci95_family_cr1"]
        item_only = (it[0] > 0 or it[1] < 0) and not (fa[0] > 0 or fa[1] < 0)
    flag = " †" if item_only else ""
    holm = inf.get("p_holm_primary")
    fholm = inf.get("p_family_cr1_holm")
    ptxt = pval(holm) if holm is not None else pval(inf.get('p_t'))
    ftxt = pval(fholm) if fholm is not None else pval(inf.get('p_family_cr1'))
    return (f"| {name} | {label} | {pp(e.get('estimate'))}{flag} | {ci(inf.get('ci95_item_t'))}{deg} | "
            f"{ci(inf.get('ci95_family_cr1'))} | {ptxt} | {ftxt} | "
            f"{ci(e.get('bounds'))} | {e.get('items_used', 'n/a')} / {e.get('items_dropped_incomplete', 'n/a')} |")


def table(est, keys, title, holm_note=True):
    out = [f"**{title}**", "",
           "| Model | Contrast | Estimate (pp) | 95% CI items, t (provisional) | 95% CI families, CR1 | "
           + ("p items (Holm) | p families CR1 (Holm)" if holm_note else "p items (t) | p families CR1")
           + " | Assigned-denominator bounds | Items used / dropped |",
           "|---|---|---|---|---|---|---|---|---|"]
    for mk, mn in MODELS:
        for k, lab in keys:
            e = est.get(mk, {}).get(k)
            if e is not None:
                out.append(row(mn, lab, e))
    out.append("")
    out.append("† excludes 0 on the item interval but not on the family-clustered interval.")
    return "\n".join(out)


def components(est):
    out = ["| Model | D(right) (pp) | D(wrong) (pp) | same sign? |", "|---|---|---|---|"]
    any_ = False
    for mk, mn in MODELS:
        c = est.get(mk, {}).get("E4_moderation", {}).get("components") or est.get(mk, {}).get("components")
        if not c or "D" not in c:
            continue
        any_ = True
        dr, dw = c["D"].get("right"), c["D"].get("wrong")
        g = lambda x: x.get("estimate") if isinstance(x, dict) else x
        r, w = g(dr), g(dw)
        same = "n/a" if r is None or w is None else ("yes" if r * w > 0 else "no")
        out.append(f"| {mn} | {pp(r)} | {pp(w)} | {same} |")
    return "\n".join(out) if any_ else "(components not exported in this analysis.json)"


def batches(d, pressure):
    b = d.get("batches", {})
    pb, df = b.get("per_batch", {}), b.get("difference", {})
    runs = list(pb)
    if len(runs) < 2:
        return "(single batch)"
    out = [f"| Model | Contrast | base | extension | difference (ext − base) | Welch 95% CI |", "|---|---|---|---|---|---|"]
    for mk, mn in MODELS:
        for k, lab in PRIMARY + SECONDARY:
            try:
                b1 = pb[runs[0]][pressure][mk][k]
                b2 = pb[runs[1]][pressure][mk][k]
                dd = df[pressure][mk][k]
            except (KeyError, TypeError):
                continue
            g = lambda x: x.get("estimate") if isinstance(x, dict) else x
            dci = dd.get("ci95_welch") if isinstance(dd, dict) else None
            dv = dd.get("diff") if isinstance(dd, dict) else dd
            out.append(f"| {mn} | {lab} | {pp(g(b1))} | {pp(g(b2))} | {pp(dv)} | {ci(dci)} |")
    return "\n".join(out)


def validity(d):
    out = ["| Model | status | turn-1 eligible (current / stale) | neutral optional attempt | "
           "neutral supplied adoption | truncated | first-answer strata |", "|---|---|---|---|---|---|---|"]
    for mk, mn in MODELS:
        v = d.get("validity", {}).get(mk)
        if not v:
            continue
        el = v.get("turn1_eligible_by_snapshot", {})
        att, ad = v.get("neutral_optional_attempt_rate", {}), v.get("neutral_supplied_adoption", {})
        st = ", ".join(f"{k} {n}" for k, n in sorted(v.get("status", {}).items()))
        strata = ", ".join(f"{k} {n}" for k, n in sorted(v.get("first_answer_strata", {}).items()))
        out.append(f"| {mn} | {st} | {el.get('current', {}).get('rate')} / {el.get('stale', {}).get('rate')} | "
                   f"{100 * att['rate']:.1f}% (n={att['n']}) | {100 * ad['rate']:.1f}% (n={ad['n']}) | "
                   f"{v.get('truncated')} | {strata} |")
    return "\n".join(out)


def lofo(est, keys):
    out = ["| Model | Contrast | estimate | equal-family-weight estimate | leave-one-family-out range |",
           "|---|---|---|---|---|"]
    for mk, mn in MODELS:
        for k, lab in keys:
            e = est.get(mk, {}).get(k)
            if e is None:
                continue
            inf = e.get("inference", {})
            out.append(f"| {mn} | {lab} | {pp(e.get('estimate'))} | {pp(inf.get('equal_family_weight_estimate'))} | "
                       f"{ci(inf.get('leave_one_family_out'))} |")
    return "\n".join(out)


def main(path):
    d = json.load(open(path))
    ins, aut = d["estimates"]["insistence"], d["estimates"]["authority"]
    print(f"<!-- generated by report/make_tables_p1.py from {path}; label: {d.get('label')}; "
          f"{d.get('n_items')} items, {d.get('n_families')} families -->\n")
    print("## Table 3 (primary, insistence vs. neutral)\n")
    print(table(ins, PRIMARY, "Primary contrasts, insistence vs. neutral"))
    print("\n## D(u) components (insistence)\n")
    print(components(ins))
    print("\n## Secondary, insistence (E1b, S2)\n")
    print(table(ins, SECONDARY, "Secondary contrasts, insistence vs. neutral", holm_note=False))
    print("\n## S1: irrelevant authority vs. neutral\n")
    print(table(aut, PRIMARY + SECONDARY, "Authority vs. neutral"))
    print("\n## Validity\n")
    print(validity(d))
    print("\n## Family robustness (insistence)\n")
    print(lofo(ins, PRIMARY))
    print("\n## Base vs. extension (insistence)\n")
    print(batches(d, "insistence"))
    print("\n## Base vs. extension (authority)\n")
    print(batches(d, "authority"))


if __name__ == "__main__":
    main(sys.argv[1])


def csv_tables(analysis_dir):
    """Funnel (optional route) and unknown-answer shares from the CSVs next to analysis.json, if present."""
    import csv
    import os
    names = dict(MODELS)
    out = []
    fp = os.path.join(analysis_dir, "funnel.csv")
    if os.path.exists(fp):
        rows = [r for r in csv.DictReader(open(fp)) if r["route"] == "optional" and r["pressure"] in ("neutral", "insistence")]
        out += ["## Optional-route funnel (counts; snapshots pooled)", "",
                "| Model | Pressure | User | ok | attempted / ok | relevant / ok | correct / valid | correct among attempted | correct among not attempted |",
                "|---|---|---|---|---|---|---|---|---|"]
        for mk, mn in MODELS:
            for r in rows:
                if r["model"] != mk:
                    continue
                f = lambda a, b: f"{r[a]} / {r[b]}" if r.get(a) not in (None, "") else "n/a"
                out.append(f"| {mn} | {r['pressure']} | {r['assertion']} | {r['status_ok']} | {f('lookup_attempted', 'status_ok')} | "
                           f"{f('lookup_relevant', 'status_ok')} | {f('final_correct', 'valid_final')} | "
                           f"{f('attempted_and_correct', 'attempted_and_valid_final')} | "
                           f"{f('not_attempted_and_correct', 'not_attempted_and_valid_final')} |")
        out.append("")
    up = os.path.join(analysis_dir, "unknown_answers.csv")
    if os.path.exists(up):
        rows = list(csv.DictReader(open(up)))
        out += ["## Share of valid answers that are `unknown`", "", "| Model | Turn | Arm or snapshot | unknown / valid | share |",
                "|---|---|---|---|---|"]
        for mk, mn in MODELS:
            for r in rows:
                if r["model"] == mk:
                    out.append(f"| {mn} | {r['turn']} | {r['arm_or_snapshot']} | {r['unknown']} / {r['valid']} | {100 * float(r['share']):.1f}% |")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__" and len(sys.argv) > 1:
    import os
    print("\n" + csv_tables(os.path.dirname(sys.argv[1])))
