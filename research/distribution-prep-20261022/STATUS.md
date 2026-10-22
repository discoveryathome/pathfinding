# Current distribution status — pathfinding

Open for limited contributor trials and expert review. FIRST_TASKS.md supplies
four bounded entry points; EVALUATION.md defines exposed versus fresh evaluation;
FIRST_REVIEW.md is ready for an independent, uncoached participant.

## New evidence

MAPF-LNS2 was built at the pinned commit and 12 routes were checked in a paired
three-case/two-seed comparison with LaCAM3. The initial default pass is retained:
maxIterations=0 stopped improvement after feasibility. A separately declared
configuration correction enabled 1,000,000 iterations under the six-second limit.
All 12 corrected-pass routes verified. Three nondominated alternatives were added
to the archive. They improve SOC/makespan tradeoffs; the existing best-SOL starts
remain available and are not reset to easier targets.

Both methods receive a requested six-second limit and outputs use the same checker.
However LNS2 optimizes SOC while LaCAM3 optimizes SOL; assertion settings also differ.
Recorded elapsed times were about 6.25–6.73 seconds and include parent-side
parsing/verification, so they must not be labeled pure solver wall time. Child CPU
time is recorded separately. These are
baseline context measurements, not a matched-objective or equal-CPU algorithm ranking.
A domain reviewer should resolve the desired objective before a stronger claim.

The new headroom tool strengthens the obstacle-aware distance bound with disjoint
pairs forced to collide on all individually shortest trajectories. It improves
the lower bound on all 20 cases. Tiny exact joint-search controls test admissibility.
The archived report binds the incumbent at report time; after archive changes,
regenerate into a new output file. Remaining gaps need not be achievable.

## Reproduce / contribute

```sh
python tools/headroom.py --out research/my-headroom.json
python tools/pick.py --task replication
```

Optional baseline reproduction (Eigen 3.x and Boost required):

```sh
# macOS dependency setup: brew install boost eigen@3
# macOS only: export CMAKE_PREFIX_PATH="$(brew --prefix eigen@3);$(brew --prefix)"
sh tools/build_lns2.sh
python tools/compare_lns2.py --out research/my-baseline-comparison
```

On Linux the optional upstream dependencies are libboost-all-dev and libeigen3-dev.
LNS2 source/binaries are not included in our source release; its research license
remains separate. See THIRD-PARTY.md and lns2-source.json.

Linux execution and independent outside review remain pending; see MIGRATION.md.
The main contribution workflow does not require the optional LNS2 build.
