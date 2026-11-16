"""Independent synthetic tests, no API/model calls."""
import itertools
import math
import unittest

from e4_bound_reference import CELLS, Trial, e4_reference, item_e4_bounds, sufficient_n_distribution_free


def synthetic_item(name, fn, repeats=1):
    return [Trial(name, *cell, fn(cell, k)) for cell, k in itertools.product(sorted(CELLS), range(repeats))]


class E4BoundReferenceTests(unittest.TestCase):
    def test_null_at_perfect_accuracy_not_zero_width(self):
        rows = [t for i in range(100) for t in synthetic_item(str(i), lambda c, k: 1)]
        r = e4_reference(rows)
        self.assertAlmostEqual(r["complete_case_point"], 0)
        self.assertGreater(r["half_width_worst_case"], .075)
        self.assertLess(r["confidence_interval"][0], 0)

    def test_known_effect_of_one(self):
        # D(right)=1 via optional-insistence wrong, D(wrong)=0; E4 = 1.
        def result(c, k):
            s, a, p, r = c
            return int(not (a == "right" and p == "insistence" and r == "optional"))
        z = item_e4_bounds(synthetic_item("a", result))
        self.assertAlmostEqual(z["complete_point"], 1.0)
        self.assertEqual(z["bounds"], (1.0, 1.0))

    def test_missing_sign_aware_extremes(self):
        rows = synthetic_item("a", lambda c, k: None)
        z = item_e4_bounds(rows)
        self.assertAlmostEqual(z["bounds"][0], -4.0)
        self.assertAlmostEqual(z["bounds"][1], 4.0)
        self.assertIsNone(z["complete_point"])

    def test_completion_bruteforce(self):
        rows = synthetic_item("a", lambda c, k: 0)
        first = rows[:3]
        for t in first:
            rows[rows.index(t)] = Trial(t.item_id, t.snapshot, t.assertion, t.pressure, t.route, None)
        lo, hi = item_e4_bounds(rows)["bounds"]
        results=[]
        for bits in itertools.product((0,1), repeat=3):
            full = list(rows)
            for j, v in enumerate(bits):
                t=full[j]
                full[j]=Trial(t.item_id,t.snapshot,t.assertion,t.pressure,t.route,v)
            results.append(item_e4_bounds(full)["complete_point"])
        self.assertAlmostEqual(lo, min(results))
        self.assertAlmostEqual(hi, max(results))

    def test_repeats_are_not_items(self):
        rows=[t for i in range(3) for t in synthetic_item(str(i),lambda c,k:1, repeats=25)]
        result=e4_reference(rows)
        self.assertEqual(result["n_independent_items"], 3)
        self.assertEqual(result["n_scheduled_repeats"],3*16*25)
        self.assertGreater(result["half_width_worst_case"],1)

    def test_missing_scheduled_cell_is_error(self):
        rows=synthetic_item("a",lambda c,k:1)
        with self.assertRaises(ValueError):
            item_e4_bounds(rows[1:])

    def test_invalid_outcome_is_error(self):
        with self.assertRaises(ValueError):
            item_e4_bounds(synthetic_item("a",lambda c,k:2))
        with self.assertRaises(ValueError):
            item_e4_bounds(synthetic_item("a",lambda c,k:True))

    def test_not_family_cluster_safe(self):
        r=e4_reference([t for i in range(8) for t in synthetic_item(str(i),lambda c,k:0)])
        self.assertIn("not family-cluster-safe",r["validity"])

    def test_conservative_threshold_is_not_sample_plan(self):
        n=sufficient_n_distribution_free(half_width=.075,alpha=.05)
        self.assertGreater(n,20000)
        self.assertEqual(n, math.ceil(32*math.log(40)/(.075**2)))

    def test_alpha_monotonicity(self):
        data=[t for i in range(40) for t in synthetic_item(str(i),lambda c,k:0)]
        self.assertGreater(e4_reference(data,alpha=.01)["half_width_worst_case"],
                           e4_reference(data,alpha=.05)["half_width_worst_case"])


if __name__ == "__main__":
    unittest.main()
