# Addendum to Research Quality Protocol — Master Checklist v3

Adopt Master Checklist v3 (`MASTER_CHECKLIST_v3.md`; canonical copy in dshi2/research-candidates) as the governing standard. It supersedes EXECUTION_CHECKLIST.md, except for the four additions below, which v3 lacks or states only loosely.

## Additions (merge into v3)
1. **Gate 3 + Gate 6: the harness enforces the matrix.** DESIGN_MATRIX.csv is the harness's *input*, not documentation. Any run that isn't a cell of the frozen matrix is refused in code.
2. **Gate 2/7: cost the full matrix before running.** If the authorized budget can't cover every planned cell, shrink the design (fewer factors, levels or models). Never run a subset of cells.
3. **Gate 7: exploratory backlog.** Ideas that come up mid-run go to BACKLOG.md and never into the running experiment. A backlog item later gets its own small, fully crossed matrix, labeled exploratory.
4. **Gate 6/7: version rule.** Any change to prompts, code, scoring or the dataset after the freeze creates a new version. Incompatible versions are never pooled. Rerun every cell whose stimuli, code path or scoring changed, *plus* every cell it is contrasted with. Hosted models can change silently, so the two sides of a contrast must be run under the same version and in the same time window.
5. **CONTRAST_LEDGER.csv (from the auditor).** One row per prespecified contrast, with these fields:
   - contrast ID
   - hypothesis
   - compared cells
   - intended difference
   - attributes held fixed
   - unavoidable accompanying differences
   - primary outcome
   - unit
   - alternative explanations it cannot rule out
   - statistical method
   - claim boundary

   It catches what a balanced matrix can't: comparing the wrong things.

## Auditor corrections to §2.3 (accepted)
- **Balance is a design goal, not a precondition.** Plan balance for the primary paired contrasts. At analysis, refuse *unaccounted* imbalance; report planned vs. observed per cell; test whether failures depend on condition or model; apply the prespecified missing-data rule.
- **Turn structure, not realized turns.** Freeze the number of user turns, the opportunities to act, tool permissions, token and compute limits, and how evidence is supplied. Realized tool calls are an *outcome* (P1's Δcheck) and are never equalized.
- **Planned incomplete or sequential designs are allowed** if justified and written down before running. Outcome-driven or undocumented asymmetry is not.
- **Multiplicity covers every confirmatory family,** including confirmatory secondary claims.
- **Analysis tests on simulated data** must include known-null and known-effect sets and assert recovery.
- **Randomize within blocks** by model/provider to control time-related drift.
- **Manifests record the actual configuration and deviations,** not only the intended settings.

## Corrections to v3's application section
- **P1 cell count.** The evidence factor has three levels (no tool / optional / supplied), and snapshot version is crossed as well: 2 snapshot × 2 user assertion × 3 pressure × 3 evidence = **36** cells per item × model × repeat (full randomized crossing, P1 rev 3 from caf0977). Realized disagreements are a secondary analysis. The earlier 18-cell disagreement-only design is withdrawn. Primary pressure contrast: insistence vs. neutral (authority secondary).
- **External timestamp (Gate 2).** OSF or AsPredicted registration needs an account created by the user. Agents prepare the text; the user registers it.

## The four kinds of "round" (keep in DESIGN_MATRIX.csv as separate columns)
| Term | Meaning | Counts as an independent case? |
|---|---|---|
| `item_id` | Independent scenario | **Yes** (unit of analysis) |
| `turn` | Conversational step within a trial | No, fixed per condition |
| `repeat` | Same item × cell re-sampled | No, nested in the item |
| `phase` | pilot / exploratory / confirmatory | Never pooled across phases |

## Approvals (no one approves their own work)
| Approval | Prepared by | Granted by |
|---|---|---|
| Scientific (question, novelty, comparisons) | Claude (lead) | Codex + third reviewer |
| Engineering (code matches the frozen protocol, invariants pass) | Claude (lead) | Codex (Agent 5 role) |
| Publication (evidence supports a meaningful claim) | Claude + Codex | **User (PI)** |

## Mandatory artifacts: current status (16 Nov 2026, PR heads)
| Artifact | P1 (verification-under-pressure) | P2 (scope-of-trust) | P3 (research-candidates) |
|---|---|---|---|
| NOVELTY_GATE.md | NOVELTY_GATE_FINAL.md + rev-3 spec §1 (E4 carries novelty) | NOVELTY_GATE_FINAL.md + rev-3 spec §1 | P3_NOVELTY_DOSSIER.md; C1 open |
| PROTOCOL.md | `rev3/REVISION_3_SPEC.md` (draft) | `rev3/REVISION_3_SPEC.md` (draft) | two competing direction drafts (PR #1, PR #2) |
| DESIGN_MATRIX.csv | missing (no items yet) | `rev3/DESIGN_MATRIX_dev.csv` (dev; model/repeat TBD) | not started |
| CONTRAST_LEDGER.csv | `rev3/CONTRAST_LEDGER.csv` | `rev3/CONTRAST_LEDGER.csv` | not started |
| DATASET_CARD.md | missing | partial: `COVERAGE_dev.md` | not started |
| SCORING_SPEC.md | spec §7–8 | `rev3/SCORING_SPEC.md` | not started |
| Design-adherence report | not yet (no matrix) | `rev3/p2v3/matrix_audit.py` (planned matrix + reconciliation) | not started |
| Analysis validated on known effects | `rev3/p1v3/estimands.py` + tests (points, bounds; no intervals) | not yet (coverage simulation specified) | not started |
| PREREGISTRATION.md | not yet (needs frozen spec; OSF by PI) | not yet | not yet |
| IMPLEMENTATION_AUDIT.md, RUN_MANIFEST.json, RAW_LOGS/, ANALYSIS/, INDEPENDENT_AUDIT.md, FINAL_CLAIMS.md | after harness / runs | after harness / runs | after harness / runs |
| BACKLOG.md | in spec §12 | `rev3/BACKLOG.md` | — |

## Second auditor amendments (accepted)
- **Staged freezes:** diagnostic specification → implementation + pilot → revised confirmatory freeze. This avoids circularity: the pilot needs software, and software needs a design.
- **One central question;** a small set of co-primary outcomes is allowed when the claim needs them, with success criteria and multiplicity handling stated.
- **Account for the planned design,** not every conceivable factorial cell.
- **Match what is meant to be controlled,** and name the differences that *are* the intervention.
- **A strong, relevant comparator is required;** replicating a prior setting is used where it establishes the extension, not universally.
- **Untestable assumptions** are stated, justified and sensitivity-tested; conclusions stay conditional on them.
- **Infrastructure failures** never count as model behavior, but are reported as a separate end-to-end reliability endpoint.
- **Every requirement records:** the evidence (an inspectable artifact), reviewer, status, and consequence of failure. "N/A" needs a reason.
- **The machine report is a design-adherence report** (planned vs. executed, configuration diffs, contrast-ledger checks), not merely a count of cells.
- **Editorial:** the master checklist has 10 gates; its introduction's "six" must be corrected.
