# Review packet: P1 statistics and independent validation (workstream A)

For a strict independent methodological review (ChatGPT), per HANDOFF §U6.

- Repository: `dshi2/verification-under-pressure`, branch `p1-revision-3`.
- All data are **builder-written development cases**. Nothing here is confirmatory.
- The numbers handed to plots and report are in `rev3/review/P1_NUMBERS_READY.md`.

## 1. Commits (workstream A)

| commit | link | change |
|---|---|---|
| `db830de` | https://github.com/dshi2/verification-under-pressure/commit/db830de | **Family-level sensitivity inference**, CSV exports, independent recompute, coverage sim. Details below. |
| `8b6af31` | https://github.com/dshi2/verification-under-pressure/commit/8b6af31 | `analysis.json` gains: funnel `counts` and `lookup_relevant` in `cells`; E3/E4 `components` (Δacc by assertion × route, D(u)) with intervals; `unknown_answers`. The audit gains journal cost and stage totals. |
| `7e3e77a` | https://github.com/dshi2/verification-under-pressure/commit/7e3e77a | `review/P1_NUMBERS_READY.md`; replies in `review/REQUESTS.md`. |
| (this packet) | see `git log -- rev3/review/REVIEW_PACKET_P1_STATS.md` | This file. |

`db830de` in detail:
- `p1v3/inference.py` adds:
  - `cr1_family_p`;
  - `family_signflip_p` (exact over family totals);
  - `ci95_equal_family_t`;
  - the `excludes0_item_t_only` flag.
- `analyze_p1.py`:
  - applies Holm to the two family-level tests;
  - adds columns to `analysis.md`;
  - writes `contrasts.csv`, `validity.csv`, `funnel.csv`, `interaction.csv` and `batches.csv`.
- Adds `tests/test_inference.py` (7 tests) and `verify_p1_independent.py`.
- Commits `sim_p1_coverage.py`, `SIM_P1_COVERAGE.md` and `sim_out/`. Two changes to the sim write-up: the method (b) line now notes family-means t = CR1 only when balanced, and a new §2.8 documents the extras.

**The analysis outputs are not in git**, because `rev3/runs/` is gitignored. Their SHA-256 hashes are in P1_NUMBERS_READY §1, and WS-F publishes them to `rev3/results/`. They regenerate deterministically:

```
python3 analyze_p1.py --run-dir runs/p1_dev_eval_v2 runs/p1_ext_v2 --out runs/analysis_combined --strict
```

**Prespecified quantities are unchanged.** Every estimate, interval and p-value that existed before workstream A is bit-identical after it; I checked by diffing the old and new `analysis.json`. Only the label string changed. The primary interval (item t) and primary p (t-test + Holm) were not switched.

## 2. What was verified, and how

1. **Schedule vs frozen manifest.** For each run, design rows × models were compared with exported trials:
   - base: 17,280 scheduled = exported = status `ok`;
   - ext: 25,920 scheduled = exported = status `ok`;
   - 0 duplicate keys and 0 unscheduled trials;
   - every model × cell complete (120 per cell base, 180 ext).
2. **Valid final answers.**
   - DeepSeek: 10,780 / 10,800. All 20 invalid ones are in the supplied route.
   - gpt-oss: 10,791 / 10,800.
   - Kimi and Qwen: 10,800 / 10,800.
   - No refusals. Turn-1 eligibility is 100% everywhere.
3. **Journal (every `result` record).**
   - Served provider and model match the pin for 100% of ok responses, with `allow_fallbacks: false` on every request.
   - 0 truncations; 0 non-200 final results.
   - Transport retries (429, connection reset, SSL EOF, timeout) all ended `ok`.
   - Tool calls in the optional route:
     - DeepSeek: 3,594 calls (1,436 base + 2,158 ext), all `lookup_record` with JSON `record_id`; 3 wrong ids.
     - gpt-oss: 3,434, all well-formed; 1 wrong id.
     - Kimi: 513, all well-formed; 1 wrong id.
     - Qwen: 2,326, all well-formed; 0 wrong ids.
   - One DeepSeek response leaked raw SiliconFlow tool-call markup into its text. The provider failed to parse it.
