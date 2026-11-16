"""plot_p1.py draws exactly what analysis.json says, and never draws a missing value.

Every check reads coordinates back from the matplotlib artists (located by gid) and compares them with analysis.json
values in percentage points. Run from rev3/: python3 -m unittest tests.test_plot_p1
"""
import json
import os
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402

import plot_p1 as P  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = [os.path.join(HERE, "runs", d, "analysis.json") for d in ("analysis_combined", "analysis_base", "analysis_ext")]
MODELS = list(P.MODEL_STYLE)


def gids(fig):
    return {a.get_gid(): a for a in fig.findobj(lambda o: isinstance(o, (Line2D, Rectangle, Text))) if a.get_gid()}


def texts(fig):
    return [t.get_text() for t in fig.findobj(Text) if t.get_text().strip()]


def fixture():
    """Small analysis.json-shaped dict: known cell means, two estimands, one deliberately missing cell."""
    cells = {}
    for j, m in enumerate(MODELS):
        cells[m] = {}
        for s in P.SNAPS:
            for a in P.ASSERTIONS:
                for p in P.PRESSURES:
                    for r in P.ROUTES:
                        v = (0.9 - 0.1 * j - 0.2 * (p == "insistence") * (r == "optional") * (a == "wrong")
                             + 0.05 * (s == "stale") - 0.03 * (r == "none"))
                        c = {"final_correct": [round(v, 6), 100]}
                        if r == "optional":
                            c["lookup_attempted"] = [0.8 - 0.1 * (p == "insistence"), 100]
                        cells[m][f"{s}/{a}/{p}/{r}"] = c
    del cells[MODELS[3]]["stale/wrong/insistence/optional"]  # missing cell -> nothing drawn there
    est = {}
    for p in ("insistence", "authority"):
        est[p] = {}
        for j, m in enumerate(MODELS):
            e = {}
            for i, name in enumerate(P.PRIMARY + P.SECONDARY):
                x = 0.01 * (i + 1) * (j + 1) * (1 if p == "insistence" else -1)
                deg = (j == 1 and name == "E1_delta_attempt")
                e[name] = {"estimate": x, "bounds": [x - 0.01, x + 0.02], "items_used": 10,
                           "inference": {"ci95_item_t": [x, x] if deg else [x - 0.02, x + 0.03],
                                         "ci95_family_cr1": [x, x] if deg else [x - 0.04, x + 0.05],
                                         "degenerate": deg}}
            if j == 2:
                del e["E2_delta_acc_supplied"]  # missing estimand -> "n/a", never a 0 marker
            est[p][m] = e
    validity = {m: {"turn1_eligible_by_snapshot": {"current": {"rate": 1.0, "n": 10}, "stale": {"rate": 0.9, "n": 10}},
                    "neutral_supplied_adoption": {"rate": 0.95, "n": 10},
                    "neutral_optional_attempt_rate": None if j == 0 else {"rate": 0.5, "n": 10}}
                for j, m in enumerate(MODELS)}
    return {"cells": cells, "estimates": est, "validity": validity, "n_items": 10, "n_families": 2,
            "run_dirs": ["runs/fixture_run"]}


class Base(unittest.TestCase):
    def assertSeq(self, got, want, msg=None):
        self.assertEqual(len(got), len(want), msg)
        for g, w in zip(got, want):
            self.assertAlmostEqual(float(g), float(w), places=9, msg=msg)

    def ctx(self, an, synthetic=False):
        return {"synthetic": synthetic, "sub": P.subtitle(an)}

    def tearDown(self):
        plt.close("all")


