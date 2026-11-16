#!/usr/bin/env python3
"""Coverage simulation for P1 rev-3 interval methods (REVISION_3_SPEC.md §7 E4 floor, §9 step 2).

Purpose: pick the confirmatory interval method on evidence. For each scenario the script simulates complete
P1 datasets for one model, computes the item-level contrasts d_i exactly as p1v3/estimands.py does (its
`weights`, observed-outcome cell means, items missing a needed cell dropped), then builds 95% intervals with:
  item_t      item t-interval (p1v3/inference.py t_interval; df = n_items - 1)
  family_t    t-interval over family means (df = n_families - 1), as analyze_p1.py reports it
  boot_item   item-cluster percentile bootstrap (B resamples of items)
  boot_family family-cluster percentile bootstrap (B resamples of families, item-weighted mean)
  floor_t     boundary-safe item t: SE^2 = max(s^2, V_floor)/n, V_floor = sum_c w_c^2 p~_c(1-p~_c)/r_c with
              p~_c = (y_c+1)/(N_c+2) pooled over items (Agresti-Coull-type pseudo-counts), r_c = mean
              observed repeats per item in cell c. Same centre as item_t; never zero width.
and the two-sided sign-flip p-value (same algorithm as inference.signflip_p, n > 16 branch: 20,000 flips,
(hits+1)/(B+1); flips shared across a chunk of replications, as the reference reuses one seed) plus Holm,
and the same test over family means (exact enumeration when F <= 16) plus Holm.

Data-generating process (one model): items nested in families (item i in family i % F). Per outcome
(lookup_attempted, final_correct), item i, cell c (the 36 CELLS), repeat r:
  logit p = mu_c + u_f + g_f.x_c + v_i + h_i.x_c + t_{i,s(c),r}
u_f, v_i random intercepts; g_f, h_i random slopes on 8 factor codes x_c (wrong, stale, supplied, optional,
pressure, pressure x wrong, pressure x supplied, pressure x wrong x supplied; pressure = 1 insistence,
0.5 authority, 0 neutral); t = shared turn-1 prefix effect per item x snapshot x repeat (all branches of one
turn 1 share it). mu_c is solved by quadrature so that the population-average probability of every cell
equals a planted table, so the planted (superpopulation) contrasts sum_c w_c P_c hold exactly.
Y ~ Bernoulli(p). Missingness: item x snapshot ineligible (drops the item), turn-1 failure per
item x snapshot x repeat (removes its 18 branches), trial failure (MCAR), and optionally informative
missingness (incorrect final answers go missing more often).

Targets: `super` = planted population contrast (families and items random; the confirmatory target).
`famcond` = expected contrast over new items from the sampled families (what item-level methods target if
families are treated as fixed); reported as a secondary column.

Outputs (under --out, default sim_out/): results.csv (one row per scenario x estimand x method),
tests.csv (sign-flip and Holm rejection rates, variance decomposition), tables.md, summary.json, run_log.txt.
numpy only beyond the repo. Fixed seeds; each scenario's seed is derived from its name.

Extras (statistical review): (A) type-I error of the sign-flip test vs the one-sample t-test when item effects are
heterogeneous and asymmetric with population mean exactly 0 (asym_typeI.csv); (B) unequal family sizes: unweighted
mean-of-family-means t vs CR1 cluster-robust variance of the item-weighted mean, G-1 df (unequal_families.csv).
Both are summarised in tables_extras.md.

Run: python3 sim_p1_coverage.py [--reps 2000] [--boot 1000] [--workers 6] [--part all|main|extras] [--quick]
"""
import argparse
import csv
import json
import math
import os
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p1v3.estimands import CELLS, estimate_one, weights  # noqa: E402
from p1v3.inference import holm, signflip_p, t_interval, t_quantile  # noqa: E402

