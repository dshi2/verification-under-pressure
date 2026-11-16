# Verification Under Pressure: Does Supplying the Record Change How Agents Respond to Correct and Incorrect Pushback?

**Draft for the Apart AI × Epistemics sprint report (official template, ≤8 pages).** This file holds the source text; formatting happens in the Google Doc.

Text in [brackets] is not filled yet. Every number in the Results section must come from checked logs or committed test output. Spec of record: `rev3/REVISION_3_SPEC.md` at `7c42796`.

**Authors:** [names, affiliations]
**Track:** 1, Model Epistemics & Decision-Making Evals

---

## Abstract (target 150–250 words; currently ≈215)

AI agents increasingly answer questions in workflows where a user can push back and where an authoritative record is either available on request or supplied automatically. Existing work shows that pressure can change model answers. It also shows that optional and supplied judgments can differ. What is not known is whether an evidence-delivery policy changes the *pressure penalty*, and whether it does so differently when the user is right and when the user is wrong. The difference matters because a policy that protects against wrong pushback might also suppress warranted correction.

We specify a randomized two-turn experiment on binary registry-record tasks. Each item crosses four factors:
- snapshot version (current or stale)
- assigned user correctness (right or wrong)
- pressure (neutral, insistence, irrelevant authority)
- evidence route (none, optional lookup, supplied record)

That gives 36 cells, all sharing a journaled first answer. The primary estimand, E4, is the three-way contrast: the difference between supplied and optional evidence in the insistence-versus-neutral effect on final-answer correctness, compared between correct and incorrect assertions. Supporting estimands separate lookup *attempts* from correctness when the record is supplied.

During the sprint we completed four things:
- the specification
- a contrast ledger
- point estimators with sign-aware missing-outcome bounds, validated on synthetic data with known effects (10/10 recovery tests pass)
- [a precision simulation: status]

No model experiments have been run, so this report makes no empirical claim about model behaviour. We report the design, the validated estimators, the precision requirements and the decision rules, including equivalence criteria for informative nulls.

---

## 1. Introduction

When an agent answers a factual question and the user pushes back, two failure modes matter. The agent may abandon a correct answer under pressure (erroneous concession), or it may refuse warranted correction. Giving the agent access to the authoritative record should help with both, but *how* the record is delivered is a design choice:
- **Optional lookup:** the agent must decide to check.
- **Supplied:** the workflow injects the record automatically.

These policies can differ in how far pressure moves the answer. The difference may also depend on whether the pressure points toward or away from the truth.

**Research question (E4).** In binary registry-record tasks, does the effect of insistence versus a neutral assertion on final-answer correctness differ between optional lookup and supplied evidence, and does that difference depend on whether the user's assertion is correct?

**Why it matters for decision quality.** An organisation choosing between "let the agent check" and "always attach the record" needs to know whether the choice changes susceptibility to pushback. It also needs to know whether that change is symmetric. A policy that reduces erroneous concession while also reducing warranted correction trades one error for another.

**Contribution.**
1. A fully randomized design in which user correctness is *assigned*, not inferred from the model's first answer. The novelty-bearing interaction (E4) is therefore identified on manipulated factors.
2. Explicit separation of lookup attempts (E1), correctness with a supplied record (E2), the delivery effect on the pressure penalty (E3) and its moderation by user correctness (E4).
3. Estimators with sign-aware assigned-denominator bounds, so that missing or invalid responses cannot be silently scored as "did not check".
4. Prespecified rules for when a null result is informative.

Acquisition versus delivery alone is not our novelty; the interaction is (§2).

## 2. Related work

- **Pressure and sycophancy.** SycEval (Fanous et al., 2025) and ELEPHANT (Cheng et al., 2025) measure answer-flipping under rebuttal and social sycophancy. MASK (Ren et al., 2025) shows models contradicting their own beliefs under pressure. The sprint's suggested *FlipRate* project measures flip curves under escalating rebuttals. These works study *whether* answers change. We study whether an evidence-delivery policy changes that susceptibility, separately for correct and incorrect pushback.
- **Correct versus incorrect challenges.** *Correction or Manipulation?* (arXiv 2610.36453) contrasts correct and incorrect challenges under pressure, with verification language but no consultable evidence.
- **Supplied versus acquired evidence.** *Why LLMs Give In* (arXiv 2608.01017) supplies grounding but never lets the model acquire it. Christian & Mazor (arXiv 2601.14553) compare optional self-consultation with injected judgments.
- **Tool use under pressure.** AgentDecept (arXiv 2610.39377) [verify by ID before citing] studies pressure in executable tool environments. When2Tool (arXiv 2605.09252) studies when agents call tools.

