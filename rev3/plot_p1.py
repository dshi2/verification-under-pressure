"""P1 paper figures. Reads analysis.json from analyze_p1.py and nothing else (matplotlib).

  python3 plot_p1.py --analysis runs/X/analysis.json [--out runs/X/figures]

Every plotted number is an analysis.json value or a fixed linear combination of its `cells`. Nothing is recomputed
from trials, and no interval is computed here: only intervals exported by analyze_p1.py are drawn. A value that is
missing from analysis.json is not drawn (and is labelled where a reader would expect it), never drawn as 0.

Main figures
  fig_p1_e4_interaction  Pressure x evidence-delivery interaction split by the user's asserted value (E3/E4).
                         Panels A/B: insistence - neutral change in final accuracy (pp, snapshot-averaged cell means)
                         under optional lookup and supplied evidence, for a correct (A) and a wrong (B) assertion; the
                         slope of each line is D(u). Panel C: E3 = mean of D(right), D(wrong) and E4 = D(right) -
                         D(wrong) with the exported provisional item-t interval and the family-clustered (CR1) one.
                         Component intervals are drawn only if analyze_p1 exports them (estimates[p][m].components).
  fig_p1_funnel          Optional-route workflow: lookup attempted -> relevant record retrieved -> final correct,
                         neutral vs insistence, per model and assertion, each bar labelled with its denominator.
                         Steps missing from analysis.json are labelled "not exported" (no bar).
  fig_p1_estimands       Forest plot of E1-E4 per model and pressure (insistence, authority vs neutral): estimate,
                         provisional item-t 95% interval (thin), family-clustered CR1 95% interval (thick, light),
                         assigned-denominator bounds (grey). Hollow marker = degenerate interval (zero spread, not
                         precision); dagger = excludes 0 on the item-t interval only.
Appendix
  fig_p1_e4_interaction_authority  as main figure 1, authority vs neutral.
  fig_p1_secondary       E1b and S2 forest (same encoding as fig_p1_estimands).
  fig_p1_batches         base vs extension item set: per-batch estimates and the Welch difference interval.
  fig_p1_accuracy        final accuracy by pressure x route (snapshot-averaged cell means), per model and assertion.
  fig_p1_lookup          optional-route lookup attempt rate by pressure, per model and assertion.
  fig_p1_validity        validity checks per model (turn-1 eligibility, neutral supplied adoption, neutral optional
                         attempt rate).

Each figure is written as PNG (200 dpi), PDF and SVG. Model colour and marker are fixed by model name and are the same
in plot_p2.py (scope-of-trust). Artists carry gids so tests/test_plot_p1.py can read plotted values back.
"""
import argparse
import json
import os
import re
import textwrap
from collections import namedtuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

Style = namedtuple("Style", "label color marker")
# Fixed model -> (label, colour, marker) assignment; identical in scope-of-trust rev3/plot_p2.py. Okabe-Ito colours.
MODEL_STYLE = {
    "gpt-oss-120b": Style("gpt-oss-120b", "#0072B2", "o"),
    "deepseek-v3.2": Style("DeepSeek-V3.2", "#D55E00", "s"),
    "qwen3-235b-a22b-2507": Style("Qwen3-235B-A22B-2507", "#009E73", "^"),
    "kimi-k2-0905": Style("Kimi-K2-0905", "#CC79A7", "D"),
}
INK, MUTED, GRID, BOUND = "#222222", "#6b6b6b", "#ebebeb", "#d6d6d2"
STAMP_COLOR = "#b00020"
LABEL = "DEVELOPMENT cases (builder-written); intervals provisional"
STAMP = "SYNTHETIC DEMO — not results"
SYNTH_RE = re.compile(r"synth|dry|demo|scratchpad|cert|fixture", re.I)
FORMATS = ("png", "pdf", "svg")
PRESSURES, ROUTES, ASSERTIONS, SNAPS = ("neutral", "insistence", "authority"), ("none", "optional", "supplied"), \
    ("right", "wrong"), ("current", "stale")
