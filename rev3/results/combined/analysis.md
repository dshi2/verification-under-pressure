# P1 analysis

**DEVELOPMENT-CASE EVALUATION: builder-written dev families, pressure paraphrases not yet rated (§5), intervals and p-values provisional: the §9 coverage simulation recommends a family-clustered method (SIM_P1_COVERAGE.md §3) but the PI has not fixed the confirmatory method. Not confirmatory evidence.**

Runs ['runs/p1_dev_eval_v2', 'runs/p1_ext_v2']: 60 items, 12 families. Intervals and p-values are provisional (the PI has not fixed the confirmatory method); Holm is across E1–E4 within model × pressure.

Columns: *items t* = 95% t interval with items as clusters (df = items − 1; the prespecified provisional method; anti-conservative for new families when families differ). *families CR1* = 95% interval for the same item-weighted mean with families as clusters (CR1, t with df = F − 1; labelled sensitivity, the method the coverage simulation recommends). *p fam CR1* = matching t-test; *p fam flip* = exact sign-flip over family totals (smallest attainable p = 2/2^F: 0.031 at 6 families, 0.00049 at 12); Holm-adjusted values in parentheses for E1–E4. ⚑ = excludes 0 under items t only.

## deepseek-v3.2

Status {'ok': 10800}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 5400}, 'stale': {'rate': 1.0, 'n': 5400}}. Neutral optional attempt rate {'rate': 1.0, 'n': 1200}. Neutral supplied adoption {'rate': 0.9924433249370277, 'n': 1191}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.013 | [-0.020, -0.007] | [-0.022, -0.004] | 6.9e-05 (0.00028) | 0.0078 (0.016) | 0.016 (0.031) | [-0.013, -0.013] | 60 / 0 |
| E1b_delta_relevant | insistence | -0.012 | [-0.019, -0.006] | [-0.022, -0.003] | 0.00013 | 0.011 | 0.016 | [-0.012, -0.012] | 60 / 0 |
| E2_delta_acc_supplied | insistence | -0.024 | [-0.037, -0.012] | [-0.036, -0.013] | 0.00025 (0.00075) | 0.00069 (0.0027) | 0.00098 (0.0039) | [-0.027, -0.017] | 60 / 0 |
| E3_delivery_effect | insistence | -0.018 | [-0.030, -0.005] | [-0.027, -0.009] | 0.0064 (0.013) | 0.0013 (0.0039) | 0.0029 (0.0088) | [-0.021, -0.010] | 60 / 0 |
| E4_moderation | insistence | +0.025 ⚑ | [+0.004, +0.046] | [-0.000, +0.051] | 0.019 (0.019) | 0.052 (0.052) | 0.062 (0.062) | [+0.010, +0.032] | 60 / 0 |
| S2_delta_acc_none | insistence | +0.151 | [+0.128, +0.173] | [+0.120, +0.182] | 0 | 4.1e-07 | 0.00049 | [+0.151, +0.151] | 60 / 0 |
| E1_delta_attempt | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 60 / 0 |
| E1b_delta_relevant | authority | -0.001 | [-0.004, +0.002] | [-0.004, +0.002] | 0.57 | 0.59 | 1 | [-0.001, -0.001] | 60 / 0 |
| E2_delta_acc_supplied | authority | +0.002 | [-0.005, +0.008] | [-0.006, +0.010] | 0.6 (1) | 0.66 (1) | 0.81 (1) | [-0.004, +0.009] | 60 / 0 |
| E3_delivery_effect | authority | +0.003 | [-0.005, +0.010] | [-0.007, +0.012] | 0.5 (1) | 0.57 (1) | 0.7 (1) | [-0.003, +0.010] | 60 / 0 |
| E4_moderation | authority | -0.012 | [-0.026, +0.003] | [-0.029, +0.006] | 0.11 (0.44) | 0.17 (0.66) | 0.25 (1) | [-0.033, -0.007] | 60 / 0 |
| S2_delta_acc_none | authority | +0.011 | [-0.005, +0.026] | [-0.005, +0.027] | 0.17 | 0.17 | 0.2 | [+0.011, +0.011] | 60 / 0 |

## gpt-oss-120b

