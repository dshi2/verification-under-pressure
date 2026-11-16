# Adversarial novelty assessment

**Later review:** the [strict contribution assessment](STRICT_NOVELTY_GATE_v3.md) adds closer precedents, identifies scientific design flaws and supersedes readiness judgments here. This earlier screen is retained as history.

Working specification: [revision 2 protocol](PROTOCOLS_v1_revision2.md). This literature screen is not the condition specification. See the [latest P2 follow-up](P2_LITERATURE_FOLLOWUP_v2.md) for additional precedents and access limits.

Retrieved and assessed 2026-11-16. Agent 1; independent literature challenge, not an empirical result. Primary papers, public repositories and accessible Apart project pages were inspected. This is a targeted screen, not proof of global novelty. No private manuscript, private repository, hidden sprint submission or unpublished private result was accessed. Reported findings below are authors' findings, not replications by this team. The accompanying `sources.json` records access depth and verified locations.

## Decision

**Proceed with the narrowly frozen protocols and validation pilots for both projects. Do not claim either is the first study of checking under sycophancy or of verification labels affecting decisions.** Newly found close precedents make those broad claims untenable. The inspected sources do not implement either exact proposed causal contrast. A defensible contribution is a specific causal comparison and carefully validated application, rather than a new tool interface or animal-welfare topic alone.

For Project A, the new Self-Blinding precedent is particularly important: voluntary use of a debiasing tool and behavior after supplied tool output have already been distinguished. Our additional question is whether randomized, evidence-free insistence changes acquisition and use of *objectively decisive external records*. For Project B, prior Apart work already holds facts fixed and exchanges Verified/Preliminary labels. Our additional question is whether a truthful verification of P increases a false attribution that distinct Q was established.

## A. Verification Under Pressure

### Closest comparisons

