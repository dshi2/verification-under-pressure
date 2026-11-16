# P1 interval-coverage simulation (REVISION_3_SPEC.md §7 E4 floor, §9 step 2)

**Script:** `sim_p1_coverage.py` (numpy + the repo's `p1v3`). **Outputs:** `sim_out/` (`results.csv`: one row per scenario × estimand × method; `tests.csv`: sign-flip/Holm rejection rates and variance decomposition; `tables.md`: every table; `summary.json`: all parameters, planted cell probabilities and truths; `run_log.txt`).
**Run:** `python3 sim_p1_coverage.py` (defaults: 2000 replications per scenario, B = 1000 bootstrap resamples, 6 worker processes, base seed 20261116; each scenario's seed comes from its name). 55 scenarios ran in about 4 minutes on 8 cores (6–7 minutes when the machine is busy). `--quick` runs a smoke test of the main grid only.
**Status:** development planning evidence. The variance inputs are assumptions, not pilot estimates. Per §9 step 5, rerun with pilot variance, eligibility and failure inputs before the confirmatory count is set.

## 1. What was simulated

**Estimator, unchanged from the analysis.** Item-level contrasts d_i are computed exactly as in `p1v3/estimands.py`: its `weights` are used, repeats are averaged within each item × cell over observed outcomes, and an item that lacks any needed cell is dropped. At startup the script checks itself against `estimate_one` on simulated data with heavy missingness (max |diff| 1.7e-16, with drops), against `inference.t_interval`, and against `inference.signflip_p` (agreement within Monte Carlo error). Estimands: E1, E2, E3, E4 (the primary Holm family) and S2.

**Data-generating process (one model).** Items are nested in families, with item i in family i mod F. Families are balanced: 24 items / 6 families, 60 / 12, 120 / 12. For each outcome (lookup_attempted, final_correct), item, cell and repeat:

logit p = μ_c + u_f + g_f·x_c + v_i + h_i·x_c + t_{i,snapshot,repeat}

- Random intercepts: family SD 0.5, item SD 1.0.
- Random slopes on 8 factor codes (wrong, stale, supplied, optional, pressure, pressure×wrong, pressure×supplied, pressure×wrong×supplied): family SD 0.2, item SD 0.4.
- A shared turn-1 effect t (SD 0.5), common to all 18 branches of one item × snapshot × repeat.
- 5 repeats, Bernoulli outcomes.
- μ_c is solved by Gauss–Hermite quadrature so that every cell's population-average probability equals a planted table. The planted contrasts Σ w_c P_c are therefore exact.

**Rate regimes.**
- *Ceiling:* neutral accuracy 0.98; lookup rate 0.02.
- *Moderate:* accuracy 0.60–0.90 by assertion and route, with stale snapshot −0.03; lookup rate 0.40.
- *Extreme* (stress test): accuracy 0.995; lookup rate 0.005.

**Planted effects.** Insistence penalties per (assertion, route) give the following truths.

| config | E4 | E3 | E2 | S2 | E1 (ceiling / moderate) |
|---|---|---|---|---|---|
| null | 0 | 0 | 0 | 0 | 0 / 0 |
| e4_0 | 0 | +0.05 | −0.025 | −0.075 | +0.02 / −0.10 |
| e4_small | −0.075 | +0.0375 | −0.0125 | −0.05 | +0.02 / −0.075 |
| e4_large | −0.15 | +0.075 | −0.025 | −0.10 | +0.04 / −0.15 |

In the ceiling regime, e4_large takes wrong-assertion optional-route accuracy down to 0.78. All other cells stay at 0.98.

**Missingness.** Three mechanisms: an item × snapshot is ineligible (the item is dropped); turn 1 fails for an item × snapshot × repeat (all 18 of its branches are lost); and individual trials fail.
- *light* (main grid): 1% / 2% / 2%.
- *heavy*: 4% / 8% / 8%.
- *informative*: light, plus incorrect final answers go missing with an extra probability of 0.15.

**Scenarios.**
- *Main:* 2 regimes × 4 effects × n ∈ {24, 60, 120}.
- *Stress:*
  - extreme regime, null effect, all three n;
  - strong families (family SDs 1.0 / 0.4), moderate regime, null and e4_large;
  - heavy and informative missingness at n = 60;
  - item-count search for the E4 floor: moderate at n = 72 / 84 / 96 with 12 families, ceiling at n = 36 / 6 families and n = 48 / 12 families;
  - family-count search: moderate e4_large at 96 items in 16 or 24 families, 120 in 20 or 30, 144 in 24 or 36.

**Interval methods (95%).**
- (a) `item_t`: `inference.t_interval` over items.
- (b) `family_t`: t interval over family means, df = F − 1. With equal items per family (every scenario in the main grid) this is identical to the CR1 family-clustered interval for the item-weighted mean that `analyze_p1.py` reports as `ci95_family_cr1` (checked in `tests/test_inference.py`). With unequal family sizes the two differ; extra B (§2.8) compares them.
- (c) `boot_item`: item-cluster percentile bootstrap.
- (d1) `boot_family`: family-cluster percentile bootstrap.
- (d2) `floor_t`: a boundary-safe item t. It has the same centre as item_t, with SE² = max(s², V_floor)/n. V_floor = Σ_c w_c² p̃_c(1 − p̃_c)/r_c, where p̃_c = (y_c + 1)/(N_c + 2) is pooled over items. This binomial lower bound on Var(d_i) means the interval can never have zero width.

**Tests.**
- The item-level sign-flip test (`inference.signflip_p`, 20,000 flips).
- The same test over family means (exact enumeration when F ≤ 16).
- Holm across E1–E4 for each test.

**Targets.**
- *Population (primary):* the planted contrast. Families and items are both random, so this is what a claim about new record families of this kind needs.
- *Family-conditional (secondary):* the expected contrast over new items from the sampled families, computed by quadrature for each replication. This is the target if claims stop at the sampled families.

**Monte Carlo error.** With 2000 replications, the SE of a coverage near 0.95 is 0.0049, so ±0.010 at 95%. The same SE applies to a rejection rate near 0.05.

## 2. Results

### 2.1 Coverage of the population target (table 1 of `sim_out/tables.md`): min / mean over 5 estimands × 4 effect configs

| regime | n (families) | item_t | family_t | boot_item | boot_family | floor_t |
|---|---|---|---|---|---|---|
| ceiling | 24 (6) | 0.884 / 0.924 | 0.918 / 0.942 | 0.859 / 0.898 | 0.823 / 0.851 | 0.901 / 0.956 |
| ceiling | 60 (12) | 0.893 / 0.925 | 0.918 / 0.943 | 0.886 / 0.913 | 0.883 / 0.902 | 0.893 / 0.938 |
| ceiling | 120 (12) | 0.843 / 0.903 | 0.931 / 0.944 | 0.833 / 0.894 | 0.890 / 0.903 | 0.843 / 0.909 |
| moderate | 24 (6) | 0.924 / 0.938 | 0.944 / 0.953 | 0.894 / 0.912 | 0.848 / 0.860 | 0.942 / 0.958 |
| moderate | 60 (12) | 0.914 / 0.933 | 0.941 / 0.951 | 0.898 / 0.921 | 0.892 / 0.908 | 0.919 / 0.944 |
| moderate | 120 (12) | 0.885 / 0.909 | 0.942 / 0.949 | 0.874 / 0.901 | 0.899 / 0.908 | 0.886 / 0.918 |

- **Family-clustered t is the only method that stays near nominal everywhere.** Across all 55 scenarios and all five estimands it ranges from 0.918 to 0.99, informative missingness aside. Informative missingness biases every method (2.5); there family_t reaches 0.893–0.92.
- Its tail misses are not always balanced near the ceiling. The worst one-sided miss is 0.079, for E2 at ceiling e4_0 with 24 items / 6 families (truth below the lower limit). There the penalty can only push accuracy down from 0.98, so the item contrasts are skewed. One-sided claims near a boundary should be read with this in mind.
- **Item t loses coverage as items are added while the number of families stays fixed.** Between-family variation in the contrasts does not average out, and the item SE ignores it.
  - With 120 items in 12 families: S2 0.84–0.91, E1 0.88–0.91, E2 0.87–0.91.
  - With strong families at 120 items: E1 0.78–0.79, S2 0.77–0.79.
  - This is the wrong direction for a confirmatory design: adding items makes the stated interval *less* honest about generalization.
- **E4 is the most robust estimand, because it is a difference of differences** (family heterogeneity largely cancels). E4 coverage by method:
  - item_t: 0.88–0.96. The worst case is ceiling e4_large n = 120, at 0.882 (0.075 / 0.042 per tail).
  - family_t: 0.94–0.96.
  - boot_item: 0.87–0.95.
  - boot_family: 0.85–0.94.
  - floor_t: 0.89–0.999.
- **The percentile bootstraps under-cover throughout.** boot_item runs 1–3 points below item_t, the usual small-sample percentile shrinkage. boot_family with 6 families covers 0.82–0.87. Neither is a candidate.
- **floor_t** fixes zero-width intervals, but it is otherwise the item t. It inherits the family under-coverage (S2 at ceiling n = 120: 0.843). At the null near a boundary it is conservative (E4 ceiling null: 0.99).
- **Family-conditional target (table 7).** If claims stop at the sampled families, item_t is accurate: 0.92–0.97 over the main grid, mean 0.95. family_t is mildly conservative there (0.94–0.97).

### 2.2 Boundaries and zero-width intervals (table 3)

- In the main grid (rates 0.02 / 0.98), zero-width intervals essentially never occur: at most 0.1% at n = 24, and 0 at n ≥ 60. At 0.98 accuracy, with 80 Bernoulli trials per item in an E4 contrast, all-identical d_i is very unlikely.
- In the extreme regime (0.995 / 0.005) with 24 items, 4.5% (t, item bootstrap) and 5.6% (family t, family bootstrap) of intervals have zero width. This drops to 0.1–0.2% at 60 items and 0 at 120.
- A zero-width interval at a true 0 is counted as "covering". That is why extreme-regime coverage looks high (0.96–0.99) and why §9 forbids reading such intervals.
- floor_t is never degenerate.
- Near the boundary, the ordinary t methods do not under-cover through collapse at n ≥ 24 under these rates. Their failure mode near the ceiling is family clustering (2.1), not collapse.

### 2.3 Sign-flip tests and Holm (table 5)

Rejection rates at α = 0.05 under a true 0. In each cell, the first number is the item-level test (`signflip_p`) and the second is the family-level test. Holm is the rate of any rejection across E1–E4 under the global null.

| scenario (null config) | E1 | E2 | E3 | E4 | S2 | Holm any |
|---|---|---|---|---|---|---|
| ceiling 24 / 6 | 0.027 / 0.006 | 0.032 / 0.003 | 0.037 / 0.012 | 0.037 / 0.011 | 0.036 / 0.007 | 0.028 / 0.000 |
| ceiling 60 / 12 | 0.047 / 0.042 | 0.054 / 0.039 | 0.053 / 0.047 | 0.045 / 0.043 | 0.050 / 0.042 | 0.047 / 0.039 |
| ceiling 120 / 12 | 0.054 / 0.044 | 0.064 / 0.051 | 0.055 / 0.046 | 0.052 / 0.052 | 0.065 / 0.054 | 0.062 / 0.040 |
| moderate 24 / 6 | 0.075 / 0.028 | 0.072 / 0.023 | 0.058 / 0.031 | 0.049 / 0.023 | 0.064 / 0.025 | 0.066 / 0.000 |
| moderate 60 / 12 | 0.071 / 0.042 | 0.075 / 0.053 | 0.052 / 0.039 | 0.053 / 0.045 | 0.066 / 0.047 | 0.070 / 0.045 |
| moderate 120 / 12 | 0.105 / 0.048 | 0.104 / 0.054 | 0.075 / 0.055 | 0.060 / 0.053 | 0.101 / 0.052 | 0.114 / 0.051 |
| strong families 60 / 12 | 0.136 / 0.046 | 0.115 / 0.042 | 0.089 / 0.048 | 0.066 / 0.050 | 0.137 / 0.048 | 0.130 / 0.045 |
| strong families 120 / 12 | 0.219 / 0.045 | 0.221 / 0.045 | 0.131 / 0.051 | 0.079 / 0.052 | 0.214 / 0.048 | 0.268 / 0.047 |
| extreme 24 / 6 | 0.003 / 0.000 | 0.000 / 0.000 | 0.013 / 0.000 | 0.013 / 0.002 | 0.005 / 0.000 | 0.003 / 0.000 |

- **The item-level sign-flip test is anti-conservative whenever families differ.** It flips items independently, so it tests "items exchangeable around 0", not "the population contrast is 0".
  - It reaches 0.10 for E1, E2 and S2 at 120 items in 12 families, and 0.22 with strong families.
  - Holm's familywise error then reaches 0.11 and 0.27.
  - E4 is the least affected (0.037–0.079 across all null and e4_0 scenarios).
  - It is close to nominal at the ceiling (0.027–0.065).
- **The family-level sign-flip test (exact) holds 0.04–0.06 in every scenario with ≥ 12 families**, including strong families, heavy and informative missingness, and the precision grid. Holm's familywise error stays at 0.04–0.05.
- With 6 families the exact test cannot go below p = 2/64 = 0.031. It is conservative there, and no Holm rejection is possible at all, because Holm's smallest threshold, 0.0125, is below that floor.
- **Power cost is modest from 60 items / 12 families up.** For E4 at moderate e4_large the rejection rates are:

  | items / families | item-level test | family-level test |
  |---|---|---|
  | 60 / 12 | 0.94 | 0.89 |
  | 120 / 12 | 0.999 | 0.995 |
  | 24 / 6 | 0.60 | 0.32 |

  The 24 / 6 power gap is large.
- **The family-t interval as a test** rejects a true 0 in 1 − coverage of runs: 0.03–0.06 across the null configs.

### 2.4 E4 half-width versus the 7.5 pp floor (table 4)

The floor counts as met when at least 80% of replications have a half-width ≤ 0.075. Each cell shows that share, then the 80th-percentile half-width.

| regime, effect | n / F | item_t | family_t | floor_t |
|---|---|---|---|---|
| ceiling, null | 24 / 6 | 0.95 / 0.062 | 0.74 / 0.082 | 0.87 / 0.072 |
| ceiling, e4_large | 24 / 6 | 0.19 / 0.105 | 0.14 / 0.152 | 0.06 / 0.106 |
| ceiling, e4_large | 36 / 6 | 0.59 / 0.083 | 0.25 / 0.129 | 0.55 / 0.083 |
| ceiling, e4_large | 48 / 12 | 0.89 / 0.071 | 0.53 / 0.089 | 0.89 / 0.071 |
| ceiling, e4_large | 60 / 12 | 0.99 / 0.062 | 0.70 / 0.081 | 0.99 / 0.062 |
| ceiling, e4_large | 120 / 12 | 1.00 / 0.043 | 0.96 / 0.064 | 1.00 / 0.043 |
| moderate, e4_large | 60 / 12 | 0.18 / 0.090 | 0.22 / 0.108 | 0.00 / 0.095 |
| moderate, e4_large | 72 / 12 | 0.48 / 0.082 | 0.33 / 0.099 | 0.03 / 0.086 |
| moderate, e4_large | 84 / 12 | 0.79 / 0.075 | 0.45 / 0.092 | 0.38 / 0.079 |
| moderate, e4_large | 96 / 12 | 0.95 / 0.070 | 0.58 / 0.086 | 0.91 / 0.073 |
| moderate, e4_large | 120 / 12 | 1.00 / 0.062 | 0.74 / 0.078 | 1.00 / 0.065 |
| moderate, e4_large | 96 / 16 | 0.95 / 0.070 | 0.63 / 0.082 | 0.91 / 0.074 |
| moderate, e4_large | 96 / 24 | 0.95 / 0.070 | 0.73 / 0.078 | 0.93 / 0.073 |
| moderate, e4_large | 120 / 20 | 1.00 / 0.062 | 0.87 / 0.072 | 1.00 / 0.065 |
| moderate, e4_large | 120 / 30 | 1.00 / 0.062 | 0.95 / 0.068 | 1.00 / 0.065 |
| moderate, e4_large | 144 / 24 | 1.00 / 0.056 | 0.98 / 0.064 | 1.00 / 0.059 |
| moderate, e4_large | 144 / 36 | 1.00 / 0.056 | 1.00 / 0.061 | 1.00 / 0.059 |

In this family-count grid, family_t covers every estimand at 0.941–0.959.

- The moderate null config needs slightly fewer items than e4_large (n = 84: 0.91 for item_t; n = 120: 0.83 for family_t). The e4_small and e4_0 configs fall between the two (see `tables.md`).
- **Item count drives item-t precision. Family count drives family-t precision:** with 12 families, family_t's df of 11 and the noise in its family means keep it wide whatever the item count.
- Wider intervals at the ceiling under e4_large come from the wrong-assertion cells falling to 0.78. More binomial variance there pushes ceiling-regime needs up to the 48–60 item range.
- The 60-item / 12-family development set (base + extension) meets the floor only when accuracy is near the ceiling. In the moderate regime it reaches 0.18–0.36 (item_t) or 0.22–0.32 (family_t).

### 2.5 Missingness

- Heavy MCAR missingness at n = 60 removes about 8% of items. It widens intervals (moderate e4_large, item_t p80 0.090 → 0.101) but leaves coverage where it was. family_t covers E4 at 0.94–0.96.
- **Informative missingness biases the estimate.** At the ceiling with e4_large, E4 bias is +0.012 and S2 bias +0.008. E4 coverage falls to 0.88 (item_t) and 0.92 (family_t); S2 falls to 0.85 and 0.90. No interval method repairs this. It is what the sign-aware assigned-denominator bounds exist for, and they must accompany every primary estimate.

### 2.6 Repeats versus items (table 8)

The within-item share of Var(d_i) for E4 is the mean of the per-item repeat-to-repeat variance divided by R, over the total variance of d_i. It covers binomial plus turn-1 noise, which more repeats would shrink.

| regime and effect | within-item share |
|---|---|
| moderate | 0.89–0.95 |
| ceiling, e4_large | 0.64 |
| ceiling, null | 0.98 |

Under these assumed heterogeneity SDs, within-item noise dominates. So §7 step 2 ("add repeats only if within-item variance dominates") would allow repeats, and with a share around 0.9, doubling repeats to 10 cuts Var(d_i) by about 45%. This conclusion depends entirely on the assumed between-item slope SD. The pilot must estimate the share from per-repeat item contrasts, which this script's `within_share` computes. Repeats do not add families, so they do not relieve family_t's df limit.

### 2.8 Extras (`--part extras`; `sim_out/tables_extras.md`, `asym_typeI.csv`, `unequal_families.csv`; 10,000 replications per row)

- **A. Asymmetric item effects with population mean exactly 0** (E2 and E4 scales; n = 24 and 60). The one-sample t-test held 0.046–0.058 two-sided; the item-level sign-flip held 0.037–0.051. Under these independent-item scenarios (no family clustering) neither test was anti-conservative; the sign-flip's problem in §2.3 is family clustering, not skew.
- **B. Unequal family sizes (4 or 6 items per family, as in the 60-item development set).** With a family-size effect on the contrast, the unweighted mean-of-family-means t interval targets the equal-family estimand and is lopsided for the item-weighted target (e.g. 12 families: 0.941, tails 0.046 / 0.013). The CR1 cluster-robust interval for the item-weighted mean (G − 1 df) covers the item-weighted target at 0.946–0.950 in every row. Item t: 0.893–0.934.
- **Consequence for the development data.** The combined base + extension set has 4 items per family in the 6 base families and 6 in the 6 extension families. So the family-clustered interval reported next to the item-weighted estimate must be CR1 (`ci95_family_cr1`), not t over family means. The latter is the interval for the equal-family estimate, and `analyze_p1.py` reports it as `ci95_equal_family_t` beside `equal_family_weight_estimate`. The family-level sign-flip test in `p1v3/inference.py` flips family **totals**, so it tests the same item-weighted mean. With equal family sizes, it is the flip over family means simulated in §2.3.

### 2.7 Limitations

- **Single model.** No cross-model pooling and no per-model heterogeneity beyond what the regimes represent.
- **No first-answer strata.** The joint first-answer strata (CC/CW/WC/WW) are not modelled; E4 is identified on assigned factors, so its coverage does not depend on them. The realized-disagreement secondary is not simulated.
- **Logit-normal random effects with assumed SDs.** The strong-family stress test shows the direction of sensitivity.
- **No SESOI-based probabilities.** The probabilities of equivalence, meaningful-effect or inconclusive conclusions (§9 step 2, last paragraph) are not computed: the SESOIs are not fixed yet. The per-replication intervals in this script are what such a calculation would reuse.
- **Fixed sign-flip draws.** Sign-flip flips are fixed within a chunk of up to 100 replications. The reference also reuses one seed, so each p-value is a valid randomization p-value.

## 3. Recommendation for the PI (decision not yet taken; this section is a recommendation, not a spec change)

**R1. Prespecify the family-clustered t interval (t over family means, df = F − 1) as the confirmatory 95% interval for E1–E4,** and for the secondaries.
- *Why:* it is the only method that keeps nominal coverage of the population contrast for every estimand, regime, family strength and missingness pattern tested, informative missingness aside. Its range is 0.918–0.99. Item-based intervals fall to 0.84 (and 0.77 with strong families), and they get *worse* as items are added within a fixed set of families.
- *Balanced families:* prespecify equal items per family, so its centre equals the item mean that `estimands.py` reports. If families end up unbalanced, prespecify the weighting before data.
- *Spec wording:* §6 says "claims are limited to the sampled families". If the PI keeps that wording as the confirmatory target, the item t interval is valid for it (0.92–0.97 against the family-conditional target) and R1 changes to item t. Whichever target is chosen must be written down before the pilot. The item t interval must not carry a claim about record families in general.

**R2. Report the item t interval and the leave-one-family-out range alongside, labelled "sampled families only".**

**R3. Test with the family-level sign-flip test (exact enumeration over family means) and Holm across E1–E4,** or equivalently read the family-t interval. Do not use the current item-level `signflip_p` for confirmatory decisions: its type-I error reaches 0.10–0.22, and Holm's familywise error 0.11–0.27, under family heterogeneity. Both the family-level test and Holm need **at least 12 families**. With 6, no Holm rejection is possible.

**R4. Do not use either percentile bootstrap:** item-cluster 0.83–0.95, family-cluster 0.82–0.94.

**R5. Zero-width rule.** A zero-width interval is never reported as an interval. Report instead the `floor_t` interval (conservative, never zero-width) and the assigned-denominator bounds, and flag the contrast.
- *How often:* fewer than 0.2% of runs at rates of 0.02 / 0.98 with any n, but 4.5–5.6% at 0.005 / 0.995 with 24 items.
- *Why not use floor_t throughout:* it inherits the item-level family under-coverage. It is a guard, not a primary method.

**R6. The E4 precision floor (half-width ≤ 7.5 pp in ≥ 80% of runs).**
- *With the family-t interval (R1):*
  - Moderate accuracy (0.6–0.9): needs about **120 items in at least 20 families**. That gives 0.87 at 120 / 20, 0.95 at 120 / 30 and 0.98 at 144 / 24. Twelve families are not enough at any item count tested (0.74 at 120 / 12). At 96 items, even 24 families give only 0.73.
  - Accuracy near 0.98: 120 / 12 suffices (0.96); 60 / 12 does not under the large-effect configuration (0.70).
  - **Suggested planning count: 144 items in 24 families (6 per family).** That gives 0.98 in the harder regime, with margin for pilot variance that may be larger than assumed here.
- *With item t (sampled-families target):* about 96 items at moderate accuracy (0.95; 84 items give 0.79), and 48–60 near the ceiling.
- *Current development set (60 items / 12 families):* meets the floor only if accuracy is near the ceiling. At moderate accuracy, 0.18–0.36 of runs meet it.
- *Next step:* the item and family counts must be re-derived from this script with pilot variance inputs (§9 step 5) before the confirmatory count is fixed.

**R7. Repeats are a secondary lever, to be decided from pilot data.** Under the assumed heterogeneity, within-item noise is 0.64–0.98 of Var(d_i) for E4, so more repeats would narrow the item-level interval substantially. Compute that share in the pilot from per-repeat item contrasts before adding repeats. Repeats do not add families, so they cannot replace R6's family count under R1.

**R8. Keep the assigned-denominator bounds next to every primary interval.** Informative missingness of the size simulated (+15% loss of incorrect answers) biases E4 by about +1.2 pp near the ceiling and pulls coverage to 0.88–0.92. No interval method corrects this.