**Positioning.** None of these randomizes pressure and the delivery of the same objective record *crossed with* assigned user correctness. The contribution sentence and novelty gate are recorded in spec §1. If E4 cannot reach its precision floor (§3.6), the novelty assessment is reopened rather than kept on weaker contrasts.

## 3. Methods

### 3.1 Design

Factors are randomized within each item × model × repeat:

| Factor | Levels | Turn |
|---|---|---|
| Snapshot version | current (agrees with record), stale (contradicts it) | 1 |
| User assertion | right, wrong (relative to the record) | 2 |
| Pressure | neutral, insistence, irrelevant authority | 2 |
| Evidence route | none, optional, supplied | 2 |

That gives 2 × 2 × 3 × 3 = 36 cells. The realized first answer is a measured pre-treatment covariate. Each item × model × repeat is assigned a joint stratum from its first-answer correctness on (current, stale): CC, CW, WC or WW. Effective item counts are reported per stratum.

### 3.2 Trial structure

1. **Turn 1 (shared).** The user asks for the value of record X. The only source is a dated secondary source, visibly older than the registry. No tools are offered. Turn 1 runs **once** per item × snapshot × model × repeat and is journaled before any branching. A turn-1 failure propagates to all 18 dependent branches.
2. **Turn 2 (randomized).** The user asserts the assigned value under one pressure level. Evidence route:
   - **none:** no tool.
   - **optional:** `lookup_record(id)` available with a cap of K calls, described neutrally with no cost or encouragement wording.
   - **supplied:** the harness injects a tool call with the correct id and its result.
3. **Final answer.** Parsed from a structured field. No LLM grader is used.

The system prompt and tool schema are byte-identical across arms, and sampling settings are frozen per model.

### 3.3 Pressure stimuli

- Neutral, insistence (repetition and confidence, no new content) and irrelevant authority all assert the same value with identical factual content.
- No paraphrase presupposes disagreement, so the same wording works in agreement trials.
- There are at least 4 paraphrases per level.
- **Validation gate.** Before any pilot, blind raters must find insistence > neutral on perceived pressure. They must also find no difference in clarity or deliberation cue, shown by equivalence (TOST, ±0.5 on a 7-point scale). Paraphrases that fail are replaced.

### 3.4 Items

The unit of analysis is the item: one binary record with two snapshot versions. Repeats and paraphrases are nested within items. There are at least 6 independently designed record families. Confirmatory families are written by a different author and held outside the repository. Items are frozen before the pilot and are never kept or dropped based on model behaviour.

### 3.5 Outcomes and estimands

Every estimand is a fixed linear contrast of cell means. Items are weighted equally and so are the two snapshot versions. Insistence is compared with neutral throughout.

| ID | Estimand | Arms |
|---|---|---|
| E1 | Δ P(lookup attempted) | optional |
| E2 | Δ accuracy when the record is supplied | supplied |
| E3 | Delivery effect on the pressure penalty: mean over u of D(u) | optional, supplied |
| **E4** | **D(right) − D(wrong)** | optional, supplied, both assertions |

Here D(u) = [acc(ins, sup, u) − acc(neu, sup, u)] − [acc(ins, opt, u) − acc(neu, opt, u)].

- **Secondary contrasts:** authority comparisons, the no-tool pressure penalty, relevant retrieval E1b (split exactly as Δa·q_I + a_N·Δq), and concession among realized disagreements (never pooled with agreement trials).
- **Validity checks** must pass before any contrast is interpreted: turn-1 eligibility, supplied-record adoption under neutral pressure, and parse and failure rates by arm.
- **Missing data.** Every primary estimate is accompanied by **assigned-denominator bounds** over all scheduled trials. In cells with positive weight, the upper bound fills missing outcomes with 1; in cells with negative weight, with 0. The lower bound does the reverse. Filling everything with 0 and then with 1 is not a valid bound for mixed-sign contrasts.

### 3.6 Inference, informative nulls and sample planning

- **Multiplicity.** Holm correction is applied across E1–E4, with item-clustered inference. The interval method is chosen by a coverage simulation that reflects the design: family dependence, shared first answers, rare lookups, near-perfect accuracy and missingness.
- **Interpreting a two-sided primary contrast:**
  - **Equivalent within ±SESOI** only if the 95% interval lies entirely inside the bounds.
  - **Meaningful directional effect** if the interval lies entirely beyond one bound.
  - **Inconclusive** otherwise.

  A claim of joint absence across contrasts or models requires simultaneous intervals.
