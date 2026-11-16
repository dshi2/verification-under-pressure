# HANDOFF — Apart AI × Epistemics sprint (P1 + P2), state at 16:10 IST, 16 Nov 2026

Identical copy in both repos (`verification-under-pressure/rev3/HANDOFF.md`, `scope-of-trust/rev3/HANDOFF.md`).
A new session should read this file first, then each project's `REVISION_3_SPEC.md` and `REPORT_DRAFT.md`.

**Submission deadline: 18:30 IST, 16 Nov 2026.**

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
