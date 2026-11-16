# P1 numbers ready (workstream A, p1-stats)

Written 16 Nov 2026, ~16:40 IST. Plots (C) and the report (D) cite P1 numbers **only** from the files named here.

## 1. Where the numbers are

**Code commit:** `8b6af31` on `p1-revision-3`. The family-level sensitivity, CSV exports, components and independent check landed in `db830de` and `8b6af31`.

**Analysis outputs** are local only, because `runs/` is gitignored. They were regenerated from the v2 runs at this commit, and WS-F publishes them to `rev3/results/`.

| set | dir | items / families | runs |
|---|---|---|---|
| **combined (report this)** | `rev3/runs/analysis_combined/` | 60 / 12 (6 families × 4 items + 6 × 6) | `runs/p1_dev_eval_v2` + `runs/p1_ext_v2` |
| base only | `rev3/runs/analysis_base/` | 24 / 6 | `runs/p1_dev_eval_v2` |
| ext only | `rev3/runs/analysis_ext/` | 36 / 6 | `runs/p1_ext_v2` |

Each directory holds:
- `analysis.json`, the single source of truth;
- `analysis.md`;
- `contrasts.csv`, every estimand with every interval type;
- `validity.csv`;
- `funnel.csv`, counts with denominators;
- `interaction.csv`, the D(u) components;
- `unknown_answers.csv`;
- `batches.csv` (combined only).

SHA-256 at this commit:

```
f7ec6369dc9328ba63a2605c55576640dc86a46de3ce17d087280d7c997ce71e  runs/analysis_combined/analysis.json
8a7f4b36db12493cd2ccef214847fd7df910a4edb525edabda761755f80ed98b  runs/analysis_combined/contrasts.csv
5fee33d69d487ddc411d5dead6950c53a8f7f066a6ba0bbeadd60b3aec049eb6  runs/analysis_combined/funnel.csv
156b88bb737596f8e8d1cf7ab3efa3bdc1ae7feb09334d670186d0598b4f7643  runs/analysis_combined/interaction.csv
84ba6fbb7706ffa84cd75eedab66c2d64883b52f64152e945cadc3b57ef51d73  runs/analysis_combined/validity.csv
a73b6c26c1888d94431e042d09bff0409500a3e4a62715e3cfad8fb19cd65032  runs/analysis_combined/unknown_answers.csv
8588cd17a2f5e911f02a637d086d501b34666bda7f2e68b80e58b43b66d9bc3f  runs/analysis_combined/batches.csv
841aedeabd5e3e2c65cdfad71b36dccb1fd9da229d622d6cd2eab2b9eefd9956  runs/analysis_base/analysis.json
9d9f2af9c7978e001e29743cc6857cf8c1e6cea52d3f77e0c609d36948c986d3  runs/analysis_ext/analysis.json
```

**Regenerate** (from `rev3`, deterministic):

```
python3 analyze_p1.py --run-dir runs/p1_dev_eval_v2 runs/p1_ext_v2 --out runs/analysis_combined --strict
```

**Independent check:** `verify_p1_independent.py` (numpy/scipy; it never imports `p1v3.estimands` or `p1v3.inference`). It reproduces every estimate in all three sets for both pressures, with a max abs diff of 4.6e-14 and 0 mismatches. The fields checked are:
- E1, E1b, E2, E3, E4, S2;
- the item-t and CR1 intervals;
- t-test p, Holm, CR1 p and the exact family sign-flip p (each with Holm);
- the equal-family estimate and its interval;
- the assigned-denominator bounds;
- items used.

Its output is `runs/audit_p1/independent_check.json`. Tests: 34 OK (`python3 -m unittest discover -s tests`).

### JSON keys requested by C and D (all in `analysis.json`)

- **Funnel (Fig 2).** `cells[model]["<snapshot>/<assertion>/<pressure>/<route>"]` now also has:
  - `lookup_relevant: [mean, n]`;
  - a `counts` block: `scheduled`, `status_ok`, `valid_final`, `final_unknown`, `final_correct`, plus `attempted`, `completed` and `relevant` in the optional route. Their denominator is `status_ok`.

  The same data, pooled over snapshots, is in `funnel.csv`. **Note for C:** a cell dict now contains a non-`[mean, n]` entry, `counts`. Skip it when iterating outcomes.
- **E3/E4 components (Fig 1).** `estimates[pressure][model]["components"]` has:
  - `["delta_acc"][u][route]`, where u ∈ {right, wrong} and route ∈ {none, optional, supplied};
  - `["D"][u]`.

  Each is `{estimate, items_used, inference: {ci95_item_t, ci95_family_cr1, degenerate, …}}`. They are item-weighted and averaged over snapshots. They reconstruct E3, E4 and S2 to within 6e-17. They are descriptive components: no Holm, and not separate hypotheses. The same data is in `interaction.csv`.
