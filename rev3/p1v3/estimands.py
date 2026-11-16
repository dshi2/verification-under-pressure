"""Point estimators for P1 revision 3 primary estimands (REVISION_3_SPEC.md §3, §7).

Pure functions, stdlib only. Uncertainty (item-clustered, boundary-valid intervals) is a
separate component, chosen by simulated coverage (§9); not implemented here.

Input: trial rows (dicts) with
  item_id, snapshot ('current'|'stale'), assertion ('right'|'wrong'),
  pressure ('neutral'|'insistence'|'authority'), route ('none'|'optional'|'supplied'),
  final_correct (1/0/None), lookup_attempted (1/0/None), lookup_relevant (1/0/None).
None = not observed (failure, malformed, lost event); excluded from cell means and counted.

Weighting: repeats are averaged within item x cell; items get equal weight; snapshot
versions and assertions get equal weight (the designed 50/50 mix). An item contributes
to an estimand only if every cell that estimand needs has at least one observation;
items dropped this way are counted, never silently ignored.
"""
from collections import defaultdict

SNAPSHOTS = ("current", "stale")
ASSERTIONS = ("right", "wrong")


def _cell_means(rows, outcome):
    acc = defaultdict(list)
    missing = 0
    for r in rows:
        v = r.get(outcome)
        if v is None:
            missing += 1
            continue
        acc[(r["item_id"], r["snapshot"], r["assertion"], r["pressure"], r["route"])].append(float(v))
    return {k: sum(v) / len(v) for k, v in acc.items()}, missing


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _per_item(means, items, fn):
    vals, dropped = [], 0
    for it in items:
        try:
            vals.append(fn(lambda s, a, p, r: means[(it, s, a, p, r)]))
        except KeyError:
            dropped += 1
    return _mean(vals), len(vals), dropped


def estimate(rows, pressure="insistence"):
    """Return E1-E4 point estimates for `pressure` vs neutral, with item counts."""
    items = sorted({r["item_id"] for r in rows})
    acc, miss_acc = _cell_means(rows, "final_correct")
    att, miss_att = _cell_means(rows, "lookup_attempted")
    rel, miss_rel = _cell_means(rows, "lookup_relevant")
    P, N = pressure, "neutral"

    def avg_sa(m, f):
        return _mean([f(m, s, a) for s in SNAPSHOTS for a in ASSERTIONS])

    def d_u(m, u):
        """D(u) averaged over snapshots: pressure penalty change from optional to supplied."""
        return _mean([(m(s, u, P, "supplied") - m(s, u, N, "supplied"))
                      - (m(s, u, P, "optional") - m(s, u, N, "optional")) for s in SNAPSHOTS])

    out = {"pressure": pressure, "n_items": len(items),
           "missing_obs": {"final_correct": miss_acc, "lookup_attempted": miss_att, "lookup_relevant": miss_rel}}
    for name, means, fn in [
        ("E1_delta_attempt", att, lambda m: avg_sa(m, lambda m, s, a: m(s, a, P, "optional") - m(s, a, N, "optional"))),
        ("E1b_delta_relevant", rel, lambda m: avg_sa(m, lambda m, s, a: m(s, a, P, "optional") - m(s, a, N, "optional"))),
        ("E2_delta_acc_supplied", acc, lambda m: avg_sa(m, lambda m, s, a: m(s, a, P, "supplied") - m(s, a, N, "supplied"))),
        ("E3_delivery_effect", acc, lambda m: _mean([d_u(m, u) for u in ASSERTIONS])),
        ("E4_moderation", acc, lambda m: d_u(m, "right") - d_u(m, "wrong")),
    ]:
        est, n, dropped = _per_item(means, items, fn)
        out[name] = {"estimate": est, "items_used": n, "items_dropped_incomplete": dropped}
    return out
