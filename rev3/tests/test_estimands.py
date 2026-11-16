"""Estimator recovery on constructed data with known effects (spec §9 step 3)."""
import itertools
import unittest

from p1v3.estimands import estimate, estimate_by_model

PRESSURES = ("neutral", "insistence", "authority")
ROUTES = ("none", "optional", "supplied")


def build(acc_fn, att_fn=lambda *a: 0.5, rel_fn=None, items=8, repeats=4, model="m1"):
    """Deterministic rows: in each cell, a fraction p of repeats are 1 (p chosen so p*repeats is integral)."""
    rel_fn = rel_fn or att_fn
    rows = []
    for i in range(items):
        for s, a, p, r in itertools.product(("current", "stale"), ("right", "wrong"), PRESSURES, ROUTES):
            pa, pt, pr = acc_fn(s, a, p, r), att_fn(s, a, p, r), rel_fn(s, a, p, r)
            for k in range(repeats):
                rows.append({"model": model, "item_id": f"it{i}", "repeat": k,
                             "snapshot": s, "assertion": a, "pressure": p, "route": r,
                             "final_correct": int(k < pa * repeats),
                             "lookup_attempted": int(k < pt * repeats) if r == "optional" else None,
                             "lookup_relevant": int(k < pr * repeats) if r == "optional" else None})
    return rows


