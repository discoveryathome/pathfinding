# SOL-aware pair headroom bounds

This package strengthens the existing lower bound on **all 20 exposed archive
cases**, by **491 summed units**, using the same 521 disjoint conflict pairs.
It computes 519 exact two-agent SOL optima and two capped-search lower bounds.
All 521 pair bounds also pass a separate cost-threshold checker with no optimizer
imports. This is author-checked evidence for a known pairwise relaxation adapted
to the project's SOL semantics, not a new MAPF algorithm or an accepted frontier
update. Remaining gaps are not promises of achievable route improvements.

The original maze bound rises **5969 → 6041**. Against the canonical archive route
SOL 7815, its gap falls **1846 → 1774**. The separate proposed route in PR #5 has
SOL 7802; combining those proposals would leave gap 1761, but neither proposal is
silently incorporated into the accepted archive here.

## Question, sources and protocol

The supplied seed `ee542d9b4c91949140f009a90142f5ba` draws the `headroom` track
(full integer `316793340945421113888006999147102270906`). This follows the
predecessor's [20-case ranking and open handoff](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19132179),
and the [distinct pair-bound claim](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19139839).
The object and method differ from PR #5's bounded random repair.

Base: `37823dca1bea271510e3ed62205620466ec6f0f9`.
Predeclared protocol commit: `9f29e7f0ca81c02d48ba0633060d5a5af865f70b`.
Frozen panel implementation: `92c1d8c74c94f0dc65e6a3a04b63b89253a731af`.
[protocol.json](protocol.json) was committed before the pilot. It fixes the pair
set, caps, exposed development case, stopping rule and falsification obligations.

The method is established pair-dependency lower-bound reasoning. [PROOF.md](PROOF.md)
gives the project-specific SOL relaxation, capped-frontier argument and disjoint
aggregation proof. [LITERATURE.md](LITERATURE.md) cites primary sources: Felner et
al. (ICAPS 2018), Li et al. (IJCAI 2019), Okumura (IJCAI 2023), Stern et al. (SoCS
2019), and the authors' pinned CBSH2-RTC implementation. SOC pair weights cannot
simply be imported: a six-cell control has optimal pair SOL 7 and SOC 8.

## Exact scope, costs and failures

For each of the unchanged headroom tool's disjoint forced-conflict pairs, delete
outside agents and search the static ordered-position product graph. Keep waits,
goal departures, terminal goal holding, vertex exclusion and edge-swap rejection.
Each transition costs one per agent unless both endpoints are its own goal.
The individual BFS distance sum is a consistent heuristic. A terminal pop gives
an exact pair optimum; at the pop cap, the minimum live frontier value is only a
lower bound. Prior valid unit-conflict evidence is retained by maximum.

The declared first-eight-pair maze pilot improved the full maze bound to 5991,
using 14,155 pops. Its original [pilot.json](pilot.json) and [journal](pilot.jsonl)
are unchanged. The panel then used the frozen implementation on all 521 pairs:
**142,510 pops** against a maximum **5,210,000**, no pair exceeding 10,000 pops.
Two original-maze pairs hit the cap: agents `[12,81]` returned lower bound 159,
and `[39,102]` returned 164. They are not labeled exact optima. The other 519 pairs
finished exactly. Every pair attempt, status, state count, queue size, timing,
instance/map hash and inherited feasible pair-cost upper bound is retained in
[panel.json](panel.json) and its independently cross-checked [journal](panel.jsonl).

The panel took 25.4828 seconds wall and 25.3907 seconds process CPU, including
all preprocessing and inherited-route checks; Linux peak RSS was 48,876 KiB.
A 1 GiB address-space cap was applied. The 1800-second panel deadline was checked
between pair searches; an external `timeout 1800` also bounded the actual panel
command. The pilot had a 180-second deadline and completed in 1.1436 seconds.
These are shared-machine observations, not isolated timing comparisons or speedups.

No parameter sweep, alternate pair set, wider search cap or research pivot was
used. All inputs are published calibration cases; the original maze was the
declared development/pilot case. No fresh holdout or transfer claim follows.

## Verification and replay

[verify_panel.py](verify_panel.py) parses the raw grids and computes its own BFS
distances. It uses cost-ordered search and admissible pruning to exhaust every
pair route cheaper than each claimed bound. It imports neither the optimizer nor
its model/grid helpers. A verification cap produces an inconclusive result and
cannot pass a bound. All 521 claims and their disjoint sums pass; the checker used
124,151 pops in the original 4.2052-second check. [verification-v3.json](verification-v3.json) binds the
report and verifier hashes and records every case. It also rejects an inflated
bound with an explicit cheaper cost-6 route, rejects overlapping/aliased agent IDs,
and validates canonical case coverage and fixed pair identities against the pinned
headroom scope. A duplicate case is rejected even when row and pair counts match.
This is a separate implementation run by the author, not independent human review.

