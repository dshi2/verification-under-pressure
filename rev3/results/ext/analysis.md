# P1 analysis

**DEVELOPMENT-CASE EVALUATION: builder-written dev families, pressure paraphrases not yet rated (§5), intervals and p-values provisional: the §9 coverage simulation recommends a family-clustered method (SIM_P1_COVERAGE.md §3) but the PI has not fixed the confirmatory method. Not confirmatory evidence.**

Runs ['runs/p1_ext_v2']: 36 items, 6 families. Intervals and p-values are provisional (the PI has not fixed the confirmatory method); Holm is across E1–E4 within model × pressure.

Columns: *items t* = 95% t interval with items as clusters (df = items − 1; the prespecified provisional method; anti-conservative for new families when families differ). *families CR1* = 95% interval for the same item-weighted mean with families as clusters (CR1, t with df = F − 1; labelled sensitivity, the method the coverage simulation recommends). *p fam CR1* = matching t-test; *p fam flip* = exact sign-flip over family totals (smallest attainable p = 2/2^F: 0.031 at 6 families, 0.00049 at 12); Holm-adjusted values in parentheses for E1–E4. ⚑ = excludes 0 under items t only.

## deepseek-v3.2

Status {'ok': 6480}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 3240}, 'stale': {'rate': 1.0, 'n': 3240}}. Neutral optional attempt rate {'rate': 1.0, 'n': 720}. Neutral supplied adoption {'rate': 0.9902097902097902, 'n': 715}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.015 ⚑ | [-0.023, -0.007] | [-0.031, +0.001] | 0.00039 (0.0016) | 0.058 (0.12) | 0.12 (0.25) | [-0.015, -0.015] | 36 / 0 |
| E1b_delta_relevant | insistence | -0.014 ⚑ | [-0.022, -0.006] | [-0.030, +0.002] | 0.0008 | 0.08 | 0.12 | [-0.014, -0.014] | 36 / 0 |
| E2_delta_acc_supplied | insistence | -0.024 | [-0.043, -0.005] | [-0.042, -0.006] | 0.014 (0.042) | 0.02 (0.06) | 0.031 (0.12) | [-0.028, -0.017] | 36 / 0 |
| E3_delivery_effect | insistence | -0.017 | [-0.036, +0.001] | [-0.029, -0.005] | 0.07 (0.14) | 0.014 (0.055) | 0.031 (0.12) | [-0.021, -0.010] | 36 / 0 |
| E4_moderation | insistence | +0.017 | [-0.011, +0.046] | [-0.024, +0.059] | 0.23 (0.23) | 0.33 (0.33) | 0.38 (0.38) | [+0.003, +0.025] | 36 / 0 |
| S2_delta_acc_none | insistence | +0.146 | [+0.117, +0.175] | [+0.089, +0.203] | 6.3e-12 | 0.0012 | 0.031 | [+0.146, +0.146] | 36 / 0 |
| E1_delta_attempt | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 36 / 0 |
| E1b_delta_relevant | authority | +0.001 | [-0.001, +0.004] | [-0.002, +0.005] | 0.32 | 0.36 | 1 | [+0.001, +0.001] | 36 / 0 |
| E2_delta_acc_supplied | authority | +0.003 | [-0.006, +0.012] | [-0.010, +0.016] | 0.53 (1) | 0.61 (1) | 1 (1) | [-0.004, +0.010] | 36 / 0 |
| E3_delivery_effect | authority | +0.001 | [-0.008, +0.011] | [-0.013, +0.015] | 0.77 (1) | 0.81 (1) | 1 (1) | [-0.006, +0.008] | 36 / 0 |
| E4_moderation | authority | -0.014 | [-0.032, +0.004] | [-0.037, +0.009] | 0.13 (0.53) | 0.19 (0.74) | 0.5 (1) | [-0.039, -0.011] | 36 / 0 |
| S2_delta_acc_none | authority | +0.004 | [-0.014, +0.022] | [-0.023, +0.032] | 0.65 | 0.71 | 0.81 | [+0.004, +0.004] | 36 / 0 |

## gpt-oss-120b