class TestFixedStyle(Base):
    def test_palette_and_markers_are_fixed_by_name(self):
        want = {"gpt-oss-120b": ("#0072B2", "o"), "deepseek-v3.2": ("#D55E00", "s"),
                "qwen3-235b-a22b-2507": ("#009E73", "^"), "kimi-k2-0905": ("#CC79A7", "D")}
        self.assertEqual({m: (s.color, s.marker) for m, s in P.MODEL_STYLE.items()}, want)
        self.assertEqual(len({s.marker for s in P.MODEL_STYLE.values()}), 4)

    def test_model_order_does_not_depend_on_sorting(self):
        an = {"validity": {m: {} for m in sorted(MODELS)}}
        self.assertEqual(P.model_list(an), MODELS)
        with self.assertRaises(SystemExit):
            P.model_list({"validity": {"unknown-model": {}}})

    def test_every_estimate_marker_uses_its_model_style(self):
        an = fixture()
        figs = P.build(an, MODELS, self.ctx(an))
        for name, fig in figs.items():
            for gid, a in gids(fig).items():
                if not isinstance(a, Line2D) or not ("/est" in gid or "/pt/" in gid):
                    continue
                m = next(m for m in MODELS if f"/{m}/" in gid + "/")
                face, edge = to_hex(a.get_markerfacecolor()), to_hex(a.get_markeredgecolor())
                self.assertEqual((edge if face == "#ffffff" else face).upper(), P.MODEL_STYLE[m].color, f"{name} {gid}")
                self.assertEqual(a.get_marker(), P.MODEL_STYLE[m].marker, f"{name} {gid}")
            self.assertTrue(any(P.LABEL in t.replace("\n", " ") for t in texts(fig)), name)
            small = [t for t in fig.findobj(Text) if t.get_text().strip() and t.get_fontsize() < 7]
            self.assertEqual(small, [], name)


