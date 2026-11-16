# Revision 2 literature follow-up and interpretation

Checked 2026-11-16. Working specification: [authoritative revision 2 protocol](PROTOCOLS_v1_revision2.md), with the [interpretation addendum](INTERPRETATION_ADDENDUM_v2.md). This note updates positioning, not conditions or the frozen pilot baseline. No live experiments were run.

## Decisions retained

- P1 runs first for measurement readiness; no impact ranking is established. P2's welfare application is plausible, not evidence of adoption or animal benefit.
- P2 A retains the identical practice fact used in B. C versus C′ compares the same scope content in different formats; B versus C adds scope information.
- B approximately equal to D1, with both above A, can be informative about nonspecific verification effects. A nonsignificant B−D1 test does not establish equivalence. Report uncertainty and require a prespecified equivalence margin before asserting similarity.
- B greater than D1 supports content specificity, not identification of a psychological mechanism. Authority may contribute. Neither an undesired effect pattern nor a null result alone triggers a switch to composition.
- P1's candidate contribution remains pressure × (choosing to check vs. evidence supplied) × user right/wrong, with objective evidence.
- Matched native tool-call/result formatting controls representation. Optional agents still make a preceding retrieval decision; supplied evidence bypasses that decision. Identical messages do not establish identical attention or eliminate all timing/selection explanations. Do not condition accuracy comparisons on voluntary checkers.

## Literature findings

| Source and access | Relevant finding and implication |
|---|---|
| [Audit Without Verification](https://arxiv.org/html/2609.07680), full-text methods, results, limitations and appendices inspected | Deleting the upstream attribution field while holding observations fixed helps when the suggestion is wrong and can hurt when it is right; the trade-off varies by domain. Its original responsibility-framing confirmatory result is null; the deletion experiment is exploratory. This is a report-interface precedent, not our truthful P-verification versus unchecked-Q attribution contrast. Cite the controlled ablation and both directions of its result, not an unconditional improvement claim. Code and raw results were not independently reproduced. |
| [Silence Is Endorsement](https://arxiv.org/html/2609.20211), remaining appendices F–K inspected | Appendix J already compares identical status content in prose, JSON fields and typed tags through a summarizer. Preservation varies by summarizer. It also tests placement, with only four bindable items per monitor. This strengthens the prior-art case for formatting interventions: C′−C is secondary, not standalone novelty. P2 differs by directly measuring whether truthful verification of P is attributed to Q, without a compression stage. |
| [Verified but Vacuous](https://arxiv.org/html/2611.05590), abstract and introduction inspected | Verifier acceptance, syntactic specification binding and semantic fidelity are separate properties. The reported 1.9% measures a particular structural binding criterion, not the percentage of programs that are correct. This motivates careful scope labels; it does not measure reader overgeneralization. Full-paper review remains uncompleted. |
| [Who Verifies the Tools?](https://arxiv.org/html/2610.32110), main-text methods, results and limitations inspected; workshop acceptance stated on arXiv | A close additional precedent: changing disclosure of fixed tool results changes agents' overclaims and verifier verdicts. Repaired text combines facts and instructions. Thus neither “scope clarification reduces overclaim” nor “same facts, different presentation” is sufficient novelty. P2's narrower contribution is the incremental effect of truthful P-verification on attribution to distinct Q, with unchanged factual content and an unrelated-check control. No exact equivalent factorial was found in the inspected design. |

## Workshop screen: partial, explicitly bounded

The [official workshop site](https://verify-agents-workshop.github.io/) and its linked [OpenReview venue](https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/Verify-Agents) were checked. OpenReview returned a loading shell; a public API listing attempt returned HTTP 403. No access restrictions were bypassed. A complete accepted-paper inventory was therefore not available through these routes.

Public searches found the formatter paper above and [Anchor](https://arxiv.org/abs/2605.26321), whose abstract concerns generating mutually consistent instructions, environments and verifiers. Another relevant abstract, [Widening Harm Evaluation Coverage](https://arxiv.org/abs/2611.02624), compares trajectory and environment-state access for harm judges. Neither abstract describes P2's contrast. These abstract screens do not replace full-text review or establish complete workshop coverage.

**Verdict:** retain both projects and their current diagnostic-pilot baseline. Narrow the novelty wording around cross-claim attribution; do not claim novelty for structured provenance or clarification alone. The targeted comparisons support proceeding with validation, while the workshop-wide novelty screen remains incomplete. Confirmatory execution remains disabled.
