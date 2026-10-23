"""Check pair lower bounds without importing the optimizer or its grid helpers."""
import argparse
import hashlib
import heapq
import json
import time
from collections import deque
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def wavefront(adj, goal):
    distance, queue = {goal: 0}, deque([goal])
    while queue:
        cell = queue.popleft()
        for other in adj[cell]:
            if other not in distance:
                distance[other] = distance[cell] + 1
                queue.append(other)
    return distance


def certify(adj, starts, goals, ds, claimed, pop_cap=500000):
    """Exhaust all paths that could cost less than claimed; never truncate to pass."""
    start = tuple(starts)
    queue, best, popped = [(0, start)], {start: 0}, 0
    while queue:
        if popped >= pop_cap:
            return {"verified": False, "reason": "verification_cap", "popped": popped}
        cost, state = heapq.heappop(queue)
        popped += 1
        if cost != best[state]:
            continue
        if cost + ds[0][state[0]] + ds[1][state[1]] >= claimed:
            continue
        if state == tuple(goals):
            return {"verified": False, "reason": "cheaper_pair_route", "cost": cost, "popped": popped}
        for first in (state[0], *adj[state[0]]):
            for second in (state[1], *adj[state[1]]):
                if first == second or (first == state[1] and second == state[0]):
                    continue
                added = int(state[0] != goals[0] or first != goals[0])
                added += int(state[1] != goals[1] or second != goals[1])
                value = cost + added
                if value + ds[0][first] + ds[1][second] >= claimed:
                    continue
                successor = (first, second)
                if value < best.get(successor, float("inf")):
                    best[successor] = value
                    heapq.heappush(queue, (value, successor))
    return {"verified": True, "reason": "cheaper_routes_exhausted", "popped": popped}


def check_matching(records):
    used = set()
    for record in records:
        agents = record["witness"]["agents"]
        if len(agents) != 2 or len(set(agents)) != 2 or used.intersection(agents):
            raise ValueError("Overlapping or malformed pair matching")
        used.update(agents)


def raw_grid(instance):
    data = (ROOT / instance["map"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == instance["map_sha256"]
    lines = data.decode().splitlines()
    height, width = int(lines[1].split()[1]), int(lines[2].split()[1])
    rows = lines[4:]
    assert len(rows) == height and all(len(row) == width for row in rows)
    free = {y * width + x for y, row in enumerate(rows) for x, cell in enumerate(row) if cell in ".GS"}
    adj = {}
    for cell in free:
        x, y = cell % width, cell // width
        adj[cell] = tuple(yy * width + xx for xx, yy in
                          ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                          if 0 <= xx < width and 0 <= yy < height and yy * width + xx in free)
    return adj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = (PACKAGE / args.out).resolve()
    if output.parent != PACKAGE or output.exists():
        parser.error("Use a new output filename in this package")
    report = json.loads((PACKAGE / "panel.json").read_text())
    assert report["all_cases_completed"] and len(report["cases"]) == 20
    for path, expected in report["source_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    journal = [json.loads(line) for line in (PACKAGE / "panel.jsonl").read_text().splitlines()]
    assert journal == [r for row in report["cases"] for r in row["pair_results"]]
    tick = time.perf_counter()
    results, total_pops, pairs = [], 0, 0
    for row in report["cases"]:
        raw = (ROOT / row["instance"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["instance_sha256"]
        instance = json.loads(raw)
        adj = raw_grid(instance)
        ds = [wavefront(adj, goal) for goal in instance["goals"]]
        individual = [d[s] for d, s in zip(ds, instance["starts"])]
        assert sum(individual) == row["individual_distance_bound"]
        check_matching(row["pair_results"])
        total, pair_pops = sum(individual), 0
        for record in row["pair_results"]:
            i, j = record["witness"]["agents"]
            assert record["individual_pair_bound"] == individual[i] + individual[j]
            claimed = record["combined_pair_bound"]
            answer = certify(adj, [instance["starts"][i], instance["starts"][j]],
                             [instance["goals"][i], instance["goals"][j]], [ds[i], ds[j]], claimed)
            assert answer["verified"], (row["case"], i, j, answer)
            total += claimed - individual[i] - individual[j]
            pair_pops += answer["popped"]
            pairs += 1
        assert total == row["new_pair_bound"]
        results.append({"case": row["case"], "verified_pair_bound": total,
                        "pairs_checked": len(row["pair_results"]), "verification_pops": pair_pops})
        total_pops += pair_pops
    assert pairs == 521
    loop = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3, 5), 5: (2, 4)}
    bad_bound = certify(loop, (0, 2), (2, 0), [wavefront(loop, g) for g in (2, 0)], 7)
    assert not bad_bound["verified"] and bad_bound["reason"] == "cheaper_pair_route"
    assert bad_bound["cost"] == 6
    overlapping = [{"witness": {"agents": [0, 1]}}, {"witness": {"agents": [1, 2]}}]
    try:
        check_matching(overlapping)
    except ValueError as error:
        overlap_error = str(error)
    else:
        raise AssertionError("Overlapping matching accepted")
    result = {"verified": True, "evidence_level": "author-checked separate implementation",
              "optimizer_imports": False, "cases": results, "pairs_checked": pairs,
              "verification_pops": total_pops, "per_pair_verification_pop_cap": 500000,
              "elapsed_seconds": time.perf_counter() - tick,
              "failure_controls": {"inflated_bound": bad_bound, "overlapping_matching": overlap_error},
              "panel_sha256": hashlib.sha256((PACKAGE / "panel.json").read_bytes()).hexdigest(),
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}))
