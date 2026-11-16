# Handoff to Codex: reconcile the harness with PROTOCOLS_v1.md (revision 2)

Attach this file together with PROTOCOLS_v1.md. The protocol is the authority. Where the harness differs from it, change the harness, or list the difference with a reason for keeping it.

## Deliverable
A difference table (provision | harness status | fixed / kept + reason), plus a test for each item below. "Reconciled" without the table does not count.

## Known differences (the harness was built from revision 1)
- Track 2 has 96 mock trials = 8 conditions × 12 items. Revision 2 has 9 conditions (A0 added), and baseline A has changed.
- The novelty wording in the preregistration draft says "compare voluntary retrieval with automatic delivery". Christian & Mazor 2026 already did that. Use: **pressure × (choosing to check vs. evidence supplied) × user right/wrong, with objective evidence.**

## Checklist (each item needs a test or a written check)
### P2
1. A states the practice fact in exactly the same words as B ("The facility provides X m² per animal"), with no verification statement.
2. D1 and D2 contain that same fact, unverified.
3. A0 (outcome claim only) exists and is labeled exploratory.
4. C′ has the same scope content as C, in structured fields.
5. A test diffs A, B and D1 and fails on any difference outside the verification block and length filler.
6. The issuer and auditor identity are identical across B, C, C′, D1, D2 and E.
7. Welfare cases include both improved and non-improved outcomes (E must be able to support *or* contradict the outcome claim).
8. Primary estimands: attribution B−A, B−D1, C−B; correct endorsement in E. Secondary: C′−C.
### P1
9. The tool description and system prompt are byte-identical across arms, with no "use tools when unsure" wording.
10. The supplied arm's injected tool call + result has exactly the format the optional arm returns.
11. No analysis conditions on who checked (intention-to-treat only).
12. Pilot gate on the floor check: report the neutral-arm check rate; if it is below ~10%, revise the task, never one arm's prompt.
13. Secondary outcome: pressure × user-correctness on adopting the evidence in the supplied arm.
14. Wrong-id lookups are logged as "checked" but not "relevant".
### Both
15. The grader never sees the condition label or the verification-block wording.
16. The held-out split is enforced in code (development families cannot reach confirmatory runs).
17. Repeated seeds are within-item repeats; uncertainty is computed by item (random intercept or cluster bootstrap).
18. Mock or simulated outputs go to a separate, labeled directory and can never be loaded by the analysis of real runs.
19. **A hard spending cap blocks live runs:** estimate cost before each call and refuse if over budget; record actual usage after each call; persist the running total across restarts and parallel workers; halt (don't skip trials) when the budget is exhausted.

## Disk
Free space on this machine is very low (under 100 MB at last check). Keep logs compact, and don't install packages or write large caches without checking first.
