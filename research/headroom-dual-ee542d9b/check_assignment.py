"""Check an integer assignment/dual witness without importing its optimizer."""


def groups(matrix):
    remaining = {i for i in range(len(matrix)) if any(matrix[i])}
    answer = []
    while remaining:
        todo, reached = [min(remaining)], set()
        while todo:
            i = todo.pop()
            if i in reached:
                continue
            reached.add(i)
            todo.extend(j for j, value in enumerate(matrix[i]) if value > 0 and j not in reached)
        remaining.difference_update(reached)
        answer.append(sorted(reached))
    return answer


def check(weights, result):
    n = len(weights)
    if any(len(row) != n for row in weights):
        raise ValueError("Non-square matrix")
    if any(type(w) is not int or w < 0 for row in weights for w in row):
        raise ValueError("Noninteger or negative weight")
    if any(weights[i][i] or any(weights[i][j] != weights[j][i] for j in range(n)) for i in range(n)):
        raise ValueError("Non-symmetric pair matrix")
    expected = groups(weights)
    certificates = result["components"]
    if (any(type(result[key]) is not int for key in ("component_rounded_extra", "support_rounded_extra"))
            or any(any(type(i) is not int for i in c["agents"]) for c in certificates)):
        raise ValueError("Use integer objectives and canonical agent IDs")
    if [c["agents"] for c in certificates] != expected:
        raise ValueError("Wrong component coverage or agent identity")
    component_total, support_total = 0, 0
    for agents, certificate in zip(expected, certificates):
        if any(type(certificate[key]) is not int for key in
               ("denominator", "numerator_value", "component_rounded_extra", "support_rounded_extra")):
            raise ValueError("Use integer certificate values")
        for edge in certificate["numerator_edges"]:
            if type(edge["numerator"]) is not int or any(type(i) is not int for i in edge["agents"]):
                raise ValueError("Use integer edge numerators and IDs")
        for group in certificate["support_groups"]:
            if (any(type(i) is not int for i in group["agents"])
                    or any(type(group[key]) is not int for key in ("numerator_value", "rounded_extra"))):
                raise ValueError("Use integer support groups")
        k = len(agents)
        p, u, v = (certificate[key] for key in ("permutation", "row_potentials", "column_potentials"))
        if (len(p) != k or any(type(j) is not int for j in p) or sorted(p) != list(range(k))
                or len(u) != k or len(v) != k or any(type(x) is not int for x in [*u, *v])):
            raise ValueError("Malformed permutation or integer potentials")
        maximum = max(weights[i][j] for i in agents for j in agents)
        cost = sum(maximum - weights[agents[i]][agents[p[i]]] for i in range(k))
        for i in range(k):
            for j in range(k):
                if u[i] + v[j] > maximum - weights[agents[i]][agents[j]]:
                    raise ValueError("Assignment dual inequality violated")
        if sum(u) + sum(v) != cost:
            raise ValueError("Assignment primal/dual objectives differ")
        numerator_edges, capacities = {}, {i: 0 for i in agents}
        for i, j in enumerate(p):
            a, b = agents[i], agents[j]
            if a != b and weights[a][b] > 0:
                edge = tuple(sorted((a, b)))
                numerator_edges[edge] = numerator_edges.get(edge, 0) + 1
        expected_edges = [{"agents": [i, j], "numerator": z}
                          for (i, j), z in sorted(numerator_edges.items())]
        if certificate["denominator"] != 2 or certificate["numerator_edges"] != expected_edges:
            raise ValueError("Wrong fractional matching witness")
        support = [[0] * n for _ in range(n)]
        numerator_value = 0
        for (i, j), z in numerator_edges.items():
            capacities[i] += z
            capacities[j] += z
            support[i][j] = support[j][i] = z
            numerator_value += weights[i][j] * z
        if any(value > 2 for value in capacities.values()):
            raise ValueError("Fractional matching exceeds vertex capacity")
        if numerator_value != k * maximum - cost or certificate["numerator_value"] != numerator_value:
            raise ValueError("Wrong numerator objective")
        component_bound = (numerator_value + 1) // 2
        if certificate["component_rounded_extra"] != component_bound:
            raise ValueError("Wrong component ceiling")
        expected_support = []
        for members in groups(support):
            value = sum(weights[i][j] * z for (i, j), z in numerator_edges.items() if i in members)
            expected_support.append({"agents": members, "numerator_value": value,
                                     "rounded_extra": (value + 1) // 2})
        if certificate["support_groups"] != expected_support:
            raise ValueError("Wrong disjoint support partition")
        support_bound = sum(g["rounded_extra"] for g in expected_support)
        if certificate["support_rounded_extra"] != support_bound:
            raise ValueError("Wrong support ceiling sum")
        component_total += component_bound
        support_total += support_bound
    if (result["component_rounded_extra"] != component_total
            or result["support_rounded_extra"] != support_total):
        raise ValueError("Wrong aggregate objective")
    return {"component_rounded_extra": component_total, "support_rounded_extra": support_total}
