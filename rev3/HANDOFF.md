# HANDOFF — Apart AI × Epistemics sprint (P1 + P2), state at 16:10 IST, updated 16:25 IST, 16 Nov 2026

Identical copy in both repos (`verification-under-pressure/rev3/HANDOFF.md`, `scope-of-trust/rev3/HANDOFF.md`).
A new session should read this file first, then each project's `REVISION_3_SPEC.md` and `REPORT_DRAFT.md`.

**Submission deadline: 18:30 IST, 16 Nov 2026.**

## UPDATE 16:25 IST (new account). This section supersedes the status lines in §3–§5 below

Sections §0–§2 (ground rules, repos, infrastructure) still apply unchanged.

### U1. Run status (checked from summary.json and the logs, not estimated)

| Run | Status |
|---|---|
| P1 `runs/p1_dev_eval_v2` (base, 24 items) | COMPLETE: 17,280 / 17,280 trials ok |
| P1 `runs/p1_ext_v2` (ext, 36 items) | COMPLETE: 25,920 / 25,920 trials ok. The runner died at 53,279 / 53,280 calls when the old account's session ended. It was resumed at 16:14 and finished at 16:15. No duplicates. |
| P2 `runs/p2_dev_eval_v1`, `runs/p2_ext_v1` (batch 1, 12 cases) | COMPLETE: 3,360 + 3,360 ok |
| P2 `runs/p2_ba_v1`, `runs/p2_bb_v1`, `runs/p2_bc_v1` (batch 2, 3 × 8 cases) | LAUNCHED 16:15 (Terminal tabs "P2 ba/bb/bc run"), ETA about 16:25. Cases committed in b7c2279 before launch. 238 tests OK, and an offline dry run completed 4,480 / 4,480 per batch. The stimuli_dev/ext hashes are unchanged. |

Raw-data backup, outside both repos and not in git:
- Location: `/Users/divyansh/Documents/research_active/ai-epistemics/_backup_raw_2026-11-16/`
- Contents: `p1_runs_v2_and_v1.tgz`, `p2_runs_batch1.tgz`, `SHA256SUMS.txt`, `SHA256SUMS_files.txt` (per-file hashes of journal / trials / responses / manifest / summary).
- Batch 2 is added to the backup when it completes.
- `runs/` is gitignored, so GitHub has none of the raw data.

### U2. Analyses and figures that exist now

