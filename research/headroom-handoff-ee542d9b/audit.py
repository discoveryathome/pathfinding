"""Author-check the bound routes, trace accounting, and deterministic replay."""
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from model import read_instance
from repair_round2 import run
from verify import check


def load(path):
    return json.loads(path.read_text())


def route_metrics(paths):
    # Recompute final arrivals directly, including visits followed by departures.
    arrivals = [max((t + 1 for t, v in enumerate(p) if v != p[-1]), default=0)
                for p in paths]
    losses = [sum(a != p[-1] or b != p[-1] for a, b in zip(p, p[1:]))
              for p in paths]
    return {"soc": sum(arrivals), "sol": sum(losses), "makespan": max(arrivals)}


def trace_accounting(trace, initial):
    budget = trace["budget"]
    history = trace["history"]
    assert budget["nodes_used"] == sum(row["popped"] for row in history)
    assert budget["nodes_used"] <= budget["node_limit"] == 100000
    assert len(history) == budget["attempts_used"] <= budget["attempt_limit"] == 96
    assert budget["per_agent_limit"] == 10000
    improvements = {item["attempt"]: item for item in trace["improvements"]}
    assert len(improvements) == len(trace["improvements"])
    paths, before, used = initial["paths"], initial["metrics"], 0
    checked = 0
    for number, row in enumerate(history):
        assert row["attempt"] == number and row["before"] == before
        group = row["agents"]
        assert len(set(group)) == len(group) == 4
        assert all(0 <= i < len(paths) for i in group)
        assert 0 <= row["popped"] <= min(4 * budget["per_agent_limit"], 100000 - used)
        used += row["popped"]
        after = row["proposed"]
        expected = (row["status"] == "complete"
                    and all(after[k] <= before[k] for k in before)
                    and (after["sol"] < before["sol"] or after["soc"] < before["soc"]))
        assert row["accepted"] == expected
        assert row["accepted"] == (number in improvements)
        if row["status"] != "complete":
            assert after == before
        if row["accepted"]:
            item = improvements[number]
            assert item["metrics"] == after == route_metrics(item["paths"])
            assert all(p == item["paths"][i] for i, p in enumerate(paths) if i not in group)
            check(ROOT / PROTOCOL["instance"], {**initial, "paths": item["paths"], "metrics": after})
            checked += 1
            paths, before = item["paths"], after
    assert paths == trace["paths"] and before == trace["metrics"]
    return checked


def rejected(call, text, error_type=ValueError):
    try:
        call()
    except error_type as error:
        assert text in str(error)
        return str(error)
    raise AssertionError("Negative control was accepted")


if __name__ == "__main__":
    PROTOCOL = load(PACKAGE / "protocol.json")
    for path, digest in PROTOCOL["sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    initial = load(ROOT / PROTOCOL["candidate_source"])
    candidate = load(PACKAGE / "experiment/candidate.json")
    trace = load(PACKAGE / "experiment/trace.json")
    instance = ROOT / PROTOCOL["instance"]
    inherited_check = check(instance, initial)
    candidate_check = check(instance, candidate)
    assert initial["metrics"] == PROTOCOL["candidate_source_metrics"]
    assert candidate["paths"] == trace["paths"]
    assert candidate["metrics"] == trace["metrics"] == route_metrics(candidate["paths"])
    assert trace["seed"] == candidate["seed"] == PROTOCOL["seed_decimal"]
    assert trace["variant"] == candidate["method"] == "random4"
    assert candidate["metrics"]["sol"] < initial["metrics"]["sol"]
    assert all(candidate["metrics"][k] <= initial["metrics"][k] for k in initial["metrics"])
    intermediates = trace_accounting(trace, initial)

    bad_binding = {**candidate, "instance_sha256": "0" * 64}
    bad_metrics = {**candidate, "metrics": {**candidate["metrics"], "sol": 0}}
    bad_budget = copy.deepcopy(trace)
    bad_budget["budget"]["nodes_used"] -= 1
    controls = {
        "wrong_instance_binding": rejected(lambda: check(instance, bad_binding), "Wrong instance binding"),
        "wrong_SOL": rejected(lambda: check(instance, bad_metrics), "Incorrect claimed metrics"),
        "forged_pop_accounting": rejected(lambda: trace_accounting(bad_budget, initial), "", AssertionError),
    }
    replay = run(read_instance(instance), initial["paths"], "random4", PROTOCOL["seed_decimal"],
                 node_budget=100000, attempts=96, agent_cap=10000)
    stable = lambda result: {k: v for k, v in result.items()
                             if k not in ("preprocess_seconds", "elapsed_seconds")}
    assert stable(replay) == stable(trace), "Deterministic replay differs"

    rows = load(PACKAGE / "headroom.json")
    assert len(rows) == 20
    headroom = next(r for r in rows if r["case"] == PROTOCOL["case"])
    assert headroom["incumbent"]["sha256"] == PROTOCOL["sha256"][PROTOCOL["candidate_source"]]
    assert headroom["individual_distance_bound"] == 5926
    assert len(headroom["disjoint_pair_witnesses"]) == 43
    assert headroom["pair_conflict_bound"] == 5969
    assert headroom["sol_gap"] == 1846
    changes = []
    for i, (before, after) in enumerate(zip(initial["paths"], candidate["paths"])):
        if before != after:
            changes.append({"agent": i, "before": route_metrics([before]),
                            "after": route_metrics([after])})
    print(json.dumps({
        "passed": True,
        "evidence_level": "author-checked",
        "inherited": inherited_check,
        "candidate": candidate_check,
        "candidate_sha256": hashlib.sha256((PACKAGE / "experiment/candidate.json").read_bytes()).hexdigest(),
        "accepted_intermediate_routes_checked": intermediates,
        "trace_accounting_passed": True,
        "attempt_status_counts": dict(Counter(row["status"] for row in trace["history"])),
        "failure_controls": controls,
        "deterministic_replay_all_non_timing_fields_equal": True,
        "verification_replay_nodes": replay["budget"]["nodes_used"],
        "verification_replay_elapsed_seconds": replay["elapsed_seconds"],
        "verification_replay_preprocess_seconds": replay["preprocess_seconds"],
        "remaining_SOL_bound_gap": candidate["metrics"]["sol"] - headroom["pair_conflict_bound"],
        "changed_agents": changes,
    }, indent=2))
