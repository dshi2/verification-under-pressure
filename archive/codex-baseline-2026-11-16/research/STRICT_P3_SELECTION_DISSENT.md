# P3 selection addendum: one candidate for the next gate

2026-11-16. **Recommendation: select welfare measurement-boundary displacement for the next design/label gate; do not yet implement or call it novel. Set Hidden Weights aside rather than developing both.** This is a recommendation to investigate one candidate, not a claim that it has passed the gate.

## Full-method check of Boresta et al.

I inspected the primary HTML of [Boresta et al., arXiv:2610.23673v1](https://arxiv.org/html/2610.23673), including Sections 3.2–3.3, 4.2–4.3, reported outcome definitions, and Appendix A.4 prompts. No repository execution was performed.

The paper **does not directly test disclosure or recognition of an underdetermined recommendation**. Its first experiment elicits importance scores and studies deliberation. Its second elicits pairwise choices, then evaluates consistency, order sensitivity and dominance compliance. Researchers infer uncertainty sets and solve mean-weight versus robust optimization outside the model. Appendix A.4 requests scores or short supporting arguments; the model is not asked whether all admissible value vectors imply the same choice. Thus Hidden Weights is not an exact duplicate. But weight sensitivity, dominance checks and robust optimization are already present, so these cannot be its novelty claims.

The remaining disclosure question is plausible. It is also difficult to make distinctly welfare-centered: linear trade-off mathematics can again become a generic decision benchmark with animal nouns. Welfare weights and cardinality need independent justification; otherwise the elegant gold labels concern an artificial rule rather than a consequential welfare decision. This is why I prefer the boundary candidate despite the surviving computational gap.

## Why the boundary candidate is stronger for this user's requirement

There is a documented animal-specific decision failure to anchor the experiment. Section 4.1 of the European Commission's [COM(2018)181](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A52018DC0181) describes how farm-mortality limits may encourage transport of potentially unfit birds rather than welfare culling, moving events outside the farm indicator. This motivates asking whether an AI reviewer mistakes improvement in a reported indicator for improvement over the animals' relevant observation period. It is not evidence of current frequency, measured AI behavior, or the comparative suffering caused by particular actions.

**Single question:** With a fixed identified cohort and an explicitly defined welfare-relevant endpoint, does an AI evidence reviewer distinguish a genuine reduction from displacement across farm/transport/slaughter reporting boundaries when the farm-level decline is the same?

This is more consequential than arbitrary missing denominators because the omitted stage is part of the documented incentive mechanism. It is more distinct from P2 because records can all be authentic and accurately reported; neither auditor authority nor verification labels need change. What changes is whether the monitoring boundary covers the animals and events needed for the target claim.

## The potentially fatal endpoint problem

Do **not** use 'all deaths by the end of slaughter' as welfare gold: routinely slaughtered cohorts eventually reach 100%, making the quantity useless. Do not sum deaths, emergency culls, pain episodes and transport injuries into an invented total. Humane euthanasia can reduce suffering; fewer farm culls can accompany worse welfare. Nor does a lower count of one adverse event prove overall welfare improved.

Before implementation, a welfare specialist must choose a meaningful endpoint and finite interval. For example, a narrowly described incidence of a specified severe condition before routine slaughter might be usable if observation and censoring are defensible. Alternatively, describe a mortality endpoint strictly as event-accounting evidence, with separate suffering/fitness facts and no overall-welfare conclusion. If no consequential endpoint survives this check, **drop this candidate**, rather than polishing the arithmetic.

## Minimum experiment and stronger baselines

- Match observed farm records between genuine-improvement and displaced-recording cases; disclose that downstream records legitimately differ. Include a third incomplete-follow-up state and a bounded-missing state where the conclusion is nevertheless identifiable.
- Give the full target claim, fixed cohort definition and exact observation window. Start with oracle-linked event histories, then use realistic records for transfer. Same records in prose versus tables test representation; supplying additional downstream data tests information.
- Reproduce a published selection/composition baseline on its original task before claiming extension. Compare full-claim joint-source grading, entity-bound checking, and a simple stage-complete event-accounting procedure. Include a calculator or precomputed arithmetic control.
- Require correct acceptance of real reductions, correct rejection of demonstrated non-reductions, and calibrated 'not established' only when missing observations can reverse the answer. Witness completions certify the latter. An always-abstain system fails.
- Primary claim is about support for the endpoint comparison, not treatment causation, overall welfare, or the model's hidden motives.

**Positive:** models endorse the apparent improvement despite supplied downstream evidence; matched stage-complete review prevents this while retaining valid conclusions. **Precise negative:** existing strong baselines already track the cohort correctly; report bounded robustness, not switch endpoints until errors appear. **Mixed:** errors vanish with oracle linking or arithmetic assistance; the main issue is upstream extraction/calculation, not a novel inference failure.

## Novelty threats still open

Selection bias and boundary accounting are established. [TRACE](https://aclanthology.org/2026.emnlp-main.968/) and [Merging Facts](https://aclanthology.org/2024.findings-acl.160/) remain important baselines. A further primary-source search found [CausalGame](https://causalgame.github.io/), whose public project description already features survivor-censored evidence and active experiments; it prevents a broad 'LLMs overlook survivors' headline. That page was inspected, not the full paper. The earlier Deng–Yan known-selection-rule work also needs a direct experimental comparison. No direct welfare reporting-boundary AI duplicate surfaced in this bounded search, which is not proof of absence.

**Final gate decision: investigate the welfare boundary candidate only.** It has the clearest welfare-specific pathway and a plausible objective assay, conditional on expert endpoint validation. Hidden Weights survives Boresta as a narrow question but is the weaker fit here. Neither is approved for substantial implementation, and this addendum is not the required completed 30-minute adversarial audit.
