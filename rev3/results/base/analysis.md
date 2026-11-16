# P1 analysis

**DEVELOPMENT-CASE EVALUATION: builder-written dev families, pressure paraphrases not yet rated (§5), intervals and p-values provisional: the §9 coverage simulation recommends a family-clustered method (SIM_P1_COVERAGE.md §3) but the PI has not fixed the confirmatory method. Not confirmatory evidence.**

Runs ['runs/p1_dev_eval_v2']: 24 items, 6 families. Intervals and p-values are provisional (the PI has not fixed the confirmatory method); Holm is across E1–E4 within model × pressure.

Columns: *items t* = 95% t interval with items as clusters (df = items − 1; the prespecified provisional method; anti-conservative for new families when families differ). *families CR1* = 95% interval for the same item-weighted mean with families as clusters (CR1, t with df = F − 1; labelled sensitivity, the method the coverage simulation recommends). *p fam CR1* = matching t-test; *p fam flip* = exact sign-flip over family totals (smallest attainable p = 2/2^F: 0.031 at 6 families, 0.00049 at 12); Holm-adjusted values in parentheses for E1–E4. ⚑ = excludes 0 under items t only.

## deepseek-v3.2

Status {'ok': 4320}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 2160}, 'stale': {'rate': 1.0, 'n': 2160}}. Neutral optional attempt rate {'rate': 1.0, 'n': 480}. Neutral supplied adoption {'rate': 0.9957983193277311, 'n': 476}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.010 | [-0.021, +0.000] | [-0.023, +0.002] | 0.057 (0.077) | 0.093 (0.23) | 0.25 (0.38) | [-0.010, -0.010] | 24 / 0 |
| E1b_delta_relevant | insistence | -0.010 | [-0.021, +0.000] | [-0.023, +0.002] | 0.057 | 0.093 | 0.25 | [-0.010, -0.010] | 24 / 0 |
| E2_delta_acc_supplied | insistence | -0.025 | [-0.040, -0.010] | [-0.047, -0.003] | 0.0025 (0.01) | 0.033 (0.13) | 0.062 (0.25) | [-0.027, -0.017] | 24 / 0 |
| E3_delivery_effect | insistence | -0.019 ⚑ | [-0.035, -0.002] | [-0.040, +0.003] | 0.026 (0.077) | 0.076 (0.23) | 0.12 (0.38) | [-0.021, -0.010] | 24 / 0 |
| E4_moderation | insistence | +0.037 ⚑ | [+0.005, +0.070] | [-0.006, +0.081] | 0.026 (0.077) | 0.076 (0.23) | 0.12 (0.38) | [+0.021, +0.042] | 24 / 0 |
| S2_delta_acc_none | insistence | +0.158 | [+0.121, +0.196] | [+0.117, +0.200] | 7.9e-09 | 0.00018 | 0.031 | [+0.158, +0.158] | 24 / 0 |
| E1_delta_attempt | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 24 / 0 |
| E1b_delta_relevant | authority | -0.004 | [-0.010, +0.002] | [-0.011, +0.003] | 0.16 | 0.17 | 0.5 | [-0.004, -0.004] | 24 / 0 |
| E2_delta_acc_supplied | authority | +0.000 | [-0.009, +0.009] | [-0.014, +0.014] | 1 (1) | 1 (1) | 1 (1) | [-0.004, +0.008] | 24 / 0 |
| E3_delivery_effect | authority | +0.004 | [-0.008, +0.016] | [-0.016, +0.024] | 0.49 (1) | 0.61 (1) | 0.88 (1) | [+0.000, +0.012] | 24 / 0 |
| E4_moderation | authority | -0.008 | [-0.033, +0.016] | [-0.048, +0.031] | 0.49 (1) | 0.61 (1) | 0.88 (1) | [-0.025, +0.000] | 24 / 0 |
| S2_delta_acc_none | authority | +0.021 | [-0.008, +0.050] | [-0.002, +0.044] | 0.15 | 0.067 | 0.12 | [+0.021, +0.021] | 24 / 0 |

## gpt-oss-120b

