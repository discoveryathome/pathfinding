"""Audit frozen paired experiments without importing the repair optimizers."""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from verify import check


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_sources():
    prefix = str(PACKAGE.relative_to(ROOT)) + "/"
    return {prefix + name for name in ("sol_repair.py", "run_one.py", "run_study.py", "protocol.json",
                                       "inputs/maze-start.json")} | {
        "src/model.py", "src/repair.py", "src/repair_round2.py", "src/verify.py", "discover/incumbents.json"}


@lru_cache(maxsize=None)
def committed_sources(commit):
    if type(commit) is not str or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("Use a full code commit identity")
    return {path: hashlib.sha256(subprocess.check_output(["git", "show", commit + ":" + path], cwd=ROOT,
                                                        stderr=subprocess.DEVNULL)).hexdigest()
            for path in sorted(required_sources())}


def validate_manifest(manifest, commit):
    if not isinstance(manifest, dict) or set(manifest) != required_sources():
        raise ValueError("Incomplete or unexpected source key set")
    if type(commit) is not str or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("Use a full code commit identity")
    try:
        expected = committed_sources(commit)
    except subprocess.CalledProcessError as error:
        raise ValueError("Recorded source version unavailable; fetch the retained Git history") from error
    if manifest != expected:
        raise ValueError("Source hashes do not match the recorded commit")


def metrics_shape(metrics):
    if (set(metrics) != {"sol", "soc", "makespan"}
            or any(type(value) is not int or value < 0 for value in metrics.values())):
        raise ValueError("Use exact nonnegative integer metrics")


def trimmed(path):
    result = list(path)
    while len(result) > 1 and result[-1] == result[-2]:
        result.pop()
    return result


def validate_cohort(rows, cases, challenger):
    expected = {(c["case"], trial, method) for c in cases for trial in range(3)
                for method in ("arrival", challenger)}
    keys = [(r["case"], r["trial"], r["method"]) for r in rows]
    if (any(type(r["trial"]) is not int for r in rows) or len(keys) != len(expected)
            or len(set(keys)) != len(keys) or set(keys) != expected):
        raise ValueError("Wrong canonical case/trial/method cohort")


def validate_trace(initial, trace, candidate, instance):
    metrics_shape(initial["metrics"])
    metrics_shape(candidate["metrics"])
    budget, history = trace["budget"], trace["history"]
    if any(type(v) is not int for v in budget.values()):
        raise ValueError("Use integer resource counts")
    assert budget["node_limit"] == 100000 and budget["attempt_limit"] == 96 and budget["per_agent_limit"] == 10000
    assert budget["attempts_used"] == len(history) <= 96
    assert budget["nodes_used"] == sum(r["popped"] for r in history) <= 100000
    assert len(history) == 96 or budget["nodes_used"] == 100000, "Incomplete search history"
    improvements = {r["attempt"]: r for r in trace["improvements"]}
    assert len(improvements) == len(trace["improvements"])
    paths, before, used, checked_routes = [trimmed(p) for p in initial["paths"]], initial["metrics"], 0, 0
    for number, row in enumerate(history):
        metrics_shape(row["before"])
        metrics_shape(row["proposed"])
        assert type(row["attempt"]) is int and row["attempt"] == number and row["before"] == before
        group = row["agents"]
        if (len(group) != min(4, len(paths)) or len(set(group)) != len(group)
                or any(type(i) is not int or not 0 <= i < len(paths) for i in group)):
            raise ValueError("Invalid neighborhood IDs")
        assert type(row["popped"]) is int and 0 <= row["popped"] <= min(len(group) * 10000, 100000 - used)
        used += row["popped"]
        assert row["status"] in {"complete", "budget", "exhausted", "blocked_start", "total_budget"}
        after = row["proposed"]
        accepted = (row["status"] == "complete" and all(after[k] <= before[k] for k in before)
                    and (after["sol"] < before["sol"] or after["soc"] < before["soc"]))
        assert type(row["accepted"]) is bool and row["accepted"] == accepted
        assert accepted == (number in improvements)
        if row["status"] != "complete":
            assert after == before
        if accepted:
            item = improvements[number]
            assert item["metrics"] == after
            assert all(p == item["paths"][i] for i, p in enumerate(paths) if i not in group)
            check(instance, {**candidate, "paths": item["paths"], "metrics": item["metrics"]})
            checked_routes += 1
            paths, before = item["paths"], after
    assert trace["paths"] == candidate["paths"] == paths
    assert trace["metrics"] == candidate["metrics"] == before
    rejected = [r for r in history if r["status"] == "complete" and not r["accepted"]]
    reasons = {"completed_rejected": len(rejected),
               "SOL_better_SOC_worse": sum(r["proposed"]["sol"] < r["before"]["sol"]
                                            and r["proposed"]["soc"] > r["before"]["soc"] for r in rejected),
               "guard_regressions": {key: sum(r["proposed"][key] > r["before"][key] for r in rejected)
                                     for key in ("sol", "soc", "makespan")}}
    return {"accepted_routes_checked": checked_routes, "rejections": reasons,
            "groups": [r["agents"] for r in history], "status_counts": dict(Counter(r["status"] for r in history))}


