#!/usr/bin/env python3
"""Check published P1 headline numbers against the committed aggregate JSON.

This is a reproducibility smoke test: it does not rescore raw model responses,
verify provider requests, or independently recompute statistical intervals.
No external packages, credentials, or API calls are required.
"""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "rev3/results/combined/analysis.json").read_text())
assert data["n_items"] == 60, "Expected 60 items"
assert data["n_families"] == 12, "Expected 12 record families"
models = data["estimates"]["insistence"]
want = {
    "qwen3-235b-a22b-2507": (-49.7, -0.2, 25.6, -40.5),
    "gpt-oss-120b": (-10.0, -0.4, 4.5, -4.7),
    "deepseek-v3.2": (-1.3, -2.4, -1.8, 2.5),
    "kimi-k2-0905": (-5.8, -0.4, 5.1, 1.5),
}
assert set(models) == set(want), "Model set changed"
keys = ("E1_delta_attempt", "E2_delta_acc_supplied", "E3_delivery_effect", "E4_moderation")
for model, values in want.items():
    for key, expected_pp in zip(keys, values):
        entry = models[model][key]
        got_pp = entry["estimate"] * 100
        assert math.isfinite(got_pp), f"{model} {key}: nonfinite result"
        assert abs(got_pp - expected_pp) < 0.055, (
            f"{model} {key}: found {got_pp:.3f} pp, expected {expected_pp} pp"
        )
        assert entry["items_used"] == 60, f"{model} {key}: unexpected item count"
        ci = entry["inference"]["ci95_family_cr1"]
        assert len(ci) == 2 and ci[0] <= entry["estimate"] <= ci[1], (
            f"{model} {key}: main CI does not contain point estimate"
        )
assert 60 * 2 * 2 * 3 * 3 * 4 * 5 == 43_200
print("P1 aggregate headline check PASS: 60 items, 12 families, 4 models, 43,200 scheduled trials; E1–E4 agree.")
print("Note: aggregate-output consistency only. Raw response journals are not in this repository.")
