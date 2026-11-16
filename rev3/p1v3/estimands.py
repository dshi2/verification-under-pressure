"""Point estimates and assigned-denominator bounds for P1 rev 3 estimands (REVISION_3_SPEC.md §3, §7).

Stdlib only. Interval estimation is chosen by the §9 coverage simulation and is not here.

Rows: one per *scheduled* trial, with item_id, snapshot ('current'|'stale'), assertion ('right'|'wrong'),
pressure ('neutral'|'insistence'|'authority'), route ('none'|'optional'|'supplied') and outcomes
final_correct / lookup_attempted / lookup_relevant in {1, 0, None}. None = not observed.

Every estimand is a fixed linear contrast of cell means: sum over cells of w_c * mean_c, averaged over
items with equal weight (repeats averaged within item x cell; snapshots and assertions weighted equally).
Point estimate: observed outcomes only; an item missing any needed cell is dropped and counted.
Bounds: every scheduled trial counts; missing outcomes are set to 1 where w_c > 0 and 0 where w_c < 0
for the upper bound, and the reverse for the lower. Setting all missing to 0, then all to 1, is not a
bound for contrasts with weights of both signs.
"""
from collections import defaultdict
from itertools import product

SNAPSHOTS = ("current", "stale")
ASSERTIONS = ("right", "wrong")


def weights(name, p="insistence"):
    """Return (outcome, {(snapshot, assertion, pressure, route): weight})."""
    n = "neutral"
    w = defaultdict(float)
    if name in ("E1_delta_attempt", "E1b_delta_relevant", "E2_delta_acc_supplied"):
        outcome = {"E1_delta_attempt": "lookup_attempted", "E1b_delta_relevant": "lookup_relevant",
                   "E2_delta_acc_supplied": "final_correct"}[name]
        route = "supplied" if name.startswith("E2") else "optional"
        for s, a in product(SNAPSHOTS, ASSERTIONS):
            w[(s, a, p, route)] += 0.25
            w[(s, a, n, route)] -= 0.25
        return outcome, dict(w)
    # D(u) averaged over snapshots: (P,sup) - (N,sup) - (P,opt) + (N,opt)
    sign_u = {"E3_delivery_effect": {"right": 0.5, "wrong": 0.5},
              "E4_moderation": {"right": 1.0, "wrong": -1.0}}[name]
    for s, u in product(SNAPSHOTS, ASSERTIONS):
        k = sign_u[u] / 2
        for pr, rt, sg in ((p, "supplied", 1), (n, "supplied", -1), (p, "optional", -1), (n, "optional", 1)):
            w[(s, u, pr, rt)] += sg * k
    return "final_correct", dict(w)


ESTIMANDS = ("E1_delta_attempt", "E1b_delta_relevant", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation")


def _cells(rows, outcome):
    """{(item, cell): [observed values]} and {(item, cell): n scheduled}."""
    obs, sched = defaultdict(list), defaultdict(int)
    for r in rows:
        key = (r["item_id"], (r["snapshot"], r["assertion"], r["pressure"], r["route"]))
        sched[key] += 1
        if r.get(outcome) is not None:
            obs[key].append(float(r[outcome]))
    return obs, sched


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def estimate_one(rows, name, pressure="insistence"):
    outcome, w = weights(name, pressure)
    obs, sched = _cells(rows, outcome)
    items = sorted({r["item_id"] for r in rows})
    point, lo, hi, dropped = [], [], [], 0
    for it in items:
        if all(obs.get((it, c)) for c in w):
            point.append(sum(wc * _mean(obs[(it, c)]) for c, wc in w.items()))
        else:
            dropped += 1
        if all(sched.get((it, c)) for c in w):
            def filled(c, wc, upper):
                v, n = obs.get((it, c), []), sched[(it, c)]
                fill = (n - len(v)) * (1.0 if (wc > 0) == upper else 0.0)
                return (sum(v) + fill) / n
            lo.append(sum(wc * filled(c, wc, False) for c, wc in w.items()))
            hi.append(sum(wc * filled(c, wc, True) for c, wc in w.items()))
    missing = sum(sched[k] - len(obs.get(k, [])) for k in sched if k[1] in w)
    return {"estimate": _mean(point), "items_used": len(point), "items_dropped_incomplete": dropped,
            "bounds": (_mean(lo), _mean(hi)), "missing_obs": missing}


def estimate(rows, pressure="insistence"):
    out = {"pressure": pressure, "n_items": len({r["item_id"] for r in rows})}
    out.update({name: estimate_one(rows, name, pressure) for name in ESTIMANDS})
    return out
