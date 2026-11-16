# Response to attached review — P1

Reviewed head: **1247db4c8e75704b6fc1eb8c4169ff1ee06aedb4**, PR #1, branch p1-revision-3. The attached review examined 7f5967f; its conclusions must be reconciled against the newer design.

## Finding disposition

| Attached finding | Current evidence | Disposition |
|---|---|---|
| Eighteen scheduled branches do not guarantee balanced initial-correctness strata | REVISION_3_SPEC §§2–4 now uses 36 assigned cells; user correctness is randomized independently of actual first answer. Actual disagreement is secondary. Full crossing introduced at caf0977b1428637cdae20d1efbd72c200a0280c5. | Superseded for primary identification; still relevant to precision/interpretation of the secondary subset. |
| Simulate the joint first-answer distribution and report contributing items | §3 and §9 now explicitly require joint strata and effective item counts; 7834fd3516b1eeb9626384120a4469cf1ef9dc0a. | Addressed as a specification requirement, not an executed simulation. |
| Demotion of E4 requires reopening novelty | §§1,7,12 now say exactly this; more independent items first, then a revised contribution if precision remains inadequate. | Addressed at 7834fd3. The provisional 7.5-point precision floor still needs scientific justification and simulation. |
| Diagnostic implementation follows revised spec | New p1v3/estimands.py and tests exist; archive remains historical. | Six tests independently executed and passed at this head. These test point estimates, not a live harness or confidence intervals. |
| No CI checks | Current PR has successful unittest checks, including run 43805217591. | Historical statement no longer current. |

Latest wording changes at 1247db4 address agreement-compatible pressure descriptions. No paid calls, merges or scientific freeze were performed in this response.

## Two mathematical specification corrections remain

### R1 — Retrieval decomposition is not a product of differences

REVISION_3_SPEC.md §7, line 143 states:
Delta_relevant = Delta_attempt × P(relevant | attempted).

This is not generally true when conditional relevance differs by arm. Let a_p=P(attempt|p), q_p=P(relevant|attempt,p). The arm-level identity is r_p=a_p q_p; the contrast is:

**r_I − r_N = a_I q_I − a_N q_N
= q_N(a_I−a_N) + a_I(q_I−q_N).**

Example: both attempt rates .5; conditional relevance .2 under insistence and .8 under neutral. Delta_attempt=0, but Delta_relevant=−.3. The current code estimates the two contrasts separately correctly; its existing test already demonstrates that attempts can stay unchanged while relevance changes. Fix the prose, not that correct code behavior. If an arm has no attempts, conditional relevance is undefined; report it as such, without dividing by zero.

### R2 — All-missing-zero versus all-missing-one is not a contrast bound

§7 line 151 asks for assigned-denominator bounds by setting missing outcomes to 0 and then 1. Those are two imputations, but do not generally bound a difference or interaction.

Reproduced using the committed estimator: when attempts are missing in both optional arms, globally filling 0 gives E1=0 and globally filling 1 also gives E1=0. Valid arm-specific completions give **−1 and +1**.

For a fixed linear contrast sum(w_j mu_j), minimize by assigning missing positive-weight outcomes to 0 and negative-weight outcomes to 1; maximize with the reverse assignments. Keep planned denominators and item weights fixed. For E3/E4 use their actual signed coefficients. If additional constraints couple outcomes, minimize/maximize over those admissible completions instead. Structural turn-1 exclusions must be distinguished from turn-2 missing outcomes in the target population.

The estimator currently supplies complete-observation point estimates only and drops incomplete items per estimand. Counting those drops is useful, but does not make the point estimate intention-to-treat. Add signed bounds as a separate implementation; do not label a bootstrap CI around a selected complete-case estimate an assigned-population effect.

See reproduce_missingness_counterexample.py in this review folder. These are specification counterexamples, not a claim that the absent bounds implementation already returns invalid intervals.

## Additional reporting issue for implementation

_cell_means counts None across every route. Therefore lookup missing_obs includes structurally inapplicable none/supplied trials, not just missing optional-arm events. Scope each diagnostic denominator to the estimand's eligible cells and report not-applicable separately before using this count as a reliability statistic.

## Next decision

Continue offline development. Correct the two mathematical statements before implementing the sensitivity analysis; retain the accepted E1 and E4 changes. A real precision/coverage simulation, independently validated pressure wording and a tested execution harness remain necessary at their stated milestones. No new general checklist is requested.