class TestFixture(Base):
    def setUp(self):
        self.an = fixture()

    def test_forest_coordinates_and_degenerate(self):
        fig = P.fig_forest(self.an, MODELS, self.ctx(self.an))
        g = gids(fig)
        for p in ("insistence", "authority"):
            for j, m in enumerate(MODELS):
                for name in P.PRIMARY:
                    key = f"forest/{p}/{m}/{P.SHORT[name]}"
                    r = self.an["estimates"][p][m].get(name)
                    if r is None:
                        self.assertNotIn(f"{key}/est", g)
                        self.assertIn(f"forest/missing/{p}/{m}/{P.SHORT[name]}", g)
                        continue
                    self.assertSeq(g[f"{key}/est"].get_xdata(), [100 * r["estimate"]], key)
                    self.assertSeq(g[f"{key}/item"].get_xdata(), [100 * v for v in r["inference"]["ci95_item_t"]])
                    self.assertSeq(g[f"{key}/cr1"].get_xdata(), [100 * v for v in r["inference"]["ci95_family_cr1"]])
                    self.assertSeq(g[f"{key}/bounds"].get_xdata(), [100 * v for v in r["bounds"]])
                    hollow = to_hex(g[f"{key}/est"].get_markerfacecolor()) == "#ffffff"
                    self.assertEqual(hollow, r["inference"]["degenerate"], key)

    def test_interaction_points_are_cell_recombination(self):
        fig = P.fig_interaction(self.an, MODELS, self.ctx(self.an))
        g = gids(fig)
        for m in MODELS:
            for u in P.ASSERTIONS:
                for r in ("optional", "supplied"):
                    key = f"e4/pt/insistence/{m}/{u}/{r}"
                    vals = []
                    for p in ("insistence", "neutral"):
                        cs = [self.an["cells"][m].get(f"{s}/{u}/{p}/{r}") for s in P.SNAPS]
                        vals.append(None if None in cs else sum(c["final_correct"][0] for c in cs) / 2)
                    if None in vals:
                        self.assertNotIn(key, g)  # missing cell: no point, no zero
                        self.assertIn(f"e4/missing/insistence/{m}/{u}/{r}", g)
                    else:
                        self.assertSeq(g[key].get_ydata(), [100 * (vals[0] - vals[1])], key)
                        self.assertNotIn(f"e4/ci/insistence/{m}/{u}/{r}", g)  # no exported interval -> none drawn

    def test_decomposition_formula(self):
        d = P.decomposition(self.an, MODELS[0], "insistence")
        for u in P.ASSERTIONS:
            self.assertAlmostEqual(d["D"][u], d["delta"][u]["supplied"] - d["delta"][u]["optional"])
        self.assertAlmostEqual(d["E3"], (d["D"]["right"] + d["D"]["wrong"]) / 2)
        self.assertAlmostEqual(d["E4"], d["D"]["right"] - d["D"]["wrong"])
        self.assertAlmostEqual(d["D"]["wrong"], 0.2)  # fixture: insistence costs 0.2 only in optional/wrong
        self.assertAlmostEqual(d["D"]["right"], 0.0)

    def test_funnel_missing_steps_are_labelled_not_zero(self):
        fig = P.fig_funnel(self.an, MODELS, self.ctx(self.an))
        g = gids(fig)
        for m in MODELS:
            for a in P.ASSERTIONS:
                self.assertNotIn(f"funnel/bar/{m}/{a}/neutral/lookup_relevant", g)
                self.assertIn(f"funnel/missing/{m}/{a}/lookup_relevant", g)
                h = g[f"funnel/bar/{m}/{a}/neutral/lookup_attempted"].get_height()
                self.assertAlmostEqual(h, 0.8)
        self.assertNotIn(f"funnel/bar/{MODELS[3]}/wrong/insistence/final_correct", g)

    def test_validity_missing_rate_not_drawn(self):
        g = gids(P.fig_validity(self.an, MODELS, self.ctx(self.an)))
        self.assertNotIn(f"validity/est/{MODELS[0]}/attempt", g)
        self.assertIn(f"validity/missing/{MODELS[0]}/attempt", g)
        self.assertSeq(g[f"validity/est/{MODELS[1]}/attempt"].get_ydata(), [50.0])

    def test_synthetic_stamp_and_files(self):
        tmp = tempfile.mkdtemp()
        run = os.path.join(tmp, "synth_run")
        os.makedirs(run)
        an = dict(fixture(), run_dirs=[run])
        path = os.path.join(run, "analysis.json")
        with open(path, "w") as f:
            json.dump(an, f)
        out = P.main(["--analysis", path])
        for name in ("fig_p1_e4_interaction", "fig_p1_funnel", "fig_p1_estimands"):
            for ext in P.FORMATS:
                self.assertGreater(os.path.getsize(os.path.join(out, f"{name}.{ext}")), 1000)
        ctx = P.make_context(path, an)
        self.assertTrue(ctx["synthetic"])
        fig = P.fig_forest(an, MODELS, ctx)
        self.assertTrue(any(t.get_gid() == "synthetic_stamp" for t in fig.findobj(Text)))
        real_ctx = P.make_context("runs/analysis_combined/analysis.json", {"run_dirs": ["runs/p1_dev_eval_v2"]})
        self.assertFalse(real_ctx["synthetic"])


