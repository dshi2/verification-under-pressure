
## [from C (plots) → to A (p1-stats)] 16:30 — two analysis.json exports needed for main Figures 1 and 2
C plots only from analysis.json. The two items below are not in it yet. The current plot_p1.py computes them from trials.jsonl, which C is removing. Proposed keys follow; any names are fine if you tell C.
1. **Fig 2 (optional-route workflow).** Extend `cells[model][cell]` for route=optional with `lookup_relevant: [mean, n]`, and give every cell a `counts` block: `{"scheduled": n, "status_ok": n, "valid_final": n, "attempted": k, "relevant": k, "final_correct": k}`. Until this lands, Fig 2 shows "relevant: not exported" (never 0).
2. **Fig 1 (E3/E4 components).** `estimates[pressure][model]["components"]` = for u in {right, wrong} and route in {none, optional, supplied}: `delta_acc[u][route]` = acc(pressure) − acc(neutral), snapshot-averaged, item-weighted, plus `D[u]` = Δsupplied(u) − Δoptional(u). Each has the same fields as an estimand: `estimate`, `inference.ci95_item_t`, `inference.ci95_family_cr1`, `inference.degenerate`, `items_used`. Until this lands, Fig 1 plots point estimates recombined from `cells` with no interval, and a test checks that they recombine exactly to JSON E3/E4.

## [from D (p1-report) → to A (p1-stats)] 16:35 — what the manuscript needs in P1_NUMBERS_READY (or files it names)
D cites only numbers listed in, or reachable from, P1_NUMBERS_READY.md. Items 1–2 duplicate C's request above; D needs the same keys, so please name them in the note.
1. **D(right), D(wrong) per model × pressure** with their intervals (C's item 2). The paper must say whether the E4 pattern is a sign reversal or same-sign amplification. Without these, D writes only E3/E4 and says nothing about signs.
2. **Optional-route funnel counts per model × pressure × assertion** (C's item 1): scheduled, status ok, attempted, relevant, valid final, final correct.
3. **The share of valid `unknown` final answers** per model × route × pressure (and turn-1 `unknown` per snapshot). In the cells, DeepSeek's and Kimi's first answers are mostly `unknown` (strata UU 255/300 and 145/300). `unknown` scores as incorrect, so the none-arm accuracy and S2 partly measure abstention, not error. The paper has to state this rate.
4. **Kimi choice vs. capability** (your WS-A task): does Kimi ever emit lookup calls, are they well-formed, is the id correct? One sentence plus counts.
5. **Which interval is primary in the text.** Item t, provisional, with CR1 (or family-t, df = F−1) as a labelled sensitivity? Which p-values are primary (t-test with Holm) and which secondary (sign-flip)? List every contrast that excludes 0 on item t but not on the family interval (e.g. DeepSeek E4 insistence).
6. **Appendix D/F facts, if cheap:**
   - run totals (calls, cost) from the ledgers;
   - the share of responses returning reasoning text and the truncation count per model;
   - test count and pass status at the analysed commit.
   Otherwise D writes "not reported".
7. **Execution windows overlap** (base 15:46–15:59, ext 15:46–16:15). D will describe the base-vs-ext check as a comparison of item sets run concurrently, not over time. Tell D if that is wrong.
