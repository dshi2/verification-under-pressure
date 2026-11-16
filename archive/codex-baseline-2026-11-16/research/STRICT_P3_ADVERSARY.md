# Strict P3 novelty adversary: welfare must be the research question

Date: 2026-11-16. Reviewed `outputs/research/P3_EVIDENCE_COMPATIBILITY_CANDIDATE.md` as a proposal, not authority. This is a focused independent adversarial screen, not a completed, instrumented 30-minute attack; no such duration is claimed. No code, frozen protocol, or experiment output was changed.

## Verdict

**REDESIGN the current P3; do not implement it as written.** Its denominator/endpoint compatibility experiment could be useful, but the current document explicitly treats animal welfare as an application. Its fundamental inference survives replacing animals with widgets. That fails the user's stronger requirement that P3 answer a consequential animal-welfare question, rather than simply apply a generic error benchmark to that domain.

The strongest replacement to investigate is **Welfare Without Hidden Weights**, restricted to one question:

> Given complete, accurate animal-based outcome data, does an AI correctly distinguish a welfare ranking that holds under all declared admissible value judgments from a ranking that depends on choosing particular trade-offs?

**INVESTIGATE FURTHER, not proceed**, for this replacement. A very close October 2026 healthcare decision paper already studies LLM-derived preference weights and robust optimization. The potentially remaining contribution is the epistemic status of a welfare recommendation under declared value uncertainty, not discovering that values matter, estimating moral weights, or inventing multi-criteria optimization.

## Five nearest sources for the replacement

