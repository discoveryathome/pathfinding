"""Freeze the complete forced-conflict graph, retaining the canonical matching."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from model import distances, read_instance


def full_pairs(ins, horizon=32):
    forced = []
    for start, goal in zip(ins["starts"], ins["goals"]):
        left, right = distances(ins["grid"], start), distances(ins["grid"], goal)
        length = left[goal]
        cells = []
        for step in range(horizon + 1):
            if step >= length:
                cells.append(goal)
            else:
                choices = [v for v, d in left.items() if d == step and v in right and step + right[v] == length]
                cells.append(choices[0] if len(choices) == 1 else None)
        forced.append(cells)
    edges = []
    for i in range(len(forced)):
        for j in range(i):
            for step in range(1, horizon + 1):
                a, b = forced[i][step], forced[j][step]
                vertex = a is not None and a == b
                swap = (a is not None and b is not None and forced[i][step - 1] == b and forced[j][step - 1] == a)
                if vertex or swap:
                    edges.append({"agents": [j, i], "time": step, "kind": "vertex" if vertex else "edge-swap"})
                    break
    return edges


def greedy_matching(edges):
    used, chosen = set(), []
    for edge in edges:
        if not used.intersection(edge["agents"]):
            chosen.append(edge)
            used.update(edge["agents"])
    return chosen


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = (PACKAGE / args.out).resolve()
    if out.parent != PACKAGE or out.exists():
        parser.error("Use a new scope filename in this package")
    canonical_path = ROOT / "research/distribution-prep-20261022/headroom.json"
    assert hashlib.sha256(canonical_path.read_bytes()).hexdigest() == "18a57ffab7f44ae9659ff55f137b02d8313b1a0873839c4090deab2ab300a350"
    canonical = {r["case"]: r for r in json.loads(canonical_path.read_text())}
    rows = []
    for case in json.loads((ROOT / "discover/incumbents.json").read_text()):
        ip = ROOT / case["instance"]
        edges = full_pairs(read_instance(ip))
        matching = greedy_matching(edges)
        assert edges and matching == canonical[case["case"]]["disjoint_pair_witnesses"]
        assert len(edges) == canonical[case["case"]]["conflicting_pairs"]
        rows.append({"case": case["case"], "instance": case["instance"],
                     "instance_sha256": hashlib.sha256(ip.read_bytes()).hexdigest(),
                     "pairs": edges, "fixed_matching": matching})
    assert len(rows) == 20 and sum(len(r["pairs"]) for r in rows) == 2785
    assert sum(len(r["fixed_matching"]) for r in rows) == 521
    result = {"horizon": 32, "canonical_headroom_sha256": hashlib.sha256(canonical_path.read_bytes()).hexdigest(),
              "scope_builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "cases": rows}
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"saved": str(out), "cases": 20, "pairs": 2785, "fixed_pairs": 521,
                      "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}))
