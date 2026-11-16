# Project 3 candidate: Evidence Compatibility

**Historical candidate, superseded by the [strict review](STRICT_NOVELTY_GATE_v3.md).** The generic composition design did not establish a sufficiently meaningful welfare contribution. The proposed P3 is now Welfare Without False Certainty, with an investigate-further verdict. The text below records the earlier proposal, not current approval.

Working question: **Can these sources actually be combined?**

Status, 2026-11-16: selected as a third research candidate for design and measurement validation, following the user's expansion of the portfolio. Not a frozen protocol, completed novelty clearance, or authorization for paid calls. No P3 experiments or condition renderers have been built. P1 and P2 remain unchanged. The intended final portfolio contains two well-executed submissions, not necessarily two positive results.

## Contribution to test

Existing work establishes that entity ambiguity, claim decomposition and complex evidence relations can cause factuality and citation failures. The narrower question is whether evaluators still accept unsupported cross-source comparisons **after entity identity and extraction errors have been removed**, because they fail to check whether the populations, denominators or measurements are comparable.

We would distinguish failure to recover facts from failure to establish the relation between facts by supplying independently checked, lossless evidence records, retaining the complete target claim, and varying only the comparison-relevant metadata. We would measure erroneous support judgments, correct rejection of contradicted claims, and preservation of acceptance on valid comparisons. This precise combination survived a targeted screen; it is not a claim that nobody has studied it.

P1 asks whether pressure changes evidence acquisition and use. P2 asks whether truthful verification of P changes attribution of verification to Q. P3 asks whether a fixed conclusion follows from several source records; no verified badge, auditor authority or user-pressure manipulation is required. This distinction is essential to avoiding a third version of P2.

## A concrete diagnostic example

These are invented complete administrative records, not estimates from real animals. The endpoint is the recorded injury fraction among the enumerated animals, not overall welfare, population prevalence or a causal effect of an intervention.

Target claim in every version: “The recorded injury fraction was lower in period 2 than period 1.” Both periods concern the same identified facility, population definition and injury definition.

| Evidence | Correct status |
|---|---|
| Period 1: 8 injured out of 100; period 2: 4 out of 100 | Supported: 8% to 4% |
| Period 1: 8 out of 100; period 2: 4 out of 25 | Refuted: 8% to 16% |
| Period 1: 8 out of 100; period 2: 4 injured, total unspecified | Not established: totals of 100 and 25 are both consistent with the visible record, but imply opposite answers |

This is a sanity check, not a publishable dataset by itself. A second family can hold denominators known while varying whether two reports cover the same cohort or endpoint. Incompatible observations generally leave the target comparison **not established**, rather than proving it false. Literal differences in units are not necessarily incompatibilities: known conversions must be accepted.

Changing comparison metadata changes information. We must not describe all facts as identical across gold-status variants. Hold the target claim, unaffected counts, identities, source style and irrelevant text fixed; document the exact metadata changes and counterbalance wording and position.

## Closest studies and the novelty boundary

