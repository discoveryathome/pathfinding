# Explicit SOL-aware prioritized repair

The frozen SOL-aware policy improves 17 of 51 paired evaluation runs and ties
the other 34 on SOL. Summed evaluation differences are SOL -172 and SOC -97,
with no paired SOC or makespan regression. This is exposed-corpus evidence under
a fixed search-pop allowance, not an unseen-transfer or speed result.

## Question and method

The current `random4` repair minimizes each replanned agent's final arrival time.
SOL charges every transition except a hold at the agent's own goal, so arrival
and SOL can prefer different routes. `sol_repair.py` replaces only the low-level
objective with lexicographic `(SOL, final arrival)`. It retains four-agent random
neighborhoods, sequential reservations, legal goal departures, the current
makespan horizon, and the original Pareto acceptance gate. The method is ordinary
prioritized MAPF repair with A*, not a new search algorithm. See [PROOF.md](PROOF.md)
for the bounded-search guarantee and [LITERATURE.md](LITERATURE.md) for primary
sources and the six-cell SOL 6 versus 5 counterexample.

The donation seed is `ee542d9b4c91949140f009a90142f5ba`; it is a randomness seed,
not a Git revision. Canonical base is
`37823dca1bea271510e3ed62205620466ec6f0f9`. `protocol.json` binds all 20 instances,
starts, 60 exact 128-bit seeds, resource caps, selection rule and stopping rule.
Nineteen starts come from the current canonical Pareto archive. The original
maze deliberately inherits PR #5's already known proposed SOL 7802 / SOC 8223 /
makespan 125 witness, retained byte-for-byte in `inputs/maze-start.json`; resetting
it to accepted SOL 7815 would count known progress again. This inheritance does
not change the project's accepted archive.

## Frozen development and evaluation

Protocol commit `8d0f774` precedes method freeze `5c54e6e`. The three predeclared
development cases are `empty-32-32-s2-n256`, `random-32-32-20-s2-n192` and
`room-32-32-4-s2-n160`, each with three seeds and two paired methods. The automated
gate requires lower total SOL, no higher total SOC and no makespan regression.
A single per-agent-arrival-deadline pivot was allowed only after a specified
majority of completed rejected proposals lowered SOL while worsening SOC.

The primary policy passed. Selection and all 18 development runs were committed
at `b99c1ec` before launching the 102 evaluation runs on the other 17 published
cases. The pivot did not run. Sources remained byte-identical across phases.
All source identities, commands, failures, resource use and worker outcomes are
retained in `a1-*.json`, the two JSONL journals and `runs/`.
After the study, the runner's replay journal was corrected to retain the exact
executed command when copied to another package. The original experiment runner
remains recoverable at `5c54e6e` and matches the run manifests; no experiment was
rerun or its outputs rewritten for that bookkeeping correction.

| Declared panel | Paired runs | SOL wins / ties / losses | Sum SOL delta | Sum SOC delta | SOC / makespan regressions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development | 9 | 3 / 6 / 0 | -50 | -8 | 0 / 0 |
| Evaluation | 51 | 17 / 34 / 0 | -172 | -97 | 0 / 0 |

Negative deltas favor SOL-aware repair. These sums include three runs per case;
they are not summed improvements to unique archive entries. All cases were
published calibration material. New repair seeds do not create new maps or
independent human evaluation.

`summary.json` separately indexes the best `(SOL, SOC, makespan, method, trial)`
witness among each case's six declared runs. This after-search selection improves
12 unique starts by 210 total SOL units and 114 SOC units. It includes both
methods and is not the selected policy's success rate. The original maze's
proposed witness reaches SOL 7794 / SOC 8215 / makespan 125. Every indexed route
was checked, but these proposals await maintainer review and acceptance.

## Resources and limitations

Each run allowed at most 100,000 popped nodes, 96 neighborhood attempts and
10,000 pops per replanned agent, with a 600-second external timeout and 1 GiB
address-space cap. The declared maximum including the conditional pivot was
138 runs; 120 ran. Their combined search used 8,105,535 pops. Full worker journals
include startup, validation and orchestration wall time; they are not solver-only
timings.

| Method, 60 runs each | Search pops | Inclusive engine wall seconds | Worker user CPU seconds | Worker system CPU seconds |
| --- | ---: | ---: | ---: | ---: |
| Current arrival repair | 4,539,643 | 90.8520 | 173.0800 | 2.6313 |
| SOL-aware repair | 3,565,892 | 98.5922 | 195.7496 | 2.3294 |

