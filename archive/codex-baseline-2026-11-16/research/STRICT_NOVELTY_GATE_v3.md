# Strict contribution review — three candidates, two possible submissions

**Subsequent update:** see [P3 comparison and revision-3 proposal audit](P3_COMPARISON_AND_REVISION3_AUDIT.md). P3 selection is unresolved; the recommendation below was provisional. The newly inspected decision-completeness study narrows its candidate contribution. The update also identifies a P1 disagreement-only identification issue and P2 measurement-order considerations.

16 November 2026. This is a research-selection review, not a protocol freeze, preregistration, or report of model results. The latest constraint is that **P3 must center on animal welfare**. Software already written earns no credit toward scientific readiness.

| Candidate | Decision from this review | What must change |
|---|---|---|
| P1 — Verification Under Pressure | **Redesign the manipulation, then validate** | Remove the neutral-only deliberation instruction; validate pressure and retrieval opportunity. |
| P2 — The Scope of Trust | **Redesign the measurement controls, then validate** | Separate scope disclosure from supplied answer labels; test outcome evidence without an explicit verdict. |
| P3 — Welfare Without False Certainty | **Investigate further; proposed replacement for generic composition** | Establish realistic welfare decisions and conditional labels with domain expertise; test the remaining disclosure question against close decision-support research. |

None has passed the full gate. P1 retains the clearest experimental contrast. P2 has a plausible, narrower contribution than previously claimed. P3 is a candidate for investigation, not a promised third paper. Generic Evidence Compatibility is no longer the proposed standalone P3.

## P1 — Verification Under Pressure

**1. Closest studies and their experiments.**

