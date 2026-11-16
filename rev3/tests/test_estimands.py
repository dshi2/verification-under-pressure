"""Estimator recovery on constructed data with known effects (spec §9 step 3)."""
import itertools
import unittest

from p1v3.estimands import estimate

PRESSURES = ("neutral", "insistence", "authority")
ROUTES = ("none", "optional", "supplied")


def build(acc_fn, att_fn=lambda *a: 0.5, rel_fn=None, items=8, repeats=4):
    """Deterministic rows: in each cell, a fraction p of repeats are 1 (p chosen so p*repeats is integral)."""
    rel_fn = rel_fn or att_fn
    rows = []
    for i in range(items):
        for s, a, p, r in itertools.product(("current", "stale"), ("right", "wrong"), PRESSURES, ROUTES):
            pa, pt, pr = acc_fn(s, a, p, r), att_fn(s, a, p, r), rel_fn(s, a, p, r)
            for k in range(repeats):
                rows.append({"item_id": f"it{i}", "snapshot": s, "assertion": a, "pressure": p, "route": r,
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

    def test_missing_cells_drop_item_and_are_counted(self):
        rows = [r for r in build(lambda *a: 0.75)
                if not (r["item_id"] == "it0" and r["pressure"] == "insistence" and r["route"] == "supplied")]
        e = estimate(rows)
        self.assertEqual(e["E4_moderation"]["items_used"], 7)
        self.assertEqual(e["E4_moderation"]["items_dropped_incomplete"], 1)
        self.assertEqual(e["E1_delta_attempt"]["items_used"], 8)  # E1 does not need supplied cells

    def test_none_outcomes_excluded_and_counted(self):
        rows = build(lambda *a: 0.75)
        rows[0]["final_correct"] = None
        e = estimate(rows)
        self.assertEqual(e["missing_obs"]["final_correct"], 1)
        self.assertEqual(e["E4_moderation"]["items_used"], 8)


if __name__ == "__main__":
    unittest.main()
