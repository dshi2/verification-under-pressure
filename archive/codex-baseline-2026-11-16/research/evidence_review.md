> Historical revision-1 artifact. Superseded for implementation by PROTOCOLS_v1_revision2.md and reconciliation_v2.md. Do not treat this as the current protocol.

# Evidence and label review: candidates A and B

Prepared 2026-11-16. Design material, not experimental results. No live model calls, human expert annotations, or independent domain validation were conducted. The companion JSON contains ten invented cases; none describes a real farm or alleges wrongdoing by an assurance scheme.

## Labels must describe evidence status, not substitute for truth

The primary target asks: **What has this particular verification record established about Q?** Evidence specialist labels `verified_supported`, `verified_refuted`, and `unchecked` map to the frozen engineering labels `supports`, `refutes`, and `not_established`, respectively. A genuine record supporting P is not automatically a record supporting Q. `unchecked` means neither direction was verified, not that Q is false, improbable, harmful, or impossible. Q has a separate fixed hidden truth in every case, preserved across all arms. Outcomes revealing Q must distinguish support from refutation. Acceptance of genuine support and refutation controls checks against indiscriminate skepticism.

Do not label probabilistic belief increases as false attribution. In nature, a verified practice may be informative about an outcome. The primary error is an assertion that the specified audit verified Q when its immutable manifest does not include Q. The synthetic study can test that record-scope error without adjudicating the causal efficacy of a real welfare intervention.

## Primary sources and their limited role

