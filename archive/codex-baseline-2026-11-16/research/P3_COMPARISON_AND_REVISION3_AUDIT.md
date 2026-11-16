# P3 comparison and revision-3 proposal audit

Evaluator review of the latest pasted amendments. No protocol implementation, model calls or scientific approval. The linked Claude files themselves have not been inspected; the proposals below are assessed from the user's pasted text.

## Portfolio clarification

The lead reviewer introduced Welfare Without False Certainty as a provisional replacement in this task. It was not a jointly frozen selection. P3 is now explicitly **an unselected slot with two alternatives under review**, not two additional projects. Both must center on animal welfare and satisfy the same contribution standard. Earlier portfolio wording overstated how settled that selection was.

## New primary-source finding

[Training Language Models to Be Coherent Decision-Makers, arXiv:2610.09164](https://arxiv.org/html/2610.09164), especially §§3.4–3.5 and Appendix B.4, already evaluates whether models recognize absent utility information. It removes one or both error costs, substitutes length-matched irrelevant information, and scores identification of missing costs; decisions are requested only for the complete condition. The study also trains and routes models for decision completeness and execution, reporting improved performance. This is a closer precedent than the description “values vary while evidence is fixed” suggests. Methods and prompt templates were inspected; no reproduction was run.

## Same contribution gate for both P3 alternatives

| Gate | Welfare Without False Certainty | Welfare Evidence Composition |
|---|---|---|
| Central question | Can a model identify when a welfare recommendation holds across declared admissible value policies, and when it depends on selecting one? | Can a model distinguish supported welfare comparisons from incompatible combinations of individually correct source facts? |
| Closest established work | Decision completeness in 2610.09164; [Boresta et al.](https://arxiv.org/html/2610.23673) on model preferences and robust optimization; [LISTEN](https://ijcai.org/proceedings/2026/403) on preference-based selection. | [Merging Facts, Crafting Fallacies](https://aclanthology.org/2024.findings-acl.160/) shows true facts forming a false whole; [TRACE](https://aclanthology.org/2026.emnlp-main.968/) studies multi-table reasoning; [FORCEBENCH](https://arxiv.org/abs/2605.28044) evaluates claim strength against evidence. |
| Remaining candidate contribution | Correctly distinguishing robust, conditional and tied recommendations under partially specified policies, rather than merely detecting an absent number. Needs meaningful welfare-policy validation. | A consequential welfare comparison that remains mishandled after entity, extraction, arithmetic and source-completeness controls, with meaningful transfer beyond existing composition tasks. |
| Strong comparator | Decision-completeness prompting and explicit sensitivity analysis; compare binary complete/missing-policy cases with partial-policy cases containing both robust winners and reversals. | Full-claim joint-source evaluation, entity-bound checking and explicit measurement compatibility review. Compare joined/split presentations without losing facts or adding distractors. |
| Positive finding | Unsupported universal claims persist under strong controls; sensitivity reporting reduces them while preserving warranted recommendations. | Comparison errors persist with correct extraction and computations; a targeted compatibility procedure improves them without excessive abstention. |
| Precise null | Existing decision-support methods already handle the tested partial-policy decisions; extra machinery is unnecessary within scope. | Existing joint-source evaluation already handles the welfare cases; separate composition machinery is unnecessary within scope. |
| Mixed finding | Arithmetic assistance alone resolves errors, or formal cases fail to transfer: narrow the contribution accordingly. | Oracle extraction removes errors: locate the issue upstream rather than claim a new composition failure. |
| Main alternative | Generic quantifier/optimization difficulty or an artificial admissible policy set. | Generic attention, entity binding or extraction difficulty. |
| Stop criterion | Only absent-utility detection or animal relabeling remains; or no defensible real decision/use case. | Only another domain instance of known composition failure remains, without validated measurement or consequential transfer. |
| Current verdict | **Investigate further; no implementation clearance.** New paper weakens broad novelty. | **Investigate/redesign; no implementation clearance.** Prior composition results weaken broad novelty; welfare specificity remains unestablished. |

The new paper does not by itself establish whether a model can reason over an admissible set whose members sometimes agree and sometimes reverse a ranking. That is a candidate boundary, not sufficient evidence of significance. Missing exact utilities do not always preclude a decision when dominance or bounds determine one. Conversely, finding such a formal difference is not enough to earn a paper without a meaningful application and strong comparator.

A welfare application may be valuable even when the mathematics generalizes. The requirement is a demonstrated evaluation need or consequential transfer, not mathematical uniqueness to animals. Neither candidate currently has the necessary independent welfare validation. Do not select one by title or reviewer vote.

## P2 amendments: direction approved, implementation unverified

- Remove the probability model and general scope instruction from the primary attribution stimulus. Scope-only C/C′ and outcome-data-only E are appropriate revisions.
- The old C contrast tested a combined scope-and-conclusion disclosure. It did not uniquely identify answer copying as the mechanism. Likewise, verdict-bearing E could be passed without interpreting counts; that establishes an assay weakness, not proof that models would copy.
- Sequential attribution then probability prevents later information reaching the earlier request, provided the first answer is stored immutably. However, the second answer can be anchored by the first answer. For separate measurements, prefer two fresh branches from the common dossier: attribution with neutral field definitions; belief with the stipulated probability model, without the attribution response in its history. If a sequential workflow is the target, retain it but interpret belief as conditional on that history.
- Adding a probability model changes the information available. Do not call differences between the branch outputs incoherence under identical evidence. The numerical belief task is a stipulated-model diagnostic, not real-world welfare calibration.
- C/C′ may explicitly disclose unassessed outcomes; that is legitimate scope information. Keep their substantive content identical. Removing response-category labels separates disclosure from an explicitly supplied conclusion.
- E must align with Q's metric, population, dates and comparator, with both signs. Complete records showing a lower observed rate support that descriptive comparison; they do not automatically establish a causal effect, statistical significance or overall welfare improvement.
- Preserve a genuinely established scoped-Q positive control if claiming a mitigation retains warranted acceptance.

## P1: moving agreement cases changes identification

For a binary amber/violet answer, excluding unknowns, disagreement implies:

| Initial model answer | Disagreeing user assertion |
|---|---|
| Correct | Incorrect |
| Incorrect | Correct |

Thus a disagreement-only sample makes user correctness inseparable from initial-answer correctness. Conditioning on a pre-pressure initial answer is not the same post-treatment bias as selecting voluntary checkers, but it changes the estimand and removes independent crossing within that initial state. Unknown initial answers require their own prespecified handling.

**Recommendation:** retain the full crossed assertion design for the primary randomized workflow question; report disagreement-only concession as a secondary analysis. If the desired primary question is specifically responses to challenges, use that population explicitly and interpret user-correctness moderation jointly with initial correctness. Do not promise a clean independent user-rightness effect from those restricted cells.

A three-way interaction must still be estimated directly if claimed. Shared initial-response generation and failure resolution must occur before branches, with actual initial responses preserved.

## Next decision package

Resolve P1's target population and P2's elicitation workflow, then inspect rendered examples, the contrast ledger and the generated candidate matrix together. For P3, compare a small set of concrete welfare decisions against the strongest known methods and obtain independent domain feedback before committing to a candidate. Neither further checklist drafting nor full harness construction resolves that contribution question.
