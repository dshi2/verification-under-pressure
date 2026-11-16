# Novelty-and-contribution assessment (pre-implementation) — Nov 16, 2026

Stage: **targeted adversarial check** (stage 2 of 3). Stage 3, the final positioning check against the findings we actually get, is due before submission.
Every link below was found and read (abstract or full text) in this session. Anything unverified is flagged.

## ⚠️ CORRECTION (round 4): the "could not be found" list below was WRONG
Fetched directly by arXiv/ACL ID, all of these exist. My search index had missed papers from Aug–Oct 2026.
- Correction or Manipulation? — https://arxiv.org/abs/2610.36453
- FactRot (EMNLP 2026) — https://aclanthology.org/2026.emnlp-main.2472/
- Big-Big-SycoBench — https://arxiv.org/abs/2610.15634
- Understanding before verifying — https://arxiv.org/abs/2608.30145

"Not found in search" is a limit of the search, not evidence that a paper was fabricated. Still unverified: LRT-ReviChain.

## (Superseded) original citation-hygiene list
These titles in the other plan could not be found at the time. **Do not cite them** unless someone finds the real paper:
- "Correction or Manipulation?" → nearest real paper: Knowing but Not Correcting, https://arxiv.org/abs/2605.05957
- "FactRot" → nearest real paper: LLM as a Broken Telephone, https://arxiv.org/abs/2502.20258
- "Understanding before verifying" → nearest real paper: What Do Claim Verification Datasets Actually Test?, https://arxiv.org/abs/2604.01657
- "Is Sycophancy a Form of In-Context Updating?" → the real title appears to be "Sycophancy as Miscalibrated In-Context Updating", https://neurips.cc/virtual/2026/166036
- LRT-ReviChain: not checked.
- Big-Big-SycoBench: only news coverage found (https://officechai.com/ai/big-big-sycobench-ai-model-sycophancy/). No paper located.

Past Apart precedents to stay clear of (reported by the other agent, not re-verified): The Alignment Gap, SUP, EchoAudit.

---

# Project 1 (Track 1): Verification Under Pressure

## Closest studies and design comparison
| Study | Their design | Their finding | Our design differs by |
|---|---|---|---|
| **A-CC**, Waqas et al., Dec 2025 — https://arxiv.org/abs/2512.00332 (**full text read**) | BFCL v3 multi-turn; one-sentence *incorrect* user assertion that a wrong function will work; confident vs. hedged tone; 11 small open models (3–70B); metric = calls the asserted function at least once | Compliance 36% (confident) / 28% (hedged); task success drops up to 23 points | (i) **No verification tool and no option to check**: any call to the asserted function counts as compliance. (ii) **Assertions are always wrong**, so correct updating can't be scored. (iii) Tone only, no authority or evidence types. (iv) No frontier models |
| **Bronder**, Aug 2026 — https://arxiv.org/abs/2608.14992 | Claude Opus 5; false claim delivered as tool result vs. inline text vs. prior assistant turn | Channel not necessary: inline 60/60 vs. tool 57/60 adoption; preregistered hypothesis failed | No user pressure; the model never decides *whether* to call a tool |
| **Synthetic Web**, Shah & Ozgur 2026 — https://arxiv.org/abs/2603.00801 | Search agents in mini-internets; one planted misinformation article | Accuracy collapses; agents rarely escalate search | Trigger is a planted source, not user pressure; escalation observed but not manipulated |
| **Sycophancy Suppression**, Ma et al. 2026 — https://arxiv.org/pdf/2608.26511 | Anti-sycophancy methods; unsupported yielding vs. rational updating | Reducing one harms the other; the two are entangled internally | No tools |
| **SycEval**, Fanous et al. 2025 — https://arxiv.org/abs/2502.08177 | Rebuttal types; flips toward correct vs. toward wrong answers | Citation rebuttals drive the most flips toward wrong answers | No tools |

## Precise unanswered question
When a user challenges an agent's answer, does the *type* of challenge (evidence vs. authority vs. insistence) change whether the agent **voluntarily consults** a reliable verification tool? And when it does consult, does it then follow the evidence or the user?

## Contribution and why it matters
- **Novelty type:** measurement plus empirical evidence. The decision to verify is the main outcome, separated into seeking evidence and integrating it.
- **Why it matters:** "Give agents tools" is the default fix for sycophancy and hallucination. If pressure suppresses checking, tool access gives no protection in exactly the cases where it is needed. Answer-level benchmarks such as A-CC and SycEval cannot see this.

## Minimum experiment
- **Task:** about 60 items with known answers in a deterministic local record store, accessed through `lookup_record(id)`, with every call logged.
- **Turn 1:** the model's initial answer, held fixed per item (cached).
- **Factors:** 4 challenge types (none / evidence / authority / insistence) × 2 user correctness (right / wrong) × 3 tool conditions (none / optional / required) × 3 models.
- **Baseline arm:** no-tool × challenge. This reproduces SycEval/A-CC-style yielding and validates the setup.
- **Outcomes:** call rate (optional arm); correct interpretation of the result (required arm); final accuracy; abstention as its own category.
- **Pilot gate:** 8–12 items, 1 model. If the call rate is above 95% in every condition (ceiling), add a stated tool cost or call budget and include items the model can answer without a lookup. Then re-pilot.

## Strongest plausible alternative explanation
Differences in call rate come from **surface features of the challenge text**: length, emotional salience, or the mere mention of "check". Controls:
- length-matched challenges
- a neutral "please double-check" arm
- item-level mixed-effects analysis (items are not independent across conditions)

## What each outcome would support
- **Positive:** call rate lower under authority/insistence than under evidence → pressure suppresses verification; tool access is not a sufficient fix. Claim limited to this lookup setting and these models.
- **Negative:** call rate flat and high → agents check reliably, and yielding (if any) happens downstream of evidence. A useful bound on the problem.
- **Mixed:** agent checks but still follows the user (seen in the required arm) → the bottleneck is evidence integration, not evidence seeking. This distinguishes the two competing hypotheses.

## Strongest claim the design supports
"In a controlled lookup task, across 3 models, challenge type changes voluntary verification by Δ, and unverified yielding accounts for X% of wrong final answers."
It does **not** support claims about intent ("wants to please") or about open-web agents.

## Recommendation: **PROCEED**, subject to the pilot ceiling gate.
Reading A-CC in full confirmed the gap: it has no verification option, no correct-assertion condition, and no pressure types.

---

# Project 2 (Track 2): Semantic Citation Drift

## Closest studies and design comparison
| Study | Their design | Their finding | Our design differs by |
|---|---|---|---|
| **Citation Drift**, Seetha Ram, WASP 2025 — https://aclanthology.org/2025.wasp-main.20 | 240 multi-turn conversations, 4 LLaMA models, 36 real sources; Jaccard stability of references across turns | References mutate, disappear, get fabricated (up to 85.6%) | They measure the **reference** changing. We measure whether an **unchanged** reference still supports a **changed** claim |
| **LLM as a Broken Telephone** — https://arxiv.org/abs/2502.20258 | Iterative rephrasing and translation chains | Distortion accumulates; constrained prompting reduces it but doesn't eliminate it | No citations, no source-support labels |
| **SourceCheckup**, Wu et al., Nat. Commun. 2025 — https://arxiv.org/abs/2402.02008 | 7 LLMs, 58k statement–source pairs, GPT-4 verifier validated by doctors | 50–90% of responses not fully supported | Static snapshot; no editing over time |
| **What Do Claim Verification Datasets Test?** — https://arxiv.org/abs/2604.01657 | Reasoning-trace analysis of 1,000 samples | Scope and specificity mismatch is a distinct pattern | Gives us an error taxonomy, not a drift measurement |

Practitioner reports describe this exact "scope dropping" failure in AI-maintained wikis (supports "why it matters"):
- https://www.glukhov.org/knowledge-management/knowledge-systems-architectures/compiled-knowledge/llm-wiki-maintenance-knowledge-drift/

## Precise unanswered question
When AI edits a cited claim repeatedly, how often, at which step, and through which edit operations does the claim stop being supported by its source **while its citation stays unchanged**? And does checking each revision against the source prevent this without stripping useful information?

## Contribution and why it matters
- **Novelty type:** measurement (support retention vs. citation retention) plus empirical evidence (which edit operations break support) plus intervention evaluation (the fidelity vs. information trade-off).
- **Why it matters:** An unchanged citation makes a drifted claim look verified, and citation-existence checkers pass it. That makes it a blind spot in tools built to catch citation errors.

## Minimum experiment
- **Data:** about 50 source passages with quantitative or scoped findings, plus one supported seed claim each.
- **Chains:** 5 edits per chain, with operations shorten / simplify / formal / merge / persuasive. Report each operation separately.
- **Arms:**
  - (A) ordinary editing
  - (B) citation-preserving instruction
  - (C) source-bound check after each revision
  - (D) attention control: same length as C, no check
- **Models:** 2–3.
- **Baseline arm:** A, scored with Broken-Telephone-style fact survival. This reproduces known degradation, and the new support labels then test whether citation retention overstates fidelity.
- **Outcomes:**
  - share of claims unsupported with the citation retained
  - first step at which support is lost
  - error type: number, population, causal, or dropped qualifier
  - share of atomic facts kept
- **Validation:** about 100 human-labelled claim–source pairs; report κ against the LLM verifier. Use a second verifier from another model family.
- **Pilot gate:** 8–12 passages, 1 model. If there is no drift, **do not escalate prompts to manufacture it**. Report the null result or switch to the fallback.

### Added: animal welfare slice (directional drift)
- About 1/3 of passages come from animal welfare science: sentience evidence (fish and insect pain), welfare-label studies (e.g. what "cage-free" measures), and farm-practice statistics.
- Each passage carries a pre-registered label saying which way a distortion would *understate* or *overstate* harm to animals.
- **Extra hypothesis:** drift in welfare claims leans toward understating harm, consistent with the speciesist bias reported in https://www.nature.com/articles/s41467-026-72297-9 ("LLMs exhibit speciesist bias against animals"). Neutral-domain drift should have no direction.
- **Test:** the share of drifted claims that understate vs. overstate, welfare vs. neutral domain, with chain-level analysis.
- **Null** (no directional difference) → drift is noise-like rather than following the model's biases. Also reportable.
- Related, but not about epistemics: AnimalHarmBench (https://arxiv.org/abs/2503.04804) and Speciesism in AI (https://arxiv.org/abs/2508.11534).

## Strongest plausible alternative explanation
Arm C "wins" only because it makes the model **shorter or more hedged**, not more faithful. Controls:
- the information-retention metric
- the length-matched attention control (D)

Second alternative: judge error. Handled by human κ and the cross-family verifier.

## What each outcome would support
- **Positive:** support drops while the citation survives → citation presence is a misleading proxy; verification must re-run after every edit.
- **Negative:** support stays intact → evidence that iterative AI editing is safe for these operations. A useful null.
- **Mixed:** arm C restores support but loses information → a quantified fidelity vs. information trade-off.

## Strongest claim the design supports
"After k edits by models M, X% of claims whose citation is unchanged are unsupported, concentrated in operations O; per-revision checking reduces this to Y% at an information cost of Z."
It is limited to these passage types and edit operations, and uses chain-level analysis (turns are not independent).

## Recommendation: **PROCEED.**

---

## Independence check
| Project | Outcome | Level | Track |
|---|---|---|---|
| P1 | Decision to verify under conversational pressure | Agent behavior | 1 |
| P2 | Preservation of support across revisions | Artifact | 2 |

They share only infrastructure (adapters, logging, statistics). OK.

**Fallback if the P2 pilot is null before about 06:00:** "Cost of calm" (see NOVELTY_CHECK.md, Project B).

---

# Candidate 3 (standalone, not selected): audience-conditioned animal welfare facts

**Closest studies:**
- **Persona-dependent answers are already known in general:**
  - ConsistencyAI — https://arxiv.org/abs/2510.13852
  - Intersectional Sycophancy — https://arxiv.org/abs/2604.11609
  - MIT CCC study: less accurate answers for users who appear less educated or non-native — https://www.helpnetsecurity.com/2026/02/20/mit-llms-response-reliability-risks-study/
- **Animal welfare-specific work:**
  - MANTA: multi-turn adversarial test of whether models keep their animal welfare values under pressure — https://library.sparai.org/attachments/reports/recGfsd5EMHp8y4Ef/do-llms-hold-their-values-manta-a-multi-turn-adversarial-benchmark-for-animal-welfare-reasoning-p8y4ef.pdf
  - "Assert, don't describe": linguistic features of fine-tuning data shift animal welfare reasoning — https://arxiv.org/abs/2606.26104
  - Speciesist bias — https://www.nature.com/articles/s41467-026-72297-9
  - AnimalHarmBench — https://arxiv.org/abs/2503.04804

**Gap:** nothing found tests whether *empirical* animal welfare claims (sentience evidence, welfare statistics) shift with who is asking: farmer vs. advocate vs. neutral. Nothing found checks models' sentience claims across taxa against a graded expert reference. The New York Declaration on Animal Consciousness grades "strong support" for mammals and birds and a "realistic possibility" for fish, cephalopods, decapods and insects: https://www.yorku.ca/yfile/?p=355968

**Best version:** test **asymmetric sycophancy**. Do models shift further toward the farmer persona than the advocate persona, because the farmer's view matches their documented speciesist prior? That would be a mechanism-level claim, not just a new domain. Asymmetric sycophancy *in general* has not been checked yet; do that before proceeding.

**Scores:** novelty 3.5, impact 4, strength 3.5 (persona shift needs no ground truth, but the expert reference for calibration is contestable), feasibility 4.5.

**Recommendation: INVESTIGATE FURTHER.** It's a good third idea or a future paper. The animal welfare slice in P2 already captures a directional-bias test with a stronger design.

---

# Rigor plan for both selected projects (strength over speed)
1. **Preregister** hypotheses, primary metrics, exclusions and the analysis plan in a timestamped repo commit before the main run.
2. **Pilot → power:** use pilot effect sizes and variances to set the number of items. Report the planned minimum detectable effect.
3. **Split items** into a development set (prompt iteration) and a held-out evaluation set. Report only held-out results as confirmatory.
4. **Models:** 4–5, including at least 2 open-weight models for reproducibility. Fixed temperature and multiple seeds. Log model IDs and dates.
5. **Statistics:** mixed-effects models with item (and chain) random effects; cluster-robust confidence intervals; Holm correction across primary contrasts.
6. **Grader validity:** blinded to condition; a second grader from another model family; ≥100 human labels per project with κ reported; report disagreements.
7. **Manipulation checks:**
   - P1: does the model register the authority cue? Are challenges length-matched? Is there a neutral "double-check" arm?
   - P2: is the length-matched attention control in place? Is information retention measured?
8. **Robustness:** paraphrase prompts (2–3 templates), so no effect depends on one wording.
9. **Release:** code, items, raw logs and analysis notebook. Every claim traces to a logged run.
10. **Final positioning check:** compare the *actual findings* against the literature before writing conclusions.

---

# Round 3: five new proposals (Missing Denominator, Signed but Wrong, Evidence Contracts, Beliefs Under Stakes, Handoffs)

| Proposal | Closest verified work | Gap left | N / I / S / F | Recommendation |
|---|---|---|---|---|
| **Missing Denominator** | Cognitive-bias evaluation with a survivorship task: treatment shows only survivors vs. control showing both — https://arxiv.org/abs/2410.15413 | No benchmark found that gives a **known sampling mechanism** (random / outcome-dependent / curated), scores against **exact or bounded** answers, measures whether the model **asks for the denominator**, or tests an evidence-manifest intervention | 4 / 4.5 / **5** / 4.5 | **PROCEED (top pick)** |
| **Beliefs Under Stakes** | Beliefs and Behavior in LMs: decision framings (threshold / costs / bets) — https://arxiv.org/abs/2609.07943; belief–action consistency — https://arxiv.org/abs/2602.06286; revealed vs. stated preferences — https://arxiv.org/abs/2605.08556 | None found that holds the evidence fixed, varies only the payoff, and checks whether the **stated probability** moves | 3.5 / 3.5 / 5 / 5 | **INVESTIGATE FURTHER**: read 2609.07943 in full first |
| **Signed but Wrong** | No agent-specific study found. Adjacent: forged authority signals in search agents — https://arxiv.org/html/2606.16821; C2PA "valid ≠ true" — https://arxiv.org/abs/2604.24890 | Valid authentication + false content, separating signature / signer / claim in the interface | 3.5 / 4 / 3.5 / 4 | Backup. Risk: when signature is independent of truth, the setup is artificial, and trusting a signature can be rational in the real world |
| **Evidence Contracts** | WICE (subclaims need different evidence); Decomposition Dilemmas — https://arxiv.org/abs/2411.02400; Alignment Bottleneck — https://arxiv.org/abs/2602.10380 | ML-comparison composition errors (version / benchmark / setting mismatch) | 3 / 4 / 3.5 / 3 | Backup. Depends heavily on annotation |
| **Uncertainty Through Handoffs** | Generalization bias: LLM summaries overgeneralize findings, OR≈4.85 vs. experts — https://arxiv.org/abs/2504.00025; plus SAUP and PropUQ-MAS (named by the other agent; not verified here) | Causal "restore one caveat" interventions | 2.5 / 4 / 3 / 2.5 | Drop |

**Effect on P2:** Peters & Chin-Yee (https://arxiv.org/abs/2504.00025) is close prior work for Semantic Citation Drift: overgeneralization when summarizing. P2's novelty drops to 3.5. Its remaining difference is iterative edits, citation retention and a per-revision source check. P2 becomes the backup.

## Final selection
1. **Missing Denominator.** Track 1 core plus a Track 2 artifact (the evidence manifest).
2. **Verification Under Pressure** (Track 1).

They are independent:
- MD: estimation under a selection mechanism. No social pressure.
- P1: decision to verify under conversational pressure. No selection.

**Animal welfare** becomes a scenario family inside MD. Example: welfare audits where farms choose whether to be audited, so participation depends on the outcome; or certification reports curated by producers. It is a real-world selection mechanism with policy stakes.

### Missing Denominator: design checklist
- **Simulator:** known population, outcome rate, and reporting or selection function. Evidence packets are matched across mechanisms (identical reports, different selection).
- **Disclosure conditions:** mechanism known / partially described / unavailable.
  - When unavailable: score whether conclusions stay within **partial-identification bounds**, and whether the model requests the sampling method or denominator. Don't penalize it for missing information it cannot know.
- **Outcomes:** estimation error, interval coverage, decision regret, information-request rate, and the direction judgment (is the true rate higher or lower than the observed one?).
- **Baseline arm:** a survivorship treatment-vs-control in the style of 2410.15413. This reproduces the known bias.
- **Intervention:** a structured evidence manifest (population, sampling method, coverage, exclusions) vs. a generic "consider selection bias" instruction of the same length vs. nothing.
- **Main alternative explanation:** failures come from **arithmetic**, not from recognizing selection. Controls:
  - a computation-only arm, where the mechanism is given as numbers in neutral framing
  - a qualitative direction question
  - an optional code-tool arm
- **Second alternative:** familiar textbook framings (e.g. the WWII planes story) trigger memorized answers. Use novel surface scenarios and held-out scenario families.

---

# Round 4: decision after verifying the other agents' citations (supersedes rounds 1–3)

## What verification changed
| Paper (verified by direct fetch) | What it kills or narrows |
|---|---|
| Deng & Yan, "Selected Evidence, Omitted Information, and Belief Updating in LLM Decision Support" (SSRN 2026; hiring and procurement examples) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7066638 | **Missing Denominator → DROP** (my round-3 top pick was wrong). Also weakens "Unmeasured is not unharmed" |
| Correction or Manipulation? — https://arxiv.org/abs/2610.36453 (7 models; authority and citation pressure; signal detection theory for correction vs. manipulation; agentic study with a verification policy) | Kills "pressure type × user right" as a contribution, and my old SDT "Stubborn ≠ vigilant" idea |
| Why LLMs Give In — https://arxiv.org/abs/2608.01017 (role × evidence × structure × grounding; 1.2M trials; grounding helps but doesn't eliminate yielding) | Grounding is supplied, never *acquired* by the agent → the voluntary-acquisition gap survives |
| DIVA — https://arxiv.org/abs/2610.32181 (costly checks, stopping, value of information; no social pressure) | Evidence acquisition is studied, but not under pressure |
| MCP Sycophancy Detector — https://github.com/syedairhakazmi/MCP-Sycophancy-Detector | Verification is automatic in the pipeline, not chosen by the agent; pilot only |
| FactRot (EMNLP 2026) + Understanding before verifying | **Citation Drift → DROP.** Closest work for the final-vs-per-edit redesign: "Efficient Real-time Refinement" (named by the other agent; not verified here) |
| FORCEBENCH — https://arxiv.org/abs/2605.28044 | Narrows Evidence Contracts |
| Silence Is Endorsement: Verification-Status Laundering — https://arxiv.org/abs/2609.20211 | Closest work for verification-scope spillover (removing an "unverified" marker raises approval) |

## Final decision
**P1: Verification Under Pressure, redesigned. Status: protocol + pilot.**
- **Question:** holding the user's factual assertion, the value of the evidence and the cost of checking fixed, does social pressure change (a) **acquisition** of decisive evidence, (b) **use** of evidence already supplied, or both?
- **Core design:**
  - pressure: neutral vs. pressured version of the *same* assertion
  - acquisition: agent chooses to look up vs. identical evidence supplied automatically (enforced workflow, not an instruction)
  - user: right vs. wrong
  - no-tool arm as the replication baseline
  - start with one pressure type
- **Measures:** relevant retrieval (not raw call counts), final accuracy, acceptance of valid corrections, rejection of invalid ones.
- **Free, clearly relevant tool is the baseline.** Vary tool cost only as a separate, deliberate factor. Label pilot-driven changes exploratory and confirm them on fresh items.
- **Alternatives to rule out:** pressure changes perceived reliability or instruction priority; auto-supplied evidence changes salience. Hold the speaker's stated expertise constant where possible and standardize evidence presentation.

**P2: Verification-scope spillover in animal welfare assurance. Status: investigate further → pilot.**
- **Question:** when a verifier correctly confirms a *narrow* claim (e.g. "the housing-policy implementation was audited at facility X"), does the agent extend that trust to *unchecked, broader* claims ("welfare outcomes improved")? Does binding the verification result to its exact claim prevent this, without rejecting valid evidence?
- **Why animal welfare:** commitment → implementation → measured outcome are genuinely different evidential steps. Certifications usually verify practices, not animals' outcomes (ANSES emphasizes outcome measures).
- **Labels are fixed by design.** The scope of the check is known exactly, so "does the conclusion exceed what was verified" needs no contested expert judgment on welfare itself. A domain expert should still review realism.
- **Matched non-welfare family** (process certification vs. defect rates) tests whether the effect is general or welfare-specific.
- **Conditions:**
  - no verification
  - unrelated claim verified
  - relevant narrow claim verified, scope stated in prose vs. structured fields
  - ambiguous "verified" label as a practical comparison
  - which claim is false, swapped
  - agreeing cases
  - legitimate differences (dates, populations)
  - strong-evidence cases, so blanket distrust can't score well
- **Before piloting:** read "Silence Is Endorsement" in full, and check Authority Bias (https://arxiv.org/html/2609.37616v1) and Epistemic Cue Utilization (https://arxiv.org/html/2610.12788v1). The other agent named these; I have not verified them.

**Backup:** composition experiment (source separation × measurement compatibility). Clean 2×2, narrower impact.

**Dropped:** Missing Denominator; Citation Drift (both versions); Signed but Wrong (original); Evidence Contracts (original); Uncertainty Through Handoffs; Stubborn ≠ vigilant; the broad evidence-laundering study; animal welfare "same facts, different audience". The last remains possible only with a role × stated-position crossed design.

**Rigor-plan amendments:** external timestamped preregistration (OSF / AsPredicted); smallest effect of interest set in advance, sized with pilot variance and dependence; human validation per error category and condition, with adjudication; a stated rationale for model choice; numeric 1–5 scores dropped as false precision.

---

# Round 5: review of the "Scientific Novelty Assessment" (T1 authority → checking; T2 Semantic Citation Drift)

## New references, all verified by direct fetch
| Paper | Finding that matters |
|---|---|
| Beyond the Sycophancy Score — https://arxiv.org/abs/2610.08840 | 104k replies, 10 model configs, 13 pressure conditions. **Task type dominates** yielding (ΔR² 0.485); pressure tactic barely matters (0.009); fallacious or emotional framing adds nothing over **plain repetition**; most concessions come from models that can't solve the item; max reasoning removed concessions on deep puzzles. No tools; voluntary evidence acquisition not measured |
| Is Sycophancy a Form of In-Context Updating? — https://arxiv.org/abs/2610.28325 | Deference to users shares mechanisms with general in-context updating. No callable tools mentioned |
| Relevant Is Not Warranted (Findings EMNLP 2026) — https://aclanthology.org/2026.findings-emnlp.1577/ | Published version of ForceBench (same title and abstract as arXiv 2605.28044) |
| Show Me How You Cite (EMNLP 2026) — https://aclanthology.org/2026.emnlp-main.2063/ | Citation fidelity across levels of AI involvement in authorship. Not tracked across edits |

## Verdict on the document
- **Agree:**
  - phrase the T1 question without assuming a direction
  - Δ_check as the primary measure
  - novelty and feasibility as separate gates
  - one deterministic tool; scoped claims
  - T1 verdict "redesign narrowly"
- **T1 fixes:**
  1. **Restore the evidence-auto-supplied arm**, delivered by an enforced workflow. Without it you cannot separate acquisition from use.
  2. **Authority is a confound.** A claimed expert's assertion is legitimately informative, so deference could be rational updating. Use repetition or insistence as the pressure manipulation (Beyond the Sycophancy Score shows plain repetition is as strong as fancier tactics), or hold claimed expertise constant across arms.
  3. **Item choice decides everything** (task type dominates). Use items whose answers *require* the lookup (records not in model memory), so that checking is decision-relevant. Report results by item type.
  4. **Expect small effects.** Preregister a smallest effect of interest. A 10–12 scenario pilot validates the measurement; it is not a test of the hypothesis.
- **T2: disagree with "proceed to pilot".**
  - "Longitudinal" adds a time dimension to FactRot (fact survival over hops, faithfulness prompts) and ForceBench (citation laundering). Under §2.2 that is a combination of known variables unless it yields a new inference.
  - Its arms (ordinary / citation-preserving / careful / source-bound) largely repeat FactRot's prompt conditions. It has no final-vs-per-edit comparison and no matched compute.
  - Verdict stays **REDESIGN**.
- **Priority:** disagree with "T2 first". T1 stays first.
- **Second project:** the document does not consider **verification-scope spillover** (animal welfare assurance). That remains my recommended P2: labels fixed by design, closest work is Silence Is Endorsement (2609.20211), and it has a direct welfare-decision use.

## Round 5b: self-review of the Round 5 verdict (corrections)
1. **"Past Apart reviewers raised the authority-as-evidence point."** This came from another agent's summary (The Alignment Gap feedback). I did not verify it. Cite the reviewer note only after opening it.
2. **"0.009 vs. 0.485 explained variance" is imprecise.** These are *drops in McFadden R²* when a factor is removed from a logistic model of *answer yielding*. "Effects on checking may be small" is my extrapolation to a different outcome, not a finding.
3. **Switching from authority to repetition changes the question.** It removes the expertise confound, but it is no longer "does perceived authority affect checking". Better: keep both as separate arms (repetition-only; authority with expertise irrelevant to the item), each with a manipulation check. Do not swap one for the other silently.
4. **Design hole in my own fix.** If items are "records the model can't have memorized", the model has no basis for an initial answer to be challenged. Fix: in turn 1, give the model a plausible but secondary or noisy source (e.g. a summary or an older snapshot) from which it answers. The lookup tool returns the authoritative record. The user's challenge is right or wrong relative to that record. This keeps checking decision-relevant without making turn 1 arbitrary.
5. **"T2's arms largely repeat FactRot's prompt conditions" overstated it.** Only the "careful rewriting" arm ≈ FactRot's generic-faithfulness prompt. The citation-preserving and source-bound arms are new, since FactRot has no citations. The real objection stands, but it is narrower: the document does not say what new *inference* the combination gives.
6. **P2 (verification-scope spillover) is less settled than I implied.**
   - Silence Is Endorsement was read only at abstract level; Authority Bias (2609.37616) and Epistemic Cue Utilization (2610.12788) are still unverified.
   - "Labels fixed by design" holds only if the outcome is **attribution of verification**: does the agent describe claim B as verified, or justify B by the check on A? It does not hold for "is B plausible?". Implementation evidence can be weak, legitimate evidence about outcomes, which turns into warrant-strength calibration and runs into ForceBench.
   - Score the attribution outcome as primary; treat confidence in B as secondary.
7. **Status:** P2 is "investigate further", not ahead of other candidates by default.
