"""Adversarial source/cohort/trace controls for the separate experiment audit."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("verify_study", Path(__file__).with_name("verify_study.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_source_manifest_requires_all_declared_keys():
    record = next((verify.PACKAGE / "runs/a1-dev-primary").glob("*/run.json"))
    data = json.loads(record.read_text())
    verify.validate_manifest(data["source_sha256"], data["code_commit"])
    missing = dict(data["source_sha256"])
    missing.pop(next(iter(missing)))
    for manifest in ({}, missing, {**data["source_sha256"], "unexpected/path": "0" * 64}):
        with pytest.raises(ValueError, match="source key set"):
            verify.validate_manifest(manifest, data["code_commit"])


def test_canonical_cohort_rejects_duplicates_and_trial_aliases():
    cases = [{"case": "tiny"}]
    rows = [{"case": "tiny", "trial": trial, "method": method}
            for trial in range(3) for method in ("arrival", "sol")]
    verify.validate_cohort(rows, cases, "sol")
    duplicate = copy.deepcopy(rows)
    duplicate[1] = duplicate[0]
    with pytest.raises(ValueError):
        verify.validate_cohort(duplicate, cases, "sol")
    for trial in (-1, True, 0.0):
        wrong = copy.deepcopy(rows)
        wrong[0]["trial"] = trial
        with pytest.raises(ValueError):
            verify.validate_cohort(wrong, cases, "sol")


def test_wrong_trace_pop_accounting_and_metrics_rejected():
    initial = {"paths": [[0]], "metrics": {"sol": 0, "soc": 0, "makespan": 0}}
    candidate = copy.deepcopy(initial)
    trace = {"paths": [[0]], "metrics": initial["metrics"], "history": [], "improvements": [],
             "budget": {"node_limit": 100000, "nodes_used": 0, "attempt_limit": 96,
                        "attempts_used": 0, "per_agent_limit": 10000}}
    assert verify.validate_trace(initial, trace, candidate, Path("unused"))["accepted_routes_checked"] == 0
    bad = copy.deepcopy(trace)
    bad["budget"]["nodes_used"] = 1
    with pytest.raises(AssertionError):
        verify.validate_trace(initial, bad, candidate, Path("unused"))
    with pytest.raises(ValueError):
        verify.metrics_shape({"sol": 0.0, "soc": 0, "makespan": 0})


def test_artifact_paths_cannot_escape_declared_runs():
    with pytest.raises(ValueError):
        verify.artifact("../outside.json")
