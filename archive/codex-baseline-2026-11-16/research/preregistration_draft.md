# Preregistration draft — NOT REGISTERED, NOT FROZEN

Revision 2 reconciliation draft, 2026-11-16. The authoritative design is PROTOCOLS_v1_revision2.md, together with HANDOFF_CHECKLIST.md. This supersedes the old imported-snapshot/six-arm protocol. Archived scripted v1 runs are software validation only.

## Questions and design

P1 candidate contribution: **pressure × (choosing to check vs. evidence supplied) × user right/wrong, with objective evidence**. Christian and Mazor's voluntary-versus-supplied self-blinding design is a precedent. Manipulated pressure with decisive objective evidence is our narrower candidate contribution, not a global novelty guarantee.

P1 starts with an actual model answer to a secondary source. Cache its raw response, parsed answer, configuration and source, then reuse it identically across matched branches. Never fabricate a prior answer. Cross neutral, insistence and irrelevant-authority pressure with no-tool, optional-tool and supplied-evidence routes, plus assertion correctness. Preserve native tool-call/result messages and log relevant returns separately from attempted/wrong-ID calls.

**Explicit implementation decision:** retain all independently crossed assertion-correctness cells. Neutral wording asks reconsideration rather than falsely asserting disagreement when the user already agrees with the cached answer. Concession means changed from the cached answer to the user assertion; already-agreeing cases contribute zero to the unconditional intention-to-treat rate. Also report initial-alignment and initial-correctness strata. This differs from a concession rate restricted to initially disagreeing cases; do not interchange their denominators.

P2 nine arms: A content-matched baseline; A0 outcome-only exploratory; B narrow practice verification; C scope prose; C_prime equivalent structured scope; D1 unrelated same-facility verification; D2 same-practice different-facility verification; E direct outcome evidence; V vague verification label. A/B/D1 substantive content must match outside verification/filler. D2 preserves the target-facility practice as unverified. Issuer is identical where applicable, and verification placement is counterbalanced.

Define Q with metric, population, date and comparator. Observational improvement is not causal improvement. Separate direct verification attribution from belief. A disclosed synthetic probability model may make indirect belief changes rational; its numbers are experimental stipulations, not empirical welfare probabilities. V requires an explicit oracle-scope policy; vague display alone does not establish Q.

## Proposed primary estimands

P1, for each prespecified non-neutral pressure versus neutral:

1. Relevant lookup rate in optional route. Attempted and wrong-ID requests reported separately.
2. Accuracy difference in supplied route.
3. Pressure accuracy penalty optional minus supplied, by intention to treat.
4. Discrimination between valid and invalid user assertions, with the exact agreement/concession event and denominator locked. Report cached-initial correctness and alignment because these affect the opportunity to concede.

Supplied-arm pressure × user-correctness on record adoption is secondary. Matching tool-message format controls representation, but cannot prove initiation, timing and salience irrelevant. Do not interpret behavior conditional on voluntary checking causally or claim identified psychological mediation.

P2 primaries: unsupported attribution B−A; B−D1; C−B. Correct E support/refutation is a validity check. C_prime−C is secondary; A0, D2, V, belief and decisions remain exploratory unless promoted before lock. Count unsupported support and unsupported refutation as errors where neither is established, reporting directions separately.

E tests general sensitivity to valid outcome evidence. It does not establish preserved warranted acceptance under each scope intervention. That claim requires truthful scoped-Q controls beyond these nine arms. Authority may contribute to spillover; D1 is a specificity control, not proof of a unique mechanism.

## Analysis and confirmation

Report named-model estimates and paired risk differences with item-cluster uncertainty. Keep seeds, pressure variants, routes and world variants in the same base-item cluster. Account for substantive template families or narrow generalization accordingly. Enforce family-held-out separation.

Enumerate every elementary primary test before locking, including both pressure levels and any model-wise tests. Apply the prespecified Holm family. Four conceptual endpoints need not mean four tests. Ordinary confidence intervals are not simultaneous. Choose smallest meaningful effects from practical significance, then size the study using clustered variability/simulation. Precise-null claims require prespecified equivalence tests, not a nonsignificant difference.

Retain scheduled denominators, errors, refusals, malformed answers and retries. Report conditional-on-valid performance, coverage and missing-outcome bounds. Validate free-text attribution with blinded human labels; structured/free-text disagreement cannot silently count as success.

## Pilot gates

Pilot 8–12 development items per project on one explicitly configured model. Validate cached initial answers, truth isolation, tool reachability, genuine pressure/irrelevant-expertise manipulation, E support/refutation sensitivity and technical-failure rates. These are measurement diagnostics, not confirmatory tests.

If neutral optional checking is below approximately 10%, report a floor and bounded sensitivity to suppression. Do not report no pressure effect as robustness. Any task revision receives a new version and fresh development pilot; never alter only one arm or strengthen pressure until failures appear. A ceiling or a clean null is not a reason to switch projects. Redesign for a documented measurement/contribution failure.

## Open fields before confirmatory execution

| Field | Required completion |
|---|---|
| Models | Exact endpoint/version, native-tool support, reasoning/temperature and selection rationale. |
| Budget | Explicit monetary/token/call cap; price inputs verified or conservatively stipulated; initial-cache calls included; restart-safe reservations and actual usage reconciliation. |
| Population | Independent substantive families, counts, eligibility rules, immutable split, repetitions and generalization limits. |
| Precision | Smallest meaningful effects, cluster covariance assumptions, simulations and independent-item sample size. |
| Labels | Exact Q and V semantics; real-case expert review; blinded pressure ratings and free-text validation/adjudication. |
| Statistics | Elementary test family, equivalence procedure, missingness bounds and independent raw-log reproduction. |
| Release | Frozen prompt/code/data hashes, external timestamp, deviations and raw-log policy. |

No confirmatory execution before these decisions and independent audit. A local build freeze is not public preregistration. Previously inspected data remain exploratory. Real-document animal-welfare claims require two independent domain-informed raters and adjudication; agent consensus is not human validation.

## Permitted claims

Results can establish observed acquisition, accuracy and attribution effects in the specified task/model population. They cannot establish internal motives, unique psychological mechanisms, population calibration from curated toy cases, animal-welfare deployment benefits or preserved warranted trust under untested interventions. Scripted outputs test software only; empirical model claims require actual logged model responses.
