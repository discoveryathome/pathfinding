"""Recompute cohort, query draws and route evidence without importing producers."""
import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from verify import check

MAPS = ("maze-32-32-4", "room-32-32-4", "random-32-32-20")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def required_sources():
    prefix = str(PACKAGE.relative_to(ROOT)) + "/"
    return {prefix + name for name in ("common.py", "inputs.py", "run_native.py", "run_repair.py",
                                       "sol_repair.py", "protocol.json")} | {
        "src/model.py", "src/repair.py", "src/repair_round2.py", "src/verify.py"} | {
        f"data/maps/{name}.map" for name in MAPS}


@lru_cache(maxsize=None)
def committed_sources(commit):
    if type(commit) is not str or not re.fullmatch("[0-9a-f]{40}", commit):
        raise ValueError("Require an exact commit identity")
    kind = subprocess.check_output(["git", "cat-file", "-t", commit], cwd=ROOT,
                                   text=True, stderr=subprocess.DEVNULL).strip()
    if kind != "commit":
        raise ValueError("Source object is not a commit")
    return {path: hashlib.sha256(subprocess.check_output(["git", "show", commit + ":" + path],
            cwd=ROOT, stderr=subprocess.DEVNULL)).hexdigest() for path in sorted(required_sources())}


def validate_sources(record, expected=None):
    manifest = record["source_sha256"]
    if not isinstance(manifest, dict) or set(manifest) != required_sources():
        raise ValueError("Require the complete source manifest")
    try:
        actual = committed_sources(record["code_commit"])
    except subprocess.CalledProcessError as error:
        raise ValueError("Fetch the retained source commit history") from error
    if manifest != actual or (expected is not None and manifest != expected):
        raise ValueError("Source binding changed")
    if sha(ROOT / "src/verify.py") != manifest["src/verify.py"]:
        raise ValueError("The current standalone checker differs from the recorded checker")
    return manifest


def cohort(rows, expected, fields):
    keys = [tuple(row[field] for field in fields) for row in rows]
    if (len(keys) != len(expected) or len(set(keys)) != len(keys) or set(keys) != set(expected)
            or any("trial" in row and type(row["trial"]) is not int for row in rows)):
        raise ValueError("Wrong canonical cohort or aliased trial")


def artifact(relative, area):
    path = (PACKAGE / relative).resolve()
    if not path.is_relative_to((PACKAGE / area).resolve()):
        raise ValueError("Artifact escaped its declared area")
    return path


def shape(metrics):
    assert set(metrics) == {"sol", "soc", "makespan"}
    assert all(type(value) is int and value >= 0 for value in metrics.values())


def command_root(command, worker):
    path = Path(command[1])
    if not path.is_absolute() or ".." in path.parts or len(path.parents) < 3:
        raise ValueError("Require an absolute recorded worker path")
    recorded = path.parents[2]
    if path != recorded / PACKAGE.relative_to(ROOT) / worker:
        raise ValueError("Recorded worker is outside the declared package")
    return recorded


def trim(path):
    result = list(path)
    while len(result) > 1 and result[-1] == result[-2]:
        result.pop()
    return result


