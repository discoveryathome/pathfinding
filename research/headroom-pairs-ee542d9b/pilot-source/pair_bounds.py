"""SOL lower bounds in the static two-agent position product graph."""
from heapq import heappop, heappush
from itertools import product
from time import perf_counter


def lower_bound(adj, starts, goals, distances, node_limit=10000):
    """Return an exact optimum, or the admissible open-frontier lower bound.

    Goals are not absorbing. Each agent transition costs one unless both
    endpoints are its goal. With no outside agents, time is unnecessary state.
    Every heap pop, including a stale entry, consumes the declared node cap.
    """
    starts, goals = tuple(starts), tuple(goals)
    if (len(starts) != 2 or len(goals) != 2 or len(set(starts)) != 2
            or len(set(goals)) != 2 or node_limit < 0):
        raise ValueError("Use two distinct starts/goals and a nonnegative cap")
    if any(s not in d for s, d in zip(starts, distances)):
        raise ValueError("Disconnected start/goal")
    tick = perf_counter()
    initial = sum(d[s] for d, s in zip(distances, starts))
    queue = [(initial, 0, starts)]
    best = {starts: 0}
    popped, peak_queue = 0, 1

    def result(value, status):
        return {"lower_bound": value, "status": status, "popped": popped,
                "node_limit": node_limit, "discovered_states": len(best),
                "peak_queue_entries": peak_queue,
                "elapsed_seconds": perf_counter() - tick}

    while queue:
        if popped >= node_limit:
            # Ignore obsolete entries; all previously popped live states were
            # fully expanded, so the live frontier still separates every path.
            frontier = min((f for f, negcost, state in queue
                            if best[state] == -negcost), default=None)
            return result(frontier, "capped" if frontier is not None else "infeasible")
        _, negcost, positions = heappop(queue)
        popped += 1
        cost = -negcost
        if best[positions] != cost:
            continue
        if positions == goals:
            return result(cost, "optimal")
        for nxt in product(*(tuple(adj[v]) + (v,) for v in positions)):
            if (nxt == positions or nxt[0] == nxt[1]
                    or (nxt[0] == positions[1] and nxt[1] == positions[0])):
                continue
            if any(v not in d for v, d in zip(nxt, distances)):
                continue
            value = cost + sum(a != goal or b != goal
                               for a, b, goal in zip(positions, nxt, goals))
            if value >= best.get(nxt, float("inf")):
                continue
            best[nxt] = value
            estimate = value + sum(d[v] for d, v in zip(distances, nxt))
            heappush(queue, (estimate, -value, nxt))
        peak_queue = max(peak_queue, len(queue))
    return result(None, "infeasible")