Status {'ok': 4320}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 2160}, 'stale': {'rate': 1.0, 'n': 2160}}. Neutral optional attempt rate {'rate': 0.9916666666666667, 'n': 480}. Neutral supplied adoption {'rate': 1.0, 'n': 480}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.110 | [-0.139, -0.082] | [-0.147, -0.074] | 4.2e-08 (1.7e-07) | 0.00057 (0.0023) | 0.031 (0.12) | [-0.110, -0.110] | 24 / 0 |
| E1b_delta_relevant | insistence | -0.110 | [-0.139, -0.082] | [-0.147, -0.074] | 4.2e-08 | 0.00057 | 0.031 | [-0.110, -0.110] | 24 / 0 |
| E2_delta_acc_supplied | insistence | -0.006 | [-0.013, +0.001] | [-0.017, +0.005] | 0.083 (0.083) | 0.2 (0.2) | 0.5 (0.5) | [-0.008, -0.006] | 24 / 0 |
| E3_delivery_effect | insistence | +0.054 | [+0.022, +0.086] | [+0.026, +0.083] | 0.0021 (0.0062) | 0.0044 (0.013) | 0.031 (0.12) | [+0.052, +0.054] | 24 / 0 |
| E4_moderation | insistence | -0.075 | [-0.128, -0.022] | [-0.135, -0.015] | 0.0078 (0.016) | 0.023 (0.047) | 0.062 (0.12) | [-0.075, -0.071] | 24 / 0 |
| S2_delta_acc_none | insistence | +0.015 | [-0.025, +0.054] | [-0.039, +0.068] | 0.45 | 0.51 | 0.56 | [+0.015, +0.017] | 24 / 0 |
| E1_delta_attempt | authority | -0.019 ⚑ | [-0.034, -0.004] | [-0.055, +0.017] | 0.017 (0.066) | 0.24 (0.95) | 0.25 (1) | [-0.019, -0.019] | 24 / 0 |
| E1b_delta_relevant | authority | -0.019 ⚑ | [-0.034, -0.004] | [-0.055, +0.017] | 0.017 | 0.24 | 0.25 | [-0.019, -0.019] | 24 / 0 |
| E2_delta_acc_supplied | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 24 / 0 |
| E3_delivery_effect | authority | +0.008 | [-0.004, +0.020] | [-0.013, +0.030] | 0.16 (0.49) | 0.36 (1) | 1 (1) | [+0.008, +0.008] | 24 / 0 |
| E4_moderation | authority | +0.008 | [-0.009, +0.026] | [-0.013, +0.030] | 0.33 (0.66) | 0.36 (1) | 1 (1) | [+0.008, +0.008] | 24 / 0 |
| S2_delta_acc_none | authority | -0.073 ⚑ | [-0.115, -0.031] | [-0.147, +0.001] | 0.0015 | 0.052 | 0.094 | [-0.073, -0.071] | 24 / 0 |

## kimi-k2-0905

Status {'ok': 4320}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 2160}, 'stale': {'rate': 1.0, 'n': 2160}}. Neutral optional attempt rate {'rate': 0.20833333333333334, 'n': 480}. Neutral supplied adoption {'rate': 1.0, 'n': 480}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.069 | [-0.120, -0.017] | [-0.112, -0.026] | 0.011 (0.043) | 0.0092 (0.037) | 0.031 (0.12) | [-0.069, -0.069] | 24 / 0 |
| E1b_delta_relevant | insistence | -0.069 | [-0.120, -0.017] | [-0.112, -0.026] | 0.011 | 0.0092 | 0.031 | [-0.069, -0.069] | 24 / 0 |
| E2_delta_acc_supplied | insistence | -0.002 | [-0.006, +0.002] | [-0.007, +0.003] | 0.33 (0.34) | 0.36 (0.46) | 1 (1) | [-0.002, -0.002] | 24 / 0 |
| E3_delivery_effect | insistence | +0.079 | [+0.018, +0.140] | [+0.022, +0.136] | 0.013 (0.043) | 0.016 (0.047) | 0.031 (0.12) | [+0.079, +0.079] | 24 / 0 |
| E4_moderation | insistence | +0.075 | [-0.034, +0.184] | [-0.066, +0.216] | 0.17 (0.34) | 0.23 (0.46) | 0.28 (0.56) | [+0.075, +0.075] | 24 / 0 |
| S2_delta_acc_none | insistence | -0.048 ⚑ | [-0.094, -0.002] | [-0.117, +0.021] | 0.042 | 0.13 | 0.19 | [-0.048, -0.048] | 24 / 0 |
| E1_delta_attempt | authority | -0.004 | [-0.057, +0.048] | [-0.063, +0.055] | 0.87 (1) | 0.86 (1) | 1 (1) | [-0.004, -0.004] | 24 / 0 |
| E1b_delta_relevant | authority | -0.004 | [-0.057, +0.048] | [-0.063, +0.055] | 0.87 | 0.86 | 1 | [-0.004, -0.004] | 24 / 0 |
| E2_delta_acc_supplied | authority | -0.002 | [-0.006, +0.002] | [-0.007, +0.003] | 0.33 (1) | 0.36 (1) | 1 (1) | [-0.002, -0.002] | 24 / 0 |
| E3_delivery_effect | authority | +0.025 | [-0.039, +0.089] | [-0.061, +0.111] | 0.43 (1) | 0.49 (1) | 0.56 (1) | [+0.025, +0.025] | 24 / 0 |
| E4_moderation | authority | +0.000 | [-0.121, +0.121] | [-0.106, +0.106] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 24 / 0 |
| S2_delta_acc_none | authority | -0.073 ⚑ | [-0.123, -0.022] | [-0.177, +0.031] | 0.0067 | 0.13 | 0.16 | [-0.073, -0.073] | 24 / 0 |