def canonical_draw(case, donation):
    lines = (ROOT / case["map"]).read_text().splitlines()
    height, width = int(lines[1].split()[1]), int(lines[2].split()[1])
    assert (height, width) == (32, 32)
    cells = {y * width + x for y, row in enumerate(lines[4:]) for x, value in enumerate(row) if value in ".GS"}
    edges = {cell: [other for other in (cell - width, cell + width, cell - 1, cell + 1)
                    if other in cells and abs(cell % width - other % width) + abs(cell // width - other // width) == 1]
             for cell in cells}
    remaining, components = set(cells), []
    while remaining:
        seed = min(remaining)
        stack, component = [seed], set()
        remaining.remove(seed)
        while stack:
            cell = stack.pop()
            component.add(cell)
            for other in edges[cell]:
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
        components.append(sorted(component))
    largest = sorted(components, key=lambda group: (-len(group), group[0]))[0]
    raw = hashlib.sha256(donation + b":fresh-v1:" + case["id"].encode()).digest()[:16]
    assert raw.hex() == case["draw_seed_hex"] and str(int.from_bytes(raw, "big")) == case["draw_seed_decimal"]
    rng = random.Random(int.from_bytes(raw, "big"))
    return rng.sample(largest, case["agents"]), rng.sample(largest, case["agents"]), edges


def verify_inputs(plan, manifest):
    cohort(plan["cases"], [(f"{name}-fresh{query}-n{count}",) for name in MAPS
                            for count in (64, 128) for query in (0, 1)], ("id",))
    rows = load(PACKAGE / "inputs.json")
    validate_sources(rows, manifest)
    assert rows["protocol_sha256"] == sha(PACKAGE / "protocol.json") and rows["generated_after_source_commit"] is True
    cohort(rows["cases"], [(case["id"],) for case in plan["cases"]], ("case",))
    byid = {row["case"]: row for row in rows["cases"]}
    donation = bytes.fromhex(plan["seed_hex"])
    for case in plan["cases"]:
        name, suffix = case["id"].split("-fresh")
        query, count = suffix.split("-n")
        assert case["map"] == f"data/maps/{name}.map" and case["query"] == int(query)
        assert type(case["agents"]) is int and case["agents"] == int(count)
        assert sha(ROOT / case["map"]) == case["map_sha256"] == manifest[case["map"]]
        row = byid[case["id"]]
        expected = str((PACKAGE / "inputs" / (case["id"] + ".json")).relative_to(ROOT))
        assert row["instance"] == expected
        path = ROOT / expected
        assert sha(path) == row["instance_sha256"]
        instance = load(path)
        assert instance["id"] == case["id"] and instance["map"] == case["map"]
        assert instance["map_sha256"] == case["map_sha256"]
        starts, goals, edges = canonical_draw(case, donation)
        assert instance["starts"] == starts and instance["goals"] == goals
        scenario = PACKAGE / "inputs" / (case["id"] + ".scen")
        assert row["scenario"] == instance["scenario"] == str(scenario.relative_to(ROOT))
        assert sha(scenario) == row["scenario_sha256"] == instance["scenario_sha256"]
        actual_lines = scenario.read_text().splitlines()
        assert actual_lines[0] == "version 1" and len(actual_lines) == len(starts) + 1
        for start, goal, line in zip(starts, goals, actual_lines[1:]):
            distances, frontier = {goal: 0}, [goal]
            for cell in frontier:
                for other in edges[cell]:
                    if other not in distances:
                        distances[other] = distances[cell] + 1
                        frontier.append(other)
            assert line.split() == list(map(str, (0, Path(case["map"]).name, 32, 32,
                start % 32, start // 32, goal % 32, goal // 32, distances[start])))
        assert [seed["trial"] for seed in case["repair_seeds"]] == [0, 1, 2]
        for trial, seed in enumerate(case["repair_seeds"]):
            raw = hashlib.sha256(donation + b":repair-fresh-v1:" + case["id"].encode()
                                 + b":" + str(trial).encode()).digest()[:16]
            assert seed["hex"] == raw.hex() and seed["decimal"] == str(int.from_bytes(raw, "big"))
    return byid


def audit_trace(trace, initial, candidate, instance):
    budget, history = trace["budget"], trace["history"]
    assert set(budget) == {"node_limit", "nodes_used", "attempt_limit", "attempts_used", "per_agent_limit"}
    assert all(type(value) is int for value in budget.values())
    assert (budget["node_limit"], budget["attempt_limit"], budget["per_agent_limit"]) == (100000, 96, 10000)
    assert budget["attempts_used"] == len(history) <= 96
    assert budget["nodes_used"] == sum(row["popped"] for row in history) <= 100000
    assert len(history) == 96 or budget["nodes_used"] == 100000, "Incomplete search history"
    improvements = {row["attempt"]: row for row in trace["improvements"]}
    assert len(improvements) == len(trace["improvements"])
    assert all(type(number) is int for number in improvements)
    paths, before, used = [trim(path) for path in initial["paths"]], initial["metrics"], 0
    shape(before)
    for number, row in enumerate(history):
        shape(row["before"])
        shape(row["proposed"])
        assert type(row["attempt"]) is int and row["attempt"] == number and row["before"] == before
        group = row["agents"]
        assert len(group) == min(4, len(paths)) and len(set(group)) == len(group)
        assert all(type(agent) is int and 0 <= agent < len(paths) for agent in group)
        assert type(row["popped"]) is int and 0 <= row["popped"] <= min(len(group) * 10000, 100000 - used)
        used += row["popped"]
        assert row["status"] in {"complete", "budget", "exhausted", "blocked_start", "total_budget"}
        after = row["proposed"]
        accepted = (row["status"] == "complete" and all(after[key] <= before[key] for key in before)
                    and (after["sol"] < before["sol"] or after["soc"] < before["soc"]))
        assert type(row["accepted"]) is bool and row["accepted"] == accepted == (number in improvements)
        if row["status"] != "complete":
            assert after == before
        if accepted:
            item = improvements[number]
            assert item["metrics"] == after
            assert all(path == item["paths"][agent] for agent, path in enumerate(paths) if agent not in group)
            check(instance, {**candidate, "paths": item["paths"], "metrics": after})
            paths, before = item["paths"], after
    assert trace["paths"] == candidate["paths"] == paths
    assert trace["metrics"] == candidate["metrics"] == before
    return len(improvements), [row["agents"] for row in history]


def verify_native(plan, manifest, inputs):
    report = load(PACKAGE / "native.json")
    validate_sources(report, manifest)
    assert report["inputs_sha256"] == sha(PACKAGE / "inputs.json")
    journal = [json.loads(line) for line in (PACKAGE / "native-journal.jsonl").read_text().splitlines()]
    assert [event["case"] for event in journal] == [case["id"] for case in plan["cases"]]
    cohort(report["rows"], [(case["id"],) for case in plan["cases"]], ("case",))
    native = {row["case"]: row for row in report["rows"]}
    for case, event in zip(plan["cases"], journal):
        row, cid = native[case["id"]], case["id"]
        recorded_root = command_root(event["command"], "run_native.py")
        assert event["command"][2:] == ["--case", cid]
        assert event["address_space_mib"] == 1024 and 0 < event["external_timeout_seconds"] <= 60
        assert event["process_group_owned"] is True
        record = PACKAGE / "native" / cid / "run.json"
        if not record.exists():
            assert row["status"] != "verified" and row["candidate"] is None and event["record_sha256"] is None
            continue
        assert sha(record) == event["record_sha256"] and load(record) == row
        validate_sources(row, manifest)
        assert row["status"] in {"verified", "failed", "timeout"}
        assert row["input"] == inputs[cid] and row["binary_sha256"] == plan["native"]["binary_sha256"]
        raw = PACKAGE / "native" / cid / "output.txt"
        assert (sha(raw) if raw.exists() else None) == row["raw_output_sha256"]
        assert row["execution"]["address_space_mib"] == 1024 and 0 < row["execution"]["external_timeout_seconds"] <= 45
        assert row["execution"]["process_group_owned"] is False
        recorded_raw = recorded_root / PACKAGE.relative_to(ROOT) / "native" / cid / "output.txt"
        expected_command = [str(recorded_root / plan["native"]["binary"]), "-m", str(recorded_root / case["map"]),
            "-i", str(recorded_root / inputs[cid]["scenario"]), "-N", str(case["agents"]), "-s", "0", "-t", "12", "-o", str(recorded_raw), "-v", "0"]
        assert row["execution"]["command"] == expected_command
        if row["status"] != "verified":
            assert row["candidate"] is None and row["candidate_sha256"] is None
            continue
        assert event["status"] == row["execution"]["status"] == "complete"
        assert event["returncode"] == row["execution"]["returncode"] == 0
        assert row["candidate"] == f"native/{cid}/candidate.json"
        certificate_path = artifact(row["candidate"], "native")
        assert sha(certificate_path) == row["candidate_sha256"]
        certificate = load(certificate_path)
        shape(certificate["metrics"])
        checked = check(ROOT / inputs[cid]["instance"], certificate)
        assert {key: checked[key] for key in ("sol", "soc", "makespan")} == row["metrics"]
        states = []
        coordinate = r"\((-?\d+),(-?\d+)\)"
        for line in raw.read_text().splitlines():
            if not (match := re.match(r"^(\d+):(.*)$", line)):
                continue
            points = [(int(x), int(y)) for x, y in re.findall(coordinate, match[2])]
            assert all(0 <= x < 32 and 0 <= y < 32 for x, y in points)
            assert not re.sub(coordinate, "", match[2]).strip(" ,\t")
            states.append((int(match[1]), [y * 32 + x for x, y in points]))
        assert [tick for tick, _ in states] == list(range(len(states)))
        assert all(len(state) == case["agents"] for _, state in states)
        assert certificate["paths"] == [trim([state[agent] for _, state in states]) for agent in range(case["agents"])]
        for key, field in (("sol", "sum_of_loss"), ("soc", "soc"), ("makespan", "makespan")):
            assert int(re.search(rf"^{field}=(\d+)$", raw.read_text(), re.M)[1]) == row["metrics"][key]
    return native


def verify_repairs(plan, manifest, inputs, native):
    report = load(PACKAGE / "repair.json")
    validate_sources(report, manifest)
    assert report["native_sha256"] == sha(PACKAGE / "native.json")
    eligible = [case for case in plan["cases"] if native[case["id"]]["status"] == "verified"]
    assert report["skipped"] == [{"case": case["id"], "reason": "native_not_verified", "native_status": native[case["id"]]["status"]}
                                  for case in plan["cases"] if case not in eligible]
    expected = {(case["id"], trial, method) for case in eligible for trial in range(3) for method in ("arrival", "sol")}
    cohort(report["rows"], expected, ("case", "trial", "method"))
    journal = [json.loads(line) for line in (PACKAGE / "repair-journal.jsonl").read_text().splitlines()]
    attempted = {(row["case"], row["trial"], row["method"]) for row in report["rows"] if row["status"] != "not_attempted"}
    cohort(journal, attempted, ("case", "trial", "method"))
    order = [(case["id"], trial, method) for index, case in enumerate(plan["cases"]) if case in eligible
             for trial in range(3) for method in (("arrival", "sol") if (index + trial) % 2 == 0 else ("sol", "arrival"))]
    assert [(e["case"], e["trial"], e["method"]) for e in journal] == order[:len(journal)]
    assert [(r["case"], r["trial"], r["method"]) for r in report["rows"] if r["status"] == "not_attempted"] == order[len(journal):]
    assert report["all_jobs_attempted"] == (len(journal) == len(order))
    bykey = {(row["case"], row["trial"], row["method"]): row for row in report["rows"]}
    cases, groups, checked = {case["id"]: case for case in eligible}, {}, 0
    for event in journal:
        key = event["case"], event["trial"], event["method"]
        row, case = bykey[key], cases[key[0]]
        directory = PACKAGE / "runs" / f"{key[0]}-t{key[1]}-{key[2]}"
        command_root(event["command"], "run_repair.py")
        assert event["command"][2:] == ["--case", key[0], "--trial", str(key[1]), "--method", key[2]]
        assert event["address_space_mib"] == 1024 and 0 < event["external_timeout_seconds"] <= 600
        assert event["process_group_owned"] is True
        if row["verified"] is False:
            assert row["status"] in {"worker_failed", "worker_timeout", "invalid_record"}
            assert row["artifacts"] == event["failure_artifacts"] == {
                str(item.relative_to(PACKAGE)): sha(item) for item in directory.glob("*") if item.is_file()}
            assert event["record_sha256"] == (sha(directory / "run.json") if (directory / "run.json").exists() else None)
            if (directory / "request.json").exists():
                request = load(directory / "request.json")
                validate_sources(request, manifest)
                assert (request["case"], request["trial"], request["method"]) == key
                assert request["seed"] == case["repair_seeds"][key[1]] and request["instance"] == inputs[key[0]]
            continue
        validate_sources(row, manifest)
        assert row["verified"] is True and row["status"] == "verified"
        assert row["seed"] == case["repair_seeds"][key[1]]
        assert row["instance"] == inputs[key[0]] and row["inherited_sha256"] == native[key[0]]["candidate_sha256"]
        assert load(directory / "run.json") == row and sha(directory / "run.json") == event["record_sha256"]
        assert row["candidate"] == str((directory / "candidate.json").relative_to(PACKAGE))
        assert row["trace"] == str((directory / "trace.json.gz").relative_to(PACKAGE))
        request = load(directory / "request.json")
        assert request == {key: row[key] for key in ("code_commit", "source_sha256", "case", "trial", "method",
                                                    "seed", "instance", "inherited_sha256")}
        assert not (directory / "failure.json").exists()
        assert event["status"] == "complete" and event["returncode"] == 0
        certificate_path, trace_path = artifact(row["candidate"], "runs"), artifact(row["trace"], "runs")
        assert sha(certificate_path) == row["candidate_sha256"] and sha(trace_path) == row["trace_sha256"]
        candidate, trace = load(certificate_path), json.loads(gzip.decompress(trace_path.read_bytes()))
        initial = load(artifact(native[key[0]]["candidate"], "native"))
        instance = ROOT / inputs[key[0]]["instance"]
        shape(candidate["metrics"])
        assert check(instance, candidate) == row["after"] and check(instance, initial) == row["before"]
        assert trace["seed"] == row["seed"]["decimal"] and type(trace["seed"]) is str
        assert trace["variant"] == ("random4" if key[2] == "arrival" else "sol")
        count, sequence = audit_trace(trace, initial, candidate, instance)
        assert row["accepted_intermediates"] == count and trace["budget"] == row["budget"]
        assert row["status_counts"] == dict(Counter(step["status"] for step in trace["history"]))
        assert row["preprocess_seconds"] >= 0 and row["core_wall_seconds"] >= 0
        assert row["engine_wall_seconds"] == trace["elapsed_seconds"]
        assert row["preprocess_seconds"] == trace["preprocess_seconds"]
        assert abs(row["engine_wall_seconds"] - row["core_wall_seconds"] - row["preprocess_seconds"]) < 1e-9
        assert all(row["after"][metric] <= row["before"][metric] for metric in ("sol", "soc", "makespan"))
        checked += count
        groups[key] = sequence
    pairs = []
    incomplete = []
    for case in eligible:
        for trial in range(3):
            left, right = (case["id"], trial, "arrival"), (case["id"], trial, "sol")
            a, b = bykey[left], bykey[right]
            if a["verified"] is not True or b["verified"] is not True:
                incomplete.append({"case": case["id"], "trial": trial, "arrival_status": a["status"], "sol_status": b["status"]})
                continue
            prefix = min(len(groups[left]), len(groups[right]))
            assert groups[left][:prefix] == groups[right][:prefix]
            pairs.append({"case": case["id"], "trial": trial,
                          **{metric + "_delta": b["after"][metric] - a["after"][metric] for metric in ("sol", "soc", "makespan")}})
    successful = [row for row in report["rows"] if row["verified"] is True]
    return successful, checked, pairs, {"planned_jobs": len(order), "attempted_jobs": len(journal),
        "failed_or_unattempted": dict(Counter(row["status"] for row in report["rows"] if row["verified"] is False)),
        "incomplete_pairs": incomplete}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="verification.json")
    args = parser.parse_args()
    output = PACKAGE / args.out
    if Path(args.out).name != args.out or output.exists():
        parser.error("Use an unused filename directly inside the package")
    started = time.perf_counter()
    plan, inputs_record = load(PACKAGE / "protocol.json"), load(PACKAGE / "inputs.json")
    manifest = validate_sources(inputs_record)
    prefix = str(PACKAGE.relative_to(ROOT)) + "/"
    assert sha(PACKAGE / "protocol.json") == manifest[prefix + "protocol.json"]
    assert sha(PACKAGE / "sol_repair.py") == plan["policy_sha256"] == manifest[prefix + "sol_repair.py"]
    inputs = verify_inputs(plan, manifest)
    native = verify_native(plan, manifest, inputs)
    rows, intermediates, pairs, coverage = verify_repairs(plan, manifest, inputs, native)
    assert not any(name in sys.modules for name in ("sol_repair", "repair", "repair_round2"))
    resources = {method: {field: sum(row[field] for row in rows if row["method"] == method)
                         for field in ("core_wall_seconds", "engine_wall_seconds", "preprocess_seconds", "worker_wall_seconds",
                                       "worker_user_cpu_seconds", "worker_system_cpu_seconds")}
                 for method in ("arrival", "sol")}
    result = {"verified": True, "evidence_level": "author-checked separate audit", "optimizer_imports": False,
              "native_status_counts": dict(Counter(row["status"] for row in native.values())),
              "fresh_queries_recomputed": len(inputs), "final_repair_routes_checked": len(rows),
              "accepted_intermediate_routes_checked": intermediates, "paired_runs": len(pairs), "pairs": pairs,
              "coverage": coverage,
              "SOL_wins": sum(row["sol_delta"] < 0 for row in pairs),
              "SOL_ties": sum(row["sol_delta"] == 0 for row in pairs),
              "SOL_losses": sum(row["sol_delta"] > 0 for row in pairs),
              "delta_sums": {metric: sum(row[metric + "_delta"] for row in pairs) for metric in ("sol", "soc", "makespan")},
              "regressions": {metric: sum(row[metric + "_delta"] > 0 for row in pairs) for metric in ("sol", "soc", "makespan")},
              "search_pops_audited": sum(row["budget"]["nodes_used"] for row in rows),
              "recorded_resources": resources, "elapsed_seconds": time.perf_counter() - started,
              "protocol_sha256": sha(PACKAGE / "protocol.json"), "inputs_sha256": sha(PACKAGE / "inputs.json"),
              "native_sha256": sha(PACKAGE / "native.json"), "repair_sha256": sha(PACKAGE / "repair.json"),
              "auditor_sha256": sha(Path(__file__))}
    with output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("pairs", "recorded_resources")}))


if __name__ == "__main__":
    main()
