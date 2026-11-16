"""Provisional item-clustered inference for P1 estimands (development reporting; spec §7, §9). Stdlib only.

Every estimand is the mean over items of an item-level contrast d_i (repeats averaged within item x cell), so
the item is the cluster and a one-sample analysis of {d_i} is the cluster-robust analysis (Miller 2024,
"Adding Error Bars to Evals"). Reported per model, per estimand:
- t interval over items (df = n_items - 1), 95%;
- family-clustered t interval over family means (df = n_families - 1), a sensitivity check because items
  within a family share a template;
- two-sided sign-flip randomization p-value for mean d = 0 (exact when n <= 16, else 20,000 seeded flips);
- leave-one-family-out range of the estimate;
- `degenerate` when every d_i is equal: the interval then has zero width and is NOT evidence of precision
  (spec §9 forbids reading such an interval); the assigned-denominator bounds still apply.
Holm adjustment is applied across the primary family E1-E4 within each model x pressure contrast.

PROVISIONAL: §9's coverage simulation has not yet selected the confirmatory interval method. These numbers
describe development data and decide no hypothesis.
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


def summarize(item_values, family_of, seed=0):
    items = sorted(item_values)
    xs = [item_values[i] for i in items]
    out = {"n_items": len(xs), "estimate": mean(xs) if xs else None}
    if len(xs) < 2:
        return dict(out, note="fewer than 2 items with complete cells")
    fams = sorted({family_of[i] for i in items})
    fam_means = [mean(item_values[i] for i in items if family_of[i] == f) for f in fams]
    lofo = [mean(item_values[i] for i in items if family_of[i] != f) for f in fams] if len(fams) > 1 else []
    out.update({"sd_items": stdev(xs), "se_items": stdev(xs) / math.sqrt(len(xs)),
                "ci95_item_t": t_interval(xs), "degenerate": len(set(xs)) == 1,
                "p_signflip": signflip_p(xs, seed),
                "n_families": len(fams), "ci95_family_t": t_interval(fam_means) if len(fams) >= 3 else None,
                "leave_one_family_out": [min(lofo), max(lofo)] if lofo else None})
    return out


def holm(pvals):
    """{name: p} -> {name: Holm-adjusted p}; None p-values are skipped."""
    named = sorted(((p, k) for k, p in pvals.items() if p is not None))
    adj, run, m = {}, 0.0, len(named)
    for j, (p, k) in enumerate(named):
        run = max(run, min(1.0, (m - j) * p))
        adj[k] = run
    return adj