BASE_SEED = 20261116
ESTS = ("E1_delta_attempt", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation", "S2_delta_acc_none")
PRIMARY = ESTS[:4]
METHODS = ("item_t", "family_t", "boot_item", "boot_family", "floor_t")
OUTCOMES = ("lookup_attempted", "final_correct")
FLOOR = 0.075          # §7 E4 half-width floor
N_FLIPS = 20000        # inference.B_FLIPS
REPEATS = 5
NC = len(CELLS)

# ---------------------------------------------------------------- contrast weights (from estimands.py)
CIDX = {c: j for j, c in enumerate(CELLS)}
W = np.zeros((len(ESTS), NC))
NEED = np.zeros((len(ESTS), NC), bool)
OUT_IDX = np.zeros(len(ESTS), int)
for _e, _name in enumerate(ESTS):
    _out, _w = weights(_name)
    OUT_IDX[_e] = OUTCOMES.index(_out)
    for _c, _wc in _w.items():
        W[_e, CIDX[_c]] = _wc
        NEED[_e, CIDX[_c]] = True
SNAP_OF_CELL = np.array([0 if c[0] == "current" else 1 for c in CELLS])
PFAC = {"neutral": 0.0, "insistence": 1.0, "authority": 0.5}

# factor codes for random slopes
X = np.array([[c[1] == "wrong", c[0] == "stale", c[3] == "supplied", c[3] == "optional", PFAC[c[2]],
               PFAC[c[2]] * (c[1] == "wrong"), PFAC[c[2]] * (c[3] == "supplied"),
               PFAC[c[2]] * (c[1] == "wrong") * (c[3] == "supplied")] for c in CELLS], float)
XSQ = (X ** 2).sum(1)

# ---------------------------------------------------------------- planted cell probabilities
REGIMES = {
    # neutral accuracy by (assertion, route); stale snapshot lowers none/optional accuracy by stale_drop
    "ceiling": dict(acc={("right", "supplied"): .98, ("wrong", "supplied"): .98, ("right", "optional"): .98,
                         ("wrong", "optional"): .98, ("right", "none"): .98, ("wrong", "none"): .97},
                    stale_drop=0.0, look=0.02),
    "moderate": dict(acc={("right", "supplied"): .90, ("wrong", "supplied"): .90, ("right", "optional"): .85,
                          ("wrong", "optional"): .70, ("right", "none"): .80, ("wrong", "none"): .60},
                     stale_drop=0.03, look=0.40),
    "extreme": dict(acc={k: .995 for k in [(a, r) for a in ("right", "wrong") for r in ("supplied", "optional", "none")]},
                    stale_drop=0.0, look=0.005),
}
# insistence penalty Delta(a, route): (R,opt)=-k, (R,sup)=-k+rR, (W,opt)=-m, (W,sup)=-m+rW, (R,none)=-k, (W,none)=-m
# => D(right)=rR, D(wrong)=rW, E4=rR-rW, E3=(rR+rW)/2. Authority cells get half the penalty (not used by E1-E4).
EFFECTS = {
    "null": dict(k=0, m=0, rR=0, rW=0, e1={"ceiling": 0, "moderate": 0, "extreme": 0}),
    "e4_0": dict(k=.05, m=.10, rR=.05, rW=.05, e1={"ceiling": .02, "moderate": -.10, "extreme": .01}),
    "e4_small": dict(k=0, m=.10, rR=0, rW=.075, e1={"ceiling": .02, "moderate": -.075, "extreme": .01}),
    "e4_large": dict(k=0, m=.20, rR=0, rW=.15, e1={"ceiling": .04, "moderate": -.15, "extreme": .02}),
}
RE_SETS = {  # logit-scale SDs
    "base": dict(fam_int=0.5, fam_slope=0.2, item_int=1.0, item_slope=0.4, t1=0.5),
    "strongfam": dict(fam_int=1.0, fam_slope=0.4, item_int=1.0, item_slope=0.4, t1=0.5),
}
MISS_SETS = {  # q_inel per item x snapshot, q_t1 per item x snapshot x repeat, q_trial per trial, q_inf extra if incorrect
    "light": dict(q_inel=.01, q_t1=.02, q_trial=.02, q_inf=0.0),
    "heavy": dict(q_inel=.04, q_t1=.08, q_trial=.08, q_inf=0.0),
    "informative": dict(q_inel=.01, q_t1=.02, q_trial=.02, q_inf=.15),
}


def cell_probs(regime, effect):
    R, E = REGIMES[regime], EFFECTS[effect]
    delta = {("right", "optional"): -E["k"], ("right", "supplied"): -E["k"] + E["rR"], ("right", "none"): -E["k"],
             ("wrong", "optional"): -E["m"], ("wrong", "supplied"): -E["m"] + E["rW"], ("wrong", "none"): -E["m"]}
    P = np.empty((2, NC))
    for j, (s, a, pr, rt) in enumerate(CELLS):
        f = PFAC[pr]
        P[0, j] = R["look"] + f * E["e1"][regime]
        P[1, j] = R["acc"][(a, rt)] - (R["stale_drop"] if s == "stale" and rt != "supplied" else 0) + f * delta[(a, rt)]
    assert (P > 0).all() and (P < 1).all(), (regime, effect)
    return P


GH_Z, GH_W = np.polynomial.hermite_e.hermegauss(60)
GH_W = GH_W / GH_W.sum()


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def sigmas(re):
    tot = np.sqrt(re["fam_int"] ** 2 + re["item_int"] ** 2 + re["t1"] ** 2 + (re["fam_slope"] ** 2 + re["item_slope"] ** 2) * XSQ)
    inner = np.sqrt(re["item_int"] ** 2 + re["t1"] ** 2 + re["item_slope"] ** 2 * XSQ)
    return tot, inner


def solve_mu(P, sig):
    """mu such that E[expit(mu + sig Z)] = P, elementwise (bisection, Gauss-Hermite)."""
    lo, hi = np.full(P.shape, -40.0), np.full(P.shape, 40.0)
    for _ in range(80):
        mid = (lo + hi) / 2
        f = (expit(mid[..., None] + sig[..., None] * GH_Z) * GH_W).sum(-1)
        lo, hi = np.where(f < P, mid, lo), np.where(f < P, hi, mid)
    return (lo + hi) / 2


@lru_cache(maxsize=None)
def tq(df):
    return t_quantile(0.975, df)


# ---------------------------------------------------------------- data generation
def simulate_chunk(rng, nrep, n, F, mu, re, miss):
    """Returns Y (2,nrep,n,36,R) bool, obs (2,nrep,n,36,R) bool, fam_part (nrep,2,F,36), fam (n,)."""
    fam = np.arange(n) % F
    K = X.shape[1]
    fam_part = rng.normal(0, re["fam_int"], (nrep, 2, F, 1)) + rng.normal(0, re["fam_slope"], (nrep, 2, F, K)) @ X.T
    item_part = rng.normal(0, re["item_int"], (nrep, 2, n, 1)) + rng.normal(0, re["item_slope"], (nrep, 2, n, K)) @ X.T
    t1 = rng.normal(0, re["t1"], (nrep, 2, n, 2, REPEATS))[:, :, :, SNAP_OF_CELL, :]          # (nrep,2,n,36,R)
    eta = mu[None, :, None, :, None] + fam_part[:, :, fam, :, None] + item_part[..., None] + t1
    Y = rng.random(eta.shape) < expit(eta)
    Y = np.moveaxis(Y, 1, 0)                                                                   # (2,nrep,n,36,R)
    inel = (rng.random((nrep, n, 2)) < miss["q_inel"])[:, :, SNAP_OF_CELL][..., None]
    t1f = (rng.random((nrep, n, 2, REPEATS)) < miss["q_t1"])[:, :, SNAP_OF_CELL, :]
    trial = rng.random((nrep, n, NC, REPEATS)) < miss["q_trial"]
    base_miss = inel | t1f | trial
    obs = np.stack([~base_miss, ~base_miss])
    if miss["q_inf"] > 0:   # incorrect final answers go missing more often (e.g. malformed)
        obs[1] &= ~((~Y[1]) & (rng.random(Y[1].shape) < miss["q_inf"]))
    return Y, obs, fam_part, fam


def contrasts(Y, obs):
    """Item contrasts as estimands.estimate_one: d (5,nrep,n) with NaN for dropped items, valid, floor var."""
    cnt = obs.sum(-1)
    sm = (Y & obs).sum(-1)
    mean = sm / np.maximum(cnt, 1)
    nrep, n = Y.shape[1], Y.shape[2]
    d = np.full((len(ESTS), nrep, n), np.nan)
    valid = np.zeros((len(ESTS), nrep, n), bool)
    vfloor = np.zeros((len(ESTS), nrep))
    for e in range(len(ESTS)):
        o = OUT_IDX[e]
        valid[e] = (cnt[o][..., NEED[e]] > 0).all(-1)
        de = (mean[o] * W[e]).sum(-1)
        d[e] = np.where(valid[e], de, np.nan)
        ytot = (sm[o] * valid[e][..., None]).sum(1)
        ntot = (cnt[o] * valid[e][..., None]).sum(1)
        nv = np.maximum(valid[e].sum(1), 1)[:, None]
        pt = (ytot + 1) / (ntot + 2)
        reff = np.maximum(ntot, 1) / nv
        vfloor[e] = (W[e] ** 2 * pt * (1 - pt) / reff)[:, NEED[e]].sum(-1)
    return d, valid, vfloor


def within_share(Y):
    """Complete data: (E[Var(d_i | item)], Var(d_i)) per replication; the within part (binomial + turn-1) shrinks with repeats."""
    out = np.zeros((2, len(ESTS), Y.shape[1]))
    for e in range(len(ESTS)):
        dir_ = np.einsum("rncR,c->rnR", Y[OUT_IDX[e]].astype(float), W[e])   # per-repeat contrast
        out[0, e] = dir_.var(-1, ddof=1).mean(-1) / REPEATS                  # unbiased E[Var(d_i | item)]
        out[1, e] = dir_.mean(-1).var(-1, ddof=1)                            # total Var(d_i)
    return out


def famcond_target(mu, fam_part, sig_in, F, n):
    """Expected contrast over new items in the sampled families (nrep, 5)."""
    eta = mu[None, :, None, :, None] + fam_part[..., None] + sig_in[None, None, None, :, None] * GH_Z
    Pf = (expit(eta) * GH_W).sum(-1)                         # (nrep,2,F,36)
    nf = np.bincount(np.arange(n) % F, minlength=F) / n
    Pbar = np.einsum("roFc,F->roc", Pf, nf)                  # item-weighted
    return np.stack([Pbar[:, OUT_IDX[e]] @ W[e] for e in range(len(ESTS))], 1)


# ---------------------------------------------------------------- one scenario
def run_scenario(sc):
    t0 = time.time()
    rng = np.random.default_rng([BASE_SEED, zlib.crc32(sc["name"].encode())])
    n, F, reps, B = sc["n"], sc["F"], sc["reps"], sc["boot"]
    re, miss = RE_SETS[sc["re"]], MISS_SETS[sc["miss"]]
    P = cell_probs(sc["regime"], sc["effect"])
    sig_tot, sig_in = sigmas(re)
    mu = solve_mu(P, np.broadcast_to(sig_tot, P.shape))
    truth = np.array([P[OUT_IDX[e]] @ W[e] for e in range(len(ESTS))])
    lo = np.full((reps, len(ESTS), len(METHODS)), np.nan)
    hi = np.full_like(lo, np.nan)
    est = np.full((reps, len(ESTS)), np.nan)
    pval = np.full((reps, len(ESTS)), np.nan)
    pfam = np.full((reps, len(ESTS)), np.nan)
    holm_any = np.zeros(reps, bool)
    holm_any_fam = np.zeros(reps, bool)
    # family-level sign-flip over family means: exact enumeration when F <= 16 (as signflip_p), else 20,000 flips
    exact_fam = F <= 16
    if exact_fam:
        fam_flips = np.array([[1.0 if (b >> k) & 1 else -1.0 for k in range(F)] for b in range(2 ** F)])
    tfam = np.zeros((reps, len(ESTS)))
    wshare = np.zeros((2, reps, len(ESTS)))
    nvalid = np.zeros((reps, len(ESTS)))
    chunk = max(1, min(100, int(4e6 // (n * NC * REPEATS))))
    r0 = 0
    while r0 < reps:
        m = min(chunk, reps - r0)
        Y, obs, fam_part, fam = simulate_chunk(rng, m, n, F, mu, re, miss)
        d, valid, vfloor = contrasts(Y, obs)
        tfam[r0:r0 + m] = famcond_target(mu, fam_part, sig_in, F, n)
        wshare[:, r0:r0 + m] = within_share(Y).transpose(0, 2, 1)
        flips = rng.choice(np.array([-1.0, 1.0]), size=(N_FLIPS, n))
        if not exact_fam:
            fam_flips = rng.choice(np.array([-1.0, 1.0]), size=(N_FLIPS, F))
        onehot = np.eye(F)[fam]                                                  # (n,F)
        for j in range(m):
            r = r0 + j
            V = valid[:, j, :].T.astype(float)                                   # (n,5)
            Dz = np.nan_to_num(d[:, j, :].T)                                     # (n,5) zero-filled
            nv = V.sum(0)
            nvalid[r] = nv
            mean = Dz.sum(0) / np.maximum(nv, 1)
            est[r] = mean
            ss = ((Dz - mean) ** 2 * V).sum(0)
            sd2 = ss / np.maximum(nv - 1, 1)
            q = np.array([tq(int(k) - 1) if k >= 2 else np.nan for k in nv])
            h = q * np.sqrt(sd2 / np.maximum(nv, 1))
            lo[r, :, 0], hi[r, :, 0] = mean - h, mean + h
            hf = q * np.sqrt(np.maximum(sd2, vfloor[:, j]) / np.maximum(nv, 1))
            lo[r, :, 4], hi[r, :, 4] = mean - hf, mean + hf
            # family t over family means
            fs, fc = onehot.T @ Dz, onehot.T @ V                                 # (F,5)
            for e in range(len(ESTS)):
                ok = fc[:, e] > 0
                if ok.sum() >= 2:
                    fm = fs[ok, e] / fc[ok, e]
                    hfam = tq(int(ok.sum()) - 1) * fm.std(ddof=1) / math.sqrt(ok.sum())
                    lo[r, e, 1], hi[r, e, 1] = fm.mean() - hfam, fm.mean() + hfam
            # item-cluster percentile bootstrap (resample all scheduled items; dropped ones stay dropped)
            idx = rng.integers(0, n, (B, n)) + n * np.arange(B)[:, None]
            C = np.bincount(idx.ravel(), minlength=B * n).reshape(B, n).astype(float)
            with np.errstate(invalid="ignore", divide="ignore"):
                bm = (C @ Dz) / (C @ V)
            lo[r, :, 2], hi[r, :, 2] = np.nanquantile(bm, [0.025, 0.975], axis=0)
            # family-cluster percentile bootstrap
            idf = rng.integers(0, F, (B, F)) + F * np.arange(B)[:, None]
            Cf = np.bincount(idf.ravel(), minlength=B * F).reshape(B, F).astype(float)
            with np.errstate(invalid="ignore", divide="ignore"):
                bf = (Cf @ fs) / (Cf @ fc)
            lo[r, :, 3], hi[r, :, 3] = np.nanquantile(bf, [0.025, 0.975], axis=0)
            # sign-flip p (inference.signflip_p, n>16 branch)
            obs_s = np.abs(Dz.sum(0))
            hits = (np.abs(flips @ Dz) >= obs_s - 1e-12).sum(0)
            p = (hits + 1) / (N_FLIPS + 1)
            p[obs_s == 0] = 1.0
            pval[r] = p
            adj = holm({ESTS[e]: p[e] for e in range(4)})
            holm_any[r] = min(adj.values()) < 0.05
            with np.errstate(invalid="ignore", divide="ignore"):
                fmz = np.nan_to_num(fs / fc)                                     # empty family -> 0 (no effect on sums)
            obs_f = np.abs(fmz.sum(0))
            hits_f = (np.abs(fam_flips @ fmz) >= obs_f - 1e-12).sum(0)
            pf = hits_f / len(fam_flips) if exact_fam else (hits_f + 1) / (N_FLIPS + 1)
            pf[obs_f == 0] = 1.0
            pfam[r] = pf
            adjf = holm({ESTS[e]: pf[e] for e in range(4)})
            holm_any_fam[r] = min(adjf.values()) < 0.05
        r0 += m
    return dict(sc=sc, truth=truth, lo=lo, hi=hi, est=est, pval=pval, holm_any=holm_any, tfam=tfam,
                pfam=pfam, holm_any_fam=holm_any_fam,
                wshare=wshare, nvalid=nvalid, P=P.tolist(), seconds=time.time() - t0)


# ---------------------------------------------------------------- summaries
def summarize(res):
    sc, truth = res["sc"], res["truth"]
    rows, tests = [], []
    reps = res["lo"].shape[0]
    for e, name in enumerate(ESTS):
        th = truth[e]
        tf = res["tfam"][:, e]
        for k, meth in enumerate(METHODS):
            lo, hi = res["lo"][:, e, k], res["hi"][:, e, k]
            na = np.isnan(lo) | np.isnan(hi)
            hw = (hi - lo) / 2
            hwv = hw[~na]
            rows.append(dict(
                scenario=sc["name"], group=sc["group"], regime=sc["regime"], effect=sc["effect"], n_items=sc["n"],
                n_families=sc["F"], re=sc["re"], miss=sc["miss"], estimand=name, truth=round(th, 6), method=meth,
                reps=reps, coverage=np.mean(~na & (lo <= th + 1e-12) & (hi >= th - 1e-12)),
                truth_below_lo=np.mean(~na & (lo > th + 1e-12)), truth_above_hi=np.mean(~na & (hi < th - 1e-12)),
                degenerate=np.mean(~na & (hi - lo < 1e-12)), na=np.mean(na),
                coverage_famcond=np.mean(~na & (lo <= tf + 1e-12) & (hi >= tf - 1e-12)),
                excludes_0=np.mean(~na & ((lo > 1e-12) | (hi < -1e-12))),
                hw_mean=hwv.mean() if hwv.size else np.nan,
                hw_p10=np.quantile(hwv, .1) if hwv.size else np.nan, hw_p50=np.quantile(hwv, .5) if hwv.size else np.nan,
                hw_p80=np.quantile(hwv, .8) if hwv.size else np.nan, hw_p90=np.quantile(hwv, .9) if hwv.size else np.nan,
                share_hw_le_floor=np.mean(~na & (hw <= FLOOR)),
                bias=np.nanmean(res["est"][:, e]) - th))
        tests.append(dict(scenario=sc["name"], group=sc["group"], regime=sc["regime"], effect=sc["effect"],
                          n_items=sc["n"], n_families=sc["F"], re=sc["re"], miss=sc["miss"], estimand=name,
                          truth=round(th, 6), reps=reps, signflip_reject=np.mean(res["pval"][:, e] < 0.05),
                          holm_any_primary=np.mean(res["holm_any"]),
                          signflip_family_reject=np.mean(res["pfam"][:, e] < 0.05),
                          holm_any_primary_family=np.mean(res["holm_any_fam"]), within_share=res["wshare"][0, :, e].mean() / res["wshare"][1, :, e].mean(),
                          mean_items_used=res["nvalid"][:, e].mean(), sd_estimate=np.nanstd(res["est"][:, e], ddof=1),
                          bias=np.nanmean(res["est"][:, e]) - th, seconds=res["seconds"]))
    return rows, tests


def scenarios(reps, boot, quick=False):
    fam_of = {24: 6, 36: 6, 48: 12, 60: 12, 72: 12, 84: 12, 96: 12, 120: 12}
    out = []

    def add(group, regime, effect, n, re="base", miss="light", F=None):
        F = F or fam_of[n]
        name = f"{group}|{regime}|{effect}|n{n}|F{F}|{re}|{miss}"
        out.append(dict(name=name, group=group, regime=regime, effect=effect, n=n, F=F, re=re, miss=miss,
                        reps=reps, boot=boot))
    ns = (24, 60, 120)
    for regime in ("ceiling", "moderate"):
        for effect in EFFECTS:
            for n in ns:
                add("main", regime, effect, n)
    if quick:
        return out
    for n in ns:
        add("extreme", "extreme", "null", n)
        for effect in ("null", "e4_large"):
            add("strongfam", "moderate", effect, n, re="strongfam")
    for regime in ("ceiling", "moderate"):
        for effect in ("null", "e4_large"):
            add("heavymiss", regime, effect, 60, miss="heavy")
            add("informative", regime, effect, 60, miss="informative")
    for n in (72, 84, 96):           # where does moderate-regime E4 cross the floor?
        for effect in ("null", "e4_large"):
            add("precision", "moderate", effect, n)
    for n in (36, 48):               # and the ceiling regime
        add("precision", "ceiling", "e4_large", n)
    for n, F in ((96, 16), (96, 24), (120, 20), (120, 30), (144, 24), (144, 36)):   # more families
        add("famcount", "moderate", "e4_large", n, F=F)
    return out


# ---------------------------------------------------------------- reference checks
def reference_checks(log):
    """Vectorized contrasts, t interval and sign-flip match p1v3 on simulated data."""
    rng = np.random.default_rng(BASE_SEED)
    n, F = 30, 6
    re, miss = RE_SETS["base"], MISS_SETS["heavy"]
    P = cell_probs("moderate", "e4_large")
    mu = solve_mu(P, np.broadcast_to(sigmas(re)[0], P.shape))
    # planted marginals recovered by quadrature
    sig = sigmas(re)[0]
    back = (expit(mu[..., None] + sig[None, :, None] * GH_Z) * GH_W).sum(-1)
    assert np.abs(back - P).max() < 1e-9
    Y, obs, _, fam = simulate_chunk(rng, 1, n, F, mu, re, miss)
    d, valid, _ = contrasts(Y, obs)
    rows = []
    for i in range(n):
        for j, (s, a, pr, rt) in enumerate(CELLS):
            for r in range(REPEATS):
                rows.append(dict(model="m", item_id=f"i{i:03d}", family=f"f{fam[i]}", snapshot=s, assertion=a,
                                 pressure=pr, route=rt, repeat=r,
                                 lookup_attempted=int(Y[0, 0, i, j, r]) if obs[0, 0, i, j, r] else None,
                                 final_correct=int(Y[1, 0, i, j, r]) if obs[1, 0, i, j, r] else None))
    maxdiff, dropped = 0.0, 0
    for e, name in enumerate(ESTS):
        ref = estimate_one(rows, name)
        mine = {f"i{i:03d}": d[e, 0, i] for i in range(n) if valid[e, 0, i]}
        assert set(mine) == set(ref["item_values"]), name
        maxdiff = max(maxdiff, max(abs(mine[k] - ref["item_values"][k]) for k in mine))
        dropped += ref["items_dropped_incomplete"]
        xs = list(ref["item_values"].values())
        ci = t_interval(xs)
        m_, s_ = np.mean(xs), np.std(xs, ddof=1)
        h = tq(len(xs) - 1) * s_ / math.sqrt(len(xs))
        assert abs(ci[0] - (m_ - h)) < 1e-12 and abs(ci[1] - (m_ + h)) < 1e-12
    assert maxdiff < 1e-12
    # sign-flip: same algorithm, different random stream -> compare p within Monte Carlo error
    sp = []
    for k in range(6):
        xs = rng.normal(0.03 * k, 0.3, 40)
        flips = rng.choice(np.array([-1.0, 1.0]), size=(N_FLIPS, 40))
        mine = ((np.abs(flips @ xs) >= abs(xs.sum()) - 1e-12).sum() + 1) / (N_FLIPS + 1)
        ref = signflip_p(list(xs), seed=k)
        sp.append((round(float(ref), 4), round(float(mine), 4)))
        assert abs(mine - ref) < 5 * math.sqrt(max(ref * (1 - ref), 1e-4) / N_FLIPS) + 1e-3
    log(f"reference checks passed: item contrasts match estimands.estimate_one (max |diff| {maxdiff:.1e}, "
        f"{dropped} item-estimand drops under heavy missingness), t intervals match inference.t_interval, "
        f"sign-flip p (ref, vectorized) = {sp}")


# ---------------------------------------------------------------- tables
def fmt(x, k=3):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{k}f}"


def tables(rows, tests, reps):
    mc = math.sqrt(.95 * .05 / reps)
    L = [f"# Coverage simulation tables (auto-generated by sim_p1_coverage.py)", "",
         f"{reps} replications per scenario; Monte Carlo SE of a 95% coverage estimate ≈ {mc:.4f} "
         f"(±{1.96 * mc:.3f} at 95%); of a 5% rejection rate ≈ {mc:.4f}.", ""]
    by = {}
    for r in rows:
        by.setdefault((r["scenario"], r["estimand"]), {})[r["method"]] = r
    sc_order = list(dict.fromkeys(r["scenario"] for r in rows))
    meta = {r["scenario"]: r for r in rows}

    L += ["## 1. Coverage (target = planted population contrast), min and mean over all five estimands and four effect configs", "",
          "| regime | n (fam) | " + " | ".join(f"{m} min / mean" for m in METHODS) + " |",
          "|---|---|" + "---|" * len(METHODS)]
    for regime in ("ceiling", "moderate"):
        for n in (24, 60, 120):
            cells = [r for r in rows if r["group"] == "main" and r["regime"] == regime and r["n_items"] == n]
            fam = cells[0]["n_families"]
            L.append(f"| {regime} | {n} ({fam}) | " + " | ".join(
                f"{fmt(min(c['coverage'] for c in cells if c['method'] == m))} / {fmt(np.mean([c['coverage'] for c in cells if c['method'] == m]))}"
                for m in METHODS) + " |")
    L.append("")

    def block(title, scs, ests=ESTS, famcond=False):
        out = [f"## {title}", "", "| scenario | estimand | truth | " + " | ".join(METHODS) + " |",
               "|---|---|---|" + "---|" * len(METHODS)]
        for s in scs:
            for e in ests:
                d = by[(s, e)]
                mm = meta[s]
                lab = f"{mm['regime']} {mm['effect']} n{mm['n_items']}/{mm['n_families']}f {mm['re']} {mm['miss']}"
                key = "coverage_famcond" if famcond else "coverage"
                out.append(f"| {lab} | {e.split('_')[0]} | {d['item_t']['truth']:+.4f} | " + " | ".join(
                    f"{fmt(d[m][key])} ({fmt(d[m]['truth_below_lo'])}/{fmt(d[m]['truth_above_hi'])})"
                    + (f" deg {fmt(d[m]['degenerate'])}" if d[m]["degenerate"] > 0 else "") for m in METHODS) + " |")
        return out + [""]

    main = [s for s in sc_order if meta[s]["group"] == "main"]
    L += block("2. Main grid: coverage (truth < lower / truth > upper), degenerate rate if > 0", main)
    L += ["## 3. Degenerate (zero-width) intervals: max rate over estimands and effects", "",
          "| scenario group | regime | n | " + " | ".join(METHODS) + " |", "|---|---|---|" + "---|" * len(METHODS)]
    for g in dict.fromkeys(meta[s]["group"] for s in sc_order):
        for regime in dict.fromkeys(meta[s]["regime"] for s in sc_order if meta[s]["group"] == g):
            for n in sorted({meta[s]["n_items"] for s in sc_order if meta[s]["group"] == g and meta[s]["regime"] == regime}):
                cells = [r for r in rows if r["group"] == g and r["regime"] == regime and r["n_items"] == n]
                L.append(f"| {g} | {regime} | {n} | " + " | ".join(
                    fmt(max(c["degenerate"] for c in cells if c["method"] == m)) for m in METHODS) + " |")
    L.append("")
    L += ["## 4. E4 half-width versus the 7.5 pp floor", "",
          "Share of replications with half-width ≤ 0.075 (floor met if ≥ 0.80); p50 and p80 half-width.", "",
          "| scenario | " + " | ".join(f"{m} share / p50 / p80" for m in METHODS) + " |", "|---|" + "---|" * len(METHODS)]
    for s in sc_order:
        d = by[(s, "E4_moderation")]
        mm = meta[s]
        L.append(f"| {mm['group']} {mm['regime']} {mm['effect']} n{mm['n_items']}/{mm['n_families']}f {mm['re']} {mm['miss']} | "
                 + " | ".join(f"{fmt(d[m]['share_hw_le_floor'], 2)} / {fmt(d[m]['hw_p50'])} / {fmt(d[m]['hw_p80'])}" for m in METHODS) + " |")
    L.append("")
    L += ["## 5. Sign-flip tests: rejection rate at α = 0.05 (type-I where truth = 0), Holm any-primary rejection", "",
          "Each cell: item-level sign-flip (inference.signflip_p) / family-level sign-flip over family means "
          "(exact when F ≤ 16; with 6 families the smallest attainable p is 2/64 = 0.031).", "",
          "| scenario | " + " | ".join(e.split("_")[0] for e in ESTS) + " | Holm any (E1–E4) |", "|---|" + "---|" * (len(ESTS) + 1)]
    tby = {}
    for t in tests:
        tby.setdefault(t["scenario"], {})[t["estimand"]] = t
    for s in sc_order:
        mm = meta[s]
        L.append(f"| {mm['group']} {mm['regime']} {mm['effect']} n{mm['n_items']} {mm['re']} {mm['miss']} | " + " | ".join(
            f"{fmt(tby[s][e]['signflip_reject'])} / {fmt(tby[s][e]['signflip_family_reject'])}{'*' if abs(tby[s][e]['truth']) < 1e-12 else ''}" for e in ESTS)
            + f" | {fmt(tby[s][ESTS[0]]['holm_any_primary'])} / {fmt(tby[s][ESTS[0]]['holm_any_primary_family'])} |")
    L += ["", "\\* = truth 0 (entry is a type-I error rate).", ""]
    stress = [s for s in sc_order if meta[s]["group"] != "main"]
    L += block("6. Stress scenarios: coverage (truth < lower / truth > upper)", stress)
    L += block("7. Coverage of the family-conditional target (new items, same families), main grid",
               main, famcond=True)
    L += ["## 8. Within-item share of Var(d_i) = mean E[Var(d_i | item)] / mean Var(d_i) (binomial + turn-1 noise, reducible by repeats), E4, complete data; values near 1 mean between-item variance is small relative to it", "",
          "| scenario | within share | sd of estimate | mean items used | bias |", "|---|---|---|---|---|"]
    for s in sc_order:
        t = tby[s]["E4_moderation"]
        mm = meta[s]
        L.append(f"| {mm['group']} {mm['regime']} {mm['effect']} n{mm['n_items']} {mm['re']} {mm['miss']} | "
                 f"{fmt(t['within_share'])} | {fmt(t['sd_estimate'], 4)} | {t['mean_items_used']:.1f} | {t['bias']:+.4f} |")
    return "\n".join(L) + "\n"

# ================================================================ extras (statistical review, 16 Nov)
# (A) Type-I error under asymmetric heterogeneous item effects with population mean exactly 0.
# Item i has a true contrast delta_i drawn from a mean-zero (possibly skewed) distribution; its cell probabilities
# are p_ic = base_i + delta_i * w_c / sum(w^2), so sum_c w_c p_ic = delta_i exactly and E[d_i] = 0 exactly
# (weights sum to 0, so base_i cancels). 5 repeats per cell, Bernoulli; no families (isolates the symmetry issue).
def _two_point(pneg, a, b):
    assert abs((1 - pneg) * a + pneg * b) < 1e-12
    return lambda rng, size: np.where(rng.random(size) < pneg, b, a)


ASYM_DISTS = {
    "sym_uniform": (lambda rng, size: rng.uniform(-0.1, 0.1, size), "U(-0.10, 0.10), symmetric reference"),
    "two_point_90_10": (_two_point(0.10, 0.02, -0.18), "90% +0.02, 10% -0.18"),
    "two_point_97_3": (_two_point(0.03, 0.006, -0.194), "97% +0.006, 3% -0.194"),
    "beta_skew": (lambda rng, size: 0.3 * (0.1 - rng.beta(0.5, 4.5, size)), "0.3*(0.1 - Beta(0.5, 4.5)): range [-0.27, +0.03]"),
    "two_point_90_10_large": (_two_point(0.10, 0.05, -0.45), "90% +0.05, 10% -0.45"),
}
ASYM_CASES = [  # (estimand, base range for base_i, distributions)
    ("E2_delta_acc_supplied", (0.30, 0.70), ("sym_uniform", "two_point_90_10", "two_point_97_3", "beta_skew", "two_point_90_10_large")),
    ("E4_moderation", (0.45, 0.85), ("sym_uniform", "two_point_90_10", "two_point_97_3", "beta_skew", "two_point_90_10_large")),
    ("E4_moderation", (0.93, 0.96), ("sym_uniform", "two_point_90_10", "two_point_97_3", "beta_skew")),
]


def run_asym(args):
    est_name, base_rng, dist, n, reps = args
    e = ESTS.index(est_name)
    need = NEED[e]
    w = W[e][need]
    scale = w / (w ** 2).sum()
    draw = ASYM_DISTS[dist][0]
    rng = np.random.default_rng([BASE_SEED, zlib.crc32(f"asym|{est_name}|{base_rng}|{dist}|{n}".encode())])
    rej_sf = rej_t = t_lo = t_hi = 0
    skews = []
    q = tq(n - 1)
    done = 0
    while done < reps:
        m = min(250, reps - done)
        base = rng.uniform(*base_rng, (m, n, 1))
        delta = draw(rng, (m, n, 1))
        p = base + delta * scale
        assert (p >= 0).all() and (p <= 1).all()
        d = (rng.binomial(REPEATS, p) / REPEATS) @ w                          # (m, n) item contrasts
        mean, sd = d.mean(1), d.std(1, ddof=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = mean / (sd / math.sqrt(n))
        t = np.where(sd > 0, t, 0.0)
        rej_t += int((np.abs(t) > q).sum())
        t_lo += int((t < -q).sum())
        t_hi += int((t > q).sum())
        flips = rng.choice(np.array([-1.0, 1.0]), size=(N_FLIPS, n))
        obs = np.abs(d.sum(1))
        hits = (np.abs(flips @ d.T) >= obs - 1e-12).sum(0)
        pv = np.where(obs == 0, 1.0, (hits + 1) / (N_FLIPS + 1))
        rej_sf += int((pv < 0.05).sum())
        c = d - mean[:, None]
        with np.errstate(divide="ignore", invalid="ignore"):
            sk = (c ** 3).mean(1) / (c ** 2).mean(1) ** 1.5
        skews.append(sk[np.isfinite(sk)])
        done += m
    dsk = draw(np.random.default_rng(1), 200000)
    return dict(estimand=est_name, base=f"U{base_rng}", dist=dist, dist_desc=ASYM_DISTS[dist][1], n_items=n, reps=reps,
                delta_skewness=float(((dsk - dsk.mean()) ** 3).mean() / dsk.var() ** 1.5) if dsk.var() > 0 else 0.0,
                d_skewness_median=float(np.median(np.concatenate(skews))),
                typeI_signflip=rej_sf / reps, typeI_t=rej_t / reps, t_reject_low=t_lo / reps, t_reject_high=t_hi / reps,
                mc_se=math.sqrt(0.05 * 0.95 / reps))


# (B) Family-clustered intervals for the item-weighted estimand with unequal family sizes.
# Each family's size is drawn per replication: 4 or 6 items with probability 1/2 (families are sampled from a
# population of families whose sizes vary). Item i in family f: delta_i = theta + s(size_f) + u_f + e_i (E4 contrast
# scale), p_ic = 0.70 + a_i + delta_i * w_c / sum(w^2). With size_effect, s(4) = +0.15, s(6) = -0.10, so the
# item-weighted population target E[n_f mu_f] / E[n_f] = theta + (4*0.15 - 6*0.10)/10 = theta, while the family-weighted
# target (what the unweighted mean of family means estimates) is theta + (0.15 - 0.10)/2 = theta + 0.025.
# Items are then dropped MCAR with probability q_drop (incomplete items, as estimands.py drops them).
UNEQ_THETA = -0.075


def run_uneq(args):
    F, size_effect, q_drop, reps = args
    e = ESTS.index("E4_moderation")
    w = W[e][NEED[e]]
    scale = w / (w ** 2).sum()
    s4, s6 = (0.15, -0.10) if size_effect else (0.0, 0.0)
    t_item = UNEQ_THETA + (4 * s4 + 6 * s6) / 10
    t_fam = UNEQ_THETA + (s4 + s6) / 2
    fam = np.repeat(np.arange(F), 6)                 # 6 slots per family; slots beyond the family's size are empty
    slot = np.tile(np.arange(6), F)
    n = 6 * F
    rng = np.random.default_rng([BASE_SEED, zlib.crc32(f"uneq|{F}|{size_effect}|{q_drop}".encode())])
    onehot = np.eye(F)[fam]
    out = {k: [] for k in ("item_t", "famt_unweighted", "cr1_itemweighted")}
    done = 0
    while done < reps:
        m = min(500, reps - done)
        size = rng.choice(np.array([4, 6]), size=(m, F))
        shift = np.where(size == 4, s4, s6)
        u = rng.uniform(-0.15, 0.15, (m, F))
        delta = UNEQ_THETA + shift[:, fam] + u[:, fam] + rng.uniform(-0.2, 0.2, (m, n))
        p = 0.70 + rng.uniform(-0.1, 0.1, (m, n, 1)) + delta[..., None] * scale
        assert (p >= 0).all() and (p <= 1).all()
        d = (rng.binomial(REPEATS, p) / REPEATS) @ w                          # (m, n)
        K = ((slot[None, :] < size[:, fam]) & (rng.random((m, n)) >= q_drop)).astype(float)
        N = K.sum(1)
        theta_hat = (d * K).sum(1) / N
        # item t over kept items
        ss = (((d - theta_hat[:, None]) ** 2) * K).sum(1)
        se_i = np.sqrt(ss / (N - 1) / N)
        qi = np.array([tq(int(k) - 1) for k in N])
        out["item_t"].append(np.stack([theta_hat - qi * se_i, theta_hat + qi * se_i], 1))
        # family sums/counts over kept items
        fs, fc = (d * K) @ onehot, K @ onehot
        G = (fc > 0).sum(1)
        qg = np.array([tq(int(g) - 1) for g in G])
        with np.errstate(invalid="ignore", divide="ignore"):
            fm = np.where(fc > 0, fs / fc, np.nan)
        mfm = np.nanmean(fm, 1)
        se_f = np.nanstd(fm, 1, ddof=1) / np.sqrt(G)
        out["famt_unweighted"].append(np.stack([mfm - qg * se_f, mfm + qg * se_f], 1))
        # CR1: V = G/(G-1) * sum_g (sum_{i in g} (d_i - theta_hat))^2 / N^2, df G-1
        S = ((d - theta_hat[:, None]) * K) @ onehot
        V = G / (G - 1) * (S ** 2).sum(1) / N ** 2
        out["cr1_itemweighted"].append(np.stack([theta_hat - qg * np.sqrt(V), theta_hat + qg * np.sqrt(V)], 1))
        done += m
    rows = []
    for meth, iv in out.items():
        iv = np.concatenate(iv)
        lo, hi = iv[:, 0], iv[:, 1]
        rows.append(dict(n_families=F, n_items_expected=5 * F, sizes="4 or 6, random per family", size_effect=size_effect, q_drop=q_drop,
                         reps=reps, method=meth, target_item=round(t_item, 6), target_family=round(t_fam, 6),
                         coverage_item_target=np.mean((lo <= t_item) & (hi >= t_item)),
                         item_target_below_lo=np.mean(lo > t_item), item_target_above_hi=np.mean(hi < t_item),
                         coverage_family_target=np.mean((lo <= t_fam) & (hi >= t_fam)),
                         hw_mean=np.mean((hi - lo) / 2), mc_se=math.sqrt(0.05 * 0.95 / reps)))
    return rows


def run_extras(out_dir, reps, workers, log):
    t0 = time.time()
    asym_jobs = [(e, b, dist, n, reps) for e, b, dists in ASYM_CASES for dist in dists for n in (24, 60)]
    uneq_jobs = [(F, se, q, reps) for F in (6, 12, 24) for se in (False, True) for q in (0.0, 0.15)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        asym = list(ex.map(run_asym, asym_jobs))
        uneq = [r for rows in ex.map(run_uneq, uneq_jobs) for r in rows]
    for fn, data in (("asym_typeI.csv", asym), ("unequal_families.csv", uneq)):
        with open(os.path.join(out_dir, fn), "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(data[0]))
            wr.writeheader()
            for x in data:
                wr.writerow({k: (round(v, 6) if isinstance(v, (float, np.floating)) else v) for k, v in x.items()})
    mc = math.sqrt(0.05 * 0.95 / reps)
    L = ["# Extras (auto-generated by sim_p1_coverage.py --part extras)", "",
         f"{reps} replications per row; Monte Carlo SE of a 5% rate ≈ {mc:.4f}, of a 95% coverage ≈ {mc:.4f}.", "",
         "## A. Type-I error at α = 0.05, item effects heterogeneous and asymmetric, population mean exactly 0", "",
         "| estimand | base p | item-effect distribution | skew(δ) | n | median skew(d_i) | sign-flip | t-test (low / high tail) |",
         "|---|---|---|---|---|---|---|---|"]
    for r in asym:
        L.append(f"| {r['estimand'].split('_')[0]} | {r['base']} | {r['dist_desc']} | {r['delta_skewness']:+.2f} | {r['n_items']} | "
                 f"{r['d_skewness_median']:+.2f} | {r['typeI_signflip']:.4f} | {r['typeI_t']:.4f} ({r['t_reject_low']:.4f} / {r['t_reject_high']:.4f}) |")
    L += ["", "## B. Unequal family sizes (4 or 6 items, random per family): coverage of the item-weighted target (E4 scale, θ = −0.075)", "",
          "With a size effect, the item-weighted target is θ and the family-weighted target is θ + 0.025.", "",
          "| families (items) | size effect | item drop | method | coverage, item target (below/above) | coverage, family target | mean half-width |",
          "|---|---|---|---|---|---|---|"]
    for r in uneq:
        L.append(f"| {r['n_families']} (~{r['n_items_expected']}) | {'yes' if r['size_effect'] else 'no'} | {r['q_drop']:.2f} | {r['method']} | "
                 f"{r['coverage_item_target']:.4f} ({r['item_target_below_lo']:.4f}/{r['item_target_above_hi']:.4f}) | "
                 f"{r['coverage_family_target']:.4f} | {r['hw_mean']:.4f} |")
    with open(os.path.join(out_dir, "tables_extras.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    log(f"extras: {len(asym_jobs)} asymmetric-effect cells, {len(uneq_jobs)} unequal-family cells, {reps} reps, {time.time() - t0:.1f}s")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=min(6, os.cpu_count() or 1))
    ap.add_argument("--quick", action="store_true", help="main grid only, 100 reps (smoke test)")
    ap.add_argument("--out", default=os.path.join(HERE, "sim_out"))
    ap.add_argument("--part", choices=("all", "main", "extras"), default="all",
                    help="main = coverage grid; extras = asymmetric-effect type-I and unequal-family CR1 checks")
    ap.add_argument("--extra-reps", type=int, default=10000)
    a = ap.parse_args()
    if a.quick:
        a.reps = min(a.reps, 100)
    os.makedirs(a.out, exist_ok=True)
    logf = open(os.path.join(a.out, "run_log.txt" if a.part != "extras" else "run_log_extras.txt"), "w")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()
    t0 = time.time()
    log(f"sim_p1_coverage.py: reps={a.reps} boot={a.boot} workers={a.workers} seed={BASE_SEED} numpy={np.__version__}")
    reference_checks(log)
    if a.part in ("all", "extras"):
        run_extras(a.out, 1000 if a.quick else a.extra_reps, a.workers, log)
    if a.part == "extras":
        log(f"done in {time.time() - t0:.1f}s; outputs in {a.out}")
        return
    scs = scenarios(a.reps, a.boot, a.quick)
    log(f"{len(scs)} scenarios")
    rows, tests, meta = [], [], []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(run_scenario, scs):
            r, t = summarize(res)
            rows += r
            tests += t
            meta.append(dict(scenario=res["sc"]["name"], truth=dict(zip(ESTS, res["truth"].round(6).tolist())),
                             cell_probs=res["P"], seconds=round(res["seconds"], 1)))
            log(f"  {res['sc']['name']}: {res['seconds']:.1f}s")
    for fn, data in (("results.csv", rows), ("tests.csv", tests)):
        with open(os.path.join(a.out, fn), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            for x in data:
                w.writerow({k: (round(v, 6) if isinstance(v, (float, np.floating)) else v) for k, v in x.items()})
    with open(os.path.join(a.out, "tables.md"), "w") as f:
        f.write(tables(rows, tests, a.reps))
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(dict(args=vars(a), base_seed=BASE_SEED, regimes={k: {**v, "acc": {f"{a_}|{r_}": x for (a_, r_), x in v["acc"].items()}}
                                                                    for k, v in REGIMES.items()},
                       effects=EFFECTS, re_sets=RE_SETS, miss_sets=MISS_SETS, methods=METHODS, scenarios=meta,
                       seconds=round(time.time() - t0, 1)), f, indent=1, default=float)
    log(f"done in {time.time() - t0:.1f}s; outputs in {a.out}")


if __name__ == "__main__":
    main()
