# Local multi-agent pathfinding pilot — frozen trial plan

Open for local contributions and expert-agent review. This is an author-run trial,
not an independent donor session or a new state-of-the-art claim.

Problem: labeled agents on four-neighbor unit-cost grids; wait actions allowed;
forbid vertex sharing and opposing edge swaps at integer time steps; after the
recorded horizon agents stay at their distinct goals. Agents may visit a goal and
later leave it. Track sum of final arrival times (SOC), sum of loss (SOL: steps
where either endpoint is not the agent's goal), and makespan separately.

Baseline: pinned, unmodified LaCAM3 with default enhancements and 3-second and
6-second wall deadlines. Those runs supply candidate witnesses, not a timing
competition under the current high load. Main repair comparisons all start from
the SAME frozen 3-second witness. If that run fails, retain the failure and use the
6-second witness explicitly as fallback; if both fail, retain the unsolved case.
An empty solution is failure even if the upstream verifier accepts emptiness.

Development: empty-32-32 (128,256 agents), random-32-32-20 (96,192 agents).
Held-out families: room-32-32-4 (96,160), maze-32-32-4 (64,128).
Use the first N rows of Moving AI random scenario 1; source rows and hashes pinned.
All cases fixed before seeing outcomes. Seeds 17 and 29 for repair runs.

Known-method repair baseline: random four-agent destroy/replan. Alternatives:
excess-cost single-agent and four-agent selection, proximity-based four-agent and
eight-agent selection. Use the SAME space-time A* engine, max 30,000 popped search
states, 64 neighborhood attempts, and 3,000 states per agent search. BFS heuristic
preprocessing and reservation construction are reported outside the expansion
budget; expansion counts are not equal wall-clock or equal all-operation budgets.
Sequential prioritized replanning may fail despite a feasible group solution.
Every failed attempt retains the incumbent. Accept only a strict Pareto improvement
in SOC/SOL, with neither cost nor the incumbent makespan increasing.

Choose the alternative with smallest sum of development SOL across both seeds;
tie-break by total SOC, then name. Promote it only if the (SOL,SOC) pair is strictly
lexicographically lower than random-four repair. Freeze selection before running
held-out repair. If none qualifies, retain the random baseline and still report
its headroom over incumbent. Held-out data become exposed after this trial.

Every saved solution is independently checked by a standalone pairwise checker:
input identity, obstacles, starts/goals, legal moves, vertex/edge conflicts, both
cost definitions, and individual BFS lower bounds. Negative controls must catch
swaps, teleports, collisions, wrong endpoints, wrong costs and empty paths. Small
joint-state exact searches test the semantics. Duplicate deterministic repair runs
must agree in routes, costs and expansion counts, independent of runtime.

Deliverables: all successes and failures, source/data/solution hashes, candidate
verification, open contribution task cards, local review handoff, a self-contained
playback of real verified paths, and an honest assessment of baseline authority,
remaining headroom and practical utility. No external posting or remote creation.
