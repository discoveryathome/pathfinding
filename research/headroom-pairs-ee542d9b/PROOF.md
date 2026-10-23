# Scope of the pair bound

This is an adaptation of established pair-dependency lower-bound reasoning, not a
new MAPF technique. Primary-source attribution and differences from SOC literature
are recorded separately in LITERATURE.md.

An agent's SOL charges a transition unless both endpoints are its goal. Its
individual shortest grid distance `d_i` is a lower bound on that cost, including
when it visits a goal and later departs. Every off-goal move or wait costs one;
goal waiting cannot reduce the number of charged moves needed to reach the goal.

## Two-agent relaxation

Delete every other agent and retain the two agents' static grid, distinct starts
and goals, vertex exclusion, edge-swap exclusion, and endpoint holding. A state is
their ordered positions. A transition chooses a legal grid neighbor or wait for
each agent and costs the sum of the two SOL charges. Goals are not absorbing.

Any valid global schedule projects to a walk in this graph; extending its shorter
path by goal holds changes neither cost nor validity. The projected prefix ending
when both agents first occupy their respective goals has cost at most their full
global cost and can end there because both goals are distinct and static. Conversely
any product-graph walk ending at the two goals is a feasible relaxed schedule with
permanent terminal holding. Thus its shortest-path cost `C_ij` is a lower bound on
the pair's contribution to any full valid plan. There is no outside trajectory or
time-dependent constraint in this relaxation, so absolute time need not be state.

Removing a simultaneous wait self-loop is safe: it leaves positions unchanged,
has nonnegative cost, and there is no external clock to synchronize with. This
does not prohibit one agent from waiting while the other moves. A goal departure
continues to cost one; no agent is deleted when it reaches its goal.

## Capped A* lower bound

The heuristic `h(u,v) = dist(u,g_i) + dist(v,g_j)` is nonnegative and consistent:
an off-goal transition costs one and changes grid distance by at most one; an
at-goal hold costs zero and leaves distance zero. Costs, heuristic values and all
comparisons are exact integers. Each live heap entry has the best discovered cost
to that position pair; stale entries are ignored for expansion/frontier bounds.

Before reaching a terminal state, the live frontier contains a state on some
optimal path with its optimal prefix cost, so its minimum `f=g+h` cannot exceed
`C_ij`. A popped terminal state has `h=0` and attains the optimum. At a pop cap,
all previous live pops have been fully expanded; return the minimum live `f`,
not a guessed terminal cost. If all live states are exhausted, the pair is
infeasible. A known valid global certificate rules that case out for the panel.
Every pop, including stale entries, counts toward the declared cap. A capped
bound is not labeled an exact pair optimum.

## Disjoint aggregation and retained forced-conflict evidence

For the existing pairwise-disjoint matching `M`, use a certified lower bound
`L_ij <= C_ij` for each pair and `d_i` for unmatched agents. Summing disjoint
contributions gives a global SOL lower bound. The existing forced-shortest-path
witness already proves `C_ij >= d_i + d_j + 1`; taking the maximum of that bound
and the search lower bound is therefore safe. For a pilot or wall-limited panel,
unsearched pairs retain their old `+1` evidence. No pair's agents are counted twice.

For each agent, SOL is at most its final-arrival time: after final arrival all
holds are free, and each earlier transition costs at most one. The same global
SOL lower bound is consequently also a SOC lower bound. This does not assert that
the minimizing SOL and SOC schedules coincide or give a makespan bound.

The inherited valid plan supplies an upper bound on every relaxed pair cost.
Before the pilot, these upper bounds priced the strongest possible fixed-pair
result: on the original maze, the matching's total excess-cost ceiling is 1570,
versus the present 43-unit bound. A gain of at most 1527 is possible for this
matching, so this relaxation is not ruled out by its fully charged best case.
This ceiling is not an achieved or guaranteed improvement.

All inputs are published calibration cases. Tiny exhaustive oracle agreement and
author checks are evidence for this implementation; they are not independent
human review or an optimality claim for the 128–256-agent problem.
