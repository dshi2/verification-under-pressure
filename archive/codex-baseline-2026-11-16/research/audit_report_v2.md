# Independent audit of revision 2

Date: 2026-11-16. Status: **offline software audit passed within the scope below; scientific and live-provider validation pending**. The protocol remains a draft, not a formal preregistration or frozen confirmatory design. This report supersedes the v1 audit only for the revision-2 implementation.

## What was reviewed and reproduced

The reviewer read the authoritative revision-2 protocol and all 19 handoff provisions, inspected `harness_v2.py`, `p2.py` and `budget.py`, and wrote an independent check suite without modifying implementation code. The engineering lead resolved findings. Exact old-versus-new dispositions are recorded in `reconciliation_v2.md`.

All **32 implementation tests and 11 independent audit tests passed** on the final reviewed implementation. Independent checks include deliberately altered practice text, an initial-answer adapter returning `unknown`, an incorrect record-ID adapter, fabricated all-wrong-ID acquisition metrics, exhaustive missing-outcome bounds, repeated-row invariance, concurrent ledger reservations and a pre-network cap failure. These go beyond checking expected output from the ordinary oracle fixture.

Both saved simulated runs contain **468 development observations**: P1 has 324 observations from 9 items; P2 has 144 observations from 8 items, crossing two outcome truths and nine arms. Independent arithmetic parsed raw response strings, not the implementation's stored score fields, to reproduce P1 accuracy interactions, supplied-evidence adoption strata and the pressure × user-correctness interaction, plus P2 B−A, B−D1 and C−B attribution-error contrasts. Both manifests match the current hashes of all three implementation modules. No held-out, live or empirical model run was audited or produced here.

## Findings resolved during review

1. **C originally changed more than scope.** Its confirmation prose did not preserve the exact B verification prefix. C now begins with B's exact confirmation text and adds scope; C_prime carries that same text plus the same canonical scope fields in structured form. The independent regression checks exact prefix identity and typed-field equivalence. Human equivalence of perceived scope remains to be evaluated.
2. **Attempted checking could falsely pass the acquisition floor.** An agent could call only wrong IDs and have checked=1 with relevant=0. The gate now separately examines attempted and relevant acquisition; the all-wrong-ID fixture triggers lookup/measurement revision. Missing measurements produce an insufficient-data status. Neither failure authorizes selectively rewriting one arm.
3. **The supplied-route secondary interaction needed an explicit estimator.** It is now reported as pressure-minus-neutral evidence adoption with a correct user minus that difference with an incorrect user. Independent raw-answer arithmetic reproduces the full difference of differences.
4. **Simulation provenance needed enforcement beyond a label.** Analysis checks directory kind, manifest kind, per-row provenance and fixture response markers; the simulated runs are rejected by the real-analysis entrypoint. This is an integrity safeguard, not cryptographic protection against intentionally rewriting every provenance field.
5. **Actual initial responses and initial alignment need explicit interpretation.** Turn-one model output is cached and shared across downstream arms. An independent adapter returning `unknown` confirms it is not replaced by the supplied snapshot. Some assertions agree with that initial response. Already-aligned cases contribute zero to the unconditional changed-to-user concession rate; diagnostic initial-alignment/correctness strata are reported.

## Scientific limits retained explicitly

- The narrow novelty claim is **pressure × (choosing to check vs. evidence supplied) × user right/wrong, with objective evidence**. Neither voluntary-versus-supplied information alone nor an animal-welfare setting alone establishes novelty.
- P1 native tool-message matching controls the representation of returned evidence. Route randomization identifies the effect of the route package, including initiation and salience. It does not identify psychological mediation or prove that all timing/salience explanations are excluded. Final agreement with the objective record is evidence adoption as operationalized here, not a direct measure of comprehension.
- P2's primary endpoint is unsupported attribution of support/refutation to Q, including listing Q among supported verified claims. A rational increase in Q belief after learning P is not itself an error. The numerical posterior targets follow the stipulated synthetic generative model; they are not expert probabilities about real animal-welfare interventions.
- Q means the specified descriptive outcome-rate change in the fictional records. It does not establish a causal intervention benefit, whole-animal welfare improvement or the validity of an actual certification scheme. Independent animal-welfare review and real-source label adjudication have not happened.
- E checks whether the model uses directly supporting/refuting Q evidence in the ordinary verification format. E alone does not establish that the scope interventions C/C_prime preserve warranted acceptance when Q is explicitly verified. Such a claim requires additional scoped-Q controls.
- Character-length matching uses padding. It does not establish equal meaningful information, effort or perceived pressure. Three pressure wordings require human manipulation checks. Blind grader export omits metadata and verification-block text, but model responses may reveal treatment cues; free-text grader validation is still pending.
- Item-level bootstrap intervals are exploratory. The small number of items and shared templates constrain generalization. Repeated seeds are not independent new items. Complete-item estimates are accompanied by scheduled-denominator missingness bounds; absence of a significant difference is not evidence of equivalence.
- Family collision checks and disabled confirmatory execution prevent accidental reuse. The reserved families have already been visible to implementers and therefore are not a scientifically untouched holdout. A final confirmatory set, analysis specification, multiplicity decisions, effect-size targets and registration must precede confirmatory execution.

## Spending-control audit

The ledger reserves a conservative monetary bound before any request, persists reservations and settlements in SQLite, and serializes worker reservations. A restart cannot reuse held balance. Missing or uncertain usage blocks further execution while retaining reserved cost; the run stops rather than skipping unaffordable work. Independent concurrent reservations stayed within the cap, and a preflight cap failure made no network call.

This guarantee is conditional on every worker sharing the ledger and the configured rate card/token bounds covering actual billing. Underestimated provider charges cannot be prevented after a request has already been billed; the implementation records such excess and blocks further calls. This is not an account-wide provider spending cap. No real provider/model has been selected or billed in this audit.

## Disposition

**Proceed to a versioned development pilot only after provider/model, price bounds and monetary cap are configured and independently checked.** Offline implementation is sufficiently reconciled for that stage. Do not call the package empirically validated, the protocol frozen, the labels expert-validated or the experiments confirmatory. Complete pressure manipulation checks, domain/label review and blind response grading before making corresponding scientific claims. The pilot may reveal floor/ceiling or task-validity problems; any substantive redesign must be versioned and followed by fresh development observations.

Reproduce the checks from the workspace root:

```sh
python3 -m unittest discover -s outputs/epistemics_lab/tests -v
python3 outputs/research/audit_checks_v2.py
```
