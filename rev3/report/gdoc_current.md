<!-- Plain-text snapshot of the P1 Google Doc (https://docs.google.com/document/d/1_v5ev4v2f-FH8ZK3938FkITJnO8sSVES-I-VLqyRjwA/edit), read via the Doc's mobilebasic view at 16:31 IST, 16 Nov 2026. Headings lost their markup. Includes ChatGPT's earlier edits to the title, abstract, intro, methods and limitations. NOTE: the Doc's methods still say DeepSeek on AtlasCloud; P1 v2 runs used SiliconFlow fp8 (configs/p1_dev_eval_v2.json). -->

Copy of Apart Research hackathon submission template

Verification Under Pressure: Does Social Insistence Disrupt Evidence-Seeking or Evidence Use?[1]

Author name 1
Affiliation

Author name 2
Affiliation

Author name 3
Affiliation

Author name 4
Affiliation

Author name 5
Affiliation

Author name 6
Affiliation

With
Apart Research

Abstract

DRAFT ABSTRACT — RESULTS PENDING. Language-model assistants may encounter confident user assertions that conflict with records. A model can correctly interpret evidence when supplied yet fail to obtain it voluntarily; conversely, it can seek evidence without resisting a misleading claim. We test these distinct failures in a controlled factorial evaluation. We randomize whether initial information is current or stale, whether the user assertion is right or wrong, whether the user is neutral, insistent or invokes irrelevant authority, and whether objective evidence is absent, optionally available through lookup, or supplied directly. The resulting 36 conditions per item are evaluated on four open-weight model families with five repeated generations. We separately observe lookup attempts, relevant retrieval and final-answer correctness. The central E4 contrast asks whether the effect of insistence differs across optional versus supplied evidence, and whether that contrast changes with user correctness. Initial model answers are shared across experimental branches to isolate follow-up interventions. The available cases are researcher-authored development scenarios; independent validation and confirmatory inference are distinct future stages. Findings, confidence intervals and conclusions will be added once live results have been collected and audited.

1. Introduction

Correctly responding to available evidence and choosing to obtain evidence are different safety-relevant behaviors. A user who insists on a false value may suppress verification even when a model would use an objective record if shown it.

The intervention comparison isolates operational evidence-delivery choices. It tests whether making the same record available via optional lookup versus supplying it changes vulnerability to user pressure.

Provide enough background for readers to understand your work.

If relevant, briefly describe the threat model or failure mode you're addressing; reference prior work that motivates why it is worth addressing, or explain it yourself.

Aspire to clearly list your most important contributions that go beyond what exists today.

Our main contributions are:

[First contribution — what new thing did you create, discover, or demonstrate?]
[Second contribution]
[Third contribution, if applicable]

2. Related Work

What prior work is most similar, and how does your work differ?

Cite the most relevant papers, tools, or projects. Explain what gap your work addresses.

Some questions which may help:

When and why would someone use your method over the existing state-of-the-art?
What information/insight does your method provide which we did not have before?

3. Methods

We cross two evidence snapshots (current, stale), two assertion correctness levels (right, wrong), three pressures (neutral, insistence, irrelevant authority) and three evidence routes (none, optional lookup, supplied), giving 36 randomized cells per item. Five generations per cell are nested in an item. The initial answer is generated once per item × snapshot × model × repeat, then replayed into 18 follow-up branches. Main contrasts E1–E4 quantify lookup-attempt change, supplied-arm accuracy change, delivery-by-pressure interaction, and its moderation by user correctness. Item-level inference and missing-result bounds are required; response-level independence is not assumed.

Four text-only open-weight families: GPT-OSS 120B (DeepInfra), DeepSeek V3.2 with reasoning enabled (AtlasCloud), Qwen3 235B Instruct 2507 (DeepInfra), and Kimi K2 Instruct 0905 (Novita). Sampling parameters are omitted so pinned providers use their defaults; max_tokens is 8192. Five repeats per item and condition. Base development bank: 24 cases across six families. A separately frozen 36-item extension adds six families. The raw requests, stage keys, response journal, manifests, scorer, confidence intervals and figure scripts are reproducibility artifacts.

4. Results

RESULTS PENDING: Insert completed-cell counts, model-specific contrasts with item/case-clustered confidence intervals, robustness checks, quality metrics and numbered figures after auditing live data. Offline planted-effect tests are not empirical results.

[template guidance text omitted]

5. Discussion and Limitations

Discuss the broader implications for AI safety.

What do your results mean? What trends do you notice and what might they indicate?

Limitations

Synthetic binary registries may not represent complex real-world record workflows. Builder-authored cases and unvalidated pressure paraphrases limit generalization. The optional lookup condition measures observable tool attempts, not latent intent. Canonicalized supplied evidence is a controlled workflow, not arbitrary provider-native tool use. Statistical uncertainty must cluster repeated generations by item and account for family heterogeneity.

Future Work

What are the natural next steps? How could this work be extended?

6. Conclusion

CONCLUSION PENDING: This section will be written from validated model responses and prespecified statistical decisions, not from expected results.

Code and Data

Code repository: https://github.com/dshi2/verification-under-pressure
Data: Development datasets and frozen manifests; live output data not yet verified.
Other artifacts (optional): [Demo link, video walkthrough, Hugging Face Space, etc.]

Author Contributions (optional)

References

[Reference 1]
[Reference 2]

Appendix (optional)

LLM Usage Statement

LLM assistance supported research planning, code development and report drafting. All reported empirical results, citations and methodological claims must be verified by the research team before submission.

[1] Research conducted at the AI x Epistemics Research Sprint, November 2026