Status {'ok': 10800}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 5400}, 'stale': {'rate': 1.0, 'n': 5400}}. Neutral optional attempt rate {'rate': 0.99, 'n': 1200}. Neutral supplied adoption {'rate': 0.9991652754590985, 'n': 1198}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.100 | [-0.125, -0.075] | [-0.151, -0.049] | 5e-11 (2e-10) | 0.0012 (0.0047) | 0.00049 (0.002) | [-0.100, -0.100] | 60 / 0 |
| E1b_delta_relevant | insistence | -0.100 | [-0.125, -0.075] | [-0.151, -0.049] | 5e-11 | 0.0012 | 0.00049 | [-0.100, -0.100] | 60 / 0 |
| E2_delta_acc_supplied | insistence | -0.004 | [-0.008, +0.000] | [-0.011, +0.003] | 0.058 (0.058) | 0.21 (0.21) | 0.38 (0.38) | [-0.007, -0.002] | 60 / 0 |
| E3_delivery_effect | insistence | +0.045 | [+0.024, +0.066] | [+0.013, +0.077] | 5.4e-05 (0.00016) | 0.011 (0.022) | 0.0059 (0.018) | [+0.042, +0.047] | 60 / 0 |
| E4_moderation | insistence | -0.047 | [-0.077, -0.017] | [-0.077, -0.016] | 0.0028 (0.0055) | 0.0067 (0.02) | 0.0088 (0.018) | [-0.050, -0.042] | 60 / 0 |
| S2_delta_acc_none | insistence | +0.023 | [-0.001, +0.046] | [-0.008, +0.053] | 0.064 | 0.13 | 0.15 | [+0.023, +0.024] | 60 / 0 |
| E1_delta_attempt | authority | -0.009 | [-0.020, +0.002] | [-0.026, +0.007] | 0.11 (0.44) | 0.25 (0.74) | 0.38 (1) | [-0.009, -0.009] | 60 / 0 |
| E1b_delta_relevant | authority | -0.009 | [-0.020, +0.002] | [-0.026, +0.007] | 0.11 | 0.25 | 0.38 | [-0.009, -0.009] | 60 / 0 |
| E2_delta_acc_supplied | authority | -0.001 | [-0.004, +0.002] | [-0.004, +0.002] | 0.57 (1) | 0.58 (1) | 1 (1) | [-0.002, +0.001] | 60 / 0 |
| E3_delivery_effect | authority | +0.001 | [-0.009, +0.010] | [-0.008, +0.010] | 0.86 (1) | 0.85 (1) | 1 (1) | [-0.000, +0.002] | 60 / 0 |
| E4_moderation | authority | +0.015 | [-0.005, +0.035] | [-0.003, +0.033] | 0.13 (0.44) | 0.1 (0.4) | 0.19 (0.75) | [+0.013, +0.018] | 60 / 0 |
| S2_delta_acc_none | authority | -0.028 ⚑ | [-0.051, -0.005] | [-0.069, +0.012] | 0.017 | 0.15 | 0.16 | [-0.028, -0.027] | 60 / 0 |

## kimi-k2-0905

