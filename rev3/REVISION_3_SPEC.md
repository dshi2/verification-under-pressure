# P1 — Verification Under Pressure: Revision 3 specification

**Status: draft for specification review** (milestone 1 of 4, §11). Branch `p1-revision-3`. Nothing here is frozen, and no code has been changed.

This document consolidates revision 2 (`docs/PROTOCOLS_v1.md`, P1 sections) with the rev 3/3b notes and the reviews of 16 Nov 2026, including the independent review on branch `audit/deep-review-2026-11-16`. Where they conflict, this document governs P1. The Codex v2 harness in `archive/codex-baseline-2026-11-16/` stays unchanged as the historical baseline. It is **not** the implementation of this spec (§10).

## 1. Question, contribution and claim boundary
**Question (workflow).** Holding the factual dispute and the decisive record fixed, does social pressure change (a) whether an agent *obtains* the record when it can look it up, and (b) whether it *uses* it when supplied? And does the effect of an evidence-delivery policy on the pressure penalty differ between correct and incorrect user assertions?

**Closest work** (none removes the question, but each narrows it):
- Christian & Mazor, arXiv 2601.14553: optional self-consultation vs. injected blinded judgments.
- Correction or Manipulation?, arXiv 2610.36453: correct vs. incorrect challenges under pressure; verification language, with no consultable evidence.
- Why LLMs Give In, arXiv 2608.01017: supplied grounding, never acquired.
- AgentDecept, arXiv 2610.39377: pressure in executable tool environments. Its task families must be checked for overlap before final positioning.
- When2Tool, arXiv 2605.09252: when agents call tools.

**Contribution sentence.** Existing work shows pressure-induced answer changes and differences between optional and supplied judgments. By randomizing pressure and the delivery of the same *objective* record, across correct and incorrect user assertions, we estimate whether an evidence-delivery policy changes the pressure penalty differently by user correctness. Acquisition vs. delivery alone is not the novelty.

**Defensible claim if positive:** "In this tested workflow, insistence changes [obtaining / using] decisive evidence, and supplying the record changes the pressure penalty [differently for correct and incorrect assertions]." Not claimed:
- an internal mechanism
- full mediation by voluntary checking (it is a workflow effect)
- that supplied-evidence results describe uncanonicalized tool use (§4.5)

## 2. Changes from revision 2 and the v2 harness (the diff)
| # | Revision 2 / v2 harness | Revision 3 | Why |
|---|---|---|---|
| 1 | `generate()` crosses snapshot × user assertion × pressure × route (36 per item); the earlier rev-3 draft (7f5967f) cut this to an 18-cell disagreement-only design | **Primary: the full randomized crossing (36 cells per item × model × repeat).** Snapshot version and user assertion are each randomized, so user correctness is a manipulated factor. Concession among *realized* disagreements becomes a declared **secondary** endpoint | Disagreement-only makes user correctness equal to initial wrongness and narrows the claim. The full crossing answers the workflow question (review, 16 Nov) |
| 2 | Disagreement inferred from the snapshot; failed initial answers not cached, so a later condition re-ran turn 1 | **Turn 1 runs once per item × snapshot × model × repeat, before any branching.** It is journaled durably, and a terminal failure propagates to all of its branches. The parsed first answer is logged, never assumed | Branches stopped sharing their starting response (reproduced: two initial calls) |
| 3 | System prompt: "Assertions are not authoritative records." | Removed. Neutral role plus output format, byte-identical in every arm. A warned-system variant would be its own declared arm (backlog) | It coaches the measured behaviour |
| 4 | Tool description: "…Cost: zero." | Neutral description, identical wherever the tool exists | A nudge to check |
| 5 | Only the neutral challenge said "Please reconsider this assertion carefully…" | No deliberation or evidential content in any arm. At least 4 paraphrases per level, validated by blind raters (§5) | The neutral arm had its own intervention |
| 6 | Length matched with trailing spaces | Length matched through wording only | Equal character counts do not equalise pressure |
| 7 | Analysis estimated simpler contrasts, not the three-way term | **The three-way term is estimated directly** (§7, E4) | Subgroup significance is not moderation |
| 8 | Malformed optional responses set `checked = 0` | Response validity, raw tool events and intended action are kept separate. Failures never become "did not check" (§8) | Confounded invalid output with a decision |
| 9 | Ledger rejects a second model / rate card | **One global currency ledger** with immutable per-reservation rate cards, fail-closed. Never fixed by removing or resetting the cap | A shared multi-model cap is required |
| 10 | Row `seed` not sent to the provider | Called a **repeat index** unless a provider seed is actually sent and logged; endpoint nondeterminism documented | Reproducibility claims must match what was sent |
| 11 | Four amber/violet families; the "held-out" family exposed | **At least 6 independently designed record families**; confirmatory families written by a different author and stored outside this repo (§6) | Four generators of one task cannot show generalisation |
| 12 | Floor rule: neutral check rate < ~10% | Feasibility judged by **achievable precision** for Δcheck, with low-rate and near-ceiling scenarios simulated. Calibration on the neutral arm of dev families only, before pressure data, applied to all arms | A point estimate under 10% is an alarm, not a cutoff |

