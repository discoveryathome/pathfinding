# Multi-agent pathfinding — local Discovery@Home pilot

**Open for local trial contributions and expert-agent review.**

This pilot tests whether bounded neighborhood repairs can improve verified grid
plans inherited from LaCAM3. Eight instances with 64–256 agents, 56 repair trials,
separate collision/cost verification and an interactive playback are prepared.

Read [the assessment](research/ASSESSMENT.md), then open
[the verified-plan playback](visuals/pathfinding.html). All initial evidence is
author-checked; no novel algorithm or accepted performance record is claimed.

## Start

Requires Python 3.12, `uv`, Git and a C++17 compiler. Tested on macOS/Apple Clang.

```sh
sh tools/setup.sh
source .venv/bin/activate
python tools/check.py --quick
python tools/pick.py --seed 42
```

`python tools/check.py` runs the tests and rechecks every archived route, including
accepted intermediate repairs. A lightweight candidate check is:

```sh
python tools/verify_candidate.py data/instances/room-32-32-4-n160.json results/repair/room-32-32-4-n160-proximity4-s17.json
```

See DISCOVERY.md for a one-command contribution from the current local incumbent.
Replay experiments in a copy: `tools/prepare.py` and `tools/run_trial.py` overwrite
experiment outputs, and asynchronous native deadline runs can produce new routes.
The verifier is reproducible from frozen routes; repair reruns are deterministic.

The playback is a self-contained local file. To rebuild it, run
`python tools/build_visual.py`. Browser checks optionally use requirements-visual.txt
and a local Chrome installation; they are not needed for route verification.

The local `discover.json` has a file URI and no hub enrollment. No remote was
created. Pilot-owned code is MIT; solver and benchmark notices remain separate.

- [Contributor entry](AGENTS.md)
- [Trial protocol](research/PROTOCOL.md)
- [Current candidate archive](discover/incumbents.json)
- [Sources and licenses](THIRD-PARTY.md)
- [Review handoff](research/REVIEW.md)
