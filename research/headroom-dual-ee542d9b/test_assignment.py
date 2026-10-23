"""Exact tiny assignment, cover and malformed-certificate controls."""
import copy
import importlib.util
import itertools
from pathlib import Path

import pytest

def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

assignment, checker = module("assignment"), module("check_assignment")


def matrix(n, edges):
    result = [[0] * n for _ in range(n)]
    for i, j, w in edges:
        result[i][j] = result[j][i] = w
    return result


def integer_cover(weights):
    n, maximum = len(weights), max((w for row in weights for w in row), default=0)
    return min(sum(x) for x in itertools.product(range(maximum + 1), repeat=n)
               if all(x[i] + x[j] >= weights[i][j] for i in range(n) for j in range(i)))


def test_all_four_vertex_weight_matrices_against_exact_oracles():
    edges = list(itertools.combinations(range(4), 2))
    for values in itertools.product(range(3), repeat=len(edges)):
        weights = matrix(4, [(i, j, w) for (i, j), w in zip(edges, values)])
        witness = assignment.maximum_assignment(weights)
        value = sum(weights[i][j] for i, j in enumerate(witness["permutation"]))
        exact = max(sum(weights[i][j] for i, j in enumerate(p)) for p in itertools.permutations(range(4)))
        assert value == exact
        result = assignment.solve(weights)
        checked = checker.check(weights, result)
        assert checked["component_rounded_extra"] <= checked["support_rounded_extra"] <= integer_cover(weights)


def test_odd_cycles_components_and_integer_cover_limit():
    triangle = matrix(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)])
    assert assignment.solve(triangle)["component_rounded_extra"] == 2
    two = matrix(6, [(0, 1, 1), (1, 2, 1), (0, 2, 1), (3, 4, 1), (4, 5, 1), (3, 5, 1)])
    assert assignment.solve(two)["component_rounded_extra"] == 4
    two[0][3] = two[3][0] = 1
    # Component merging can weaken this rounding heuristic; prior witnesses stay valid.
    assert assignment.solve(two)["component_rounded_extra"] == 3
    complete = matrix(4, [(i, j, 1) for i, j in itertools.combinations(range(4), 2)])
    assert assignment.solve(complete)["component_rounded_extra"] == 2 < integer_cover(complete) == 3
    cycle = matrix(5, [(i, (i + 1) % 5, 1) for i in range(5)])
    assert assignment.solve(cycle)["component_rounded_extra"] == 3


def test_fixed_points_and_large_exact_integers():
    weights = matrix(3, [(0, 1, 5), (1, 2, 1), (0, 2, 1)])
    result = assignment.solve(weights)
    assert checker.check(weights, result)["support_rounded_extra"] == 5
    assert any(i == j for i, j in enumerate(result["components"][0]["permutation"]))
    huge = matrix(2, [(0, 1, 10**60)])
    assert checker.check(huge, assignment.solve(huge))["support_rounded_extra"] == 10**60
    assert checker.check([], assignment.solve([]))["support_rounded_extra"] == 0


def test_reject_invalid_assignment_dual_capacity_and_scope():
    weights = matrix(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)])
    original = assignment.solve(weights)
    alterations = [
        lambda x: x["components"][0]["permutation"].__setitem__(0, -1),
        lambda x: x["components"][0]["row_potentials"].__setitem__(0, 999),
        lambda x: x["components"][0]["numerator_edges"][0].__setitem__("numerator", 3),
        lambda x: x["components"][0]["agents"].__setitem__(0, -1),
        lambda x: x["components"][0].__setitem__("component_rounded_extra", 99),
        lambda x: x["components"][0]["support_groups"][0].__setitem__("agents", [0, 0]),
    ]
    for alter in alterations:
        invalid = copy.deepcopy(original)
        alter(invalid)
        with pytest.raises(ValueError):
            checker.check(weights, invalid)
    with pytest.raises(ValueError):
        assignment.solve([[0, 1], [0, 0]])
