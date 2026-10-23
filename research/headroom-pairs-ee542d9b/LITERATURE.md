# Pairwise headroom bounds for this repository's SOL objective

Date: 2026-10-23. Track: headroom. Seed: `ee542d9b4c91949140f009a90142f5ba`.
Research provenance: author-assisted research by gpt-6.1-sol; this is not independent human scientific signoff.
Local source snapshot inspected: `9f29e7f0ca81c02d48ba0633060d5a5af865f70b`.

## Answer and recommended scope

The proposed **SOL-cost, synchronous two-agent position-product search is valid** without an explicit time coordinate. Exact pair costs, or correctly obtained capped A* lower bounds on those costs, can replace the current unit pair penalties. A matching of such weighted penalties gives an additive lower bound on global SOL and therefore on global SOC. Overlapping pair constraints can also be aggregated safely using a checked fractional-matching witness or an exactly solved edge-weighted minimum vertex cover.

The important qualification is the objective: an optimal **SOC** pair cost need not lower-bound **SOL**. The six-cell example below has pair optima SOC = 8 and SOL = 7. Keep goal departures available and use the repository's endpoint-based transition cost throughout. Start with standard-library A* and deterministic greedy weighted matching; fractional witnesses are an optional strengthening that needs no optimization dependency.

## Primary-source lineage

