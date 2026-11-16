# P1 results (published analysis outputs)

These are the aggregated analysis outputs behind `report/REPORT_P1_FINAL.md`, copied from the gitignored `runs/` directories. They contain no raw model responses.

- `combined/`: 60 items and 12 families (the reported set). Files: `analysis.json` (the single numerical source), `contrasts.csv` (every estimand with every interval type), `funnel.csv`, `interaction.csv`, `validity.csv`, `unknown_answers.csv`, `batches.csv`.
- `base/` and `ext/`: each item set analysed alone.
- `audit/independent_check.json`: the separate recomputation (`verify_p1_independent.py`), with 0 mismatches.
- `RAW_ARCHIVE_SHA256.txt`: SHA-256 hashes of the archived raw journals.

Regenerate from `rev3/` with `python3 analyze_p1.py --run-dir runs/p1_dev_eval_v2 runs/p1_ext_v2 --out runs/analysis_combined --strict`. Analysis code: commit `8b6af31`.