PRIMARY = ("E1_delta_attempt", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation")
SECONDARY = ("E1b_delta_relevant", "S2_delta_acc_none")
NICE = {"E1_delta_attempt": "E1  Δ lookup attempt\n(optional route)",
        "E1b_delta_relevant": "E1b  Δ relevant lookup\n(optional route)",
        "E2_delta_acc_supplied": "E2  Δ accuracy\n(record supplied)",
        "E3_delivery_effect": "E3  delivery effect\non the pressure penalty",
        "E4_moderation": "E4  E3 moderation by\nuser correctness",
        "S2_delta_acc_none": "S2  Δ accuracy\n(no evidence route)"}
SHORT = {"E1_delta_attempt": "E1", "E1b_delta_relevant": "E1b", "E2_delta_acc_supplied": "E2",
         "E3_delivery_effect": "E3", "E4_moderation": "E4", "S2_delta_acc_none": "S2"}
FUNNEL = (("lookup_attempted", "attempted\nlookup"), ("lookup_relevant", "relevant\nrecord"),
          ("final_correct", "final\ncorrect"))

plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "xtick.labelsize": 8,
                     "ytick.labelsize": 8, "legend.fontsize": 8, "figure.facecolor": "white",
                     "axes.facecolor": "white", "savefig.facecolor": "white", "svg.fonttype": "none",
                     "pdf.fonttype": 42, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK})


# ---- data access (analysis.json only) -----------------------------------------------------------------------

def model_list(an):
    present = set(an.get("validity") or {}) | set(an.get("cells") or {})
    unknown = present - set(MODEL_STYLE)
    if unknown:
        raise SystemExit(f"no fixed style for {sorted(unknown)}: add it to MODEL_STYLE here and in plot_p2.py")
    return [m for m in MODEL_STYLE if m in present]


def pp(v):
    return None if v is None else 100.0 * v


def cell(an, m, snap, a, p, r, key):
    """(mean, n) for one snapshot/assertion/pressure/route cell, or None if analysis.json has no value."""
    v = ((an.get("cells") or {}).get(m) or {}).get(f"{snap}/{a}/{p}/{r}", {}).get(key)
    if not v or v[0] is None or not v[1]:
        return None
    return float(v[0]), int(v[1])


def snap_mean(an, m, a, p, r, key):
    """Equal-weight mean over the two snapshot versions (the estimands' weighting); None if either is missing."""
    vs = [cell(an, m, s, a, p, r, key) for s in SNAPS]
    return None if any(v is None for v in vs) else sum(v[0] for v in vs) / len(vs)


def pooled(an, m, a, p, r, key):
    """(events, n) pooled over snapshot versions, from cell means x n; None if either snapshot is missing."""
    vs = [cell(an, m, s, a, p, r, key) for s in SNAPS]
    if any(v is None for v in vs):
        return None
    return int(round(sum(mu * n for mu, n in vs))), sum(n for _, n in vs)


def route_delta(an, m, a, r, p):
    """acc(p) - acc(neutral) in one route and assertion, snapshot-averaged; None if any cell is missing."""
    x, y = snap_mean(an, m, a, p, r, "final_correct"), snap_mean(an, m, a, "neutral", r, "final_correct")
    return None if x is None or y is None else x - y


def decomposition(an, m, p):
    """The E3/E4 components recombined from cells: delta[u][route], D[u] = delta_supplied - delta_optional,
    E3 = mean_u D[u], E4 = D[right] - D[wrong] (spec §3). Equals the item-weighted estimands when every item has
    every cell (items_dropped_incomplete = 0 and missing_obs = 0); checked by consistency()."""
    d = {u: {r: route_delta(an, m, u, r, p) for r in ROUTES} for u in ASSERTIONS}
    D = {u: (None if None in (d[u]["supplied"], d[u]["optional"]) else d[u]["supplied"] - d[u]["optional"])
         for u in ASSERTIONS}
    ok = None not in D.values()
    return {"delta": d, "D": D, "E3": (D["right"] + D["wrong"]) / 2 if ok else None,
            "E4": D["right"] - D["wrong"] if ok else None}


def estimand(an, p, m, name):
    e = (an.get("estimates") or {}).get(p, {}).get(m)
    return e.get(name) if isinstance(e, dict) else None


def consistency(an, m, p):
    """max |recombined E3/E4 - exported E3/E4| (proportion), or None if not checkable. Uses the exported D[u]
    (item-weighted, exact) when analyze_p1 provides components; otherwise the cell recombination, which differs
    slightly when final answers are missing (cells pool trials, the estimands weight items equally)."""
    D = {u: exported_D(an, p, m, u) for u in ASSERTIONS}
    if any(v is None for v in D.values()):
        dec = decomposition(an, m, p)
        D = dec["D"]
    else:
        D = {u: v["estimate"] for u, v in D.items()}
    if None in D.values():
        return None
    rec = {"E3_delivery_effect": (D["right"] + D["wrong"]) / 2, "E4_moderation": D["right"] - D["wrong"]}
    diffs = []
    for name, v in rec.items():
        r = estimand(an, p, m, name)
        if not r or r.get("estimate") is None:
            return None
        diffs.append(abs(v - r["estimate"]))
    return max(diffs)


