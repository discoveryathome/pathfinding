# Bounded low-level objective

Fix the other agents' paths, their vertex and reverse-edge reservations through
the current global makespan `T`, one replanned start and goal, and a final-arrival
deadline at most `T`. A state is `(v,t)`. A legal transition advances time by one
and uses a grid edge or wait, avoiding the reservations. Its SOL cost is zero
only when both endpoints equal this agent's own goal; otherwise it is one.

For any fixed `(v,t)`, a lower accumulated SOL dominates a higher one: both have
the same remaining legal moves, same time and same future reservations. Retaining
only the smallest SOL label per state is therefore sound. Equal labels need no
second parent. Improved labels replace the parent and stale heap entries still
consume the declared pop allowance before being skipped.

Let `d(v)` be the static shortest-path distance to the goal, ignoring other
agents. Every route from `v` to that goal needs at least `d(v)` charged transitions
and at least `d(v)` time steps. Thus `(g + d(v), t + d(v))` is a lexicographic lower
bound on `(final SOL, final arrival)`. Its primary component is consistent for
every legal edge, including zero-cost goal holds. On edges where the primary
component ties, the secondary bound cannot decrease. The heap orders these two
components first; subsequent tie breakers do not affect optimality.

A goal state is terminal only after the last reservation of that goal through
the full global horizon, so holding it forever is safe. Earlier goal visits may
wait or depart; they are not absorbing. A terminal state's two heap bounds equal
its actual objectives. Consequently the first live terminal popped is a
lexicographically minimum `(SOL, final arrival)` legal route within the deadline,
provided the pop cap has not interrupted search. Reservation suffix checks remain
through `T` even in the declared, unused per-agent-deadline pivot.

The state graph is finite and time strictly increases. Queue exhaustion proves
no route in this *fixed-reservation, fixed-deadline subproblem*. A cap returns no
candidate and proves nothing about feasibility. The prioritized four-agent
sequence can miss jointly feasible or better solutions; the low-level argument
does not establish global MAPF optimality or a globally superior repair policy.
The unchanged macro Pareto gate and standalone checker establish the metrics and
validity of each retained improvement.

The tiny DP oracle in `test_sol_repair.py` enumerates time layers without the
production heap/heuristic. A separate 70-walk enumeration checks the six-cell
counterexample independently of that DP. These finite controls support the code
implementation; they do not replace the argument above or human scientific review.
