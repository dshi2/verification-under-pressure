# Novelty and contribution gate: P1, P2, P3 (Nov 16, 2026)

This is the required pre-implementation deliverable (framework §2.2), one page per project. Design details are in PROTOCOLS_v1.md (revision 2 + revision 3 notes). These are second-round (adversarial) reviews; the final positioning check is still due before submission.

**Common search gaps**
- Sprint submissions are hidden until judging (the sprint page says so), so they can't be checked yet.
- Of the mentors and judges, only one lists a code repository (github.com/SuneetMalhotra), and it hasn't been searched.
- The "Who Verifies the Agents?" workshop has been screened only paper by paper; the OpenReview listing was inaccessible.

---

## P1: Verification Under Pressure (Track 1)

**Core sentence.** Existing work establishes that pressure makes models yield, with or without supplied grounding (Correction or Manipulation?; Why LLMs Give In), and that models seldom consult a tool unprompted but defer to its supplied output (Christian & Mazor). It leaves unresolved whether *social pressure* acts on **obtaining** decisive objective evidence, on **using** it, or both, and whether that depends on the user being right. We separate these by crossing pressure (insistence vs. neutral) × evidence route (optional lookup vs. identical supplied tool result) × user right/wrong. Either outcome tells a deployer whether automatic retrieval fixes the failure.

| Closest study (verified) | What it ran and found | Our difference |
|---|---|---|
| Christian & Mazor, arXiv 2601.14553 | Self-call tool: spontaneous use rare; supplied blinded answers followed 79–85%, more when they favor the user | Pressure manipulated; objective record instead of self-opinion; user right/wrong; generation instead of logits |
| Correction or Manipulation?, arXiv 2610.36453 | Pressure types × correct/incorrect challenges; discrimination; agentic policy | No voluntary acquisition vs. supplied evidence contrast |
| Why LLMs Give In, arXiv 2608.01017 | Role × evidence × structure × grounding, 1.2M trials | Grounding is always supplied, never acquired |
| When2Tool, arXiv 2605.09252 (cite the version used) | When tool calls are needed; necessity is decodable from hidden states | No social pressure |
| SPINE, arXiv 2609.09090 | The correct answer is often still in the reasoning trace when the model caves | Supports a use failure; no tools |

- **Novelty type:** interaction / causal identification.
- **Baseline arm reproducing the known setting:** the no-tool arm reproduces standard pressure-induced yielding. The supplied arm reproduces Christian & Mazor's deference with objective evidence.
- **Unanswered question:** with the factual challenge and decisive evidence held fixed, does pressure change acquisition and correctness differently when evidence must be fetched vs. is supplied, and does that depend on user correctness?
- **Minimum experiment:** insistence vs. neutral × optional vs. supplied × user right/wrong, disagreement trials only, one model, enough items for the preregistered precision on the interaction.
- **Strongest alternative explanation:** the supplied route differs in salience and in who started the call (a workflow difference), not only in "acquisition". Floor (agents almost never check) is a second risk.
- **What results mean:**
  - Δcheck < 0 and supplied accuracy unaffected → retrieval policy is the fix.
  - Supplied accuracy also drops → integration/response policy needs work; retrieval alone is insufficient.
  - Neither → pressure acts on neither under these conditions (precise null, by equivalence test).
  - Mixed by user correctness → selective deference (an objective-evidence version of Christian & Mazor).
- **Strongest supportable claim:** a workflow effect ("supplying evidence changes the pressure penalty"), not full mediation.
- **Recommendation: PROCEED** (pilot on development families, then freeze).

---

## P2: The Scope of Trust (Track 2, animal welfare)

**Core sentence.** Existing work establishes that false or lost verification status sways agents (Authority Bias; Silence Is Endorsement), and that disclosing omitted details changes overclaiming from fixed tool output (Who Verifies the Tools?). It leaves unresolved whether a **truthful** verification of claim P raises the claim that a **distinct, unchecked** claim Q was verified, holding the facts fixed. We test this with a content-matched baseline (A), a matched unrelated check (D1) and genuine outcome evidence (E), in welfare assurance, where practice audits are routinely read as outcome evidence.