def _components(an, p, m):
    e = (an.get("estimates") or {}).get(p, {}).get(m)
    return (e.get("components") if isinstance(e, dict) else None) or {}


def exported_component(an, p, m, u, r):
    """analyze_p1 export estimates[p][m].components.delta_acc[u][route] (item-weighted, with intervals)."""
    v = ((_components(an, p, m).get("delta_acc") or {}).get(u) or {}).get(r)
    return v if isinstance(v, dict) and v.get("estimate") is not None else None


def exported_D(an, p, m, u):
    v = (_components(an, p, m).get("D") or {}).get(u)
    return v if isinstance(v, dict) and v.get("estimate") is not None else None


def is_synthetic(analysis_path, an):
    paths = [analysis_path] + list(an.get("run_dirs") or [])
    return any(SYNTH_RE.search(os.path.basename(os.path.normpath(p)) or "") or
               SYNTH_RE.search(os.path.basename(os.path.dirname(os.path.abspath(p)))) for p in paths if p)


def subtitle(an):
    return f"{an.get('n_items', '?')} items, {an.get('n_families', '?')} families, 4 models. {LABEL}."


# ---- drawing helpers ----------------------------------------------------------------------------------------

def style(ax, grid_axis="x"):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=8)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def model_handles(models):
    return [Line2D([], [], marker=MODEL_STYLE[m].marker, color=MODEL_STYLE[m].color, linestyle="", markersize=7)
            for m in models], [MODEL_STYLE[m].label for m in models]


def interval_handles():
    return ([Line2D([], [], color=MUTED, linewidth=1.5), Line2D([], [], color=MUTED, alpha=0.35, linewidth=5),
             Line2D([], [], color=BOUND, linewidth=7),
             Line2D([], [], marker="o", linestyle="", markerfacecolor="white", markeredgecolor=MUTED)],
            ["item-t 95% (provisional)", "family CR1 95% (df = families − 1)", "assigned-denominator bounds",
             "degenerate interval (zero spread)"])


def finish(fig, title, footer, synthetic, handles=None, labels=None, ncol=None):
    """Title on top. Legend below the axes with the wrapped footer as its title, so constrained layout reserves
    room for both and nothing overlaps."""
    fig.suptitle(title, fontsize=10.5, color=INK)
    width = int(fig.get_size_inches()[0] * 15.5)
    leg = fig.legend(handles or [], labels or [], loc="outside lower center", ncol=ncol or max(1, len(handles or [])),
                     frameon=False, fontsize=8, title="\n".join(textwrap.wrap(footer, width, break_on_hyphens=False)), title_fontsize=8,
                     alignment="center")
    leg.get_title().set_color(MUTED)
    leg.get_title().set_gid("footer")
    if synthetic:
        fig.text(0.5, 0.5, STAMP, ha="center", va="center", rotation=22, fontsize=34, color=STAMP_COLOR, alpha=0.22,
                 fontweight="bold", zorder=100, gid="synthetic_stamp")
    return fig


def hinterval(ax, y, r, m, gid, bounds=True):
    """One forest row in pp. Returns True if the item-t interval excludes 0 but the CR1 interval does not."""
    s = MODEL_STYLE[m]
    inf = r.get("inference") or {}
    b = r.get("bounds")
    if bounds and b and None not in b:
        ax.plot([pp(min(b)), pp(max(b))], [y, y], color=BOUND, linewidth=7, solid_capstyle="butt", zorder=1,
                gid=f"{gid}/bounds")
    cr1, it = inf.get("ci95_family_cr1"), inf.get("ci95_item_t")
    if cr1 and None not in cr1:
        ax.plot([pp(cr1[0]), pp(cr1[1])], [y, y], color=s.color, alpha=0.35, linewidth=5, solid_capstyle="butt",
                zorder=2, gid=f"{gid}/cr1")
    if it and None not in it:
        ax.plot([pp(it[0]), pp(it[1])], [y, y], color=s.color, linewidth=1.5, zorder=3, gid=f"{gid}/item")
    if r.get("estimate") is not None:
        deg = bool(inf.get("degenerate"))
        ax.plot([pp(r["estimate"])], [y], s.marker, markersize=6.5, linestyle="", zorder=4,
                markerfacecolor="white" if deg else s.color, markeredgecolor=s.color, markeredgewidth=1.3,
                gid=f"{gid}/est")
    if "excludes0_item_t_only" in inf:  # analyze_p1's own flag
        item_only = bool(inf["excludes0_item_t_only"])
    else:
        item_only = bool(it and cr1 and None not in it and None not in cr1 and (it[0] > 0 or it[1] < 0)
                         and cr1[0] <= 0 <= cr1[1])
    if item_only:
        ax.text(pp(max(it[1], cr1[1])), y, " †", fontsize=9, color=INK, va="center", ha="left", gid=f"{gid}/dagger")
    return item_only


