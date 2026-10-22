# Pathfinding pilot assessment — 2026-10-22

**Recommendation: promising as a visual, contribution-friendly optimization pilot;
keep it in local/pre-release incubation until a stronger transfer result exists.**
Compared with the earlier exact-predicate geometry trial, this is easier to explain
and produces a much clearer artifact: many agents moving without collisions.
It has an exact feasibility checker and reusable solution witnesses. This round
found small improvements but did not establish a broadly better search method.

## What was set up and actually run

Built pinned, unmodified LaCAM3, including its default enhancements. Downloaded
four public Moving AI grid families and scenario 1 for each. Eight 32×32 instances
have 64–256 agents; empty/random grids are development, rooms/mazes are held-out
families. Counts within a family are nested prefixes of the same scenario, not
independent observations. This is a small panel with two repair seeds, not a
statistical study or an independent donor experiment.

Sixteen native runs (3- and 6-second deadlines) all supplied feasible plans whose
routes, SOL, SOC and makespan matched a separate Python checker. Native deadlines
are affected by shared load and asynchronous refinement; the 6-second run is a
context comparison, not guaranteed to dominate the 3-second witness. No native
speed or equal-CPU superiority claim is made.

Ran 56 bounded repair trials, each starting from the same corresponding frozen
3-second plan, with up to 30,000 popped space-time search states and 64 neighborhood
attempts. A random four-agent neighborhood is the substantive local repair baseline.
Four alternatives used excess-cost or proximity selection and neighborhood sizes
1, 4 or 8. A common prioritized space-time A* engine replans the group. Failed
replans retain the incumbent. Only a strict gain with no regression in either
recorded cost or makespan is accepted.

All final and accepted intermediate plans pass the standalone pairwise checker.
It checks source binding, obstacles, endpoints, four-neighbor moves, vertex sharing,
edge swaps, future goal holding and cost accounting. Independent BFS lower bounds
are computed for the correct movement model. Small joint-state exact searches and
negative controls test the semantics. Repeating a full repair reproduced paths,
metrics, attempt history and expansion counts exactly. This is author-checked work
using a separately implemented checker, not independent human/scientific review.

## Results

The development selection chose **proximity-four repair**. Totals below include
both seeds on each of four instances per split; they are not eight independent maps.
Lower is better for both metrics.

| Panel and policy | Sum of loss (SOL) | Total final arrival time (SOC) |
|---|---:|---:|
| Development inherited plans | 31,512 | 32,708 |
| Development random-four repair | 31,493 | 32,694 |
| Development selected repair | 31,486 | 32,619 |
| Held-out inherited plans | 39,150 | 41,562 |
| Held-out random-four repair | 39,119 | 41,549 |
| Held-out selected repair | 39,126 | 41,539 |

The selected rule improves development SOL by only 7 over random repair (about
0.022%). On held-out maps it is **7 worse on SOL**, although 10 better on SOC.
Its improvement over the held-out starting plans is 24 SOL units (0.061%) and
23 SOC units (0.055%). These are real verified route changes, but small. It improves
four of eight held-out case/seed runs; it makes no progress on either maze instance.
Random repair makes a small primary-cost improvement in seven of those eight runs.
Do not present the selected heuristic as a general win or hide the null cases.

Including the six-second native context further limits the result: those plans
dominate the selected repairs on both room cases and the 64-agent maze. Across
all eight instances, the only strict SOL improvement over BOTH observed native
runs is a two-unit gain on the 128-agent maze, found by random-four repair. Other
repairs add some SOC/makespan tradeoff points to the local Pareto archive. Thus the
round demonstrates a useful workflow more strongly than a new competitive method.

SOL excludes a step only when an agent stays at its goal for that step. SOC counts
until the last arrival after any departure. They differ when agents visit and later
leave goals. Both must remain visible; the underlying LaCAM3 search optimizes SOL.
The baseline lower bound ignores other agents and is generally loose. A remaining
bound gap is not proof that an attainable improvement exists.

The solver and local repair techniques are established methods. No published
record, current-state-of-the-art advantage, formal optimality of these plans, or
new algorithm was established. Fixed popped-state budgets exclude preprocessing,
reservation work and neighborhood selection costs; actual runtime is separately
recorded, and the caps need not be exhausted. Do not equate them with equal CPU.

## Handoff state and practical usefulness

The project is locally committed, open for trial contributions and expert-agent
reviews, and includes an interactive playback of actual verified plans. The current
`discover/incumbents.json` archive merges all checked native and repair witnesses
and retains nondominated metric triples. New contributors must inherit that
stronger archive rather than re-solving the old raw 3-second frontier. It remains
an author-checked local archive, not a literature leaderboard or accepted finding.

Potential contributions include better neighborhood selection or joint repair,
robust failure handling, certificates/checker audits, competitive baseline
reproduction, and useful benchmark construction. This has more varied bounded
work than the narrow numerical-formula tuning trial. Exact paths make the outcome
easier to verify than many biological hypotheses. The initial small gains are
sufficient to test the workflow, not sufficient for a featured discovery claim.

Game movement and fleet/warehouse coordination are plausible application directions.
This model uses static grids, synchronized steps and point agents. Physical size,
turning, timing uncertainty, changing goals and safe robot control are absent.
Practical deployment value has to be demonstrated in the relevant richer model.

## Next work we can do locally

- Run fresh scenario files, larger maps, more seeds and a predeclared evaluation
  rule. Keep family-level transfer separate from improvements on exposed cases.
- Compare modern MAPF-LNS/LNS2 and newer PIBT preference baselines on exactly
  matched objectives; identify known algorithms before claiming any novelty.
- Add joint/corridor-aware repairs or adaptive neighborhoods to address the maze
  failures. Test improved candidates against the current archive and budgeted
  random repair, retaining every negative result.
- Profile total work and peak memory, and replicate on a quiet machine. This is
  necessary before efficiency claims, even though certificate validity is exact.
- Audit stronger lower bounds and add small exactly solved instances as controls.

## Outside help that would make this stronger

A MAPF/operations-research specialist should review baseline competitiveness,
search-budget fairness, neighborhood headroom and worthwhile open questions.
A game-navigation or warehouse-planning maintainer can supply a realistic objective,
layout and query distribution; a robotics claim additionally needs a physical
motion model and domain validation. An independent contributor should reproduce
one full handoff. These are routes to better evidence, not closed intake gates.

Sources: [LaCAM3 and its paper](https://github.com/Kei18/lacam3),
[Moving AI benchmarks](https://movingai.com/benchmarks/mapf/index.html), and
[newer PIBT preference work](https://github.com/HirokiNagai-39/pibt-tiebreaking).
The last is a comparison target, not a reproduced or surpassed result here.
