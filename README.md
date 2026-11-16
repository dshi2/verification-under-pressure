# Verification Under Pressure (P1)

Does social pressure change whether an agent fetches objective evidence, uses supplied evidence, or both? The proposed contribution is the pressure × evidence-delivery × user-correctness comparison.

## Current development

Work is on `p1-revision-3`. The [revision-3 specification](rev3/REVISION_3_SPEC.md) describes the current design; older protocol amendments are historical context. Offline estimators and tests exist. A complete live execution harness, precision validation and human validation of pressure wording remain separate requirements. Confirmatory experiments and paid runs are not authorized.

- [Specification and estimands](rev3/REVISION_3_SPEC.md)
- [Estimator implementation](rev3/p1v3/estimands.py) and [tests](rev3/tests/)
- [Commit-specific reviews](reviews/)

Run the offline tests from `rev3/`:

```sh
python3 -m unittest discover -s tests -t . -q
```

## Historical material

`archive/codex-baseline-2026-11-16/` preserves the original combined P1/P2 diagnostic harness and its hashes. Do not edit it in place or use it as the current runner. `docs/` contains earlier protocols, checklists and handoffs; consult their revision status before applying them.

Shared execution infrastructure is planned, not an existing framework. If introduced, it must have one maintained implementation and recorded dependency versions rather than independently edited copies.

## Rules
- **Handoffs:** every handoff and review names repository · branch · commit · changes · checks performed · open issues. A review applies only to the commit it inspected.
- **No self-approval:** whoever wrote a component cannot approve it. Human/domain validation is required where the protocol says so.
- **Secrets:** never committed (see `.gitignore`). API keys stay in local environment variables.
- **Held-out confirmatory items** are kept outside development repos. Validators may inspect them under a fixed rubric; they and their results are never used for tuning, model choice, scoring changes or hypothesis selection.
- **Spending:** all projects share one ceiling and one ledger outside the repos (`~/Documents/research_active/ai-epistemics/budget/`, not yet created). Never one ledger per repo.
