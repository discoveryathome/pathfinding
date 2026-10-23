# SOL-aware single-agent repair: literature and correctness note

2026-10-23. Author-assisted research by Codex / gpt-6.1-sol, max reasoning,
default service setting; not independent human signoff. This is a bounded
method proposal and synthetic correctness study, not an accepted result or a
new-algorithm claim. No published case was used for tuning.

## Finding and primary credit

Replacing the single-agent arrival-time objective with lexicographic
`(SOL, final arrival)` addresses a real objective gap. With fixed reservations
and a fixed horizon, the proposed heuristic is consistent and a correctly
relaxing A* returns the earliest final arrival among minimum-SOL feasible paths
when it completes. Budget/deadline interruption gives no such completed result.

- David Silver, [Cooperative Pathfinding, AIIDE 2005](https://ojs.aaai.org/index.php/AIIDE/article/download/18726/18503), pp. 118–120: sequential space-time searches, reservation tables, waiting actions and obstacle-aware spatial heuristics are established. Its WHCA* cost rule already assigns zero to holding at the destination and one to other within-window actions, and permits continued search after visiting the destination. This proposal has especially direct precedent there; its full-horizon terminal condition differs from WHCA*'s window boundary and abstract terminal edge.
- Jiaoyang Li, Zhe Chen, Daniel Harabor, Peter J. Stuckey and Sven Koenig, [Anytime Multi-Agent Path Finding via Large Neighborhood Search, IJCAI 2021](https://www.ijcai.org/proceedings/2021/568), §§2–4; [authors' paper copy](https://pathfinding.ai/pdf/lchsk-ijcai21-amapfvlns.pdf): destroying and repairing agent subsets is MAPF-LNS. The paper uses SOC, vertex/swapping conflicts and permanent holding after path completion; prioritized repair is not globally complete or optimal. A different repair objective does not establish superiority over that work.
- Keisuke Okumura, [Improving LaCAM for Scalable Eventually Optimal Multi-Agent Pathfinding, IJCAI 2023](https://www.ijcai.org/proceedings/2023/0028.pdf), §2: SOL counts transitions other than an agent holding at its own goal. Flowtime/SOC instead uses the time from which the agent permanently remains there; temporary goal visits separate them. The paper explicitly gives spatial shortest-path distances as SOL lower bounds.
- Okumura, [Engineering LaCAM*: Towards Real-Time, Large-Scale, and Near-Optimal Multi-Agent Pathfinding, AAMAS 2024](https://ifaamas.csc.liv.ac.uk/Proceedings/aamas2024/pdfs/p1501.pdf), §§2, 6–7: LaCAM3's refinement work and SOL objective are prior art. Credit its implementation and retain the repository's [third-party notices](../../THIRD-PARTY.md), including Moving AI attribution if benchmark data are later used.

## Local scope and source limitation

Observed checkout HEAD was `53f33999362d55b06ba49afa9ac6245d69955b4d`.
The supplied `ee542d9b4c91949140f009a90142f5ba` is the donation's randomness seed,
not a Git revision. The parent confirmed the source identities below also match
canonical base `37823dca1bea271510e3ed62205620466ec6f0f9`. The original note's
attempt to resolve the seed as a revision was a source-study interpretation error;
it does not limit the hash-bound observations or executable controls. Native and
context-tool reads agreed on the following SHA-256 identities:

```text
src/repair.py        a1cbf0769f05bedbd386197df6eb1351bb753f5954c31c7494ee2a397ac55b91
src/model.py         8f536e512b8f5a080f6b0d1d249b4b7dfa837fedf851bc541d8dabb22341eed9
src/repair_round2.py  05f2af815e7cab634532ba1fd74fa12fc352378dea19efaa22c79fbeacfe9ff2
```

[repair.py](../../src/repair.py), lines 7–38, reserves outsiders through `T`,
including final holding and reverse-edge conflicts. Its queue minimizes
`t + dist[v]`, ties by `-t`, and marks `(v,t)` seen on discovery. This is an
arrival-time search: every history reaching a given `(v,t)` has the same elapsed
time, so that use of `seen` does not itself invalidate arrival optimality.
It provides no SOL tie guarantee.

[model.py](../../src/model.py), lines 25–37, gives own-goal holds zero SOL and
counts all other transitions, including waits elsewhere and goal departures.
SOC is final arrival after trimming trailing holds. The macro in `repair.py`,
lines 57–77, uses the current makespan as `T`, sequentially adds repaired paths
to reservations, and accepts only nonregression in SOL, SOC and makespan with
strict SOL or SOC improvement. [repair_round2.py](../../src/repair_round2.py),
lines 10–60, already has two-agent SOL search, best labels and stale checks;
the present proposal concerns the single-agent objective and arrival tie-break.

## Search claim and proof

Fix the outsiders and any already replanned agents for this invocation. Legal
states are `(v,t)` at absolute integer times `t0 <= t <= T`. A transition to
`(u,t+1)` must be a graph move or wait, avoid occupied vertices, and avoid an
outsider's reverse edge at that timestep. Define its vector cost as

```text
c(v,u) = (ell(v,u), 1)
ell(v,u) = 0 iff v = u = own_goal; otherwise 1.
d(v) = exact static graph distance from v to own_goal.
h(v,t) = (d(v), d(v)).
queue's first two keys = (gSOL + d(v), t + d(v)).
```

Earlier goal visits and subsequent departures remain legal. Let `b` be the last
reserved time at the goal over the entire global interval through `T`, or `-1`
if none. A terminal is `v == goal` and `t > b`. This verifies the held suffix,
not merely current goal occupancy. With the repository's `at` extension,
outsiders hold their final vertices after `T`, so this suffix remains safe
after `T` too. A goal reserved at `T` yields no terminal through `T`.

**Admissibility and consistency.** Any completion from `v` needs at least `d(v)`
charged transitions and at least `d(v)` timesteps; reservations can only remove
options. For a unit-charge move or wait, `d(v) <= 1 + d(u)`, so both components
of `h(v,t) <= c(v,u) + h(u,t+1)` hold componentwise. For a zero-charge goal hold,
the comparison is `(0,0) <= (0,1)`. Thus the heuristic is lexicographically
consistent, including zero-SOL holds. Future goal blocks can make it weak at
the goal but cannot make it overestimate. Pruning `t+d(v)>T` is safe.

**Labels and termination.** Retain minimum `gSOL` for each `(v,t)`, enqueue
strict improvements, and reject stale queue entries before testing the terminal.
Different histories at equal space and time can have different SOL. Their future
legal options are identical, so the lower-SOL history dominates; the time
component is already fixed by `t`. Permit relaxation/reopening instead of a
discovery-only `seen` rule. With this consistent heuristic, a correctly settled
nonstale state never actually needs reopening after settlement; improvement of
an enqueued state is nevertheless essential to the general relaxation rule.

Suppose the first nonstale popped terminal had a worse pair than some feasible
terminal path. A frontier prefix of that better path has `f` no larger than its
completion pair, by admissibility; dominance cannot eliminate its better
continuation. It therefore must precede the purported returned terminal, whose
heuristic is zero. Contradiction. Hence the result minimizes SOL and, among
those paths, final arrival. Preserve those two queue keys before any tertiary
tie-break; a `-t` tie-break ahead of estimated final arrival does not prove the
secondary claim. Absolute `t` adds the same `t0` offset to every elapsed-time
cost, so it does not change ordering. Holding has vector cost `(0,1)`, and the
finite time horizon prevents an infinite zero-SOL waiting sequence.

This proves only one invocation's optimum under its fixed reservations. A greedy
choice can block a later agent, so it proves neither neighborhood feasibility
nor a globally optimal MAPF plan. Count **every heap pop** toward the cap,
including stale, terminal and horizon entries. A cap or external deadline that
interrupts before a proved terminal returns no candidate, not infeasibility or
an optimal partial result. Check deadlines independently of stale-entry handling.
Only complete exhaustion without interruption proves failure in the bounded
reservation graph.

## A six-vertex counterexample

Use the obstacle-free 2-by-3 grid with row-major labels, orthogonal moves and
waits. Match the repository's adjacency order: up, down, left, right, then wait.
Replan start `1`, goal `2`, with global horizon `T=7`. A single outsider follows
the fixed row below and holds `1` forever afterwards; its start is `4`, goal `1`.

```text
grid:       0 1 2
            3 4 5

time        0 1 2 3 4 5 6 7
outsider    4 5 5 4 5 2 2 1
old A*      1 2 2 1 4 5 5 2    SOL=6, final arrival=7
better      1 2 2 2 1 4 5 2    SOL=5, final arrival=7
```

Both routes obey vertices, moves and edge-swap restrictions. The goal is blocked
at times 5 and 6, so no terminal precedes 7. The old route has one zero-charge
hold, the better route two. At state `(5,6)`, their prefix costs are respectively
5 and 4; equal space-time does not imply equal SOL. Thus the issue exists even
when the optimal arrivals agree; it is not dependent on permitting SOC regression.

An in-memory execution of the inspected old A* returned the stated route in
24 pops. Separately, exhaustive legal-walk enumeration through `T=7` found 70
terminal walks, with minimum pair `(5,7)`; it visited 83 distinct `(v,t,SOL)`
labels and found costs `{4,5,6}` at `(5,6)`. Explicit move, vertex and swap
assertions passed for both displayed routes. This is an author-run synthetic
control, not independent verification or a repository candidate certificate.

**When no objective gap follows.** For any path with no own-goal holds before
final arrival, `SOL = final_arrival - t0`. In an absorbing-first-arrival model,
earliest arrival therefore minimizes SOL. Also, if every reachable first goal
visit is already safe to terminate, truncate any path there: its prefix costs
one per step and no continuation can improve it. A goal with no future
reservation is an important sufficient case. The counterexample instead
requires useful early visits that cannot yet terminate.

## Macro acceptance and the optional arrival cap

SOL-primary search can prefer a later final arrival. Keeping the same `T`
protects makespan but not SOC; the unchanged Pareto gate can reject such a
proposal. Earliest arrival *among equal-SOL optima* does not resolve a strict
SOL/arrival tradeoff, and sequential reservations can change subsequent agents'
choices as well. Log proposed metrics and rejection reasons, not only accepted
improvements.

If SOC regressions dominate, a separately declared pivot is to restrict each
replanned agent to `arrival <= its pre-attempt incumbent arrival`. This
guarantees aggregate SOC nonregression for completed neighborhoods, but forbids
useful compensating delays across agents and can reduce feasibility. It changes
the method's feasible set, not the global SOL/SOC/makespan acceptance rule.
Continue to compute goal blocks and suffix reservations through the **global**
`T`; do not truncate outsiders at the per-agent cap. Apply the smaller deadline
only to that agent's expansion/arrival bound. The macro gate remains necessary
for SOL and strict improvement. Compare the capped pivot as a separate attempt;
do not silently select it after inspecting evaluation outcomes.

## Suggested development and evaluation contract

Before implementation tuning, the parent should save the source/baseline hashes,
inputs, seeds, budgets, selection rule and stopping rule required by
[EVALUATION.md](../../EVALUATION.md), pin the intended base commit, and record the
separate seeded picker/experiment-seed mapping.

1. Use an exact time-layer DP oracle on tiny synthetic graphs: retain minimum
   SOL per `(v,t)`, relax all legal transitions, then minimize `(SOL,t)` over safe
   terminals. Add full-walk enumeration on a few tiny cases to check the oracle.
   Compare optimum pairs and independently recompute reconstructed path metrics.
2. Include the witness above, early-goal departure, zero-cost holds, start equal
   to goal, future goal blocking, outsider final holding, reverse-edge rejection,
   disconnected/blocked starts, a terminal exactly at `T`, shifted absolute
   times, and multiple-SOL histories at one `(v,t)`. Cover equal minimum SOL with
   distinct terminal times to test the secondary ordering.
3. Negative controls: charge goal holds one and recover the arrival objective;
   make first arrival absorbing and lose the displayed witness; deliberately
   discard improved labels and ensure an appropriate duplicate-history case
   detects it. Exercise stale pops, zero/last-pop caps and an injected deadline:
   interrupted runs must return no candidate and must not be called infeasible.
4. Freeze the uncapped-by-old-arrival method after these controls. A bounded
   development rule could allow one fixed diagnostic batch and at most one
   predeclared cap pivot, triggered only if more than half of completed proposals
   rejected by the gate strictly lower SOL while worsening SOC. Fix the batch,
   denominator, seeds and budgets beforehand; retain all failures and null results.
   Stop after those attempts or the allotted development deadline, whichever
   comes first. Insufficient completed proposals is not evidence for a pivot.
5. Use the strongest applicable current Pareto incumbents and the existing
   arrival-time repair with matched neighborhoods, orders and initial plans.
   Fixing popped-state budgets is a useful work-count experiment, **not equal
   CPU**: heap entries, stale pops, relaxations and memory differ. Report failed
   replans, accepted/rejected proposals, SOL/SOC/makespan, preprocessing, wall/CPU
   time and memory. Add paired repeated timings and A/A controls before any speed
   claim. Separate solver-core effects from end-to-end neighborhood trajectories.
6. Freeze before opening evaluation outputs; disclose all exposed inputs.
   Published cases remain calibration/replication, and fresh seeds on them do
   not establish new-distribution transfer. Reviewer-chosen fresh inputs after
   freeze and human scientific signoff remain distinct from this author's work.

## Controls performed and remaining limits

The exploratory control was bounded in advance to 200 synthetic draws on this
same six-vertex grid, `T=8`, Python RNG seed `20261023`. Each draw sampled distinct
`start, goal, outsider_start` using `random.sample(range(6),3)` and generated eight
outsider steps with `random.choice(adjacency + wait)` in the order stated above.
It skipped 29 draws whose outsider ended at the replanned goal. All 171 remaining
draws were feasible by exact time-layer DP; old A* agreed on earliest terminal
arrival in all 171. Four draws exposed a SOL gap, including a same-arrival gap
in each. These are selected development observations, not a success-rate estimate.
The first gap was draw index 1. The displayed `T=7` control then dropped its last
outsider step and declared final holding at `1`; it is a new standalone witness,
not a claim of minimality. The old-search cap was 10,000 pops per invocation;
no cap was reached. No assertion failure occurred in these controls.

No proposed solver implementation, benchmark run, repository test-suite run or
performance measurement was made. Control programs ran only in memory; this
note is their retained description, so the parent should promote the fixed
witness and oracle checks into reproducible tests before implementation claims.
The context fetch tool failed with `Cannot find module 'turndown'`; official
publisher pages/PDFs and the authors' paper copy were read with the web tool
instead. The donation seed is not a source revision; the hashes above pin the
inspected canonical baseline, and experiment seeds are recorded separately.
Existing records, witnesses, manifests and other session work were left alone.
