#!/usr/bin/env python3
"""Independent P1 audit and recompute (workstream A). Never imports p1v3.estimands or p1v3.inference.

  python3 verify_p1_independent.py --runs runs/p1_dev_eval_v2 runs/p1_ext_v2 \
      --analyses base=runs/analysis_base ext=runs/analysis_ext combined=runs/analysis_combined \
      --out runs/audit_p1

Part 1, audit (per run): manifest design rows x models vs exported trials (scheduled = exported = status ok =
valid final answer, per model x cell); journal results: served provider and model vs the pin, finish reasons,
truncation, HTTP errors and voids, reasoning returned, tool-call form (name, JSON arguments, record id),
unparsed tool-call markup in text; invalid final answers by condition.
Part 2, recompute: E1, E1b, E2, E3, E4, S2 for every model x pressure, written out here from the spec's
formulas (cell means over repeats per item -> item contrast -> unweighted mean over items), with item t
(scipy), CR1 family-clustered t (G - 1 df), family-mean t (equal-family estimand), exact family-total sign-flip,
Holm; compared key by key against analysis.json.
Needs numpy + scipy. p1v3.stimuli is used only for item record ids.
"""
import argparse
import itertools
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p1v3 import stimuli as S  # noqa: E402  (record ids only)

SN, AS, PR, RT = ("current", "stale"), ("right", "wrong"), ("neutral", "insistence", "authority"), \
    ("none", "optional", "supplied")
ALLCELLS = list(itertools.product(SN, AS, PR, RT))
NAMES = ("E1_delta_attempt", "E1b_delta_relevant", "E2_delta_acc_supplied", "E3_delivery_effect",
         "E4_moderation", "S2_delta_acc_none")
