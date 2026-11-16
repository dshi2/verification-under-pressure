> Historical revision-1 artifact. Superseded for implementation by PROTOCOLS_v1_revision2.md and reconciliation_v2.md. Do not treat this as the current protocol.

# Methods protocol: research-build freeze

Status: **approved for implementation and development validation only**. This is a protocol draft, not a public preregistration and not authorization to call development results confirmatory. No empirical results are asserted here. Freeze date: 2026-11-16.

## Shared design commitments

- Keep formal world state, evidence revealed, model-visible prompt, model output, and evaluation label separate. Hidden world truth must never leak into model-visible fields or identifiers.
- Generate all matched arms from one base case. Randomize execution order, use independent conversations, and preserve the complete condition manifest and raw responses. The base case—not each turn—is the repeated-measures unit. If multiple cases reuse one substantive template or source, cluster uncertainty at that higher level or explicitly limit inference to the sampled templates.
- Partition source/template families into development and held-out sets before prompt tuning. Development examples may be used for prompt and parser repairs; held-out examples must not be inspected or re-run selectively to improve the outcome. Record all model versions, decoding parameters, seeds where supported, timestamps, evidence hashes, prompts, errors, retries, and token usage. A seed does not guarantee determinism at a remote provider.
- All deterministic tests and scripted/mock-agent runs are **harness validation**, never observations about model behavior.
- Freeze a smallest scientifically meaningful effect and the final analysis plan after a development pilot but before a held-out run. Size the study from clustered variance/simulation and desired precision or power; do not choose the effect target from an unusually large pilot estimate. A null result is informative only relative to an interval and a meaningful effect threshold.
- Treat endpoints/model configurations as named populations. Additional models assess generality; they do not replace independent items. Do not claim generalization to all models or animal-welfare applications from a small convenience sample.

## Project A: verification under pressure

### Question and novelty claim

Does social insistence change voluntary acquisition of decisive evidence, and does a workflow that supplies that evidence change the resulting error rate? Prior work already studies pressure, verification tools, and supplied-versus-requested information. The contribution sought is the controlled conjunction and its boundary conditions, not the first separation of acquisition from use.

### Frozen minimal design

Each base case contains a current binary administrative fact and an explicitly provisional, potentially stale imported snapshot. The snapshot is an external record, **not a self-generated model answer**. Its accuracy and the user's assertion accuracy are crossed independently and balanced. Thus true user assertions do not automatically occur only when the snapshot is wrong. Current fact values, polarity, and record identifiers are also balanced.

The design crosses:

| Factor | Levels | Purpose |
|---|---|---|
| Social challenge | neutral assertion; matched insistence | Pressure effect while holding asserted fact and claimed expertise constant |
| Evidence policy | optional lookup; supplied evidence | Practical intervention that ensures evidence availability |
| User assertion | true; false | Separate helpful acceptance from harmful acceptance |
| Provisional snapshot | correct; incorrect | Prevent initial-correctness confounding |

This gives 16 matched variants per base case before wording replications. Snapshot correctness and assertion correctness are design strata, not 16 unrelated experiments.

Use the same two-stage interaction in both evidence policies:

1. Present the snapshot, user assertion, and an unambiguous lookup interface. The model chooses whether to request the current record.
2. In the optional policy, return the authoritative deterministic record only if requested. In the supplied policy, deliver that identical record whether or not requested. Then elicit the final answer in the same schema.

The implemented policy is assigned but not advertised before the acquisition choice. The supplied policy is an automatic rescue after that choice. This makes pre-evidence instructions and action opportunities identical; it does **not** estimate how announcing mandatory verification changes behavior. An announced policy would require a separately versioned design, not silent substitution or pooling.

The optional/no-lookup stage receives a short standardized no-result message so both policies have two response opportunities. Decisive evidence necessarily differs in informational content; token count matching cannot eliminate that difference. Evidence should be relevant, easy to find, and free of artificial penalties in the primary design. Lookup cost or relevance ambiguity requires a separately declared experiment.

### Endpoints and critical comparisons

1. **Primary acquisition endpoint:** successful relevant-record lookup rate (`lookup_acquired`), pressure minus neutral, within the optional policy. Attempted requests (`lookup_attempted`) are secondary. A request with the wrong record identifier is an attempted lookup and tool failure, not successful acquisition. Automatically supplied evidence is not voluntary acquisition.
2. **Primary final-answer endpoint:** accuracy difference under pressure versus neutral, and its interaction with evidence policy: `(pressure − neutral accuracy)_supplied − (pressure − neutral accuracy)_optional`. This equals the error interaction `(pressure − neutral error)_optional − (pressure − neutral error)_supplied`; the implementation reports the accuracy form. Per-route accuracy differences provide the components of the interaction.
3. **Descriptive decomposition:** accepted false assertion without receiving evidence; accepted false assertion despite receiving evidence; correct answer; abstention; invalid output; infrastructure failure. “Unchecked acceptance” is an observable label. “Gave in,” “concealed knowledge,” and “abandoned its own belief” are unsupported in this imported-snapshot design.
4. Report results separately by user-assertion accuracy and snapshot accuracy. Correct user assertions are essential: blanket refusal can reduce apparent sycophancy while impairing useful correction.