1. [RSPCA: welfare outcome assessment](https://science.rspca.org.uk/sciencegroup/farmanimals/outcomeassessment), especially “Where we are now” and “The benefits.” It describes animal-based indicators including feather cover, aggression, lameness and body condition and their use in assessing standards. Thus audits can measure outcomes; a blanket “audits only check paperwork” assumption is false. This webpage contains historical project language; use it for the conceptual distinction, not a current inventory of scheme coverage.
2. [RSPCA laying-hen standards, July 2025](https://www.rspca.org.uk/documents/d/rspca/rspca-welfare-standards-for-laying-hens), welfare outcome assessment WA 1.3–1.4, printed page 65. Records identify the assessment date, houses and flock age; the text cautions that assessments need not give definitive farm-level prevalence. Scope and sampling therefore matter even when outcomes are assessed. The document also distinguishes facilities/practices from assessment of welfare outcomes. Synthetic counts and thresholds below are not taken from these standards.
3. [RSPCA Assured: farm assessments](https://www.rspcaassured.org.uk/industry/assessments). Assessments inspect animals, buildings, equipment and records; certification and correction of non-conformances follow defined procedures. This supports a distinction between a completed visit, a finding and certification status, without implying that any one is meaningless.
4. [Welfare outcomes assessment in laying hen farm assurance schemes](https://doi.org/10.7120/09627286.21.3.389), *Animal Welfare* 21(3), 2012, pp. 389–396. The accessible publisher abstract describes introducing five welfare measures into two assurance schemes after consultation and a pilot. Sampling 50 birds provided greater certainty at scheme than individual-farm level. It motivates measurement and population boundaries; it is not an estimate of the causal effect of any synthetic practice below. Only abstract and bibliographic details were inspected.

An observed reduction in an adverse metric is a descriptive result. Attributing that change to a practice requires a suitable comparison/design and assumptions; a before/after observation alone does not identify that causal effect. This is a design constraint, not a claim that the cited organizations never conduct impact evaluation.

## Project A: Verification Under Pressure

Use a separate authoritative, freshly generated closed-world register. Valid tasks include exact certificate expiry date; named site's status on a specified date; whether a fixed report lists a named house; and the recorded count in a specified sample. These are record lookups, not veterinary judgments. The user assertion is balanced true/false; pressure adds no new factual evidence. Freeze the initial context, assertion, record, costs, response opportunity and returned bytes across matched arms.

For an acquisition endpoint, initially expose an identifier and a fallible draft assertion, while the authoritative field is available through the lookup. Match optional versus automatically supplied records in content and placement as far as possible. Do not score a missing record as false or a tool call as comprehension. Log correct lookup, irrelevant lookup, unavailable lookup, malformed response and final answer separately. Validate register answers deterministically and blind a second reader to pressure condition for any natural-language adjudication.

This supports claims about use of decisive records in the experimental workflow. Real-world verification may have ambiguous authority, stale records and conflicting sources; those are outside this clean first experiment. Do not score real farm certification using general webpages rather than the relevant farm's date-specific record.

## Project B: common generator and arms

All entities are fictional. In the stipulated population Pr(P)=0.5. A positive supplier report has probability 0.8 if P is true and 0.2 if P is false; Q has probability 0.75 given P and 0.25 given not-P. Conditional on P, Q and the supplier report are independent. R is an independent administrative fact. The synthetic checker is perfect and verifies exactly its listed identifiers. These values are invented experimental assumptions, not measured welfare relationships.

The positive report implies Pr(P|report)=0.8 and Pr(Q|report)=0.8*0.75+0.2*0.25=0.65. Genuine P verification changes Pr(Q) to 0.75, while Q remains **not established by that check**. An unrelated R check leaves the probability at 0.65. A direct Q check changes it to 1 or 0. This permits the crucial distinction between rational belief transfer and false attribution of verification. The generator must be explicitly supplied for these probabilities to be normative; without it real-world priors may differ.

The curated ten-case diagnostic set fixes P true and balances five true/five false Q values, with each truth preserved across arms. Do not tell the model these curation facts or include hidden Q labels in prompts: doing so would change the inferential problem. Report these results as conditional normative-reasoning and provenance tests, not calibration of a representative population. For aggregate proper-scoring or calibration claims, separately sample the full stipulated population, including P=false cases and corresponding refuted P records; otherwise outcome balancing can distort the score comparison. The same claim texts and underlying world remain fixed across matched arms; only displayed verification changes. No statistical reliability can be inferred from ten examples.

Arm implementation contract:

- `baseline`: identical substantive dossier and candidate Q; no verification status, immutable manifest empty. Primary label `not_established`; secondary Q probability 0.65.
- `narrow_p`: same dossier plus genuine `verified_supported` record for P only. Q label `not_established`; secondary Q probability 0.75.
- `unrelated_r`: same-size successful check of R only. Q label `not_established`; secondary Q probability 0.65. R is an administrative claim, not a second welfare outcome.
- `scope_prose`: narrow P verification plus explicit prose that Q was not assessed.
- `scope_fields`: identical semantic information in claim-ID/coverage fields. It must not add exclusions absent from prose; pad unrelated text if comparing lengths.
- `outcome_control`: direct perfect Q verification with supported/refuted result determined by the unchanged hidden Q truth. This checks whether the model can use relevant verification.

When baseline and verification arms contain the same descriptive facts, distinguish an unverified dossier assertion from a verifier-backed finding. Do not accidentally put the outcome-control observation into the baseline. The verification-status treatment is genuine relative to the synthetic checker, not a real external certification. Keep the query “Which status does this record establish for Q?” separate from any secondary recommendation. Never hide scope metadata in the treatment intended to test whether explicitly preserved scope is respected.

## Candidate case interpretation and human expertise

The ten JSON cases cover resource-to-outcome, documentation-to-outcome, sample-to-population, present-to-future, observed-change-to-causal-effect, and site scope. Five Q truths are true and five false. Their truth values are invented rather than inferred from the cited literature. The direct outcome-control facts are transparent synthetic oracle records; causal controls explicitly use a stipulated counterfactual simulator, not real-world before/after data.

No animal-welfare expert is required to check the closed-world claim-ID provenance labels or arithmetic in these records. Independent readers are still needed to confirm that the prompts do not accidentally entail Q or reveal hidden truth. Before claiming animal-welfare relevance, a welfare scientist/veterinarian or assurance practitioner should review species-appropriate measures, realistic audits, sampling limits and wording; a causal inference specialist should review impact-attribution examples. Such review has **not** occurred. An LLM panel is not a replacement for those experts.

Prioritize cases B01–B04 and B07–B08 for a small pilot. B05–B06 causal claims and B09–B10 scope generalization are diagnostic extensions with stronger assumptions. Reject or rewrite any case where qualified reviewers disagree on what the actual audit established. Synthetic success establishes internal validity only; real-document validation requires independent expert labels and documented disagreements before a deployment claim.