def artifact(path):
    result = (PACKAGE / path).resolve()
    if not result.is_relative_to(PACKAGE / "runs"):
        raise ValueError("Artifact outside the declared runs directory")
    return result


def verify_run(record, case, manifest):
    assert record["verified"] is True
    validate_manifest(record["source_sha256"], record["code_commit"])
    assert record["source_sha256"] == manifest
    assert record["instance"] == case["instance"] and record["instance_sha256"] == case["instance_sha256"]
    assert record["inherited"] == case["start"] and record["panel"] == case["panel"]
    seed = case["seeds"][record["trial"]]
    assert record["seed_hex"] == seed["seed_hex"] and record["seed_decimal"] == seed["seed_decimal"]
    instance = (ROOT / case["instance"]).resolve()
    inherited_path = (ROOT / case["start"]["path"]).resolve()
    assert instance.is_relative_to(ROOT) and inherited_path.is_relative_to(ROOT)
    assert sha(instance) == case["instance_sha256"] and sha(inherited_path) == case["start"]["sha256"]
    initial = json.loads(inherited_path.read_text())
    assert check(instance, initial) == record["initial_metrics"]
    cp, tp = artifact(record["candidate"]), artifact(record["trace"])
    assert cp.parent == tp.parent and sha(cp) == record["candidate_sha256"] and sha(tp) == record["trace_sha256"]
    assert json.loads((cp.parent / "run.json").read_text()) == record
    candidate = json.loads(cp.read_text())
    with gzip.open(tp, "rt") as handle:
        trace = json.load(handle)
    assert candidate["method"] == record["method"] and candidate["seed_decimal"] == seed["seed_decimal"]
    assert str(trace["seed"]) == seed["seed_decimal"]
    assert trace["variant"] == ("random4" if record["method"] == "arrival" else record["method"])
    actual = check(instance, candidate)
    assert actual == record["candidate_metrics"]
    assert all(actual[key] <= record["initial_metrics"][key] for key in ("sol", "soc", "makespan"))
    verified = validate_trace(initial, trace, candidate, instance)
    assert trace["budget"] == record["budget"]
    assert verified["accepted_routes_checked"] == record["accepted_routes_checked"]
    assert verified["rejections"] == record["rejections"] and verified["status_counts"] == record["status_counts"]
    return verified


def comparison(rows, cases, challenger):
    indexed = {(r["case"], r["trial"], r["method"]): r for r in rows}
    pairs = []
    for case in cases:
        for trial in range(3):
            a = indexed[case["case"], trial, "arrival"]["candidate_metrics"]
            b = indexed[case["case"], trial, challenger]["candidate_metrics"]
            pairs.append({"case": case["case"], "trial": trial, "SOL_delta": b["sol"] - a["sol"],
                          "SOC_delta": b["soc"] - a["soc"], "makespan_delta": b["makespan"] - a["makespan"]})
    sol, soc = sum(x["SOL_delta"] for x in pairs), sum(x["SOC_delta"] for x in pairs)
    makespan = sum(x["makespan_delta"] > 0 for x in pairs)
    rejected = sum(r["rejections"]["completed_rejected"] for r in rows if r["method"] == challenger)
    tradeoffs = sum(r["rejections"]["SOL_better_SOC_worse"] for r in rows if r["method"] == challenger)
    return {"gate_passed": sol < 0 and soc <= 0 and makespan == 0, "pairs": pairs, "paired_runs": len(pairs),
            "SOL_delta_sum": sol, "SOC_delta_sum": soc, "makespan_regressions": makespan,
            "completed_rejected_challenger": rejected, "SOL_better_SOC_worse_challenger": tradeoffs,
            "pivot_trigger": rejected >= 10 and 2 * tradeoffs > rejected}


