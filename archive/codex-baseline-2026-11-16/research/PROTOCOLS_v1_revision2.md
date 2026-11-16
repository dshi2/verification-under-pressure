# Protocols v1 — P1 Verification Under Pressure · P2 The Scope of Trust

Status: design draft, revision 2. Not frozen and not preregistered. No experiments have been run.

## Revision 2 changes (Nov 16, 2026)
- **P1 narrowed** by Christian & Mazor 2026 (see the Agent 1 table). The contribution is now: does *manipulated social pressure* change the acquisition and use of *objective, decisive* evidence, given whether the user is right or wrong? The two-part design (voluntary tool use vs. an injected tool result) is no longer new by itself. Cite it as the design precedent.
- **P2 baseline is now content-matched.** Condition A states the same practice fact as B ("The facility provides X m² per animal"), without saying it was checked. The verification contrast therefore varies verification status only, not information.
- **P2 format arm is explicit.** Only C vs. C′ (structured fields vs. prose with equivalent scope content) supports a claim that structured fields work better. B vs. C supports only "stating scope helps".
- **Defensible claims, not unique mechanisms.** The P2 claim is behavioral: *holding substantive information fixed, verifying A changes unsupported attribution of verification to B, and communicating scope changes that effect.* Authority may contribute to spillover. The D1 control tests specificity; it does not rule out every psychological account.
- **A precise null is a result.** A precise null means no meaningful effect, with an equivalence test against a preregistered smallest effect of interest and with controls that work. Switch to the composition backup only if a *contribution or measurement gate* fails, not because an effect is disappointing.
- **Priority is separate from execution order:**

  | Project | Current advantage |
  |---|---|
  | P1 Verification Under Pressure | Stronger measurement readiness. Pilots first |
  | P2 The Scope of Trust | More distinctive application; more domain-validation uncertainty |

  Running P1 first implies nothing about its ultimate value. P2's "high impact" is a plausible application, not demonstrated adoption or welfare benefit.
- **Dropped project confirmed:** arXiv 2610.09164 (Yamin, Fernandes, Koch, Wilder, Horvitz, Oct 2026, "Training Language Models To Be Coherent Decision-Makers") holds evidence fixed while varying utilities and framing. That supports the earlier decision to drop Beliefs Under Stakes.
- **Checked by another agent, not re-verified here:** ClaimReceipt and TRACE both exist. TRACE (multi-table evidence retrieval and composition) is prior work, and a possible baseline, for the composition backup.

## Agent 1 — Novelty adversary

**P1: pressure → evidence acquisition vs. use.** No duplicate, but the closest precedent (first row) narrows the contribution.
| Closest | What it does | Gap left |
|---|---|---|
| **Christian & Mazor 2026, "Self-Blinding and Counterfactual Self-Simulation Mitigate Biases and Sycophancy in LLMs"** — matanmazor.github.io/files/papers/christian2026blinding.pdf (full text read; data: github.com/self-model/SelfBlindingLLMs) | 60 disputes × user side × order. A `run_counterfactual_simulation` tool queries a blinded copy of the model. **Voluntary use:** models rarely self-call to correct sycophancy. **Supplied:** an injected tool call + result → models defer 79–85% of the time, *more often when the blinded answer favors the user* (Qwen .94 vs .89; GPT .83 vs .76). Read as "knowingly sycophantic". Qwen2.5-7B and GPT-4.1; logit outcomes | Pressure is not manipulated (identity framing only; prompt instructions vary); there is no objective ground truth and no user right/wrong; the tool returns the model's own counterfactual opinion, not decisive external evidence; next-token logits, not agentic generation. **Consequences for P1:** (1) the voluntary vs. injected-result split is a precedent, not a novelty; (2) expect a *floor* in spontaneous acquisition (E11); (3) their selective deferral is our supplied-arm discrimination estimand. Report it as a conceptual replication with objective evidence |
| Correction or Manipulation? — arxiv.org/abs/2610.36453 | Pressure types × correct/incorrect; discrimination score; agentic policy study | No voluntary evidence acquisition compared with supplied evidence |
| Why LLMs Give In — arxiv.org/abs/2608.01017 | Role × evidence × structure × grounding (1.2M trials) | Grounding is supplied, never acquired |
| Beyond the Sycophancy Score — arxiv.org/abs/2610.08840 | Task type dominates yielding; plain repetition is as strong as fancier tactics | No tools |
| DIVA — arxiv.org/abs/2610.32181 | Costly information acquisition, stopping | No social pressure |
| SPINE — arxiv.org/abs/2609.09090 | 25-turn pressure; the correct answer often stays in the reasoning trace when the model caves | Supports a "use" failure; no tools |
| FVA-RAG — arxiv.org/abs/2512.07015 | Retrievers fetch premise-aligned documents; adversarial "kill queries" | Concerns query content, not the decision to check. Possible extension: does pressure bias the query? |
| Agentic financial sycophancy — arxiv.org/abs/2604.24668 | Sycophancy-inducing information arrives as tool results | Not about the decision to retrieve |
| MCP Sycophancy Detector (GitHub) | Verification is automatic in the pipeline | Not voluntary |