def missing_text(ax, x, y, gid, text="not in\nanalysis.json", **kw):
    ax.text(x, y, text, ha="center", va="center", fontsize=7, color=MUTED, style="italic", gid=gid, **kw)


# ---- main figure 1: interaction -----------------------------------------------------------------------------

def fig_interaction(an, models, ctx, p="insistence"):
    fig = plt.figure(figsize=(11.5, 4.6), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.25])
    axA = fig.add_subplot(gs[0])
    axB = fig.add_subplot(gs[1], sharey=axA)
    axC = fig.add_subplot(gs[2])
    xs = {"optional": 0.0, "supplied": 1.0}
    n = len(models)
    ys_all, n_missing, exported_any = [], 0, False
    for ax, u, letter in ((axA, "right", "A"), (axB, "wrong", "B")):
        style(ax, "y")
        ax.axhline(0, color=MUTED, linewidth=1, zorder=0)
        for j, m in enumerate(models):
            s = MODEL_STYLE[m]
            dx = (j - (n - 1) / 2) * 0.05
            pts = []
            for r in ("optional", "supplied"):
                comp = exported_component(an, p, m, u, r)
                v = comp["estimate"] if comp else route_delta(an, m, u, r, p)
                if v is None:
                    n_missing += 1
                    missing_text(ax, xs[r] + dx, 0, f"e4/missing/{p}/{m}/{u}/{r}", "n/a")
                    continue
                pts.append((xs[r] + dx, pp(v)))
                ys_all.append(pp(v))
                deg = False
                if comp:
                    exported_any = True
                    inf = comp.get("inference") or {}
                    deg = bool(inf.get("degenerate"))
                    cr1, ci = inf.get("ci95_family_cr1"), inf.get("ci95_item_t")
                    if cr1 and None not in cr1:
                        ax.plot([xs[r] + dx] * 2, [pp(cr1[0]), pp(cr1[1])], color=s.color, alpha=0.35, linewidth=5,
                                solid_capstyle="butt", zorder=2, gid=f"e4/cr1/{p}/{m}/{u}/{r}")
                        ys_all += [pp(cr1[0]), pp(cr1[1])]
                    if ci and None not in ci:
                        ax.plot([xs[r] + dx] * 2, [pp(ci[0]), pp(ci[1])], color=s.color, linewidth=1.4, zorder=3,
                                gid=f"e4/ci/{p}/{m}/{u}/{r}")
                        ys_all += [pp(ci[0]), pp(ci[1])]
                ax.plot([xs[r] + dx], [pp(v)], s.marker, markersize=7, linestyle="", zorder=4,
                        markerfacecolor="white" if deg else s.color, markeredgecolor=s.color if deg else "white",
                        markeredgewidth=1.3 if deg else 0.7, gid=f"e4/pt/{p}/{m}/{u}/{r}")
            if len(pts) == 2:
                ax.plot([q[0] for q in pts], [q[1] for q in pts], color=s.color, linewidth=1.6, zorder=3,
                        gid=f"e4/line/{p}/{m}/{u}")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["optional lookup", "record supplied"])
        ax.set_xlim(-0.35, 1.35)
        ax.set_title(f"{letter}. User asserts the {'correct' if u == 'right' else 'wrong'} value", color=INK)
    axA.set_ylabel(f"Δ final accuracy, {p} − neutral (pp)")
    plt.setp(axB.get_yticklabels(), visible=False)
    if ys_all:
        lo, hi = min(ys_all + [0]), max(ys_all + [0])
        pad = max(2.0, 0.08 * (hi - lo))
        axA.set_ylim(lo - pad, hi + pad)
    # panel C: E3 and E4 with exported intervals
    style(axC, "x")
    axC.axvline(0, color=MUTED, linewidth=1, zorder=0)
    names = ("E3_delivery_effect", "E4_moderation")
    yt, yl = [], []
    for g, name in enumerate(names):
        base = (len(names) - 1 - g) * (n + 1)
        for j, m in enumerate(models):
            y = base + (n - 1 - j)
            r = estimand(an, p, m, name)
            if r:
                hinterval(axC, y, r, m, f"e4/{p}/{m}/{SHORT[name]}", bounds=False)
            else:
                missing_text(axC, 0, y, f"e4/missing/{p}/{m}/{SHORT[name]}", "n/a")
        yt.append(base + (n - 1) / 2)
        yl.append({"E3_delivery_effect": "E3 = mean of\nD(right), D(wrong)",
                   "E4_moderation": "E4 =\nD(right) − D(wrong)"}[name])
    axC.set_yticks(yt)
    axC.set_yticklabels(yl)
    axC.set_ylim(-0.8, len(names) * (n + 1) - 1.2)
    axC.set_xlabel("estimate (pp)")
    axC.set_title("C. E3 and E4 with exported 95% intervals", color=INK)
    checks = [consistency(an, m, p) for m in models]
    if any(c is None for c in checks):
        note = "E3/E4 recombination not checkable (missing cells)"
    elif max(checks) < 1e-9:
        note = "D(right) and D(wrong) recombine exactly to the exported E3 and E4"
    else:
        note = (f"the points recombine to the exported E3 and E4 within {100 * max(checks):.2f} pp (cell means pool "
                "trials; the estimands weight items equally; a few final answers are missing)")
    comp_note = ("item-weighted components exported by analyze_p1, with item-t (thin) and family CR1 (thick) 95% "
                 "intervals; descriptive, not separate hypotheses" if exported_any else
                 "points are snapshot-averaged cell means without intervals (components not exported)")
    h, l = model_handles(models)
    ih, il = interval_handles()
    h += [ih[0], ih[1], ih[3]]
    l += [il[0], il[1], il[3]]
    if n_missing:
        note += f"; {n_missing} component(s) missing, labelled n/a"
    footer = f"Slope of each line = D(u). Panels A/B: {comp_note}; {note}. {ctx['sub']}"
    return finish(fig, f"P1 Figure 1. Pressure × evidence delivery, by user correctness ({p} vs neutral)",
                  footer, ctx["synthetic"], h, l, ncol=7)


