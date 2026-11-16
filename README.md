# Verification Under Pressure (P1)

**Question.** Holding the factual challenge and decisive evidence fixed, does social pressure change whether an agent *obtains* evidence (optional lookup) and whether it *uses* it (identical evidence supplied), and does that depend on whether the user is right? The contribution is the three-way interaction, estimated directly. Voluntary vs. supplied evidence alone is known (Christian & Mazor, arXiv 2601.14553).

## Status (2026-11-16)
| Item | Status |
|---|---|
| Specification | Revision 3 pending. Primary contrast: insistence vs. neutral |
| Offline harness | Baseline exists (archive); fixes pending |
| Diagnostic pilot | Not yet |
| Confirmatory study | **Not approved** |
| Authorized paid runs | **None** |

## Contents
- `archive/codex-baseline-2026-11-16/`: preserved Codex harness and reviews with `SHA256SUMS`. Historical diagnostic baseline; do not edit in place.
- `docs/`: governing documents.
- `common/` (to be created): shared infrastructure owned here (budget ledger, model adapter, analysis utilities).

## Known blockers (baseline)
- The neutral arm alone has a deliberation cue ("Please reconsider…").
- Agreement trials are pooled with disagreement trials.
- An anti-sycophancy hint in the system prompt.
- Too many contrasts labeled primary.
- A failed turn 1 breaks the matching.
- Length matching is done by padding with spaces.

## Governing documents (`docs/`)
- `PROTOCOLS_v1.md`: revision 2 plus revision 3 / 3b amendment notes. A consolidated revision 3 specification is in progress; until then, revision 2 + the amendment notes apply.
- `NOVELTY_GATE_FINAL.md`: §2.2 novelty and contribution gate (round 2).
- `MASTER_CHECKLIST_ADDENDUM.md`: amendments to the 10-gate Research Quality Protocol (Master Checklist v3). **The v3 checklist text itself still needs adding.**
- `EXECUTION_CHECKLIST.md`: superseded; kept for history.
- `NOVELTY_CHECK*.md`, `HANDOFF_TO_CODEX.md`: history.
- `SHA256SUMS`: hashes of these documents as first committed.

## Rules
- **Handoffs:** every handoff and review names repository · branch · commit · changes · checks performed · open issues. A review applies only to the commit it inspected.
- **No self-approval:** whoever wrote a component cannot approve it. Human/domain validation is required where the protocol says so.
- **Secrets:** never committed (see `.gitignore`). API keys stay in local environment variables.
- **Held-out confirmatory items** are kept outside development repos. Validators may inspect them under a fixed rubric; they and their results are never used for tuning, model choice, scoring changes or hypothesis selection.
- **Spending:** all projects share one ceiling and one ledger outside the repos (`~/Documents/research_active/ai-epistemics/budget/`, not yet created). Never one ledger per repo.
