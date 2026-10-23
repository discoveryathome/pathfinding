"""Exact synthetic controls, independent time-layer DP and guarded replay."""
import importlib.util
import random
from pathlib import Path

spec = importlib.util.spec_from_file_location("sol_repair", Path(__file__).with_name("sol_repair.py"))
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)
from model import distances, metrics, path_loss
from repair import reservations, space_time_astar


def grid():
    return {"w": 3, "h": 2, "adj": {v: tuple(u for u in (v - 3, v + 3, v - 1, v + 1)
            if 0 <= u < 6 and abs(v % 3 - u % 3) + abs(v // 3 - u // 3) == 1) for v in range(6)}}


def exact_dp(g, start, goal, occupied, edges, horizon, deadline=None):
    if start in occupied[0]:
        return None
    limit = horizon if deadline is None else min(horizon, deadline)
    states, answers = {start: 0}, []
    for tick in range(limit + 1):
        if goal in states and all(goal not in cells for cells in occupied[tick:]):
            answers.append((states[goal], tick))
        if tick == limit:
            break
        following = {}
        for vertex, value in states.items():
            for other in (*g["adj"][vertex], vertex):
                if other in occupied[tick + 1] or (other, vertex) in edges[tick + 1]:
                    continue
                step = 0 if vertex == goal and other == goal else 1
                following[other] = min(following.get(other, 10**9), value + step)
        states = following
    return min(answers, default=None)


def assert_legal(path, occupied, edges, g):
    for t, v in enumerate(path):
        assert v not in occupied[t]
        if t:
            assert v == path[t - 1] or v in g["adj"][path[t - 1]]
            assert (v, path[t - 1]) not in edges[t]
    assert all(path[-1] not in cells for cells in occupied[len(path) - 1:])


def test_same_arrival_SOL_counterexample_and_full_walk_control():
    g, outsider, horizon = grid(), [4, 5, 5, 4, 5, 2, 2, 1], 7
    occ, edges = reservations([outsider], set(), horizon)
    ds = distances(g, 2)
    old, _, status = space_time_astar(g, 1, 2, ds, occ, edges, horizon, 10000)
    new, _, new_status = solver.space_time_sol(g, 1, 2, ds, occ, edges, horizon, 10000)
    assert status == new_status == "found"
    assert (path_loss(old), len(old) - 1) == (6, 7)
    assert (path_loss(new), len(new) - 1) == exact_dp(g, 1, 2, occ, edges, horizon) == (5, 7)
    assert_legal(old, occ, edges, g)
    assert_legal(new, occ, edges, g)
    walks = [[1]]
    for tick in range(1, horizon + 1):
        walks = [path + [v] for path in walks for v in (*g["adj"][path[-1]], path[-1])
                 if v not in occ[tick] and (v, path[-1]) not in edges[tick]]
    terminals = [path for path in walks if path[-1] == 2]
    assert len(terminals) == 70
    assert min(path_loss(path) for path in terminals) == 5


def test_seeded_reservations_match_exact_DP_and_caps():
    g = grid()
    rng = random.Random(int("ee542d9b4c91949140f009a90142f5ba", 16))
    for _ in range(150):
        horizon = 6
        outsider = [rng.randrange(6)]
        for tick in range(horizon):
            outsider.append(rng.choice((*g["adj"][outsider[-1]], outsider[-1])))
        start, goal = rng.randrange(6), rng.randrange(6)
        occ, edges = reservations([outsider], set(), horizon)
        ds = distances(g, goal)
        for deadline in (None, 3):
            expected = exact_dp(g, start, goal, occ, edges, horizon, deadline)
            path, popped, status = solver.space_time_sol(g, start, goal, ds, occ, edges, horizon, 10000, deadline)
            assert popped <= 10000
            assert (None if path is None else (path_loss(path), len(path) - 1)) == expected
            if path is not None:
                assert_legal(path, occ, edges, g)
            for cap in (0, 1, 5):
                candidate, used, why = solver.space_time_sol(g, start, goal, ds, occ, edges, horizon, cap, deadline)
                assert used <= cap
                if candidate is not None:
                    assert (path_loss(candidate), len(candidate) - 1) == expected


def test_goal_holding_future_block_and_reservation_suffix():
    g, horizon = grid(), 5
    occ, edges = reservations([[5, 4, 1, 2, 5, 4]], set(), horizon)
    result, _, _ = solver.space_time_sol(g, 0, 1, distances(g, 1), occ, edges, horizon, 1000)
    assert result is not None and len(result) - 1 > 2
    assert_legal(result, occ, edges, g)
    # The per-agent deadline must not truncate a later outside goal reservation.
    assert solver.space_time_sol(g, 0, 1, distances(g, 1), occ, edges, horizon, 1000, 2)[0] is None
    empty = [set() for _ in range(4)]
    assert solver.space_time_sol(g, 1, 1, distances(g, 1), empty, empty, 3, 10)[0] == [1]
    assert solver.space_time_sol(g, 0, 1, {}, empty, empty, 3, 10)[0] is None


def test_macro_replay_caps_and_no_regression():
    g = grid()
    ins = {"grid": g, "starts": [0, 2], "goals": [2, 0]}
    initial = [[0, 0, 1, 2], [2, 5, 4, 3, 0]]
    for method in ("sol", "sol-deadline"):
        a = solver.run(ins, initial, method, 17, node_budget=500, attempts=8, agent_cap=100)
        b = solver.run(ins, initial, method, 17, node_budget=500, attempts=8, agent_cap=100)
        assert a["paths"] == b["paths"] and a["history"] == b["history"] and a["budget"] == b["budget"]
        assert a["budget"]["nodes_used"] <= 500
        assert all(a["metrics"][k] <= metrics(initial)[k] for k in ("sol", "soc", "makespan"))
