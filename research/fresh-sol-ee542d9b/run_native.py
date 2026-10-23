"""Retain exactly one pinned 12-second LaCAM3 start per fixed fresh query."""
import argparse
import json
from pathlib import Path
import re
import resource
import subprocess
import sys
import time

from common import (PACKAGE, ROOT, check_limits, find_case, load_inputs, protocol,
                    remaining_seconds, run_process, save, sha, source_identity)
from model import metrics, read_instance, trim
from verify import check


def parse_certificate(text, instance, count, instance_sha256):
    matches = [(int(match[1]), match[2]) for line in text.splitlines()
               if (match := re.match(r"^(\d+):(.*)$", line))]
    assert matches and [tick for tick, _ in matches] == list(range(len(matches)))
    grid = read_instance(instance)["grid"]
    states = [[int(y) * grid["w"] + int(x) for x, y in re.findall(r"\((\d+),(\d+)\)", row)]
              for _, row in matches]
    assert all(len(state) == count for state in states)
    paths = [trim([state[agent] for state in states]) for agent in range(count)]
    certificate = {"instance_sha256": instance_sha256, "paths": paths,
                   "metrics": metrics(paths), "method": "pinned LaCAM3 defaults12s", "seed": 0}
    checked = check(instance, certificate)
    for key, field in (("sol", "sum_of_loss"), ("soc", "soc"), ("makespan", "makespan")):
        match = re.search(rf"^{field}=(\d+)$", text, re.M)
        assert match and int(match[1]) == checked[key]
    return certificate


def worker(case_id):
    started = time.perf_counter()
    plan = protocol()
    identity = source_identity(plan)
    check_limits(plan)
    case = find_case(plan, case_id)
    item = next(row for row in load_inputs()["cases"] if row["case"] == case_id)
    instance = ROOT / item["instance"]
    assert sha(instance) == item["instance_sha256"]
    assert sha(ROOT / item["scenario"]) == item["scenario_sha256"]
    native = plan["native"]
    binary = ROOT / native["binary"]
    assert sha(binary) == native["binary_sha256"]
    upstream = ROOT / "vendor/lacam3"
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=upstream, text=True).strip() == native["commit"]
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=upstream / "third_party/argparse",
                                   text=True).strip() == native["argparse_commit"]
    assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"],
                                       cwd=upstream, text=True).strip()
    destination = PACKAGE / "native" / case_id
    destination.mkdir(parents=True)
    raw_path = destination / "output.txt"
    command = [str(binary), "-m", str(ROOT / case["map"]), "-i", str(ROOT / item["scenario"]),
               "-N", str(case["agents"]), "-s", "0", "-t", "12", "-o", str(raw_path), "-v", "0"]
    execution = run_process(command, min(native["external_deadline_seconds"], remaining_seconds(plan)),
                            plan["caps"]["address_space_mib"])
    status, error, certificate = "failed", None, None
    if execution["status"] == "complete":
        try:
            text = raw_path.read_text()
            certificate = parse_certificate(text, instance, case["agents"], item["instance_sha256"])
            save(destination / "candidate.json", certificate)
            status = "verified"
        except Exception as failure:
            error = f"{type(failure).__name__}: {failure}"
    else:
        status = execution["status"]
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {**identity, "case": case_id, "status": status, "error": error,
              "input": item, "execution": execution, "binary_sha256": sha(binary),
              "candidate": str((destination / "candidate.json").relative_to(PACKAGE)) if status == "verified" else None,
              "candidate_sha256": sha(destination / "candidate.json") if status == "verified" else None,
              "metrics": certificate["metrics"] if status == "verified" else None,
              "raw_output_sha256": sha(raw_path) if raw_path.exists() else None,
              "worker_wall_seconds": time.perf_counter() - started,
              "worker_user_cpu_seconds": usage.ru_utime, "worker_system_cpu_seconds": usage.ru_stime,
              "worker_peak_rss_kib_on_linux": usage.ru_maxrss}
    save(destination / "run.json", result)
    print(json.dumps({"case": case_id, "status": status, "metrics": result["metrics"]}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if bool(args.case) == args.all:
        parser.error("Choose one case or --all")
    if args.case:
        worker(args.case)
        return
    plan = protocol()
    identity = source_identity(plan)
    started = time.perf_counter()
    rows = []
    if (PACKAGE / "native.json").exists():
        parser.error("Preserve the original native attempt")
    with (PACKAGE / "native-journal.jsonl").open("x") as journal:
        for case in plan["cases"]:
            check_limits(plan)
            command = [sys.executable, str(Path(__file__).resolve()), "--case", case["id"]]
            event = run_process(command, min(plan["caps"]["native_worker_wall_seconds"], remaining_seconds(plan)),
                                plan["caps"]["address_space_mib"])
            event["case"] = case["id"]
            path = PACKAGE / "native" / case["id"] / "run.json"
            if event["status"] == "complete" and path.exists():
                row = json.loads(path.read_text())
            else:
                row = {"case": case["id"], "status": "worker_" + event["status"], "candidate": None}
            event["record_sha256"] = sha(path) if path.exists() else None
            journal.write(json.dumps(event) + "\n")
            journal.flush()
            rows.append(row)
            print(json.dumps({"case": case["id"], "status": row["status"]}), flush=True)
    save(PACKAGE / "native.json", {**identity, "rows": rows, "wall_seconds": time.perf_counter() - started,
                                   "inputs_sha256": sha(PACKAGE / "inputs.json")})


if __name__ == "__main__":
    main()