**P2: verification-scope spillover.** No duplicate found. Full text of the closest paper read.
| Closest | What it does | Gap left |
|---|---|---|
| Silence Is Endorsement — arxiv.org/abs/2609.20211 (full text read) | Same-claim conditions: no claim / UNVERIFIED marker / marker lost / VERIFIED | **No different-claim verification, no scoped-verification intervention, no unrelated-verification control** (checked against the paper) |
| Authority Bias — arxiv.org/abs/2609.37616 | A *wrong* "verified source" note flips 45–88% of correct answers | False verification, not a correct check spilling over. Its effect size sets the bar for our authority controls |
| What Counts as Evidence? — arxiv.org/abs/2610.12788 | Recognizing a cue ≠ using it | No transfer between claims |
| ClaimReceipt — arxiv.org/abs/2609.01992 | Claim-relative verifier (PASS / INVALID / INCONCLUSIVE) | A tool, not a behavioral study |
| ForceBench — aclanthology.org/2026.findings-emnlp.1577 | Relevant ≠ warranted (claim strength vs. a fixed passage) | Single claim–passage pairs; no verification result |
| Audit Without Verification — arxiv.org/abs/2609.07680 (Arslan, Sep 2026; abstract read) | Preregistered six-agent pipeline. LLM auditors adopt upstream agents' stated conclusions; removing only the conclusion field, with observations fixed, sharply raises accuracy and cuts adherence | Conclusion-relay, not narrow → broad scope transfer; no unrelated-verification or scope-statement controls. Cite for S9 (echoing dossier claims) and its content-held-fixed ablation logic |
| Verified but Vacuous — arxiv.org/abs/2611.05590 (Vempaty et al., Nov 2026; abstract read) | "Verified" code merges three surfaces: verifier acceptance ≠ binding to spec ≠ spec captures the requirement (99.1% accepted vs. 1.9% spec-binding on HumanEval) | Artifact-level scope gap, not a behavioral study of a reader overgeneralizing. Use as motivation: the scope ambiguity is real in a second domain |
| Not yet read: "Claim-relative verifiability" (AI & Ethics 2026) | Conceptual | Read before writing related work |

**Remaining adversarial tasks:**
- read the last ~20% of Silence Is Endorsement
- full text of 2609.07680 (only the abstract has been read)
- search OpenReview for NeurIPS 2026 workshop papers ("Who Verifies the Agents?")
- re-run before submission

## Agent 2 — Methodologist: which arm separates which explanation

### P1 design
- **Turn 1:** the model answers from a provided *secondary* source (summary or older snapshot). The answer is cached and identical across arms.
- **Turn 2 factors:**
  - Pressure: neutral disagreement / repetition-insistence / authority with expertise irrelevant to the item. Same factual assertion in each; length-matched.
  - Evidence: no tool / optional `lookup_record(id)` / evidence supplied. In the supplied arm the workflow *injects an identical tool-call + tool-result pair*, so position and format match the optional arm.
  - User assertion: right / wrong relative to the authoritative record.
- **Answer format:** final answer in a structured field, so no LLM grader is needed for correctness.