- **`unknown` answers.** `unknown_answers[model]["final_by_arm"]["<pressure>/<route>"]` and `["turn1_by_snapshot"][snapshot]`. Also in `unknown_answers.csv`.
- **New inference keys** on every estimand: `p_family_cr1`, `p_family_cr1_holm`, `p_signflip_family`, `p_signflip_family_holm`, `p_signflip_family_min_attainable`, `ci95_equal_family_t`, `excludes0_item_t_only`, `family_sizes`. All earlier keys are unchanged and bit-identical: only the `label` string changed.

## 2. Final vs provisional

**Final.** These are data-level counts and point quantities. They change only if a code bug is found, and the independent recompute agrees with them.
- Trial counts and status.
- Validity, parse and truncation.
- Funnel counts.
- `unknown` shares.
- All point estimates, including the D(u) components.
- The assigned-denominator bounds.
- Execution windows.
- The journal audit (provider and model identity, tool calls).
- The Kimi audit.

**Provisional.** Every interval and every p-value.
- The coverage simulation (`SIM_P1_COVERAGE.md` §3) recommends a family-clustered method. The PI has not changed the prespecified primary, which is the item t interval with t-test + Holm.
- All of it is builder-written development data. Nothing is confirmatory, no SESOI is fixed, and so no equivalence or noninferiority statement is possible.

## 3. Interval and p-value labels (exact recommended wording)

- **Primary interval column:** "95% CI, items as clusters (t, df = 59; provisional)".
  Footnote: *"Treats the 60 items as the independent units. It describes the sampled record families. Our coverage simulation shows it can under-cover for new families when families differ."*
- **Sensitivity interval column:** "95% CI, families as clusters (CR1, t with df = 11; sensitivity)".
  Footnote: *"Same item-weighted estimate, with record family as the cluster. This is the interval our coverage simulation recommends for claims beyond the sampled families."*
  - Do **not** call it "t over family means". With 4 vs 6 items per family the two differ; the family-means interval is `ci95_equal_family_t` and belongs to the equal-family estimate.
- **Primary p:** "two-sided one-sample t-test over items, Holm-adjusted across E1–E4 within each model (provisional)".
- **Sensitivity p:**
  - "CR1 family-clustered t-test (df = 11)";
  - "exact family-level sign-flip test (12 families; smallest attainable p = 0.00049)".
  - Both are Holm-adjusted the same way.
- **Item-level sign-flip** (`p_signflip_secondary`): do not cite. The simulation shows type-I error of 0.10–0.22 under family heterogeneity.
- **Base-only or ext-only (6 families):** the exact family sign-flip cannot go below p = 0.031. So no Holm rejection over four contrasts is possible there. Say this if citing it.
- **Never write "significant", "no effect" or "equivalent".** Write "excludes 0 under [named interval]" or "includes 0 under [named interval]".
- **Units:** percentage points (pp), insistence minus neutral.
- **Unit of analysis:** the item. The 5 repeats are averaged within item × cell, so n = 60 items, never 300 trials.

## 4. Headline numbers (combined, 60 items / 12 families, insistence vs neutral)

All in pp. Each entry is: estimate, item-t 95% CI, CR1 family 95% CI. The last line of each block gives the Holm-adjusted p in the order (t-test / CR1 / family sign-flip). ⚑ = the estimate excludes 0 under item t only.

**E1 Δ lookup attempt (optional route)**
- DeepSeek-V3.2: −1.3, [−2.0, −0.7], [−2.2, −0.4]
- gpt-oss-120b: −10.0, [−12.5, −7.5], [−15.1, −4.9]
- Kimi-K2-0905: −5.8, [−8.7, −2.8], [−10.3, −1.2]
- Qwen3-235B-2507: −49.7, [−52.3, −47.1], [−54.0, −45.4]
- Holm p: DeepSeek .00028 / .016 / .031; gpt-oss 2e-10 / .0047 / .002; **Kimi .00095 / .071 / .080**; Qwen <1e-15 / 1.5e-10 / .002

**E2 Δ accuracy, record supplied**
- DeepSeek-V3.2: −2.4, [−3.7, −1.2], [−3.6, −1.3]
- gpt-oss-120b: −0.4, [−0.8, +0.0], [−1.1, +0.3]
- Kimi-K2-0905: −0.4 ⚑, [−0.8, −0.1], [−0.9, +0.1]
- Qwen3-235B-2507: −0.2, [−0.4, +0.1], [−0.5, +0.2]
- Holm p: DeepSeek .00075 / .0027 / .0039; gpt-oss .058 / .21 / .38; Kimi .048 / .19 / .50; Qwen .16 / .35 / 1

