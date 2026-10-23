# Attempt B: single-thread native starts, frozen repair policy

All twelve single-thread native starts verified. Across 36 paired repair runs,
SOL-aware repair wins 26, ties 9 and loses 1 on SOL. Summed differences are
SOL -636 and SOC -349, with two paired SOC regressions and no makespan regression.
The separate audit checked all 72 final repair routes and 1,178 accepted
intermediates, plus all native routes and the exact reused query cohort. These
are fixed-pop, author-assisted within-map results, with the limitations below.

| Map family, 12 pairs each | SOL wins / ties / losses | Sum SOL delta | Sum SOC delta |
| --- | ---: | ---: | ---: |
| Maze | 11 / 1 / 0 | -281 | -178 |
| Room | 12 / 0 / 0 | -343 | -163 |
| Random | 3 / 8 / 1 | -12 | -8 |

Negative deltas favor SOL-aware repair. The two tradeoffs are retained:
`maze-32-32-4-fresh1-n128`, trial 1, SOL -4 / SOC +7; and
`random-32-32-20-fresh0-n64`, trial 0, SOL +1 / SOC +1. Both have unchanged
makespan. Every policy's final route still satisfies its original-start macro
Pareto gate; these differences compare the two policies. Three repeated trials
per query are not three independent maps, and their summed gains are not gains
to unique accepted archive entries. No result was used to retune or select a
different policy.

| Method, 36 runs each | Search pops | Core seconds | Inclusive engine seconds | Worker process user CPU seconds |
| --- | ---: | ---: | ---: | ---: |
| Current arrival repair | 3,134,232 | 26.7473 | 28.2693 | 120.4319 |
| SOL-aware repair | 2,702,879 | 33.4525 | 35.0831 | 149.4329 |

Preprocessing totals are 1.5220 / 1.6305 seconds, respectively. The challenger
used fewer pops but more observed engine/core time and worker process CPU. Its
643 accepted intermediates versus 535 for arrival also require more route
verification work. Fixed pops are not matched CPU; no speed claim is made.
All 72 scheduled workers completed, with no failed, skipped or unattempted B
jobs. Their total parent-observed phase wall time is 276.5333 seconds. Native
calls used 148.5544 seconds wall and 144.1053 child user CPU seconds; maximum
recorded child RSS was 212,128 KiB. Full per-run and parent resource records are
retained rather than treating these shared-machine observations as performance
proof.

This separately declared attempt repeats the same twelve query geometries and
repair seeds as `research/fresh-sol-ee542d9b` (attempt A). All twelve default
native calls there aborted with signal 6 before writing routes under the 1 GiB
address-space cap, so A produced zero repair-policy comparisons. That complete
failed attempt and its source/input/output identities remain preserved.

Before running any attempt-B native or repair result, this protocol changes one
native execution flag: `--no-multi-thread`. It keeps the exact compiled LaCAM3
binary, source pin, native seed 0, 12-second internal deadline, 1 GiB cap, fixed
query cohort and frozen repair policy/budgets/seeds. The exact internal cause of
the default aborts is not established. This is a declared infrastructure change
after startup failures, not repair-policy tuning. The inputs are already exposed
by A, and the policy predates their first generation. There is no unseen-corpus
or independent-human evaluation claim.

The generator recreates A's exact map/start/goal arrays and byte-identical scenario
contents under a new package path. Instance metadata hashes differ because they
name that path. The separate auditor checks every geometry and scenario against
A's retained cohort as well as independently recomputing the seed-derived draws.
No query is replaced or filtered by outcomes. All native failures, repair failures
and cap-related unattempted jobs remain explicit; only successful complete pairs
enter the policy comparison.

Sources/helpers are retained as a separate immutable attempt rather than changing
A's protocol or outputs. The copied SOL policy remains byte-identical to PR #8's
frozen source, SHA-256
`bf2a499402cc52ce482e09ef814d32bc6c99a5c0db1f42f00322a73599b4a780`.
All six producer-preflight findings and their resolved regression controls are
documented in A's `REVIEW.md`. Native source/build/environment/failure evidence is
in A's `build-records/`; no new compilation is performed for B. B's final review
and result record will identify every additional finding and correction.

The fixed comparison is unchanged random4 versus explicit lexicographic
`(SOL, final arrival)` prioritized repair, with 100,000 pops, 96 attempts and
10,000 pops per agent. Macro Pareto gates, legal goal departures and the model
stay the same. Worker/cutoff containment, exact string seeds and separated
preprocessing/engine/core/full timings follow the contracts described in A.
The worker wall timer begins inside the worker after imports/argument parsing
and ends before final record writing. Worker CPU/RSS are process snapshots.
Parent journal wall/child CPU includes startup, imports, record writing and
capture overhead. Fixed pops are not matched CPU, and no speed claim or global MAPF optimality is
implied. Rejected/partial proposal geometry that the optimizer never returns is
not separately available.

The first complete B audit failed on a schema comparison: the unchanged checker
returns diagnostics as well as SOL/SOC/makespan, while native records contain
only the three objectives. `audit-failure-v1.json` and its committed checker
source retain that failed attempt. Comparing the three declared objectives
corrected the auditor without changing any route or optimizer output.
`verification-v2.json` passed the full scope in 194.4142 seconds. The checker
supports relocation; subsequent hardening rejects hiding a completed verified run as a
failure. Each audit version is retained with its actual source hash. This is
separate author-run checking, not optimizer replay or independent human review.

From repository root, with the project dependencies and retained Git history:

```sh
python -m pytest -q tests research/fresh-sol-single-ee542d9b/test_controls.py research/fresh-sol-single-ee542d9b/test_audit.py
python tools/check.py --quick
python research/fresh-sol-single-ee542d9b/audit.py --out verification-replay.json
```

Use an unused direct package filename for audit output. A new full optimizer
replication belongs in a separate fresh package/checkout with newly recorded
cutoffs, actual native binary hash/toolchain and committed sources; keep A and B
and their original records. Then run that copy's `inputs.py`, commit all inputs,
`run_native.py --all`, and `run_repair.py --all`. A new folder alone does not renew
an expired deadline. Keep the declared predecessor cohort binding available.

Credit the project authors, unchanged standalone checker/model/repair code,
established prioritized MAPF/LNS/A*, Kei Okumura's LaCAM3 and argparse authors,
and the Moving AI benchmark creators. Existing third-party notices apply.
Continues the predecessor headroom handoff and PRs #5–#8 from the same posting
account. Codex-authored and author-commissioned reviews/audits do not establish
independent human scientific acceptance. Accepted records, frontier and frozen
project witnesses remain untouched; acceptance and merges stay with the maintainer.