Status {'ok': 6480}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 3240}, 'stale': {'rate': 1.0, 'n': 3240}}. Neutral optional attempt rate {'rate': 0.9888888888888889, 'n': 720}. Neutral supplied adoption {'rate': 0.9986072423398329, 'n': 718}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.093 ⚑ | [-0.131, -0.055] | [-0.193, +0.007] | 1.7e-05 (6.9e-05) | 0.062 (0.25) | 0.031 (0.12) | [-0.093, -0.093] | 36 / 0 |
| E1b_delta_relevant | insistence | -0.093 ⚑ | [-0.131, -0.055] | [-0.193, +0.007] | 1.7e-05 | 0.062 | 0.031 | [-0.093, -0.093] | 36 / 0 |
| E2_delta_acc_supplied | insistence | -0.003 | [-0.008, +0.003] | [-0.015, +0.009] | 0.32 (0.32) | 0.58 (0.58) | 1 (1) | [-0.006, +0.000] | 36 / 0 |
| E3_delivery_effect | insistence | +0.039 ⚑ | [+0.011, +0.067] | [-0.024, +0.102] | 0.008 (0.024) | 0.17 (0.35) | 0.19 (0.56) | [+0.036, +0.042] | 36 / 0 |
| E4_moderation | insistence | -0.028 | [-0.064, +0.008] | [-0.066, +0.010] | 0.12 (0.25) | 0.12 (0.35) | 0.19 (0.56) | [-0.033, -0.022] | 36 / 0 |
| S2_delta_acc_none | insistence | +0.028 | [-0.004, +0.059] | [-0.022, +0.077] | 0.082 | 0.21 | 0.31 | [+0.028, +0.029] | 36 / 0 |
| E1_delta_attempt | authority | -0.003 | [-0.019, +0.013] | [-0.024, +0.018] | 0.73 (1) | 0.75 (1) | 1 (1) | [-0.003, -0.003] | 36 / 0 |
| E1b_delta_relevant | authority | -0.003 | [-0.019, +0.013] | [-0.024, +0.018] | 0.73 | 0.75 | 1 | [-0.003, -0.003] | 36 / 0 |
| E2_delta_acc_supplied | authority | -0.001 | [-0.006, +0.004] | [-0.008, +0.005] | 0.57 (1) | 0.61 (1) | 1 (1) | [-0.003, +0.001] | 36 / 0 |
| E3_delivery_effect | authority | -0.004 | [-0.018, +0.009] | [-0.013, +0.005] | 0.54 (1) | 0.3 (0.89) | 0.5 (1) | [-0.006, -0.001] | 36 / 0 |
| E4_moderation | authority | +0.019 | [-0.012, +0.051] | [-0.015, +0.053] | 0.21 (0.85) | 0.2 (0.8) | 0.38 (1) | [+0.017, +0.025] | 36 / 0 |
| S2_delta_acc_none | authority | +0.001 | [-0.022, +0.025] | [-0.045, +0.048] | 0.9 | 0.94 | 1 | [+0.001, +0.003] | 36 / 0 |

## kimi-k2-0905