- **P1:** `runs/analysis_base/`, `runs/analysis_ext/` and `runs/analysis_combined/`. Each has `analysis.json`, `analysis.md`, and `figures/` with e4, funnel, estimands, accuracy, lookup and validity figures in pdf/png/svg. All were generated at 16:16 from the v2 runs only.
- **P1 combined headline (insistence; item t 95% CI, provisional):**
  - E1 Δlookup:
    - Qwen −49.7 pp [−52.3, −47.1]
    - gpt-oss −10.0 [−12.5, −7.5]
    - Kimi −5.8 [−8.7, −2.8]
    - DeepSeek −1.3 [−2.0, −0.7]
  - E2 Δaccuracy, supplied: within 2.4 pp for every model.
  - E3 delivery effect: Qwen +25.6 [+23.4, +27.8]; gpt-oss +4.5; Kimi +5.1; DeepSeek −1.8.
  - E4: Qwen −40.5 [−45.5, −35.5]; gpt-oss −4.7.
  - Neutral optional lookup rate: DeepSeek 100%, gpt-oss 99%, Qwen 79.8%, **Kimi 16.8%** (a validity limit for Kimi's E1).
  - Authority: mostly null; Qwen E1 +4.2, E4 +8.2.
  - Base vs ext (Welch): no insistence difference excludes 0. The one exception is gpt-oss authority S2 (+7.4, secondary).
- **P2:** `runs/p2_batch1_combined/` (analysis.json and figures). It was produced by the OLD analysis code, before the uncommitted secondary/denominator diff. It must be regenerated after the code review in WP-B.

### U3. Uncommitted work left by the old account's sessions (preserve it; owners are named in U4)

- **P1:** `sim_p1_coverage.py`, `SIM_P1_COVERAGE.md` and `sim_out/` are complete but untracked.
- **P2, modified files:**
  - `analyze_p2.py`: S1–S6 secondary family, plus the planned_keys-from-manifest denominator fix (lines ~97, ~176, ~658).
  - `plot_p2.py`: V on the ladder, renumbered figures.
  - `SIM_P2_ALLPAIRS.md`, `sim_p2_allpairs.py`, `sim_out/`.
  - `REPORT_DRAFT.md`: partly filled with batch-1 numbers, 19 `[[...]]` placeholders left.
- Tests pass on this state (238 OK, 1 skipped). None of it has been reviewed.

### U4. Parallel work plan. Each work package (WP) has one owner, and nobody edits another WP's files

All sessions share the same local checkouts. Do not use worktrees: the raw `runs/` exist only here.

**Git rules for every session:**
- `git add <explicit paths>` only. Never `git add -A`, `git add .` or anything under `runs/`.
- Before every push, run `git pull --rebase`. If you hit an index.lock, wait and retry.
- Short neutral commit messages ending with the Co-Authored-By line from §0.

**Familiarise first (mandatory before editing anything).** Read, in full:
1. This HANDOFF.
2. `REVISION_3_SPEC.md`.
3. `CONTRAST_LEDGER.csv`.
4. The scoring spec (P2: `SCORING_SPEC.md`, `GOLD_LABELS.md`).
5. The analysis code (`analyze_p*.py`, `p1v3/` or `p2v3/`).
6. The relevant `analysis.md` outputs.
7. `REPORT_DRAFT.md`.
8. `git log --oneline -30`.

Then post a short state-of-understanding message (10–15 lines: what the study tests, what the data show, what your WP must deliver, risks) before the first edit.

These workstreams follow the reviewer's second handoff (A–F).

**Data flow.** Analysis JSON/CSV is the single numerical source of truth, and it flows A/B → C → D/E.
- When a stats workstream has verified numbers, it commits them and writes `rev3/review/P{1,2}_NUMBERS_READY.md`. The note gives the commit, the analysis dirs, and which numbers are final versus provisional.
- C plots only from those analysis files.
- D/E cite only those numbers. Until the note exists, they work on methods, related work, limitations and citations.

| WS | Session | Owns (only these files; everything is under `rev3/`) | Deliverable |
|---|---|---|---|
| A | p1-stats | P1: `analyze_p1.py`, `p1v3/` analysis modules (`estimands.py`, `inference.py`), P1 tests except plot tests, `sim_p1_coverage.py`, `SIM_P1_COVERAGE.md`, `sim_out/`, `runs/analysis_*/analysis.{json,md}` and new CSV tables, `review/P1_NUMBERS_READY.md`, `review/REVIEW_PACKET_P1_STATS.md` | Run WS-A tasks 1–11 of the reviewer's handoff. The coverage sim (complete, untracked) recommends the family-clustered t interval (df = F−1) or a family-level sign-flip test with Holm, and rejects the item-level sign-flip (type-I error 0.10–0.22) and the bootstrap. Apply it as a reported, labelled sensitivity. The prespecified-method decision belongs to the PI, so do not silently switch the primary. Check Kimi's tool use as choice versus capability: does it ever call the tool, and are the calls well-formed? |
| B | p2-stats | P2: `analyze_p2.py`, `p2v3/stats.py` (and other non-plot analysis modules), P2 tests except `tests/test_plot_p2.py`, `sim_p2_allpairs.py`, `SIM_P2_ALLPAIRS.md`, `sim_out/`, analysis dirs under `runs/` (`p2_batch1_combined`, `p2_<batch>_analysis`, `p2_all_batches`) except their `figures/`, `review/P2_NUMBERS_READY.md`, `review/REVIEW_PACKET_P2_STATS.md` | Run WS-B tasks 1–15. Review and commit the uncommitted `analyze_p2.py` diff: S1–S6 and the manifest denominator. Add regression tests for a wholly absent case and a wholly absent cell. Produce per-batch, pooled and between-batch results (spec §7a) once batch-2 `summary.json` shows complete. Give the zero-event bound at the case level. Extract V-cell response reasons for a qualitative check. Sim: keep the all-pairs Tango-c-cc interval (calibrated by simulation only). P4 stays descriptive at this case count. |
| C | plots | P1 `plot_p1.py`; P2 `plot_p2.py`, `tests/test_plot_p2.py`, new P1 plot tests; every `figures/` subdir under the analysis dirs; `review/FIGURES_READY.md` | Run WS-C. Palette: #0072B2, #D55E00, #009E73, #CC79A7, with distinct markers, fixed model → colour across both papers. Three main figures per paper, exactly as the reviewer specified. PNG/PDF/SVG. Add tests that plotted values equal the analysis-JSON values. Never show a missing value as 0, and never use synthetic data in a paper figure. |
| D | p1-report | P1: `REPORT_DRAFT.md`, `report/`, `review/REVIEW_PACKET_P1.md` | Run WS-D. Fill all 41 `[[...]]` placeholders only from P1_NUMBERS_READY/FIGURES_READY. The story: the decision to verify, versus retrieval, versus use of supplied evidence, crossed with assertion correctness. Check every citation. Write a paste-ready `report/REPORT_P1_FINAL.md`. |
| E | p2-report | P2: `REPORT_DRAFT.md` (keep its uncommitted progress), `report/`, `review/REVIEW_PACKET_P2.md` | Run WS-E. Lead with the null primary result. Discuss the floor as scope discrimination versus task explicitness. V is exploratory with a contested gold label. Keep practice / outcome / welfare / cause distinct. Write a paste-ready `report/REPORT_P2_FINAL.md`. |
| F | main (orchestrator, this account's first session) | `HANDOFF.md` (both repos), `results/` (both repos), `_backup_raw_2026-11-16/`, batch-2 runs | Run WS-F. Back up and hash the raw data. Publish a tracked, sanitized `rev3/results/` (analysis json/md/csv, figures, manifests, raw SHA-256, a secrets scan). Run the final audit: no placeholders, references real, links open. Route ChatGPT reviews to the right session. |

**No two sessions edit the same file.** If a WS needs a change in another WS's file, it writes the request into `review/REQUESTS.md` (append only, prefixed `[from X → to Y]`) and tells the user.

### U5. Claim boundaries every report must respect (from the reviewer)

- Every case and item is builder-written development data. None of it is confirmatory, and none of it is independently validated.
- Repeats are not independent cases. 5 × 12 is not 60 cases.
- **P2 zero events:**
  - Give the case-level bound as the headline. With n cases and zero events in every case, the rule of three gives roughly 3/n: 25% at 12 cases, about 8% at 36.
  - A trial-level bound (≈4.9% with 60 trials per model per cell) may appear only if it is labelled as assuming independent trials.
  - A [0, 0] case-t interval is degenerate. It does not show precision.
- **P4 is not shown noninferior.** No margin is fixed, so 100% vs 100% is "no decision", and the provisional lower bound (−0.30) would fail any reasonable margin.
- **V is exploratory.** Its gold label is contested (spec §8.6). Call it "marked established after an unscoped stamp", not "error", unless the response reasons support that. It is not a confirmed primary hypothesis.
- **Nulls stay nulls.** No equivalence claim from a nonsignificant result, and no claim that models "cannot" make the error.
- **P1:** no SESOI is fixed, so there are no equivalence statements. Kimi's low neutral lookup rate (16.8%) limits its E1. Intervals are provisional until the coverage sim's method choice is applied.
- **Batch 2 (P2)** was commissioned after batch 1 had run but before its contrasts were analysed (spec §7a, commit c22ff29). Report it as later development batches, not as replication.
- **Never fill in** expert verdicts, author names, affiliations or approvals.

### U5b. Claims in the current drafts that are UNSAFE until fixed (found at 16:20)

- **P2 abstract and Table 2:** "one-sided 95% upper bound 4.9% per model, treating trials as independent". This treats 60 repeats as independent. Replace it with the case-level bound as the headline.
- **P2 Table 2, P4 column:** "0.000; LB −0.30" is correct as a number, but the text must say "no decision; not noninferior", never "noninferior".
- **P2 batch-1 figures** in `runs/p2_batch1_combined/figures` came from the pre-review code. Regenerate them.
- **P1 intervals:**
  - The item-level t and sign-flip intervals are anti-conservative under family heterogeneity (sim: coverage down to 0.84; sign-flip type-I error up to 0.22).
  - Every P1 interval stays "provisional". The family-t interval goes beside it.
  - Small effects that exclude 0 only on item-level intervals get flagged, e.g. DeepSeek E4 +2.5 [+0.4, +4.6], whose CR1 interval is [−0.0, +5.1].
- **P1 ext figures** were produced by the current `plot_p1.py`, but WS-C has not checked them against the tables.

### U6. ChatGPT as strict reviewer (no self-approval)

Each WP writes `rev3/review/REVIEW_PACKET_<WP>.md` and pushes it. The packet contains:
1. Commit hashes and GitHub links for every change.
2. A claim → source table: each number in the report, with its file, JSON key and value.
3. Every deviation from the spec or ledger.
4. Known weaknesses.
5. Specific questions for the reviewer.

The user pastes the packet (and the report) into ChatGPT, then pastes ChatGPT's verdict back into the same session. A WP is done only after the review's blocking points are fixed or explicitly rebutted in writing. ChatGPT has the longer project history, so where it conflicts with a session's own judgement on scientific framing, flag the conflict to the user rather than silently overriding ChatGPT.

### U7. Needs the user

1. **Google Docs.**
   - The Docs connector does not respond, and the Drive connector "requires additional permissions".
   - Either reconnect Google Drive with write access in the app's connector settings, or download each Doc (File → Download → Markdown) into `rev3/report/gdoc_current.md` in each repo, so the report sessions can reconcile ChatGPT's earlier edits.
   - Fallback for the final copy: in Google Docs, Tools → Preferences → enable Markdown, then Edit → Paste from Markdown with `report/REPORT_P*_FINAL.md`.
2. SESOIs and the P4 margin. Otherwise reports say "no decision".
3. After the batch-2 runs finish (about 16:25), revoke and rotate the OpenRouter key and clean `~/.zsh_history`.

### U8. Timeline to the 18:30 IST deadline

| Time | Milestone |
|---|---|
| 16:45 | Every WP has posted its understanding message |
| 17:15 | P2 pooled numbers ready |
| 17:30 | Report numbers frozen; review packets to ChatGPT |
| 18:00 | ChatGPT fixes applied; final copies in the Google Docs |
| 18:15 | Final link check |
| 18:30 | Submit |

If batch 2 is late, the P2 report goes out on batch 1 and states that batch 2 was incomplete (spec §7a rule).

---

## 0. Ground rules that must survive the handoff

- **Roles.** Claude builds and operates. ChatGPT reviews; the user pastes its output in. No self-approval.
- **Commits.** Push every change. Use short neutral commit messages, each ending:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  Do not merge PRs.
- **Secrets.**
  - Never read, print or commit the API key.
  - The key lives only in `~/.openrouter_key` (mode 600). `launch_run.sh` reads it into the child process env.
  - The user once pasted a key into chat and shell history. Treat that key as compromised:
    - After all runs finish, the user should revoke and rotate it on OpenRouter.
    - They should also remove the lines containing it from `~/.zsh_history`.
    - Do NOT revoke while runs are still using it.
- **Privacy.** The user's email is private.
- **Files.** Do not delete files without approval.
- **Expert verdicts.** Never fill them in.
- **Data labels.**
  - Never relabel dev or builder-written data as confirmatory.
  - Report every prespecified outcome, null or not.
  - Intervals are labelled provisional/descriptive: no SESOI or margin has been given.
- **User preferences.**
  - Full runs only: no trial or pilot calls.
  - Maximum concurrency: 256 per model; adjust only if that fails.
  - No cost caps or cost drama. Parallelise aggressively. Optimise for time.
  - Don't be sycophantic. Avoid overengineering: runs come first.
- **Downloaded files.** Open them in their own directory and run Python on them with `python3 -I`.

## 1. Repos, branches, folders, links

| | P1 "Verification Under Pressure" | P2 "Scope of Trust" |
|---|---|---|
| GitHub | `dshi2/verification-under-pressure` | `dshi2/scope-of-trust` |
| Branch | `p1-revision-3` | `p2-revision-3` |
| Local | `/Users/divyansh/Documents/research_active/ai-epistemics/verification-under-pressure/rev3` | `/Users/divyansh/Documents/research_active/ai-epistemics/scope-of-trust/rev3` |
| Report Google Doc | https://docs.google.com/document/d/1_v5ev4v2f-FH8ZK3938FkITJnO8sSVES-I-VLqyRjwA/edit | https://docs.google.com/document/d/1FazmScIfkGSuEudv1xz4qniqO5df87mAgZuNqsq2Vs8/edit |
| Local report draft | `rev3/REPORT_DRAFT.md` | `rev3/REPORT_DRAFT.md` |
| GitHub review issues | #3 | #5 |

- **Google Docs connector.** It was unresponsive earlier, so the drafts are local markdown. If it still fails, the user pastes the drafts in manually.
- **Tests.** Run them from `rev3`: `python3 -m unittest discover -s tests` (P2: 119 OK). Running from the repo root gives import errors.

## 2. Shared infrastructure (identical in both repos)

- **`llmrun.py`** is a stdlib OpenRouter runner.
  - Provider pinning: order=[tag], allow_fallbacks false, require_parameters, quantizations, data_collection deny.
  - Append-only fsynced `journal.jsonl` (intent / dispatch / result / void / attempt_error / session).
  - Requests in flight are deduplicated. An AIMD limiter halves concurrency on a 429.
  - Retries: 6 per request, plus 2 re-passes; timeout 600 s.
  - `--resume` refuses a changed config, stimuli, design or repeats.
  - `summary.json` reports reserved_intents, dispatched_requests, provider_responses, ambiguous_attempts and unique_stage_results.
- **`supervise.py`** auto-resumes after transient stops or a crash after 120 s.
  - It stops on: PAUSE file, Ctrl-C, 401/402/403, error rate, disk, refusal to start, or 3 cycles with no progress (circuit breaker).
  - Exit codes: 0 complete, 3 PAUSE, 4 needs a person, 5 refused, 6 max resumes, 7 circuit breaker.
  - "complete" means every planned task ran. It is not a data-quality verdict.
- **`launch_run.sh <p1|p2> <log-name> <cmd...>`** waits for the key file, then runs `caffeinate -i python3 supervise.py -- <cmd>`. It tees output to `logs/<log-name>.log`.
- **`save_key.sh`** (P2) prompts for the key with hidden input and writes `~/.openrouter_key`.
- **Settings.**
  - Models (text-only, open-weight): gpt-oss-120b, DeepSeek-V3.2 (reasoning on), Qwen3-235B-A22B-2507, Kimi-K2-0905.
  - Provider-default sampling; max_tokens 8192; 5 repeats.
- **Exact commands used** (each in its own Terminal tab, from rev3; rerunning the same command resumes safely):
  - P1 base: `./launch_run.sh p1 p1_base_v2 python3 run_p1.py --config configs/p1_dev_eval_v2.json --repeats 5 --run-dir runs/p1_dev_eval_v2`
  - P1 ext: `./launch_run.sh p1 p1_ext_v2 python3 run_p1.py --config configs/p1_dev_eval_v2.json --item-set ext --repeats 5 --run-dir runs/p1_ext_v2`
  - P2 base: `./launch_run.sh p2 p2_base python3 run_p2.py --config configs/p2_dev_eval_v1.json --stimuli stimuli_dev.jsonl --repeats 5 --run-dir runs/p2_dev_eval_v1`
  - P2 ext: `./launch_run.sh p2 p2_ext python3 run_p2.py --config configs/p2_dev_eval_v1.json --stimuli stimuli_ext.jsonl --repeats 5 --run-dir runs/p2_ext_v1`
  - P2 batch 2 (once cases are committed; use the stimuli filenames the case sessions produce): same as P2 ext with `--stimuli stimuli_ba.jsonl --run-dir runs/p2_ba_v1`, and likewise for bb and bc.

## 3. P1 — status and what is next

**Design.**
- Each item has 36 cells: snapshot × assertion right/wrong × pressure neutral/insistence/authority × route none/optional/supplied.
- Turn 1 answers from an excerpt. In turn 2, pressure asserts a value.
- Estimands: E1 Δattempt (lookup), E1b, E2 Δaccuracy supplied, E3 delivery effect, E4 moderation, plus secondary S2.
- PRIMARY = E1, E2, E3, E4, with Holm correction over the t-test p values.
- Inference: the item is the cluster. Item t interval; CR1 family-clustered interval; sign-flip test as secondary; equal-family estimate; leave-one-family-out; a degenerate flag.

**Runs.**

| Run | Config | Items | Status |
|---|---|---|---|
| `runs/p1_dev_eval_v2` (base) | `configs/p1_dev_eval_v2.json` | 24 | COMPLETE: 17,280 trials, all ok |
| `runs/p1_ext_v2` (ext) | `configs/p1_dev_eval_v2.json` | 36 (`p1v3/stimuli.py` `ext_items`) | about 70% at 16:04, ETA a few minutes |

- In config v2, DeepSeek is pinned to SiliconFlow fp8, because AtlasCloud returned 404 on the supplied route.
- `runs/p1_dev_eval_v1` and `runs/p1_ext_v1` are ABANDONED (DeepSeek serving bug). Never pool them.
- Logs: `logs/p1_base_v2.log`, `logs/p1_ext_v2.log`.

**Next steps.**
1. When ext finishes:
   ```
   python3 analyze_p1.py --run-dir runs/p1_dev_eval_v2 --out runs/analysis_base
   python3 analyze_p1.py --run-dir runs/p1_ext_v2 --out runs/analysis_ext
   python3 analyze_p1.py --run-dir runs/p1_dev_eval_v2 runs/p1_ext_v2 --out runs/analysis_combined
   ```
   Then run `plot_p1.py` on each. The figures are fig_p1_e4, fig_p1_funnel, fig_p1_estimands, plus the accuracy, lookup and validity figures.
2. Check that Kimi-K2 makes tool calls at all: early trials showed 0 lookups. If it never does, report it as a model-level validity limit. A forced-tool diagnostic only if justified.
3. Check validity and parse rates, the strata, and the batch comparison (Welch base vs ext).
4. Fill the placeholders in `REPORT_DRAFT.md` (about 47 `[[...]]`), then move the draft into the P1 Google Doc.
5. Review and commit the untracked `sim_p1_coverage.py`, `SIM_P1_COVERAGE.md` and `sim_out/` from session p1-coverage-sim, once it finishes.

## 4. P2 — status and what is next

**Design.**
- 14 cells: A, A0, B, C, C_prime, D1, D2, V, E×3 directions, E_scope×3. Two contexts: attribution and belief.
- Primary outcome: `unsupported_q_obs`, meaning Q_obs is marked established_true where gold does not accept it.
- Contrasts:
  - P1: B−A.
  - P2: B−D1.
  - P3: C−B.
  - P4: noninferiority of E_scope vs E on correct acceptance.
- Inference: the pairing-free all-pairs Tango-c-cc interval, plus a case-level t interval. decide() returns "no decision" without a SESOI or margin.
- Secondary: V1–V3, S1–S6, X1, X2.

**Batch 1.** COMPLETE, 12 cases (base 6 + ext 6).

| Run | Trials | Dispatched | Ambiguous | Cost |
|---|---|---|---|---|
| `runs/p2_dev_eval_v1` | 3,360 ok | 3,928 | 436 | $6.77 |
| `runs/p2_ext_v1` | 3,360 ok | 4,084 | 608 | $8.17 |

Combined analysis: `runs/p2_batch1_combined/analysis.json`.

**Batch-1 RESULT (central, report it).**
- **Primary is at the floor.** `unsupported_q_obs` = 0 in every A/A0/B/C/C_prime/D1/D2/E/E_scope cell, for all 4 models.
  - No model ever marked the unchecked outcome claim established after a practice audit.
  - So P1–P3 estimates = 0.000. The case-t interval is degenerate [0, 0]. The all-pairs interval is ±0.301, which is very conservative at zero events.
  - Report an exact zero-event upper bound alongside it: rule of three, about 3/n per arm, with n = 60 per model per cell.
- **E/E_scope are at the ceiling.** V1 = V2 = 1.0, so P4 is trivially noninferior.
- **Manipulation check:** V3 = 1.0.
- **The V cell (unscoped verification stamp) is the only cell where the error fires:**

  | Model | Q_obs marked established |
  |---|---|
  | Qwen3-235B | 53% |
  | Kimi-K2 | 5% |
  | DeepSeek | 0 |
  | gpt-oss | 0 |

  This is the main positive finding: the scope error shows up when the stamp does not state its scope, not when a practice audit's scope is visible.
- **Kimi data quality:** parse 1,649 ok, 28 malformed, 3 invalid; 28 truncated.
- **Interpretation.**
  - A spillover null with a tight bound: models scope practice audits correctly.
  - Model-specific vulnerability to unscoped stamps.
  - Do not oversell: the cases are builder-written dev data, not confirmatory.

**Batch 2 (strengthening).**
- Spec §7a (commit c22ff29) fixed the rule: 3 × 8 new cases (ba, bb, bc), authored by sessions p2-cases-a, p2-cases-b and p2-cases-c.
- When they finish:
  1. Review the cases. Check that the stimuli_dev and stimuli_ext hashes are unchanged and that tests pass.
  2. Commit.
  3. Launch `runs/p2_ba_v1`, `runs/p2_bb_v1` and `runs/p2_bc_v1` in parallel via `launch_run.sh`.
  4. Analyse all batches combined, plus per batch.
- Each batch costs about $7 and takes about 10–15 min at 256 concurrency.

**Other pending P2 items.**
- **p2-secondary session:** it owns `analyze_p2.py` and `tests/test_secondary_p2.py`. Review its uncommitted diff and commit it.
  - Open ChatGPT point to apply there: build the analysis denominator from the frozen design manifest, not from observed rows, so a wholly missing case or cell counts as missing in the worst/best bounds.
- **p2-figures-sim session:** done. Its uncommitted diff covers `plot_p2.py` (validity figure reads ci95_case_t; degenerate cells hollow) and `SIM_P2_ALLPAIRS.md`. Its synthetic figures under `sim_out/synth_analysis/figures` were regenerated or deleted. Review, then commit.
  - Sim result: all-pairs Tango-c-cc coverage was within 3% of nominal at all 48 points (conservative). The case t interval missed at 21 of 48.
- **ChatGPT suggestion (exploratory):** within-response association between unsupported attribution and an approval recommendation. Report it as descriptive only.
- Run `plot_p2.py` on `runs/p2_batch1_combined`. Fill the `REPORT_DRAFT.md` placeholders. Move the draft into the P2 Google Doc.

## 5. Linked Claude sessions (desktop app, this account; ids are `local_...`)

| Name | Session id | State at handoff | Work |
|---|---|---|---|
| p2-cases-a | local_eafee55c-823f-4035-af7f-95bacc854c53 | working | batch-2 cases `ba` |
| p2-cases-b | local_c09d9d42-ab3f-44c7-b31a-6fd03d2e803d | working | batch-2 cases `bb` |
| p2-cases-c | local_e1243e8d-6c8a-4784-a06f-6fb3e6fd8e6a | working | batch-2 cases `bc` |
| p2-secondary | local_79a3fdcd-bcea-4dbc-a998-4173634311e2 | working | P2 secondary analyses in analyze_p2.py |
| p2-figures-sim | local_e8a816a1-e802-4478-ab03-d6835acacafa | idle / done | P2 figures + coverage sim |
| p1-coverage-sim | local_b4a679e7-0104-4ea2-b914-28c534913cd0 | working | P1 interval coverage sim |
| p1-report | local_901f8980-1011-4ce5-804a-73f29e9d019f | idle | P1 report draft |
| p2-report | local_7d08cb70-c3f7-49f5-a35d-a38e872afdcb | idle | P2 report draft |

If the user switches accounts, these sessions may not be reachable. Their output is in the working trees: check `git status` in both repos.

## 6. Needs the user (cannot be decided by Claude)

- SESOIs for P1 E1–E4 (the spec floor for E4 is 7.5 pp) and for P2 P1–P3.
- The P2 P4 noninferiority margin (the spec proposes 5 pp).
- Expert verdicts; independent (non-builder) cases for a confirmatory run.
- Revoking and rotating the exposed key after the runs, and cleaning `~/.zsh_history`.

## 7. Latest commits at handoff

- **P1** `p1-revision-3`: 27dbb7f (report draft), b9bce70, 71e7b18, c42b825, b953951, 9df359c, d25bfa9, 23a1c1e (ext items).
- **P2** `p2-revision-3`: c22ff29 (batch-2 rule), 0efd94b (report draft), 6c0afb3, 9d3b78e, ddea64e, d7b6d9f, 3d0e8a1, c59cebf.
