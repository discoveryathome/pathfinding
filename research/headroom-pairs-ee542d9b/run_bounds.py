"""Run the predeclared fixed-pair lower-bound experiment; never overwrite output."""
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
sys.path.insert(0, str(ROOT / "tools"))
from headroom import bound
from model import distances, path_loss, read_instance
from pair_bounds import lower_bound
from verify import check


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_case(case, pair_limit, deadline, journal):
    started = time.perf_counter()
    ip = ROOT / case["instance"]
    source = case["pareto_candidates"][0]
    certificate_path = ROOT / source["path"]
    assert digest(certificate_path) == source["sha256"]
    certificate = json.loads(certificate_path.read_text())
    verified = check(ip, certificate)
    ins = read_instance(ip)
    old = bound(ins)
    ds = [distances(ins["grid"], goal) for goal in ins["goals"]]
    individual = [d[start] for d, start in zip(ds, ins["starts"])]
    used_agents = [i for witness in old["disjoint_pair_witnesses"] for i in witness["agents"]]
    assert len(set(used_agents)) == len(used_agents)
    assert sum(individual) == old["individual_distance_bound"]
    witnesses = old["disjoint_pair_witnesses"][:pair_limit]
    records = []
    for witness in witnesses:
        if time.perf_counter() >= deadline:
            break
        i, j = witness["agents"]
        elementary = individual[i] + individual[j]
        upper = path_loss(certificate["paths"][i]) + path_loss(certificate["paths"][j])
        result = lower_bound(ins["grid"]["adj"], [ins["starts"][i], ins["starts"][j]],
                             [ins["goals"][i], ins["goals"][j]], [ds[i], ds[j]], 10000)
        assert result["lower_bound"] is not None, "Valid global witness has an infeasible pair"
        combined = max(elementary + 1, result["lower_bound"])
        assert elementary + 1 <= combined <= upper
        record = {"case": case["case"], "witness": witness,
                  "individual_pair_bound": elementary, "inherited_pair_SOL_upper_bound": upper,
                  "combined_pair_bound": combined, "search": result}
        journal.write(json.dumps(record) + "\n")
        journal.flush()
        records.append(record)
    strengthened = old["pair_conflict_bound"] + sum(
        r["combined_pair_bound"] - r["individual_pair_bound"] - 1 for r in records)
    assert old["pair_conflict_bound"] <= strengthened <= min(verified["sol"], verified["soc"])
    optimistic_extra = sum(path_loss(certificate["paths"][i]) - individual[i] for i in used_agents)
    return {"case": case["case"], "instance": case["instance"], "instance_sha256": digest(ip),
            "map": ins["map"], "map_sha256": ins["map_sha256"], "inherited": source,
            "verified_inherited": verified, "individual_distance_bound": sum(individual),
            "old_pair_bound": old["pair_conflict_bound"], "new_pair_bound": strengthened,
            "bound_gain": strengthened - old["pair_conflict_bound"],
            "old_SOL_gap": verified["sol"] - old["pair_conflict_bound"],
            "new_SOL_gap": verified["sol"] - strengthened,
            "optimistic_fixed_pair_extra_upper_bound": optimistic_extra,
            "fixed_disjoint_pairs": len(old["disjoint_pair_witnesses"]),
            "selected_pairs": len(witnesses), "completed_pairs": len(records),
            "all_selected_pairs_completed": len(records) == len(witnesses),
            "nodes_popped": sum(r["search"]["popped"] for r in records),
            "status_counts": dict(Counter(r["search"]["status"] for r in records)),
            "pair_results": records, "elapsed_seconds_including_checks": time.perf_counter() - started}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--limit-pairs", type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.limit_pairs is not None and (not args.case or args.limit_pairs < 1):
        parser.error("A positive --limit-pairs requires one --case")
    output = (ROOT / args.out).resolve()
    journal_path = output.with_suffix(".jsonl")
    if (output.suffix != ".json" or not output.is_relative_to(PACKAGE) or output.exists() or journal_path.exists()
            or not output.parent.is_dir()):
        parser.error("Use a new output file inside this research package")
    cases = json.loads((ROOT / "discover/incumbents.json").read_text())
    if args.case:
        cases = [c for c in cases if c["case"] == args.case]
        if not cases:
            parser.error("Unknown case")
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    memory_cap = min(x for x in (1024 * 1024**2, soft, hard) if x != resource.RLIM_INFINITY)
    resource.setrlimit(resource.RLIMIT_AS, (memory_cap, hard))
    tick = time.perf_counter()
    cpu = time.process_time()
    seconds = 180 if args.limit_pairs else 1800
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "base_commit": "37823dca1bea271510e3ed62205620466ec6f0f9",
              "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in
                                [Path(__file__), PACKAGE / "pair_bounds.py", PACKAGE / "protocol.json",
                                 ROOT / "tools/headroom.py", ROOT / "src/model.py", ROOT / "src/verify.py",
                                 ROOT / "discover/incumbents.json"]},
              "python": sys.version, "platform": platform.platform(), "node_limit_per_pair": 10000,
              "wall_cap_seconds": seconds, "effective_address_space_cap_bytes": memory_cap,
              "exposed_inputs": True, "evidence_level": "author-checked", "cases": []}
    with journal_path.open("x") as journal:
        for case in cases:
            if time.perf_counter() - tick >= seconds:
                break
            row = run_case(case, args.limit_pairs, tick + seconds, journal)
            report["cases"].append(row)
            print(json.dumps({k: row[k] for k in ("case", "old_pair_bound", "new_pair_bound", "bound_gain", "completed_pairs", "nodes_popped", "status_counts")}), flush=True)
    report.update({"elapsed_seconds": time.perf_counter() - tick,
                   "process_cpu_seconds": time.process_time() - cpu,
                   "peak_rss_kib_on_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "all_cases_completed": len(report["cases"]) == len(cases)
                   and all(r["all_selected_pairs_completed"] for r in report["cases"]),
                   "total_popped": sum(r["nodes_popped"] for r in report["cases"])})
    assert all(r["nodes_popped"] <= 10000 * r["completed_pairs"] for r in report["cases"])
    if report["all_cases_completed"] and not args.case:
        assert len(report["cases"]) == 20
        assert sum(r["completed_pairs"] for r in report["cases"]) == 521
        assert report["total_popped"] <= 5210000
    with output.open("x") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"saved": str(output), "all_cases_completed": report["all_cases_completed"],
                      "total_popped": report["total_popped"], "elapsed_seconds": report["elapsed_seconds"]}))
