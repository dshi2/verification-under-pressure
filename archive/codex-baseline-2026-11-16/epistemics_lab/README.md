# Revision 2 — Verification Under Pressure and The Scope of Trust

The authoritative design is `../research/PROTOCOLS_v1_revision2.md`. It is a design draft, not frozen or preregistered. This implementation is version 0.2.0. Use `harness_v2.py`; the former uncapped HTTP prototype has been removed from this active package and preserved in the original archive for audit.

No real-model experiments or human domain validation have been performed. Python standard library only; no package installation needed.

## Run the offline checks

From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 harness_v2.py generate --output new_dataset.json --items 12
PYTHONDONTWRITEBYTECODE=1 python3 harness_v2.py run --dataset new_dataset.json --output simulated/my_oracle --mock oracle
PYTHONDONTWRITEBYTECODE=1 python3 harness_v2.py analyze simulated/my_oracle --kind simulated --output simulated/my_oracle/analysis.json
```

Output directories must be new. Fixture outputs are confined to `simulated/`; real outputs to `real/`. Analysis requires an explicit kind and validates directory, manifest, and row provenance. Mock outputs are software checks with privileged truth access, never model findings.

## Projects

**P1:** three pressure conditions (neutral, insistence, irrelevant-domain authority), three evidence routes (none, optional, supplied), independently right/wrong user assertions and accurate/inaccurate older snapshots. The first answer is actually generated and cached across matched conditions. Neutral assertions sometimes agree with the initial answer; the implementation does not invent disagreement. Concession means changing from a different initial answer to the user assertion, with the unconditional randomized denominator retained.

`lookup_record(id)` is a native function call. Supplied evidence injects the same canonical assistant-call/tool-result pair that optional retrieval returns. Provider call IDs are normalized in both histories; original responses remain logged. Tool and system definitions are identical across arms. Matching format does not eliminate all timing, initiation or salience differences. Wrong IDs count as checked but not relevant. The analysis uses all assigned trials, not a selected group of checkers.

The neutral optional check rate is a pilot gate. Below 10% triggers task revision and a fresh pilot, never a prompt change in one arm only. A ceiling is reported rather than engineered away. Pressure manipulation and irrelevant-expertise perception still require human checks. Equal character length and neutral filler are engineering controls, not validated semantic equivalence.

**P2:** A, A0, B, C, C_prime, D1, D2, E and V. A/B/D1/D2 retain the identical practice fact. C preserves B's exact confirmation and adds scope; C_prime includes the same confirmation and scope in structured fields. A0 is explicitly exploratory. Auditor and issuer identity remain fixed. Verification placement varies by item/seed, paired across arms. Equal length is measured in characters, not tokens.

Cases operationalize improved welfare as a specific observed animal-based metric between two periods, without claiming causation or total welfare improvement. E supports or contradicts the claim in the same underlying world. The belief targets come from a stipulated fictional probability model, not real welfare estimates. A0 has no practice information; D2's other-facility check is explicitly independent. Primary attribution is captured by the categorical response and claims_verified; free-text rationale is retained in a blinded grading packet. Human/LLM free-text grading remains pending, so no complete free-text endorsement result is claimed.

## Dataset and analysis

Default dataset: 12 P1 items × 36 conditions = 432 trials, plus 10 P2 items × two truth states × nine conditions = 180; total 612. Development: 9 P1 items × 36 = 324 and 8 P2 items × 18 = 144; total 468. The other 144 trials are reserved. Repeated seeds stay within item clusters, never inflate the number of independent items. Reserved families are diagnostic reservations; engineers have seen their generator. They are not a genuinely untouched confirmatory corpus.

The code rejects any confirmatory/held-out run and any family spanning splits. Future confirmatory execution needs a frozen approved protocol and new untouched families. Current analyses give paired item-cluster exploratory intervals and all-scheduled missing-outcome bounds. They do not implement confirmatory Holm-adjusted tests or equivalence tests; those remain blocked until thresholds and sampling are registered. Missing outcomes remain visible. No analysis filters correctness to checkers.

## Live budget guard — not activated

`live_config.example.json` intentionally cannot run. Before a live pilot, supply an authorized provider/model, verified rates, input-token billing upper bound, completion limit, total dollar cap, and one absolute shared ledger path. Set `allow_live` only when those choices are authorized. Configure API credentials locally using the named environment variable.

```sh
python3 harness_v2.py run --dataset dataset_v2.json --output real/model_dev --live-config approved_config.json
```

The SQLite ledger reserves a conservative call cost before network transmission, atomically across workers. It records actual returned usage and settles cost at the configured rates. Unknown usage/timeouts retain the reservation and block further calls. Budget exhaustion halts the whole run: it does not skip a condition and continue. Unexecuted scheduled trials remain reported, and no confirmatory inference should be made from that incomplete batch.

Use the SAME ledger path across restarts/workers; cap and rate card cannot silently change. The current ledger supports one provider/model rate card. Multiple models require an audited shared multi-rate-card extension or explicitly separate budget allocations whose sum respects the authorized total; the harness never creates fresh ledgers automatically. Pricing must cover all billable token categories, including reasoning; unsupported flat fees or invalid bounds invalidate cost protection. An actual charge exceeding its reservation is recorded and blocks further use. This is local admission control, not a provider-account billing limit.

No automatic network retries occur. Provider transport is tested with mocked responses only. A live provider smoke test is still required. The first-answer cache is persisted with each completed or budget-halted run; there is no automatic interrupted-run resume or retry mechanism that silently changes assignments.