| Competing explanation | Distinguishing contrast | Prediction if true |
|---|---|---|
| E1 Pressure suppresses **acquisition** | Pressure vs. neutral, optional arm, P(relevant lookup) | Δcheck < 0 |
| E2 Pressure harms **use** | Pressure vs. neutral, supplied arm, accuracy | Δacc_supplied < 0 |
| E3 Acquisition accounts for the accuracy loss | Pressure penalty in optional vs. supplied (intention-to-treat; **no conditioning on who checked**, since that is post-treatment) | Penalty_optional > Penalty_supplied ≈ 0 |
| E4 General pliability, not evidence-sensitive | Pressure × user-correctness | Same effect when user is right or wrong (no discrimination) |
| E5 Authority treated as **evidence** (possibly rational) | Authority vs. repetition arms × evidence | Authority > repetition with no tool; gap closes when evidence is supplied |
| E6 Salience or timing of supplied evidence | Injected tool-turn format identical to the optional-arm return | Rules this out by construction (residual: who initiated the call) |
| E7 Surface features (length, politeness) | Length-matched neutral arm containing the same assertion | — |
| E8 Pressure read as an instruction not to check | No instruction content in pressure text; manipulation check | — |
| E9 Ceiling (always checks) | Report it as a finding. A cost factor only as a *separate preregistered* extension | — |
| E10 Model already knows the answer | Private synthetic records; secondary source in turn 1 | Lookup is decision-relevant |
| E11 Floor: models almost never check unprompted (Christian & Mazor) | Neutral-arm check rate in the pilot. If it is near 0, Δcheck cannot be estimated | Pilot gate: if the neutral check rate is < ~10%, change the *task* so that checking is plausible (e.g. the secondary source is visibly dated). Never add "use tools" wording to one arm only |
| E12 Selective deferral: evidence is used when it favors the user, ignored when it contradicts | Supplied arm, P(final answer = record) when user wrong vs. user right | Lower adoption when the record contradicts the user. This is the objective-evidence version of Christian & Mazor's asymmetry; test whether pressure *amplifies* it |

**Primary estimands (preregister):** Δcheck(optional); Δacc(supplied); interaction (Penalty_optional − Penalty_supplied); discrimination = P(concede | user right) − P(concede | user wrong).
**Secondary:** pressure × user-correctness on adoption in the supplied arm (E12).

**Defensible P1 claim:** "Holding the evidence available fixed, pressure changes [whether the agent obtains / how it uses] decisive evidence, and this does / does not depend on whether the user is right." This makes no claim about internal mechanism.

### P2 design
- **Same facility facts throughout.** Every condition states the practice fact in the same words ("The facility provides X m² per animal") and the same outcome claim B ("welfare outcomes have improved"). Conditions differ only in *verification status and scope text*. Dossier length is matched with neutral filler, and the auditor identity is identical across conditions.

| Code | Condition |
|---|---|
| A | **Content-matched baseline:** practice fact + outcome claim, with no verification statement |
| A0 | Outcome claim only, no practice fact (exploratory: how much the practice *information* moves belief) |
| B | A + genuine confirmation that *this practice fact* was checked |
| C | B plus scope stated in prose: what was and wasn't checked ("outcomes were not assessed") |
| C′ | Same scope content as C, in structured fields (**format** test; only C vs. C′ supports a format claim) |
| D1 | A + an unrelated property verified at the same facility (e.g. fire-safety certificate); the practice fact stays unverified |
| D2 | A + the same welfare practice verified at a *different* facility (population or place scope mismatch) |
| E | Genuine animal-based outcome evidence (positive control) |
| V | Vague "Verified ✓" label (practical comparison) |

- **Outcomes:**
  - **Primary:** attribution. Does the agent state or imply that welfare *outcomes* are verified or demonstrated, or cite the practice check as proof? Captured in a structured `claims_verified` field plus free text.
  - **Secondary:** belief, P(outcomes improved).
  - **Tertiary:** supplier decision; whether it requests outcome evidence.

| Competing explanation | Contrast | Prediction |
|---|---|---|
| S1 Scope spillover | Attribution B vs. D1, and B vs. A | B > D1 ≈ A |
| S2 General reassurance or authority | Same contrasts | B ≈ D1 > A |
| S3 Rational indirect evidence | Belief vs. attribution; synthetic cases with a stated P(outcome \| practice) | Belief may rise in B (compare to the Bayesian target); attribution should not |
| S4 Topical priming without a scope error | D2 vs. B | If D2 ≈ B, place and population scope are ignored too |
| S5 Clarification (content) | B vs. C | C < B on attribution |
| S6 Format | C vs. C′ | Difference = format effect only |
| S7 Lexical "verified" token | V vs. B | — |
| S8 Blanket distrust | E: endorsing a supported outcome claim must be scored as *correct* | E ≫ others on correct endorsement |
| S9 Agent just echoes dossier claims | A's attribution rate | If A is high, spillover is not needed to explain errors |

| S10 Verification adds information, not just status | A is content-matched to B | Rules this out by construction for B − A. A0 vs. A measures the information effect separately |

