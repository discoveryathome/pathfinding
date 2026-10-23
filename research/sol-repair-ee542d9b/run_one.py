"""Run one frozen paired experiment and retain all routes, attempts and costs."""
import argparse
import gzip
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
from model import read_instance
from repair_round2 import run as arrival_run
from sol_repair import run as sol_run
from verify import check


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_paths():
    return [*(PACKAGE / name for name in ("sol_repair.py", "run_one.py", "run_study.py", "protocol.json",
                                         "inputs/maze-start.json")),
            *(ROOT / name for name in ("src/model.py", "src/repair.py", "src/repair_round2.py",
                                      "src/verify.py", "discover/incumbents.json"))]


def rejection_summary(history):
    rejected = [r for r in history if r["status"] == "complete" and not r["accepted"]]
    sol_better_soc_worse = sum(r["proposed"]["sol"] < r["before"]["sol"]
                               and r["proposed"]["soc"] > r["before"]["soc"] for r in rejected)
    return {"completed_rejected": len(rejected), "SOL_better_SOC_worse": sol_better_soc_worse,
            "guard_regressions": {key: sum(r["proposed"][key] > r["before"][key] for r in rejected)
                                  for key in ("sol", "soc", "makespan")}}


if __name__ == "__main__":
    started = time.perf_counter()
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--trial", type=int, required=True)
    parser.add_argument("--method", choices=("arrival", "sol", "sol-deadline"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    protocol = json.loads((PACKAGE / "protocol.json").read_text())
    case = next((c for c in protocol["cases"] if c["case"] == args.case), None)
    if case is None or args.trial not in range(3):
        parser.error("Use a predeclared case/trial")
    plan = case["seeds"][args.trial]
    seed = int(plan["seed_decimal"])
    assert seed == int(plan["seed_hex"], 16)
    destination = (PACKAGE / args.out).resolve()
    if not destination.is_relative_to(PACKAGE / "runs") or destination.exists():
        parser.error("Use a new runs/<stage>/<case-trial-method> output")
    paths = source_paths()
    relative = [str(p.relative_to(ROOT)) for p in paths]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    subprocess.run(["git", "ls-files", "--error-unmatch", "--", *relative], cwd=ROOT,
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "diff", "--quiet", commit, "--", *relative], cwd=ROOT, check=True)
    assert digest(ROOT / "discover/incumbents.json") == protocol["archive_sha256"]
    ip, source = ROOT / case["instance"], ROOT / case["start"]["path"]
    assert digest(ip) == case["instance_sha256"] and digest(source) == case["start"]["sha256"]
    initial = json.loads(source.read_text())
    initial_check = check(ip, initial)
    ins = read_instance(ip)
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    memory_cap = min(x for x in (1024 * 1024**2, soft, hard) if x != resource.RLIM_INFINITY)
    resource.setrlimit(resource.RLIMIT_AS, (memory_cap, hard))
    destination.mkdir(parents=True)
    engine = arrival_run if args.method == "arrival" else sol_run
    variant = "random4" if args.method == "arrival" else args.method
    result = engine(ins, initial["paths"], variant, seed, node_budget=100000, attempts=96, agent_cap=10000)
    certificate = {"instance_sha256": case["instance_sha256"], "paths": result["paths"],
                   "metrics": result["metrics"], "method": args.method,
                   "seed_decimal": plan["seed_decimal"], "seed_hex": plan["seed_hex"]}
    candidate_path = destination / "candidate.json"
    candidate_path.write_text(json.dumps(certificate, separators=(",", ":")) + "\n")
    trace_path = destination / "trace.json.gz"
    trace_path.write_bytes(gzip.compress(json.dumps(result, separators=(",", ":")).encode(), mtime=0))
    verify_tick = time.perf_counter()
    candidate_check = check(ip, certificate)
    for item in result["improvements"]:
        check(ip, {**certificate, "paths": item["paths"], "metrics": item["metrics"]})
    assert all(candidate_check[key] <= initial_check[key] for key in ("sol", "soc", "makespan"))
    verification_seconds = time.perf_counter() - verify_tick
    usage = resource.getrusage(resource.RUSAGE_SELF)
    record = {"case": args.case, "trial": args.trial, "method": args.method, "panel": case["panel"],
              "seed_hex": plan["seed_hex"], "seed_decimal": plan["seed_decimal"],
              "base_commit": protocol["base_commit"], "code_commit": commit,
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in paths},
              "instance": case["instance"], "instance_sha256": case["instance_sha256"], "inherited": case["start"],
              "initial_metrics": initial_check, "candidate_metrics": candidate_check,
              "budget": result["budget"], "accepted_routes_checked": len(result["improvements"]),
              "status_counts": dict(Counter(row["status"] for row in result["history"])),
              "rejections": rejection_summary(result["history"]),
              "core_elapsed_seconds": result["elapsed_seconds"], "preprocess_seconds": result["preprocess_seconds"],
              "verification_seconds": verification_seconds, "worker_elapsed_seconds": time.perf_counter() - started,
              "worker_user_cpu_seconds": usage.ru_utime, "worker_system_cpu_seconds": usage.ru_stime,
              "worker_peak_rss_kib_on_linux": usage.ru_maxrss, "address_space_cap_bytes": memory_cap,
              "candidate": str(candidate_path.relative_to(PACKAGE)), "candidate_sha256": digest(candidate_path),
              "trace": str(trace_path.relative_to(PACKAGE)), "trace_sha256": digest(trace_path),
              "python": sys.version, "platform": platform.platform(), "verified": True,
              "recorded_at": datetime.now(timezone.utc).isoformat(), "evidence_level": "author-checked"}
    (destination / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({key: record[key] for key in ("case", "trial", "method", "candidate_metrics", "budget",
                                                   "accepted_routes_checked", "core_elapsed_seconds", "worker_elapsed_seconds")}))