def verify_batch(path, protocol, challenger, attempt, stage):
    report = json.loads(path.read_text())
    assert report["complete"] is True and report["challenger"] == challenger
    panel = "evaluation" if stage == "evaluation" else "development"
    assert report["attempt"] == attempt and report["stage"] == stage and report["panel"] == panel
    prefix = str(PACKAGE.relative_to(ROOT)) + "/"
    assert report["source_sha256"][prefix + "protocol.json"] == sha(PACKAGE / "protocol.json")
    assert report["source_sha256"]["src/verify.py"] == sha(ROOT / "src/verify.py")
    cases = [c for c in protocol["cases"] if c["panel"] == panel]
    rows = report["rows"]
    validate_cohort(rows, cases, challenger)
    assert report["completed_runs"] == report["expected_runs"] == len(rows)
    journal = [json.loads(line) for line in path.with_suffix(".jsonl").read_text().splitlines()]
    assert journal == report["events"] and len(journal) == len(rows)
    bykey = {(r["case"], r["trial"], r["method"]): r for r in rows}
    event_keys = [(e["case"], e["trial"], e["method"]) for e in journal]
    assert len(set(event_keys)) == len(rows) and set(event_keys) == set(bykey)
    cases_by_id = {case["case"]: case for case in cases}
    verified, accepted = {}, 0
    for event in journal:
        assert event["returncode"] == 0
        row = bykey[event["case"], event["trial"], event["method"]]
        record_file = artifact(event["record"])
        assert json.loads(record_file.read_text()) == row
        assert record_file.parent == artifact(row["candidate"]).parent
        result = verify_run(row, cases_by_id[row["case"]], report["source_sha256"])
        verified[row["case"], row["trial"], row["method"]] = result
        accepted += result["accepted_routes_checked"]
    for case in cases:
        for trial in range(3):
            a = verified[case["case"], trial, "arrival"]["groups"]
            b = verified[case["case"], trial, challenger]["groups"]
            common = min(len(a), len(b))
            assert a[:common] == b[:common], "Paired random-neighborhood prefix differs"
    expected = comparison(rows, cases, challenger)
    assert report["comparison"] == expected
    assert report["total_search_pops"] == sum(r["budget"]["nodes_used"] for r in rows)
    return {"batch": path.name, "runs_checked": len(rows), "intermediate_routes_checked": accepted,
            "search_pops_audited": report["total_search_pops"], "comparison": expected,
            "source_sha256": report["source_sha256"], "batch_sha256": sha(path)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="a1")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if not args.attempt.replace("-", "").replace("_", "").isalnum():
        parser.error("Use a simple attempt ID")
    output = (PACKAGE / args.out).resolve()
    if output.parent != PACKAGE or output.exists():
        parser.error("Use a new verification filename")
    tick = time.perf_counter()
    protocol = json.loads((PACKAGE / "protocol.json").read_text())
    assert len(protocol["cases"]) == len({c["case"] for c in protocol["cases"]}) == 20
    selection_path = PACKAGE / f"{args.attempt}-development.json"
    selection = json.loads(selection_path.read_text())
    assert selection["primary_batch"] == f"{args.attempt}-dev-primary.json"
    assert selection["rule"] == protocol["development_gate"]
    batches = []
    primary = verify_batch(PACKAGE / selection["primary_batch"], protocol, "sol", args.attempt, "dev-primary")
    batches.append(primary)
    assert primary["source_sha256"] == selection["source_sha256"]
    expected_selected = "sol" if primary["comparison"]["gate_passed"] else None
    should_pivot = not primary["comparison"]["gate_passed"] and primary["comparison"]["pivot_trigger"]
    assert selection["pivot_batch"] == (f"{args.attempt}-dev-pivot.json" if should_pivot else None)
    if should_pivot:
        pivot = verify_batch(PACKAGE / selection["pivot_batch"], protocol, "sol-deadline", args.attempt, "dev-pivot")
        batches.append(pivot)
        assert pivot["source_sha256"] == selection["source_sha256"]
        if pivot["comparison"]["gate_passed"]:
            expected_selected = "sol-deadline"
    assert selection["selected"] == expected_selected
    evaluation_path = PACKAGE / f"{args.attempt}-evaluation.json"
    if expected_selected is not None:
        evaluated = verify_batch(evaluation_path, protocol, expected_selected, args.attempt, "evaluation")
        assert evaluated["source_sha256"] == selection["source_sha256"]
        batches.append(evaluated)
    else:
        assert not evaluation_path.exists(), "Evaluation ran without a development winner"
    result = {"verified": True, "optimizer_imports": False, "evidence_level": "author-checked separate audit",
              "attempt": args.attempt, "selected": expected_selected, "batches": batches,
              "runs_checked": sum(b["runs_checked"] for b in batches),
              "accepted_intermediate_routes_checked": sum(b["intermediate_routes_checked"] for b in batches),
              "elapsed_seconds": time.perf_counter() - tick, "protocol_sha256": sha(PACKAGE / "protocol.json"),
              "selection_sha256": sha(selection_path), "verifier_sha256": sha(Path(__file__))}
    with output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "batches"}))