**E3 delivery effect on the insistence penalty**
- DeepSeek-V3.2: −1.8, [−3.0, −0.5], [−2.7, −0.9]
- gpt-oss-120b: +4.5, [+2.4, +6.6], [+1.3, +7.7]
- Kimi-K2-0905: +5.1 ⚑, [+1.5, +8.7], [−0.4, +10.5]
- Qwen3-235B-2507: +25.6, [+23.4, +27.8], [+22.8, +28.4]
- Holm p: DeepSeek .013 / .0039 / .0088; gpt-oss .00016 / .022 / .018; Kimi .020 / .19 / .19; Qwen <1e-15 / 1.6e-9 / .002

**E4 moderation by assigned user correctness**
- DeepSeek-V3.2: +2.5 ⚑, [+0.4, +4.6], [−0.0, +5.1]
- gpt-oss-120b: −4.7, [−7.7, −1.7], [−7.7, −1.6]
- Kimi-K2-0905: +1.5, [−4.5, +7.5], [−6.1, +9.1]
- Qwen3-235B-2507: −40.5, [−45.5, −35.5], [−47.4, −33.6]
- Holm p: DeepSeek .019 / .052 / .062; gpt-oss .0055 / .020 / .018; Kimi .62 / .67 / .71; Qwen <1e-15 / 1.1e-7 / .002

**E1b Δ relevant retrieval (secondary).** Identical to E1 for gpt-oss, Kimi and Qwen. For DeepSeek it is −1.2 vs −1.3. Every trial with an attempt also retrieved the correct id, except 3 DeepSeek trials. Kimi's single wrong-id call came in a trial that also made a correct call.

**S2 Δ accuracy, no evidence route (secondary; see the §6 caveat on `unknown`)**
- DeepSeek-V3.2: +15.1, [+12.8, +17.3], [+12.0, +18.2]
- gpt-oss-120b: +2.3, [−0.1, +4.6], [−0.8, +5.3]
- Kimi-K2-0905: −3.7 ⚑, [−6.8, −0.7], [−8.1, +0.6]
- Qwen3-235B-2507: +7.9, [+4.4, +11.4], [+2.7, +13.2]

**E4 half-width vs the 7.5 pp floor (descriptive).**

| | item t | CR1 |
|---|---|---|
| DeepSeek | 2.1 | 2.6 |
| gpt-oss | 3.0 | 3.1 |
| Kimi | 6.0 | **7.6 (above the floor)** |
| Qwen | 5.0 | 6.9 |

**Components (insistence; D(u) = Δsupplied(u) − Δoptional(u); item t CI, CR1 CI).** In no model do D(right) and D(wrong) have opposite signs:

| model | D(right) | D(wrong) | Δoptional right / wrong | Δsupplied right / wrong |
|---|---|---|---|---|
| DeepSeek | −0.5 [−1.4, +0.4] [−1.4, +0.4] | −3.0 [−5.2, −0.9] [−5.1, −1.0] | +0.2 / −1.5 | −0.3 / −4.5 |
| gpt-oss | +2.2 [+0.7, +3.6] [−0.5, +4.9] | +6.8 [+3.5, +10.1] [+2.5, +11.1] | −2.5 / −7.3 | −0.3 / −0.5 |
| Kimi | +5.8 [+0.7, +11.0] [−2.4, +14.0] | +4.3 [+0.2, +8.5] [−0.2, +8.9] | −6.5 / −4.5 | −0.7 / −0.2 |
| Qwen | +5.3 [+3.0, +7.7] [+1.6, +9.0] | +45.8 [+41.8, +49.8] [+40.7, +50.9] | −5.3 / −46.2 | 0.0 / −0.3 |

**Authority vs neutral (secondary S1; the authority cue is unrated).** Most estimates include 0. These are the exceptions:

| contrast | estimate | item t | CR1 | Holm p (t / CR1 / flip) | excludes 0 under |
|---|---|---|---|---|---|
| Qwen E1 | +4.2 | [+1.5, +7.0] | [+0.3, +8.2] | .008 / .11 / .13 | item-t Holm only |
| Qwen E4 | +8.2 | [+3.9, +12.4] | [+3.7, +12.7] | .0012 / .0086 / .039 | all three |
| Kimi S2 | −6.7 | [−9.4, −4.0] | [−11.3, −2.0] | — | both intervals |
| gpt-oss S2 | −2.8 ⚑ | [−5.1, −0.5] | [−6.9, +1.2] | — | item t only |

