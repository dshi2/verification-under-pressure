# Reconciliation: Google Doc export (`report/gdoc_current.md`, 16:31) → `REPORT_DRAFT.md`

The export contains ChatGPT's earlier edits. Each one below is either kept in the draft or the reason for not keeping it is given.

| Doc text (section) | Status in the draft |
|---|---|
| Title "Verification Under Pressure: Does Social Insistence Disrupt Evidence-Seeking or Evidence Use?" | **Not applied: conflict, flagged to the user.** The workstream brief fixes the title "…Optional vs. Supplied Record Evidence Under Correct and Incorrect User Insistence". The authors choose; both are listed in the review packet. |
| Footnote "Research conducted at the AI x Epistemics Research Sprint, November 2026"; "With Apart Research" | Kept (header line). |
| Abstract: "A model can correctly interpret evidence when supplied yet fail to obtain it voluntarily; conversely, it can seek evidence without resisting a misleading claim." | Kept (abstract, opening). |
| Abstract: initial answers shared across branches "to isolate follow-up interventions" | Kept (abstract). |
| Abstract: "researcher-authored development scenarios; independent validation and confirmatory inference are distinct future stages" | Kept (abstract, last paragraph). |
| Intro: "Correctly responding to available evidence and choosing to obtain evidence are different safety-relevant behaviors. A user who insists on a false value may suppress verification even when a model would use an objective record if shown it." | Kept (intro, opening). |
| Intro: "The intervention comparison isolates operational evidence-delivery choices…" | Kept (intro, second paragraph). |
| Methods: "Five generations per cell are nested in an item … response-level independence is not assumed" | Kept (§3.5, repeats). |
| Methods: "Item-level inference and missing-result bounds are required" | Already covered (§3.7–3.8). |
| Methods: DeepSeek V3.2 "(AtlasCloud)" | **Not applied: factually superseded.** The analysed v2 runs used SiliconFlow fp8 (`configs/p1_dev_eval_v2.json`, spec §9 serving change). |
| Methods: "raw requests, stage keys, response journal, manifests, scorer, confidence intervals and figure scripts are reproducibility artifacts" | Kept in substance (Code and Data). Raw journals are archived with hashes, not in git. |
| Limitations: "Synthetic binary registries may not represent complex real-world record workflows." | Kept (Limitations, first bullet). |
| Limitations: "optional lookup condition measures observable tool attempts, not latent intent" | Kept (Limitations, measurement). |
| Limitations: "Canonicalized supplied evidence is a controlled workflow, not arbitrary provider-native tool use." | Already covered (Limitations, canonicalized workflow). |
| Limitations: "uncertainty must cluster repeated generations by item and account for family heterogeneity" | Covered (§3.8; Limitations, provisional inference). |
| LLM usage: "LLM assistance supported research planning, code development and report drafting. All reported empirical results, citations and methodological claims must be verified by the research team before submission." | Kept, and expanded into the final LLM Usage Statement. Verification of citations by Claude is stated separately; the research team's sign-off is left to the authors. |
