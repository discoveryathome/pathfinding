"""Verify full-scope pair bounds and integer assignment/dual certificates."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from check_assignment import check as check_aggregation
from pair_verifier import certify, raw_grid, wavefront

SCOPE_SHA256 = "e40ec6b5f08d0d2d032e55921b5ed0d61051e14cf31b2ccc5e0611f002976cb0"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_scope(rows, scope, archive):
    names = [row["case"] for row in rows]
    if len(names) != len(scope) or len(set(names)) != len(names) or set(names) != set(scope):
        raise ValueError("Each canonical case must appear exactly once")
    for row in rows:
        name = row["case"]
        if (row["instance"] != scope[name]["instance"] or row["instance"] != archive[name]["instance"]
                or row["instance_sha256"] != scope[name]["instance_sha256"]
                or row["inherited"] != archive[name]["pareto_candidates"][0]):
            raise ValueError("Wrong canonical instance or incumbent binding")
        if ([r["witness"] for r in row["pairs"]] != scope[name]["pairs"]
                or any(r["case"] != name for r in row["pairs"])
                or row["fixed_matching"] != scope[name]["fixed_matching"]):
            raise ValueError("Wrong full pair scope or fixed matching")


def pair_ids(record, agents):
    ids = record["witness"]["agents"]
    if (len(ids) != 2 or any(type(i) is not int or not 0 <= i < agents for i in ids)
            or ids[0] >= ids[1]):
        raise ValueError("Invalid canonical pair IDs")
    return ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = (PACKAGE / args.out).resolve()
    if output.parent != PACKAGE or output.exists():
        parser.error("Use a new verification output in this package")
    assert digest(PACKAGE / "scope.json") == SCOPE_SHA256
    scope_data = json.loads((PACKAGE / "scope.json").read_text())
    scope = {c["case"]: c for c in scope_data["cases"]}
    archive = {c["case"]: c for c in json.loads((ROOT / "discover/incumbents.json").read_text())}
    assert len(scope) == len(archive) == 20 and set(scope) == set(archive)
    report = json.loads((PACKAGE / "panel.json").read_text())
    validate_scope(report["cases"], scope, archive)
    for path, expected in report["source_sha256"].items():
        assert digest(ROOT / path) == expected, path
    journal = [json.loads(line) for line in (PACKAGE / "panel.jsonl").read_text().splitlines()]
    assert journal == [r for row in report["cases"] for r in row["pairs"]]
    tick = time.perf_counter()
    checked_cases, verification_pops, pair_count = [], 0, 0
    for row in report["cases"]:
        raw = (ROOT / row["instance"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["instance_sha256"]
        instance = json.loads(raw)
        adj = raw_grid(instance)
        ds = [wavefront(adj, goal) for goal in instance["goals"]]
        individual = [d[start] for d, start in zip(ds, instance["starts"])]
        assert sum(individual) == row["individual_distance_bound"]
        n, seen = len(individual), set()
        weights = [[0] * n for _ in range(n)]
        pops = 0
        for record in row["pairs"]:
            i, j = pair_ids(record, n)
            assert (i, j) not in seen
            seen.add((i, j))
            elementary = individual[i] + individual[j]
            claimed = record["pair_lower_bound"]
            assert type(claimed) is int and claimed >= elementary + 1
            assert record["individual_pair_bound"] == elementary
            assert record["excess"] == claimed - elementary
            result = certify(adj, [instance["starts"][i], instance["starts"][j]],
                             [instance["goals"][i], instance["goals"][j]], [ds[i], ds[j]], claimed)
            assert result["verified"], (row["case"], i, j, result)
            weights[i][j] = weights[j][i] = claimed - elementary
            pops += result["popped"]
        assert len(seen) == row["pair_count"]
        verified = check_aggregation(weights, row["dual_certificate"])
        fixed_extra = sum(weights[edge["agents"][0]][edge["agents"][1]] for edge in row["fixed_matching"])
        expected = sum(individual) + max(fixed_extra, verified["component_rounded_extra"], verified["support_rounded_extra"])
        assert row["fixed_pair_bound"] == sum(individual) + fixed_extra
        assert row["graph_component_bound"] == sum(individual) + verified["component_rounded_extra"]
        assert row["witness_support_bound"] == sum(individual) + verified["support_rounded_extra"]
        assert row["selected_bound"] == expected
        checked_cases.append({"case": row["case"], "pairs_checked": len(seen), "verified_bound": expected,
                              "verification_pops": pops, "assignment_and_dual_valid": True})
        verification_pops += pops
        pair_count += len(seen)
    assert pair_count == 2785
    result = {"verified": True, "evidence_level": "author-checked separate implementations",
              "optimizer_imports": False, "canonical_scope_verified": True,
              "cases": checked_cases, "pairs_checked": pair_count, "verification_pops": verification_pops,
              "elapsed_seconds": time.perf_counter() - tick, "scope_sha256": SCOPE_SHA256,
              "panel_sha256": digest(PACKAGE / "panel.json"),
              "verifier_sha256": digest(Path(__file__)), "aggregation_checker_sha256": digest(PACKAGE / "check_assignment.py")}
    with output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}))