Degenerate (all item contrasts equal; zero width, which is not precision):
- DeepSeek authority E1: 0, because lookups are 100% in both arms;
- Qwen authority E2: 0, because accuracy is 100% in both arms.

**Every ⚑ flag (estimate excludes 0 under item t but not under CR1).**
- Combined:
  - DeepSeek E4 insistence;
  - Kimi E2, E3 and S2 insistence;
  - gpt-oss S2 authority.
- Base only:
  - DeepSeek E3 and E4 insistence;
  - Kimi and Qwen S2 insistence;
  - gpt-oss E1, E1b and S2 authority;
  - Kimi S2 authority.
- Ext only:
  - DeepSeek E1 and E1b insistence;
  - gpt-oss E1, E1b and E3 insistence;
  - Kimi E1, E1b and E2 insistence;
  - Qwen S2 insistence;
  - Kimi S2 authority;
  - Qwen E1 and E1b authority.

Full list: `excludes0_item_t_only` in each `contrasts.csv`.

## 5. Validity, funnel, Kimi, journal (all final)

**Schedule.**
- base: 17,280 scheduled = exported = status `ok`;
- ext: 25,920 scheduled = exported = status `ok`;
- 0 duplicates; every model × cell is complete (120 per cell base, 180 ext).

**Turn-1 eligibility and truncation.** Turn-1 eligibility is 100% for every model and snapshot. Truncation: 0.

**Invalid (malformed) final answers.** 29 of 43,200 trials (0.07%). Missingness is only at accuracy, never at lookup.
- DeepSeek: 20, all in the supplied route.
- gpt-oss: 9.
- Kimi and Qwen: 0.

**Positive control: neutral supplied adoption.**

| model | rate | n |
|---|---|---|
| DeepSeek | 99.2% | 1,191 |
| gpt-oss | 99.9% | 1,198 |
| Kimi | 100% | 1,200 |
| Qwen | 100% | 1,200 |

**Neutral optional lookup rate** (n = 1,200 each): DeepSeek 100%, gpt-oss 99.0%, Qwen 79.8%, Kimi 16.75%.

**Funnel (combined, optional route, all pressures; `funnel.csv`).** Attempted / status ok; relevant; attempted and correct:

| model | attempted | relevant | attempted and correct |
|---|---|---|---|
| DeepSeek | 3,584 / 3,600 | 3,581 | 3,581 |
| gpt-oss | 3,433 / 3,600 | 3,433 | 3,433 |
| Kimi | 512 / 3,600 | 512 | 512 |
| Qwen | 2,326 / 3,600 | 2,326 | 2,326 |

Descriptively, a trial with a lookup attempt almost always ended with the record's value. The insistence penalty in the optional route sits in trials with no lookup attempt. For example:
- Qwen, insistence, wrong assertion: 177 / 600 attempted, 207 / 600 correct;
- Qwen, neutral, wrong assertion: 481 / 600 attempted, 484 / 600 correct.

This is conditional on a post-treatment choice. **It is descriptive, not mediation.**

**Kimi-K2: choice vs capability.** The finding is a low propensity to call the tool, not a tool-call or serving failure.
- Kimi emitted 513 `lookup_record` calls in the optional route, across 512 of 3,600 trials (both runs).
  - 513 / 513 were well-formed: JSON arguments with `record_id`, finish_reason `tool_calls`.
  - 512 / 513 had the correct id.
  - All 512 trials with a call ended with the correct final answer.
- No failure signal in the logs:
  - 0 responses with finish_reason `tool_calls` but no parsed call;
  - 0 responses with tool-call markup leaked into the text;
  - 0 non-200 final results.
- Transport retries (HTTP 429 and connection resets, 317 across both runs) were spread across routes: none 81, optional 129, supplied 104, turn 1 3. All ended `ok`.
- The lookup rate is low in every cell: 7.7–20.0% across pressure × assertion × snapshot (n = 300 each).
- Without a lookup, Kimi mostly answered `unknown`: 63.5% of neutral and 69.3% of insistence optional trials.
- Wording: "Kimi-K2 produced well-formed lookups when it used the tool, but used it in only 16.8% of neutral optional trials, so its E1 rests on a low base rate."
- Do not say "chose": the data show behaviour, not intent.

**Journal (provider identity).**
- Every `ok` result was served by the pinned provider and model:
  - DeepSeek: SiliconFlow `deepseek/deepseek-v3.2`;
  - gpt-oss: DeepInfra;
  - Qwen: DeepInfra;
  - Kimi: Novita.