# ---- main figure 2: workflow funnel -------------------------------------------------------------------------

COUNT_KEYS = {"lookup_attempted": ("attempted", "status_ok"), "lookup_relevant": ("relevant", "status_ok"),
              "final_correct": ("final_correct", "valid_final")}


def funnel_value(an, m, a, p, key):
    """(rate, events, n) for one funnel step, summed over both snapshot versions. Uses the exported `counts`
    block (events / explicit denominator: status ok for the lookup steps, valid final answer for correctness);
    falls back to cell mean x n. None if analysis.json has neither."""
    num, den = COUNT_KEYS[key]
    cs = [((an.get("cells") or {}).get(m) or {}).get(f"{s}/{a}/{p}/optional", {}).get("counts") for s in SNAPS]
    if all(c and c.get(num) is not None and c.get(den) for c in cs):
        k, n = sum(c[num] for c in cs), sum(c[den] for c in cs)
        return k / n, k, n
    c = pooled(an, m, a, p, "optional", key)
    if c is None:
        return None
    k, n = c
    return k / n, k, n


def scheduled(an, m, a, p):
    cs = [((an.get("cells") or {}).get(m) or {}).get(f"{s}/{a}/{p}/optional", {}).get("counts") for s in SNAPS]
    return sum(c["scheduled"] for c in cs) if all(c and c.get("scheduled") for c in cs) else None


