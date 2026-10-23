"""Exhaustive tiny controls using a separate unheuristic position-graph oracle."""
import heapq
import importlib.util
import itertools
import math
from collections import deque
from pathlib import Path

spec = importlib.util.spec_from_file_location("pair_bounds", Path(__file__).with_name("pair_bounds.py"))
pair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pair)


def distances(adj, goal):
    answer, queue = {goal: 0}, deque([goal])
    while queue:
        v = queue.popleft()
        for u in adj[v]:
            if u not in answer:
                answer[u] = answer[v] + 1
                queue.append(u)
    return answer


def exact(adj, starts, goals):
    queue = [(0, tuple(starts))]
    best = {tuple(starts): 0}
    while queue:
        cost, state = heapq.heappop(queue)
        if cost != best[state]:
            continue
        if state == tuple(goals):
            return cost
        first, second = state
        for a in (*adj[first], first):
            for b in (*adj[second], second):
                if a == b or (a == second and b == first):
                    continue
                added = 0
                if first != goals[0] or a != goals[0]:
                    added += 1
                if second != goals[1] or b != goals[1]:
                    added += 1
                value = cost + added
                if value < best.get((a, b), math.inf):
                    best[a, b] = value
                    heapq.heappush(queue, (value, (a, b)))
    return math.inf


def controls():
    loop = {v: tuple(u for u in range(6)
                     if abs(v % 3 - u % 3) + abs(v // 3 - u // 3) == 1)
            for v in range(6)}
    branch = {0: (1,), 1: (0, 2, 4), 2: (1,), 4: (1,)}
    corridor = {0: (1,), 1: (0, 2), 2: (1,)}
    return loop, branch, corridor


def test_exhaustive_admissibility_exactness_and_caps():
    for adj in controls():
        positions = list(itertools.permutations(adj, 2))
        for goals in positions:
            ds = [distances(adj, g) for g in goals]
            for starts in positions:
                optimum = exact(adj, starts, goals)
                previous = sum(d[s] for d, s in zip(ds, starts))
                for cap in (0, 1, 2, 5, 10, 40, 1000):
                    result = pair.lower_bound(adj, starts, goals, ds, cap)
                    assert result["popped"] <= cap
                    if result["status"] == "infeasible":
                        assert math.isinf(optimum)
                    else:
                        assert previous <= result["lower_bound"] <= optimum
                        previous = result["lower_bound"]
                    if result["status"] == "optimal":
                        assert result["lower_bound"] == optimum
                assert result["status"] != "capped"


def test_goal_departure_is_required_and_charged():
    _, adj, _ = controls()
    starts, goals = (1, 0), (1, 2)
    ds = [distances(adj, g) for g in goals]
    result = pair.lower_bound(adj, starts, goals, ds)
    assert exact(adj, starts, goals) == result["lower_bound"] == 4
    assert sum(d[s] for d, s in zip(ds, starts)) == 2
    # Agent zero begins at its own goal and must vacate it for agent one.
    assert all(u != 2 for u in adj[0])


def test_zero_cost_terminal_holding_and_unsolvable_swap():
    loop, _, corridor = controls()
    goals = (0, 5)
    ds = [distances(loop, g) for g in goals]
    assert pair.lower_bound(loop, goals, goals, ds)["lower_bound"] == 0
    result = pair.lower_bound(corridor, (0, 2), (2, 0),
                              [distances(corridor, g) for g in (2, 0)])
    assert result["status"] == "infeasible" and result["lower_bound"] is None


def test_SOC_pair_cost_is_not_an_SOL_lower_bound():
    # Five horizontal cells and a side pocket below cell three.
    adj = {0: (1,), 1: (0, 2), 2: (1, 3), 3: (2, 4, 8), 4: (3,), 8: (3,)}
    starts, goals = (8, 0), (3, 4)
    paths = ([8, 3, 3, 8, 3], [0, 1, 2, 3, 4])
    ds = [distances(adj, g) for g in goals]
    result = pair.lower_bound(adj, starts, goals, ds)
    loss = sum(a != g or b != g for p, g in zip(paths, goals) for a, b in zip(p, p[1:]))
    final_arrivals = sum(max(t + 1 for t, v in enumerate(p) if v != g)
                         for p, g in zip(paths, goals))
    assert result["lower_bound"] == exact(adj, starts, goals) == loss == 7
    assert final_arrivals == 8


def test_reject_malformed_pair_and_cap():
    import pytest
    adj = controls()[0]
    ds = [distances(adj, g) for g in (0, 5)]
    for starts, goals, supplied, cap in [((0, 0), (0, 5), ds, 10),
                                        ((0, 5), (0, 0), ds, 10),
                                        ((0, 5), (0, 5), ds[:1], 10),
                                        ((0, 5), (0, 5), ds, -1)]:
        with pytest.raises(ValueError):
            pair.lower_bound(adj, starts, goals, supplied, cap)
