"""Provisional item-clustered inference for P1 estimands (development reporting; spec §7, §9). Stdlib only.

Every estimand is the mean over items of an item-level contrast d_i (repeats averaged within item x cell), so
the item is the cluster and a one-sample analysis of {d_i} is the cluster-robust analysis (Miller 2024,
"Adding Error Bars to Evals"). Reported per model, per estimand:
- t interval over items (df = n_items - 1), 95%;
- family-clustered interval for the SAME item-weighted mean: cluster-robust (CR1) variance with families as
  clusters, t with n_families - 1 df (items within a family share a template);
- primary p-value: two-sided one-sample t-test on {d_i} (df n_items - 1), matching the t interval; the
  sign-flip randomization p-value is reported as a secondary check only, because it assumes item effects are
  symmetric about 0, which a zero mean does not guarantee (calibration: SIM_P1_COVERAGE.md);
- equal-family-weight estimate (mean of family means), a different estimand, reported as a sensitivity;
- leave-one-family-out range of the estimate;
- `degenerate` when every d_i is equal: the interval then has zero width and is NOT evidence of precision
  (spec §9 forbids reading such an interval); the assigned-denominator bounds still apply.
Holm adjustment (on the t-test p-values) is applied across the primary family E1-E4 within each model x
pressure contrast.

Family-level sensitivity columns (added after SIM_P1_COVERAGE.md §3 R1/R3; the PI has not changed the primary):
- p_family_cr1: t-test matching ci95_family_cr1 (CR1 SE, G - 1 df);
- p_signflip_family: exact sign-flip over family totals (tests the same item-weighted mean); its smallest
  attainable p is 2 / 2^G (0.031 with 6 families, so no Holm rejection over 4 contrasts is possible);
- ci95_equal_family_t: t over family means for the equal-family estimate (a different estimand when family
  sizes differ);
- excludes0_item_t_only: the item t interval excludes 0 but the CR1 family interval does not.

PROVISIONAL: the §9 coverage simulation recommends a family-clustered method (SIM_P1_COVERAGE.md §3) but the PI
has not fixed the confirmatory method. These numbers describe development data and decide no hypothesis.
"""
import math
import random
from itertools import product
from statistics import mean, stdev

