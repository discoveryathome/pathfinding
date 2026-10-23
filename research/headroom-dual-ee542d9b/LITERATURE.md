# Certifying overlapping SOL pair bounds with assignment

Date: 2026-10-23. Track: headroom. Seed: `ee542d9b4c91949140f009a90142f5ba`.
Provenance: author-assisted research by gpt-6.1-sol, max reasoning; not independent human review. This note extends the preceding contribution's `research/headroom-pairs-ee542d9b/LITERATURE.md` (on its own contribution branch), assumes its SOL projection argument, and makes no algorithmic novelty or performance claim.

## Answer

The proposed reduction is correct: maximum-weight assignment on the completed bipartite double cover has value **twice the maximum fractional-matching value**. Every permutation supplies an exact denominator-2 lower-bound witness, even without an optimality certificate. Integer Hungarian potentials can additionally certify that the assignment is optimal. Rounding independently over disjoint agent components is valid and can strengthen one global ceiling.

One additional implementation caveat matters: **rounding over the current positive-edge components is not monotone under adding edges**. Two disjoint unit triangles give 4; adding one unit bridge joins their components and the same policy gives 3. Retain earlier checked bounds/partitions and take their maximum. The fractional optimum itself remains monotone.

## Primary sources and what they establish

1. **Birkhoff / von Neumann.** Garrett Birkhoff, *Tres observaciones sobre el álgebra lineal*, Universidad Nacional de Tucumán, Revista A **5** (1946), 147–151, is identified in [Kuhn's original bibliography, reference 6](https://onlinelibrary.wiley.com/doi/10.1002/nav.3800020109). John von Neumann, *A Certain Zero-sum Two-person Game Equivalent to the Optimal Assignment Problem*, in *Contributions to the Theory of Games II*, Annals of Mathematics Studies **28** (1953), 5–12, defines the doubly stochastic and permutation matrices on p. 7 and proves their convex-hull equality in **Lemma 2, pp. 8–9**, explicitly crediting Birkhoff. [Primary chapter scan](https://api.pageplace.de/preview/DT0400.9781400881970_A27168456/preview-9781400881970_A27168456.pdf#page=16), [chapter DOI](https://doi.org/10.1515/9781400881970-002). The proof was checked in von Neumann's scan; Birkhoff's original scan was not inspected.

2. **Assignment primal/dual certificates.** Harold W. Kuhn, *The Hungarian Method for the Assignment Problem*, Naval Research Logistics Quarterly **2** (1955), 83–97, especially **p. 90**, states the maximum-score assignment dual `a_i+b_j >= r_ij` and explains that a complete assignment on equality entries is optimal. [Original paper scan](https://web.eecs.umich.edu/~pettie/matching/Kuhn-hungarian-assignment.pdf), [publisher DOI](https://doi.org/10.1002/nav.3800020109).

3. **Cost conversion and integer assignment.** James Munkres, *Algorithms for the Assignment and Transportation Problems*, Journal of the Society for Industrial and Applied Mathematics **5** (1957), 32–38, **§1, p. 32**, explicitly converts maximum ratings into minimum costs using `c_ij = max(r)-r_ij`, initially for integer entries. [Original paper scan](https://www.math.ucdavis.edu/~saito/data/emd/munkres.pdf), [publisher record](https://doi.org/10.1137/0105003). The modern dense cubic implementation should not be attributed verbatim to this original algorithm.

4. **Fractional versus integral matching.** Jack Edmonds, *Maximum Matching and a Polyhedron With 0,1-Vertices*, Journal of Research of the National Bureau of Standards B **69B** (1965), 125–130, **§2, p. 126, inequalities (1)–(3)**, distinguishes degree constraints from the additional odd-set inequalities needed for the integral matching polytope. **§3** states LP duality. [Original NBS paper](https://nvlpubs.nist.gov/nistpubs/jres/69B/jresv69Bn1-2p125_A1b.pdf). The assignment reduction below solves the degree-only fractional relaxation; it does not enforce those odd-set inequalities.

5. **MAPF cover formulation.** Li, Felner, Boyarski, Ma, and Koenig, *Improved Heuristics for Multi-Agent Path Finding with Conflict-Based Search*, IJCAI 2019, 442–449, **§5.1, p. 444**, formulate edge-weighted minimum vertex cover using nonnegative **integer** vertex values and constraints `x_i+x_j >= Δ_ij`. [Primary paper](https://www.ijcai.org/Proceedings/2019/0063.pdf), [author publication record](https://jiaoyangli.me/publications/LiIJCAI19/). Their objective conventions do not replace the preceding note's SOL-specific proof.

Access qualification: the Kuhn p. 90 and IJCAI p. 444 passages were available through indexed original-paper text; direct PDF opens failed. The argument below is derived explicitly here, not inferred from secondary tutorials.

## Definitions and the witness proof

For every feasible global solution, inherit

```text
B0 = sum_i d_i,
e_i = loss_i - d_i ∈ Z_{≥0},
e_i + e_j >= w_ij.
```

Here `w_ij` is a certified SOL pair excess lower bound. Use a symmetric matrix `W`, with nonnegative integer entries, `W_ii=0`, and `W_ij=w_ij` on retained pairs. Uncomputed or omitted pairs have matrix weight zero. Repeated bounds for the same unordered pair combine by maximum, not addition.

For a permutation `P` of the agents, define only for **distinct** agents

```text
z_ij = [P(i)=j] + [P(j)=i],       i < j,
y_ij = z_ij / 2,
A(P) = sum_i W_i,P(i) = sum_{i<j} w_ij*z_ij.
```

Each agent has at most one outgoing and one incoming selected off-diagonal arc. Hence `sum_j z_ij <= 2`, also after discarding zero-weight pairs. Multiplying the pair inequalities gives

```text
sum_{i<j} w_ij*z_ij
 <= sum_i e_i * sum_j z_ij
 <= 2*sum_i e_i.
```

Therefore **`SOL >= B0 + (A(P)+1)//2`**. This needs only a valid permutation and valid input weights; optimality is unnecessary. Nonnegativity of the excesses is essential to the second inequality.

Permutation cycles have a simple interpretation: a fixed point contributes nothing; a transposition gives its unordered pair numerator 2; a directed cycle of length at least 3 gives its cycle edges numerator 1. Even and odd cycles are both valid. These are abstract certificate arcs, not simultaneous MAPF moves: a transposition must not be rejected as an agent-swap collision.

## Exact LP connection

Define the degree-only fractional matching optimum

```text
F(W) = max sum_{i<j} w_ij*y_ij
       subject to y_ij >= 0, sum_j y_ij <= 1 for every i.
```

Zero-weight variables can be omitted. The claimed identity is

```text
max_permutation P A(P) = 2*F(W).
```

**Fractional matching to assignment.** Given feasible `y`, extend it symmetrically and set `X_ij=y_ij` off the diagonal and `X_ii=1-sum_j y_ij`. This matrix is nonnegative and every row and column sums to one. Symmetry of `W` and its zero diagonal give `sum_ij W_ij*X_ij = 2*sum_{i<j} w_ij*y_ij`. By the Birkhoff convex-hull theorem proved in von Neumann's Lemma 2, some permutation has at least this objective. Thus the assignment optimum is at least `2F`.

**Assignment to fractional matching.** More generally, for any doubly stochastic `X`, let `y_ij=(X_ij+X_ji)/2` for `i<j`. Its degree at agent `i` is `1-X_ii <= 1`; its objective is half the assignment objective. Applying this to a permutation proves the reverse inequality. Consequently an optimal denominator-2 witness always exists, even for real symmetric weights; integer weights make its objective an integer or half-integer. No separate half-integrality theorem is needed for this reduction.

By LP duality, `F(W)` also equals the minimum of `sum_i x_i` over **real** `x_i>=0` with `x_i+x_j>=w_ij`. It generally differs from the integer EWMVC optimum `V(W)`, and both relax the full MAPF problem:

```text
ceil(F(W)) <= sum_C ceil(F(W[C])) <= V(W)
          <= minimum feasible global SOL - B0.
```

Here `C` ranges over positive-weight connected components. For unit `K4`, `F=2` (all `x_i=1/2`) but `V=3`; an assignment certificate cannot establish the latter. A feasible integer cover is an upper bound on `V`, not a global-excess lower-bound certificate.

## Zeros, components, and rounding

- **Complete the assignment matrix.** Retain all zero-weight off-diagonal entries and all diagonal entries as allowed assignments. The diagonal is a dummy assignment between the two copies of one agent, not an inequality `2e_i>=w_ii`. It absorbs unused fractional capacity. Forbidding these entries can destroy the equivalence or feasibility. On a triangle with weights `5,1,1`, the optimum is a heavy-edge transposition plus a fixed point: assignment value 10. Requiring a derangement leaves only value-7 directed triangles.
- **Unknown is not proven independent.** Replacing an uncomputed pair by zero drops its constraint. The resulting bound remains valid. Cross-component constraints discovered later cannot invalidate an earlier bound. The certificate verifies aggregation only; it must still bind each positive weight to its independently replayable SOL pair-bound evidence.
- **Round disjoint budgets separately.** Within component `C`, its excess sum is an integer and is at least `A_C/2`, so use `H=sum_C (A_C+1)//2`. Isolated agents contribute zero. Two unit triangles give `2+2=4`, whereas `ceil((3+3)/2)=3`. With integer weights, only components whose optimum assignment value is odd create such a rounding opportunity.
- **Preserve earlier partitions.** Add one unit edge between those triangles: the graph becomes connected, `A=6`, and componentwise `H` falls to 3 although `V` remains 4. Taking the maximum with the earlier checked value 4 is sound. More generally any partition into disjoint agent sets permits separate rounding after ignoring crossing constraints. Splitting a permutation into its disjoint cycles, or splitting its positive witness support, can therefore be safe and stronger, but depends on the chosen optimal permutation; it is not an exact integer-cover solver.
- **Overlapping sets cannot be added.** Two distinct unit triangles `012` and `013` each give 2, but the assignment `e=(1,1,0,0)` satisfies their combined five pair constraints with total 2. Adding their rounded bounds would claim 4. Compare overlapping certificates by maximum unless a combined capacity check proves additivity.

## Integer Hungarian certificate and a small checker

For one component of size `k`, let `M=max_ij W_ij` and construct **every** cost entry as `c_ij=M-W_ij`, including `c_ii=M` and zero-weight pairs' costs `M`. For a permutation `P`, let `C=sum_i c_i,P(i)`. Then `A(P)=k*M-C`.

Use a standard dense Hungarian routine with integer reduced costs. Return the permutation and integer row/column potentials `u,v` satisfying

```text
u_i + v_j <= c_ij             for every real row/column pair,
sum_i u_i + sum_j v_j = C.
```

This is the minimum-cost sign convention; normalize a solver's convention before checking. Potentials may be negative. The equality proves optimality because every other permutation has cost at least the potential sum. Integer initialization and slack updates preserve integrality. Exclude any algorithmic dummy index-0 potential from the real row/column sums.

An optional useful cross-check is

```text
t_i = M-u_i-v_i >= 0,
t_i+t_j >= 2*w_ij,
sum_i t_i = A(P).
```

Thus `t/2` is a feasible real cover attaining the same value as the fractional witness. The diagonal inequalities establish its nonnegativity; the two directed inequalities for each pair establish coverage.

The standalone checker should reconstruct canonical weights and components, check integer types/dimensions, symmetry, zero diagonal, nonnegative weights, distinct agent IDs, and permutation bijectivity. Recompute `z`, all degree capacities, `A`, `C`, `M`, each dual inequality, the objective equality, and each integer ceiling. Store instance/objective identifiers, ordered agent IDs, pair-evidence references, permutation, potentials, and the claimed component totals. Python arbitrary-precision integers suffice; no optimization package or floating feasibility tolerance is needed. All-entry optimality checking takes quadratic work per component; a dense successive-augmentation implementation with at most `k` column scans per row augmentation takes cubic work. These are loop-count bounds, not runtime measurements.

**Keep certificate directions straight.** A feasible permutation gives a lower bound on maximum assignment weight. Feasible minimum-cost potentials alone give a lower bound on minimum cost, hence an **upper** bound on maximum assignment weight. Example: for a unit edge, `M=1`, `c=[[1,0],[0,1]]`, `u=(-1,-1)`, `v=(0,0)` is dual-feasible but would incorrectly suggest excess 2 from `(k*M-sum(u)-sum(v))/2`; the true minimum excess is 1. Require primal/dual equality to claim exactness. On interruption, retain an actually complete checked permutation or an earlier certificate; a partial assignment is insufficient.

## Exact small controls and shortcut failures

These values were checked in bounded, in-memory enumeration: all permutations, all feasible denominator-2 edge numerators, and all integer covers with coordinates in `0..max(W)`. The latter range suffices because truncating a cover coordinate to `max(W)` preserves feasibility. These are abstract pair-inequality controls, not constructed MAPF instances. Graphs had at most six vertices; no MAPF search or benchmark was run.

| Graph; all unspecified edges zero | Maximum assignment `A` | Fractional `F=A/2` | Component-rounded `H` | Integer cover `V` |
| --- | ---: | ---: | ---: | ---: |
| Empty / one isolated agent | 0 | 0 | 0 | 0 |
| One unit edge | 2 | 1 | 1 | 1 |
| Unit path on 3 vertices | 2 | 1 | 1 | 1 |
| Unit triangle | 3 | 3/2 | 2 | 2 |
| Two disjoint unit triangles | 6 | 3 | 4 | 4 |
| Unit cycle on 4 vertices | 4 | 2 | 2 | 2 |
| Unit cycle on 5 vertices | 5 | 5/2 | 3 | 3 |
| Unit `K4` | 4 | 2 | 2 | 3 |
| Triangle, edge weights `3,2,2` | 7 | 7/2 | 4 | 4 |
| Triangle, edge weights `5,1,1` | 10 | 5 | 5 | 5 |
| Two unit triangles joined by one unit edge | 6 | 3 | 3 | 4 |

For a unit odd cycle of length `2r+1`, the same calculation gives `F=r+1/2`, rounded bound `r+1`, and ordinary maximum matching weight `r`. An even directed assignment cycle can instead be replaced by alternating transpositions of at least its weight; odd cycles explain the possible fractional improvement over ordinary matching.

Small counterexamples to unsafe shortcuts:

- **Forget the factor two / round each directed arc separately:** a single unit edge gives assignment value 2 but feasible excess `(1,0)` totals 1. This already fails on two agents.
- **Sum overlapping pair weights / violate capacity:** the unit path `01,12` has feasible excess `(0,1,0)` totaling 1, not 2. Numerators `z_01=z_12=2` overfill agent 1 to 4 and must be rejected. Three vertices are the smallest simple graph with two distinct overlapping edges.
- **Round each fractional edge separately:** the unit triangle's feasible witness has three contributions `1/2`. Their separate ceilings total 3, but feasible excess `(1,1,0)` totals 2. Round the justified integer budget, not each term.
- **Treat the relaxation as integer EWMVC:** unit `K4` gives 2 versus 3. The triangle already separates fractional and integer values before ceiling; `K4` is a smallest unit-weight example where one connected-component ceiling still misses the integer optimum.

Separate in-memory Hungarian controls checked primal/dual equality, all reduced-cost inequalities, and the `t` cover identities on the isolated vertex, edge, path, unit triangle, both weighted triangles, and an edge of weight `2**53+1`. The invalid-capacity and dual-only examples were checked explicitly. Implementation tests should additionally mutate a column into a duplicate, alter a potential or claimed total, inject a nonzero diagonal/asymmetric weight, and test missing/zero edges, tied optima, and component merges. Reject malformed certificates instead of repairing them silently.

Recommended contribution scope: deterministic standard-library assignment, a separate exact arithmetic aggregation checker, these tiny controls, and provenance linking back to the existing SOL pair certificates. The reported headroom remains a gap to a relaxation, not attainable improvement or scientific acceptance.
