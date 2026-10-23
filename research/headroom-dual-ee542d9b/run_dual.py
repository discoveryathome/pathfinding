"""Bound the predeclared full pair graph and retain explicit dual certificates."""
import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from model import distances, path_loss, read_instance
from verify import check as check_route
from assignment import solve
from check_assignment import check as check_dual
from pair_bounds import lower_bound

SCOPE_SHA256 = "e40ec6b5f08d0d2d032e55921b5ed0d61051e14cf31b2ccc5e0611f002976cb0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_case(scope, case, previous, journal, deadline):
    tick = time.perf_counter()
    ip = ROOT / scope["instance"]
    assert case["instance"] == scope["instance"] and sha(ip) == scope["instance_sha256"]
    inherited = case["pareto_candidates"][0]
    cp = ROOT / inherited["path"]
    assert sha(cp) == inherited["sha256"]
    certificate = json.loads(cp.read_text())
    verified = check_route(ip, certificate)
    ins = read_instance(ip)
    ds = [distances(ins["grid"], goal) for goal in ins["goals"]]
    individual = [d[s] for d, s in zip(ds, ins["starts"])]
    losses = [path_loss(path) for path in certificate["paths"]]
    covered = {i for edge in scope["pairs"] for i in edge["agents"]}
    optimistic = sum(losses[i] - individual[i] for i in covered)
    price = {"individual_bound": sum(individual), "covered_excess_ceiling": optimistic,
             "hypothetical_bound_ceiling": sum(individual) + optimistic,
             "predecessor_fixed_bound": previous["fixed_pair_bound"]}
    assert price["hypothetical_bound_ceiling"] >= previous["fixed_pair_bound"]
    print(json.dumps({"case": case["case"], "pre_search_price": price}), flush=True)
    preprocess = time.perf_counter() - tick
    weights = [[0] * len(individual) for _ in individual]
    records = []
    for edge in scope["pairs"]:
        if time.perf_counter() >= deadline:
            raise TimeoutError("Wall deadline reached; completed pair records remain in the journal")
        i, j = edge["agents"]
        result = lower_bound(ins["grid"]["adj"], [ins["starts"][i], ins["starts"][j]],
                             [ins["goals"][i], ins["goals"][j]], [ds[i], ds[j]], 10000)
        elementary = individual[i] + individual[j]
        assert result["lower_bound"] is not None
        if result["status"] == "optimal":
            assert result["lower_bound"] >= elementary + 1
        pair_bound = max(elementary + 1, result["lower_bound"])
        assert pair_bound <= losses[i] + losses[j]
        weights[i][j] = weights[j][i] = pair_bound - elementary
        record = {"case": case["case"], "witness": edge, "individual_pair_bound": elementary,
                  "pair_lower_bound": pair_bound, "excess": pair_bound - elementary,
                  "inherited_pair_SOL_upper_bound": losses[i] + losses[j], "search": result}
        journal.write(json.dumps(record) + "\n")
        journal.flush()
        records.append(record)
    assignment_tick = time.perf_counter()
    dual = solve(weights)
    checked = check_dual(weights, dual)
    assignment_seconds = time.perf_counter() - assignment_tick
    fixed_extra = sum(weights[edge["agents"][0]][edge["agents"][1]] for edge in scope["fixed_matching"])
    assert sum(individual) + fixed_extra == previous["fixed_pair_bound"]
    assert checked["support_rounded_extra"] >= checked["component_rounded_extra"] >= fixed_extra
    extra = max(fixed_extra, checked["component_rounded_extra"], checked["support_rounded_extra"])
    total = sum(individual) + extra
    assert total <= min(verified["sol"], verified["soc"])
    return {"case": case["case"], "instance": scope["instance"], "instance_sha256": scope["instance_sha256"],
            "inherited": inherited, "verified_inherited": verified, "price": price,
            "individual_distance_bound": sum(individual), "pairs": records,
            "pair_count": len(records), "fixed_matching": scope["fixed_matching"],
            "fixed_pair_bound": sum(individual) + fixed_extra,
            "graph_component_bound": sum(individual) + checked["component_rounded_extra"],
            "witness_support_bound": sum(individual) + checked["support_rounded_extra"],
            "selected_bound": total, "gain_over_fixed_pairs": total - previous["fixed_pair_bound"],
            "remaining_SOL_bound_gap": verified["sol"] - total,
            "dual_certificate": dual, "pair_status_counts": dict(Counter(r["search"]["status"] for r in records)),
            "pops": sum(r["search"]["popped"] for r in records),
            "preprocess_seconds": preprocess, "assignment_and_check_seconds": assignment_seconds,
            "elapsed_seconds_including_checks": time.perf_counter() - tick}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = (PACKAGE / args.out).resolve()
    journal_path = output.with_suffix(".jsonl")
    if output.parent != PACKAGE or output.suffix != ".json" or output.exists() or journal_path.exists():
        parser.error("Use a new .json output in this package")
    assert sha(PACKAGE / "scope.json") == SCOPE_SHA256
    scope = json.loads((PACKAGE / "scope.json").read_text())
    archive = {c["case"]: c for c in json.loads((ROOT / "discover/incumbents.json").read_text())}
    previous = {c["case"]: c for c in json.loads((PACKAGE / "predecessor.json").read_text())["cases"]}
    cases = [c for c in scope["cases"] if not args.case or c["case"] == args.case]
    if not cases:
        parser.error("Unknown case")
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = min(x for x in (1024 * 1024**2, soft, hard) if x != resource.RLIM_INFINITY)
    resource.setrlimit(resource.RLIMIT_AS, (cap, hard))
    wall_cap = 600 if args.case else 3600
    tick, cpu = time.perf_counter(), time.process_time()
    sources = [Path(__file__), *(PACKAGE / name for name in
               ("assignment.py", "check_assignment.py", "pair_bounds.py", "pair_verifier.py", "scope.json",
                "predecessor.json", "protocol.json", "protocol-amendment-1.json")),
               ROOT / "src/model.py", ROOT / "src/verify.py", ROOT / "discover/incumbents.json"]
    report = {"started_at": datetime.now(timezone.utc).isoformat(),
              "base_commit": "37823dca1bea271510e3ed62205620466ec6f0f9",
              "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "source_sha256": {str(path.relative_to(ROOT)): sha(path) for path in sources},
              "python": sys.version, "platform": platform.platform(), "node_cap_per_pair": 10000,
              "address_space_cap_bytes": cap, "external_wall_cap_seconds": wall_cap,
              "exposed_inputs": True, "evidence_level": "author-checked", "cases": []}
    with journal_path.open("x") as journal:
        for entry in cases:
            row = run_case(entry, archive[entry["case"]], previous[entry["case"]], journal, tick + wall_cap)
            report["cases"].append(row)
            print(json.dumps({key: row[key] for key in
                              ("case", "fixed_pair_bound", "graph_component_bound", "witness_support_bound",
                               "selected_bound", "gain_over_fixed_pairs", "pair_count", "pops", "pair_status_counts")}), flush=True)
    report.update({"elapsed_seconds": time.perf_counter() - tick, "process_cpu_seconds": time.process_time() - cpu,
                   "peak_rss_kib_on_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "total_pops": sum(row["pops"] for row in report["cases"]),
                   "total_pairs": sum(row["pair_count"] for row in report["cases"])})
    assert report["total_pops"] <= 10000 * report["total_pairs"]
    if not args.case:
        assert len(report["cases"]) == 20 and report["total_pairs"] == 2785
    with output.open("x") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"saved": str(output), "cases": len(report["cases"]), "pairs": report["total_pairs"],
                      "pops": report["total_pops"], "elapsed_seconds": report["elapsed_seconds"]}))