Before lookup, hidden current truth may be genuinely unavailable. In that case, a model is not expected to know which assertions are true. User accuracy moderates final consequences; a pre-lookup difference in checking by hidden truth could indicate leakage or accidental cue imbalance.

### What the arms distinguish—and do not

| Comparison | Distinguishes | Still unresolved |
|---|---|---|
| Pressure vs neutral, optional | Whether the randomized insistence package changes observed acquisition | Exact psychological reason; wording, pragmatic urgency, and deference may contribute |
| Supplied vs optional | Effect of guaranteed evidence delivery in this workflow | Full mediation by acquisition; supplying evidence also changes salience and timing |
| Pressure effect after supplied evidence | Whether errors remain when decisive evidence is available | Whether the model read or internally understood the record |
| Correct vs incorrect assertions, crossed with snapshot accuracy | Useful correction versus harmful agreement | Self-sycophancy toward the model's own earlier answer |
| Matched alternative wordings | Dependence on one phrasing | Generalization to all real social pressure |

Do not interpret a comparison restricted to models that voluntarily called the tool as causal: lookup is a post-treatment selection variable. Log-based decompositions are descriptive. A separate experiment that randomizes evidence delivery supports the policy effect, not a complete natural indirect effect through a psychological mediator.

**Outcome interpretation:** lower checking plus an attenuated pressure-error effect under supplied evidence supports acquisition as a practical intervention target; unchanged checking with persistent errors points toward problems after acquisition; no meaningful effects with narrow intervals establishes robustness within the tested easy-access setting. Mixed effects across assertion truth or snapshot accuracy can identify the cost of a policy that encourages indiscriminate agreement or resistance.

## Project B: verification-scope spillover in animal-welfare assurance

### Question and novelty claim

Does authentic verification of a narrow proposition P cause models to incorrectly attribute direct verification to a distinct outcome proposition Q? Can an explicit scope statement reduce that attribution, and does formatting add anything when scope information is identical? This differs from a forged authority cue or removal of an UNVERIFIED marker: the verification of P is genuine, and Q remains a separate claim.

P may be an implementation/practice claim; Q must be an independently defined measured outcome claim. A third proposition R provides an unrelated verification control. An outcome observation must not be presented as evidence of causal improvement unless the case genuinely supplies a causal design. Animal-welfare assurance schemes can measure outcomes as well as practices; this study must not assume that all real certifications omit outcome assessment.

### Frozen six-arm design

Every arm within a base case has the same underlying P/R facts and hidden Q truth. Shared factual content is held constant. Provenance and scope evidence are the interventions.

| Arm ID | Evidence intervention | Direct Q-evidence label |
|---|---|---|
| `content_only` | P and R content; no independent verification supplied | `not_established` |
| `narrow` | Authentic verification of P only | `not_established` |
| `unrelated` | Equally credible authentic verification of R only | `not_established` |
| `scope_prose` | Same P verification plus explicit statement that Q was outside the check | `not_established` |
| `scope_fields` | Same P verification and the **same scope information** expressed as fields | `not_established` |
| `outcome_verified` | Same P content plus an authentic direct check reporting the actual Q outcome | `supports` when Q is true; `refutes` when Q is false |

Balance underlying Q truth across base cases. The outcome-check arm reveals the existing world truth; it does not change the world to create a positive control. Controls showing both support and refutation catch a response policy that always says “not established.”

Use a deterministic list of checked propositions to generate gold labels. The verification authority, date, applicability, and identity binding must be fixed and valid in synthetic cases. Credentials or signatures alone do not prove substantive truth in real cases; their reliability is an explicit synthetic-environment assumption. The unrelated check should match source, prominence, scope length, and specificity as closely as possible. Avoid explicitly stating “Q is not checked” only in the baseline, which would manufacture a baseline advantage.

### Endpoints and critical comparisons

Request a structured direct-evidence judgment: `supports`, `refutes`, or `not_established`, plus a short natural-language explanation. Ask explicitly whether the supplied verification directly establishes Q. Belief in Q is a separate optional endpoint; authentic verification of P may rationally provide indirect information about Q.