| Verified source | What was tested/found | Required distinction or baseline |
|---|---|---|
| [Merging Facts, Crafting Fallacies](https://aclanthology.org/2024.findings-acl.160/); [author repository](https://github.com/d223302/Merging-Facts-Crafting-Fallacies) | Ambiguous-name biographies combine facts about different people. FActScore and citation recall can overestimate their factuality; D-FActScore groups and entity-links facts. | This defeats the generic “true pieces, false whole” headline. Include entity-bound evaluation and explicit identities; new welfare examples alone add no scientific distinction. |
| [TRACE: Tree-Structured Reasoning for Multi-Table Multi-Hop Fact-Checking](https://aclanthology.org/2026.emnlp-main.968/) | Dependency-aware composition improves verification under gold and retrieved evidence. The novelty adversary inspected its construction appendix: refuted claims contradict evidence, while merely unsupported/unverifiable examples are excluded. | Gold extraction and structured composition are already precedents. Test genuine underdetermination as distinct from contradiction. This is the multi-table TRACE paper, not other systems sharing that name. |
| [Relevant Is Not Warranted / ForceBench](https://arxiv.org/html/2605.28044) | Fixed passages paired with supported versus strengthened claims expose failures of generic support judges; warrant-aware prompting helps. Its stated limitations exclude multi-hop synthesis and cross-source aggregation. | Include warrant-aware judging. Scope inflation and better caution prompts are not new by themselves; test compatibility between source records with the full claim fixed. |
| [Citation Failure / CiteControl](https://arxiv.org/html/2510.20303) | Separates response failure from citation failure and varies reasoning complexity, including multi-hop and intersection relations. Complex relations increase citation failures. | Citation completeness and relational complexity are established. Judge derivability, not just whether all relevant documents are cited. |
| [A Closer Look at Claim Decomposition](https://aclanthology.org/2024.starsem-1.13/) | Decomposition choices themselves change factuality scores; the paper proposes decomposition evaluation and an improved method. | Never obtain the headline by intentionally deleting the relation from a decomposed claim. Evaluate actual methods, preserve the complete claim, and inspect what each decomposition retains. |

Additional checks: [MEBench](https://aclanthology.org/2025.emnlp-main.77/) already measures comparative, statistical and relational cross-document QA. [Structured scientific evidence extraction](https://link.springer.com/article/10.1007/s00799-026-00449-9) measures binding and downstream aggregation errors. Neither “cross-document reasoning is difficult” nor “perfect extraction helps” would be a sufficient headline.

Access scope: primary abstracts, author repository descriptions and targeted methods/limitations were inspected by the lead and novelty adversary; TRACE appendix inspection was performed by the adversary. This was not exhaustive full-paper/code replication or a search of private unpublished work. Record further direct duplicates and amend positioning before substantial implementation.

## Minimum convincing experiment

1. **Prove the labels first.** Use a small finite-world generator with declared definitions. Supported means the claim holds in every admissible completion; refuted means its negation holds in every completion; not established means both are possible. Each underdetermined case must include two independently checked completion witnesses yielding opposite answers. Missing fields can still permit a bound that establishes the conclusion, so absence alone cannot determine the label. Reject inconsistent evidence sets instead of assigning them ordinary support labels.
2. **Start with one relation family.** Validate the measurement on denominator compatibility, then freeze any additional cohort/endpoint families before the main run. Balance directions and include nontrivial valid conversions and compatible comparisons. An always-abstain system must fail.
3. **Primary input is an oracle evidence table.** Entities and source facts are explicitly bound and correct. The evaluator sees all relevant facts and the complete claim, never the gold status or completion witnesses. Raw document packets provide a later transfer test. Comparing text and oracle tables changes representation, so the difference alone does not identify a pure extraction-mediated effect.
4. **Compare strong evaluators.** Include full-claim joint-source entailment, entity-bound verification, warrant-aware prompting, and an explicit comparison-check procedure. Include the original atomized metric as a diagnostic, not the sole competitor. Any adaptation of published methods must be labeled and checked against their original task; do not call an imitation a reproduction.
5. **Test the proposed intervention fairly.** It must identify which population, endpoint, period and denominator license the relation, then return supported/refuted/not established. Compare against a generic review procedure with matched information and model-call/token budgets. A deterministic checker operating on oracle records is a gold/sanity baseline, not evidence of a novel algorithm or deployable extraction system.
6. **Keep evaluation independent of generation.** Fixed candidate claims are the primary study, avoiding selection on a generator's errors. A secondary report-generation audit can measure naturally produced failures, with all outputs retained and human review. Do not estimate deployment prevalence from a balanced synthetic stress test.

Primary quantities to freeze: false support rate on underdetermined cases; false support rate on refuted cases; supported-case acceptance; and the paired intervention change in false support alongside its change in supported-case acceptance. Report a complete three-way confusion matrix. Claims of an acceptable trade-off require a prespecified valid-acceptance noninferiority margin, not a nonsignificant loss.

Use base-scenario clusters for uncertainty; seeds and paired variants are repeated observations. Hold out whole construction families where feasible, with genuinely unseen examples authored after development choices. Size the study for a meaningful effect or precision target using development variability, not a promise of significance. Model choices, total budget, minimum effects, multiplicity and the final analysis are unresolved; this is not a preregistration.

## What each result would teach

| Result | Interpretation and consequence |
|---|---|
| Strong evaluators accept unsupported comparisons even with correct extraction and identity | A compatibility-validation weakness remains beyond those known upstream errors, within the tested families. |
| Comparison checks reduce false support while preserving valid acceptance | Evidence for a useful intervention at its measured computational cost. Release the procedure and case-level results. |
| Improvement is matched by generic review or disappears with equal budgets | More review/computation is sufficient to explain the gain; do not claim a unique compatibility-check mechanism. |
| Errors disappear with entity binding or full-claim evaluation | Existing methods address this case class. Useful validation/replication, but the proposed new failure claim is unsupported. |
| Strong baselines already perform reliably with narrow uncertainty | A bounded robustness result. Do not keep changing examples until models fail. Publication value depends on coverage and precision. |
| Performance varies by relation type or works only on oracle tables | Locate a generalization boundary; report the extraction/representation limitation without treating it as proof of internal mechanism. |
| Labels remain ambiguous after independent review | Redesign or stop. Agent consensus is not ground truth. |

## Impact, feasibility and the animal-welfare connection

Potential users are developers of citation checkers and research assistants who need to decide whether extraction and entity binding are sufficient safeguards. A useful release would contain paired cases, formal label witnesses, evaluator adapters, an error taxonomy and reproducible costs. It can inform which checks deserve deployment testing; it would not establish real-world impact by itself.

Animal-welfare reports offer an application: counts, inspection populations, observation periods and outcome definitions may differ. Begin with transparent synthetic examples. Add real-source cases only after domain experts validate the exact comparison and permissible conclusions. Include a second domain if claiming generality. There is no claim that the experiment changes animal outcomes.

Engineering feasibility is favorable for the controlled core: no model training, browser environment or live web retrieval is required. Label validity, strong baseline implementation and realistic transfer are the difficult work. Reuse condition-independent budget/log/cache infrastructure only after design freeze; keep P3 manifests and outputs separate from P1/P2. No new model calls are authorized by this document.

## Five-role work allocation and final selection

- Novelty adversary: compare the precise experiment to the five nearest studies; search recent/public work and keep an explicit duplication log.
- Methodologist: freeze label semantics, causal contrasts, strong baselines, error trade-offs and analysis.
- Evidence specialist: audit completion witnesses; arrange independent human and animal-welfare review for real cases.
- Engineering lead: implement the frozen generator, evaluators and reproducibility checks, reusing shared infrastructure.
- Independent auditor: try to break labels, detect leaked gold information, reproduce metrics and test simpler explanations without authoring the evaluated labels.

**Recommendation: advance this narrower P3 through design and measurement validation. Do not build the broad composition proposal.** Meaningful novelty remains provisional, with a larger overlap risk than P1/P2's more-developed designs.

Choose the final two projects by: defensible contribution after final literature review; independent label validity; successful controls; adequate precision; robustness on untouched cases; reproducible artifacts; and a concrete community use. A precise null can pass. A large effect with weak labels cannot. Do not promise a publication or submit a second project merely to fill a slot.

Declare this three-candidate selection process before main runs. Use development pilots to assess measurement and contribution, not to select the largest effects. Publish the disposition of all three candidates, including nulls and abandoned designs, and retain every preregistered main-run result. Five AI roles improve throughput but do not substitute for independent human/domain expertise.
