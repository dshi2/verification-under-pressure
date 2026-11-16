# Research portfolio — three candidates, two intended submissions

**Current decision: see the [strict contribution review](research/STRICT_NOVELTY_GATE_v3.md). P1 needs a pressure-manipulation repair; P2 needs revised measurement controls; P3 is a welfare-centered candidate for further investigation. None is confirmatory-ready.** Revision 2 remains the historical diagnostic baseline; its software tests do not resolve these scientific issues.

**1. Verification Under Pressure (Track 1).** Does social pressure change whether an AI fetches objective evidence, uses it, or both? Compare neutral, insistent and irrelevant-authority assertions; no-tool, optional-tool and supplied-evidence workflows; and right versus wrong users.

**2. The Scope of Trust (Track 2).** Does verifying a narrow animal-welfare practice make an AI wrongly attribute verification to an unchecked outcome? Nine dossier conditions distinguish matching facts, scope clarification, format, unrelated checks, another facility's check, genuine outcome evidence and a vague label.

**3. Animal-welfare project — selection unresolved.** Two alternatives are under the same contribution gate: Welfare Without False Certainty and a welfare-centered Evidence Composition study. The former was the lead reviewer's provisional recommendation, not a jointly frozen selection. A newly inspected decision-completeness paper narrows its novelty; composition also has close predecessors. [Current comparison and audit](research/P3_COMPARISON_AND_REVISION3_AUDIT.md). Neither is implementation-cleared. There is one P3 slot, not two additional projects.

The intended final output is two well-executed submissions selected for contribution and evidence quality, including informative nulls. The implemented P1/P2 baseline remains revision 2; the strict review proposes changes for a future revision. Citation Drift, original Missing Denominator and Signed but Wrong remain inactive. Reporting-boundary displacement was considered during P3 review and is parked, not a fourth project.

## Review the current work

- [Latest P3 comparison and P1/P2 amendment audit](research/P3_COMPARISON_AND_REVISION3_AUDIT.md)

- [Contribution acceptance criteria: impact, novelty, validity and stopping rules](research/CONTRIBUTION_ACCEPTANCE_CRITERIA.md)

- [Strict contribution review and current decisions](research/STRICT_NOVELTY_GATE_v3.md)
- [Independent methods critique](research/STRICT_METHODS_REVIEW.md)
- [Independent P1/P2 novelty screen](research/STRICT_P1_P2_NOVELTY_REVIEW.md)
- [P3 adversary's assessment](research/STRICT_P3_ADVERSARY.md) and [selection disagreement](research/STRICT_P3_SELECTION_DISSENT.md)

- [Authoritative revision 2 protocol](research/PROTOCOLS_v1_revision2.md)
- [All 19 provisions: difference table and test mapping](research/reconciliation_v2.md)
- [Independent revision-2 audit](research/audit_report_v2.md)
- [Verified P2 source access](research/p2_source_status_v2.md)
- [Current harness instructions](epistemics_lab/README.md)
- [Preregistration draft](research/preregistration_draft.md) — not registered or frozen
- [Original novelty review](research/novelty_review.md) and [source ledger](research/sources.json)
- [Human review requirements](research/human_review_protocol.md)

Use `epistemics_lab/harness_v2.py`, not the archived revision 1 prototype. Revision 1 remains available in the original ZIP for comparison. Its uncapped HTTP runner was removed from the active package. Current mock runs are under `epistemics_lab/simulated/`, clearly separated from real-run paths.

## What the software has done

The revision-2 dataset contains 612 scheduled trials. The scripted development validation has 468 trials per policy: 324 P1 trials and 144 P2 trials. P2's count is 9 conditions × 8 development items × 2 truth states. The earlier 96 was 6 × 8 × 2, not 8 × 12. These scripted runs test software; they are not findings about language models. No held-out or live-model experiment has been executed.

The budget ledger reserves conservative cost before each call and records returned usage afterwards, under an atomic persistent cap shared across workers. Missing usage fails closed. Exhaustion halts the run. No API model, price card or spending amount has been selected, and the example configuration intentionally cannot run.

## Deliberately unfinished scientific work

The protocol itself is a design draft. Confirmatory execution is disabled. Real-model pilots, pressure manipulation checks, animal-welfare expertise, free-text grading validation, adequate substantive case coverage, effect/precision targets, multiplicity procedures and formal registration remain outstanding. Blinded grading packets and mechanical labels are not human validation. Reserved diagnostic families are not an untouched confirmatory corpus.

The user has explicitly expanded the candidate portfolio to three. Changes to P1/P2 still require a demonstrated flaw or established contribution reason; the new candidate does not silently alter their frozen diagnostic baseline.

Validation: 32 implementation tests and 11 independently authored checks passed. Both scripted runs contain 468 development trials. The full revision-2 package is epistemics_research_revision2.zip.
