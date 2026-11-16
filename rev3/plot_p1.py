"""Figures for a P1 analysis (reads analysis.json from analyze_p1.py; matplotlib).

  python3 plot_p1.py --analysis runs/X/analysis.json [--out runs/X/figures]

fig_p1_e4          MAIN FIGURE 1: the E4 interaction. Change in accuracy under insistence vs neutral, optional vs
                   supplied route, split by user assertion right / wrong, per model (item-level means, 95% t CI).
fig_p1_funnel      MAIN FIGURE 2: optional-route workflow: lookup attempted, relevant record retrieved, final
                   correct, by pressure, per model; denominators = observed trials per bar (in the caption data).
fig_p1_estimands   MAIN FIGURE 3: forest plot: E1-E4, E1b, S2 per model, insistence and authority vs neutral; point estimate,
                   provisional 95% item-clustered interval (line), assigned-denominator bounds (grey bracket);
                   hollow marker = degenerate interval (zero spread; not precision).
fig_p1_accuracy    final accuracy by pressure x route, one row per model, split by assertion (right/wrong),
                   averaged over snapshot versions.
fig_p1_lookup      optional route: lookup attempt rate by pressure, per model, split by assertion.
fig_p1_validity    validity checks: turn-1 eligibility by snapshot, neutral supplied adoption, neutral
                   optional attempt rate, per model.
Each figure is written as PNG (200 dpi) and PDF. Titles carry the development / provisional label.
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]  # Okabe-Ito; same model, same colour in every figure
MARKERS = ["o", "s", "^", "D"]  # second encoding, so colour is never the only cue
INK, MUTED, GRID = "#222222", "#6b6b6b", "#e6e6e3"
PRESSURES, ROUTES, ASSERTIONS, SNAPS = ("neutral", "insistence", "authority"), ("none", "optional", "supplied"), \
    ("right", "wrong"), ("current", "stale")
ORDER = ["E1_delta_attempt", "E1b_delta_relevant", "E2_delta_acc_supplied", "E3_delivery_effect",
         "E4_moderation", "S2_delta_acc_none"]
NICE = {"E1_delta_attempt": "E1 Δ lookup attempt", "E1b_delta_relevant": "E1b Δ relevant lookup",
        "E2_delta_acc_supplied": "E2 Δ accuracy, supplied", "E3_delivery_effect": "E3 delivery effect",
        "E4_moderation": "E4 moderation by correctness", "S2_delta_acc_none": "S2 Δ accuracy, no evidence"}


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=8)
    ax.grid(axis="both", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def save(fig, out, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def cell_mean(cells, m, assertion, pressure, route, k):
    vals = [cells[m].get(f"{s}/{assertion}/{pressure}/{route}", {}).get(k) for s in SNAPS]
    vals = [v[0] for v in vals if v]
    return sum(vals) / len(vals) if len(vals) == len(SNAPS) else None


def forest(an, models, out, sub):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True)
    for ax, p in zip(axes, ("insistence", "authority")):
        est = an["estimates"].get(p, {})
        style(ax)
        ax.axvline(0, color=MUTED, linewidth=1)
        for j, m in enumerate(models):
            e = est.get(m)
            if not isinstance(e, dict):
                continue
            for i, name in enumerate(ORDER):
                r = e.get(name, {})
                inf = r.get("inference", {})
                y = len(ORDER) - 1 - i + (j - (len(models) - 1) / 2) * 0.17
                b = r.get("bounds") or (None, None)
                if None not in b:
                    ax.plot(b, [y, y], color="#bdbdb8", linewidth=4, solid_capstyle="butt", zorder=1)
                ci = inf.get("ci95_item_t")
                if ci:
                    ax.plot(ci, [y, y], color=COLORS[j], linewidth=2, zorder=2)
                if r.get("estimate") is not None:
                    deg = inf.get("degenerate")
                    ax.plot(r["estimate"], y, MARKERS[j], markersize=7, zorder=3,
                            markerfacecolor="white" if deg else COLORS[j], markeredgecolor=COLORS[j],
                            markeredgewidth=1.6, label=m if i == 0 else None)
        ax.set_yticks(range(len(ORDER)))
        ax.set_yticklabels([NICE[n] for n in reversed(ORDER)], fontsize=8)
        ax.set_title(f"{p} vs neutral", fontsize=10, color=INK)
        ax.set_xlabel("difference (proportion)", fontsize=9, color=INK)
    axes[0].legend(fontsize=8, frameon=False, loc="lower left")
    fig.suptitle("P1 contrasts per model: estimate, provisional 95% item-clustered CI (line), "
                 "assigned-denominator bounds (grey)\n" + sub, fontsize=9, color=INK)
    save(fig, out, "fig_p1_estimands")


def lines_by_pressure(an, models, out, sub, name, key, routes, title, ylabel, by_model_rows):
    cells = an["cells"]
    if by_model_rows:
        fig, axes = plt.subplots(len(models), 2, figsize=(8.5, 2.3 * len(models)), sharex=True, sharey=True,
                                 squeeze=False)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.4), sharey=True, squeeze=False)
    x = range(len(PRESSURES))
    for r, m in enumerate(models if by_model_rows else [None]):
        for c, a in enumerate(ASSERTIONS):
            ax = axes[r][c]
            style(ax)
            series = [(rt, mm) for rt in routes for mm in ([m] if by_model_rows else models)]
            for j, (rt, mm) in enumerate(series):
                ys = [cell_mean(cells, mm, a, p, rt, key) for p in PRESSURES]
                k = j if by_model_rows else models.index(mm)
                ax.plot(x, [v if v is not None else float("nan") for v in ys], marker=MARKERS[k], color=COLORS[k],
                        linewidth=2, markersize=7, label=rt if by_model_rows else mm)
            ax.set_ylim(-0.03, 1.03)
            ax.set_xticks(list(x))
            ax.set_xticklabels(PRESSURES, fontsize=8)
            ax.set_title((f"{m} — " if m else "") + f"user assertion {a}", fontsize=9, color=INK)
            if c == 0:
                ax.set_ylabel(ylabel, fontsize=8, color=INK)
    axes[0][1].legend(fontsize=8, frameon=False, loc="best")
    fig.suptitle(title + "\n" + sub, fontsize=9, color=INK)
    fig.tight_layout()
    save(fig, out, name)


def validity(an, models, out, sub):
    v = an["validity"]
    labels = ["turn-1 eligible,\ncurrent", "turn-1 eligible,\nstale", "neutral supplied\nadoption",
              "neutral optional\nattempt rate"]
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    style(ax)
    w = 0.8 / len(models)
    for j, m in enumerate(models):
        vm = v.get(m, {})
        el = vm.get("turn1_eligible_by_snapshot", {})
        vals = [el.get("current", {}).get("rate"), el.get("stale", {}).get("rate"),
                vm.get("neutral_supplied_adoption", {}).get("rate"), vm.get("neutral_optional_attempt_rate", {}).get("rate")]
        xs = [i + (j - (len(models) - 1) / 2) * w for i in range(len(labels))]
        ax.bar(xs, [x if x is not None else 0 for x in vals], width=w * 0.9, color=COLORS[j], label=m,
               edgecolor="white", linewidth=1)
        for xx, val in zip(xs, vals):
            ax.text(xx, (val or 0) + 0.02, "–" if val is None else f"{val:.2f}", ha="center", fontsize=6, color=INK)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("rate", fontsize=8)
    ax.legend(fontsize=7, frameon=False, ncol=len(models), loc="upper center", bbox_to_anchor=(0.5, -0.2))
    ax.set_title("P1 validity and positive-control checks (must pass before contrasts are read)\n" + sub,
                 fontsize=9, color=INK)
    save(fig, out, "fig_p1_validity")


def _item_delta(trials, m, assertion, route, p, key="final_correct"):
    """Per item: mean over snapshots of (pressure cell mean - neutral cell mean) for one route x assertion."""
    from collections import defaultdict
    cell = defaultdict(list)
    for t in trials:
        if t["model"] == m and t["assertion"] == assertion and t["route"] == route and t.get(key) is not None:
            cell[(t["item_id"], t["snapshot"], t["pressure"])].append(t[key])
    out = []
    for it in sorted({k[0] for k in cell}):
        ds = []
        for snap in SNAPS:
            a, b = cell.get((it, snap, p)), cell.get((it, snap, "neutral"))
            if a and b:
                ds.append(sum(a) / len(a) - sum(b) / len(b))
        if len(ds) == len(SNAPS):
            out.append(sum(ds) / len(ds))
    return out


def e4_figure(trials, models, out, sub, p="insistence"):
    from p1v3.inference import t_interval
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, a in zip(axes, ASSERTIONS):
        style(ax)
        ax.axhline(0, color=MUTED, linewidth=1)
        for j, m in enumerate(models):
            for k, rt in enumerate(("optional", "supplied")):
                d = _item_delta(trials, m, a, rt, p)
                if not d:
                    continue
                x = k + (j - (len(models) - 1) / 2) * 0.12
                mu = 100 * sum(d) / len(d)
                ci = t_interval(d)
                if ci:
                    ax.plot([x, x], [100 * ci[0], 100 * ci[1]], color=COLORS[j], linewidth=2)
                ax.plot(x, mu, MARKERS[j], color=COLORS[j], markersize=7, label=m if k == 0 else None,
                        markerfacecolor=COLORS[j] if (ci and ci[0] != ci[1]) else "white")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["optional lookup", "record supplied"], fontsize=8)
        ax.set_title(f"user assertion {a}", fontsize=9, color=INK)
    axes[0].set_ylabel(f"accuracy change, {p} − neutral (pp)", fontsize=8)
    axes[1].legend(fontsize=7, frameon=False, loc="best")
    fig.suptitle("P1 Figure 1. Pressure penalty by evidence route and user correctness (E3/E4 components)\n"
                 + sub, fontsize=9, color=INK)
    fig.tight_layout()
    save(fig, out, "fig_p1_e4")


def funnel_figure(trials, models, out, sub):
    keys = [("lookup_attempted", "attempted"), ("lookup_relevant", "relevant record"), ("final_correct", "final correct")]
    fig, axes = plt.subplots(1, len(PRESSURES), figsize=(10, 3.6), sharey=True)
    w = 0.8 / len(models)
    for ax, p in zip(axes, PRESSURES):
        style(ax)
        for j, m in enumerate(models):
            ts = [t for t in trials if t["model"] == m and t["route"] == "optional" and t["pressure"] == p
                  and t["status"] == "ok"]
            vals = []
            for k, _ in keys:
                v = [t[k] for t in ts if t.get(k) is not None]
                vals.append(sum(v) / len(v) if v else float("nan"))
            xs = [i + (j - (len(models) - 1) / 2) * w for i in range(len(keys))]
            ax.bar(xs, vals, width=w * 0.9, color=COLORS[j], edgecolor="white", linewidth=1,
                   label=f"{m} (n={len(ts)})")
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels([lbl for _, lbl in keys], fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_title(p, fontsize=9, color=INK)
        ax.legend(fontsize=6, frameon=False, loc="upper right")
    axes[0].set_ylabel("share of ok optional-route trials", fontsize=8)
    fig.suptitle("P1 Figure 2. Optional-route workflow: attempted lookup → relevant record → final correct\n" + sub,
                 fontsize=9, color=INK)
    fig.tight_layout()
    save(fig, out, "fig_p1_funnel")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--out")
    ap.add_argument("--trials", nargs="*", default=None,
                    help="trials.jsonl file(s) for the item-level figures (default: from analysis run_dirs)")
    a = ap.parse_args()
    with open(a.analysis) as f:
        an = json.load(f)
    out = a.out or os.path.join(os.path.dirname(a.analysis), "figures")
    os.makedirs(out, exist_ok=True)
    models = sorted(an["validity"])
    sub = f"{an.get('n_items', '?')} items, {an.get('n_families', '?')} families. DEVELOPMENT cases; intervals provisional."
    synthetic = any(k in d for d in an.get("run_dirs", []) for k in ("synth", "dry", "demo", "scratchpad", "cert"))
    if synthetic:
        sub = "SYNTHETIC DEMO — NOT RESULTS. " + sub
    files = a.trials or [os.path.join(d, "trials.jsonl") for d in an.get("run_dirs", [])]
    trials = []
    for fp in files:
        with open(fp) as f:
            trials += [json.loads(x) for x in f if x.strip()]
    if trials:
        e4_figure(trials, models, out, sub)
        funnel_figure(trials, models, out, sub)
    forest(an, models, out, sub)
    lines_by_pressure(an, models, out, sub, "fig_p1_accuracy", "final_correct", ROUTES,
                      "P1 final accuracy by pressure and evidence route (averaged over snapshots)", "accuracy", True)
    lines_by_pressure(an, models, out, sub, "fig_p1_lookup", "lookup_attempted", ("optional",),
                      "P1 lookup attempt rate, optional route", "attempt rate", False)
    validity(an, models, out, sub)
    print("wrote", sorted(os.listdir(out)))


if __name__ == "__main__":
    main()