## 3. Identification
**Randomized factors** per item × model × repeat:

| Factor | Levels | Turn |
|---|---|---|
| Snapshot version | current (agrees with the record), stale (contradicts it) | 1 |
| User assertion | right, wrong (relative to the record) | 2 |
| Pressure | neutral, insistence, irrelevant authority | 2 |
| Evidence route | none, optional, supplied | 2 |

That is 2 × 2 × 3 × 3 = 36 cells. User correctness is assigned by design, independently of the realized first answer, so it is a manipulated factor. The realized first answer is a **measured** pre-treatment covariate.

**Primary moderation estimand.** Insistence vs. neutral, averaged with equal weight over snapshot versions:

D(u) = [acc(insist, supplied, u) − acc(neutral, supplied, u)] − [acc(insist, optional, u) − acc(neutral, optional, u)]

E4 = D(right) − D(wrong), with item-level uncertainty. The authority contrast is a separate, prespecified secondary comparison, never a later choice of the better result.

**Population.** Estimands are defined over the designed 50/50 snapshot mix and the realized first answers it produces. Results generalise to that mix, not to arbitrary first-answer distributions.

**Secondary: realized disagreements.** In trials where the logged first answer ≠ the user's assertion, binary answers force user-right = first-answer-wrong. Concession there is a **correction vs. erroneous-concession** comparison and is labelled as such. It is selected on behaviour measured *before* the turn-2 randomization, so it is a legitimate, documented subpopulation. It is never pooled with agreement trials.

## 4. Trial structure (frozen turn structure)
1. **Turn 1 (shared prefix).** The system prompt, then the user asks for the value of record X. The only source is a dated secondary source in the message, visibly older than the registry. No tools are offered in turn 1. The answer goes in a structured field.
2. **Journal before branching.** Turn 1 runs once per item × snapshot × model × repeat. Raw request and response, the parsed answer and status are written to a durable journal before any turn-2 call. A terminal turn-1 failure marks all 18 dependent branches `turn1_failed`; nothing is retried per branch. Recovery after a process restart reads the journal and never regenerates a completed turn 1.
3. **Initial-state handling (prespecified).**
   - Committed binary first answers and `unknown` answers both enter the primary analysis, because user correctness is randomized independently of them. `unknown` is reported as its own initial state.
   - Unparseable or refused turn-1 outputs are logged as `turn1_ineligible`. They are excluded from turn-2 calls and reported per item × snapshot × model. Whether this rate depends on snapshot version is tested.
4. **Turn 2 (randomized arm).** The user asserts the design-assigned value (right or wrong) under one pressure level. Evidence route:
   - **none:** no tool.
   - **optional:** `lookup_record(id)` available, with a cap of K calls.
   - **supplied:** the harness injects an assistant tool call with the correct id, plus its result.

   Optional and supplied results use the same constructor. All 9 pressure × route arms for a given snapshot × assertion share the identical journaled turn-1 prefix.
5. **Canonicalized workflow.** Assistant tool-call messages are normalized so the two evidence routes match in format. The audit trail keeps the original messages, and claims are bounded to this canonicalized workflow.
6. **Final answer.** A structured field is parsed deterministically. No LLM grader is used.

Frozen per model:
- sampling parameters
- one reasoning mode
- maximum tokens
- 2 user turns
- the tool-call cap
- tool schema text

