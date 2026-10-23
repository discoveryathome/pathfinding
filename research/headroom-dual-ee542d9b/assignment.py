"""Integer Hungarian assignment and explicit fractional-matching witnesses."""


def maximum_assignment(weights):
    n = len(weights)
    if any(len(row) != n for row in weights):
        raise ValueError("Assignment matrix must be square")
    if any(type(w) is not int or w < 0 for row in weights for w in row):
        raise ValueError("Use nonnegative integer weights")
    maximum = max((w for row in weights for w in row), default=0)
    costs = [[maximum - w for w in row] for row in weights]
    u, v, column_row, previous = ([0] * (n + 1) for _ in range(4))
    for row in range(1, n + 1):
        column_row[0] = row
        column = 0
        slack, used = [None] * (n + 1), [False] * (n + 1)
        while True:
            used[column] = True
            active = column_row[column]
            delta, next_column = None, None
            for candidate in range(1, n + 1):
                if used[candidate]:
                    continue
                reduced = costs[active - 1][candidate - 1] - u[active] - v[candidate]
                if slack[candidate] is None or reduced < slack[candidate]:
                    slack[candidate], previous[candidate] = reduced, column
                if delta is None or slack[candidate] < delta:
                    delta, next_column = slack[candidate], candidate
            for candidate in range(n + 1):
                if used[candidate]:
                    u[column_row[candidate]] += delta
                    v[candidate] -= delta
                elif slack[candidate] is not None:
                    slack[candidate] -= delta
            column = next_column
            if column_row[column] == 0:
                break
        while column:
            parent = previous[column]
            column_row[column] = column_row[parent]
            column = parent
    permutation = [0] * n
    for column in range(1, n + 1):
        permutation[column_row[column] - 1] = column - 1
    return {"permutation": permutation, "row_potentials": u[1:], "column_potentials": v[1:]}


def components(matrix):
    unseen = {i for i, row in enumerate(matrix) if any(row)}
    answer = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        group, pending = {seed}, [seed]
        while pending:
            i = pending.pop()
            neighbors = {j for j in unseen if matrix[i][j] > 0}
            unseen.difference_update(neighbors)
            group.update(neighbors)
            pending.extend(sorted(neighbors))
        answer.append(sorted(group))
    return answer


def solve(weights):
    n = len(weights)
    if any(len(row) != n for row in weights):
        raise ValueError("Weights must be square")
    if any(type(w) is not int or w < 0 for row in weights for w in row):
        raise ValueError("Use nonnegative integer weights")
    if any(weights[i][i] or any(weights[i][j] != weights[j][i] for j in range(n)) for i in range(n)):
        raise ValueError("Pair weights must be symmetric with zero diagonal")
    certificates = []
    for agents in components(weights):
        local = [[weights[i][j] for j in agents] for i in agents]
        certificate = maximum_assignment(local)
        numerators = {}
        for i, j in enumerate(certificate["permutation"]):
            if i != j and local[i][j] > 0:
                edge = tuple(sorted((agents[i], agents[j])))
                numerators[edge] = numerators.get(edge, 0) + 1
        numerator_value = sum(weights[i][j] * z for (i, j), z in numerators.items())
        support = [[0] * len(agents) for _ in agents]
        index = {agent: i for i, agent in enumerate(agents)}
        for (i, j), z in numerators.items():
            support[index[i]][index[j]] = support[index[j]][index[i]] = z
        support_groups = []
        for positions in components(support):
            members = {agents[i] for i in positions}
            value = sum(weights[i][j] * z for (i, j), z in numerators.items() if i in members)
            support_groups.append({"agents": sorted(members), "numerator_value": value,
                                   "rounded_extra": (value + 1) // 2})
        certificates.append({"agents": agents, **certificate, "denominator": 2,
                             "numerator_edges": [{"agents": [i, j], "numerator": z}
                                                 for (i, j), z in sorted(numerators.items())],
                             "numerator_value": numerator_value,
                             "component_rounded_extra": (numerator_value + 1) // 2,
                             "support_groups": support_groups,
                             "support_rounded_extra": sum(x["rounded_extra"] for x in support_groups)})
    return {"components": certificates,
            "component_rounded_extra": sum(c["component_rounded_extra"] for c in certificates),
            "support_rounded_extra": sum(c["support_rounded_extra"] for c in certificates)}
