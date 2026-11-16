> Historical revision-1 artifact. Superseded for implementation by PROTOCOLS_v1_revision2.md and reconciliation_v2.md. Do not treat this as the current protocol.

# Independent audit

Audit started 2026-11-16. Reviewer performed role 1 (novelty adversary) before taking role 5; independent from implementation and case construction, but **not independent from the project's literature framing**. No human/domain-expert review is implied.

## Current status

- Design review performed: `BUILD_FREEZE.md`.
- Full methods review performed: `methods_protocol.md`.
- Evidence design and ten-case JSON reviewed: `evidence_review.md`, `candidate_cases.json`.
- Implementation review and independent offline execution: completed for `epistemics_lab/lab.py`, `cases.json`, and implementation tests. Seven independent audit checks passed.
- Scripted fixture analysis replication: completed for the 384-row oracle and 384-row biased validation runs; raw-response arithmetic agrees with saved analysis.
- Empirical model results and statistical replication: not available; **not passed**. Offline fixtures are not model findings.
- Human/domain label validation: not performed.

## Design review findings

The freeze supports building diagnostic infrastructure. It does not authorize confirmatory interpretation. Key confounds are acknowledged: imported provisional records are not model-authored prior answers; evidence delivery is a workflow intervention; confidence in Q is distinct from attribution of verification; fictional scope labels are not expert scientific judgments.

### Required checks before a model run

1. **A, assertion agreement:** crossing provisional-record accuracy and user-assertion accuracy creates agreeing and disagreeing trials. User messages must not falsely describe every trial as disagreement. The outcome is pressure on final judgment, not necessarily concession from the model's own answer.
2. **A, action opportunity:** optional and supplied routes require the same number of response opportunities and comparable output format. A nonbinding preference in the supplied route is not voluntary retrieval. Record the current-record contents actually delivered; do not infer checking from prose or intended tool calls.
3. **A, treatment isolation:** neutral and insistent prompts must preserve factual assertion, expertise, evidence quantity, record visibility and budgets. If pressure includes demands to avoid checking, effects mix insistence with explicit workflow instructions.
4. **A, scoring:** unsupported/conflicting final values, abstentions, malformed output and technical failures need explicit separate labels. Accuracy must not silently exclude them. Conditional performance among voluntary checkers is post-treatment-selected and cannot identify mediation.
5. **B, same-information core:** content_only, narrow and unrelated arms must preserve P, R and Q text and the same underlying world. Direct outcome verification intentionally supplies different evidence and is a positive/negative capability control, not a same-information causal contrast.
6. **B, scope versus format:** scope_prose and scope_fields need identical semantic clauses. Both must retain the same original verification facts. Narrow-to-scope effects include extra information; prose-to-fields isolates rendering more closely.
7. **B, ontology:** not_established is not false. The target must ask what the audit establishes. Outcome observations are not automatically causal improvement. If Q concerns change, its baseline/population/time/comparator must be explicit.
8. **B, artificial rule leakage:** a schema that literally announces 'Q was not verified' makes scope arms easy by construction. That is a legitimate communication test, but cannot support broad claims about real assurance comprehension. The unclarified arm must remain realistic and uniquely labeled.
9. **Both, independent units:** number of templates/cases, rather than repeated seeds alone, governs generalization. Cluster related conditions and repetitions by base case. Avoid presenting synthetic scripted-policy runs as model behavior.
10. **Both, freeze and selection:** keep development and held-out cases separate, freeze outcomes/contrasts before confirmatory use, and retain clean null findings. Do not adapt case difficulty until a desired failure occurs.

## Acceptance criteria for subsequent audit

- Generated items encode ground truth separately from visible prompts and verify no accidental answer leakage.
- Core treatment arms preserve required text; independent perturbation checks confirm labels change when relevant facts change, and do not when irrelevant facts change.
- Tool traces prove that retrieval occurred and which record was returned.
- Independent recomputation from raw outputs reproduces reported counts/contrasts, including failed calls.
- Paired/clustered uncertainty respects case identity; no confirmatory p-values on adapted pilot prompts.
- Model identity, endpoint, decoding and dates are recorded; no model findings when no model was called.

## Provisional disposition

**Design: suitable for building and diagnostic testing, subject to checks above. Empirical validity: pending.** No claim about pressure suppressing checking or welfare verification spillover has been established.

## Methods review: issues requiring resolution

1. **Policy disclosure mismatch.** BUILD_FREEZE describes the supplied policy as disclosed with a nonbinding first-stage preference. Methods recommends an undisclosed automatic rescue after the acquisition choice, while allowing a documented disclosed variant. Either design is defensible but they estimate different workflows. Align the specification and implementation before model runs; do not pool variants.
2. **Mitigation calibration is not identified by the six arms alone.** The plain `outcome_verified` arm detects generic inability to recognize verified Q. It does not show that the scope intervention preserves warranted attribution, because that intervention is absent in this arm. Add truthful scoped-Q positive and negative controls (where scope explicitly includes Q), or restrict the claim to reduction of unsupported attribution and acknowledge that intervention-specific sensitivity is untested. Merely saying 'Q not assessed' will correctly force not_established in all such cases.