Status {'ok': 10800}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 5400}, 'stale': {'rate': 1.0, 'n': 5400}}. Neutral optional attempt rate {'rate': 0.1675, 'n': 1200}. Neutral supplied adoption {'rate': 1.0, 'n': 1200}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.058 | [-0.087, -0.028] | [-0.103, -0.012] | 0.00024 (0.00095) | 0.018 (0.071) | 0.02 (0.08) | [-0.058, -0.058] | 60 / 0 |
| E1b_delta_relevant | insistence | -0.058 | [-0.087, -0.028] | [-0.103, -0.012] | 0.00024 | 0.018 | 0.02 | [-0.058, -0.058] | 60 / 0 |
| E2_delta_acc_supplied | insistence | -0.004 ⚑ | [-0.008, -0.001] | [-0.009, +0.001] | 0.024 (0.048) | 0.087 (0.19) | 0.25 (0.5) | [-0.004, -0.004] | 60 / 0 |
| E3_delivery_effect | insistence | +0.051 ⚑ | [+0.015, +0.087] | [-0.004, +0.105] | 0.0068 (0.02) | 0.065 (0.19) | 0.064 (0.19) | [+0.051, +0.051] | 60 / 0 |
| E4_moderation | insistence | +0.015 | [-0.045, +0.075] | [-0.061, +0.091] | 0.62 (0.62) | 0.67 (0.67) | 0.71 (0.71) | [+0.015, +0.015] | 60 / 0 |
| S2_delta_acc_none | insistence | -0.037 ⚑ | [-0.068, -0.007] | [-0.081, +0.006] | 0.015 | 0.084 | 0.089 | [-0.037, -0.037] | 60 / 0 |
| E1_delta_attempt | authority | -0.018 | [-0.050, +0.013] | [-0.054, +0.018] | 0.25 (0.49) | 0.28 (0.67) | 0.33 (0.98) | [-0.018, -0.018] | 60 / 0 |
| E1b_delta_relevant | authority | -0.018 | [-0.050, +0.013] | [-0.054, +0.018] | 0.25 | 0.28 | 0.33 | [-0.018, -0.018] | 60 / 0 |
| E2_delta_acc_supplied | authority | -0.002 | [-0.004, +0.001] | [-0.004, +0.001] | 0.16 (0.48) | 0.17 (0.67) | 0.5 (1) | [-0.002, -0.002] | 60 / 0 |
| E3_delivery_effect | authority | +0.028 | [-0.006, +0.063] | [-0.016, +0.073] | 0.11 (0.43) | 0.19 (0.67) | 0.22 (0.89) | [+0.028, +0.028] | 60 / 0 |
| E4_moderation | authority | +0.017 | [-0.046, +0.079] | [-0.049, +0.082] | 0.6 (0.6) | 0.59 (0.67) | 0.62 (1) | [+0.017, +0.017] | 60 / 0 |
| S2_delta_acc_none | authority | -0.067 | [-0.094, -0.040] | [-0.113, -0.020] | 7.1e-06 | 0.0093 | 0.015 | [-0.067, -0.067] | 60 / 0 |

## qwen3-235b-a22b-2507

Status {'ok': 10800}. Turn-1 eligibility {'current': {'rate': 1.0, 'n': 5400}, 'stale': {'rate': 1.0, 'n': 5400}}. Neutral optional attempt rate {'rate': 0.7975, 'n': 1200}. Neutral supplied adoption {'rate': 1.0, 'n': 1200}. Truncated 0.

| contrast | pressure | estimate | 95% CI items t (provisional primary) | 95% CI families CR1 (sensitivity) | t-test p (Holm, primary) | p fam CR1 (Holm) | p fam flip (Holm) | assigned-denominator bounds | items used / dropped |
|---|---|---|---|---|---|---|---|---|---|
| E1_delta_attempt | insistence | -0.497 | [-0.523, -0.471] | [-0.540, -0.454] | 0 (0) | 3.9e-11 (1.5e-10) | 0.00049 (0.002) | [-0.497, -0.497] | 60 / 0 |
| E1b_delta_relevant | insistence | -0.497 | [-0.523, -0.471] | [-0.540, -0.454] | 0 | 3.9e-11 | 0.00049 | [-0.497, -0.497] | 60 / 0 |
| E2_delta_acc_supplied | insistence | -0.002 | [-0.004, +0.001] | [-0.005, +0.002] | 0.16 (0.16) | 0.35 (0.35) | 1 (1) | [-0.002, -0.002] | 60 / 0 |
| E3_delivery_effect | insistence | +0.256 | [+0.234, +0.278] | [+0.228, +0.284] | 0 (0) | 5.3e-10 (1.6e-09) | 0.00049 (0.002) | [+0.256, +0.256] | 60 / 0 |
| E4_moderation | insistence | -0.405 | [-0.455, -0.355] | [-0.474, -0.336] | 0 (0) | 5.5e-08 (1.1e-07) | 0.00049 (0.002) | [-0.405, -0.405] | 60 / 0 |
| S2_delta_acc_none | insistence | +0.079 | [+0.044, +0.114] | [+0.027, +0.132] | 3e-05 | 0.0069 | 0.002 | [+0.079, +0.079] | 60 / 0 |
| E1_delta_attempt | authority | +0.042 | [+0.015, +0.070] | [+0.003, +0.082] | 0.0027 (0.008) | 0.036 (0.11) | 0.043 (0.13) | [+0.042, +0.042] | 60 / 0 |
| E1b_delta_relevant | authority | +0.042 | [+0.015, +0.070] | [+0.003, +0.082] | 0.0027 | 0.036 | 0.043 | [+0.042, +0.042] | 60 / 0 |
| E2_delta_acc_supplied | authority | +0.000 | [+0.000, +0.000] (degenerate: zero spread, not precision) | [+0.000, +0.000] | 1 (1) | 1 (1) | 1 (1) | [+0.000, +0.000] | 60 / 0 |
| E3_delivery_effect | authority | -0.001 | [-0.021, +0.019] | [-0.030, +0.029] | 0.93 (1) | 0.95 (1) | 1 (1) | [-0.001, -0.001] | 60 / 0 |
| E4_moderation | authority | +0.082 | [+0.039, +0.124] | [+0.037, +0.127] | 0.00029 (0.0012) | 0.0022 (0.0086) | 0.0098 (0.039) | [+0.082, +0.082] | 60 / 0 |
| S2_delta_acc_none | authority | -0.004 | [-0.020, +0.012] | [-0.025, +0.017] | 0.6 | 0.67 | 0.73 | [-0.004, -0.004] | 60 / 0 |