B_FLIPS = 20000


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
            c = 1.0 + aa / c
            c = c if abs(c) > 1e-300 else 1e-300
            h *= d * c
        if abs(d * c - 1.0) < 1e-14:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    p = 0.5 * _ibeta(df / 2, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def t_quantile(p, df):
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def t_interval(xs, level=0.95):
    n = len(xs)
    if n < 2:
        return None
    m, sd = mean(xs), stdev(xs)
    h = t_quantile(1 - (1 - level) / 2, n - 1) * sd / math.sqrt(n)
    return [m - h, m + h]


def t_test_p(xs):
    n = len(xs)
    if n < 2:
        return None
    sd = stdev(xs)
    if sd == 0:
        return 1.0 if mean(xs) == 0 else 0.0
    t = mean(xs) / (sd / math.sqrt(n))
    return min(1.0, 2 * (1 - t_cdf(abs(t), n - 1)))


def cr1_family_interval(xs, fams, level=0.95):
    """Cluster-robust CR1 interval for the item-weighted mean, families as clusters, t with G - 1 df."""
    n, G = len(xs), len(set(fams))
    if G < 3:
        return None
    m = mean(xs)
    sums = {}
    for x, f in zip(xs, fams):
        sums[f] = sums.get(f, 0.0) + (x - m)
    se = math.sqrt(G / (G - 1) * sum(v * v for v in sums.values())) / n
    h = t_quantile(1 - (1 - level) / 2, G - 1) * se
    return [m - h, m + h]


def signflip_p(xs, seed=0):
    """Two-sided randomization p-value for H0: d_i symmetric about 0 (mean 0)."""
    n = len(xs)
    if n == 0:
        return None
    obs = abs(sum(xs))
    if obs == 0:
        return 1.0
    if n <= 16:
        hits = sum(abs(sum(x if s else -x for x, s in zip(xs, signs))) >= obs - 1e-12
                   for signs in product((0, 1), repeat=n))
        return hits / 2 ** n
    rng = random.Random(seed)
    hits = sum(abs(sum(x if rng.random() < 0.5 else -x for x in xs)) >= obs - 1e-12 for _ in range(B_FLIPS))
    return (hits + 1) / (B_FLIPS + 1)


def cr1_family_p(xs, fams):
    """Two-sided p for H0: item-weighted mean = 0, CR1 SE with families as clusters, t with G - 1 df.
    The test that matches ci95_family_cr1 (same centre, same SE, same df)."""
    n, G = len(xs), len(set(fams))
    if G < 3:
        return None
    m = mean(xs)
    sums = {}
    for x, f in zip(xs, fams):
        sums[f] = sums.get(f, 0.0) + (x - m)
    se = math.sqrt(G / (G - 1) * sum(v * v for v in sums.values())) / n
    if se == 0:
        return 1.0 if m == 0 else 0.0
    return min(1.0, 2 * (1 - t_cdf(abs(m / se), G - 1)))


def family_signflip_p(xs, fams, seed=0):
    """Two-sided family-level sign-flip p for H0: family totals of d_i symmetric about 0 (cluster randomization).
    Flips whole families: statistic |sum_f s_f T_f| with T_f = sum of d_i in family f, so it tests the same
    item-weighted mean the estimate reports (with equal family sizes this is the flip over family means).
    Exact enumeration when G <= 16 (smallest attainable p = 2 / 2^G), else 20,000 random flips."""
    tot = {}
    for x, f in zip(xs, fams):
        tot[f] = tot.get(f, 0.0) + x
    T = list(tot.values())
    G = len(T)
    if G == 0:
        return None
    obs = abs(sum(T))
    if obs == 0:
        return 1.0
    if G <= 16:
        hits = sum(abs(sum(t if s else -t for t, s in zip(T, signs))) >= obs - 1e-12
                   for signs in product((0, 1), repeat=G))
        return hits / 2 ** G
    rng = random.Random(seed)
    hits = sum(abs(sum(t if rng.random() < 0.5 else -t for t in T)) >= obs - 1e-12 for _ in range(B_FLIPS))
    return (hits + 1) / (B_FLIPS + 1)


def excludes_zero(ci):
    return None if not ci else (ci[0] > 0 or ci[1] < 0)


def summarize(item_values, family_of, seed=0):
    items = sorted(item_values)
    xs = [item_values[i] for i in items]
    out = {"n_items": len(xs), "estimate": mean(xs) if xs else None}
    if len(xs) < 2:
        return dict(out, note="fewer than 2 items with complete cells")
    fams = sorted({family_of[i] for i in items})
    fam_means = [mean(item_values[i] for i in items if family_of[i] == f) for f in fams]
    lofo = [mean(item_values[i] for i in items if family_of[i] != f) for f in fams] if len(fams) > 1 else []
    fam_of_x = [family_of[i] for i in items]
    out.update({"sd_items": stdev(xs), "se_items": stdev(xs) / math.sqrt(len(xs)),
                "ci95_item_t": t_interval(xs), "degenerate": len(set(xs)) == 1,
                "p_t": t_test_p(xs), "p_signflip_secondary": signflip_p(xs, seed),
                "n_families": len(fams),
                "family_sizes": sorted({sum(1 for g in fam_of_x if g == f) for f in fams}),
                "ci95_family_cr1": cr1_family_interval(xs, fam_of_x),
                "equal_family_weight_estimate": mean(fam_means),
                "by_family": {f: m for f, m in zip(fams, fam_means)},
                "leave_one_family_out": [min(lofo), max(lofo)] if lofo else None})
    # Family-level sensitivity (SIM_P1_COVERAGE.md §3 R1/R3). Labelled sensitivity; the primary is unchanged.
    out.update({"p_family_cr1": cr1_family_p(xs, fam_of_x),
                "p_signflip_family": family_signflip_p(xs, fam_of_x, seed),
                "p_signflip_family_min_attainable": (2 / 2 ** len(fams)) if len(fams) <= 16 else None,
                # t over family means (df = F - 1) is the interval for the equal-family estimate, a different
                # estimand from the item-weighted mean whenever family sizes differ (combined: 4 vs 6 items)
                "ci95_equal_family_t": t_interval(fam_means) if len(fams) > 1 else None})
    item_ex, fam_ex = excludes_zero(out["ci95_item_t"]), excludes_zero(out["ci95_family_cr1"])
    out["excludes0_item_t_only"] = bool(item_ex and fam_ex is False and not out["degenerate"])
    return out


def holm(pvals):
    """{name: p} -> {name: Holm-adjusted p}; None p-values are skipped."""
    named = sorted(((p, k) for k, p in pvals.items() if p is not None))
    adj, run, m = {}, 0.0, len(named)
    for j, (p, k) in enumerate(named):
        run = max(run, min(1.0, (m - j) * p))
        adj[k] = run
    return adj