The historical raw field `core_elapsed_seconds` and summary field `core_seconds`
include preprocessing because both engines start their elapsed timer before BFS.
Those original records remain unchanged. `clarify_timing.py` derives
`timing-clarification.json` from all 120 retained records: after subtracting
preprocessing, actual core totals are 82.3147 seconds for arrival and 90.1157
seconds for SOL. The table above reports the original inclusive engine totals.

The challenger used fewer pops but more observed engine/core wall and CPU time. Fixed pops
are not equal CPU. Workers ran sequentially on a shared machine; no A/A or
matched-time controls were run, so no speed claim is made. The frozen experiment
used Python 3.13.5; upstream native solvers and Python 3.12 were not exercised.
This method returns only the first bounded prioritized candidate for a chosen
agent order and is not complete or optimal for joint MAPF. A capped failure is
not evidence of infeasibility.

## Verification and reproduction

`verify_study.py` imports the unchanged standalone route checker, not either
optimizer. It checks source/input and artifact hashes, exact case/trial/method
coverage, complete journals, initial and final metrics, every accepted
intermediate route, Pareto gates, resource counts, development selection and the
paired common random neighborhood prefixes. `verification.json` records all
120 final routes and 313 accepted intermediate routes checked in 178.0431
seconds. This original audit and the intermediate V2 audit are preserved. The
final tightened verifier checked the same scope in 181.6307 seconds, retained
as `verification-v3.json`. Optimizer traces are losslessly compressed; candidate certificates are
plain JSON. Separate checking is still author-assisted evidence.

From repository root, with the documented project dependencies installed:

```sh
python -m pytest -q tests research/sol-repair-ee542d9b/test_*.py
python tools/check.py --quick
python research/sol-repair-ee542d9b/verify_study.py --attempt a1 --out verification-replay.json
python research/sol-repair-ee542d9b/summarize.py --attempt a1 --out summary-replay.json
```

The two output names must be unused filenames directly inside this package;
absolute paths and overwriting retained outputs are deliberately rejected.
Source provenance checking requires the recorded Git commit objects and their
files. Fetch the contribution branch's retained history if needed; a source
archive or shallow checkout without those objects cannot establish that check
and is rejected explicitly, even when current file hashes match.

For a new full optimizer replay after the recorded 2026-10-23 12:05 UTC research
cutoff, make a separate checkout and a fresh research package as required by
DISTRIBUTION.md. Copy the method/runner, protocol and inputs while retaining this
original package and its evidence. Record new absolute research/end cutoffs in
the copied protocol, update any package-relative input references, and commit
that new source identity before running. Use an unused attempt identifier with
`run_study.py --attempt replay --stage development`, then `--stage evaluation`
only if development selects a policy. A new identifier alone does not renew the
original deadline. The worker requires committed, clean method/input sources.
A detached checkout of `5c54e6e` preserves the original development source state;
`b99c1ec` preserves the selection before evaluation. A later replay is a separately
identified attempt, not an overwrite of these records. Timing, timestamps, peak
RSS and worker code-commit metadata may differ.

Tests cover the exact 70-walk counterexample, 150 deterministic tiny reservation
draws against a time-layer DP oracle, goal departures/holds, deadlines, caps,
macro guards, development eligibility, copied-package journal paths and checker
tamper controls. All 33 relevant tests pass; `checks-v3.json` records final checks,
while `checks.json` retains the earlier 31-test state. The full
120-run optimizer panel has not been replayed a second time. Rejected proposals'
metrics and failure statuses are retained, but their full rejected or partial
route geometry was not stored or separately checked. No unseen corpus,
statistical population claim, native-solver comparison or independent human
scientific signoff is provided.

## Credit and provenance

This continues @thakrarsagar's
[open headroom handoff](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19132179)
and PRs [#5](https://github.com/discoveryathome/pathfinding/pull/5),
[#6](https://github.com/discoveryathome/pathfinding/pull/6) and
[#7](https://github.com/discoveryathome/pathfinding/pull/7). The posting account is
the same as that predecessor; this is continued work, not independent replication.
Credit the project authors and unchanged model, repair and route checker, known
prioritized MAPF/LNS and A* methods, LaCAM3 for inherited plans and the Moving AI
benchmark creators for inputs. Existing third-party notices remain applicable.

Codex agents authored the method, experiment, separate audit and literature note.
Author-assisted Standards and Spec review outcomes are retained in `REVIEW.md`.
They are distinct from independent human scientific review, which remains
pending. No frozen witness, accepted-result record or project frontier is edited.