@unittest.skipUnless(any(os.path.isfile(p) for p in REAL), "live analysis.json not present")
class TestRealAnalysis(Base):
    """On every live analysis.json: plotted values equal the JSON values."""

    def each(self):
        for path in REAL:
            if os.path.isfile(path):
                with open(path) as f:
                    yield path, json.load(f)

    def test_forest(self):
        for path, an in self.each():
            models = P.model_list(an)
            ctx = self.ctx(an)
            g = gids(P.fig_forest(an, models, ctx))
            g.update(gids(P.fig_forest(an, models, ctx, P.SECONDARY)))
            for p in ("insistence", "authority"):
                for m in models:
                    for name in P.PRIMARY + P.SECONDARY:
                        r = P.estimand(an, p, m, name)
                        key = f"forest/{p}/{m}/{P.SHORT[name]}"
                        self.assertSeq(g[f"{key}/est"].get_xdata(), [100 * r["estimate"]], f"{path} {key}")
                        inf = r["inference"]
                        self.assertSeq(g[f"{key}/item"].get_xdata(), [100 * v for v in inf["ci95_item_t"]], key)
                        if inf.get("ci95_family_cr1"):
                            self.assertSeq(g[f"{key}/cr1"].get_xdata(), [100 * v for v in inf["ci95_family_cr1"]])
                        self.assertSeq(g[f"{key}/bounds"].get_xdata(), sorted(100 * v for v in r["bounds"]))
                        hollow = to_hex(g[f"{key}/est"].get_markerfacecolor()) == "#ffffff"
                        self.assertEqual(hollow, bool(inf.get("degenerate")), key)
                        if "excludes0_item_t_only" in inf:
                            self.assertEqual(f"{key}/dagger" in g, bool(inf["excludes0_item_t_only"]), key)

    def test_interaction(self):
        for path, an in self.each():
            models = P.model_list(an)
            for p in ("insistence", "authority"):
                g = gids(P.fig_interaction(an, models, self.ctx(an), p))
                for m in models:
                    for name in ("E3_delivery_effect", "E4_moderation"):
                        r = P.estimand(an, p, m, name)
                        key = f"e4/{p}/{m}/{P.SHORT[name]}"
                        self.assertSeq(g[f"{key}/est"].get_xdata(), [100 * r["estimate"]], key)
                        self.assertSeq(g[f"{key}/item"].get_xdata(), [100 * v for v in r["inference"]["ci95_item_t"]])
                    for u in P.ASSERTIONS:
                        for rt in ("optional", "supplied"):
                            comp = P.exported_component(an, p, m, u, rt)
                            key = f"{p}/{m}/{u}/{rt}"
                            if comp:
                                self.assertSeq(g[f"e4/pt/{key}"].get_ydata(), [100 * comp["estimate"]], key)
                                inf = comp["inference"]
                                self.assertSeq(g[f"e4/ci/{key}"].get_ydata(), [100 * v for v in inf["ci95_item_t"]])
                                self.assertSeq(g[f"e4/cr1/{key}"].get_ydata(),
                                               [100 * v for v in inf["ci95_family_cr1"]])
                            else:
                                self.assertSeq(g[f"e4/pt/{key}"].get_ydata(),
                                               [100 * P.route_delta(an, m, u, rt, p)], key)
                    c = P.consistency(an, m, p)
                    exported = all(P.exported_D(an, p, m, u) for u in P.ASSERTIONS)
                    self.assertLess(c, 1e-9 if exported else 1e-3, f"{path} {m} {p}: recombination {c}")

    def test_funnel(self):
        for path, an in self.each():
            models = P.model_list(an)
            g = gids(P.fig_funnel(an, models, self.ctx(an)))
            for m in models:
                for a in P.ASSERTIONS:
                    for p in ("neutral", "insistence"):
                        for key, _ in P.FUNNEL:
                            num, den = P.COUNT_KEYS[key]
                            cs = [an["cells"][m][f"{s}/{a}/{p}/optional"].get("counts") for s in P.SNAPS]
                            gid = f"funnel/bar/{m}/{a}/{p}/{key}"
                            if all(cs):
                                k, n = sum(c[num] for c in cs), sum(c[den] for c in cs)
                                self.assertAlmostEqual(g[gid].get_height(), k / n, places=12, msg=gid)
                                self.assertEqual(g[f"funnel/label/{m}/{a}/{p}/{key}"].get_text(), f"{k}/{n}")
                            elif key == "lookup_relevant" and not all(
                                    an["cells"][m][f"{s}/{a}/{p}/optional"].get("lookup_relevant") for s in P.SNAPS):
                                self.assertNotIn(gid, g)

    def test_batches(self):
        for path, an in self.each():
            diff = (an.get("batches") or {}).get("difference")
            if not diff:
                continue
            models = P.model_list(an)
            g = gids(P.fig_batches(an, models, self.ctx(an)))
            for m in models:
                for name in P.PRIMARY:
                    d = diff["insistence"][m][name]
                    self.assertSeq(g[f"batches/est/{m}/{P.SHORT[name]}"].get_xdata(), [100 * d["diff"]])
                    self.assertSeq(g[f"batches/ci/{m}/{P.SHORT[name]}"].get_xdata(),
                                   [100 * v for v in d["ci95_welch"]])


if __name__ == "__main__":
    unittest.main()
