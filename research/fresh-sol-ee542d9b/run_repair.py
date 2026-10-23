"""Paired frozen repairs, with complete route traces and no output-based tuning."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import platform
import resource
import sys
import time

from common import (PACKAGE, ROOT, check_limits, find_case, protocol, remaining_seconds,
                    run_process, save, sha, source_identity)
from model import read_instance
from repair_round2 import run as arrival_run
from sol_repair import run as sol_run
from verify import check


def worker(case_id, trial, method):
    started = time.perf_counter()
    plan = protocol()
    identity = source_identity(plan)
    check_limits(plan)
    case = find_case(plan, case_id)
    if type(trial) is not int or trial not in range(3) or method not in ("arrival", "sol"):
        raise ValueError("Use a declared case/trial/method")
    native = json.loads((PACKAGE / "native" / case_id / "run.json").read_text())
    assert native["status"] == "verified"
    initial_path = PACKAGE / native["candidate"]
    assert sha(initial_path) == native["candidate_sha256"]
    initial = json.loads(initial_path.read_text())
    instance = ROOT / native["input"]["instance"]
    assert sha(instance) == native["input"]["instance_sha256"]
    initial_metrics = check(instance, initial)
    engine, variant = (arrival_run, "random4") if method == "arrival" else (sol_run, "sol")
    seed = case["repair_seeds"][trial]
    result = engine(read_instance(instance), initial["paths"], variant, int(seed["decimal"]),
                    node_budget=100000, attempts=96, agent_cap=10000)
    candidate = {"instance_sha256": initial["instance_sha256"], "paths": result["paths"],
                 "metrics": result["metrics"], "method": method, "seed_decimal": seed["decimal"]}
    checked = check(instance, candidate)
    for step in result["improvements"]:
        check(instance, {**candidate, "paths": step["paths"], "metrics": step["metrics"]})
    assert all(checked[key] <= initial_metrics[key] for key in ("sol", "soc", "makespan"))
    destination = PACKAGE / "runs" / f"{case_id}-t{trial}-{method}"
    destination.mkdir(parents=True)
    save(destination / "candidate.json", candidate)
    trace = destination / "trace.json.gz"
    with trace.open("xb") as handle:
        handle.write(gzip.compress(json.dumps(result, separators=(",", ":")).encode(), mtime=0))
    usage = resource.getrusage(resource.RUSAGE_SELF)
    record = {**identity, "case": case_id, "trial": trial, "method": method, "seed": seed,
              "instance": native["input"], "inherited_sha256": native["candidate_sha256"],
              "before": initial_metrics, "after": checked, "budget": result["budget"],
              "accepted_intermediates": len(result["improvements"]),
              "status_counts": dict(Counter(row["status"] for row in result["history"])),
              "preprocess_seconds": result["preprocess_seconds"], "core_wall_seconds": result["elapsed_seconds"],
              "worker_wall_seconds": time.perf_counter() - started,
              "worker_user_cpu_seconds": usage.ru_utime, "worker_system_cpu_seconds": usage.ru_stime,
              "worker_peak_rss_kib_on_linux": usage.ru_maxrss,
              "candidate": str((destination / "candidate.json").relative_to(PACKAGE)),
              "candidate_sha256": sha(destination / "candidate.json"),
              "trace": str(trace.relative_to(PACKAGE)), "trace_sha256": sha(trace),
              "python": sys.version, "platform": platform.platform(), "verified": True}
    save(destination / "run.json", record)
    print(json.dumps({"case": case_id, "trial": trial, "method": method, "after": checked}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--trial", type=int)
    parser.add_argument("--method", choices=("arrival", "sol"))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.case and not args.all and args.trial is not None and args.method:
        worker(args.case, args.trial, args.method)
        return
    if not args.all or args.case or args.trial is not None or args.method:
        parser.error("Choose --all or one complete case/trial/method")
    plan = protocol()
    identity = source_identity(plan)
    native = json.loads((PACKAGE / "native.json").read_text())
    rows, skipped, started = [], [], time.perf_counter()
    if (PACKAGE / "repair.json").exists():
        parser.error("Preserve the original repair attempt")
    with (PACKAGE / "repair-journal.jsonl").open("x") as journal:
        for index, case in enumerate(plan["cases"]):
            start = next(row for row in native["rows"] if row["case"] == case["id"])
            if start["status"] != "verified":
                skipped.append({"case": case["id"], "reason": "native_not_verified", "native_status": start["status"]})
                continue
            for trial in range(3):
                methods = ("arrival", "sol") if (index + trial) % 2 == 0 else ("sol", "arrival")
                for method in methods:
                    check_limits(plan)
                    remaining = min(plan["caps"]["phase_wall_seconds"] - (time.perf_counter() - started),
                                    remaining_seconds(plan))
                    if remaining <= 0:
                        raise TimeoutError("Repair phase cutoff reached; retain partial journal")
                    command = [sys.executable, str(Path(__file__).resolve()), "--case", case["id"],
                               "--trial", str(trial), "--method", method]
                    event = run_process(command, min(plan["caps"]["repair_worker_wall_seconds"], remaining),
                                        plan["caps"]["address_space_mib"])
                    event.update(case=case["id"], trial=trial, method=method)
                    path = PACKAGE / "runs" / f"{case['id']}-t{trial}-{method}" / "run.json"
                    event["record_sha256"] = sha(path) if path.exists() else None
                    journal.write(json.dumps(event) + "\n")
                    journal.flush()
                    if event["status"] != "complete" or not path.exists():
                        raise RuntimeError("Repair worker failed; retain partial journal without replacing it")
                    row = json.loads(path.read_text())
                    rows.append(row)
                    print(json.dumps({"case": case["id"], "trial": trial, "method": method, "after": row["after"]}), flush=True)
    save(PACKAGE / "repair.json", {**identity, "rows": rows, "skipped": skipped,
                                   "native_sha256": sha(PACKAGE / "native.json"),
                                   "wall_seconds": time.perf_counter() - started,
                                   "evidence_level": "author-checked fixed fresh within-map panel"})


if __name__ == "__main__":
    main()
