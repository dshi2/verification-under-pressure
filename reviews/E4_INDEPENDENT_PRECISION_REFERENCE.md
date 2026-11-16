# P1 E4 independent bounded reference — audit only

**Audit base:** P1 PR #1 head `433fe86b54d3056d935b92cfb49af057eb92eab3`, 16 November 2026.

**Status:** adversarial offline statistical comparator. It is NOT P1's final estimation method, precision simulation, sample-size recommendation, protocol approval, or an empirical finding. No external model calls. Do not merge this reference into the builder's estimator automatically.

## Reproduce

From the P1 repository root:

```sh
python3 -m unittest discover -s reviews -p 'test_e4_bound_reference.py' -v
```

Only Python standard library is used. The ten tests exercise (i) an exact E4=1 synthetic interaction, (ii) perfect accuracy with still-positive uncertainty, (iii) sign-aware bounds on arbitrary missing responses, (iv) brute-force recovery of extrema among completions, (v) repetitions nested within items, (vi) absent E4 cells and bad data, (vii) the independent-item warning, (viii) the very loose required N and (ix) confidence-level monotonicity.

## Which design cells and what is independent?

The full P1 design has 2 snapshot × 2 assigned assertion correctness × 3 pressure × 3 evidence-route = **36 scheduled conditions per item × model × repeat**. E4 specifically uses **16**: snapshot {current, stale} × assertion {right, wrong} × pressure {neutral, insistence} × evidence route {optional, supplied}. The unused arms still matter to the full experimental protocol and other contrasts; this reference is *not* a design-matrix validator.

E4 is the equal-snapshot-weight contrast

`D(u) = [acc(insist,supplied,u) - acc(neutral,supplied,u)] - [acc(insist,optional,u) - acc(neutral,optional,u)]`

and `E4 = D(right) - D(wrong)`.

There is exactly one item-level contrast `Z_i` per item, with `Z_i in [-4,4]`; repeating the same item does not create new independent units. An incomplete but scheduled trial must be represented with `final_correct=None`. Entirely absent scheduled E4 cells are rejected rather than treated as zero.

For arbitrary not-scored outcomes, each item's lower/upper E4 is computed using sign-aware completions: **missing=0 on positive weights and missing=1 on negative weights** for the lower endpoint, reversed for the upper. This yields a sample identification interval, not a confidence interval.

For n independently sampled items and a two-sided alpha, Hoeffding gives the **extremely conservative** radius

`sqrt(32 * log(2/alpha) / n)`

to add outside the sample identification interval (clamped to [-4,4]). Even if all observed answers are perfect and the point E4 is exactly zero, this radius is positive. At alpha=.05 and half-width=.075, the sufficient n from this worst-case inequality is **20,986 independent items**; with alpha=.0125 it is **28,873 independent items**. These figures are not sample-size recommendations and should NOT be used to decide P1's feasibility. They demonstrate that a worst-case, distribution-free guarantee leaves enormous unused information relative to a variance-aware paired estimator.

**Critical limitation:** independent *item* draws are an explicit assumption of this reference. When independently authored cases share a family-level random effect or identical template, the effective information is lower; the code is NOT family-cluster valid. Nor does it model model-level heterogeneity, first-answer CC/CW/WC/WW strata, shared first-turn failures, near-ceiling parametric behavior, Holm joint coverage or missingness mechanisms.

## Builder comparison required

Do not use this reference to decide P1's required N. Instead, run the builder's planned **family-aware simulation** with at least:
1. realistic item-level pairing and shared turn-1 prefix within each snapshot/model/repeat;
2. joint first-answer correctness patterns CC, CW, WC, WW, not only marginal accuracy;
3. multiple authorially independent families and model families (report each model separately);
4. near-zero lookup and near-perfect final accuracy, plus missing/invalid outcomes;
5. known null E4 and known nonzero E4, with effects near and beyond ±SESOI;
6. E1–E4 family-level multiplicity and 95% interval coverage at boundary cases;
7. the stipulated 7.5-percentage-point E4 half-width reached with the prespecified probability (≥80%).

Then evaluate a valid paired/clustered candidate interval against the conservative bound on identical independent-item scenarios. Its shorter intervals can be justified by statistical structure and coverage simulation, not assumed to be wrong because they are shorter. A result that fails at the boundary or has unacceptable undercoverage is not an approved estimator.

**The important interpretation:** exact unit definitions, full trial accounting, verified interval coverage and scientific SESOI matter more than the raw count of model calls. A precise null is informative; an underpowered non-significant result is not.

No merging or paid/model runs authorized by this audit.
