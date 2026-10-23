# Pair constraints, assignment and rounded dual witnesses

This applies established weighted-dependency and assignment/LP reasoning; primary
sources and limitations are in LITERATURE.md. The SOL pair relaxation and its
capped-search argument are reused from the pinned source snapshots in SOURCES.md.

For each agent let `d_i` be its individual grid distance and let
`e_i = loss_i - d_i`. Every valid global route has integer `e_i >= 0`. A certified
two-agent lower bound `L_ij` implies `e_i + e_j >= w_ij`, where
`w_ij = max(0, L_ij-d_i-d_j)`. Other agents are deleted only for this relaxation;
goal departures and zero-cost own-goal holds remain available. Thus the pair costs
are SOL costs, not SOC optima. Pair-weight validity is checked separately from
the aggregation below.

## Feasible rational dual

For nonnegative integer edge numerators `z_ij` with incident sums at most 2,
multiply every excess constraint by `z_ij/2` and sum. The result is

```
sum_ij w_ij*z_ij/2 <= sum_i e_i * (sum_j z_ij)/2 <= sum_i e_i.
```

The ceiling is valid because the right-hand side is an integer. If the witness's
positive edges partition into disjoint sets of agents, the same proof applies
to each set separately, so its ceilings may be summed. This does not permit
adding overlapping rounded certificates.

## Obtaining the witness by assignment

Complete a symmetric matrix `W` with the edge weights and zero diagonal/nonedges.
For any permutation `P`, set `z_ij=[P(i)=j]+[P(j)=i]` on positive edges. An agent
has at most one outgoing and one incoming selected arc, so its incident numerator
is at most 2. Fixed points and zero arcs are permitted dummy assignments; they
contribute no bound. The numerator objective is exactly the assignment weight.
A complete feasible permutation already supplies a valid lower-bound witness;
an unfinished partial assignment or arbitrary dual potentials do not.

Let `F` be the maximum fractional-matching objective with vertex capacities one.
Any feasible undirected fractional matching `y` maps to a doubly stochastic matrix
whose off-diagonal entries are `y_ij` and whose diagonal is `1-sum_j y_ij`.
Its assignment objective is twice that of `y`. Birkhoff/von Neumann integrality
therefore gives maximum assignment weight at least `2F`. Conversely permutation
extraction above gives a feasible fractional matching of half its weight, so no
assignment exceeds `2F`. Equality follows. This is the degree-only fractional
relaxation, not integer edge-weighted vertex cover or full MAPF optimality.

## Integer primal/dual check

For each positive-graph component of size `k`, put `M=max(W)` and
`c_ij=M-W_ij`, including every diagonal and zero entry. The Hungarian routine returns
a permutation and integer potentials satisfying `u_i+v_j <= c_ij` everywhere.
The separate checker recomputes the selected cost and requires
`sum(u)+sum(v)=sum_i c_i,P(i)`. Weak duality then proves assignment optimality.
The resulting numerator is `k*M-selected_cost`. No floating-point tolerance is
used; Python integers also support the large-weight test.

The checker independently reconstructs all numerator edges, capacities, positive
support groups, graph-component and support-group ceiling sums. It rejects wrong
permutations, bad potentials, aliased IDs, overfilled/mismatched edge witnesses,
incorrect group coverage and inflated objectives. Pair bounds still require their
separate raw-grid threshold proof.

## Rounding and alternatives

Each positive-edge graph component has a disjoint agent budget. The selected
permutation's positive witness support can split that component further; rounding
those support groups separately is also valid and at least as strong for that
witness. The amendment adding this comparison was recorded before the pilot.

Component rounding is not generally monotone when edges are added: two separate
unit triangles give 4, but a bridge merges them and the graph-component ceiling
can give 3. Selected optimal permutations can also have different support rounding.
No exact integer-cover optimizer or globally best rounding policy is claimed.
Earlier checked partitions/witnesses remain valid after adding constraints. This
experiment therefore retains the prior complete fixed-matching certificate and
takes the maximum of complete valid alternatives, never their overlapping sum.

## Charged favorable case and checks

The inherited valid route supplies integer excess values. Any valid capacity
witness over the graph's covered vertices is bounded above by their total
inherited excess. Before the original-maze pilot, that ceiling was 1769 above the
5926 individual-distance bound: hypothetical total 7695, versus predecessor bound
6041. This priced favorable case does not rule out useful strengthening; it is not
an attained result or a guaranteed gain.

Exhaustive four-vertex matrices with weights 0–2 compare assignment to all
permutations and rounded bounds to exact integer cover. Controls include odd
cycles, component merging, K4's fractional/integer gap, heavy-edge fixed points,
large integers and malformed certificates. The declared scope is all 2785 existing
32-step forced-conflict pairs on 20 published cases, including the earlier 521
disjoint pairs. All work is author-checked and does not change accepted records.
