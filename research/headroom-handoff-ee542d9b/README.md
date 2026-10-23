# One bounded repair from the open headroom handoff

On the exposed `maze-32-32-4-n128` instance, one predeclared random4 repair reduced
SOL **7815 → 7802** and SOC **8225 → 8223**, with makespan **125 → 125**. This is a
proposed, author-checked route. It is not an accepted frontier update, a new
algorithm, an optimality result, an unseen transfer result, or a speed comparison.

This takes up [@thakrarsagar's headroom handoff](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19132179),
following its 20-case ranking and 43-witness maze audit (predecessor fork commit
`9e23023`). The predecessor identified the case and question; this session adds
the fixed-cap repair, exact route, failed attempts, resource ledger and replay.
The [claim](https://github.com/discoveryathome/pathfinding/discussions/2#discussioncomment-19139269)
was posted before computation. Both sessions use the `thakrarsagar` GitHub
account; no separate human contributor or independent human review is implied.

Base commit: `37823dca1bea271510e3ed62205620466ec6f0f9`. Priority revision: 3.
Seed: `ee542d9b4c91949140f009a90142f5ba`, converted with `int(seed, 16)` to
`316793340945421113888006999147102270906`. The repository's own picker draws
`headroom`. Its matching open handoff takes precedence over repeating the ranking.
The protocol and recorder were committed before the search at `a9c1b5c`.

## Fixed scope and complete attempt accounting

[protocol.json](protocol.json) binds the instance, map, inherited candidate and
unchanged implementation by SHA-256. The inherited route is the current minimum-SOL
Pareto candidate `random4-seed29`, not the obsolete native starting plan.
There was one search run, one variant and one seed; no parameter tuning or pivot.

The declared limits were 100,000 popped states, 96 attempts, 10,000 pops per
low-level agent search, and a 600-second external wall cap. The run used exactly
100,000 pops in 17 attempts. Fourteen neighborhoods completed; three stopped at a
search cap, retaining their failed work. Two proposals were accepted (zero-based
attempts 8 and 15). Attempt 13 proposed worse metrics and was rejected.
[experiment/trace.json](experiment/trace.json) retains every attempt, selected group,
pop count, status, proposal metrics, and both accepted intermediate routes.

The first accepted route had SOL 7813 / SOC 8223 / makespan 125. The final route has
SOL 7802 / SOC 8223 / makespan 125. Agent 29 saves two final-arrival and SOL units;
agents 4 and 31 save two and nine SOL units respectively with unchanged final
arrival times. Thus eleven of the thirteen SOL units are additional zero-cost
goal-holding transitions, consistent with the model's allowed goal departures.
This is not a thirteen-unit improvement in total final-arrival time.

The regenerated [20-case headroom report](headroom.json) reproduces distance bound
5926 and disjoint-pair bound 5969 for this case, including 43 witnesses. The SOL
bound gap falls from 1846 to 1833. This is a gap to a lower bound, not evidence that
1833 more units are achievable. This session does not repeat the predecessor's
independent wavefront witness implementation.

## Evidence and replay

Candidate SHA-256:
`1e2836611e43e0346ac1e24cf6bd40304cf40297d9f9ac8406aff8b039fc5561`.
The exact candidate is [experiment/candidate.json](experiment/candidate.json),
and its completed provenance is [experiment/handoff.json](experiment/handoff.json).

From the repository root with the project environment active:

```sh
python tools/verify_candidate.py data/instances/maze-32-32-4-n128.json research/headroom-handoff-ee542d9b/experiment/candidate.json
python research/headroom-handoff-ee542d9b/audit.py
python -m pytest -q tests
python tools/check.py --quick
```

The standalone checker accepts the inherited, final and both accepted intermediate
routes. [audit.py](audit.py) recomputes final-arrival and loss metrics, checks source
hashes, trace accounting, nonregression, and unchanged agents outside each accepted
neighborhood. It rejects deliberately wrong instance binding, wrong SOL, and forged
pop accounting. Its deterministic replay reproduces **all non-timing trace fields**,
including paths, every attempt, and budgets. This replay spends another 100,000
pops on the same computation and is verification, not an additional selected run.
Total search work including this one replay is 200,000 pops.

All 21 existing Python tests passed. Their controls include vertex collisions,
edge swaps, terminal goal holding, goal departure/revisit metrics, bad certificates,
future goal blocking, exact tiny joint-search comparisons, and capped replay.
The final quick check passed, including maintained and historical artifact bindings.
Raw commands, outputs, return codes and resource observations are in [logs/](logs/).

Observed original-run optimizer time was 1.0684 seconds, including 0.0770 seconds
preprocessing. The contribution command including certificate checks and output
took 2.3454 seconds wall, 2.2835 seconds child user CPU and 0.0383 seconds child
system CPU, with peak child RSS 29,716 KiB on Linux. The recorder's wall measurement
includes process startup and parent capture; it is not pure solver wall time.
These are contextual observations on a shared machine, with no speedup claim.

## Environment, setup and limitations

Agent: OpenAI Codex, `gpt-6.1-sol`, max reasoning effort. This conversation did not
prepare the project or the predecessor package; the agent read their published
evidence during orientation. All checks here were run by the authoring agent.
Scientific acceptance and independent human domain review remain pending.

Tested: Linux x86-64, kernel `6.12.113+deb13-amd64`, glibc 2.41, Python 3.13.5,
pytest 9.1.1, jsonschema 4.26.0. The installed dependency versions are recorded in
[environment.json](environment.json). The initial quick check used system
jsonschema 4.19.2; the final check used the repository-pinned 4.26.0.

The documented uv/Python 3.12 setup was unavailable. For this pure-Python task the
actual local setup was:

```sh
python3 -m venv .venv --system-site-packages --without-pip
.venv/bin/python -m ensurepip --default-pip
.venv/bin/python -m pip install pytest==9.1.1 jsonschema==4.26.0
```

The sandbox initially could not resolve external hosts. Authorized network
operations used command escalation; repository computations ran sandboxed.
The optional helper matched its pinned SHA-256 and `discover screen repo` returned
no findings before execution. Context-mode's URL helper failed because `turndown`
was missing; its subprocess could not see this workspace, so bounded native output
processing was used. No coordinator assistance or research-scope revision was
required after the protocol.

Not checked: documented Python 3.12/uv/native setup, macOS or other Python versions,
new native LaCAM3/LNS2 runs, full historical `tools/check.py` or
`tools/check_round2.py`, unseen inputs, optimality, physical robot safety, or
independent scientific review. Source/archive/frontier records are unchanged.
No wall/CPU-matched baseline comparison was attempted.

## Credit and open next questions

Credit @thakrarsagar for the predecessor ranking, witness audit and concrete
handoff; Douglas Colkitt (@Mister-Meeseeks) and project contributors for the archive,
checker and pilot; Keisuke Okumura's LaCAM3 at
`1c3ecf8ade40298f16047544634e9c0c1cf3b93c`; established MAPF large-neighborhood
and prioritized space-time A* methods; and Nathan Sturtevant / Moving AI Lab for
the benchmark. Contains information from the Moving AI benchmarks, available under
ODC Attribution License 1.0. Preserve [THIRD-PARTY.md](../../THIRD-PARTY.md),
[data/NOTICE.md](../../data/NOTICE.md) and their license notices.

The next useful question is a scoped reviewer check of the eleven SOL-only units:
can a checker implemented without optimizer imports confirm the accepted goal
holding/revisit transitions for agents 4 and 31, with meaningful collision and
metric failure controls? Start from the bound candidate and the two intermediate
routes, then report exact SOL/SOC/makespan agreement or a minimized counterexample.
An author rerun is not independent review. Frontier promotion remains a maintainer
decision; no archive update is part of this contribution.
