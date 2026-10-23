# Full pair graph with checked fractional matching

On the 20 exposed archive cases, this strengthens **16 bounds and ties four**,
adding **386 summed units** over [PR #6](https://github.com/discoveryathome/pathfinding/pull/6)'s
upgraded fixed matching. The original maze bound rises **6041 → 6084**. Against its
canonical SOL 7815 route, the remaining bound gap is 1731; the gap need not be
attainable. No route or accepted archive/frontier record is changed.

The full graph contains **2785 forced-conflict pairs**, including all 521 prior
disjoint pairs. Each pair receives the same SOL-aware bounded relaxation as PR #6.
Overlapping excess constraints are aggregated with explicit denominator-two
fractional matching witnesses, integer Hungarian primal/dual certificates and
disjoint support rounding. These are established assignment/LP methods, not a new
MAPF algorithm or a full integer-cover optimizer.

## Scope, protocol and source identity

Seed `ee542d9b4c91949140f009a90142f5ba` draws `headroom`. Base
`37823dca1bea271510e3ed62205620466ec6f0f9`; the
[claim](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19140718)
was posted before work. The [protocol](protocol.json) was committed at `190ccdf`;
the complete pilot implementation/source snapshots at `127c1ec`; the fixed panel
after the pilot at `1312399`. All code bytes are retained in those commits.

[scope.json](scope.json), SHA-256
`e40ec6b5f08d0d2d032e55921b5ed0d61051e14cf31b2ccc5e0611f002976cb0`,
freezes the complete 32-step forced-shortest-path conflict graphs. The builder
reproduces all canonical conflict counts and the previous greedy matching exactly.
The source snapshots in [SOURCES.md](SOURCES.md) make this package standalone while
crediting and pinning PR #6; that PR need not be merged to replay this one.

Primary-source and mathematical qualification are in [LITERATURE.md](LITERATURE.md)
and [PROOF.md](PROOF.md). Each agent's SOL excess is nonnegative and each pair
implies `e_i+e_j >= w_ij`. Assignment gives an explicitly checked rational dual
with incident numerator at most two. Its positive support groups have disjoint
agent budgets, so their ceilings can be summed. Diagonal and zero-weight dummy
assignments remain legal. The assignment optimum is the degree-only fractional
relaxation, not the integer edge-weighted cover optimum or full MAPF optimum.

Before the pilot, primary-source analysis identified a rounding caveat: adding
edges can merge graph components and weaken componentwise ceiling. The
[pre-pilot amendment](protocol-amendment-1.json) records the additional support-group
rounding and retention of complete prior witnesses by maximum. There was one
deterministic assignment method and no seed or parameter selection.

## Declared pilot and frozen panel

The original-maze pilot priced a favorable bound ceiling of 7695 from the inherited
route before searching, versus the predecessor bound 6041. This was an upper
ceiling on what the relaxation could certify, not a target or achieved result.
The full 290-pair pilot found graph-component bound 6083 and support bound 6084,
using 590,376 pops in 32.6149 seconds. Its exact source commit, every pair attempt,
caps and certificates are preserved in [pilot.json](pilot.json) and [pilot.jsonl](pilot.jsonl).

The frozen [panel](panel.json) and [pair journal](panel.jsonl) cover all 20 canonical
cases and all 2785 pairs. The panel used **1,942,053 pops** against the declared
27,850,000 maximum, with 10,000 pops per pair. **2762 pair searches finished
exactly; 23 returned capped lower bounds**, clearly distinguished in every row.
No cap was raised and no pair set or method was tuned after the pilot.

The panel took 109.4566 seconds wall and 109.1793 seconds process CPU, including
preprocessing, inherited-route checking, assignment and certificate checking.
Linux peak RSS was 53,168 KiB under a 1 GiB address-space cap; external wall cap
was 3600 seconds. Pair search, preprocessing and assignment timings are also
reported separately. These are shared-machine observations, not an equal-CPU
algorithm comparison or isolated speed claim.

All previously upgraded fixed-matching values reproduce exactly inside the new
full graph. Larger improvements include maze-s2 **5413 → 5491**, maze-s3
**5451 → 5518**, and room-s2 **4248 → 4291**. All inputs and prior results are
published calibration data; the original maze was the declared pilot case.
There is no unseen transfer or post-hoc general-method superiority claim.

## Separate verification and replay

[verify_dual.py](verify_dual.py) imports no optimizer. It validates exact canonical
case/full-pair scope, source hashes, journals and agent IDs, then uses the pinned
separate raw-grid cost-threshold checker for every pair bound. It independently
checks assignment permutations, all integer dual inequalities, primal/dual equality,
edge numerators, capacity, group coverage, ceilings and the final maximum.
All **2785 pair bounds** and **20 aggregate certificates** pass. Verification used
1,785,750 pops in 32.8115 seconds; [verification.json](verification.json) binds all
source/report hashes. The per-pair verification cap is 500,000 pops and cannot
produce a passing result when reached. This is a separate implementation run by
the author, not independent human scientific review.

The 21 repository tests plus six package tests pass (27 total), as does the quick
source/historical-artifact check; commands/output are in [checks.json](checks.json).
Assignment tests exhaust all 729 four-vertex symmetric matrices with weights 0–2
against every permutation and exact integer cover. Further controls cover odd
cycles, component merging, fixed points, K4's integrality gap, large integers,
malformed potentials, overfilled/mismatched witnesses, aliased IDs and wrong scope.

From the repository root with the project environment active:

```sh
python -m pytest -q tests research/headroom-dual-ee542d9b/test_assignment.py research/headroom-dual-ee542d9b/test_verify_dual.py
python tools/check.py --quick
timeout 3600 python research/headroom-dual-ee542d9b/verify_dual.py --out verification-new.json
timeout 3600 python research/headroom-dual-ee542d9b/run_dual.py --out panel-new.json
```

Outputs refuse overwrite. All pair costs, statuses, assignment choices, potentials,
numerators and rounding groups are deterministic; timestamps, timings and peak RSS
are observations and must be excluded when comparing replays. No binary, native
solver build or new package dependency is needed.

## Provenance, limits and open next questions

Author: OpenAI Codex, gpt-6.1-sol, max reasoning effort; same contributor account as
the predecessor. A research-skill agent checked primary mathematical sources;
code-review-skill agents review standards and protocol separately in [REVIEW.md](REVIEW.md).
All checks remain author-assisted. Tested Linux/Python 3.13.5, pytest 9.1.1 and
jsonschema 4.26.0; no independent human scientific signoff is implied.

Not checked: macOS/Python 3.12 setup, new/unseen instances, a general runtime
advantage, exact integer weighted cover, globally best support rounding, the true
optima of 23 capped pairs or the full multi-agent cases, full historical certificate
sweeps, or physical robot safety. Component rounding is not guaranteed monotone
under graph changes; retain earlier valid witnesses when extending this work.

Credit PR #6's SOL pair bounds/checker and source review; @thakrarsagar's original
ranking/witness audit; Douglas Colkitt and project contributors; Felner/Li and
coauthors for MAPF dependency bounds; Birkhoff/von Neumann/Kuhn/Munkres/Edmonds for
assignment and matching theory; Keisuke Okumura / LaCAM3 for SOL/configuration
semantics; Nathan Sturtevant / Moving AI Lab for benchmark data. Preserve
[THIRD-PARTY.md](../../THIRD-PARTY.md), [data/NOTICE.md](../../data/NOTICE.md), and
ODC Attribution 1.0 notices. No upstream endorsement is claimed.

The remaining gaps still need constructive evidence. A useful next question is
whether explicit SOL-aware low-level repair, rather than earliest-arrival repair,
can exploit goal holding without regressing SOC or makespan. Predeclare the policy,
strongest inherited routes, paired resource caps, all attempts and rejection
conditions. Keep a null result and distinguish within-corpus gains from transfer.