- Requests were sent with `allow_fallbacks: false`.
- One DeepSeek optional response (base run) has SiliconFlow's raw tool-call markup in its text instead of a parsed call. It is one of 7,194 DeepSeek optional-stage responses.
- Reasoning text returned:
  - DeepSeek: 100% of ok responses; mean reasoning tokens 224 base, 227 ext.
  - gpt-oss: 98.1% base, 97.9% ext; mean reasoning tokens 107, 104.
  - Kimi and Qwen: 0 (non-thinking checkpoints).
- ok provider responses: base 22,275; ext 33,192.
- Provider-reported cost of ok responses: base $4.10, ext $5.73. These equal `confirmed_usd` in each `summary.json`.

**Execution windows.** These come from the journal session records.
- base: 15:46:07–15:59:41 IST;
- ext: 15:46:32–16:15:23 IST, with a restart at 16:14 for the final call.

The two item sets ran **concurrently**, not one after the other. D's wording, "item sets run concurrently", is correct.

**Base vs ext (`batches.csv`; Welch over item values, unadjusted, 48 comparisons).**
- 1 of 48 differences excludes 0: gpt-oss authority S2, +7.4 [+2.7, +12.1]. That is about the number expected by chance (≈2.4 at 5%).
- No insistence difference excludes 0.
- Welch here ignores family clustering.

## 6. Claims

**Safe** (each with the named interval; all are "in these builder-written development cases"):
1. All 43,200 scheduled trials completed. 99.93% had a valid final answer, and none was truncated. Every response came from the pinned endpoint.
2. **Qwen3-235B:** insistence cut optional lookup attempts by 49.7 pp. Its insistence penalty on accuracy was 25.6 pp smaller with the record supplied than with optional lookup (E3). That difference was 40.5 pp larger for wrong than for right assertions (E4). All three exclude 0 under both the item and the family interval, and under all three Holm-adjusted tests.
3. **gpt-oss-120b:** E1 −10.0, E3 +4.5 and E4 −4.7 exclude 0 under both intervals and all three Holm tests.
4. **The E4 pattern is same-sign amplification, not reversal.** For gpt-oss and Qwen, D(wrong) > D(right) > 0 in the point estimates. No model shows D(right) and D(wrong) of opposite sign.
5. **DeepSeek-V3.2** looked up the record in essentially every optional trial (neutral 100%). With the record supplied, insistence lowered accuracy by 2.4 pp (E2, excludes 0 under both intervals). This is concentrated in wrong assertions (Δsupplied −4.5 pp). It is the only model whose E3 is negative (−1.8, excludes 0 under both).
6. E2 was small for every model: estimates between −2.4 and −0.2 pp. This is a statement about the size of the estimate. It is not "no effect".
7. Descriptively, optional-route trials with a lookup attempt almost always ended correct. The accuracy penalty sits in trials without an attempt. No mediation claim.
8. The Kimi-K2 audit sentence in §5.
9. Base and extension estimates agree: no insistence difference excludes 0, and 1 of 48 differences overall (unadjusted).

**Unsafe** (do not write):
- Any equivalence, "no effect", "eliminates" or "noninferior" statement. No SESOI is fixed.
- "Reversal" of the delivery effect for any model.
- DeepSeek E4 (+2.5) as a moderation effect. It excludes 0 only under the item interval (CR1 [−0.0, +5.1]; family Holm .052 / .062).
- Kimi E3 (+5.1) or Kimi E2 (−0.4) as excluding 0. Item-only.
- Kimi E1 as surviving multiplicity. It survives item-t Holm only (family Holm .071 / .080), and it rests on a 16.8% base rate.
- **S2 or none-route accuracy as "accuracy loss" or "sycophancy" without the `unknown` caveat.** `unknown` is scored incorrect.
  - In the none route, DeepSeek answered `unknown` in 85.5% of neutral and 55.5% of insistence trials.
  - Qwen: 16.8% → 1.3%.
  - So S2 > 0 mainly reflects insistence reducing abstention.
  - Turn-1 `unknown`: DeepSeek 92%, Kimi 71%, gpt-oss 52–58%, Qwen 19% (`unknown_answers.csv`).
- Any mechanism: "trusts the user over the record", "decides not to verify because…", or "insistence suppresses checking, which causes the penalty".
- Using the item-t interval to talk about record tasks or families in general. Use CR1 for that, and still only as a development-case description.
- Pooled or cross-model rankings with inference. Models are compared descriptively only.
- Authority as "authority pressure" without "unrated cue". Qwen authority E1 survives item-t Holm only.
- Trial-level n (300 or 600 per cell) as the sample size. n = 60 items, 12 families.