Status {'ok': 6480}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 3240}, 'stale': {'rate': 1.0, 'n': 3240}}. Neutral optional attempt rate {'rate': 0.14027777777777778, 'n': 720}. Neutral supplied adoption {'rate': 1.0, 'n': 720}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.050 ⚑ | [-0.087, -0.013] | [-0.137, +0.037] | 0.0096 (0.039) | 0.2 (0.7) | 0.22 (0.88) | [-0.050, -0.050] | 36 / 0 |
| E1b_delta_relevant | insistence | -0.050 ⚑ | [-0.087, -0.013] | [-0.137, +0.037] | 0.0096 | 0.2 | 0.22 | [-0.050, -0.050] | 36 / 0 |
| E2_delta_acc_supplied | insistence | -0.006 ⚑ | [-0.011, -0.000] | [-0.015, +0.003] | 0.044 (0.13) | 0.17 (0.7) | 0.5 (1) | [-0.006, -0.006] | 36 / 0 |
| E3_delivery_effect | insistence | +0.032 | [-0.014, +0.078] | [-0.068, +0.132] | 0.17 (0.34) | 0.45 (0.9) | 0.47 (1) | [+0.032, +0.032] | 36 / 0 |
| E4_moderation | insistence | -0.025 | [-0.094, +0.044] | [-0.130, +0.080] | 0.47 (0.47) | 0.57 (0.9) | 0.69 (1) | [-0.025, -0.025] | 36 / 0 |
| S2_delta_acc_none | insistence | -0.031 | [-0.072, +0.011] | [-0.106, +0.044] | 0.14 | 0.34 | 0.34 | [-0.031, -0.031] | 36 / 0 |
| E1_delta_attempt | authority | -0.028 | [-0.068, +0.013] | [-0.088, +0.032] | 0.17 (0.6) | 0.29 (1) | 0.34 (1) | [-0.028, -0.028] | 36 / 0 |
| E1b_delta_relevant | authority | -0.028 | [-0.068, +0.013] | [-0.088, +0.032] | 0.17 | 0.29 | 0.34 | [-0.028, -0.028] | 36 / 0 |
| E2_delta_acc_supplied | authority | -0.001 | [-0.004, +0.001] | [-0.005, +0.002] | 0.32 (0.65) | 0.36 (1) | 1 (1) | [-0.001, -0.001] | 36 / 0 |
| E3_delivery_effect | authority | +0.031 | [-0.012, +0.073] | [-0.039, +0.100] | 0.15 (0.6) | 0.31 (1) | 0.5 (1) | [+0.031, +0.031] | 36 / 0 |
| E4_moderation | authority | +0.028 | [-0.044, +0.100] | [-0.084, +0.140] | 0.44 (0.65) | 0.55 (1) | 0.56 (1) | [+0.028, +0.028] | 36 / 0 |
| S2_delta_acc_none | authority | -0.062 ⚑ | [-0.095, -0.030] | [-0.128, +0.003] | 0.00037 | 0.057 | 0.094 | [-0.062, -0.062] | 36 / 0 |

## qwen3-235b-a22b-2507

Status {'ok': 6480}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 3240}, 'stale': {'rate': 1.0, 'n': 3240}}. Neutral optional attempt rate {'rate': 0.7777777777777778, 'n': 720}. Neutral supplied adoption {'rate': 1.0, 'n': 720}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.494 | [-0.527, -0.462] | [-0.559, -0.430] | 0 (0) | 6.3e-06 (2.5e-05) | 0.031 (0.12) | [-0.494, -0.494] | 36 / 0 |
| E1b_delta_relevant | insistence | -0.494 | [-0.527, -0.462] | [-0.559, -0.430] | 0 | 6.3e-06 | 0.031 | [-0.494, -0.494] | 36 / 0 |
| E2_delta_acc_supplied | insistence | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 36 / 0 |
| E3_delivery_effect | insistence | +0.247 | [+0.222, +0.272] | [+0.209, +0.285] | 0 (0) | 1.4e-05 (4.3e-05) | 0.031 (0.12) | [+0.247, +0.247] | 36 / 0 |
| E4_moderation | insistence | -0.389 | [-0.449, -0.328] | [-0.499, -0.279] | 5.1e-15 (1e-14) | 0.00027 (0.00054) | 0.031 (0.12) | [-0.389, -0.389] | 36 / 0 |
| S2_delta_acc_none | insistence | +0.081 ⚑ | [+0.038, +0.123] | [-0.004, +0.165] | 0.00043 | 0.058 | 0.031 | [+0.081, +0.081] | 36 / 0 |
| E1_delta_attempt | authority | +0.047 ⚑ | [+0.009, +0.085] | [-0.023, +0.118] | 0.016 (0.048) | 0.15 (0.44) | 0.25 (0.75) | [+0.047, +0.047] | 36 / 0 |
| E1b_delta_relevant | authority | +0.047 ⚑ | [+0.009, +0.085] | [-0.023, +0.118] | 0.016 | 0.15 | 0.25 | [+0.047, +0.047] | 36 / 0 |
| E2_delta_acc_supplied | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 36 / 0 |
| E3_delivery_effect | authority | -0.008 | [-0.036, +0.019] | [-0.057, +0.040] | 0.54 (1) | 0.68 (1) | 0.81 (1) | [-0.008, -0.008] | 36 / 0 |
| E4_moderation | authority | +0.106 | [+0.049, +0.162] | [+0.044, +0.167] | 0.00058 (0.0023) | 0.0068 (0.027) | 0.062 (0.25) | [+0.106, +0.106] | 36 / 0 |
| S2_delta_acc_none | authority | -0.006 | [-0.026, +0.015] | [-0.045, +0.034] | 0.59 | 0.73 | 0.81 | [-0.006, -0.006] | 36 / 0 |
