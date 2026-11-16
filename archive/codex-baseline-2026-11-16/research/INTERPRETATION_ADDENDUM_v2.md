# Revision 2: interpretation and change control

Recorded 2026-11-16. This addendum clarifies interpretation and prospective workflow. It does not change the locked diagnostic-pilot baseline, experimental arms, estimands, or code, and is not a confirmatory preregistration.

## What B versus D1 can establish

For unsupported attribution of outcome verification, the intended interpretation of a reliably positive B−D1 contrast is:

> B > D1 shows the effect depends on what was verified, not just that something was. It doesn't tell us whether authority, inference or something else carries it.

This interpretation requires the matched controls to hold: the same issuer and auditor, target practice fact, surrounding facts, and matched presentation length, with the planned difference in verification content. A positive sample estimate alone is insufficient; report its uncertainty and the manipulation checks.

A credible difference is inconsistent with a purely content-independent authority or reassurance effect as the complete explanation. Such an effect may still contribute to both conditions. Topic-sensitive authority remains a possible mechanism: an on-topic verification may carry more authority for welfare outcomes than an unrelated verification. The experiment does not identify authority, inference, or another psychological mechanism separately.

Keep unsupported attribution distinct from belief. Verifying a relevant practice may legitimately change belief about outcomes without establishing that the outcomes were verified. The main claim concerns the latter attribution error.

## Freeze chronology and future changes

The current condition renderers were built and tested offline before the formal diagnostic-pilot baseline lock. The hash manifest explicitly records that chronology. It must not be described as a pre-implementation freeze. No live model experiment preceded that lock; the confirmatory design remains unfrozen.

For future unfrozen design revisions, development may proceed only on condition-independent infrastructure: model adapters, spending cap, response cache, JSONL logging, and mock-model tests. Changes to P1 or P2 condition renderers must wait until the corresponding design revision is frozen. Then record the protocol difference, update implementation and tests, and issue a new baseline manifest rather than silently changing the existing one.

The existing frozen diagnostic-pilot renderers are retained without changes. This addendum does not authorize paid calls or confirmatory runs.

## Storage check

The filesystem reported 2.9 GiB available when checked on 2026-11-16. This supersedes the earlier approximately 570 MB estimate, but is a point-in-time observation. Keep logs compact, check space before larger writes, and avoid package installations or large caches without a fresh check. No files were deleted for this update.
