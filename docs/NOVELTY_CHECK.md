# Novelty check — AI x Epistemics sprint (Nov 15, 2026, ~21:30 IST)

Status: v1, written by Claude Code. Needs the 30-minute attack by a second agent before code.
Sprint project list is not public until after judging, so it could not be searched. The track page lists "FlipRate" and "Dispute Escalation Benchmark" as example ideas, so expect several teams near both original designs.

---

## Project A — original design: "Updating vs. caving" (FlipRate with valid / fake / social pushback)

### 1. Closest studies (verified links)
| Study | What they ran | What they found |
|---|---|---|
| SycEval, Fanous et al. 2025 — https://arxiv.org/abs/2502.08177 | GPT-4o, Claude Sonnet, Gemini 1.5 Pro on math + medical; rebuttal types (simple, ethos, justification, citation); splits **progressive** (flip to correct) vs **regressive** (flip to wrong) | Simple rebuttals drive progressive flips; citation rebuttals drive regressive flips; flips persist |
| Resist and Update, Yang & Yeung 2026 — https://arxiv.org/abs/2607.12985 | Synthetic Bayesian-witness tasks where the same disagreement is evidence or pressure depending only on stated reliability | Resist-only training collapses updating; proposes an activation clamp that restores both |
| BeliefShift, Myakala et al. 2026 — https://arxiv.org/abs/2603.23848 | 2,400 multi-session trajectories, 7 models; Evidence-Driven Revision track | Trade-off: personalizing models drift without evidence; grounded models miss genuine updates |
| Also: Farm (https://arxiv.org/abs/2312.09085), LoFa (https://arxiv.org/abs/2606.31039), Kumaran et al. (https://arxiv.org/abs/2507.03120) | Persuasion / fallacy resistance / advice weighting | Correct beliefs are easy to overturn; models overweight contrary advice |

### Verdict on the original design: **REDESIGN.**
"Flip rate for valid minus flip rate for fake" is SycEval's progressive/regressive split, plus BeliefShift's trade-off. Adding more models or datasets would not make it new.

### Redesigned A: "Stubborn ≠ vigilant: do sycophancy benchmarks predict who gives good advice?"
**Sentence:** Existing work measures how often models flip under pushback (SycEval, Farm, LoFa) and shows a resist/update trade-off (BeliefShift, Resist and Update). No study we found tests whether these benchmark scores **predict the quality of decisions people make with the model's help**, which is a question the track asks directly. We measure flip-only scores, a signal-detection discrimination score, and downstream decision accuracy for the same models and items. Then we test which score predicts decision quality.

2. **Difference / novelty type:** *Measurement + question.*
   - Signal detection theory splits a model's behavior into two parts: **d′**, how well it tells valid corrections from invalid ones, and **criterion c**, how easily it gives in overall. We found no published use of this for sycophancy. The nearest is a forced-choice paper: https://arxiv.org/abs/2510.16727.
   - It also links the benchmark to a downstream decision outcome. Our search found no study doing that.
3. **Why it matters:** Leaderboards that reward low regressive flipping may be rewarding **stubbornness**. A stubborn model also ignores the user when the user is right. That is a real failure mode in advice settings: medical, financial, forecasting.
4. **Baseline arm (reproduces the known setting):** A standard regressive-sycophancy battery in the SycEval/Farm style (model is correct; user pushes back with fake citation, authority, or plain disagreement) → flip rate per model. This is the "known result" arm.
   - **New arms:**
     - (a) matched **valid-correction** trials, where the model starts wrong and the user brings true evidence. Together with the baseline, this gives d′ and c.
     - (b) an **advisory decision task**. Questions have known answers. A simulated user holds a prior that is sometimes right and sometimes wrong, consults the model, and then decides. Outcome: final decision accuracy, and how often a correct user is talked into a wrong answer.
5. **What each result would mean:**
   - **Positive** (d′ predicts decision quality, flip rate does not) → flip-rate leaderboards mislead; recommend d′ and c.
   - **Negative** (flip rate predicts as well as d′) → the simple metric is validated for this use.
   - **Mixed** (depends on domain) → benchmarks only transfer within a domain.
   - **Nothing predicts** → current benchmarks lack predictive validity for decisions.
   - Every outcome teaches something → keep.
6. **Strongest claim supported:** "Among N models, score S predicts simulated-advisee decision accuracy better than flip rate, controlling for the model's baseline accuracy."
   - **Main alternative explanation:** general capability. Bigger models could be both more discerning and more accurate. Controls: (i) baseline accuracy as a covariate, (ii) item-level mixed-effects models, (iii) restrict some analyses to items every model answers correctly at first.
   - **Second caveat:** the simulated advisee is an LLM. State this; hand-check a sample; and, if a local hub allows, run a 10–20 person pilot.
   - **Power caveat:** with 8–12 models, model-level correlations are weak. Lean on the item-level analysis.
7. **Verdict: GO on the redesign**, pending the attack.

---

## Project B — original design: Dispute Escalation Bench (simulated heated users, escalation grading)

### 1. Closest studies (verified links)
| Study | What they ran | What they found |
|---|---|---|
| Sun, Xu & Li 2026, "Reducing Conversational Escalation… with Nonviolent Communication Constraints" — https://arxiv.org/abs/2606.26106 | Two-agent simulation: assistant vs. simulated user at several resistance levels; interpersonal conflict and distress; escalation scored −2..+2 | NVC prompt constraints consistently reduce escalation |
| Cheng et al. 2025/2026 (Science), "Sycophantic AI Decreases Prosocial Intentions…" — https://arxiv.org/abs/2510.01395 | 11 models; 3 preregistered human experiments, N=2,405 | Affirming responses reduce willingness to repair conflict and increase conviction of being right; users prefer them |
| ELEPHANT, Cheng et al. ICLR 2026 — https://arxiv.org/abs/2505.13995 | Social sycophancy on AITA, plus a flip test (both sides of the same conflict) | Models affirm whichever side the user takes ~48% of the time |
| Also: Spiral-Bench (https://eqbench.com/spiral-bench.html), DistressBench (https://labs.scale.com/blog/distressbench) | Simulated-user de-escalation in delusion and crisis settings | |

### Verdict on the original design: **REDESIGN.**
"Simulated heated user → escalation score → prompt fix" is Sun et al. 2026 almost exactly.

### Redesigned B: "The cost of calm: do de-escalation fixes talk genuinely wronged users out of legitimate grievances?"
**Sentence:** Existing work shows that de-escalation prompting reduces escalation (Sun et al.) and that affirmation harms conflict repair (Cheng et al.). That work treats validation as bad and de-escalation as good across the board. Nothing we found checks the **cost** of these fixes when the user really is the wronged party. In that case de-escalation can become false balance or victim-blaming. We vary who is at fault, by scenario construction, and measure both escalation and false balance.

2. **Difference / novelty type:** *Missing comparison + intervention cost* (the boundary of an existing finding).
3. **Why it matters:** People bring real grievances to chatbots: wage theft, harassment, discrimination, a landlord withholding a deposit. A fix that calms everyone down can steer wronged people away from asserting their rights. Labs could deploy anti-sycophancy or NVC-style prompts on the strength of results measured only on at-fault or ambiguous users.
4. **Baseline arm:** Default assistant vs. NVC-style de-escalation prompt, on at-fault and ambiguous users, using Sun et al.'s −2..+2 escalation scale. This should **reproduce** their result.
   - **New cell:** the **genuinely-wronged** users. Facts are fixed in the scenario, so the ground truth on fault is known.
   - **Full design:** fault (at-fault / ambiguous / wronged) × assistant condition (default / NVC de-escalation / "be honest, challenge the user" anti-sycophancy) × 4–6 models.
5. **What each result would mean:**
   - **Positive** (fixes raise false balance and lower actionable help for wronged users) → fixes must depend on who is at fault; tradeoff curve per model.
   - **Negative** (no cost) → evidence that these prompts are safe to deploy, which is useful.
   - **Mixed** (some models only) → deployment guidance per model.
   - Every outcome is informative → keep.
6. **Strongest claim supported:** "Intervention X lowers escalation by Δ₁ but raises false-balance responses toward genuinely wronged users by Δ₂, in simulated dialogues across N models."
   - **Main alternative explanation:** the judge reads NVC's softer *tone* as hedging and scores it as false balance. Controls:
     - separate rubric items for substance (who is at fault, what remedies are offered) and for style
     - judge blind to condition
     - judges from two model families
     - ~100 human-labelled items, with agreement reported
   - **Secondary outcome:** the simulated user's final message to the other party.
7. **Verdict: GO on the redesign**, pending the attack.

---

## Things the attacking agent must check (30 min)
- Read the full Sun et al. 2026 paper. Do its scenarios vary user fault, and does it measure any cost of de-escalation? If yes, B needs another angle.
- Read arXiv 2510.16727. Does it already compute d′ for valid vs. invalid corrections? If yes, A's measurement novelty shrinks to the link with decision outcomes.
- Search for any study correlating sycophancy-benchmark scores with downstream decision or advice outcomes, including the Decision Lab "LLM advisors" study: https://thedecisionlab.com/research/measuring-sycophancy-in-llm-advisors
- Check whether ELEPHANT's open-ended set already separates wronged users from at-fault users in a way that covers B.
- Try to break each item-6 claim. Re-check positioning once more before submission.