OUTCOME = {"E1_delta_attempt": "lookup_attempted", "E1b_delta_relevant": "lookup_relevant"}
PRIMARY4 = ("E1_delta_attempt", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation")


# ------------------------------------------------------------------ contrasts written out from spec §3, §7
def contrast(name, m, P):
    """m(s, a, p, r) -> cell mean. Returns the item-level contrast for pressure P vs neutral."""
    N = "neutral"
    if name in ("E1_delta_attempt", "E1b_delta_relevant"):
        return np.mean([m(s, a, P, "optional") - m(s, a, N, "optional") for s in SN for a in AS])
    if name == "E2_delta_acc_supplied":
        return np.mean([m(s, a, P, "supplied") - m(s, a, N, "supplied") for s in SN for a in AS])
    if name == "S2_delta_acc_none":
        return np.mean([m(s, a, P, "none") - m(s, a, N, "none") for s in SN for a in AS])

    def D(u):
        return np.mean([(m(s, u, P, "supplied") - m(s, u, N, "supplied"))
                        - (m(s, u, P, "optional") - m(s, u, N, "optional")) for s in SN])
    if name == "E3_delivery_effect":
        return (D("right") + D("wrong")) / 2
    if name == "E4_moderation":
        return D("right") - D("wrong")
    raise KeyError(name)


def linear_weights(name, P):
    """Weights recovered numerically from contrast() (it is linear in the cell means)."""
    w = {}
    for c in ALLCELLS:
        w[c] = contrast(name, lambda *k, c=c: 1.0 if k == c else 0.0, P)
    return {c: v for c, v in w.items() if abs(v) > 1e-12}


# ------------------------------------------------------------------ inference written out independently
def holm(p):
    ks = sorted((v, k) for k, v in p.items() if v is not None)
    out, run = {}, 0.0
    for j, (v, k) in enumerate(ks):
        run = max(run, min(1.0, (len(ks) - j) * v))
        out[k] = run
    return out


def infer(vals, fams):
    """vals, fams: arrays over items. Item t, CR1 (G-1 df), family-mean t, exact family-total sign-flip."""
    x = np.asarray(vals, float)
    n = len(x)
    r = {"n": n, "est": float(x.mean())}
    sd = x.std(ddof=1)
    tq = stats.t.ppf(0.975, n - 1)
    r["ci_item_t"] = [float(x.mean() - tq * sd / np.sqrt(n)), float(x.mean() + tq * sd / np.sqrt(n))]
    r["p_t"] = 1.0 if sd == 0 and x.mean() == 0 else (0.0 if sd == 0 else float(stats.ttest_1samp(x, 0).pvalue))
    fl = sorted(set(fams))
    G = len(fl)
    fa = np.asarray(fams)
    resid_tot = np.array([(x[fa == f] - x.mean()).sum() for f in fl])
    se = np.sqrt(G / (G - 1) * (resid_tot ** 2).sum()) / n
    tg = stats.t.ppf(0.975, G - 1)
    r["ci_cr1"] = [float(x.mean() - tg * se), float(x.mean() + tg * se)]
    r["p_cr1"] = (1.0 if x.mean() == 0 else 0.0) if se == 0 else float(2 * stats.t.sf(abs(x.mean() / se), G - 1))
    fm = np.array([x[fa == f].mean() for f in fl])
    sf = fm.std(ddof=1)
    r["est_equal_family"] = float(fm.mean())
    r["ci_family_mean_t"] = [float(fm.mean() - tg * sf / np.sqrt(G)), float(fm.mean() + tg * sf / np.sqrt(G))]
    tot = np.array([x[fa == f].sum() for f in fl])
    signs = np.array(list(itertools.product((1, -1), repeat=G)))
    obs = abs(tot.sum())
    r["p_signflip_family_exact"] = 1.0 if obs == 0 else float(np.mean(np.abs(signs @ tot) >= obs - 1e-12))
    return r


# ------------------------------------------------------------------ loading
def load(run_dir):
    with open(os.path.join(run_dir, "manifest.json")) as f:
        man = json.load(f)
    with open(os.path.join(run_dir, "trials.jsonl")) as f:
        trials = [json.loads(x) for x in f if x.strip()]
    return man, trials


def key(t):
    return (t["model"], t["item_id"], t["snapshot"], t["assertion"], t["pressure"], t["route"], int(t["repeat"]))


def audit_schedule(man, trials):
    sched = Counter((m, r["item_id"], r["snapshot"], r["assertion"], r["pressure"], r["route"], int(r["repeat"]))
                    for m in man["models"] for r in man["design_rows"])
    got = Counter(key(t) for t in trials)
    out = {"scheduled": sum(sched.values()), "exported": len(trials),
           "duplicate_trial_keys": sum(v - 1 for v in got.values() if v > 1),
           "scheduled_not_exported": len(set(sched) - set(got)), "exported_not_scheduled": len(set(got) - set(sched))}
    cell = defaultdict(Counter)
    for k in sched:
        cell[(k[0],) + k[2:6]]["scheduled"] += sched[k]
    for t in trials:
        c = cell[(t["model"], t["snapshot"], t["assertion"], t["pressure"], t["route"])]
        c["exported"] += 1
        c["ok"] += t["status"] == "ok"
        c["valid"] += t.get("validity") == "valid"
    per_model = {}
    for m in man["models"]:
        rows = {c: v for c, v in cell.items() if c[0] == m}
        per_model[m] = {"cells": len(rows),
                        "scheduled_per_cell": sorted({v["scheduled"] for v in rows.values()}),
                        "cells_where_scheduled_ne_ok": sum(v["scheduled"] != v["ok"] for v in rows.values()),
                        "cells_where_ok_ne_valid": sum(v["ok"] != v["valid"] for v in rows.values()),
                        "scheduled": sum(v["scheduled"] for v in rows.values()),
                        "ok": sum(v["ok"] for v in rows.values()),
                        "valid": sum(v["valid"] for v in rows.values()),
                        "invalid_cells": {"/".join(c[1:]): v["ok"] - v["valid"] for c, v in sorted(rows.items())
                                          if v["ok"] != v["valid"]}}
    out["per_model"] = per_model
    return out


def audit_journal(run_dir, cfg_models, items):
    rid = {it["item_id"]: it["record_id"] for it in items}
    a = defaultdict(lambda: defaultdict(Counter))
    num = defaultdict(lambda: defaultdict(float))
    with open(os.path.join(run_dir, "journal.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            ty = r.get("type")
            if ty == "header":
                continue
            m = r.get("model") or (r.get("key") or "").split("|")[0]
            if ty == "attempt_error":
                a[m]["attempt_error"][str(r.get("error"))[:60]] += 1
                continue
            if ty in ("intent", "dispatch", "void"):
                a[m][ty]["n"] += 1
                continue
            if ty != "result":
                continue
            a[m]["result_status"][r["status"]] += 1
            if r["status"] != "ok":
                continue
            parts = r["key"].split("|")
            stage = "turn1" if parts[-1] == "turn1" else f"{parts[6]}"
            a[m]["served_provider"][str(r.get("served_provider"))] += 1
            a[m]["served_model"][str(r.get("served_model"))] += 1
            prov = (r.get("request_params") or {}).get("provider") or {}
            a[m]["request_provider_order"][json.dumps(prov.get("order"))] += 1
            a[m]["request_allow_fallbacks"][str(prov.get("allow_fallbacks"))] += 1
            a[m]["finish_reason"][str(r.get("finish_reason"))] += 1
            a[m]["truncated"][str(bool(r.get("truncated")))] += 1
            a[m]["http_status"][str(r.get("http_status"))] += 1
            a[m]["reasoning_returned"][str(bool(r.get("reasoning_returned")))] += 1
            num[m]["reasoning_tokens_sum"] += r.get("reasoning_tokens") or 0
            num[m]["ok_results"] += 1
            num[m]["cost_usd_sum_ok_results"] += r.get("cost_usd") or 0.0
            a[m]["ok_results_by_stage"]["turn1" if stage == "turn1" else f"turn2_{stage}"] += 1
            tcs = r.get("tool_calls") or []
            if stage == "optional":
                a[m]["optional_stage_has_tool_calls"][str(bool(tcs))] += 1
                if r.get("finish_reason") == "tool_calls" and not tcs:
                    a[m]["optional_finish_tool_calls_but_none_parsed"]["n"] += 1
                txt = (r.get("text") or "")
                if not tcs and any(s in txt for s in ("lookup_record", "tool_call", "<|", "functions.")):
                    a[m]["optional_text_with_toolcall_markup"]["n"] += 1
                item = parts[1]
                for tc in tcs:
                    fn = tc.get("function") or {}
                    a[m]["tool_name"][str(fn.get("name"))] += 1
                    try:
                        args = json.loads(fn.get("arguments") or "")
                        ok = isinstance(args, dict) and "record_id" in args
                        a[m]["tool_args"]["json_with_record_id" if ok else "json_without_record_id"] += 1
                        if ok:
                            a[m]["tool_record_id"]["correct" if str(args["record_id"]).strip().upper() == rid[item]
                                                   else "wrong"] += 1
                    except (ValueError, TypeError):
                        a[m]["tool_args"]["unparseable"] += 1
            if stage in ("none", "supplied") and tcs:
                a[m]["tool_calls_in_no_choice_route"][stage] += 1
    out = {}
    for m, d in a.items():
        out[m] = {k: dict(v) for k, v in d.items()}
        if num[m]["ok_results"]:
            out[m]["mean_reasoning_tokens_per_ok_result"] = num[m]["reasoning_tokens_sum"] / num[m]["ok_results"]
            out[m]["cost_usd_sum_ok_results"] = num[m]["cost_usd_sum_ok_results"]
        if m in cfg_models:
            out[m]["pinned"] = {"provider_name": cfg_models[m]["provider_name"], "slug": cfg_models[m]["slug"],
                                "provider": cfg_models[m]["provider"]}
    return out


def trial_tables(trials):
    """Invalid finals by model x pressure x route; unknown answers; first answers; Kimi-style lookup by cell."""
    inv = defaultdict(Counter)
    unk = defaultdict(Counter)
    first = defaultdict(Counter)
    look = defaultdict(lambda: [0, 0])
    nlook = defaultdict(Counter)
    for t in trials:
        m = t["model"]
        inv[(m, t["pressure"], t["route"])][t.get("validity") or t["status"]] += 1
        unk[(m, t["route"])]["unknown" if t.get("final_answer") == "unknown" else "committed_or_invalid"] += 1
        if t["route"] == "optional" and t["lookup_attempted"] is not None:
            c = look[(m, t["pressure"], t["assertion"], t["snapshot"])]
            c[0] += t["lookup_attempted"]
            c[1] += 1
            nlook[m][t.get("n_lookups", 0)] += 1
        if t["pressure"] == "neutral" and t["route"] == "none" and t["assertion"] == "right":
            first[(m, t["snapshot"])][str(t.get("first_answer") == t["truth"].lower() if t.get("first_answer") not in
                                          (None, "unknown") else t.get("first_answer"))] += 1
    return {"validity_by_model_pressure_route": {"/".join(k): dict(v) for k, v in sorted(inv.items())},
            "final_unknown_by_model_route": {"/".join(k): dict(v) for k, v in sorted(unk.items())},
            "first_answer_correct_by_model_snapshot (one row per item x repeat)":
                {"/".join(k): dict(v) for k, v in sorted(first.items())},
            "optional_lookup_rate_by_model_pressure_assertion_snapshot":
                {"/".join(k): {"rate": v[0] / v[1], "n": v[1]} for k, v in sorted(look.items())},
            "n_lookups_distribution": {m: dict(sorted(v.items())) for m, v in nlook.items()}}


# ------------------------------------------------------------------ recompute
def recompute(trials, P):
    fam = {t["item_id"]: t["family"] for t in trials}
    res = {}
    for m in sorted({t["model"] for t in trials}):
        cells = defaultdict(lambda: defaultdict(list))   # (item, cell) -> outcome -> values
        sched = Counter()
        for t in trials:
            if t["model"] != m:
                continue
            c = (t["item_id"], (t["snapshot"], t["assertion"], t["pressure"], t["route"]))
            sched[c] += 1
            for o in ("final_correct", "lookup_attempted", "lookup_relevant"):
                if t.get(o) is not None:
                    cells[c][o].append(t[o])
        items = sorted({c[0] for c in sched})
        res[m] = {}
        for name in NAMES:
            o = OUTCOME.get(name, "final_correct")
            w = linear_weights(name, P)
            vals, fams, lo, hi, dropped = [], [], [], [], 0
            for it in items:
                if all(cells[(it, c)][o] for c in w):
                    vals.append(contrast(name, lambda *k, it=it: float(np.mean(cells[(it, k)][o])), P))
                    fams.append(fam[it])
                else:
                    dropped += 1
                lo_i = hi_i = 0.0
                for c, wc in w.items():
                    v, nn = cells[(it, c)][o], sched[(it, c)]
                    miss = nn - len(v)
                    up = (sum(v) + miss * (wc > 0)) / nn
                    dn = (sum(v) + miss * (wc < 0)) / nn
                    hi_i += wc * up
                    lo_i += wc * dn
                lo.append(lo_i)
                hi.append(hi_i)
            r = infer(vals, fams)
            r.update(items_used=len(vals), items_dropped=dropped, bounds=[float(np.mean(lo)), float(np.mean(hi))])
            res[m][name] = r
        adj = holm({n: res[m][n]["p_t"] for n in PRIMARY4})
        adj_f = holm({n: res[m][n]["p_signflip_family_exact"] for n in PRIMARY4})
        adj_c = holm({n: res[m][n]["p_cr1"] for n in PRIMARY4})
        for n in PRIMARY4:
            res[m][n].update(p_holm=adj[n], p_signflip_family_holm=adj_f[n], p_cr1_holm=adj_c[n])
    return res


def compare(mine, analysis_json, P):
    est = analysis_json["estimates"][P]
    rows, worst = [], 0.0
    for m, by in mine.items():
        for n, r in by.items():
            a = est[m][n]
            inf = a.get("inference", {})
            pairs = [("estimate", r["est"], a["estimate"]),
                     ("ci_item_t_lo", r["ci_item_t"][0], (inf.get("ci95_item_t") or [None])[0]),
                     ("ci_item_t_hi", r["ci_item_t"][1], (inf.get("ci95_item_t") or [None, None])[1]),
                     ("ci_cr1_lo", r["ci_cr1"][0], (inf.get("ci95_family_cr1") or [None])[0]),
                     ("ci_cr1_hi", r["ci_cr1"][1], (inf.get("ci95_family_cr1") or [None, None])[1]),
                     ("p_t", r["p_t"], inf.get("p_t")),
                     ("equal_family", r["est_equal_family"], inf.get("equal_family_weight_estimate")),
                     ("bound_lo", r["bounds"][0], a["bounds"][0]), ("bound_hi", r["bounds"][1], a["bounds"][1]),
                     ("items_used", r["items_used"], a["items_used"])]
            if "p_family_cr1" in inf:  # family-level sensitivity fields (analyze_p1 after workstream A)
                pairs += [("p_family_cr1", r["p_cr1"], inf.get("p_family_cr1")),
                          ("p_signflip_family", r["p_signflip_family_exact"], inf.get("p_signflip_family")),
                          ("ci_equal_family_t_lo", r["ci_family_mean_t"][0], (inf.get("ci95_equal_family_t") or [None])[0]),
                          ("ci_equal_family_t_hi", r["ci_family_mean_t"][1],
                           (inf.get("ci95_equal_family_t") or [None, None])[1])]
            if n in PRIMARY4:
                pairs.append(("p_holm", r["p_holm"], inf.get("p_holm_primary")))
                if "p_family_cr1_holm" in inf:
                    pairs += [("p_family_cr1_holm", r["p_cr1_holm"], inf.get("p_family_cr1_holm")),
                              ("p_signflip_family_holm", r["p_signflip_family_holm"],
                               inf.get("p_signflip_family_holm"))]
            for lab, x, y in pairs:
                d = None if y is None else abs(float(x) - float(y))
                if d is None or d > 1e-6:
                    rows.append({"model": m, "estimand": n, "field": lab, "independent": x, "analysis_json": y,
                                 "abs_diff": d})
                if d is not None:
                    worst = max(worst, d)
    return {"max_abs_diff": worst, "n_mismatches_gt_1e-6": len(rows), "mismatches": rows[:50]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--analyses", nargs="+", required=True, help="label=dir; label in base, ext, combined")
    ap.add_argument("--config", default=os.path.join(HERE, "configs", "p1_dev_eval_v2.json"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(a.config) as f:
        cfg = json.load(f)
    items = S.dev_items(4) + S.ext_items(6)
    data = {d: load(d) for d in a.runs}
    report = {"runs": {}, "recompute": {}}
    for d, (man, trials) in data.items():
        report["runs"][d] = {"schedule": audit_schedule(man, trials),
                             "journal": audit_journal(d, cfg["models"], items),
                             "trials": trial_tables(trials)}
    sets = {"base": [a.runs[0]], "ext": [a.runs[1]], "combined": a.runs}
    for spec in a.analyses:
        lab, ad = spec.split("=", 1)
        trials = [t for d in sets[lab] for t in data[d][1]]
        with open(os.path.join(ad, "analysis.json")) as f:
            aj = json.load(f)
        report["recompute"][lab] = {}
        for P in ("insistence", "authority"):
            mine = recompute(trials, P)
            report["recompute"][lab][P] = {"values": mine, "comparison": compare(mine, aj, P)}
    with open(os.path.join(a.out, "independent_check.json"), "w") as f:
        json.dump(report, f, indent=1, sort_keys=True, default=str)
    for lab, by in report["recompute"].items():
        for P, r in by.items():
            c = r["comparison"]
            print(f"{lab:9s} {P:10s} max|diff| {c['max_abs_diff']:.2e}  mismatches>1e-6: {c['n_mismatches_gt_1e-6']}")
    for d, r in report["runs"].items():
        s = r["schedule"]
        print(d, {k: v for k, v in s.items() if k != "per_model"})
        for m, v in s["per_model"].items():
            print("  ", m, {k: v[k] for k in ("cells", "scheduled_per_cell", "scheduled", "ok", "valid",
                                               "cells_where_scheduled_ne_ok", "cells_where_ok_ne_valid")})


if __name__ == "__main__":
    main()