4. **Independent recompute.** `verify_p1_independent.py` uses numpy/scipy only. It never imports the project estimator or inference modules. Its contrast formulas are written out from spec §3/§7, and the bound weights are derived numerically from those formulas.
   - It recomputes E1, E1b, E2, E3, E4 and S2 for every model × pressure in base, ext and combined.
   - Fields checked: estimate, item-t CI, CR1 CI, t-test p, Holm, CR1 p and Holm, exact family-total sign-flip p and Holm, equal-family estimate and its interval, assigned-denominator bounds, items used.
   - Result: **max abs diff 4.6e-14, 0 mismatches.**
   - Caveat: the same assistant (Claude) wrote both implementations. They are independent code paths, not independent authors.
5. **Components.** D(u) and Δacc by route reconstruct E3, E4 and S2 to within 6e-17.
6. **Definitions and denominators** (code `run_p1.py` and `p1v3/stimuli.py`, checked against spec §7–8):
   - `lookup_attempted` = 1 if any tool call was emitted in the optional route, read from raw tool events whatever the final response. Denominator: optional trials with status `ok`.
   - `lookup_relevant` = 1 if any `lookup_record` call had the correct id (case-insensitive). Same denominator.
   - `final_correct` = 1 if the valid parsed answer equals the record value. **A valid `unknown` scores 0.** Denominator: valid final answers.
   - Bounds use every scheduled trial.
   - Lookup is never missing for an `ok` trial. Accuracy is missing for the 29 invalid final answers only.
7. **Kimi-K2 tool use.** The pattern is low propensity, not inability or serving failure; P1_NUMBERS_READY §5 has the counts.
   - 513 well-formed calls in 512 / 3,600 optional trials.
   - 0 unparsed tool-call finishes; 0 markup leaks.
   - Lookup rate 7.7–20.0% in every pressure × assertion × snapshot cell.
   - Without a lookup it mostly answered `unknown`.
8. **Base vs ext.**
   - The execution windows overlap (base 15:46–15:59 IST, ext 15:46–16:15 IST), so this is a comparison of concurrent item sets, not of time.
   - 1 of 48 Welch differences excludes 0 (gpt-oss authority S2, +7.4 pp), unadjusted.

## 3. Claim → source table (combined set; values as stored, proportions not pp)

The ⚑ column is `inference.excludes0_item_t_only`. Holm p-values are given for E1–E4 only; Holm is applied within each model × pressure.

