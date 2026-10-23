"""Adversarial controls for the auditor, using no fresh experiment outputs."""
import copy
import importlib.util
from pathlib import Path
import subprocess

import pytest

spec = importlib.util.spec_from_file_location("fresh_audit", Path(__file__).with_name("audit.py"))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_source_manifest_requires_real_commits_and_all_thirteen_files():
    manifest = {path: audit.sha(audit.ROOT / path) for path in audit.required_sources()}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=audit.ROOT, text=True).strip()
    record = {"source_sha256": manifest, "code_commit": commit}
    assert len(manifest) == 13 and audit.validate_sources(record) == manifest
    for bad in ({}, dict(list(manifest.items())[1:]), {**manifest, "extra": "0" * 64}):
        with pytest.raises(ValueError):
            audit.validate_sources({**record, "source_sha256": bad})
    tree = subprocess.check_output(["git", "rev-parse", commit + "^{tree}"], cwd=audit.ROOT, text=True).strip()
    for bad in ("0" * 40, tree, "37823dca1bea271510e3ed62205620466ec6f0f9"):
        with pytest.raises(ValueError):
            audit.validate_sources({**record, "code_commit": bad})


def test_exact_cohort_rejects_duplicates_and_alias_trials():
    rows = [{"case": "one", "trial": trial, "method": method} for trial in range(3) for method in ("arrival", "sol")]
    expected = [(row["case"], row["trial"], row["method"]) for row in rows]
    audit.cohort(rows, expected, ("case", "trial", "method"))
    duplicate = copy.deepcopy(rows)
    duplicate[1] = duplicate[0]
    for altered in [duplicate] + [[{**rows[0], "trial": value}, *rows[1:]] for value in (-1, False, 0.0)]:
        with pytest.raises(ValueError):
            audit.cohort(altered, expected, ("case", "trial", "method"))


def complete_trace():
    initial = {"paths": [[0], [1], [2], [3]], "metrics": {"sol": 0, "soc": 0, "makespan": 0}}
    history = [{"attempt": number, "agents": [0, 1, 2, 3], "popped": 4, "status": "complete",
                "accepted": False, "before": initial["metrics"], "proposed": initial["metrics"]} for number in range(96)]
    trace = {**copy.deepcopy(initial), "history": history, "improvements": [],
             "budget": {"node_limit": 100000, "nodes_used": 384, "attempt_limit": 96,
                        "attempts_used": 96, "per_agent_limit": 10000}}
    return initial, trace


def test_incomplete_histories_and_aliased_agent_ids_fail():
    initial, trace = complete_trace()
    assert audit.audit_trace(trace, initial, initial, Path("unused"))[0] == 0
    for length in (0, 1, 95):
        bad = copy.deepcopy(trace)
        bad["history"] = bad["history"][:length]
        bad["budget"].update(attempts_used=length, nodes_used=length * 4)
        with pytest.raises(AssertionError, match="Incomplete search history"):
            audit.audit_trace(bad, initial, initial, Path("unused"))
    for ids in ([-1, 1, 2, 3], [0, 0, 2, 3], [False, 1, 2, 3], [0, 1, 2, 4]):
        bad = copy.deepcopy(trace)
        bad["history"][0]["agents"] = ids
        with pytest.raises(AssertionError):
            audit.audit_trace(bad, initial, initial, Path("unused"))


def test_short_history_requires_exact_total_budget():
    initial, trace = complete_trace()
    trace["history"] = trace["history"][:3]
    for row, work in zip(trace["history"], (40000, 40000, 20000)):
        row.update(status="budget", popped=work)
    trace["budget"].update(nodes_used=100000, attempts_used=3)
    audit.audit_trace(trace, initial, initial, Path("unused"))
    trace["history"][-1]["popped"] -= 1
    trace["budget"]["nodes_used"] -= 1
    with pytest.raises(AssertionError, match="Incomplete search history"):
        audit.audit_trace(trace, initial, initial, Path("unused"))


def test_artifacts_cannot_escape_the_declared_area():
    for path in ("../outside.json", "/tmp/outside.json", "runs/../native/wrong.json"):
        with pytest.raises(ValueError):
            audit.artifact(path, "runs")