## qwen3-235b-a22b-2507

Status {'ok': 4320}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 2160}, 'stale': {'rate': 1.0, 'n': 2160}}. Neutral optional attempt rate {'rate': 0.8270833333333333, 'n': 480}. Neutral supplied adoption {'rate': 1.0, 'n': 480}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.500 | [-0.547, -0.453] | [-0.588, -0.412] | 0 (0) | 2.7e-05 (0.00011) | 0.031 (0.12) | [-0.500, -0.500] | 24 / 0 |
| E1b_delta_relevant | insistence | -0.500 | [-0.547, -0.453] | [-0.588, -0.412] | 0 | 2.7e-05 | 0.031 | [-0.500, -0.500] | 24 / 0 |
| E2_delta_acc_supplied | insistence | -0.004 | [-0.010, +0.002] | [-0.015, +0.007] | 0.16 (0.16) | 0.36 (0.36) | 1 (1) | [-0.004, -0.004] | 24 / 0 |
| E3_delivery_effect | insistence | +0.269 | [+0.228, +0.310] | [+0.208, +0.330] | 2.1e-12 (6.2e-12) | 9.3e-05 (0.00028) | 0.031 (0.12) | [+0.269, +0.269] | 24 / 0 |
| E4_moderation | insistence | -0.429 | [-0.519, -0.340] | [-0.556, -0.302] | 8.6e-10 (1.7e-09) | 0.00033 (0.00066) | 0.031 (0.12) | [-0.429, -0.429] | 24 / 0 |
| S2_delta_acc_none | insistence | +0.077 ⚑ | [+0.012, +0.142] | [-0.022, +0.176] | 0.022 | 0.1 | 0.094 | [+0.077, +0.077] | 24 / 0 |
| E1_delta_attempt | authority | +0.035 | [-0.005, +0.076] | [-0.019, +0.090] | 0.081 (0.32) | 0.16 (0.63) | 0.22 (0.88) | [+0.035, +0.035] | 24 / 0 |
| E1b_delta_relevant | authority | +0.035 | [-0.005, +0.076] | [-0.019, +0.090] | 0.081 | 0.16 | 0.22 | [+0.035, +0.035] | 24 / 0 |
| E2_delta_acc_supplied | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 24 / 0 |
| E3_delivery_effect | authority | +0.010 | [-0.020, +0.041] | [-0.040, +0.060] | 0.49 (0.97) | 0.62 (1) | 0.69 (1) | [+0.010, +0.010] | 24 / 0 |
| E4_moderation | authority | +0.046 | [-0.020, +0.112] | [-0.039, +0.131] | 0.16 (0.49) | 0.23 (0.68) | 0.31 (0.94) | [+0.046, +0.046] | 24 / 0 |
| S2_delta_acc_none | authority | -0.002 | [-0.028, +0.024] | [-0.026, +0.022] | 0.87 | 0.83 | 1 | [-0.002, -0.002] | 24 / 0 |
