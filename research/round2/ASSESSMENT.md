# Pathfinding assessment after round two

**Ready for limited pre-release contributor distribution and expert-agent review.**
There is repeatable, precisely checkable local solution progress across a broader
panel. No new generally superior algorithm, global record, optimality proof or
physical-robot result has been established. Intake is open; scientific review is pending.

## What changed

Twelve fresh Moving AI scenarios on six maps, 128–256 agents, now supplement the
original eight cases. Map sizes are 32×32, 48×48 and 64×64. Scenario 2 on empty32,
random32 and room32 was development; the other nine cases were evaluation. Larger
maps are new families/sizes; fresh scenarios on prior families are not entirely
new distribution evidence. Three repair seeds per case are not independent maps.

Sixty native runs supplied 57 independently checker-validated witnesses. Unmodified
LaCAM3 ran for 6 and 12 seconds; the newer SoCS-2025 PIBT preference implementation
ran with three seeds and a 6-second limit. Its three failures on one maze are retained.
LaCAM3 supplied every chosen starting plan. Native deadlines under shared load are
context comparisons, not equal-CPU rankings. MAPF-LNS/LNS2 has not been reproduced,
and the baseline set does not establish current state-of-the-art competitiveness.

Ninety bounded repairs tested random-four, proximity-four, corridor-four and
two-agent joint search. Each used at most 100,000 popped search states, 96 attempts
and 10,000 states per low-level search. Joint states generate more successors;
these caps do not equalize computation. Actual elapsed times and failures are kept.
The joint solver optimizes SOL; the original prioritized solver minimizes arrival
time for each selected agent. The same final no-regression gate applies to all.

## Results

| Panel | Inherited SOL | Random-four SOL | Proximity-four SOL |
|---|---:|---:|---:|
| Development, 3 cases × 3 seeds | 50,214 | 50,141 | 50,176 |
| Evaluation, 9 cases × 3 seeds | 186,567 | 186,451 | 186,437 |

Corridor-four (50,172) and joint-two (50,175) did not beat random-four in development.
The fixed selection rule therefore retained random-four. The prespecified
proximity challenger was 14 SOL units better on evaluation (0.0075% of inherited
cost), but that does not retroactively change development selection. Random repair
improved primary cost on 12/27 evaluation case/seed runs; proximity on 21/27.
Evaluation arrival-time totals were 191,469 inherited, 191,378 random and 191,259
proximity. This is a small panel with mixed algorithm-selection evidence.

Taking the best observed witness per case across all runs, the new archive improves
primary cost on **all 12 cases**, by **118 units in total** against
78,927 summed native-best SOL (0.150%). This is an after-search archive result
with multiple attempts, not a single-policy success rate or fair-budget algorithm
comparison. Every accepted repair also avoids SOC and makespan regression against
its starting plan. The archive keeps metric tradeoffs and includes all native results.

All final and accepted intermediate paths were checked independently of search.
Tiny exact dynamic-programming controls validate joint-search cost; goal blocking,
budget exhaustion and deterministic replay have tests. A full run reproduced paths,
metrics, history and budget exactly. This remains author-run verification, not an
independent external contributor or expert study.

## Distribution and next contributions

The maintained archive has 20 cases across both rounds. Contributors inherit its
strongest applicable witness. A one-command contribution produces a new candidate,
trace and handoff even when no improvement is found. The [round-two playback](../../visuals/round2.html)
shows actual native, repair and current-best routes with evidence hashes.

Prioritize: (1) independent checker/replication work; (2) matched-objective MAPF-LNS2
or other strong contemporary baseline comparisons; (3) structured bottleneck repair
on new scenarios; (4) stronger lower bounds and realistic application workloads.
Do not repeatedly advertise the same small gains from the old starting solutions.
A MAPF/operations-research reviewer can help establish baseline authority and useful
headroom; a warehouse/game partner can define practical workloads. Neither is an
intake gate for local trial contributions.

See [distribution instructions](../../DISTRIBUTION.md), [round-two protocol](PROTOCOL.md),
[complete summary](summary.json), and [original assessment](round1-assessment.md).
Sources: [LaCAM3](https://github.com/Kei18/lacam3),
[PIBT preference construction](https://github.com/HirokiNagai-39/pibt-tiebreaking),
[Moving AI](https://movingai.com/benchmarks/mapf/index.html).

## Bounded handoff smoke

A subsequent author-run 30,000-state contribution inherited the improved maze
archive and found two further SOL units (6,204 → 6,202), two SOC units (6,480 →
6,478), and one makespan step (109 → 108). Its verified candidate is now inherited.
This raises the current archive gain to 120 units across the 12 new cases; the
predeclared 90-run experiment remains 118. It demonstrates incremental handoff
progress, not an independent donor study. Evidence: ../round2-smoke/.
