"""Figures for a P1 analysis (reads analysis.json from analyze_p1.py; matplotlib).

  python3 plot_p1.py --analysis runs/X/analysis.json [--out runs/X/figures]

fig_p1_estimands   forest plot: E1-E4, E1b, S2 per model, insistence and authority vs neutral; point estimate,
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

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validated categorical slots 1-4 (light surface)
MARKERS = ["o", "s", "^", "D"]  # second encoding: two slots are below 3:1 contrast
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
    for ext in ("png", "pdf"):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    with open(a.analysis) as f:
        an = json.load(f)
    out = a.out or os.path.join(os.path.dirname(a.analysis), "figures")
    os.makedirs(out, exist_ok=True)
    models = sorted(an["validity"])
    sub = f"{an.get('n_items', '?')} items, {an.get('n_families', '?')} families. DEVELOPMENT cases; intervals provisional."
    forest(an, models, out, sub)
    lines_by_pressure(an, models, out, sub, "fig_p1_accuracy", "final_correct", ROUTES,
                      "P1 final accuracy by pressure and evidence route (averaged over snapshots)", "accuracy", True)
    lines_by_pressure(an, models, out, sub, "fig_p1_lookup", "lookup_attempted", ("optional",),
                      "P1 lookup attempt rate, optional route", "attempt rate", False)
    validity(an, models, out, sub)
    print("wrote", sorted(os.listdir(out)))


if __name__ == "__main__":
    main()
