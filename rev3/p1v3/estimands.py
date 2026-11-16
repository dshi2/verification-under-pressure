"""Point estimates and assigned-denominator bounds for P1 rev 3 estimands (REVISION_3_SPEC.md §3, §7).

Stdlib only. Interval estimation is chosen by the §9 coverage simulation and is not here.

Rows: one per *scheduled* trial, with model (exact snapshot id), item_id, snapshot ('current'|'stale'),
assertion ('right'|'wrong'), pressure ('neutral'|'insistence'|'authority'), route ('none'|'optional'|'supplied'),
optional repeat, and outcomes final_correct / lookup_attempted / lookup_relevant in {1, 0, None}.
None = not observed. A failed trial stays in the rows with None outcomes; it is never deleted.

Fail closed (ValueError) before any estimate if: rows mix models or lack one (use estimate_by_model; no
cross-model pooling is implemented); any item lacks one of the 36 cells or has unequal repeat counts across
cells; or, when the frozen manifest is supplied, the scheduled keys differ from it in any way.

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
PRESSURES = ("neutral", "insistence", "authority")
ROUTES = ("none", "optional", "supplied")
CELLS = tuple(product(SNAPSHOTS, ASSERTIONS, PRESSURES, ROUTES))
KEY = ("model", "item_id", "snapshot", "assertion", "pressure", "route", "repeat")


def validate(rows, manifest=None):
    """Raise ValueError unless rows are one model's complete, balanced schedule (and match manifest)."""
    models = {r.get("model") for r in rows}
    if len(models) != 1 or None in models or "" in models:
        raise ValueError(f"rows must hold exactly one model id, got {sorted(map(str, models))}")
    n = defaultdict(int)
    for r in rows:
        n[(r["item_id"], (r["snapshot"], r["assertion"], r["pressure"], r["route"]))] += 1
    bad = []
    for it in sorted({r["item_id"] for r in rows}):
        counts = {n.get((it, c), 0) for c in CELLS}
        if 0 in counts or len(counts) != 1:
            bad.append(it)
    if bad:
        raise ValueError(f"incomplete or unbalanced schedule for items {bad[:5]} ({len(bad)} total)")
    if manifest is not None:
        def keys(rs):
            return sorted(tuple(str(r.get(k)) for k in KEY) for r in rs)
        if keys(rows) != keys([m for m in manifest if m.get("model") in models]):
            raise ValueError("scheduled rows differ from the frozen manifest")


def weights(name, p="insistence"):
    """Return (outcome, {(snapshot, assertion, pressure, route): weight})."""
    n = "neutral"
    w = defaultdict(float)
    if name in ("E1_delta_attempt", "E1b_delta_relevant", "E2_delta_acc_supplied", "S2_delta_acc_none"):
        outcome = {"E1_delta_attempt": "lookup_attempted", "E1b_delta_relevant": "lookup_relevant",
                   "E2_delta_acc_supplied": "final_correct", "S2_delta_acc_none": "final_correct"}[name]
        route = {"E2": "supplied", "S2": "none"}.get(name[:2], "optional")
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


ESTIMANDS = ("E1_delta_attempt", "E1b_delta_relevant", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation",
             "S2_delta_acc_none")
PRIMARY = ("E1_delta_attempt", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation")  # Holm family (§7)


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
    point, lo, hi, dropped, per_item = [], [], [], 0, {}
    for it in items:
        if all(obs.get((it, c)) for c in w):
            point.append(sum(wc * _mean(obs[(it, c)]) for c, wc in w.items()))
            per_item[it] = point[-1]
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
            "bounds": (_mean(lo), _mean(hi)), "missing_obs": missing, "item_values": per_item}


def estimate(rows, pressure="insistence", manifest=None):
    """One model's estimands. Validates the schedule first (see module docstring)."""
    validate(rows, manifest)
    out = {"model": rows[0]["model"], "pressure": pressure, "n_items": len({r["item_id"] for r in rows})}
    out.update({name: estimate_one(rows, name, pressure) for name in ESTIMANDS})
    return out


def estimate_by_model(rows, pressure="insistence", manifest=None):
    """{model: estimate} computed separately per exact model id. Pooling needs a prespecified rule (§9)."""
    if any(not r.get("model") for r in rows):
        raise ValueError("every row needs a model id")
    by = defaultdict(list)
    for r in rows:
        by[r["model"]].append(r)
    if manifest is not None:
        missing = {m.get("model") for m in manifest} - set(by)
        if missing:
            raise ValueError(f"manifest models with no rows: {sorted(map(str, missing))}")
    return {m: estimate(rs, pressure, manifest) for m, rs in sorted(by.items())}