Both issues were sent to the engineering lead before empirical execution. The methods document otherwise makes the causal limits, independent units, missingness, mock-run distinction and human-review limits explicit.

## Evidence/case review

The source-grounded report correctly separates real conceptual motivation from fictional numerical facts, documents unperformed domain review, and explicitly limits calibration claims. The stipulated posterior arithmetic is correct: P posterior 0.8 after the positive report; Q probability 0.65 before verification and 0.75 after P verification. These targets are conditional on the disclosed fictional generator, not empirical welfare probabilities. The curated 5/5 Q balance must not be used for a representative-population calibration claim.

**Implementation-sensitive issue:** many `p_record` strings already state that animals/outcomes were not assessed or that only a certain scope was covered. If rendered verbatim in `narrow`, these exclusions partly implement the scope intervention in the untreated arm. Core narrow renderers should report P only without extra Q exclusions, reserving explicit exclusions for scope arms. Alternatively describe the experiment as testing robustness despite explicit scope; do not claim added scope information was manipulated when both arms contain it.

The ten cases are not ten independent domain validations. Two causal-simulator examples require stronger assumptions than record-level outcome cases. Use the recommended noncausal subset for initial diagnostic interpretation; broad welfare/certification claims remain pending real-case expert review.

## Implementation audit and resolutions

Reviewed `outputs/epistemics_lab/lab.py`, the ten engineered case records, and the fourteen implementation tests. Created and executed separate `audit_checks.py`; all seven independent checks passed after correction of the reviewer's own floating-point equality assertion. No network/model requests were made by this audit.

Resolved design issues:

- BUILD_FREEZE now adopts concealed automatic rescue, matching methods and identical stage-one prompts.
- Mitigation-specific warranted acceptance is explicitly untested; the six-arm outcome control is described as general task sensitivity only.
- Narrow rendering uses only the truthful P verification, without importing the candidate-record Q exclusions.

Found and corrected by the implementation owner before approval:

- B originally contrasted unsupported support only, although the protocol defines unsupported support **or refutation** as error. The owner added `unsupported_attribution` and switched primary contrasts accordingly. The independent adversarial check explicitly supplies an unsupported refutation and confirms it counts as a primary error.
- A acquisition endpoint is now documented as successful relevant lookup; attempted lookup is retained separately. This distinguishes a valid current record from a malformed/wrong-ID request.
- A originally coupled held-out allocation to only one wording. The split now preserves both wordings. This fixes that confound but does not create new substantive task families.

Independent execution checked full factorial balance, hidden-Q prompt invariance, identity of optional/supplied record content, unsupported refutation scoring, raw-response recomputation, missing-outcome bounds by enumerating all completions, and absence of scope exclusions in narrow records.

For the persisted artifacts, the auditor recomputed final accuracy from raw completion text, ignoring stored correctness metrics. Oracle fixtures give an A accuracy interaction of 0 and B narrow-minus-baseline unsupported attribution of 0. Biased fixtures give 0.5 and 1 respectively. Each run contains 384 scheduled development trials, and neither includes held-out trials. These injected values confirm arithmetic and logging; they establish **nothing about any language model**.

## Remaining limitations and release gate

1. A cases mostly vary record identity, binary value and two wordings within one administrative template. Case-bootstrap intervals do not support claims across diverse factual tasks. New substantive template families and a larger locked sampling plan are needed for confirmatory generalization.
2. B `scope_fields` currently renders a JSON array containing the same clauses as prose. It supports a punctuation/serialization comparison, not a claim about operational typed provenance infrastructure.
3. The structured attribution is scored mechanically; explanation/label contradiction has not been independently human-validated. Correct category plus contradictory rationale remains an unmeasured failure mode.
4. Runtime HTTP integration has not been tested against a real provider by this auditor. Endpoint-specific tool semantics are not evaluated: local JSON actions drive deterministic lookup and controller text supplies the result.
5. Perfect checker accuracy and the Bayesian source model are stipulated. Animal-welfare domain relevance, case realism and genuine scientific labels still require independent expert review. Both causal-simulator examples are artificial by construction.
6. No hidden empirical results, external preregistration, power justification, human labels or model replication have been produced. Tests that pass validate this software path, not the scientific hypotheses.

**Audit disposition: PASS for offline diagnostic harness validation. PENDING for live provider execution, independent human/domain labels and confirmatory scientific claims.** Re-run the independent checks after code changes. The existing narrow novelty claims remain provisional and should be rechecked against final methods before submission.
