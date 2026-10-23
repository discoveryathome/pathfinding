"""Draw all predeclared fresh queries once, after the policy/protocol commit."""
from collections import deque
import random

from common import PACKAGE, ROOT, check_limits, protocol, save, sha, source_identity
from model import distances, read_map


def largest_component(grid):
    unseen, components = set(grid["adj"]), []
    while unseen:
        first = min(unseen)
        unseen.remove(first)
        queue, group = deque([first]), [first]
        while queue:
            vertex = queue.popleft()
            for neighbor in grid["adj"][vertex]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    group.append(neighbor)
                    queue.append(neighbor)
        components.append(sorted(group))
    return min(components, key=lambda group: (-len(group), group[0]))


def draw(grid, count, seed):
    cells = largest_component(grid)
    rng = random.Random(seed)
    return rng.sample(cells, count), rng.sample(cells, count)


def main():
    plan = protocol()
    identity = source_identity(plan)
    check_limits(plan)
    if (PACKAGE / "inputs.json").exists() or (PACKAGE / "inputs").exists():
        raise FileExistsError("Fresh inputs already exist; preserve this draw")
    rows = []
    for case in plan["cases"]:
        grid = read_map(ROOT / case["map"])
        starts, goals = draw(grid, case["agents"], int(case["draw_seed_decimal"]))
        directory = PACKAGE / "inputs"
        directory.mkdir(exist_ok=True)
        scenario = directory / (case["id"] + ".scen")
        lines = ["version 1"]
        for start, goal in zip(starts, goals):
            distance = distances(grid, goal)[start]
            lines.append("\t".join(map(str, (0, (ROOT / case["map"]).name, grid["w"], grid["h"],
                start % grid["w"], start // grid["w"], goal % grid["w"], goal // grid["w"], distance))))
        with scenario.open("x") as handle:
            handle.write("\n".join(lines) + "\n")
        instance = {"id": case["id"], "map": case["map"], "map_sha256": case["map_sha256"],
                    "scenario": str(scenario.relative_to(ROOT)), "scenario_sha256": sha(scenario),
                    "starts": starts, "goals": goals, "movement": "four-neighbor + wait",
                    "exposure": "Fresh author-generated queries on published maps; not unseen corpus"}
        path = directory / (case["id"] + ".json")
        save(path, instance)
        rows.append({"case": case["id"], "instance": str(path.relative_to(ROOT)),
                     "instance_sha256": sha(path), "scenario": instance["scenario"],
                     "scenario_sha256": instance["scenario_sha256"]})
    save(PACKAGE / "inputs.json", {**identity, "cases": rows, "protocol_sha256": sha(PACKAGE / "protocol.json"),
                                   "generated_after_source_commit": True, "generator": "inputs.py",
                                   "evidence_level": "author-generated within-map variation"})
    print(f"Retained all {len(rows)} fixed fresh queries")


if __name__ == "__main__":
    main()