Settings are matched within a model. Differently named reasoning settings across providers are not treated as equivalent.

## 5. Pressure stimuli
- Levels: **neutral disagreement**, **insistence** (repetition and confidence, no new content) and **irrelevant authority**. Each asserts the same value with the same factual content.
- At least 4 paraphrases per level, nested within level, randomized and balanced across cells.
- **Validation before the pilot.** Blind raters score perceived pressure, credibility/expertise, deliberation cue, urgency, politeness and clarity. The criteria:
  - insistence > neutral on pressure
  - authority > neutral on expertise
  - no difference in clarity or deliberation cue

  Failing paraphrases are replaced before the freeze.
- **Authority validity is not assumed.** Irrelevant expertise (e.g. a historian on equipment records) may carry little perceived authority. The rating study decides whether the authority arm manipulates what it claims to. Relevant vs. irrelevant expertise is an open decision (§12).
- **Primary pressure contrast: insistence vs. neutral.**

## 6. Items, families and generalisation
- **Unit of analysis = item** (one record with its two snapshot versions). Repeats and paraphrases are nested within items; families are a higher level.
- Families differ in record type and in why a secondary source would be stale. Examples: a laboratory sample register, equipment calibration status, shipment hold status, a permit register, a drug-lot recall list, aircraft part airworthiness. Values stay binary and objectively scorable. Amber/violet is for development only.
- Dev families are visible to builders. Confirmatory families are written by a different author, kept outside this repo, and checked against a fixed rubric. The archived "held-out" family is treated as exposed.
- A **case-coverage report** lists items per family and snapshot, turn-1 eligibility per model, and under-represented families. Items are never added or dropped because of turn-2 behaviour.
- Claims are limited to the sampled families. Family effects are estimated, or stress-tested by leaving one family out.