## Batches (base vs extension; read before the pooled estimates)

Execution windows: {'runs/p1_dev_eval_v2': ['2026-11-16 15:46:07 IST', '2026-11-16 15:59:41 IST'], 'runs/p1_ext_v2': ['2026-11-16 15:46:32 IST', '2026-11-16 16:15:23 IST']}

| pressure | model | estimand | batch 1 | batch 2 | difference (2 − 1) | Welch 95% CI |
|---|---|---|---|---|---|---|
| insistence | deepseek-v3.2 | E1_delta_attempt | -0.010 | -0.015 | -0.005 | [-0.018, +0.008] |
| insistence | deepseek-v3.2 | E1b_delta_relevant | -0.010 | -0.014 | -0.003 | [-0.016, +0.009] |
| insistence | deepseek-v3.2 | E2_delta_acc_supplied | -0.025 | -0.024 | +0.001 | [-0.023, +0.025] |
| insistence | deepseek-v3.2 | E3_delivery_effect | -0.019 | -0.017 | +0.002 | [-0.022, +0.026] |
| insistence | deepseek-v3.2 | E4_moderation | +0.037 | +0.017 | -0.020 | [-0.062, +0.022] |
| insistence | deepseek-v3.2 | S2_delta_acc_none | +0.158 | +0.146 | -0.012 | [-0.059, +0.034] |
| insistence | gpt-oss-120b | E1_delta_attempt | -0.110 | -0.093 | +0.017 | [-0.029, +0.064] |
| insistence | gpt-oss-120b | E1b_delta_relevant | -0.110 | -0.093 | +0.017 | [-0.029, +0.064] |
| insistence | gpt-oss-120b | E2_delta_acc_supplied | -0.006 | -0.003 | +0.003 | [-0.005, +0.012] |
| insistence | gpt-oss-120b | E3_delivery_effect | +0.054 | +0.039 | -0.015 | [-0.057, +0.027] |
| insistence | gpt-oss-120b | E4_moderation | -0.075 | -0.028 | +0.047 | [-0.016, +0.110] |
| insistence | gpt-oss-120b | S2_delta_acc_none | +0.015 | +0.028 | +0.013 | [-0.036, +0.062] |
| insistence | kimi-k2-0905 | E1_delta_attempt | -0.069 | -0.050 | +0.019 | [-0.043, +0.081] |
| insistence | kimi-k2-0905 | E1b_delta_relevant | -0.069 | -0.050 | +0.019 | [-0.043, +0.081] |
| insistence | kimi-k2-0905 | E2_delta_acc_supplied | -0.002 | -0.006 | -0.003 | [-0.010, +0.003] |
| insistence | kimi-k2-0905 | E3_delivery_effect | +0.079 | +0.032 | -0.047 | [-0.122, +0.028] |
| insistence | kimi-k2-0905 | E4_moderation | +0.075 | -0.025 | -0.100 | [-0.227, +0.027] |
| insistence | kimi-k2-0905 | S2_delta_acc_none | -0.048 | -0.031 | +0.017 | [-0.043, +0.078] |
| insistence | qwen3-235b-a22b-2507 | E1_delta_attempt | -0.500 | -0.494 | +0.006 | [-0.050, +0.061] |
| insistence | qwen3-235b-a22b-2507 | E1b_delta_relevant | -0.500 | -0.494 | +0.006 | [-0.050, +0.061] |
| insistence | qwen3-235b-a22b-2507 | E2_delta_acc_supplied | -0.004 | +0.000 | +0.004 | [-0.002, +0.010] |
| insistence | qwen3-235b-a22b-2507 | E3_delivery_effect | +0.269 | +0.247 | -0.022 | [-0.069, +0.026] |
| insistence | qwen3-235b-a22b-2507 | E4_moderation | -0.429 | -0.389 | +0.040 | [-0.065, +0.146] |
| insistence | qwen3-235b-a22b-2507 | S2_delta_acc_none | +0.077 | +0.081 | +0.003 | [-0.072, +0.079] |
| authority | deepseek-v3.2 | E1_delta_attempt | +0.000 | +0.000 | +0.000 | – |
| authority | deepseek-v3.2 | E1b_delta_relevant | -0.004 | +0.001 | +0.006 | [-0.001, +0.012] |
| authority | deepseek-v3.2 | E2_delta_acc_supplied | +0.000 | +0.003 | +0.003 | [-0.010, +0.015] |
| authority | deepseek-v3.2 | E3_delivery_effect | +0.004 | +0.001 | -0.003 | [-0.018, +0.012] |
| authority | deepseek-v3.2 | E4_moderation | -0.008 | -0.014 | -0.006 | [-0.036, +0.025] |
| authority | deepseek-v3.2 | S2_delta_acc_none | +0.021 | +0.004 | -0.017 | [-0.050, +0.017] |
| authority | gpt-oss-120b | E1_delta_attempt | -0.019 | -0.003 | +0.016 | [-0.006, +0.038] |
| authority | gpt-oss-120b | E1b_delta_relevant | -0.019 | -0.003 | +0.016 | [-0.006, +0.038] |
| authority | gpt-oss-120b | E2_delta_acc_supplied | +0.000 | -0.001 | -0.001 | [-0.006, +0.004] |
| authority | gpt-oss-120b | E3_delivery_effect | +0.008 | -0.004 | -0.013 | [-0.030, +0.005] |
| authority | gpt-oss-120b | E4_moderation | +0.008 | +0.019 | +0.011 | [-0.024, +0.046] |
| authority | gpt-oss-120b | S2_delta_acc_none | -0.073 | +0.001 | +0.074 | [+0.027, +0.121] |
| authority | kimi-k2-0905 | E1_delta_attempt | -0.004 | -0.028 | -0.024 | [-0.088, +0.041] |
| authority | kimi-k2-0905 | E1b_delta_relevant | -0.004 | -0.028 | -0.024 | [-0.088, +0.041] |
| authority | kimi-k2-0905 | E2_delta_acc_supplied | -0.002 | -0.001 | +0.001 | [-0.004, +0.006] |
| authority | kimi-k2-0905 | E3_delivery_effect | +0.025 | +0.031 | +0.006 | [-0.069, +0.081] |
| authority | kimi-k2-0905 | E4_moderation | +0.000 | +0.028 | +0.028 | [-0.110, +0.166] |
| authority | kimi-k2-0905 | S2_delta_acc_none | -0.073 | -0.062 | +0.010 | [-0.048, +0.069] |
| authority | qwen3-235b-a22b-2507 | E1_delta_attempt | +0.035 | +0.047 | +0.012 | [-0.042, +0.066] |
| authority | qwen3-235b-a22b-2507 | E1b_delta_relevant | +0.035 | +0.047 | +0.012 | [-0.042, +0.066] |
| authority | qwen3-235b-a22b-2507 | E2_delta_acc_supplied | +0.000 | +0.000 | +0.000 | – |
| authority | qwen3-235b-a22b-2507 | E3_delivery_effect | +0.010 | -0.008 | -0.019 | [-0.059, +0.021] |
| authority | qwen3-235b-a22b-2507 | E4_moderation | +0.046 | +0.106 | +0.060 | [-0.025, +0.145] |
| authority | qwen3-235b-a22b-2507 | S2_delta_acc_none | -0.002 | -0.006 | -0.003 | [-0.036, +0.029] |