def fig_funnel(an, models, ctx, pressures=("neutral", "insistence")):
    fig, axes = plt.subplots(len(models), 2, figsize=(10, 2.05 * len(models) + 1.0), sharey=True, squeeze=False,
                             layout="constrained")
    w = 0.38
    n_missing_steps = set()
    for i, m in enumerate(models):
        s = MODEL_STYLE[m]
        for c, a in enumerate(ASSERTIONS):
            ax = axes[i][c]
            style(ax, "y")
            dens = {}
            for k, (key, _) in enumerate(FUNNEL):
                for q, p in enumerate(pressures):
                    x = k + (q - (len(pressures) - 1) / 2) * w
                    v = funnel_value(an, m, a, p, key)
                    if v is None:
                        if q == 0:
                            n_missing_steps.add(key)
                            missing_text(ax, k, 0.5, f"funnel/missing/{m}/{a}/{key}", "not exported\nby analyze_p1")
                        continue
                    rate, ev, nn = v
                    dens.setdefault(p, {})[COUNT_KEYS[key][1]] = nn
                    solid = p != "neutral"
                    ax.bar([x], [rate], width=w * 0.92, color=s.color if solid else "white", edgecolor=s.color,
                           linewidth=1.2, hatch=None if solid else "////", alpha=1.0, zorder=2,
                           gid=f"funnel/bar/{m}/{a}/{p}/{key}")
                    ax.text(x, rate + 0.03, f"{ev}/{nn}", ha="center", va="bottom", fontsize=7, color=INK,
                            gid=f"funnel/label/{m}/{a}/{p}/{key}")
            ax.set_xticks(range(len(FUNNEL)))
            ax.set_xticklabels([lbl for _, lbl in FUNNEL] if i == len(models) - 1 else [""] * len(FUNNEL))
            ax.set_ylim(0, 1.18)
            ax.set_yticks([0, 0.5, 1])
            ax.set_yticklabels(["0", "50%", "100%"])
            trip = {p: (scheduled(an, m, a, p) or "?", d.get("status_ok", "?"), d.get("valid_final", "?"))
                    for p, d in dens.items()}
            if len(set(trip.values())) == 1:
                t = next(iter(trip.values()))
                den_txt = f"per bar: {t[0]} scheduled, {t[1]} ok, {t[2]} valid"
            else:
                den_txt = " · ".join(f"{p} {'/'.join(map(str, t))}" for p, t in trip.items()) + \
                    " (scheduled/ok/valid)"
            ax.set_title(f"{s.label}, user asserts {'correct' if a == 'right' else 'wrong'} value\n{den_txt}",
                         fontsize=8.5, color=INK, gid=f"funnel/title/{m}/{a}")
    h = [Patch(facecolor="white", edgecolor=MUTED, hatch="////"), Patch(facecolor=MUTED, edgecolor=MUTED)]
    l = ["neutral assertion (hatched)", "insistence (solid)"]
    mh, ml = model_handles(models)
    miss = (" Relevant retrieval per cell is not exported by analyze_p1 yet (labelled, not drawn)."
            if "lookup_relevant" in n_missing_steps else "")
    footer = ("Optional route only; both snapshot versions summed. Bar labels are events / denominator: lookup "
              "attempted and relevant record (correct id) over trials with status ok; final correct over trials with a "
              "valid final answer (an 'unknown' answer counts as not correct). Shares are unconditional, so final "
              "correct is not nested in the lookup steps; descriptive, no intervals."
              f"{miss} {ctx['sub']}")
    return finish(fig, "P1 Figure 2. Optional-route workflow: attempted lookup → relevant record → final correct",
                  footer, ctx["synthetic"], h + mh, l + ml, ncol=6)


# ---- main figure 3: forest ----------------------------------------------------------------------------------

def fig_forest(an, models, ctx, names=PRIMARY, pressures=("insistence", "authority"), title=None):
    n = len(models)
    fig, axes = plt.subplots(len(names), len(pressures), figsize=(10.5, 0.5 * n * len(names) + 1.8),
                             sharey=True, squeeze=False, layout="constrained")
    daggers = []
    for i, name in enumerate(names):
        vals = []
        for c, p in enumerate(pressures):
            ax = axes[i][c]
            style(ax, "x")
            ax.axvline(0, color=MUTED, linewidth=1, zorder=0)
            for j, m in enumerate(models):
                y = n - 1 - j
                r = estimand(an, p, m, name)
                if not r or r.get("estimate") is None:
                    missing_text(ax, 0, y, f"forest/missing/{p}/{m}/{SHORT[name]}", "n/a")
                    continue
                if hinterval(ax, y, r, m, f"forest/{p}/{m}/{SHORT[name]}"):
                    daggers.append(f"{MODEL_STYLE[m].label} {SHORT[name]} {p}")
                inf = r.get("inference") or {}
                for k in ("ci95_item_t", "ci95_family_cr1"):
                    vals += [pp(v) for v in (inf.get(k) or []) if v is not None]
                vals += [pp(v) for v in (r.get("bounds") or []) if v is not None] + [pp(r["estimate"])]
            ax.set_yticks(range(n))
            ax.set_yticklabels([MODEL_STYLE[m].label for m in reversed(models)])
            ax.set_ylim(-0.6, n - 0.4)
            if i == 0:
                ax.set_title(f"{p} vs neutral", color=INK)
            if c == 0:
                ax.set_ylabel(NICE[name], rotation=0, ha="right", va="center", fontsize=8.5)
            if i == len(names) - 1:
                ax.set_xlabel("difference (pp)")
        if vals:
            lo, hi = min(vals + [0]), max(vals + [0])
            pad = max(1.0, 0.1 * (hi - lo))
            for c in range(len(pressures)):
                axes[i][c].set_xlim(lo - pad, hi + pad * 1.6)
    h, l = model_handles(models)
    ih, il = interval_handles()
    dag = (" † excludes 0 on the item-t interval but not on the family CR1 interval: " + "; ".join(daggers) + "."
           if daggers else "")
    footer = (f"Holm across E1–E4 within model × pressure (p in analysis.md). Each panel row has its own x scale."
              f"{dag} {ctx['sub']}")
    return finish(fig, title or "P1 Figure 3. Primary contrasts E1–E4 per model and pressure", footer,
                  ctx["synthetic"], h + ih, l + il, ncol=4)


