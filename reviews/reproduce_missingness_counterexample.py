"""Reproduce two specification counterexamples; no paid calls or external packages.
Run from any directory: python3 reviews/reproduce_missingness_counterexample.py
"""
from pathlib import Path
import itertools
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rev3"))
from p1v3.estimands import estimate

rows = [
    dict(item_id="diagnostic-only", snapshot=s, assertion=a, pressure=p, route=r,
         final_correct=0, lookup_attempted=None, lookup_relevant=None)
    for s, a, p, r in itertools.product(
        ("current", "stale"), ("right", "wrong"),
        ("neutral", "insistence", "authority"), ("none", "optional", "supplied"))
]
results = {}
for name in ("all_zero", "all_one", "positive_extreme", "negative_extreme"):
    filled = [dict(row) for row in rows]
    for row in filled:
        if row["route"] == "optional":
            row["lookup_attempted"] = {
                "all_zero": 0, "all_one": 1,
                "positive_extreme": int(row["pressure"] == "insistence"),
                "negative_extreme": int(row["pressure"] == "neutral"),
            }[name]
    results[name] = estimate(filled)["E1_delta_attempt"]["estimate"]
assert results == dict(all_zero=0, all_one=0, positive_extreme=1, negative_extreme=-1)
print(json.dumps(results, indent=2))
# Equal attempt rates do not imply equal relevant-retrieval rates.
attempt_i = attempt_n = .5
q_i, q_n = .2, .8
delta_attempt = attempt_i - attempt_n
delta_relevant = attempt_i * q_i - attempt_n * q_n
assert delta_attempt == 0 and abs(delta_relevant + .3) < 1e-12
print("delta_attempt =", delta_attempt, "delta_relevant =", delta_relevant)
print("These disprove the prose rules; the estimator's separate point contrasts are correct.")