**Primary estimands:** attribution B − A (verification effect, information held fixed); attribution B − D1 (specificity); attribution C − B (scope clarification); correct endorsement in E (validity check).
**Secondary:** C′ − C (format, equivalent content).

**Defensible P2 claim:** "Holding substantive information fixed, verifying A changes unsupported attribution of verification to B, and communicating scope changes that effect." B ≈ D1 > A would mean general reassurance from verification, which is still a finding. B ≈ D1 ≈ A, measured precisely, is a legitimate null.

## Agent 3 — Evidence specialist: labels and where expertise is required

**P1 labels by construction.** Record store, correct answers, and correctness of the user assertion are all set by design.
- Human checks needed only for: (a) plausibility of the secondary source, (b) **manipulation check**. Raters judge perceived pressure and perceived expertise of each challenge, blind to condition.
- Correctness comes from the structured field. "Relevant lookup" means a call that retrieves the correct record id.

**P2 labels.** Each dossier carries a claim table:
- each claim
- its evidence level: commitment / practice-implementation / animal-based outcome / causal improvement
- its status: verified / unverified / contradicted, by construction

Grounding for the level distinctions:
- ANSES: resource-based vs. animal-based measures — anses.fr/system/files/SABA2021AUTO0161RaEN.pdf
- WOAH broiler outcome indicators: mortality, culling, gait, contact dermatitis
- EFSA broiler welfare opinion: to source and verify

**Where domain expertise is required:**
1. Realism of audit scopes (what real schemes actually audit). Sources to verify: Better Chicken Commitment criteria, RSPCA Assured standards, Welfare Quality protocols. Needs a welfare scientist or auditor.
2. Plausible practice → outcome relationships for the synthetic belief target. This is stated in-world, so it needs no real-world truth, but it should not be absurd.
3. Labels for the real-document set: what a given real audit report does and doesn't establish. Expert-adjudicated; two independent raters plus an adjudicator.

**Not needed:** verified or unverified status (set by construction).

**LLM grader:** used only for free-text attribution. Validate on a stratified sample covering every condition × model, with human raters blind to condition. Report agreement and disagreements.

## Agent 5 — Independent auditor: pre-run challenges
1. **P1 post-treatment trap:** never estimate "effect among checkers". Self-selection breaks randomization. Use intention-to-treat contrasts and the supplied arm.
2. **P1 tool framing:** the tool description and system prompt must be identical and neutral. Any "use tools when unsure" wording becomes a confound with pressure.
3. **P1 reasoning modes:** reasoning modes differ (max reasoning removed concessions in Beyond the Sycophancy Score). Stratify, or fix one mode per model.
4. **P1 wrong-id calls:** a call that fetches the wrong record counts as "checked" but not "relevant". Report both.
5. **P2 judge leakage:** the grader sees the response plus the ground-truth claim table, never the condition label or the verification block's wording.
6. **P2 authority bar:** with a 45–88% authority effect known (2609.37616), any auditor or brand cue difference between B and D1 would swamp the result. Keep the issuer identical.
7. **P2 training-data contamination:** real audit documents may be memorized. Keep synthetic cases primary for confirmatory claims.
8. **Order effects:** randomize where the verification block sits in the dossier.
9. **Multiplicity:** only the primary estimands above are confirmatory. Everything else is exploratory, with Holm correction for primaries.
10. **Held-out set:** develop on families X; confirm on families Y that no agent saw during prompt tuning.
11. **P2 content matching is testable:** a script diffs A, B and D1 dossiers and fails if any of them differs from A outside the verification block (and filler).
12. **P1 floor:** if the neutral-arm check rate is near 0, Δcheck(optional) is uninformative. Do not report "pressure does not suppress checking" from a floor.

## Agent 4 — Engineering lead (BLOCKED: disk full; build only after design freeze)
- **Repository layout:**
  - `harness/` — model adapters, budget cap, response cache, JSONL logging (model id, date, params, seed, raw request/response)
  - `p1/` — record store (JSON, content-hashed), `lookup_record` tool, injected-evidence workflow, turn-1 cache, condition randomizer
  - `p2/` — dossier generator from claim tables, condition renderer (prose / structured), filler length matching
  - `analysis/` — mixed-effects logistic models (item random intercept), cluster bootstrap, held-out split enforcement
  - `tests/` — mock-model unit tests. No fabricated results.
- **Pilot:** 8–12 items per project, one model, dev families only. The pilot checks measurement validity, not hypotheses.