# ---- appendix -----------------------------------------------------------------------------------------------

def fig_batches(an, models, ctx, p="insistence", names=PRIMARY):
    b = an.get("batches") or {}
    runs = list((b.get("per_batch") or {}).keys())
    diff = (b.get("difference") or {}).get(p, {})
    n = len(models)
    fig, axes = plt.subplots(1, len(names), figsize=(11.5, 3.6), sharey=True, squeeze=False, layout="constrained")
    for ax, name in zip(axes[0], names):
        style(ax, "x")
        ax.axvline(0, color=MUTED, linewidth=1, zorder=0)
        for j, m in enumerate(models):
            s = MODEL_STYLE[m]
            d = (diff.get(m) or {}).get(name)
            y = n - 1 - j
            if not d or d.get("diff") is None:
                missing_text(ax, 0, y, f"batches/missing/{m}/{SHORT[name]}", "n/a")
                continue
            ci = d.get("ci95_welch")
            if ci and None not in ci:
                ax.plot([pp(ci[0]), pp(ci[1])], [y, y], color=s.color, linewidth=1.5, zorder=2,
                        gid=f"batches/ci/{m}/{SHORT[name]}")
            ax.plot([pp(d["diff"])], [y], s.marker, color=s.color, markersize=6.5, linestyle="", zorder=3,
                    gid=f"batches/est/{m}/{SHORT[name]}")
        ax.set_yticks(range(n))
        ax.set_yticklabels([MODEL_STYLE[m].label for m in reversed(models)])
        ax.set_ylim(-0.6, n - 0.4)
        ax.set_title(SHORT[name] + " " + NICE[name].split("  ", 1)[1].replace("\n", " "), fontsize=8.5)
        ax.set_xlabel("batch 2 − batch 1 (pp)")
    items = []
    for k, rd in enumerate(runs):
        pb = (b["per_batch"][rd].get(p) or {})
        used = sorted({(pb.get(m) or {}).get(names[0], {}).get("items_used") for m in models} - {None})
        items.append(f"batch {k + 1} = {os.path.basename(rd)} ({'/'.join(map(str, used))} items)")
    h, l = model_handles(models)
    footer = (f"{'; '.join(items)}. Difference of per-batch item-weighted estimates with a Welch 95% interval over "
              f"items (exported by analyze_p1). Secondary robustness check, not a replication. {ctx['sub']}")
    return finish(fig, f"Appendix. Item-set robustness: extension − base ({p} vs neutral)", footer,
                  ctx["synthetic"], h, l)


ROUTE_LS = {"none": ":", "optional": "--", "supplied": "-"}


def fig_lines(an, models, ctx, key, routes, name_title, ylabel):
    if len(routes) == 1:
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True, squeeze=False, layout="constrained")
    else:
        fig, axes = plt.subplots(len(models), 2, figsize=(8.5, 1.9 * len(models) + 1.0), sharex=True, sharey=True,
                                 squeeze=False, layout="constrained")
    x = list(range(len(PRESSURES)))
    rows = [None] if len(routes) == 1 else models
    for i, row_m in enumerate(rows):
        for c, a in enumerate(ASSERTIONS):
            ax = axes[i][c]
            style(ax, "y")
            for m in ([row_m] if row_m else models):
                s = MODEL_STYLE[m]
                for rt in routes:
                    ys = [snap_mean(an, m, a, p, rt, key) for p in PRESSURES]
                    ax.plot(x, [pp(v) if v is not None else float("nan") for v in ys], marker=s.marker,
                            color=s.color, linestyle=ROUTE_LS[rt], linewidth=1.5, markersize=6,
                            gid=f"lines/{key}/{m}/{a}/{rt}")
            ax.set_ylim(-3, 103)
            ax.set_xticks(x)
            ax.set_xticklabels(PRESSURES)
            ax.set_title(((MODEL_STYLE[row_m].label + ", ") if row_m else "") +
                         f"user asserts {'correct' if a == 'right' else 'wrong'} value", fontsize=8.5)
            if c == 0:
                ax.set_ylabel(ylabel)
    h, l = model_handles(models)
    if len(routes) > 1:
        h += [Line2D([], [], color=MUTED, linestyle=ROUTE_LS[r]) for r in routes]
        l += [f"route: {r}" for r in routes]
    footer = f"Snapshot-averaged cell means from analysis.json; no intervals (descriptive). {ctx['sub']}"
    return finish(fig, name_title, footer, ctx["synthetic"], h, l, ncol=7)


