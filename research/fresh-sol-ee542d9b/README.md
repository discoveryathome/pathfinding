# Frozen SOL repair on fresh within-map queries

This package evaluates the SOL-aware policy already selected in
[PR #8](https://github.com/discoveryathome/pathfinding/pull/8) on twelve newly
generated queries on three published maps. The comparison is against unchanged
`repair_round2.run(random4)` from the same pinned LaCAM3 starting plan, with three
paired seeds and the same search-pop allowance. No policy tuning or
fresh-output-driven pivot is permitted. Results and final checks are recorded
below before submission.

## Fixed scope and exposure

Canonical base is `37823dca1bea271510e3ed62205620466ec6f0f9`, donation seed
`ee542d9b4c91949140f009a90142f5ba`, drawn track `headroom`, priority revision 3.
The fixed scope is maze, room and random 32x32 maps, 64 and 128 agents each,
two generated queries per map/count. For each case, Python's seeded sampler
draws unique starts and independent unique goals from the sorted largest free
component; tied components choose the smallest first vertex. Start-equals-goal
is allowed. `protocol.json` contains every exact draw and repair seed as text.
No query is replaced or filtered based on solver outcomes.

The policy snapshot is byte-identical to the method frozen before the preceding
study's development/evaluation, SHA-256
`bf2a499402cc52ce482e09ef814d32bc6c99a5c0db1f42f00322a73599b4a780`.
It lexicographically minimizes low-level `(SOL, final arrival)` under fixed
reservations, permits goal departures, and retains the original macro Pareto
gate. See PR #8's proof and primary-source literature note for its bounded
subproblem guarantee and limits. This is established prioritized MAPF/A* repair,
not a new globally optimal MAPF solver.

The queries are generated after policy freeze, using an author-chosen fixed
generator on already exposed maps. This is fresh within-map variation, not new
maps, unseen-corpus transfer, independent human evaluation or a population
estimate. All generated queries become public exposed inputs. The three seeds
per query are repeated trials, not independent map samples. A failure of the
native start generator is retained without replacement; repair is skipped only
when no verified start is available.

## Sources, starts and resources

Each start uses pinned
[LaCAM3 source](https://github.com/Kei18/lacam3/tree/1c3ecf8ade40298f16047544634e9c0c1cf3b93c),
argparse `69dabd88a8e6680b1a1a18397eb3e165e4019ce6`, defaults, seed 0 and a
12-second internal deadline. Its
[edge objective](https://github.com/Kei18/lacam3/blob/1c3ecf8ade40298f16047544634e9c0c1cf3b93c/lacam3/src/planner.cpp#L275)
charges every transition except a hold at the agent's own goal, matching SOL.
The native output's SOL, SOC and makespan must agree with the unchanged
standalone checker. The native is a starting-plan provider; this experiment does
not compare global solver performance or claim a state-of-the-art baseline.

The source was fetched shallow with its exact submodule. Helper screening found
no issues, and the build configuration/source was inspected before execution.
Only the native `main` target was built, with GCC 14.2.0, CMake 3.31.6, empty
build type, `-UNDEBUG`, upstream `-O3` and two build jobs. Assertions are enabled.
Compilation took 39.3666 seconds, 64.2031 child user CPU seconds and 297,568 KiB
maximum child RSS under a 180-second stop. The first wrapper failed before
compilation because `/usr/bin/time` was absent. Both attempts' logs, actual flags,
resource output and wrapper source are retained in `build-records/`. Generated
compiler flags are stored as JSON strings with their byte hashes to preserve
original trailing whitespace without changing the recorded text. Binaries and
vendor code are not committed; existing third-party notices remain applicable.

Each repair run allows 100,000 pops, 96 attempts and 10,000 pops per agent,
with a 600-second external timeout and 1 GiB address-space cap. Native calls
have 45-second external timeouts inside 60-second worker limits and the same
address-space cap. Each phase is bounded by the recorded global cutoff and
resource limits; the package stops new work above 500 MiB. The pinned native is
one process with threads and joins its worker's process group so an outer timeout
also stops it. Workers run sequentially on a shared machine.

Fixed pops are not matched CPU. Per-run records separate preprocessing,
inclusive engine elapsed, core elapsed after subtracting preprocessing, complete
worker wall/CPU and memory. Parent journals include process startup/child costs.
`max_child_rss_kib_on_linux_so_far` is a cumulative maximum across children seen
by that process, not a sum or an isolated per-run RSS measure. No A/A timing or
matched-time controls were run, so no speed claim is made.

## Evidence and checking

`inputs.json` binds the exact generated instances/scenarios and the committed
producer source. `native.json`, `repair.json` and their JSONL journals preserve
all scheduled attempts, native failures, repair failures and cap-related
unattempted jobs. Failed repair workers do not discard the remaining schedule.
Each request is stored before search; a returned full trace and candidate are
stored before validation, and checker rejection retains a failure record.
An optimizer exception before it returns cannot supply a full internal trace;
its request, parent exception/output and any produced artifacts remain retained.

`audit.py` imports only the unchanged standalone checker. It separately
reconstructs all query draws and scenario distances, checks exact case/trial/
method coverage, complete source and input manifests against actual Git commit
objects, journal/command bindings, all successful native/final/accepted
intermediate routes, Pareto gates, resource counts and common random group
prefixes. It keeps failed/unattempted jobs and incomplete pairs distinct from
the policy comparison. It does not rerun optimization or establish independent
human scientific acceptance. Rejected proposals' metrics/statuses are retained;
their unreturned full geometry is not available for separate checking.

From repository root with the project environment installed:

```sh
python -m pytest -q tests research/fresh-sol-ee542d9b/test_controls.py research/fresh-sol-ee542d9b/test_audit.py
python tools/check.py --quick
python research/fresh-sol-ee542d9b/audit.py --out verification-replay.json
```

The audit output must be an unused filename directly inside this package. Source
checking needs the retained Git commit objects; fetch the contribution branch's
history if a shallow checkout lacks them. An archive alone cannot establish that
provenance check. The auditor never overwrites prior evidence.

For a new optimizer replication, retain this package and make a separate fresh
package/checkout as required by DISTRIBUTION.md. Copy sources and protocol, update
the copied absolute cutoffs and package-relative references, build the same
pinned native source with recorded flags, record the resulting binary hash and
environment in the new protocol, then commit the new source identity. Binary
bytes may vary with toolchain/environment; never silently replace the original
hash. In that copy run `inputs.py`, commit the complete new input cohort, then
`run_native.py --all` and `run_repair.py --all`. Native time-bounded output can
vary; this is a separately identified attempt. None of these commands may
overwrite the original records or renew an expired cutoff implicitly.

## Provenance and credit

This continues the
[predecessor headroom handoff](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19132179)
and this session's PRs #5–#8. The posting account is the same as the predecessor;
this is continued author-assisted work. Credit the project authors and unchanged
checker/model/repair code, known prioritized MAPF/LNS/A* methods, Kei Okumura's
LaCAM3 and argparse authors, and the Moving AI benchmark creators. The project
map sources and existing THIRD-PARTY notices are preserved.

Codex agents authored the adapters, audit and report. Separate Standards and Spec
agent reviews and all findings/resolutions are retained in `REVIEW.md`; they are
author-commissioned and not independent human signoff. Merges, accepted results
and scientific acceptance remain with the maintainer. This package changes none
of the project's accepted archive, frozen witnesses or frontier records.
