"""Known prioritized repair with explicit lexicographic (SOL, arrival) search."""
from heapq import heappop, heappush
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from model import distances, dominates, metrics, trim
from repair import add_path, choose, reservations


def space_time_sol(grid, start, goal, dist, occupied, edges, horizon, budget, arrival_cap=None):
    if start in occupied[0] or start not in dist:
        return None, 0, "blocked_start"
    deadline = horizon if arrival_cap is None else min(horizon, arrival_cap)
    last_block = max((t for t, cells in enumerate(occupied) if goal in cells), default=-1)
    queue = [(dist[start], dist[start], 0, start, 0)]
    best, parent, popped = {(start, 0): 0}, {}, 0
    while queue and popped < budget:
        _, _, negtime, vertex, cost = heappop(queue)
        tick = -negtime
        popped += 1
        state = (vertex, tick)
        if best.get(state) != cost:
            continue
        if vertex == goal and tick > last_block:
            path = [vertex]
            while state in parent:
                state = parent[state]
                path.append(state[0])
            return list(reversed(path)), popped, "found"
        if tick == deadline:
            continue
        nt = tick + 1
        for other in grid["adj"][vertex] + (vertex,):
            if (other in occupied[nt] or (other, vertex) in edges[nt]
                    or other not in dist or nt + dist[other] > deadline):
                continue
            value = cost + int(vertex != goal or other != goal)
            successor = (other, nt)
            if value >= best.get(successor, float("inf")):
                continue
            best[successor], parent[successor] = value, (vertex, tick)
            heappush(queue, (value + dist[other], nt + dist[other], -nt, other, value))
    return None, popped, "budget" if queue else "exhausted"


def run(ins, initial, method, seed, node_budget=100000, attempts=96, agent_cap=10000):
    if method not in ("sol", "sol-deadline"):
        raise ValueError("Unknown SOL repair policy")
    started = time.perf_counter()
    paths = [trim(path) for path in initial]
    rng, grid = random.Random(seed), ins["grid"]
    ds = [distances(grid, goal) for goal in ins["goals"]]
    preprocessing = time.perf_counter() - started
    used, history, improvements = 0, [], []
    for attempt in range(attempts):
        if used >= node_budget:
            break
        before = metrics(paths)
        horizon = before["makespan"]
        group = choose(paths, ds, grid, "random", 4, rng)
        occupied, edges = reservations(paths, set(group), horizon)
        candidate, popped, status = [path[:] for path in paths], 0, "complete"
        for agent in group:
            cap = min(agent_cap, node_budget - used)
            if cap <= 0:
                status = "total_budget"
                break
            arrival_cap = len(paths[agent]) - 1 if method == "sol-deadline" else None
            result, work, search_status = space_time_sol(
                grid, ins["starts"][agent], ins["goals"][agent], ds[agent],
                occupied, edges, horizon, cap, arrival_cap)
            used += work
            popped += work
            if result is None:
                status = search_status
                break
            candidate[agent] = trim(result)
            add_path(candidate[agent], occupied, edges, horizon)
        after = metrics(candidate) if status == "complete" else before
        accepted = status == "complete" and dominates(after, before)
        if accepted:
            paths = candidate
            improvements.append({"attempt": attempt, "metrics": after, "paths": [p[:] for p in paths]})
        history.append({"attempt": attempt, "agents": group, "popped": popped,
                        "status": status, "accepted": accepted, "before": before, "proposed": after})
    return {"paths": paths, "metrics": metrics(paths), "variant": method, "seed": seed,
            "budget": {"node_limit": node_budget, "nodes_used": used, "attempt_limit": attempts,
                       "attempts_used": len(history), "per_agent_limit": agent_cap},
            "preprocess_seconds": preprocessing, "elapsed_seconds": time.perf_counter() - started,
            "history": history, "improvements": improvements}
