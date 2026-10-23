# Attempt B: single-thread native starts, frozen repair policy

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
Fixed pops are not matched CPU, and no speed claim or global MAPF optimality is
implied. Rejected/partial proposal geometry that the optimizer never returns is
not separately available.

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