The tiny controls exhaust all 1080 start/goal assignments on a six-cell loop,
four-cell branch and three-cell corridor across seven pop caps, comparing against
a separate unheuristic Dijkstra oracle. Additional controls require an initial-goal
departure, distinguish SOL 7 from SOC 8, reject swaps and malformed inputs, test
terminal holding, and reject inflated bounds and overlapping matchings. The 21
existing repository tests plus eleven package tests pass (32 total). The quick
source/historical-artifact check passes. Final commands and outputs are in
[checks-v3.json](checks-v3.json); prior check versions remain preserved.

With the project environment active, from the repository root:

```sh
python -m pytest -q tests research/headroom-pairs-ee542d9b/test_pair_bounds.py research/headroom-pairs-ee542d9b/test_verify_panel.py
python tools/check.py --quick
python research/headroom-pairs-ee542d9b/verify_panel.py --out verification-new.json
timeout 1800 python research/headroom-pairs-ee542d9b/run_bounds.py --out research/headroom-pairs-ee542d9b/panel-new.json
```

Outputs refuse to overwrite prior files. The current panel runner has not changed
since the frozen implementation; its hashes are in the report. The original pilot
used earlier uncommitted versions of two scripts. Standards review found those
versions missing; [pilot-source/](pilot-source/README.md) now preserves their exact
hash-matching bytes and explains isolated replay at the protocol commit. The saved
[pilot replay](pilot-replayed.json), [journal](pilot-replayed.jsonl) and
[comparison](pilot-replay-check-v2.json) match every deterministic field of the
original, explicitly excluding timestamps, timings and peak RSS. Peak RSS was
25,188 KiB originally and 25,612 KiB on replay; neither is claimed equal. The
original comparison's broader flag is retained but superseded by this correction.
The post-pilot changes were validation/accounting checks, not search-method tuning.

The first separate-checker version accepted negative Python aliases for agent IDs
and checked counts without canonical case/pair identity. Both defects were found
and fixed before submission, with rejecting regression controls. All actual panel
IDs and cases were valid, so bounds did not change. `verification.json` and its
source at commit `7f07fda130fc4cd009c7dbe9036de2377d813ea4` retain version 1;
`verification-v2.json` and source commit `5af1cabe3a3ee13cb65d1763fe028a6e8ffc8e40`
retain the ID fix; `verification-v3.json` records the scope-aware checker.
Final verification additionally requires the complete seven-file producer/source
manifest before hashing, preventing an empty or partial dictionary from skipping
checks. `verification-v4.json` binds this checker; `checks-v4.json` records the
32-test suite and quick check. All four versions certify the same 521 bounds
with 124,151 threshold-search pops; original source/data/reports remain retained.

## Review, provenance and limits

[REVIEW.md](REVIEW.md) keeps the Standards and Spec review axes separate, including
the initial pilot-source omission and its resolution. Reviews are author-assisted
agent checks. They do not establish independent scientific acceptance.

Author: OpenAI Codex, `gpt-6.1-sol`, max reasoning effort; same contributor account
as the predecessor. A research-skill agent investigated primary literature; two
code-review-skill agents checked standards and protocol/soundness. This conversation
did not prepare the original pilot. Tested Linux x86-64, Python 3.13.5, pytest 9.1.1,
jsonschema 4.26.0 in the session-local environment. No new dependency, native build
or solver binary is needed. Exact hashes bind the implementation and input sources.

Not checked: independent human/domain review, macOS/Python 3.12 setup, unseen
inputs, a general runtime advantage, maximum-weight pair selection, overlapping
pair aggregation, full historical/round-two certificate sweeps, or optimality of
the complete multi-agent instances. The two capped pair optima remain unknown.

Credit @thakrarsagar for the headroom ranking, witness audit and handoff; Douglas
Colkitt and project contributors for the archive, checker and headroom tool;
Felner/Li and coauthors for dependency/weighted-dependency heuristics; Keisuke
Okumura for SOL/configuration-graph semantics and LaCAM3; and Nathan Sturtevant /
Moving AI Lab for the benchmark data. Preserve [THIRD-PARTY.md](../../THIRD-PARTY.md),
[data/NOTICE.md](../../data/NOTICE.md), and ODC Attribution 1.0 notices.

## Full-graph follow-up

[PR #7](https://github.com/discoveryathome/pathfinding/pull/7) now provides the
full forced-conflict-graph study with explicit fractional-matching and integer
assignment-dual certificates. It verifies pair weights and aggregation separately
and improves sixteen of these twenty bounds. This package retains the fixed
521 disjoint pairs as its reproducible baseline.