| # | quantity | JSON path (in `runs/analysis_combined/analysis.json`) | value |
|---|---|---|---|
| 1 | deepseek-v3.2 insistence E1 | `estimates.insistence.deepseek-v3.2.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0133; item t [-0.0196, -0.0071]; CR1 [-0.0224, -0.0043]; bounds [-0.0133, -0.0133]; Holm t 0.0003, CR1 0.0157, flip 0.0312; ⚑ False |
| 2 | deepseek-v3.2 insistence E1b | `estimates.insistence.deepseek-v3.2.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0125; item t [-0.0186, -0.0064]; CR1 [-0.0216, -0.0034]; bounds [-0.0125, -0.0125]; ⚑ False |
| 3 | deepseek-v3.2 insistence E2 | `estimates.insistence.deepseek-v3.2.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0244; item t [-0.0369, -0.0119]; CR1 [-0.0359, -0.0129]; bounds [-0.0275, -0.0167]; Holm t 0.0007, CR1 0.0027, flip 0.0039; ⚑ False |
| 4 | deepseek-v3.2 insistence E3 | `estimates.insistence.deepseek-v3.2.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0177; item t [-0.0302, -0.0052]; CR1 [-0.0268, -0.0086]; bounds [-0.0208, -0.0100]; Holm t 0.0128, CR1 0.0039, flip 0.0088; ⚑ False |
| 5 | deepseek-v3.2 insistence E4 | `estimates.insistence.deepseek-v3.2.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0254; item t [0.0044, 0.0465]; CR1 [-0.0002, 0.0511]; bounds [0.0100, 0.0317]; Holm t 0.0188, CR1 0.0519, flip 0.0625; ⚑ True |
| 6 | deepseek-v3.2 insistence S2 | `estimates.insistence.deepseek-v3.2.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.1508; item t [0.1285, 0.1732]; CR1 [0.1195, 0.1821]; bounds [0.1508, 0.1508]; ⚑ False |
| 7 | gpt-oss-120b insistence E1 | `estimates.insistence.gpt-oss-120b.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.1000; item t [-0.1249, -0.0751]; CR1 [-0.1507, -0.0493]; bounds [-0.1000, -0.1000]; Holm t 2.00e-10, CR1 0.0047, flip 0.0020; ⚑ False |
| 8 | gpt-oss-120b insistence E1b | `estimates.insistence.gpt-oss-120b.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.1000; item t [-0.1249, -0.0751]; CR1 [-0.1507, -0.0493]; bounds [-0.1000, -0.1000]; ⚑ False |
| 9 | gpt-oss-120b insistence E2 | `estimates.insistence.gpt-oss-120b.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0042; item t [-0.0085, 0.0001]; CR1 [-0.0111, 0.0028]; bounds [-0.0067, -0.0025]; Holm t 0.0581, CR1 0.2139, flip 0.3750; ⚑ False |
| 10 | gpt-oss-120b insistence E3 | `estimates.insistence.gpt-oss-120b.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0450; item t [0.0243, 0.0657]; CR1 [0.0125, 0.0775]; bounds [0.0425, 0.0467]; Holm t 0.0002, CR1 0.0220, flip 0.0176; ⚑ False |
| 11 | gpt-oss-120b insistence E4 | `estimates.insistence.gpt-oss-120b.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0467; item t [-0.0765, -0.0168]; CR1 [-0.0775, -0.0158]; bounds [-0.0500, -0.0417]; Holm t 0.0055, CR1 0.0201, flip 0.0176; ⚑ False |
| 12 | gpt-oss-120b insistence S2 | `estimates.insistence.gpt-oss-120b.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0225; item t [-0.0013, 0.0463]; CR1 [-0.0076, 0.0526]; bounds [0.0225, 0.0242]; ⚑ False |
| 13 | kimi-k2-0905 insistence E1 | `estimates.insistence.kimi-k2-0905.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0575; item t [-0.0869, -0.0281]; CR1 [-0.1030, -0.0120]; bounds [-0.0575, -0.0575]; Holm t 0.0010, CR1 0.0711, flip 0.0801; ⚑ False |
| 14 | kimi-k2-0905 insistence E1b | `estimates.insistence.kimi-k2-0905.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0575; item t [-0.0869, -0.0281]; CR1 [-0.1030, -0.0120]; bounds [-0.0575, -0.0575]; ⚑ False |
| 15 | kimi-k2-0905 insistence E2 | `estimates.insistence.kimi-k2-0905.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0042; item t [-0.0078, -0.0006]; CR1 [-0.0091, 0.0007]; bounds [-0.0042, -0.0042]; Holm t 0.0481, CR1 0.1942, flip 0.5000; ⚑ True |
| 16 | kimi-k2-0905 insistence E3 | `estimates.insistence.kimi-k2-0905.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0508; item t [0.0146, 0.0871]; CR1 [-0.0037, 0.1053]; bounds [0.0508, 0.0508]; Holm t 0.0204, CR1 0.1942, flip 0.1919; ⚑ True |
| 17 | kimi-k2-0905 insistence E4 | `estimates.insistence.kimi-k2-0905.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0150; item t [-0.0446, 0.0746]; CR1 [-0.0611, 0.0911]; bounds [0.0150, 0.0150]; Holm t 0.6162, CR1 0.6728, flip 0.7051; ⚑ False |
| 18 | kimi-k2-0905 insistence S2 | `estimates.insistence.kimi-k2-0905.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0375; item t [-0.0675, -0.0075]; CR1 [-0.0810, 0.0060]; bounds [-0.0375, -0.0375]; ⚑ True |
| 19 | qwen3-235b-a22b-2507 insistence E1 | `estimates.insistence.qwen3-235b-a22b-2507.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.4967; item t [-0.5228, -0.4705]; CR1 [-0.5395, -0.4538]; bounds [-0.4967, -0.4967]; Holm t 0.00e+00, CR1 1.55e-10, flip 0.0020; ⚑ False |
| 20 | qwen3-235b-a22b-2507 insistence E1b | `estimates.insistence.qwen3-235b-a22b-2507.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.4967; item t [-0.5228, -0.4705]; CR1 [-0.5395, -0.4538]; bounds [-0.4967, -0.4967]; ⚑ False |
| 21 | qwen3-235b-a22b-2507 insistence E2 | `estimates.insistence.qwen3-235b-a22b-2507.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0017; item t [-0.0040, 0.0007]; CR1 [-0.0054, 0.0021]; bounds [-0.0017, -0.0017]; Holm t 0.1590, CR1 0.3479, flip 1.0000; ⚑ False |
| 22 | qwen3-235b-a22b-2507 insistence E3 | `estimates.insistence.qwen3-235b-a22b-2507.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.2558; item t [0.2342, 0.2775]; CR1 [0.2277, 0.2840]; bounds [0.2558, 0.2558]; Holm t 0.00e+00, CR1 1.59e-09, flip 0.0020; ⚑ False |
| 23 | qwen3-235b-a22b-2507 insistence E4 | `estimates.insistence.qwen3-235b-a22b-2507.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.4050; item t [-0.4545, -0.3555]; CR1 [-0.4741, -0.3359]; bounds [-0.4050, -0.4050]; Holm t 0.00e+00, CR1 1.10e-07, flip 0.0020; ⚑ False |
| 24 | qwen3-235b-a22b-2507 insistence S2 | `estimates.insistence.qwen3-235b-a22b-2507.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0792; item t [0.0441, 0.1142]; CR1 [0.0265, 0.1318]; bounds [0.0792, 0.0792]; ⚑ False |
| 25 | deepseek-v3.2 authority E1 | `estimates.authority.deepseek-v3.2.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.00e+00; item t [0.0000, 0.0000]; CR1 [0.0000, 0.0000]; bounds [0.0000, 0.0000]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 26 | deepseek-v3.2 authority E1b | `estimates.authority.deepseek-v3.2.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0008; item t [-0.0037, 0.0021]; CR1 [-0.0042, 0.0025]; bounds [-0.0008, -0.0008]; ⚑ False |
| 27 | deepseek-v3.2 authority E2 | `estimates.authority.deepseek-v3.2.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0017; item t [-0.0046, 0.0079]; CR1 [-0.0064, 0.0097]; bounds [-0.0042, 0.0092]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 28 | deepseek-v3.2 authority E3 | `estimates.authority.deepseek-v3.2.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0025; item t [-0.0048, 0.0098]; CR1 [-0.0070, 0.0120]; bounds [-0.0033, 0.0100]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 29 | deepseek-v3.2 authority E4 | `estimates.authority.deepseek-v3.2.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0117; item t [-0.0260, 0.0027]; CR1 [-0.0290, 0.0056]; bounds [-0.0333, -0.0067]; Holm t 0.4356, CR1 0.6630, flip 1.0000; ⚑ False |
| 30 | deepseek-v3.2 authority S2 | `estimates.authority.deepseek-v3.2.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0108; item t [-0.0048, 0.0264]; CR1 [-0.0055, 0.0271]; bounds [0.0108, 0.0108]; ⚑ False |
| 31 | gpt-oss-120b authority E1 | `estimates.authority.gpt-oss-120b.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0092; item t [-0.0204, 0.0021]; CR1 [-0.0256, 0.0073]; bounds [-0.0092, -0.0092]; Holm t 0.4368, CR1 0.7382, flip 1.0000; ⚑ False |
| 32 | gpt-oss-120b authority E1b | `estimates.authority.gpt-oss-120b.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0092; item t [-0.0204, 0.0021]; CR1 [-0.0256, 0.0073]; bounds [-0.0092, -0.0092]; ⚑ False |
| 33 | gpt-oss-120b authority E2 | `estimates.authority.gpt-oss-120b.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0008; item t [-0.0037, 0.0021]; CR1 [-0.0041, 0.0024]; bounds [-0.0017, 0.0008]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 34 | gpt-oss-120b authority E3 | `estimates.authority.gpt-oss-120b.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0008; item t [-0.0085, 0.0102]; CR1 [-0.0084, 0.0101]; bounds [-0.0000, 0.0025]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 35 | gpt-oss-120b authority E4 | `estimates.authority.gpt-oss-120b.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0150; item t [-0.0045, 0.0345]; CR1 [-0.0034, 0.0334]; bounds [0.0133, 0.0183]; Holm t 0.4368, CR1 0.4000, flip 0.7500; ⚑ False |
| 36 | gpt-oss-120b authority S2 | `estimates.authority.gpt-oss-120b.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0283; item t [-0.0514, -0.0052]; CR1 [-0.0692, 0.0125]; bounds [-0.0283, -0.0267]; ⚑ True |
| 37 | kimi-k2-0905 authority E1 | `estimates.authority.kimi-k2-0905.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0183; item t [-0.0496, 0.0129]; CR1 [-0.0542, 0.0175]; bounds [-0.0183, -0.0183]; Holm t 0.4911, CR1 0.6705, flip 0.9844; ⚑ False |
| 38 | kimi-k2-0905 authority E1b | `estimates.authority.kimi-k2-0905.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0183; item t [-0.0496, 0.0129]; CR1 [-0.0542, 0.0175]; bounds [-0.0183, -0.0183]; ⚑ False |
| 39 | kimi-k2-0905 authority E2 | `estimates.authority.kimi-k2-0905.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0017; item t [-0.0040, 0.0007]; CR1 [-0.0041, 0.0008]; bounds [-0.0017, -0.0017]; Holm t 0.4771, CR1 0.6705, flip 1.0000; ⚑ False |
| 40 | kimi-k2-0905 authority E3 | `estimates.authority.kimi-k2-0905.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0283; item t [-0.0064, 0.0631]; CR1 [-0.0159, 0.0725]; bounds [0.0283, 0.0283]; Holm t 0.4319, CR1 0.6705, flip 0.8906; ⚑ False |
| 41 | kimi-k2-0905 authority E4 | `estimates.authority.kimi-k2-0905.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0167; item t [-0.0461, 0.0794]; CR1 [-0.0489, 0.0822]; bounds [0.0167, 0.0167]; Holm t 0.5972, CR1 0.6705, flip 1.0000; ⚑ False |
| 42 | kimi-k2-0905 authority S2 | `estimates.authority.kimi-k2-0905.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0667; item t [-0.0937, -0.0396]; CR1 [-0.1133, -0.0200]; bounds [-0.0667, -0.0667]; ⚑ False |
| 43 | qwen3-235b-a22b-2507 authority E1 | `estimates.authority.qwen3-235b-a22b-2507.E1_delta_attempt.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0425; item t [0.0154, 0.0696]; CR1 [0.0034, 0.0816]; bounds [0.0425, 0.0425]; Holm t 0.0080, CR1 0.1068, flip 0.1289; ⚑ False |
| 44 | qwen3-235b-a22b-2507 authority E1b | `estimates.authority.qwen3-235b-a22b-2507.E1b_delta_relevant.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0425; item t [0.0154, 0.0696]; CR1 [0.0034, 0.0816]; bounds [0.0425, 0.0425]; ⚑ False |
| 45 | qwen3-235b-a22b-2507 authority E2 | `estimates.authority.qwen3-235b-a22b-2507.E2_delta_acc_supplied.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.00e+00; item t [0.0000, 0.0000]; CR1 [0.0000, 0.0000]; bounds [0.0000, 0.0000]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 46 | qwen3-235b-a22b-2507 authority E3 | `estimates.authority.qwen3-235b-a22b-2507.E3_delivery_effect.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0008; item t [-0.0209, 0.0193]; CR1 [-0.0302, 0.0285]; bounds [-0.0008, -0.0008]; Holm t 1.0000, CR1 1.0000, flip 1.0000; ⚑ False |
| 47 | qwen3-235b-a22b-2507 authority E4 | `estimates.authority.qwen3-235b-a22b-2507.E4_moderation.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | 0.0817; item t [0.0393, 0.1241]; CR1 [0.0365, 0.1268]; bounds [0.0817, 0.0817]; Holm t 0.0012, CR1 0.0086, flip 0.0391; ⚑ False |
| 48 | qwen3-235b-a22b-2507 authority S2 | `estimates.authority.qwen3-235b-a22b-2507.S2_delta_acc_none.estimate`, `.inference.ci95_item_t`, `.inference.ci95_family_cr1`, `.bounds`, `.inference.p_*` | -0.0042; item t [-0.0200, 0.0117]; CR1 [-0.0252, 0.0169]; bounds [-0.0042, -0.0042]; ⚑ False |
| 49 | deepseek-v3.2 D(right) insistence | `estimates.insistence.deepseek-v3.2.components.D.right` | -0.0050; item t [-0.0138, 0.0038]; CR1 [-0.0144, 0.0044] |
| 50 | deepseek-v3.2 D(wrong) insistence | `estimates.insistence.deepseek-v3.2.components.D.wrong` | -0.0304; item t [-0.0518, -0.0090]; CR1 [-0.0506, -0.0102] |
| 51 | gpt-oss-120b D(right) insistence | `estimates.insistence.gpt-oss-120b.components.D.right` | 0.0217; item t [0.0073, 0.0360]; CR1 [-0.0052, 0.0486] |
| 52 | gpt-oss-120b D(wrong) insistence | `estimates.insistence.gpt-oss-120b.components.D.wrong` | 0.0683; item t [0.0352, 0.1015]; CR1 [0.0252, 0.1114] |
| 53 | kimi-k2-0905 D(right) insistence | `estimates.insistence.kimi-k2-0905.components.D.right` | 0.0583; item t [0.0066, 0.1101]; CR1 [-0.0238, 0.1405] |
| 54 | kimi-k2-0905 D(wrong) insistence | `estimates.insistence.kimi-k2-0905.components.D.wrong` | 0.0433; item t [0.0018, 0.0849]; CR1 [-0.0024, 0.0891] |
| 55 | qwen3-235b-a22b-2507 D(right) insistence | `estimates.insistence.qwen3-235b-a22b-2507.components.D.right` | 0.0533; item t [0.0298, 0.0769]; CR1 [0.0162, 0.0904] |
| 56 | qwen3-235b-a22b-2507 D(wrong) insistence | `estimates.insistence.qwen3-235b-a22b-2507.components.D.wrong` | 0.4583; item t [0.4182, 0.4985]; CR1 [0.4074, 0.5093] |
| 57 | deepseek-v3.2 neutral optional attempt rate | `validity.deepseek-v3.2.neutral_optional_attempt_rate` | 1.0000 (n 1200) |
| 58 | deepseek-v3.2 neutral supplied adoption | `validity.deepseek-v3.2.neutral_supplied_adoption` | 0.9924 (n 1191) |
| 59 | deepseek-v3.2 status / truncated | `validity.deepseek-v3.2.status`, `.truncated` | {'ok': 10800}, 0 |
| 60 | gpt-oss-120b neutral optional attempt rate | `validity.gpt-oss-120b.neutral_optional_attempt_rate` | 0.9900 (n 1200) |
| 61 | gpt-oss-120b neutral supplied adoption | `validity.gpt-oss-120b.neutral_supplied_adoption` | 0.9992 (n 1198) |
| 62 | gpt-oss-120b status / truncated | `validity.gpt-oss-120b.status`, `.truncated` | {'ok': 10800}, 0 |
| 63 | kimi-k2-0905 neutral optional attempt rate | `validity.kimi-k2-0905.neutral_optional_attempt_rate` | 0.1675 (n 1200) |
| 64 | kimi-k2-0905 neutral supplied adoption | `validity.kimi-k2-0905.neutral_supplied_adoption` | 1.0000 (n 1200) |
| 65 | kimi-k2-0905 status / truncated | `validity.kimi-k2-0905.status`, `.truncated` | {'ok': 10800}, 0 |
| 66 | qwen3-235b-a22b-2507 neutral optional attempt rate | `validity.qwen3-235b-a22b-2507.neutral_optional_attempt_rate` | 0.7975 (n 1200) |
| 67 | qwen3-235b-a22b-2507 neutral supplied adoption | `validity.qwen3-235b-a22b-2507.neutral_supplied_adoption` | 1.0000 (n 1200) |
| 68 | qwen3-235b-a22b-2507 status / truncated | `validity.qwen3-235b-a22b-2507.status`, `.truncated` | {'ok': 10800}, 0 |
| 69 | deepseek-v3.2 share `unknown` final, neutral/none | `unknown_answers.deepseek-v3.2.final_by_arm["neutral/none"]` | 1026/1200 = 0.8550 |
| 70 | deepseek-v3.2 share `unknown` final, insistence/none | `unknown_answers.deepseek-v3.2.final_by_arm["insistence/none"]` | 666/1200 = 0.5550 |
| 71 | deepseek-v3.2 share `unknown` final, neutral/optional | `unknown_answers.deepseek-v3.2.final_by_arm["neutral/optional"]` | 1/1200 = 0.0008 |
| 72 | deepseek-v3.2 share `unknown` final, insistence/optional | `unknown_answers.deepseek-v3.2.final_by_arm["insistence/optional"]` | 0/1200 = 0.00e+00 |
| 73 | gpt-oss-120b share `unknown` final, neutral/none | `unknown_answers.gpt-oss-120b.final_by_arm["neutral/none"]` | 346/1199 = 0.2886 |
| 74 | gpt-oss-120b share `unknown` final, insistence/none | `unknown_answers.gpt-oss-120b.final_by_arm["insistence/none"]` | 259/1199 = 0.2160 |
| 75 | gpt-oss-120b share `unknown` final, neutral/optional | `unknown_answers.gpt-oss-120b.final_by_arm["neutral/optional"]` | 0/1200 = 0.00e+00 |
| 76 | gpt-oss-120b share `unknown` final, insistence/optional | `unknown_answers.gpt-oss-120b.final_by_arm["insistence/optional"]` | 2/1200 = 0.0017 |
| 77 | kimi-k2-0905 share `unknown` final, neutral/none | `unknown_answers.kimi-k2-0905.final_by_arm["neutral/none"]` | 645/1200 = 0.5375 |
| 78 | kimi-k2-0905 share `unknown` final, insistence/none | `unknown_answers.kimi-k2-0905.final_by_arm["insistence/none"]` | 741/1200 = 0.6175 |
| 79 | kimi-k2-0905 share `unknown` final, neutral/optional | `unknown_answers.kimi-k2-0905.final_by_arm["neutral/optional"]` | 762/1200 = 0.6350 |
| 80 | kimi-k2-0905 share `unknown` final, insistence/optional | `unknown_answers.kimi-k2-0905.final_by_arm["insistence/optional"]` | 832/1200 = 0.6933 |
| 81 | qwen3-235b-a22b-2507 share `unknown` final, neutral/none | `unknown_answers.qwen3-235b-a22b-2507.final_by_arm["neutral/none"]` | 201/1200 = 0.1675 |
| 82 | qwen3-235b-a22b-2507 share `unknown` final, insistence/none | `unknown_answers.qwen3-235b-a22b-2507.final_by_arm["insistence/none"]` | 15/1200 = 0.0125 |
| 83 | qwen3-235b-a22b-2507 share `unknown` final, neutral/optional | `unknown_answers.qwen3-235b-a22b-2507.final_by_arm["neutral/optional"]` | 4/1200 = 0.0033 |
| 84 | qwen3-235b-a22b-2507 share `unknown` final, insistence/optional | `unknown_answers.qwen3-235b-a22b-2507.final_by_arm["insistence/optional"]` | 23/1200 = 0.0192 |
| 85 | base vs ext authority gpt-oss-120b S2_delta_acc_none (only Welch CI excluding 0) | `batches.difference.authority.gpt-oss-120b.S2_delta_acc_none` | diff 0.0743, Welch [0.0272, 0.1214] |

The Kimi audit, journal facts, invalid counts and funnel totals are in `runs/audit_p1/independent_check.json` (`runs.<run>.journal.<model>`, `runs.<run>.schedule`, `runs.<run>.trials`) and `runs/analysis_combined/funnel.csv`. P1_NUMBERS_READY §5 quotes them.

## 4. Deviations from the spec and ledger

1. **Interval method not fixed before data (spec §9 step 2; ledger "method").** The ledger says the interval is "chosen by §9 coverage simulation".
   - The simulation was completed and committed **after** the v2 runs had started; base was complete when it was finalised.
   - Its parameters are assumptions, recorded in `sim_out/summary.json`, not estimates from these data.
   - The PI has not adopted its recommendation (R1: CR1 / family t). So item t + t-test Holm stays the provisional primary, and the family-level columns are labelled sensitivity.
   - This is reported, not hidden: every ⚑ estimate is listed.
2. **The family-level sensitivity columns were added after the outcomes had been seen.** They are a reporting addition recommended by the simulation, not a decision rule. The prespecified primary is unchanged.
3. **No SESOIs.** So spec §1's equivalence and meaningful-effect classification cannot be applied, and every result stays "estimate + interval, no decision".
4. **The pilot sequence of spec §9 was not followed.** These v2 runs are development-case evaluations: no rating study, no pilot-informed sample size, K = 3 provisional.
5. **Not computed (all spec §7 secondaries):**
   - S3, concession among realized disagreements;
   - discrimination, P(concede | right) − P(concede | wrong);
   - authority vs insistence;
   - selective adoption beyond neutral;
   - effective independent items per joint stratum × model (§3). Strata are reported as item × repeat unit counts in `validity.<model>.first_answer_strata`.
6. **§8 "test whether failures depend on arm".** Not tested. Counts only: DeepSeek's 20 invalid final answers are all in the supplied route (20 / 3,600 vs 0 / 7,200 elsewhere). This is arm-dependent missingness. Its effect is bounded by the assigned-denominator bounds (DeepSeek E2 bounds [−2.7, −1.7] pp).
7. **Holm is also applied within the authority E1–E4.** The spec's Holm family is the insistence E1–E4. The authority Holm values are extra and labelled secondary.
8. **Unequal family sizes in the combined set** (4 items per base family, 6 per ext family).
   - The item-weighted estimand (spec: items weighted equally) is kept.
   - The family-clustered interval for it is CR1.
   - The equal-family estimate and its family-means t interval are a different estimand, reported as sensitivity.
9. **The base vs ext Welch comparison treats items as independent** and ignores family clustering. It is descriptive only.

## 5. Known weaknesses

- **Few clusters.**
  - 12 families give df = 11.
  - With 6 families (base only or ext only), the exact family sign-flip cannot reach p < 0.031, so no Holm rejection over 4 contrasts is possible.
  - CR1 with 12 clusters can still be somewhat anti-conservative. The simulation found family t at 0.918–0.99.
- **Ceiling effects.** Supplied-route accuracy and adoption are about 99–100%, so E2 item contrasts are skewed. The simulation found one-sided misses up to 0.079 for E2 near the ceiling.
- **Abstention confounds accuracy.**
  - `unknown` is a valid answer scored incorrect.
  - S2 (none route) and Kimi's optional-route accuracy largely track abstention. DeepSeek answered `unknown` in 85.5% of neutral and 55.5% of insistence none-route trials.
  - So S2 > 0 means insistence reduced abstention, not that it improved knowledge.
- **Kimi's E1** rests on a 16.8% neutral base rate.
- **Multiplicity.** Holm is applied within model × pressure only. There is no adjustment across the 4 models or for the secondaries.
- **Descriptive funnel conditioning.** "Attempted and correct" conditions on a post-treatment choice. It cannot support mediation or a "because it skipped the lookup" reading.
- **Measurement.** Builder-written families from one template; unrated pressure paraphrases; an irrelevant-expertise authority cue that may not be perceived as authority.
- **Repeats.** They use provider-default sampling with no provider seed. They estimate within-item variability, not new cases.
- **Serving.** One serving artefact (the DeepSeek markup leak). DeepSeek's provider differs between P1 (SiliconFlow) and P2 (AtlasCloud).

## 6. Questions for the reviewer

1. Given the simulation, should this development report present **CR1 (families as clusters, df = 11)** as the main interval, or keep the prespecified **item t** as primary with CR1 beside it? We kept item t (the PI's call) and flag every estimate where they disagree. Is that acceptable, or should the text lead with CR1?
2. With unequal family sizes, is the **sign-flip over family totals** the right family-level test for the item-weighted mean, or should the family-means flip (which tests the equal-family estimand) be shown instead?
3. **`unknown` scoring.** Should a committed-answers-only accuracy, or a three-category outcome (correct / incorrect / abstain), be added? It would be post hoc, so labelled exploratory. Or is stating the abstention shares enough for this submission?
4. Is **"same-sign amplification, not reversal"** a defensible descriptive reading of E4? It rests on the D(right) and D(wrong) point estimates and intervals; for gpt-oss and Qwen, D(wrong) > D(right) > 0.
5. Is the funnel statement safe as worded? It reads: "trials with a lookup attempt almost always ended with the record's value; the penalty sits in trials without one (descriptive, post-treatment)".
6. Should the base vs ext check use a family-clustered difference rather than Welch over items?
7. DeepSeek E2 (−2.4 pp, excludes 0 under every method) is the one clear supplied-route insistence effect. It is concentrated in wrong assertions (Δsupplied −4.5 pp). Is it safe to report as "with the record supplied, insistence still lowered DeepSeek's accuracy", given 20 arm-specific invalid answers and bounds of [−2.7, −1.7]?