- **E4 precision floor.** A 95% half-width of at most 7.5 pp with probability ≥ 0.8. If the floor is unmet, add independent items and families first. If it is still unmet, report E4 with its precision and reopen the novelty assessment.
- **Freeze.** Pilot data inform variance, eligibility and stratum prevalence only, never effect thresholds. The estimands, SESOIs, population, inference, missing-data rule and sample size are frozen before any confirmatory outcome is observed.

## 4. Results

The work so far falls into three categories, kept separate below.

### 4.1 Completed software validation

`p1v3/estimands.py` passes 10/10 tests (`cd rev3 && python3 -m unittest discover -s tests -t .`). They cover:
- recovery of a known null
- recovery of a known moderation (E3 = 0.375, E4 = −0.25)
- separation of attempted and relevant lookup
- the authority contrast kept separate from the primary
- incomplete items counted rather than silently dropped
- bounds equal to the point estimate when data are complete
- E1 bounds of [−1, 1] when all attempts are missing
- bounds matching the minimum and maximum over every 0/1 completion (brute force)

### 4.2 Precision simulation

[Fill from the simulation PR, citing its SHA, with:]
- [interval method chosen, and why]
- [coverage near 0, near 1 and near ±SESOI, with Monte Carlo SE]
- [required independent items and families for the E4 floor, as a sensitivity grid over SESOI and pilot inputs]
- [comparison against the conservative reference bound (PR #2, c817338), which needs about 21,000 independent items at a half-width of 0.075 under worst-case Hoeffding assumptions; that figure is a bound, not a plan]

### 4.3 Model results

None. No model calls have been made.

| Model | Independent items | Effective items per stratum | E1 | E2 | E3 | E4 | Missingness | Validity checks |
|---|---|---|---|---|---|---|---|---|
| [—] | [—] | [—] | [—] | [—] | [—] | [—] | [—] | [—] |

## 5. Discussion

The design separates four quantities that are often conflated:
- whether an agent tries to check
- whether it uses a supplied record
- whether the delivery policy changes the pressure penalty
- whether that change is symmetric across correct and incorrect pushback

The main risk is precision. E4 is a three-way interaction, and interactions need many independent items. The simulation decides whether E4 is feasible before any data are collected.

A precise null on E4 would be informative. It would bound how much evidence-delivery policy can differentially protect against wrong pushback relative to right pushback in this workflow.

**Future work:**
- the pressure-rating study
- the new harness, with its required tests (spec §10)
- a diagnostic pilot to check measurement only
- the confirmatory run on independently authored families across several model families

## Appendix A. Limitations and Dual-Use / Ethical Considerations (required)

**What this does and does not establish.** No model behaviour has been measured. The contribution is a specified and software-validated experimental design. Once run, results will describe a behavioural workflow effect on the measured outcomes in the tested record families and models:
- They will not establish an internal mechanism.
- They will not establish mediation through voluntary checking.
- They will not generalise to arbitrary first-answer distributions.

The supplied arm uses a harness-authored tool call. "Supplied evidence" therefore includes the fact that the model did not make the call itself, and claims are limited to this canonicalized workflow.

**Measurement limits.**
- The pressure manipulation is unvalidated until the rating study is done.
- All development items are synthetic and written by one author.
- Ceiling effects (near-universal lookup or accuracy) may compress contrasts.

**Dual use.** Knowing which pressure forms and workflows make agents concede could help someone craft manipulative pushback. We mitigate this in three ways:
- The stimuli test generic insistence and authority cues, not optimised attacks.
- We report defensive policy contrasts.
- We release no adversarial prompt sets beyond the validated paraphrases.

**Personal data.** None. All records are synthetic.

## Appendix B. New work during the sprint

All files in this repository were created during the sprint (first commit 16 Nov 2026). The Codex v2 harness in `archive/codex-baseline-2026-11-16/` is preserved as a historical baseline from [confirm date and origin], and it is not the implementation of this design.

## Appendix C. Contrast ledger

See `rev3/CONTRAST_LEDGER.csv`. For each contrast it lists the cells compared, what is held fixed, the alternatives not ruled out, the method and the claim boundary.

## References

[Verify every entry by ID before submission; made-up references disqualify a project.]

- Fanous et al. (2025). SycEval. AIES 2025.
- Cheng et al. (2025). ELEPHANT.
- Ren et al. (2025). The MASK Benchmark. CAIS.
- Christian & Mazor (2026). arXiv 2601.14553.
- *Correction or Manipulation?* arXiv 2610.36453.
- *Why LLMs Give In.* arXiv 2608.01017.
- AgentDecept. arXiv 2610.39377. [verify]
- When2Tool. arXiv 2605.09252.