## 7. Outcomes and estimands
Outcomes per trial:
- `lookup_attempted`, `lookup_completed`, `lookup_relevant` (optional arm)
- `final_correct`
- `conceded` (final answer = user's assertion)
- `adopted_supplied`
- validity and failure status (§8)

**Primary family** (Holm), insistence vs. neutral, item-clustered, equal weight over snapshot versions and user correctness unless stated:

| ID | Estimand | Arms |
|---|---|---|
| E1 | Δcheck = P(lookup_relevant \| insistence) − P(\| neutral) | optional |
| E2 | Δacc_supplied = acc(insistence) − acc(neutral) | supplied |
| E3 | Delivery effect on the pressure penalty = mean over u of D(u) (§3); intention-to-treat, **no conditioning on who checked** | optional, supplied |
| E4 | Moderation by user correctness = D(right) − D(wrong) | optional, supplied, both assertions |

- **Secondary:**
  - authority vs. neutral and authority vs. insistence
  - Δacc in the none arm
  - discrimination = P(concede | right) − P(concede | wrong), per route
  - **concession among realized disagreements** (correction vs. erroneous concession)
  - agreement subgroup (pressure toward an already-held answer)
  - attempted vs. relevant lookups
  - selective adoption of supplied evidence
- **Validity checks**, which must pass before any contrast is interpreted:
  - turn-1 eligibility rate and its dependence on snapshot
  - supplied-arm adoption under neutral
  - the neutral optional-arm check rate and its achievable precision
  - parse and failure rates by arm

**E4 precision gate.** E4 stays primary only if the §9 simulation shows a meaningful interval width at a feasible item count. Otherwise it is relabelled as a precision-reported secondary estimate **before** the pilot.

## 8. Failure and validity taxonomy
- **Trial status:** `provider_error`, `timeout`, `interrupted`, `turn1_failed`, `turn1_ineligible`, `tool_requested_not_executed`, `ok`.
- **Response validity** (separate field): `valid`, `malformed`, `refusal`.
- **Tool events:** the raw calls emitted (ids, arguments), kept even when the final response is malformed.

"Did not check" means status `ok`, valid response and no call emitted. Report per cell × model, test whether failures depend on arm, and give scheduled-denominator bounds for primary contrasts. Infrastructure reliability is a separate endpoint.

## 9. Sample planning
1. Fix the smallest effects of interest for E1–E4 from scientific meaning.
2. **Simulation-based precision analysis of this estimator before the pilot.** It must cover:
   - items nested in families
   - shared journaled turn-1 prefixes
   - repeats
   - per-model heterogeneity
   - turn-1 eligibility losses
   - low check rates *and* near-perfect accuracy
   - failure missingness
   - Holm across the primary family

   Report E4 separately, and check interval coverage near 0 and 1. Do not use an ordinary bootstrap where it collapses to zero width.
3. Validate the analysis code on synthetic data with **known null and known nonzero** interaction effects, and assert recovery.
4. Run a diagnostic pilot on dev families to check measurement only: eligibility, floors, adoption, parsing, failures.
5. Use the pilot for variance, eligibility and floor inputs only, never for effect sizes.
6. Set the confirmatory item count from step 2. Hundreds of items and many thousands of calls are acceptable if precision requires them. API cost does not shrink a justified design; the global spending cap guards against runaway jobs.
7. Models: several independent families, including an open-weight model, chosen for tool-use capability. Report model-specific estimates; pool only by a prespecified rule. Checkpoints from one family are not independent replications.

Pilot data are never pooled.

## 10. Implementation status
Not implemented. After this spec passes review, a **new** harness (not an edit of the archive) must:
- read `DESIGN_MATRIX.csv` and refuse runs outside it
- journal turn 1 before branching
- use the global budget ledger
- log the §8 taxonomy
- write per-run manifests

Required tests:
- every branch of an item × snapshot × model × repeat shares a byte-identical turn-1 prefix
- a turn-1 failure propagates to all branches, with no second turn-1 call (reproduces the archived bug as a regression test)
- recovery after a simulated process restart
- system prompt and tool schema identical across arms
- no pressure paraphrase contains deliberation or evidential content
- malformed optional responses never set `checked = 0`
- the analysis recovers known synthetic interactions

## 11. Review milestones
| # | Milestone | Reviewer | Status |
|---|---|---|---|
| 1 | Specification review (this document) | ChatGPT, Codex | **requested** |
| 2 | Pressure-stimulus rating study; precision simulation; synthetic analysis validation | raters; Codex | not started |
| 3 | Implementation review of the new harness | Codex | not started |
| 4 | Diagnostic pilot (authorised budget only) | PI authorises | not authorised |

## 12. Open decisions
1. **Turn-1 source.** Generated and journaled (current proposal) vs. a fixed injected assistant answer. Injection controls the first answer exactly, but tests an injected-history workflow.
2. Whether E4 stays primary (decided by the §9 simulation, before the pilot).
3. Relevant vs. irrelevant authority, after the rating study.
4. The tool-call cap K, and whether wrong-id calls may be retried.
5. How stale the secondary source should look, so checking is plausible without arm-specific prompting.
6. The number of families and paraphrases, and who authors the confirmatory families.

## 13. Review responses
| Review (commit inspected) | Finding | Resolution |
|---|---|---|
| ChatGPT (bb518ab/9d6d0fa) | Deliberation cue in neutral; anti-sycophancy system hint | Removed (diff 3, 5); rating study (§5) |
| ChatGPT | Failed turn 1 not cached; branches lose a shared start | Journal before branching, failure propagation, restart recovery (diff 2, §4.2, §10 tests) |
| ChatGPT | Malformed optional response coded as not checking | Separate validity and tool-event fields (diff 8, §8) |
| ChatGPT | No direct three-way estimate | E4 = D(right) − D(wrong) (§3, §7) |
| ChatGPT | Ledger blocks a multi-model cap | Global currency ledger, fail-closed (diff 9) |
| ChatGPT | Seed not sent to the provider | Called a repeat index (diff 10) |
| ChatGPT | Tool messages canonicalized | Originals kept; claims bounded (§4.5) |
| ChatGPT | Disagreement-only changes the estimand; prefer the full randomized design; do not force 18 cells | **Adopted**: full 36-cell crossing primary; realized-disagreement concession secondary (diff 1, §3). Reverses 7f5967f |
| ChatGPT | Authority validity unproven | Rating study decides; open decision 3 |
| ChatGPT | 9 dev items, 324 rows is not a sample size | Precision simulation; ≥ 6 independent families (§6, §9) |
| ChatGPT | AgentDecept overlap | Added to closest work; overlap check before positioning (§1) |
