"""Execute the fixed development gate and conditional exposed evaluation."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from run_one import PACKAGE, ROOT, digest, source_paths


def package_bytes():
    return sum(p.stat().st_size for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def compare(rows, challenger):
    bykey = {(r["case"], r["trial"], r["method"]): r for r in rows}
    pairs = []
    for case, trial, method in bykey:
        if method != "arrival":
            continue
        baseline, other = bykey[case, trial, "arrival"], bykey[case, trial, challenger]
        a, b = baseline["candidate_metrics"], other["candidate_metrics"]
        pairs.append({"case": case, "trial": trial,
                      "SOL_delta": b["sol"] - a["sol"], "SOC_delta": b["soc"] - a["soc"],
                      "makespan_delta": b["makespan"] - a["makespan"]})
    passed = (sum(p["SOL_delta"] for p in pairs) < 0
              and sum(p["SOC_delta"] for p in pairs) <= 0
              and all(p["makespan_delta"] <= 0 for p in pairs))
    rejected = sum(r["rejections"]["completed_rejected"] for r in rows if r["method"] == challenger)
    regressing = sum(r["rejections"]["SOL_better_SOC_worse"] for r in rows if r["method"] == challenger)
    return {"gate_passed": passed, "pairs": pairs, "paired_runs": len(pairs),
            "SOL_delta_sum": sum(p["SOL_delta"] for p in pairs),
            "SOC_delta_sum": sum(p["SOC_delta"] for p in pairs),
            "makespan_regressions": sum(p["makespan_delta"] > 0 for p in pairs),
            "completed_rejected_challenger": rejected, "SOL_better_SOC_worse_challenger": regressing,
            "pivot_trigger": rejected >= 10 and 2 * regressing > rejected}


def run_batch(attempt, stage, panel, challenger, protocol, hashes):
    output = PACKAGE / f"{attempt}-{stage}.json"
    journal_path = output.with_suffix(".jsonl")
    if output.exists() or journal_path.exists():
        raise SystemExit("Choose a new attempt; never overwrite an earlier batch")
    cases = [c for c in protocol["cases"] if c["panel"] == panel]
    wall_limit = 1800 if panel == "development" else 3600
    cutoff = datetime.fromisoformat(protocol["resource_caps"]["overall_research_cutoff_utc"].replace("Z", "+00:00"))
    started = time.perf_counter()
    rows, events, complete = [], [], True
    with journal_path.open("x") as journal:
        for case_index, case in enumerate(cases):
            if not case["case"].replace("-", "").isalnum():
                raise ValueError("Unexpected case identifier")
            for seed in case["seeds"]:
                trial = seed["trial"]
                expected_seed = hashlib.sha256(bytes.fromhex(protocol["seed_hex"]) + case["case"].encode()
                                               + b":" + str(trial).encode()).digest()[:16]
                assert expected_seed.hex() == seed["seed_hex"]
                assert str(int.from_bytes(expected_seed, "big")) == seed["seed_decimal"]
                methods = ("arrival", challenger) if (case_index + trial) % 2 == 0 else (challenger, "arrival")
                for method in methods:
                    remaining = min(wall_limit - (time.perf_counter() - started),
                                    (cutoff - datetime.now(timezone.utc)).total_seconds())
                    if remaining <= 0 or package_bytes() > 500 * 1024**2:
                        events.append({"status": "stage_or_disk_cap", "case": case["case"], "trial": trial, "method": method})
                        complete = False
                        break
                    relative = f"runs/{attempt}-{stage}/{case['case']}-t{trial}-{method}"
                    command = [sys.executable, str(PACKAGE / "run_one.py"), "--case", case["case"],
                               "--trial", str(trial), "--method", method, "--out", relative]
                    tick = time.perf_counter()
                    try:
                        child = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                               timeout=min(600, remaining))
                        code, stdout, stderr = child.returncode, child.stdout, child.stderr
                    except subprocess.TimeoutExpired as error:
                        code = 124
                        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
                        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
                    event = {"case": case["case"], "trial": trial, "method": method,
                             "command": ["python", "research/sol-repair-ee542d9b/run_one.py", *command[2:]],
                             "returncode": code, "parent_observed_wall_seconds": time.perf_counter() - tick,
                             "stdout": stdout, "stderr": stderr,
                             "record": relative + "/run.json", "per_run_wall_cap_seconds": min(600, remaining)}
                    events.append(event)
                    journal.write(json.dumps(event) + "\n")
                    journal.flush()
                    print(json.dumps({k: event[k] for k in ("case", "trial", "method", "returncode", "parent_observed_wall_seconds")}), flush=True)
                    if code != 0:
                        complete = False
                        break
                    record = json.loads((PACKAGE / event["record"]).read_text())
                    assert record["verified"] and record["source_sha256"] == hashes
                    assert record["case"] == case["case"] and record["trial"] == trial and record["method"] == method
                    assert record["seed_hex"] == seed["seed_hex"]
                    rows.append(record)
                if not complete:
                    break
            if not complete:
                break
    expected = len(cases) * 3 * 2
    complete = complete and len(rows) == expected
    comparison = compare(rows, challenger) if complete else None
    report = {"attempt": attempt, "stage": stage, "panel": panel, "challenger": challenger,
              "complete": complete, "expected_runs": expected, "completed_runs": len(rows),
              "source_sha256": hashes, "rows": rows, "events": events, "comparison": comparison,
              "elapsed_seconds": time.perf_counter() - started,
              "total_search_pops": sum(r["budget"]["nodes_used"] for r in rows),
              "package_bytes_after_batch": package_bytes(), "exposed_inputs": True,
              "evidence_level": "author-checked", "recorded_at": datetime.now(timezone.utc).isoformat()}
    with output.open("x") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"saved": output.name, "complete": complete, "completed_runs": len(rows), "comparison": comparison}))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "evaluation"), required=True)
    parser.add_argument("--attempt", default="a1")
    args = parser.parse_args()
    if not args.attempt.replace("-", "").replace("_", "").isalnum():
        parser.error("Use a simple attempt identifier")
    protocol = json.loads((PACKAGE / "protocol.json").read_text())
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in source_paths()}
    selection_path = PACKAGE / f"{args.attempt}-development.json"
    if args.stage == "development":
        if selection_path.exists():
            parser.error("Choose a new attempt")
        primary = run_batch(args.attempt, "dev-primary", "development", "sol", protocol, hashes)
        selected, pivot = None, None
        if primary["complete"] and primary["comparison"]["gate_passed"]:
            selected = "sol"
        elif primary["complete"] and primary["comparison"]["pivot_trigger"]:
            pivot = run_batch(args.attempt, "dev-pivot", "development", "sol-deadline", protocol, hashes)
            if pivot["complete"] and pivot["comparison"]["gate_passed"]:
                selected = "sol-deadline"
        selection = {"selected": selected, "source_sha256": hashes,
                     "primary_batch": f"{args.attempt}-dev-primary.json",
                     "pivot_batch": f"{args.attempt}-dev-pivot.json" if pivot is not None else None,
                     "rule": protocol["development_gate"], "exposed_inputs": True,
                     "recorded_at": datetime.now(timezone.utc).isoformat()}
        selection_path.write_text(json.dumps(selection, indent=2) + "\n")
        print(json.dumps({"selection": selected, "saved": selection_path.name}))
    else:
        selection = json.loads(selection_path.read_text())
        if selection["selected"] not in ("sol", "sol-deadline") or selection["source_sha256"] != hashes:
            parser.error("No eligible frozen development winner with unchanged sources")
        run_batch(args.attempt, "evaluation", "evaluation", selection["selected"], protocol, hashes)
