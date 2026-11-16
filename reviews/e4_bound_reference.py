"""Independent, deliberately conservative E4 precision comparator for P1.

Does NOT select the final interval method. Assumes independent items, each with
complete scheduled cells; repeated calls are nested within item and DO NOT grow n.
Use the 4-primary-contrast alpha appropriate to the governing multiplicity plan.
Missing outcomes may depend arbitrarily on treatment or their unobserved value.

E4 = D(right) - D(wrong), averaged 1/2 over the two snapshots, where
D(u) = [acc(insist,supplied,u) - acc(neutral,supplied,u)]
     - [acc(insist,optional,u) - acc(neutral,optional,u)].
Each independent-item E4 is in [-4,4].
"""
from collections import defaultdict
from dataclasses import dataclass
from math import ceil, log, sqrt

SNAPSHOTS = ("current", "stale")
ASSERTIONS = ("right", "wrong")
PRESSURES = ("insistence", "neutral")
ROUTES = ("supplied", "optional")
CELLS = frozenset((s, a, p, r) for s in SNAPSHOTS for a in ASSERTIONS
                 for p in PRESSURES for r in ROUTES)


def weight(cell):
    s, a, p, r = cell
    return (0.5 * (1 if a == "right" else -1)
            * (1 if p == "insistence" else -1)
            * (1 if r == "supplied" else -1))


@dataclass(frozen=True)
class Trial:
    item_id: str
    snapshot: str
    assertion: str
    pressure: str
    route: str
    final_correct: int | None
    # Every planned repeat requires its own trial record, even when outcome None.


def item_e4_bounds(rows):
    """Return item-level identification interval and observed point, if complete.

    Repeated observations in a cell are averaged; any missing outcome makes the
    observed point partial (None), but always yields an MNAR-safe interval.
    """
    cells = defaultdict(list)
    for t in rows:
        c = (t.snapshot, t.assertion, t.pressure, t.route)
        if c not in CELLS:
            raise ValueError("unplanned cell")
        if type(t.final_correct) is not int and t.final_correct is not None:
            raise ValueError("final_correct must be 0, 1 or None")
        if t.final_correct not in (0, 1, None):
            raise ValueError("final_correct must be 0, 1 or None")
        cells[c].append(t.final_correct)
    if set(cells) != CELLS:
        raise ValueError("scheduled E4 cells absent; supply terminal records for failures")
    lower = upper = observed = 0.0
    complete = True
    for c in CELLS:
        xs = cells[c]
        count = sum(x for x in xs if x is not None)
        unscored = sum(x is None for x in xs)
        w = weight(c)
        a, b = count / len(xs), (count + unscored) / len(xs)
        lower += w * (a if w > 0 else b)
        upper += w * (b if w > 0 else a)
        if unscored:
            complete = False
        else:
            observed += w * a
    return {"bounds": (lower, upper), "complete_point": observed if complete else None,
            "n_scheduled_repeats": sum(map(len, cells.values()))}


def e4_reference(trials, *, alpha=0.05):
    """Two-sided Hoeffding interval using items as independent units.

    For observed/truncated data, combining the worst-case completion interval
    with a distribution-free Hoeffding radius is conservative if item draws are
    independent and bounded. It is not valid under correlated item families.
    """
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    by_item = defaultdict(list)
    for t in trials:
        if not t.item_id:
            raise ValueError("item_id required")
        by_item[t.item_id].append(t)
    if not by_item:
        raise ValueError("at least one independently sampled item required")
    summaries = [item_e4_bounds(rows) for rows in by_item.values()]
    n = len(summaries)
    l = sum(z["bounds"][0] for z in summaries) / n
    u = sum(z["bounds"][1] for z in summaries) / n
    points = [z["complete_point"] for z in summaries]
    point = sum(points) / n if all(x is not None for x in points) else None
    # Hoeffding: P(|mean - E mean| >= t) <= 2 exp(-2n*t² / 8²)
    radius = sqrt(32 * log(2 / alpha) / n)
    return {"n_independent_items": n, "n_scheduled_repeats": sum(z["n_scheduled_repeats"] for z in summaries),
            "complete_case_point": point, "observed_sample_identification_bounds": (l, u),
            "half_width_worst_case": radius,
            "confidence_interval": (max(-4.0, l - radius), min(4.0, u + radius)),
            "validity": "independent-items-only; not family-cluster-safe"}


def sufficient_n_distribution_free(*, half_width=0.075, alpha=0.05):
    """Sufficient independent items for Hoeffding half-width, NOT planned N."""
    if not 0 < half_width < 4 or not 0 < alpha < 1:
        raise ValueError("invalid precision parameters")
    return ceil(32 * log(2 / alpha) / half_width ** 2)