class TestRecovery(unittest.TestCase):
    def test_null_everything(self):
        e = estimate(build(lambda *a: 0.75))
        for k in ("E1_delta_attempt", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation"):
            self.assertAlmostEqual(e[k]["estimate"], 0.0, msg=k)
            self.assertEqual(e[k]["items_used"], 8)

    def test_known_moderation(self):
        # insistence penalty: optional -0.5 when user wrong, -0.25 when right; supplied: 0 penalty.
        def acc(s, a, p, r):
            if p != "insistence" or r != "optional":
                return 0.75
            return 0.25 if a == "wrong" else 0.5
        e = estimate(build(acc))
        # D(right) = 0 - (-0.25) = 0.25 ; D(wrong) = 0 - (-0.5) = 0.5
        self.assertAlmostEqual(e["E3_delivery_effect"]["estimate"], 0.375)
        self.assertAlmostEqual(e["E4_moderation"]["estimate"], -0.25)
        self.assertAlmostEqual(e["E2_delta_acc_supplied"]["estimate"], 0.0)

    def test_attempt_vs_relevant_separated(self):
        # insistence leaves attempts unchanged but halves relevant retrieval (wrong-id calls)
        e = estimate(build(lambda *a: 0.75, att_fn=lambda *a: 0.5,
                           rel_fn=lambda s, a, p, r: 0.25 if p == "insistence" else 0.5))
        self.assertAlmostEqual(e["E1_delta_attempt"]["estimate"], 0.0)
        self.assertAlmostEqual(e["E1b_delta_relevant"]["estimate"], -0.25)

    def test_authority_is_a_separate_contrast(self):
        acc = lambda s, a, p, r: 0.25 if (p == "authority" and r == "optional") else 0.75
        self.assertAlmostEqual(estimate(build(acc))["E3_delivery_effect"]["estimate"], 0.0)
        self.assertAlmostEqual(estimate(build(acc), pressure="authority")["E3_delivery_effect"]["estimate"], 0.5)

    def test_unobserved_cell_drops_item_from_point_but_not_bounds(self):
        rows = build(lambda *a: 0.75)
        for r in rows:
            if r["item_id"] == "it0" and r["pressure"] == "insistence" and r["route"] == "supplied":
                r["final_correct"] = None
        e = estimate(rows)
        self.assertEqual(e["E4_moderation"]["items_used"], 7)
        self.assertEqual(e["E4_moderation"]["items_dropped_incomplete"], 1)
        self.assertEqual(e["E1_delta_attempt"]["items_used"], 8)  # E1 does not need supplied cells
        lo, hi = e["E4_moderation"]["bounds"]
        self.assertLess(lo, hi)  # it0 still in the bounds, with its unobserved cell filled at the extremes

    def test_absent_scheduled_cell_fails_closed(self):
        rows = [r for r in build(lambda *a: 0.75)
                if not (r["item_id"] == "it0" and r["pressure"] == "insistence" and r["route"] == "supplied")]
        with self.assertRaises(ValueError):
            estimate(rows)

    def test_unbalanced_repeats_fail_closed(self):
        rows = build(lambda *a: 0.75)
        rows.append(dict(rows[0], repeat=99))
        with self.assertRaises(ValueError):
            estimate(rows)

    def test_mixed_or_missing_model_fails_closed(self):
        rows = build(lambda *a: 1.0, model="X") + build(lambda *a: 0.0, model="Y")
        with self.assertRaises(ValueError):
            estimate(rows)
        no_model = build(lambda *a: 0.75)
        no_model[0]["model"] = None
        with self.assertRaises(ValueError):
            estimate(no_model)
        with self.assertRaises(ValueError):
            estimate_by_model(no_model)

    def test_reviewer_pooling_example_is_not_reproducible(self):
        # Reviewer case: X always looks up, Y never; X's insistence and Y's neutral outcomes missing.
        # Pooling would give -1.0. Per model, both items are incomplete: no point estimate, full-width bounds.
        x = build(lambda *a: 0.75, att_fn=lambda *a: 1.0, items=1, model="X")
        y = build(lambda *a: 0.75, att_fn=lambda *a: 0.0, items=1, model="Y")
        for rows, p in ((x, "insistence"), (y, "neutral")):
            for r in rows:
                if r["pressure"] == p:
                    r["lookup_attempted"] = None
        out = estimate_by_model(x + y)
        for m in ("X", "Y"):
            self.assertIsNone(out[m]["E1_delta_attempt"]["estimate"])
        self.assertEqual(out["X"]["E1_delta_attempt"]["bounds"], (-1.0, 0.0))
        self.assertEqual(out["Y"]["E1_delta_attempt"]["bounds"], (-1.0, 0.0))  # 0 - [0, 1]; truth 0 inside both
        complete = estimate_by_model(build(lambda *a: 0.75, att_fn=lambda *a: 1.0, model="X")
                                     + build(lambda *a: 0.75, att_fn=lambda *a: 0.0, model="Y"))
        self.assertEqual({m: e["E1_delta_attempt"]["estimate"] for m, e in complete.items()}, {"X": 0.0, "Y": 0.0})

    def test_manifest_mismatch_fails_closed(self):
        rows = build(lambda *a: 0.75, items=2)
        manifest = [{k: r[k] for k in ("model", "item_id", "snapshot", "assertion", "pressure", "route", "repeat")}
                    for r in rows]
        estimate(rows, manifest=manifest)  # exact match passes
        with self.assertRaises(ValueError):
            estimate([r for r in rows if r["item_id"] == "it0"], manifest=manifest)  # whole item absent
        with self.assertRaises(ValueError):
            estimate_by_model(rows, manifest=manifest + [dict(manifest[0], model="Z")])  # model with no rows

    def test_none_outcomes_excluded_and_counted(self):
        rows = build(lambda *a: 0.75)
        for r in rows:
            if r["route"] == "supplied" and r["pressure"] == "insistence":
                r["final_correct"] = None
                break
        e = estimate(rows)
        self.assertEqual(e["E4_moderation"]["missing_obs"], 1)
        self.assertEqual(e["E4_moderation"]["items_used"], 8)

    def test_bounds_equal_point_when_complete(self):
        e = estimate(build(lambda *a: 0.75))
        for k in ("E1_delta_attempt", "E3_delivery_effect", "E4_moderation"):
            lo, hi = e[k]["bounds"]
            self.assertAlmostEqual(lo, e[k]["estimate"])
            self.assertAlmostEqual(hi, e[k]["estimate"])

    def test_bounds_are_sign_aware_extremes(self):
        # All optional attempts missing: E1 bounds must be [-1, 1], not the 0 that all-0 or all-1 fills give.
        rows = build(lambda *a: 0.75, items=1)
        for r in rows:
            if r["route"] == "optional":
                r["lookup_attempted"] = None
        lo, hi = estimate(rows)["E1_delta_attempt"]["bounds"]
        self.assertAlmostEqual(lo, -1.0)
        self.assertAlmostEqual(hi, 1.0)
        self.assertIsNone(estimate(rows)["E1_delta_attempt"]["estimate"])

    def test_bounds_contain_every_completion(self):
        # Brute force: one item, one repeat, 3 missing cells; every 0/1 completion lies inside the bounds.
        import itertools as it
        rows = build(lambda *a: 0.5, items=1, repeats=2)
        miss = [i for i, r in enumerate(rows) if r["route"] in ("optional", "supplied")][:3]
        for i in miss:
            rows[i]["final_correct"] = None
        lo, hi = estimate(rows)["E4_moderation"]["bounds"]
        vals = []
        for fill in it.product((0, 1), repeat=3):
            full = [dict(r) for r in rows]
            for i, v in zip(miss, fill):
                full[i]["final_correct"] = v
            vals.append(estimate(full)["E4_moderation"]["estimate"])
        self.assertAlmostEqual(min(vals), lo)
        self.assertAlmostEqual(max(vals), hi)

    def test_weights_sum_to_zero(self):
        from p1v3.estimands import ESTIMANDS, weights
        for name in ESTIMANDS:
            self.assertAlmostEqual(sum(weights(name)[1].values()), 0.0, msg=name)


if __name__ == "__main__":
    unittest.main()