1. **Cardinal conflicts and disjoint matching.** Felner et al., *Adding Heuristics to Conflict-Based Search for Multi-Agent Path Finding*, ICAPS 2018, pp. 83–87, §§3.1–3.2, develop admissible bounds from disjoint cardinal conflicts, greedy/maximum matching, and minimum vertex cover. Counting every overlapping conflict is unsafe. [Publisher paper](https://ojs.aaai.org/index.php/ICAPS/article/download/13883/13732), [DOI and metadata](https://doi.org/10.1609/icaps.v28i1.13883).

2. **Dependency and weighted-dependency graphs.** Li, Felner, Boyarski, Ma, and Koenig, *Improved Heuristics for Multi-Agent Path Finding with Conflict-Based Search*, IJCAI 2019, pp. 442–449, §§4–5, define dependency by incompatibility of all individually optimal paths. WDG weights are optimal pair excess costs, ignoring other agents. Their EWMVC assigns nonnegative integers to vertices, minimizes their sum, and requires the two endpoint assignments to cover every edge weight. The paper's §2.1 makes only terminal goal waits free. [Publisher record](https://www.ijcai.org/proceedings/2019/63), [paper, especially pp. 442 and 444–445](https://www.ijcai.org/Proceedings/2019/0063.pdf), [author publication/code entry](https://jiaoyangli.me/publications/LiIJCAI19/).

3. **Bounded pair searches already have a precedent.** In the authors' CBSH2-RTC implementation, `solve2Agents` uses `min_f_val - root_g` on a time/node cutoff, and the exact pair solution excess on success. Larger graph components can use greedy matching instead of exact cover optimization. This is precedent for lower-bound weights from unfinished search, under that implementation's SOC semantics. It does not establish the SOL adaptation by itself. [Pinned source, `solve2Agents`, lines 222–276](https://github.com/Jiaoyang-Li/CBSH2-RTC/blob/a834df1e16c1668a677b68fef6699371c4233d33/src/CBSHeuristic.cpp#L222), [component aggregation, lines 513–607](https://github.com/Jiaoyang-Li/CBSH2-RTC/blob/a834df1e16c1668a677b68fef6699371c4233d33/src/CBSHeuristic.cpp#L513). The inspected file matches that pinned revision.

4. **The exact SOL objective and configuration graph are established.** Okumura, *Improving LaCAM for Scalable Eventually Optimal Multi-Agent Pathfinding*, IJCAI 2023, pp. 243–251, §2.1, defines SOL by charging agents unless both transition endpoints equal their own goals. It explicitly distinguishes history-dependent flowtime/SOC, permits the configuration-graph shortest-path formulation for accumulated transition costs, and gives the sum of individual graph distances as an admissible SOL heuristic. It credits earlier work by Standley and Wagner/Choset for this cost setting. [Author-submitted paper, §2.1](https://arxiv.org/html/2305.03632), [publisher record](https://www.ijcai.org/proceedings/2023/28).

5. **Goal behavior and objective conventions must be specified.** Stern et al., *Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks*, SoCS 2019, §§2.1–2.3, distinguish collision rules, terminal staying versus disappearance, and the usual SOC convention that charges goal waits preceding a later departure. [Primary paper](https://arxiv.org/pdf/1906.08291), [author-institution record](https://publications.ri.cmu.edu/multi-agent-pathfinding-definitions-variants-and-benchmarks).

The project-specific arguments below are derived here from the inspected model. They apply known pairwise relaxation and aggregation ideas to this SOL setting; this note makes no novelty or performance claim. The IJCAI-2019 PDF was available through indexed primary-source passages, but direct PDF opens failed; the bounded-search implementation claim was checked directly against the pinned author repository. No claim depends on a secondary tutorial.

## Repository semantics checked

[`src/model.py`](../../src/model.py), functions `path_loss`, `metrics`, and `at`, and the separate [`src/verify.py`](../../src/verify.py), function `check`, agree on the relevant model:

- A move is to a four-neighbor free cell; a wait is legal. Vertex collisions and opposite-direction edge swaps are forbidden. Moving into a cell just vacated by the other agent is allowed when this is not a swap.
- Starts are pairwise distinct, and goals are pairwise distinct. The verifier does not require all starts and goals to be mutually disjoint, nor does it prohibit an agent starting at its own goal.
- Each finite path ends at its own goal and is extended by holding that final cell. Earlier goal visits can be followed by departures.
- For agent `i`, transition cost is `c_i(u,v) = 0` if `u = v = g_i`, and `1` otherwise. SOL is the sum of these costs. SOC is the sum of final settling times.

Consequently, for every feasible solution, `SOL <= SOC`: before final settling, each transition costs at most one; subsequent goal holds cost zero. More precisely, `SOC - SOL` counts goal-to-same-goal transitions before the respective agents' final settling times. Thus a lower bound on SOL is also a lower bound on SOC, but the converse implication does not follow.

## Exact pair graph and projection proof

For selected agents `i,j`, let a state be their **ordered** current positions `q = (u_i,u_j)`, with `u_i != u_j`. Generate every simultaneous combination of an individual wait or legal grid move. A successor `r = (v_i,v_j)` is legal precisely when its positions differ and it is not the swap `v_i = u_j, v_j = u_i`. Give the edge cost

```text
c(q,r) = [not (u_i = v_i = g_i)] + [not (u_j = v_j = g_j)].
```

The start is `(s_i,s_j)` and the terminal state is `(g_i,g_j)`. Denote its optimal cost by `C_ij`, and let `d_i = dist(s_i,g_i)` be the individual BFS distance.

**Why positions suffice.** Both legal transitions and their SOL costs depend only on these positions, fixed goals, and the static grid. No other agent or time-indexed constraint remains. A more expensive arrival at the same pair state cannot improve the best achievable total cost, regardless of its absolute arrival time. This is exactly the Markov property needed for shortest-path duplicate detection. It would fail for a pair replanning problem with time-dependent reservations, CBS time constraints, deadlines, or other moving agents retained.

**Why `C_ij >= d_i + d_j`.** Every projected individual path contains at least its BFS distance in move transitions; all those transitions cost one. Waiting can only add a nonnegative cost. The individual unconstrained optimum is exactly `d_i`.

**Why a pair cost bounds a global solution.** Take any valid global solution, extend all paths with their final goal holds to a common horizon, and retain only `i,j`. This is a legal pair walk ending at `(g_i,g_j)` with cost exactly the two agents' global losses. Other agents' removal relaxes constraints. Therefore `loss_i + loss_j >= C_ij`. Reaching both pair goals early is sufficient: distinct final goals admit a legal zero-cost infinite holding extension in the pair relaxation, even if these agents later move again in the original global solution.

For any collection `M` of disjoint pairs and any certified `L_ij <= C_ij`, sum those inequalities and the unmatched individual distance inequalities:

```text
global SOL >= sum((i,j) in M) L_ij + sum(i unmatched) d_i
           = B0 + sum((i,j) in M) w_ij,
B0 = sum(i) d_i,
w_ij = max(0, L_ij - d_i - d_j).
```

For exact pair searches, use `L_ij = C_ij`. For unfinished searches, `L_ij` is a lower bound, not an exact pair cost. The bound need not be attainable: interactions involving three or more agents have been omitted.

## A concrete counterexample to importing SOC pair weights

Use the induced grid with horizontal free cells `(0,0)` through `(4,0)` and just one additional free cell `(3,1)`; everything else is blocked. Let A start at `(3,1)` with goal `(3,0)`, and B start at `(0,0)` with goal `(4,0)`. All four endpoints are distinct. Write `U=(3,1)` and `C=(3,0)`.

A feasible synchronized plan at times 0 through 4 is:

```text
A: U, C, C, U, C
B: (0,0), (1,0), (2,0), C, (4,0)
```

The A wait `C -> C` is free for SOL, even though A later departs. A's loss is 3 and B's is 4, so SOL is 7. Both finally settle at time 4, so SOC is 8. Every solution has B settling no earlier than time 4, and A finally entering C no earlier than time 4 because B must pass through C at time at least 3. Hence optimal SOC is 8. For SOL, if A ever leaves C, its travel from U to C and back via a departure requires at least 3 charged moves, so pair SOL is at least 7. If A never leaves C, it cannot enter until time at least 4, and that solution costs at least 8. Thus optimal SOL is exactly 7.

Using the SOC pair optimum as an SOL bound would incorrectly return 8. Making each goal absorbing at its first visit also excludes the cost-7 plan and returns 8 here. This counterexample and its proof are derived here; the cost distinction itself is documented by Okumura and Stern et al. above.

A bounded, in-memory control reproduced these numbers with exhaustive Dijkstra: the SOL position graph popped 16 states; an SOC graph augmented by irrevocable final-settlement flags popped 23 states. This was a six-cell sanity check, not a benchmark or a new saved experiment artifact.

## Capped A*: what is actually certified

Use the heuristic `h(u_i,u_j) = dist(u_i,g_i) + dist(u_j,g_j)`. It is admissible and **consistent** for the edge cost above. For an individual move or off-goal wait, the BFS triangle inequality gives `dist(u,g) <= 1 + dist(v,g)`; for a free own-goal hold both distances are zero. Summing gives `h(q) <= c(q,r) + h(r)`. This consistency proof is derived here; Okumura §2.1 supplies the underlying admissible distance heuristic.

Maintain ordinary graph A*: a best-known `g` per state, heap entries keyed by `f=g+h`, strict `g` improvements, and stale-entry removal. At a boundary **after a complete expansion and before the next valid pop**, if the goal has not been popped, let

```text
L_ij = min(q in valid OPEN) (g(q) + h(q)).
```

Then `L_ij <= C_ij`. Proof: on an optimal path there is a first state not yet expanded; its predecessor was expanded with optimal `g` by consistency, so this frontier state has an optimal-prefix `g` and `f <= C_ij`. An optimal goal pop establishes equality with that goal's `g`. At zero expansions, the initial heap gives the baseline `d_i+d_j`. The proof assumes no unaccounted pruning or lost frontier entries.

Cutoff details that affect validity:

- **Stop at complete-expansion boundaries.** If a cap or timer interrupts successor generation after popping a state, the remaining heap can omit the optimal continuation and its minimum can exceed the optimum, or be empty. Finish that expansion, retain the in-flight work in the frontier, or return the valid popped `f` saved before starting it. With this consistent A*, that popped value is itself a safe, possibly weaker bound. Apply the same rule to memory caps: dropping states silently invalidates the OPEN argument.
- **A found solution is an upper bound until certified.** A generated goal's path cost is not automatically a lower bound. Stop on a valid minimum-`f` goal pop for exactness. If incumbent pruning removes nodes with `f >= U` for a feasible pair incumbent `U`, report `min(U, min OPEN f)` with an appropriate empty-OPEN convention; do not report an OPEN minimum that has risen above the optimum after the optimum was already found.
- **A cap is not infeasibility.** Only a fully exhausted, untruncated graph search without a goal proves pair infeasibility. An infeasible pair implies global infeasibility by projection. A known valid global incumbent is therefore a useful diagnostic against an erroneous pair-infeasibility report.
- **Do not restrict the feasible graph without a relaxation proof.** A time horizon, bounding box, first-arrival goal lock, or extra collision prohibition can raise the computed optimum above the true pair optimum. A node budget that preserves the frontier does not have that problem.
- **Exactness and certification are separate.** A matching or dual witness checks aggregation; it does not independently prove its edge weights. Preserve map/instance hashes, objective/version, deterministic pair selection, cap definition, expansions, and the exact lower-bound termination rule so a separate checker can replay the bounded search. A feasible pair path alone certifies an upper bound.

There are at most `|V|(|V|-1)` ordered position states and at most 25 successor combinations per state on this grid. This is a worst-case bound, not a claim that pair searches will be cheap on every map. Report preprocessing, actual time, expanded/generated states, and caps separately.

## Stopping, waits, and zero-cost cycles

**Asynchronous completion:** one agent may hold at its goal at zero individual cost while the other continues. Keep its position in every synchronous pair state and keep checking vertex/swap conflicts. Before the pair jointly terminates, this agent must still be allowed to depart. Removing it on its first goal visit is a weaker disappearance relaxation, not the exact pair problem; freezing it on first arrival is a restriction and can give an invalidly high SOL bound, as above. Stopping when both have visited their goals at different past times also does not establish a valid pair solution.

**Simultaneous wait self-loops:** transitions with `r=q` can all be removed from this unconstrained static pair graph. They return to exactly the same state and cost 0, 1, or 2, so deleting them preserves optimal SOL. Do not remove individual wait choices when the other agent moves: those transitions change the joint state and can be necessary. The self-loop deletion argument does not carry over to time-dependent reservations, where the passage of time changes future feasibility.

**Zero cost:** an individual own-goal hold is free, but a whole pair edge has cost zero only when both agents hold at their own goals. Thus the only zero-cost edge is the terminal self-loop; after removing simultaneous waits, every remaining edge costs at least one. There are no nontrivial zero-cost cycles in this particular model. Check an initially terminal pair before expanding it; strict duplicate improvements also prevent reinserting an equal-cost self-loop.

**Terminal holding:** final goals are distinct, so both can remain forever after reaching the joint terminal. An individual path ending earlier must still be padded with goal occupancy, not treated as absent. Pair termination is sound because all other agents have been removed from the relaxation.

## Overlapping weights: safe witnesses without a solver dependency

For every global solution define the nonnegative integer excess `e_i = loss_i - d_i`. Each computed pair bound implies

```text
e_i + e_j >= w_ij.
```

The following aggregation proof is elementary algebra derived here, and is the SOL counterpart of WDG's excess-cost constraints.

**Matching.** Any matching provides a lower bound `sum w_ij` on total excess. A deterministic greedy choice in decreasing weight order needs no dependency. A maximal matching need not be maximum weight. For repeated bounds on the same pair, use their maximum, not their sum.

**Fractional matching / LP dual witness.** Supply rational numbers `y_ij >= 0` with `sum(j) y_ij <= 1` at every agent. Multiply each pair inequality by its `y`, sum, and use `e_i >= 0`:

```text
sum(ij) w_ij*y_ij
 <= sum(i) e_i * sum(j) y_ij
 <= sum(i) e_i.
```

Therefore `B0 + ceil(sum w_ij*y_ij)` is a valid integer SOL bound. No LP solver is necessary to verify this witness. Store a positive common denominator `Q` and nonnegative integer numerators `z_ij`; check `sum(j) z_ij <= Q` for each agent, and compute the ceiling using integer arithmetic. Check the pair IDs and certified weights as well. Use no floating-point feasibility tolerance.

An ordinary matching is `Q=1`. A simple stronger construction uses `Q=2`: disjoint matched edges get numerator 2, and disjoint odd cycles may give each cycle edge numerator 1. A triangle with three unit weights certifies `ceil(3/2)=2`, whereas a matching certifies 1. These cycles and edges must not overfill a vertex's capacity. On components with disjoint agent sets, round each component's bound upward separately and sum; otherwise round only a single combined feasible witness. Alternative overlapping witnesses can be compared by maximum, but cannot be freely added.

**Integer EWMVC.** Exactly minimizing `sum x_i` over nonnegative integers subject to `x_i+x_j >= w_ij` can be stronger. It is already the WDG formulation, rather than a new aggregation idea. A feasible cover assignment, or the best cover found when a minimization times out, is an **upper bound on the cover optimum**, not a certified lower bound on global excess. Use an exact optimum, a proven branch-and-bound lower bound, or the feasible dual witness above. The fractional certificate need not attain the integer cover optimum; e.g. the unit-weight complete graph on four vertices has fractional value 2 and integer cover value 3.

## Relation to the existing 32-step bound and practical recommendation

[`tools/headroom.py`](../../tools/headroom.py) currently detects unavoidable conflicts using singleton shortest-path layers, pads reached goals, and adds one for each greedily selected disjoint pair. Its SOL validity follows directly: an individual path with loss exactly `d_i` has no off-goal waits or detours and must first reach its goal at time `d_i`, then hold there forever. A forced conflict of two such padded shortest paths therefore rules out pair loss `d_i+d_j`; integrality supplies at least one extra loss unit. Looking only through time 32 can miss conflicts but cannot manufacture an extra unit. This is a sufficient dependency test, rather than the full joint-MDD dependency test in the literature.

For a bounded contribution:

1. Keep BFS baseline distances and the existing forced-conflict witnesses. Upgrade selected pairs using SOL-cost A* on the full static product graph, with fixed, reported caps and complete-expansion stopping.
2. For a pair already certified to have unit excess, use the maximum of that unit witness and any new A* excess. An unfinished search returning the baseline does not refute a known dependency; an exact baseline-cost pair path does establish independence for that pair relaxation.
3. Aggregate with deterministic weighted greedy matching. Preserve at least the previous total bound by comparing complete valid aggregation witnesses. Optionally compare a checked denominator-2 cycle/matching witness; do not add overlapping witnesses.
4. Validate the cost-7/SOC-8 control above, an initial-goal case, a necessary individual wait, a forbidden swap, terminal goal blocking, and a cap firing before/after an expansion. Check bounded pair values against exhaustive Dijkstra on tiny grids and against the corresponding projected costs of valid global incumbents.
5. Label exact pair optima, capped pair lower bounds, and aggregate lower bounds separately. State that residual headroom is a gap to a relaxation, not a promise of attainable improvement. No archive change or scientific acceptance follows from this note.

This answers the mathematical applicability question. It does not establish runtime benefit, a new algorithmic contribution, or independent scientific validation.
