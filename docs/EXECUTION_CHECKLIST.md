> **Superseded** by Master Checklist v3 + MASTER_CHECKLIST_ADDENDUM.md (Nov 16, 2026). Items 2, 4, 15, 17 and 18 were corrected by the auditor; see the addendum.

# 2.3 Execution discipline (after the novelty gate, before any real run)

Lesson from the shutdown-interference project: sub-experiments ran with uneven rounds, models and settings, so no two cells could be compared and nothing could be concluded. The novelty gate decides *what* to test. This checklist makes sure the runs can actually answer it.

## A. Freeze the run matrix before the first real call
1. **Write the matrix as a file the harness reads:** factors × levels × models × items × repeats, plus fixed settings (temperature, reasoning effort, max tokens, turn count, tool set, system prompt). The harness refuses any run that is not a cell of the matrix.
2. **Every cell gets the same n.** The design is fully crossed, or the incomplete design is planned and written down in advance. No cell is "we'll add it later".
3. **Every model runs every condition,** with versions pinned (exact model ID and date). Adding a model means running the whole matrix for it, or it goes in a separately labeled appendix.
4. **The same number of rounds and turns in every condition.** Fixed horizon. Never "run until something happens".
5. **Change one thing per contrast.** For each primary contrast, list exactly what differs between its two cells. If anything besides the factor differs (wording, length, cues, settings), fix it before running.

## B. Budget and size come from the matrix, not the other way round
6. **Cost the whole matrix before starting.** If it doesn't fit the budget, *shrink the design* (fewer factors, levels or models). Never run a fraction of the cells.
7. **Item count from a precision target,** set using the pilot's variance. The unit is the item; repeats are nested inside it.

## C. Pilot ≠ experiment
8. **The pilot checks measurement only:** parsing, floor and ceiling effects, manipulation checks, positive controls. Pilot data are never pooled with the real runs.
9. **Fix what the pilot found, re-freeze, then start fresh.** Every change goes in a change log with its reason.

## D. Run integrity
10. **Interleave or randomize trial order across conditions,** so time drift or API changes can't line up with a condition.
11. **Write a manifest for every run:** code hash, prompt hashes, matrix hash, model ID, parameters, date, seed. Analysis refuses to combine runs whose manifests differ.
12. **Stopping rule: run the full matrix.** No stopping early because it "looks good" or "looks bad". Reruns only for logged infrastructure failures, under the same rule for every cell.
13. **Keep and report every failure, per cell.** Malformed output, provider error and refusal each get their own status.

## E. No mid-run improvisation
14. **New ideas go to an exploratory backlog,** never into the running experiment. A backlog idea gets its own small, fully crossed matrix later and is labeled exploratory.
15. **Prompt or code change after the freeze = new version,** and *all* cells rerun. Never mix versions in one table.

## F. Analysis is ready before data exist
16. **Write and test the analysis script on mock data first.** Draw empty results tables and figures in advance, with every cell, the primary estimand and its interval.
17. **Run a balance check before any analysis:** print counts per cell × model × status; refuse to analyze if the design is unbalanced beyond the planned failure rate.
18. **Primary vs. exploratory is labeled in the code,** with multiplicity correction applied to the primary family only.

## G. Ownership (5-agent setup)
- **Agent 2 (methodologist)** writes the matrix and the one-difference-per-contrast table (items 1–5).
- **Agent 4 (engineering)** makes the harness enforce the matrix, manifests, randomization and balance check (1, 10–13, 17).
- **Agent 5 (auditor)** refuses sign-off if any cell is unequal, any manifest mismatches, or any run is outside the matrix.
- **The lead** owns the backlog and blocks mid-run additions (14–15).

**Gate question before each run:** "Is this run a cell of the frozen matrix, under the frozen version?" If not, don't run it.
