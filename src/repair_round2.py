"""Known-method corridor neighborhoods and bounded two-agent joint repair."""
from heapq import heappush, heappop
from itertools import product
import random
import time
from model import at, trim, metrics, dominates, distances
from repair import reservations, add_path, space_time_astar, choose, improve


def joint_astar(grid, starts, goals, ds, occupied, edges, horizon, budget):
    """Minimize SOL in a two-agent time-expanded graph with fixed outsiders.

    Waiting at a goal costs zero; leaving it costs one. Goal arrivals are not
    absorbing. The horizon is fixed, so terminal holding is checked explicitly.
    A popped joint state is NOT equivalent in cost to a single-agent state.
    """
    starts, goals = tuple(starts), tuple(goals)
    if len(starts) != 2 or len(set(starts)) != 2:
        raise ValueError('Exactly two distinct starts required')
    if any(v in occupied[0] or v not in d for v, d in zip(starts, ds)):
        return None, 0, 'blocked_start'
    last_block = [max((t for t, occ in enumerate(occupied) if g in occ), default=-1) for g in goals]
    start = (starts, 0)
    best = {start: 0}
    parents = {}
    queue = [(sum(d[v] for d, v in zip(ds, starts)), 0, 0, starts)]
    used = 0
    while queue and used < budget:
        _, g, negt, positions = heappop(queue)
        t = -negt
        used += 1
        state = (positions, t)
        if best.get(state) != g:
            continue
        if positions == goals and all(t > b for b in last_block):
            chain = [positions]
            while state in parents:
                state = parents[state]
                chain.append(state[0])
            chain.reverse()
            return [[q[i] for q in chain] for i in range(2)], used, 'found'
        if t == horizon:
            continue
        nt = t + 1
        choices = []
        for i, v in enumerate(positions):
            choices.append([u for u in grid['adj'][v] + (v,)
                            if u not in occupied[nt] and (u, v) not in edges[nt]
                            and u in ds[i] and nt + ds[i][u] <= horizon])
        for nxt in product(*choices):
            if nxt[0] == nxt[1] or (nxt[0] == positions[1] and nxt[1] == positions[0]):
                continue
            ng = g + sum(a != goal or b != goal for a, b, goal in zip(positions, nxt, goals))
            ns = (nxt, nt)
            if ng >= best.get(ns, float('inf')):
                continue
            best[ns] = ng
            parents[ns] = (positions, t)
            heappush(queue, (ng + sum(d[v] for d, v in zip(ds, nxt)), ng, -nt, nxt))
    return None, used, 'budget' if queue else 'exhausted'


def corridor_group(paths, ds, grid, rng, k=4):
    regret = [len(p) - 1 - ds[i][p[0]] for i, p in enumerate(paths)]
    anchor = rng.choices(range(len(paths)), weights=[r + 1 for r in regret])[0]
    bottlenecks = {v for v in paths[anchor] if len(grid['adj'][v]) <= 2}
    scores = {i: len(bottlenecks.intersection(p)) for i, p in enumerate(paths) if i != anchor}
    # If there is no corridor, retain a random control-style neighborhood.
    if not bottlenecks:
        group = [anchor] + rng.sample([i for i in scores], min(k - 1, len(scores)))
    else:
        jitter = {i: rng.random() for i in scores}
        group = [anchor] + sorted(scores, key=lambda i: (-scores[i], -regret[i], jitter[i]))[:k-1]
    rng.shuffle(group)
    return group


def run(ins, initial, variant, seed, node_budget=100000, attempts=96, agent_cap=10000):
    if variant in ('random4', 'proximity4'):
        return improve(ins, initial, variant, seed, node_budget, attempts, agent_cap)
    if variant not in ('corridor4', 'joint2'):
        raise ValueError(variant)
    start = time.perf_counter()
    paths = [trim(p) for p in initial]
    rng = random.Random(seed)
    grid = ins['grid']
    ds = [distances(grid, goal) for goal in ins['goals']]
    preprocess = time.perf_counter() - start
    used, history, improvements = 0, [], []
    for attempt in range(attempts):
        if used >= node_budget:
            break
        before = metrics(paths)
        horizon = before['makespan']
        group = (corridor_group(paths, ds, grid, rng) if variant == 'corridor4'
                 else choose(paths, ds, grid, 'proximity', 2, rng))
        occupied, edges = reservations(paths, set(group), horizon)
        candidate = [p[:] for p in paths]
        popped, status = 0, 'complete'
        if variant == 'joint2':
            result, work, result_status = joint_astar(
                grid, [ins['starts'][i] for i in group], [ins['goals'][i] for i in group],
                [ds[i] for i in group], occupied, edges, horizon, min(agent_cap, node_budget-used))
            used += work
            popped += work
            if result is None:
                status = result_status
            else:
                for i, path in zip(group, result):
                    candidate[i] = trim(path)
        else:
            for i in group:
                cap = min(agent_cap, node_budget-used)
                if cap <= 0:
                    status = 'total_budget'
                    break
                result, work, result_status = space_time_astar(
                    grid, ins['starts'][i], ins['goals'][i], ds[i], occupied, edges, horizon, cap)
                used += work
                popped += work
                if result is None:
                    status = result_status
                    break
                candidate[i] = trim(result)
                add_path(candidate[i], occupied, edges, horizon)
        after = metrics(candidate) if status == 'complete' else before
        accepted = status == 'complete' and dominates(after, before)
        if accepted:
            paths = candidate
            improvements.append({'attempt': attempt, 'metrics': after, 'paths': [p[:] for p in paths]})
        history.append({'attempt': attempt, 'agents': group, 'popped': popped, 'status': status,
                        'accepted': accepted, 'before': before, 'proposed': after})
    return {'paths': paths, 'metrics': metrics(paths), 'variant': variant, 'seed': seed,
            'budget': {'node_limit': node_budget, 'nodes_used': used, 'attempt_limit': attempts,
                       'attempts_used': len(history), 'per_agent_limit': agent_cap},
            'preprocess_seconds': preprocess, 'elapsed_seconds': time.perf_counter()-start,
            'history': history, 'improvements': improvements}
