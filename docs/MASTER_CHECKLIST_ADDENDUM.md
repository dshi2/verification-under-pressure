# Addendum to Research Quality Protocol — Master Checklist v3

Adopt Master Checklist v3 as the governing standard. It supersedes EXECUTION_CHECKLIST.md, except for the four additions below, which v3 lacks or states only loosely.

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
- **P1 cell count.** The evidence factor has three levels (no tool / optional / supplied), not two. The cells are 3 pressure × 3 evidence × 2 user-correctness = **18** per item × model × repeat, using disagreement trials only. The primary contrast is insistence vs. neutral (authority secondary), per revision-3 notes.
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

## Mandatory artifacts: current status
| Artifact | Status |
|---|---|
| NOVELTY_GATE.md | NOVELTY_GATE_FINAL.md (P1, P2, P3) — done for round 2 |
| PROTOCOL.md | PROTOCOLS_v1.md rev 2 + rev 3 notes — not frozen |
| DESIGN_MATRIX.csv | **Missing**, the next item |
| DATASET_CARD.md | Missing |
| SCORING_SPEC.md | Missing (P2 outcome-level fields defined in rev 3 notes) |
| PREREGISTRATION.md | Codex draft, not aligned with rev 3 |
| IMPLEMENTATION_AUDIT.md | Codex reconciliation_v2.md (19 items); rev-3 items not yet covered |
| RUN_MANIFEST.json | Implemented in the v2 harness |
| RAW_LOGS/, ANALYSIS/ | Mock only; no real data |
| INDEPENDENT_AUDIT.md | Codex audit_report_v2.md covers v2; none for rev 3 |
| FINAL_CLAIMS.md | Not started (after results) |
| BACKLOG.md | Missing (addition 3) |

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