| Source | Actual design and reported finding | Remaining distinction |
|---|---|---|
| [Correction or Manipulation?](https://arxiv.org/html/2610.36453v1), §§3–5 | Seven models face correct/incorrect challenges and pressure; a neutral double-check control separates reconsideration. Citations can increase concession and worsen discrimination. In the customer-support study, system messages supply verification status. | Its factual sources cannot be consulted; supplied policy verification is not voluntary factual evidence retrieval. Our neutral-versus-insistent manipulation must be crossed with acquisition regime. |
| [Self-Blinding and Counterfactual Self-Simulation](https://matanmazor.github.io/files/papers/christian2026blinding.pdf), §5.3, Appendix D; [repository](https://github.com/self-model/SelfBlindingLLMs/blob/main/sycophancy/README.md) | GPT-4.1 and Qwen receive access to blinded self-calls in ambiguous disputes. Effective spontaneous use is limited; supplied blinded outputs reduce but do not eliminate user-favoring responses. | Already distinguishes tool acquisition from response to available output. The output is a model's counterfactual judgment, not an objectively correct fact. No matched neutral/insistent challenge factorial was found. |
| [Beyond the Sycophancy Score](https://arxiv.org/html/2610.08840v1), §§3–4 | Controlled task regions, 13 pressure conditions, four turns and reasoning settings. Verification difficulty dominates its fitted yielding model; extra fallacious/emotional framing adds little beyond repetition. | Internal problem-solving difficulty is not randomized availability of an external decisive lookup. Its regression statistics are not power estimates for checking-rate effects. |
| [DIVA](https://arxiv.org/html/2610.32181v1), §§3–5 | Decision-value acquisition and stopping over costly checks, four domains and 20 models; reports reduced regret. | Information acquisition itself is established territory. Our added intervention is social insistence with evidence value/cost fixed. Cost extensions must not be marketed as independently new. |
| [When2Tool: LLM Agents Already Know When to Call Tools — Even Without Reasoning](https://arxiv.org/abs/2605.09252), [author project page](https://lilywenglab.github.io/when2tool/) | 18 environments with controlled tool-necessity difficulty; probes recover necessity signals from hidden states. Prompt-only and reason-then-act baselines trade fewer calls for accuracy losses. Access: abstract and author project page, not a full-paper review. | The inspected descriptions do not manipulate social pressure. Relevant alongside DIVA for choosing to check, but not evidence that the pressure interaction is already tested. Difficulty levels can inform a declared task revision after a floor failure; they do not justify changing one arm or tuning for a desired pressure effect. |
| [MCP Sycophancy Detector](https://github.com/syedairhakazmi/MCP-Sycophancy-Detector), README workflow | Public three-agent pipeline pressures an answerer, verifies cited strings against search and labels flips. Corrected pilot is reported; human gold labels are explicitly pending. | Search supports counterarguments and detection; the described design does not randomize answerer-initiated decisive lookup versus supplied identical records. It invalidates a broad 'first real-tool sycophancy experiment' claim. |

Additional overlap: [challenge-triggered verification gate](https://hexisteme.github.io/notes/challenge-triggered-reverification.html) is a public implementation note, not a controlled demonstration; it admits no head-to-head effect estimate and corrects initial keyword-only enforcement. [Monitorability Disposition](https://arxiv.org/html/2610.04914v1) varies optional/mandated reporting tools for sycophancy and other misbehavior; its tool reports behavior to monitors rather than retrieves factual evidence. Neither should be omitted from broad tool-use positioning.

### Precise knowledge claim

P1 candidate contribution: **pressure × (choosing to check vs. evidence supplied) × user right/wrong, with objective evidence**. The optional-versus-supplied comparison alone is not the novelty claim.

Existing studies establish answer yielding under pressure and failures to use debiasing/monitoring tools. Holding the claim, user expertise, information value, response opportunity and tool cost fixed, we test whether insistence changes relevant evidence retrieval, and whether externally delivering that record changes the effect of insistence on factual accuracy. This can inform whether guaranteed evidence delivery is useful in the tested workflow.

### Minimum experiment and interpretation boundaries

- Neutral versus insistent challenge crossed with optional lookup versus automatically delivered identical evidence, balanced correct/incorrect user assertions. Freeze wordings, turns, role and budgets. A neutral 'please double-check' arm can separate request-to-reconsider from insistence if the main neutral wording lacks that request.
- Use objective, fresh records; log actual relevant retrieval and record contents. Successful tool execution is not evidence of comprehension. Invalid outputs, failed lookup and unrelated lookup are distinct outcomes.
- Preserve matched initial answers/context. If initial answers are elicited, do not silently select only convenient successes. Stratify baseline correctness; truth of a hidden assertion is not information accessible to the model before checking.
- Primary contrasts: pressure effect on acquisition in the optional regime; pressure effect on accuracy in each regime; interaction between pressure and regime. Conditional comparisons among voluntary checkers are descriptive because checking is post-treatment selection.
- Remaining identification limit: revision 2 matches native tool-call/result format. Optional agents still make a preceding retrieval decision; supplied evidence bypasses it. Matching representation does not establish identical attention or eliminate every timing/selection explanation. Interpret regime effects as workflow effects, not a fully identified psychological mediator.

| Result | What it teaches |
|---|---|
| Less retrieval under insistence and accuracy loss attenuated with supplied records | Acquisition is a practically addressable contributor in this task; not proof of internal motivation. |
| Errors persist with supplied records | Guaranteed delivery is insufficient; evidence integration or response behavior remains a failure point. |
| More retrieval and better accuracy | Insistence can trigger protective checking, contrary to the proposed harmful direction. |
| Precisely negligible effects | Robustness within the tested range. Do not obscure tools or increase costs merely to manufacture failures. |
| Model/task heterogeneity | Report a boundary, with uncertainty; do not average away opposing effects. |

**Verdict: proceed to a validation pilot with the narrow claim.** Abandon broad 'first acquisition versus use' novelty. If exact neutral/insistent × objective optional/supplied comparisons emerge, reframe as a justified replication or redesign before confirmatory runs.

## B. Scope of Trust in animal-welfare assurance

### Closest comparisons

| Source | Actual design and reported finding | Remaining distinction |
|---|---|---|
| [Silence Is Endorsement](https://arxiv.org/html/2609.20211), §2, appendices | Holds action and authorization proposition fixed; varies absent claim, visible unverified marker, lost marker and verified marker. Status loss raises approval; ordinary summaries/memory can cause loss. | Our verified record remains intact and true but pertains to P, while erroneous assurance concerns Q. No compression is needed. |
| [Authority Bias](https://arxiv.org/html/2609.37616v1), §§3–5 | Wrong answers attributed to verified sources often override baseline-correct answers; source and user cues have different intervention effects. | Our verification statement is correct. We test transfer of its evidential status beyond its documented target, not a false source endorsement of Q. |
| [What Counts as Evidence?](https://arxiv.org/html/2610.12788v1), §3, Appendix C | Separates cue identification from use across reliability, lineage and temporal conditions; tests matched sham, restatement, ledger and weighting-principle interventions. | Its verified record directly establishes the target state. We test a correct record establishing a different proposition. Structured fields are already an intervention class, not headline novelty. |
| [Relevant Is Not Warranted / ForceBench](https://arxiv.org/html/2605.28044v1), §§3–5 | Fixed passage with supported versus locally strengthened claims on relation, modality, scope, time and precision; generic support judges often miss strengthening, improved by explicit warrant checks. | Under-warranted claims are already measured. Our causal treatment is truthful verification status of P with substantive dossier content fixed. A force-aware rubric is a necessary strong baseline. |
| [Does the word “verified” steer what action an AI model favors?](https://apartresearch.com/sprints/projects/does-the-word-verified-steer-what-action-an-ai-model-favors-5taz), public Apart project | Twenty-four scenarios swap Verified/Preliminary labels with identical facts. Some models favor the verified action despite larger prescribed numerical weight elsewhere. | Very close status-control precedent. It does not test whether genuine P-verification is falsely attributed to distinct Q. Merely observing a label effect is insufficient novelty. |

Other inspected work: [ClaimReceipt](https://arxiv.org/abs/2609.01992) binds evidence to evaluation claims and checks sufficiency/coverage, rather than estimating behavioral spillover. [OverclaimBench](https://arxiv.org/abs/2609.20812) checks claims of work against transcripts, relevant to report-vs-process measurement. [Fluent and wrong](https://link.springer.com/article/10.1007/s43681-026-01478-5) discusses a real-anchor halo from exploratory single-author observations; it does not provide our randomized contrast. Do not claim the intuition of real anchors legitimizing unsupported content is new.

### Precise knowledge claim

Existing work shows source-status influence and overstatement of evidence. We test whether truthful verification of P, with its contents preserved, causally raises false attribution that distinct Q has been demonstrated. Animal-welfare assurance supplies consequential, realistic scope boundaries, but its inclusion alone is not novelty or proven impact.

### Minimum experiment and interpretation boundaries

1. Same facts about P and same candidate Q in all arms. Neutral baseline has no verification status; an explicit UNVERIFIED baseline is additional, not the only baseline (otherwise the contrast mixes verification uplift with unverified discount).
2. Genuine narrow verification of P; matched unrelated successful check; scope clarification stating Q was not assessed. If claiming format benefit, include equivalent-scope prose and structured versions.
3. Direct verification supporting Q and direct verification contradicting Q as positive and negative controls. Counterbalance checked claim identity/valence, display order and answer position.
4. Primary outcome is whether the agent attributes verification/demonstration to Q beyond the record. Changes in confidence, recommendations or general expectations are secondary and can be rational.
5. Include plain P-to-Q entailment without verification cues, and a force-aware evidence rubric. These distinguish incremental status effects from ordinary reading/entailment failures and generic checking assistance.

Strongest alternative: verification of P can legitimately increase confidence in correlated Q, or communicate broader source reliability. Avoid counting this as error: ask what the specific audit established, specify the audit's covered facility/population/time/measure, and score 'not established' separately from 'false'. For realistic cases, domain review is needed because practices can provide indirect evidence of outcomes. Do not assert that all welfare certification ignores outcomes.

| Result | What it teaches |
|---|---|
| P-verification raises false Q-attribution relative to neutral and unrelated-check arms | A specific cross-claim scope-transfer effect; not proof of a unique cognitive mechanism. |
| All successful checks raise false Q-attribution similarly | Broad verification/status cue or task demand, not specificity to P-to-Q linkage. |
| Explicit scope reduces errors without reducing valid-Q acceptance | Useful scope communication in this workflow. Format superiority requires the equivalent-prose control. |
| Errors already high without verification and no incremental effect | Ordinary evidence-scope failure, already close to ForceBench; do not relabel it spillover. |
| Precise null with working valid/invalid controls | A robustness boundary; a valid finding, not automatic project failure. |
| Clarification rejects valid Q too | Blanket skepticism trade-off; not an unqualified mitigation. |

**Verdict: proceed to deterministic case validation and a pilot.** The first confirmatory claim must remain the incremental status-to-other-claim effect. If welfare cases cannot be labeled independently, retain them as illustrative/application cases and use transparent synthetic records for causal claims; do not portray agent-generated labels as expert validation.

## Search coverage and remaining uncertainty

Queries included sycophancy + tool use/checking/verification, verification + scope/spillover/halo, animal welfare + verification + LLM, and site-limited Apart/GitHub searches. Primary full-text sections were inspected for the core sources above. Public code READMEs were inspected, not independently executed.

The current [sprint page](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15) states that submissions remain hidden until judging; there is no current-submission novelty clearance. Earlier Apart entries were searched and the verified-label project above inspected. Sprint co-designer Alex Csaky's [OLD-syco-lingual repository](https://github.com/alexcsaky/OLD-syco-lingual) was inspected: it concerns multilingual sycophancy, not our specific contrasts. This was a targeted contributor check, not a full audit of every mentor/judge repository.

Before submission, repeat targeted searches using the actual final design and publish a direct comparison table. Date/version anomalies in web-rendered paper metadata should be resolved against publisher/arXiv metadata before bibliography export; no novelty claim here relies on chronological priority. A newly discovered exact duplicate is grounds for redesign or a deliberately justified replication, regardless of implemented code.