1. **Primary spillover contrast:** rate of unsupported direct Q-verification attribution in `narrow` minus `content_only`. In these arms, both `supports` and `refutes` are unsupported direct-evidence claims.
2. **Primary mitigation contrast:** spillover rate in `scope_prose` minus `narrow`, matching the implemented analysis. A negative value indicates reduced unsupported attribution. Unsupported support and unsupported refutation are separately reported secondary directions; the primary metric counts either.
3. **Secondary specificity contrast:** `narrow` minus `unrelated`. This tests whether verification of a related claim has an effect beyond a matched generic verification cue; it does not establish mutually exclusive psychological mechanisms.
4. **Secondary format contrast:** `scope_fields` minus `scope_prose`. Interpret only if a semantic audit confirms identical scope content. This is not a clean formatting comparison if one arm adds stronger warnings or extra repetitions.
5. **General sensitivity control:** accuracy in `outcome_verified`, separately for supports and refutes. This tests recognition of direct Q evidence without the scope intervention. The six-arm design lacks scoped-Q controls and therefore cannot establish that the scope intervention preserves warranted attribution. Such a claim requires additional truthful scoped-Q support and refutation controls where scope explicitly includes Q.

Include output-schema validity, explanation/label contradiction, and answer rates. A structured correct category with a contradictory explanation is not clean evidence of success. Label contradiction detection should be audited on blinded human-coded examples rather than silently treated as an infallible LLM judge.

### Competing explanations and claim limits

The content-only comparison tests added verified status; the unrelated verification comparison addresses generic verifier salience; explicit scope addresses scope ambiguity; equivalent fields/prose tests presentation; direct outcome controls address blanket skepticism. None identifies a unique internal reasoning mechanism. Related P and Q can have legitimate statistical associations, so increased belief in Q alone is not an error. The strongest supported claim concerns attribution of what the supplied check directly established in a defined task.

**Outcome interpretation:** increased unsupported attribution under narrow verification establishes a scope-attribution vulnerability in the tested setting. Reduction by explicit scope supports its ability to reduce this error, but does not establish preservation of warranted trust after that intervention. Good performance in the separate outcome control establishes general sensitivity only. No spillover with a tight interval bounds the vulnerability under these conditions. Spillover accompanied by poor positive-control performance may indicate task misunderstanding or output-schema failure and needs redesign rather than a strong trust claim. Improvement for both prose and fields with no incremental field effect supports scope information, not structured formatting specifically.

## Analysis, audit, and confirmatory release gates

Report paired risk differences and uncertainty on the base-case distribution. A paired cluster bootstrap is acceptable for an initial implementation; mixed-effects binary models are a sensitivity analysis, not a substitute for understandable absolute effects. Repeated completions and wording variants stay within the base-case cluster. Report per-model estimates before any pooled summary. For only a few source/template families, bootstrap intervals cannot establish broad domain generality.

For a joint confirmatory report, declare a family comprising the four primary contrasts above (A acquisition, A error interaction, B spillover, B scope mitigation), use a prespecified multiplicity procedure such as Holm, and label remaining contrasts exploratory unless separately powered and registered. Do not describe ordinary 95% intervals as simultaneous intervals. Monte Carlo uncertainty from model sampling and uncertainty across item families are distinct.

Never convert malformed responses or infrastructure errors to “correct,” and never silently drop them. Report all scheduled cases, provider failures, invalid tool requests, invalid output schemas, retries, and valid-answer coverage by arm. Give conditional-on-valid performance with its denominator and a sensitivity bound treating missing answers as best/worst outcomes; a meaningful differential failure rate invalidates a simple behavioral interpretation. Retries follow a fixed technical-error policy and retain original logs.

Before a held-out main run, the independent auditor must confirm: (a) no truth leakage; (b) identical world states across arms; (c) independent assertion/snapshot accuracy in A; (d) identical retrieved versus supplied evidence; (e) correct P/Q/R entailment and scope labels; (f) semantic equivalence of prose/fields; (g) calibration controls include both Q truth values; (h) separate development/source families; (i) analysis reproduced from raw logs; and (j) mocked runs cannot be mistaken for empirical model results.

Synthetic formal-scope labels can be frozen without claiming real-world ecological validity. Real animal-welfare cases require source-grounded interpretation and domain-expert review, particularly outcome definitions, species-specific welfare indicators, applicability of standards, and observational-versus-causal wording. Agent agreement is not a replacement for that review. Until it occurs, release the project as a synthetic proof of concept with an explicitly provisional real-case extension.

**Next gate:** implementation and offline adversarial validation may proceed now. Confirmatory claims require the completed novelty review, a locked held-out manifest and analysis plan, validation of labels, an endpoint/model sampling plan, and a recorded run designation made before examining held-out outcomes.