| Verified primary source | Existing experiment/finding | Remaining difference |
|---|---|---|
| [Christian & Mazor: Self-Blinding](https://matanmazor.github.io/files/papers/christian2026blinding.pdf), [released task](https://github.com/self-model/SelfBlindingLLMs/blob/main/sycophancy/README.md) | Ambiguous disputes, voluntary self-simulation and responses to blinded judgments; spontaneous checking and deference are distinct measured behaviors. | Optional versus supplied evidence is already known. Our candidate adds randomized social pressure and objectively decisive records. |
| [Correction or Manipulation?](https://arxiv.org/html/2610.36453) | Correct/incorrect challenges, pressure and reconsideration; verification-state compliance in an account-support task. | Pressure × user correctness is already known. Randomized evidence delivery is the additional comparison. |
| [AgentDecept](https://arxiv.org/html/2610.39377) | Pressure variants and pressure-free counterparts; some tasks have checkable user expectations and accessible API records. | Tools, pressure and objective records already coexist. No optional-versus-supplied intervention was found in the inspected design. |

Also inspected: [Is Sycophancy a Form of In-Context Updating?](https://arxiv.org/html/2610.28325) uses forced native lookup calls. Tool provenance is not our novelty.

**2. Contribution.** A workflow-intervention interaction: **pressure × choosing to check versus evidence supplied × user right/wrong, with objective evidence**. Existing work establishes pressure-sensitive updating and tool-related verification behavior. Our proposed randomization asks whether guaranteed delivery changes the pressure penalty, while separately observing acquisition in the optional workflow. It does not establish a cognitive mediation mechanism.

**3. Why it matters.** A system designer needs to know whether making evidence available is enough, whether delivering it helps, or whether erroneous final answers persist after delivery. These imply different remedies.

**4. Minimum experiment and baseline.** One validated pressure treatment versus neutral × optional versus supplied evidence × correct versus incorrect user. Cache the same initial answer across paired branches; use identical tools and canonical tool-result formatting. Analyze every randomized trial, including failures to check. Use the same reconsideration request in every arm, then vary only the intended pressure addition. Current code instead requests careful reconsideration only in neutral; a retrieval difference is therefore confounded.

The neutral/no-tool registry arms are **internal controls, not reproductions** of prior studies. Before the strict gate can pass, specify and run a small separately reported bridge using a released factual-challenge subset from *Correction or Manipulation?*, preserving its prompts/readouts, then add the objective-record workflow. Record all adaptations; do not pool incompatible outcomes. This bridge is proposed, not implemented.

**5. Informative results.** Lower optional retrieval plus a smaller pressure penalty under supplied evidence supports delivery as a remedy in this task. Persistent supplied-arm errors show delivery is insufficient. More checking under pressure challenges the harmful-direction hypothesis. A precise null is informative only with a working pressure manipulation and a nonfloor neutral check rate. A failed manipulation or wide interval is inconclusive, not robustness.

**6. Claim and alternative.** Claim changes in relevant retrieval and evidence-consistent final answers under these workflows. Do not claim internal evidence use or a natural indirect effect through checking. Timing, attention and who initiated the call remain possible procedural explanations. Irrelevant-authority cues cannot establish responses to genuine expertise.

**7. Verdict: REDESIGN, then diagnostic validation.** Preserve the question; repair the prompt contrast before live data collection. The current offline test suite does not test this construct-validity problem.

## P2 — The Scope of Trust

**1. Closest studies and their experiments.**

| Verified primary source | Existing experiment/finding | Remaining difference |
|---|---|---|
| [False Containment — past Apart submission](https://apartresearch.com/sprints/projects/false-containment-measuring-the-evidence-required-to-verify-autonomous-ai-incident-resolution-n5i5) | Resolved/unresolved security cases and cumulative evidence. Four exploratory stress cases show narrow checks accompanying false confidence in overall resolution. | Broad narrow-check-to-broad-confidence failure is already observed. We need the incremental effect of truthful verification status with the underlying practice fact fixed. |
| [Silence Is Endorsement](https://arxiv.org/html/2609.20211) | Authorization-status loss changes approval; an appendix compares preservation through prose and structured formats. | Our target is transfer from checked claim P to distinct claim Q, with P's status preserved. Format alone is not novel. |
| [Who Verifies the Tools?](https://arxiv.org/html/2610.32110) | Incomplete versus repaired tool-scope descriptions alter overclaims about fixed outputs. | Scope clarification already has precedent. The primary contribution must be B−A and B−D1, not simply C−B. |

Additional close controls: [Authority Bias](https://arxiv.org/html/2609.37616) and [Apart's verified/preliminary label experiment](https://apartresearch.com/sprints/projects/does-the-word-verified-steer-what-action-an-ai-model-favors-5taz).

**2. Contribution.** Does truthful verification of a fixed practice fact P cause an AI to attribute verification to a distinct, unchecked animal-based outcome Q? Compare A (P reported), B (P verified) and D1 (P reported, unrelated fact verified). This is a causal behavioral comparison, not proof of an authority mechanism. Verification adds epistemic information about P; it does not leave all information unchanged.

**3. Why it matters.** An assurance reader can reasonably become more optimistic after learning a practice was implemented while still being wrong to say the outcome was audited. The project separates those judgments. It cannot establish that all welfare labels lack outcome assessment or that the study improved animals' lives.

**4. Minimum experiment and baseline.** Keep P wording, issuer, facility and target Q fixed across A/B/D1. Add scope-only C and genuine outcome data E with both supporting and contradicting cases. Retain C′−C only as a secondary format contrast with identical meaning. Add an in-scope, genuinely established Q under the clarification procedure before claiming it preserves warranted acceptance.

Current implementation teaches the scope rule in every system prompt; C/C′ also provide `not_established` answer categories, and E explicitly says `supports/refutes Q`. These are legitimate tests of a scaffolded reader, but cannot isolate ordinary scope errors, clarification alone, or independent interpretation of outcome data. Future revision should separate minimal schema instructions from an explicit-rule safeguard, and scope-only disclosure from a supplied conclusion. E needs a facts-only counterpart.

For the strict historical baseline, preregister a compact reproduction of the released same-claim status task from *Silence Is Endorsement*, followed by a separately scored distinct-claim bridge. A/V in our current dossiers do not automatically reproduce that experiment. This work remains open.

**5. Informative results.** B>A and B>D1 supports content-dependent verification-attribution spillover. B and D1 equivalently above A supports nonspecific status influence; equivalence needs a margin and interval, not two nonsignificant tests. High A with no incremental B effect is ordinary evidence-scope failure, not new verification spillover. A precise null with functioning positive/negative controls bounds the concern. C helping only when it supplies the answer exposes a limitation of the mitigation.

**6. Claim and alternative.** B>D1 shows that what was checked matters. Topic-sensitive authority, inference or attention may carry the effect. Belief changes are not attribution errors. Use a masked response-extraction pass, then deterministic comparison with a separate gold table: giving a grader the verified-claim table can reveal the condition class despite removing the arm name.

**7. Verdict: REDESIGN measurement controls, then validate.** The narrow question survives the inspected comparisons, but broader novelty claims do not. Welfare expertise and independent interpretation labels remain necessary.

## P3 — Welfare Without False Certainty

**1. Closest studies and their experiments.**

| Verified primary source | Existing experiment/finding | Remaining difference |
|---|---|---|
| [Boresta et al.: LLM multi-criteria decisions in healthcare](https://arxiv.org/html/2610.23673) | Elicits weights and pairwise choices; examines order/role effects; researchers construct uncertainty sets and compare robust with average-weight optimization. | The inspected methods do not test whether the model correctly tells a user that a recommendation is underdetermined by the declared values. Weight sensitivity and robust optimization are already known. |
| [LISTEN to Your Preferences](https://ijcai.org/proceedings/2026/403), [paper](https://ijcai.org/proceedings/2026/0403.pdf) | Utility refinement and tournament selection for flights, products and exam schedules, evaluated against human preferences; utility assumptions affect performance. | Selecting according to preferences is known. Our proposed endpoint is correct disclosure of what the evidence plus allowed trade-offs do and do not determine. |
| [AnimalHarmBench](https://arxiv.org/abs/2503.04804) | Animal-related advice and trade-off scenarios, evaluated for harmful implications with validated grading procedures. | Another moral-preference benchmark adds little. Our labels would concern conditional validity, not agreement with a preferred ethical answer. |

Welfare grounding: [Sandøe et al., 2019](https://www.ufaw.org.uk/downloads/sandoe-2.pdf) identifies ethical and transparency problems in aggregating welfare indicators. This link is the **one-page abstract**, not the full paper. [HarvestBench](https://arxiv.org/abs/2609.04444) already measures costly choices to avoid killing animals; [MANTA](https://arxiv.org/abs/2605.16301) already studies welfare values under pressure. Neither is the proposed question.

**2. Contribution.** Existing welfare scholarship establishes that multiple outcomes require explicit value judgments; AI decision research studies preferences and robust optimization. The candidate gap is whether an assistant **accurately distinguishes a welfare recommendation valid across the declared admissible trade-offs from one that requires choosing a particular trade-off**, and can disclose that distinction without refusing clear cases. This is a proposed measurement/contribution, not a verified first-ever claim.

**3. Why it matters.** Two interventions can reduce different forms of suffering. A confident recommendation may conceal the ethical choice needed to rank them. A useful output would expose that choice to welfare assessors while still supporting a conditional decision. The scientific question concerns warranted certainty in welfare advice, not making an AI more agreeable to advocates.

**4. Minimum experiment and baseline.** Complete, stipulated animal-based outcome evidence; one species; two feasible interventions; explicit allowable decision policies. Include (a) one option better under every allowed policy, (b) different allowed policies selecting opposite options, and (c) a legitimate preference clarification resolving the conflict. No verification badges or social pressure. Score unsupported uniqueness, valid conditional recommendations and unnecessary abstention separately.

For a transparent diagnostic example only, let A have (10 severe, 40 moderate) episodes and B (20 severe, 10 moderate), with duration fixed and a *stipulated* loss `r × severe + moderate`, `2 ≤ r ≤ 5`. A is preferred for r>3, B for r<3, and they tie at 3. This proves the conditional label; it does **not** validate that loss model as true welfare or those weights as ethical consensus. Dominance cases prevent an always-cautious answer from succeeding.

Historical baseline: reproduce Boresta's published pairwise-choice procedure and readouts in a separate panel, then add the declared-policy/disclosure endpoint. Compare a strong assistant explicitly separating factual and value assumptions with a policy-enumeration procedure at matched resource budget. Include an arithmetic-assisted diagnostic so calculation failure is not misnamed moral overconfidence. Prior-setting reproduction and these new arms are not implemented.

**5. Informative results.** Unsupported uniqueness despite complete facts and easy calculations supports a specific disclosure failure. An intervention is useful only if it also retains warranted decisions. A precise null with strong baselines establishes a boundary and may show extra machinery unnecessary. Errors disappearing with precomputed arithmetic locate a calculation problem. Success on formal cases but failure on expert-reviewed cases limits transfer; it is not evidence of an internal moral defect.

**6. Claim and alternative.** The strongest possible claim is reliable or unreliable disclosure of value-dependence in the tested welfare decisions. Ordinary quantifier errors, unclear requests, extra computation and artificial utility assumptions are major alternatives. A model may legitimately choose an option if it discloses its additional assumption; choosing is not itself the error. Keep ties separate from unique robust winners. Realistic cases need independent welfare-science review of indicators, duration and overlapping outcomes, plus welfare decision/policy expertise on feasible choices and admissible trade-offs. Disagreement about aggregation rules is distinct from uncertainty about weights within one rule. Real-source cases must retain empirical uncertainty rather than pretend their outcomes are complete. No universal welfare score or real-world benefit is established by a toy solver.

**7. Verdict: INVESTIGATE FURTHER.** This is the proposed welfare-centered replacement, not authorization to build a full experiment. A welfare setting can be a meaningful contribution if it establishes consequential transfer or a validated measurement; animal nouns alone cannot do that. Drop this as a standalone submission if only a generic mathematical exercise remains.

## Adversarial disagreement and coverage

Three delegated reviewers examined novelty, methodology and P3, with the lead reviewing sources and adjudicating. They were not unanimous about P3. The P3 adversary ultimately preferred detecting displacement across farm/transport/slaughter reporting boundaries. That has a documented motivation, but still lacks a defensible primary endpoint: all deaths through routine slaughter becomes trivial, and fewer welfare culls need not mean less suffering. The lead provisionally favors the disclosure candidate because it has a clearer conditional scoring target and is more distinct from P2. Both require welfare expertise; neither is novelty-cleared. The displacement alternative is parked, not a fourth active project.

Public checks covered the sprint page, indexed past Apart projects, selected public repositories and recent preprints. Current submissions are hidden; workshop and mentor-repository coverage is partial. Source-access depth and the independent objections are recorded in the accompanying review files. Absence from these searches is not proof of absence.

The checklist's literal **30-minute independent attack on a finalized one-page design has not been completed**. These drafts already fail earlier gates; do not mark them passed. That timed review remains required after a single revised design per candidate is written and before substantial new condition implementation. Human/domain validation cannot be replaced by agent agreement.

## Portfolio and execution rules

1. Preserve revision 2 as an immutable diagnostic baseline; make scientific changes in a new version. This review changes readiness, not historical files or results.
2. Treat all inspected fixture families as development data. New confirmatory cases must vary substantive reasoning structures, not merely species or registry names. Seeds repeat items; they do not multiply independent cases.
3. Separate attribution from belief; stipulated-probability accuracy from empirical calibration; content changes from format; descriptive comparison from causal treatment effects.
4. Freeze primary contrasts, practical/equivalence margins, clustered precision targets and handling of failures before main runs. No paid or confirmatory run is authorized by this review.
5. Select the final two for contribution, validated measurement and informative evidence. Do not select on the largest effect or statistical significance. Preserve and disclose all main-run outcomes, including nulls and reasons a candidate was not submitted.

Engineering stays with reusable infrastructure until the revised designs clear their gates. No new experiment was run for this review.