1. **Boresta et al., [On the possibilities and limitations of LLM-based multi-agent systems for multi-criteria decision-making in healthcare operations management](https://arxiv.org/abs/2610.23673), October 2026.** Agents rate criterion importance for outpatient schedules and choose between emergency-department configurations. Explicit preferences vary with operating conditions and role; deliberation can erase role differences. Pairwise choices are strongly affected by presentation order. Robust optimization accounting for preference uncertainty often selects different actions from mean-weight optimization. **Closest computational threat:** generic “LLMs have implicit weights” and “weight uncertainty changes recommendations” are already addressed. Access: primary abstract, not full-text clearance. Must inspect methods and public code before authorizing the replacement.

2. **Sandøe, Corr, Lund & Forkman, [Aggregating animal welfare indicators: can it be done in a transparent and ethically robust way?](https://www.cambridge.org/core/journals/animal-welfare/article/aggregating-animal-welfare-indicators-can-it-be-done-in-a-transparent-and-ethically-robust-way/EAD62DD23305804EC1586497292955E6), Animal Welfare 2019, 28:67–76.** This is conceptual/ethical analysis, not an LLM experiment. It distinguishes within-animal from across-animal aggregation and argues that Welfare Quality aggregation can mask important problems and lacks transparent expert weighting. **Implication:** hiding severe harms through aggregate scores is an established welfare concern; do not claim its discovery. The publisher migration date says 2023, but the [journal abstract PDF](https://www.ufaw.org.uk/downloads/sandoe-2.pdf) verifies the 2019 publication. Access: abstract, not full paper.

3. **Day et al., [Optimising the selection of welfare indicators in farm animals](https://doi.org/10.3389/fvets.2025.1661470), 2025.** Builds a 382-indicator dataset across seven farm species, implements greedy and enhanced selection, and tests weighting scenarios and sensitivity. The enhanced algorithm finds global optima in their cases; user priorities affect selected indicators. **Implication:** computational selection and sensitivity analysis already exist in welfare practice. Our novelty cannot be a weighted optimizer. This is a practical source for an audit-setting task, though choosing indicators is different from ranking interventions on measured outcomes. Access: primary abstract and targeted methods/discussion.

4. **AnimalHarmBench, [What do Large Language Models Say About Animals?](https://arxiv.org/html/2503.04804v4), FAccT 2025.** Uses 1,850 curated Reddit questions and 2,500 synthetic questions covering 50 animal categories and 50 ethical scenarios. Scenarios already include practical trade-offs and willingness to pay; model judges assess harm implications, with self-preference correction. Results vary by model, species and scenario. **Implication:** an animal-welfare advice or trade-off benchmark is not new. We need explicit distinction between a conditional recommendation and a uniquely warranted one, with mathematical conditional-validity labels rather than whether a grader approves the moral preference.

5. **HarvestBench, [Measuring Whether LLM Agents Will Pay to Avoid Killing Animals](https://arxiv.org/html/2609.04444), September 2026 preprint.** Nine models make 7,201 decisions in a farm simulation with a priced option to avoid animals, alongside rock and hay controls. Kill rates and price sensitivity differ substantially; moral briefing strongly affects behavior. Scoring uses environment events. **Implication:** objective animal-related decisions, priced moral trade-offs and action-versus-talk are already studied. Our proposed target is recognizing when the evidence plus declared ethical constraints identify a recommendation, not measuring willingness to sacrifice animals.

## Required adjacent checks

- **[MANTA](https://arxiv.org/html/2605.16301)**: 1,088 five-turn conversations; seven-model study; moral sensitivity and stability under five pressure types, with species-by-pressure differences. It already covers welfare values under pressure. Keep pressure out of P3 to avoid both MANTA and P1 overlap. Access: primary abstract and methods outline; no claim of full-paper reproduction.
- **[SpeciesismBench / Large language models exhibit speciesist bias against animals](https://www.nature.com/articles/s41467-026-72297-9)**: the published abstract reports 1,009 items, psychological comparisons, and generated rationalizations. Reports devaluation of animals, especially farmed animals. Do not recycle the older 1,003-item description as the final publication count. A species-name swap or asymmetry alone is insufficient novelty. Access: published primary abstract and discussion excerpts.
- Public unfinished work also matters: **[CrueltyBench](https://github.com/CompassionML/crueltybench)** tests implicit cruelty implications plus overreach controls; **[AWB-Africa proposal](https://manifund.org/projects/animal-welfare-benchmark-for-transformative-ai)** proposes expert-validated welfare trade-offs, context transfer, and welfare-constitution interventions. These are not verified completed experimental duplicates, but prevent claiming the general project area is empty.
- The old composition proposal remains threatened by **[Merging Facts, Crafting Fallacies](https://aclanthology.org/2024.findings-acl.160/)** and **[FORCEBENCH](https://arxiv.org/html/2605.28044)**. Animal relabeling does not erase those precedents.

## What exactly is new, if the gap survives?

Existing welfare research establishes that aggregating several outcomes requires contestable trade-offs. Existing AI benchmarks measure which welfare preferences models express or enact; recent healthcare work audits elicited weights and robustness. The candidate additional question is whether an assistant **marks a recommendation as value-dependent when the stipulated admissible values select different actions, while recognizing genuinely robust rankings**.

The target user is a welfare assessor comparing two feasible interventions for a single species, given animal-based effects on two explicitly defined harms. All outcomes are supplied as known for the diagnostic task; this is not a prediction, overall welfare measurement, or proof an intervention causally works. A failure could let the model present one ethical choice as though welfare observations uniquely required it. Community value would be an expert-reviewed test and a recommendation-disclosure procedure, not claimed animal lives improved.

This differs from P2: all observations are established and no verification badge is manipulated. P2 concerns the scope of evidence; this candidate concerns the additional value assumptions required to turn evidence into a preference.

## Minimum convincing comparison and known baseline

Start with two interventions, two adverse animal-based outcome dimensions, one species and a declared admissible set of nonnegative trade-off weights. Use both a dominance/robust-ranking case family and a trade-off family in which two allowed weight vectors choose opposite interventions. Also include cases where an explicit, legitimate narrowing of the allowed weights resolves the ranking. Do not silently equate ordinal welfare scores with cardinal utilities; the scoring rule is a stipulated decision rule, not a scientifically validated universal welfare scale.

The baseline must include (a) a faithful documented implementation or reproduction of the healthcare paper's explicit-versus-implicit preference elicitation setting, after inspecting its full methods; and (b) a strong full-information assistant instructed to distinguish factual and normative premises. A generic 'be cautious' control should match the proposed value-robustness procedure in information and computation. An exact solver supplies gold robustness and witness weights; it is a known mathematical tool, not our novel algorithm.

Measure unsupported unconditional recommendation separately from the selected action. A model can legitimately choose one option while explicitly stating the trade-off it adopts. It should fail only if it misstates the assumptions, claims uniqueness where none follows, violates declared constraints, or refuses robust cases. Include conditional recommendations with verified thresholds as successes. Do not score all recommendations in a trade-off case as wrong.

For any presentation experiment, preserve every outcome and weight constraint. Giving an aggregate-only arm less outcome information tests information loss, not format. Severe-harm masking is a possible later extension; do not add it as a second headline in the minimum study.

## Outcomes and alternatives

- **Positive:** false unconditional claims persist with exact facts, easy arithmetic and strong baselines; a value-robustness procedure reduces them without losing valid decisions. This supports a specific reliability improvement in welfare advice under declared value uncertainty.
- **Negative, precise:** strong baseline distinguishes robust and conditional cases reliably. This bounds the concern in the tested setting; do not move to harder cases solely to obtain errors. Community value would require breadth and precision, not a forced failure story.
- **Mixed:** cases with explicit narrow weights work but open weight sets fail. This locates difficulty in reasoning over admissible sets; does not show hidden speciesism. Intervention helps only when computation increases: extra reasoning is sufficient explanation. Cautious controls match it: special framework unnecessary.
- **Strongest simpler explanation:** ordinary optimization/quantifier failure, or interpreting 'recommend' as asking the model to express its own values. Address with explicit output semantics, precomputed arithmetic controls and a small structurally identical neutral task. A neutral diagnostic is a control, not making P3 a generic benchmark with a welfare slice.

The strongest claim supported would concern correct disclosure of value-dependence in the specific welfare decision tasks. It would not establish moral superiority, infer internal values, validate an overall welfare metric, or demonstrate actual welfare gains.

## Gate status

**Current compatibility proposal: REDESIGN. Replacement: INVESTIGATE FURTHER.** Before substantial implementation, complete the healthcare paper comparison, inspect welfare aggregation full text, secure independent welfare-expert validation of the decision and admissible assumptions, and conduct the required timed adversarial review of a single finalized candidate. No AI-agent consensus substitutes for those steps. If only the species/domain nouns distinguish the final experiment from the closest comparator, drop it as a separate submission.
