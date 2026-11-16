"""Family-level sensitivity inference (p1v3.inference; SIM_P1_COVERAGE.md §3 R1/R3)."""
import math
import random
import unittest
from itertools import product
from statistics import mean, stdev

from p1v3.inference import (cr1_family_interval, cr1_family_p, family_signflip_p, holm, summarize, t_interval,
                            t_quantile)


def balanced(seed=1, G=6, k=4):
    rng = random.Random(seed)
    xs, fams = [], []
    for g in range(G):
        u = rng.gauss(0, 0.05)
        for _ in range(k):
            xs.append(0.02 + u + rng.gauss(0, 0.03))
            fams.append(f"f{g}")
    return xs, fams


class TestFamilyInference(unittest.TestCase):
    def test_cr1_equals_family_mean_t_when_balanced(self):
        xs, fams = balanced()
        fm = [mean(x for x, f in zip(xs, fams) if f == g) for g in sorted(set(fams))]
        a, b = cr1_family_interval(xs, fams), t_interval(fm)
        self.assertAlmostEqual(a[0], b[0], places=12)
        self.assertAlmostEqual(a[1], b[1], places=12)

    def test_cr1_p_matches_cr1_interval(self):
        xs, fams = balanced(seed=3)
        lo, hi = cr1_family_interval(xs, fams)
        G = len(set(fams))
        se = (hi - lo) / 2 / t_quantile(0.975, G - 1)
        tstat = mean(xs) / se
        # p at |t| = t_{0.975} is 0.05; check monotone agreement with the interval at the boundary
        p = cr1_family_p(xs, fams)
        self.assertEqual(p < 0.05, lo > 0 or hi < 0)
        self.assertGreater(abs(tstat), 0)

    def test_family_signflip_exact_brute_force_and_floor(self):
        xs = [0.1, 0.2, 0.05, 0.3, -0.02, 0.15, 0.1, 0.2, 0.0, 0.1, 0.12, 0.3]
        fams = [f"f{i // 2}" for i in range(12)]          # 6 families of 2
        T = [xs[2 * g] + xs[2 * g + 1] for g in range(6)]
        obs = abs(sum(T))
        brute = sum(abs(sum(s * t for s, t in zip(sg, T))) >= obs - 1e-12 for sg in product((1, -1), repeat=6)) / 64
        self.assertAlmostEqual(family_signflip_p(xs, fams), brute)
        self.assertAlmostEqual(family_signflip_p(xs, fams), 2 / 64)  # all totals positive -> the floor 2/2^G

    def test_family_signflip_uses_totals_when_unbalanced(self):
        # one big family with negative items, small families positive: totals-based test differs from means-based
        xs = [-0.1] * 6 + [0.05, 0.05] * 4 + [0.05] * 2
        fams = ["big"] * 6 + [f"s{i // 2}" for i in range(8)] + ["s4"] * 2
        p = family_signflip_p(xs, fams)
        T = {}
        for x, f in zip(xs, fams):
            T[f] = T.get(f, 0) + x
        t = list(T.values())
        obs = abs(sum(t))
        brute = sum(abs(sum(s * v for s, v in zip(sg, t))) >= obs - 1e-12
                    for sg in product((1, -1), repeat=len(t))) / 2 ** len(t)
        self.assertAlmostEqual(p, brute)

    def test_no_holm_rejection_possible_with_six_families(self):
        p = {f"E{i}": 2 / 64 for i in range(1, 5)}
        self.assertTrue(all(v >= 0.05 for v in holm(p).values()))

    def test_summarize_flags_item_only_exclusion(self):
        # strong family heterogeneity: item t excludes 0, family interval does not
        xs, fams = [], []
        for g, u in enumerate((0.20, -0.08, 0.15, -0.05, 0.12, -0.02)):
            for j in range(6):
                xs.append(u + 0.001 * j)
                fams.append(f"f{g}")
        fam_of = {f"i{k}": f for k, f in enumerate(fams)}
        s = summarize({f"i{k}": x for k, x in enumerate(xs)}, fam_of)
        self.assertTrue(s["ci95_item_t"][0] > 0)
        self.assertTrue(s["ci95_family_cr1"][0] < 0 < s["ci95_family_cr1"][1])
        self.assertTrue(s["excludes0_item_t_only"])
        self.assertAlmostEqual(s["p_signflip_family_min_attainable"], 2 / 64)
        self.assertIn("ci95_equal_family_t", s)

    def test_summarize_keeps_existing_keys(self):
        xs, fams = balanced(seed=5)
        fam_of = {f"i{k}": f for k, f in enumerate(fams)}
        s = summarize({f"i{k}": x for k, x in enumerate(xs)}, fam_of)
        for k in ("ci95_item_t", "ci95_family_cr1", "p_t", "p_signflip_secondary", "equal_family_weight_estimate",
                  "leave_one_family_out", "degenerate"):
            self.assertIn(k, s)
        self.assertFalse(math.isnan(s["p_family_cr1"]))
        self.assertGreater(stdev(xs), 0)


if __name__ == "__main__":
    unittest.main()