def fig_validity(an, models, ctx):
    labels = [("turn1_current", "turn-1 eligible,\ncurrent snapshot"), ("turn1_stale", "turn-1 eligible,\nstale snapshot"),
              ("adoption", "neutral supplied\nadoption"), ("attempt", "neutral optional\nlookup attempt")]
    fig, ax = plt.subplots(figsize=(9, 3.4), layout="constrained")
    style(ax, "y")
    n = len(models)
    for j, m in enumerate(models):
        s = MODEL_STYLE[m]
        vm = (an.get("validity") or {}).get(m, {})
        el = vm.get("turn1_eligible_by_snapshot") or {}
        vals = {"turn1_current": el.get("current"), "turn1_stale": el.get("stale"),
                "adoption": vm.get("neutral_supplied_adoption"), "attempt": vm.get("neutral_optional_attempt_rate")}
        for i, (k, _) in enumerate(labels):
            x = i + (j - (n - 1) / 2) * 0.17
            v = vals[k]
            if not v or v.get("rate") is None:
                missing_text(ax, x, 50, f"validity/missing/{m}/{k}", "n/a")
                continue
            ax.plot([x], [pp(v["rate"])], s.marker, color=s.color, markersize=7, linestyle="", clip_on=False,
                    markeredgecolor="white", markeredgewidth=0.7, gid=f"validity/est/{m}/{k}")
            ax.text(x, pp(v["rate"]) - 6, f"{100 * v['rate']:.1f}\nn={v.get('n', '?')}", ha="center", va="top",
                    fontsize=7, color=INK)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([lbl for _, lbl in labels])
    ax.set_ylim(-22, 105)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("rate (%)")
    h, l = model_handles(models)
    footer = ("Rates from analysis.json validity (no intervals). A low neutral optional attempt rate limits that "
              f"model's E1. {ctx['sub']}")
    return finish(fig, "Appendix. P1 validity checks per model", footer, ctx["synthetic"], h, l)


# ---- assembly -----------------------------------------------------------------------------------------------

FIGURES = {
    "fig_p1_e4_interaction": lambda an, ms, c: fig_interaction(an, ms, c, "insistence"),
    "fig_p1_funnel": fig_funnel,
    "fig_p1_estimands": fig_forest,
    "fig_p1_e4_interaction_authority": lambda an, ms, c: fig_interaction(an, ms, c, "authority"),
    "fig_p1_secondary": lambda an, ms, c: fig_forest(an, ms, c, SECONDARY,
                                                     title="Appendix. Secondary contrasts E1b and S2"),
    "fig_p1_batches": fig_batches,
    "fig_p1_accuracy": lambda an, ms, c: fig_lines(an, ms, c, "final_correct", ROUTES,
                                                   "Appendix. Final accuracy by pressure and evidence route",
                                                   "accuracy (%)"),
    "fig_p1_lookup": lambda an, ms, c: fig_lines(an, ms, c, "lookup_attempted", ("optional",),
                                                 "Appendix. Lookup attempt rate, optional route", "attempt rate (%)"),
    "fig_p1_validity": fig_validity,
}


def make_context(analysis_path, an, synthetic=False):
    return {"synthetic": synthetic or is_synthetic(analysis_path, an), "sub": subtitle(an)}


def build(an, models, ctx, names=None):
    out = {}
    for name, f in FIGURES.items():
        if names and name not in names:
            continue
        if name == "fig_p1_batches" and not (an.get("batches") or {}).get("difference"):
            continue
        out[name] = f(an, models, ctx)
    return out


def save(fig, out, name):
    for ext in FORMATS:
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--out")
    ap.add_argument("--synthetic", action="store_true", help="stamp SYNTHETIC DEMO regardless of path")
    a = ap.parse_args(argv)
    with open(a.analysis) as f:
        an = json.load(f)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.analysis)), "figures")
    os.makedirs(out, exist_ok=True)
    models = model_list(an)
    ctx = make_context(a.analysis, an, a.synthetic)
    for p in ("insistence", "authority"):
        for m in models:
            c = consistency(an, m, p)
            if c is not None and c > 1e-9:
                print(f"note {m} {p}: cell recombination differs from exported E3/E4 by {100 * c:.3f} pp")
    figs = build(an, models, ctx)
    for name, fig in figs.items():
        save(fig, out, name)
    print(f"synthetic stamp: {ctx['synthetic']}; wrote {len(figs) * len(FORMATS)} files to {out}")
    return out


if __name__ == "__main__":
    main()
