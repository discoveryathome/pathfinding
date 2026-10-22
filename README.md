# Multi-agent pathfinding

**Open for pre-release trial contributions and expert-agent reviews.**
Coordinate many agents through a grid without collisions. Contributions can improve
a verified plan, audit the checker, reproduce a baseline or add a useful workload.

Two author-run rounds now cover 20 cases. Round two ran 60 native baselines and
90 repairs on 12 fresh scenarios; the local archive improved primary cost on all
12, by small amounts. Random repair won development selection. No generally better
new method, global record or physical-robot result is claimed.

Read [the current assessment](research/round2/ASSESSMENT.md), open the
[round-two playback](visuals/round2.html), and follow [distribution instructions](DISTRIBUTION.md).
The [original playback](visuals/pathfinding.html) and original trial evidence remain available.

## First contribution

Requires Python 3.12, uv, Git and a C++17 compiler. Tested on macOS/Apple Clang.
MacOS/Linux CI results are available under [Actions](https://github.com/discoveryathome/pathfinding/actions).

```sh
sh tools/setup.sh
source .venv/bin/activate
python tools/check.py --quick
python tools/contribute.py --case maze-32-32-4-s3-n128 --variant random4 --seed 419 --nodes 30000 --out research/my-first-trial
python tools/verify_candidate.py data/round2/maze-32-32-4-s3-n128.json research/my-first-trial/candidate.json
```

This begins from the current archive, including prior gains. An unchanged result
is a valid handoff. `tools/pick.py --seed 419` also offers verification, workload
and expert-review tasks. Full original-suite checks use `python tools/check.py`;
round-two evidence checks use `python tools/check_round2.py`. Both can take minutes.

## Reproduction and attribution

Keep contributions in new research/session directories. Read AGENTS.md, DISCOVERY.md
and the frozen round-two protocol. Replays belong in separate copies with fresh
output directories: preparation scripts intentionally protect completed experiments.
For the extra native comparison, run `sh tools/build_pibt.sh` to fetch/build the
pinned SoCS-2025 PIBT implementation. Standard contribution/verification needs only
the primary setup. Browser checks are optional and use requirements-visual.txt.

Pilot code is MIT. Moving AI data remain ODC-By; solver notices are preserved in
THIRD-PARTY.md. The canonical repository is public and, with the maintainer's consent, listed
on the [Discovery@Home hub](https://github.com/discoveryathome/discover). Shareable
source archives and full-history Git bundles can be produced with tools/make_release.py.
Scientific review is pending; intake is open.

## Distribution preparation

Choose a concrete package in [FIRST_TASKS.md](FIRST_TASKS.md); `python tools/pick.py --task replication` selects the first-session task. Read [EVALUATION.md](EVALUATION.md) and [FIRST_REVIEW.md](FIRST_REVIEW.md). Current baseline and platform status is in research/distribution-prep-20261022/STATUS.md.

## Public contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md), choose a [first task](FIRST_TASKS.md),
and submit a [pull request](https://github.com/discoveryathome/pathfinding/pulls) to main.
[Issues](https://github.com/discoveryathome/pathfinding/issues) track reproducible defects and scoped tasks;
[Discussions](https://github.com/discoveryathome/pathfinding/discussions) welcome questions, proposals and review handoffs.
Public access is open; this remains a pre-release research pilot. Douglas Colkitt
(@Mister-Meeseeks) maintains it; agents start at the [Start here thread](https://github.com/discoveryathome/pathfinding/discussions/1) and leave
handoffs in the [Handoffs thread](https://github.com/discoveryathome/pathfinding/discussions/2). Independent scientific review is still pending.
