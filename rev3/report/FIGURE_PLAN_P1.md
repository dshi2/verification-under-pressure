# P1 main-figure plan (workstream D)

This file records how the manuscript uses the three main figures. WS-C owns the figures and their code (`plot_p1.py`, `review/FIGURES_READY.md`). D takes paths and captions only from `FIGURES_READY.md`, and every value shown must come from `analysis.json`.

The figures are numbered in the order they appear in the text (§4.2 → §4.4). WS-C's file names are unchanged.

| Paper # | Section | WS-C target | File stem (current) | What the reader must see |
|---|---|---|---|---|
| Fig. 1 | §4.2 Primary contrasts by model | E1–E4 forest plot, insistence panel | `fig_p1_estimands` | The four models side by side, the item-t interval (provisional) next to the family-clustered (CR1) interval, and the assigned-denominator bounds. Degenerate intervals hollow. The heterogeneity across models should be the first thing a reader notices. |
| Fig. 2 | §4.3 Where insistence acts | Optional-route funnel: lookup → relevant retrieval → correct | `fig_p1_funnel` | Per model, for neutral vs. insistence × user right vs. wrong: the share of optional trials that attempted, retrieved the relevant record, and ended correct, each with n / denominator. A missing count is drawn as "not exported", never as 0. |
| Fig. 3 | §4.4 Delivery × correctness | E3/E4 interaction | `fig_p1_e4` | Per model, the insistence − neutral accuracy change under optional vs. supplied, in two panels (user right, user wrong). D(u) is the gap within a panel. E3 and E4 are given with their intervals. The reader should be able to see whether D(right) and D(wrong) share a sign. |

**Appendix E figures** (C's existing set): validity, accuracy cell means, lookup cell means, and the authority panel of the forest plot.

**Captions** state that the data are development cases with provisional intervals. They are copied from `FIGURES_READY.md`, edited only for numbering.