| Closest study (verified) | What it ran and found | Our difference |
|---|---|---|
| Silence Is Endorsement, arXiv 2609.20211 (read incl. App. J–K) | Same-claim status lost in handoffs; App. J format survival; App. K policy instruction as an arm | Status intact and correct; transfer to a *different* claim; unrelated-check control |
| Authority Bias, arXiv 2609.37616 | A wrong "verified source" note flips 45–88% of answers | False vs. truthful verification; sets the bar for authority controls |
| Who Verifies the Tools?, NeurIPS 2026 (abstract) | Omission vs. disclosure in a tool formatter changes agent claims | Covers C − B partly; not P → Q transfer |
| Audit Without Verification, arXiv 2609.07680 | Auditors relay upstream conclusions; removing the conclusion field helps | Conclusion relay, not scope transfer |
| What Counts as Evidence?, arXiv 2610.12788 | Recognizing a source cue ≠ using it | No cross-claim transfer |

- **Novelty type:** question + empirical evidence in a consequential setting. Measurement novelty: attribution separated from belief.
- **Baseline arm reproducing the known setting:** V (vague "Verified ✓") reproduces the known verified-label effect. A reproduces "claims alone".
- **Unanswered question:** with substantive information fixed, does truthful verification of P increase unsupported attribution of verification to Q, and does communicating scope reduce it?
- **Minimum experiment:** A, B, D1, C, E on synthetic welfare dossiers with improved and non-improved outcomes. Primary estimands: B − A, B − D1, C − B, plus E as a validity check.
- **Strongest alternative explanation:** a general reassurance or authority effect (handled by B vs. D1, with D1 matched in issuer, template and seriousness). Also legitimate indirect inference (handled by scoring attribution separately from belief).
- **What results mean:**
  - B > D1 ≈ A → content-specific spillover (mechanism open).
  - B ≈ D1 > A → general reassurance from any verification, still a finding.
  - B ≈ D1 ≈ A, precise → no spillover under these conditions.
  - C < B → scope statements help (partly known; secondary).
- **Strongest supportable claim:** holding information fixed, verifying P changes unsupported attribution to Q; communicating scope changes that effect.
- **Recommendation: PROCEED to pilot**, conditional on revision-3 fixes: no scope rule in the shared system prompt, a matched D1, and separate outcome-level fields.

---

## P3: Evidence Composition (candidate)

**Core sentence.** Existing work establishes that models compose multi-table evidence imperfectly (TRACE, EMNLP 2026), overstate what relevant evidence supports (FORCEBENCH), and mishandle selected evidence (Deng & Yan). It leaves unresolved whether **separating sources** specifically reduces an agent's ability to tell valid comparisons from invalid ones, holding the numbers and metadata fixed. We test the interaction of location (same / separate document) × compatibility, with extraction and distance controls.

| Closest study | What it ran and found | Our difference |
|---|---|---|
| TRACE, EMNLP 2026 main.968 | Tree-structured multi-table claim decomposition and composition | No compatibility manipulation |
| FORCEBENCH, Findings EMNLP 2026 | Relevant ≠ warranted on a single passage | Single source; no measurement-condition mismatch |
| Deng & Yan, SSRN 7066638 | Models recognize selected evidence but don't correct their conclusions | Selection, not comparability |
| arXiv 2602.03238 (position) | Argues incompatible agent-evaluation comparisons should be kept separate | Conceptual; no behavioral test |
| Prior Apart submission on incomparable AI-incident rates | Denominator and estimand mismatches in incident data | Data audit, not an agent experiment; must be positioned |

- **Novelty type:** interaction / causal identification.
- **Baseline arm reproducing the known setting:** same-document incompatible pairs reproduce known single-passage overstatement.
- **Minimum experiment:** 2×2 plus a pre-extracted-fields arm and a token-distance arm. Primary estimand: drop in discrimination from same-document to separate documents.
- **Strongest alternative explanation:** extraction or distance difficulty, not comparability reasoning (controlled by the two extra arms).
- **What results mean:**
  - Interaction present and survives the controls → source separation hides incomparability.
  - Vanishes with pre-extracted fields → the extraction bottleneck is the fix target.
  - No interaction → multi-document difficulty is general, not comparability-specific.
- **Recommendation: INVESTIGATE FURTHER.** Read multi-document numerical QA (MultiHiertt, DocMath-Eval), long-context distance work and LLM meta-analysis studies before a pilot.

---

## Portfolio decision rule (set in advance)
Submit the two projects that pass novelty (final check), manipulation checks and positive controls, preregistered precision or a decisive equivalence test, and independent reproduction, regardless of effect direction. Existing code is never a reason to continue.
