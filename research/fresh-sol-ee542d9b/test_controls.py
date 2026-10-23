"""Tiny controls only; no fresh-panel output is used for method selection."""
import hashlib
import copy
import gzip
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PACKAGE, protocol, run_process, sha
from inputs import draw, largest_component
from run_native import parse_certificate
import run_repair


def test_largest_component_and_tie_are_canonical():
    grid = {"adj": {0: (1,), 1: (0,), 4: (5,), 5: (4,), 9: ()}}
    assert largest_component(grid) == [0, 1]
    starts, goals = draw(grid, 2, 382)
    assert sorted(starts) == sorted(goals) == [0, 1]
    assert draw(grid, 2, 382) == (starts, goals)


def test_full_seed_schedule_and_frozen_policy_identity():
    plan = protocol()
    assert len(plan["cases"]) == len({case["id"] for case in plan["cases"]}) == 12
    donation = bytes.fromhex(plan["seed_hex"])
    for case in plan["cases"]:
        seed = hashlib.sha256(donation + b":fresh-v1:" + case["id"].encode()).digest()[:16]
        assert seed.hex() == case["draw_seed_hex"]
        assert str(int.from_bytes(seed, "big")) == case["draw_seed_decimal"]
        for row in case["repair_seeds"]:
            raw = hashlib.sha256(donation + b":repair-fresh-v1:" + case["id"].encode()
                                 + b":" + str(row["trial"]).encode()).digest()[:16]
            assert raw.hex() == row["hex"] and str(int.from_bytes(raw, "big")) == row["decimal"]
    assert sha(PACKAGE / "sol_repair.py") == plan["policy_sha256"]


def tiny_instance(tmp_path):
    map_path = tmp_path / "tiny.map"
    map_path.write_text("type octile\nheight 2\nwidth 3\nmap\n...\n...\n")
    instance = tmp_path / "tiny.json"
    instance.write_text(json.dumps({"id": "tiny", "map": str(map_path), "map_sha256": sha(map_path),
                                    "starts": [0, 5], "goals": [1, 3]}))
    return instance


def test_native_conversion_checks_headers_times_and_goal_holds(tmp_path):
    instance = tiny_instance(tmp_path)
    text = "soc=3\nsum_of_loss=3\nmakespan=2\n0:(0,0),(2,1)\n1:(1,0),(1,1)\n2:(1,0),(0,1)\n"
    certificate = parse_certificate(text, instance, 2, sha(instance))
    assert certificate["paths"] == [[0, 1], [5, 4, 3]]
    for changed in (text.replace("soc=3", "soc=4"), text.replace("1:", "4:"), text.replace("(1,1)", "(1,0)"),
                    text.replace("(0,1)", "(3,0)"), text.replace("(0,1)", "(-3,2)")):
        with pytest.raises((AssertionError, ValueError)):
            parse_certificate(changed, instance, 2, sha(instance))


def test_process_timeout_and_failed_exit_are_retained():
    timed = run_process([sys.executable, "-c", "import time; time.sleep(5)"], 0.05, 1024)
    assert timed["status"] == "timeout" and timed["returncode"] != 0
    failed = run_process([sys.executable, "-c", "raise SystemExit(7)"], 3, 1024)
    assert failed["status"] == "failed" and failed["returncode"] == 7


def test_checker_rejection_retains_returned_routes_and_trace(tmp_path, monkeypatch):
    instance = tiny_instance(tmp_path)
    package = tmp_path / "package"
    native_dir = package / "native/tiny"
    native_dir.mkdir(parents=True)
    initial = {"instance_sha256": sha(instance), "paths": [[0, 1], [5, 4, 3]],
               "metrics": {"sol": 3, "soc": 3, "makespan": 2}}
    candidate_path = native_dir / "candidate.json"
    candidate_path.write_text(json.dumps(initial))
    native = {"status": "verified", "candidate": "native/tiny/candidate.json", "candidate_sha256": sha(candidate_path),
              "input": {"instance": str(instance), "instance_sha256": sha(instance)}}
    (native_dir / "run.json").write_text(json.dumps(native))
    seed = {"trial": 0, "hex": "00" * 16, "decimal": "0"}
    plan = {"cases": [{"id": "tiny", "repair_seeds": [seed]}]}
    monkeypatch.setattr(run_repair, "PACKAGE", package)
    monkeypatch.setattr(run_repair, "protocol", lambda: plan)
    monkeypatch.setattr(run_repair, "source_identity", lambda _: {"code_commit": "a" * 40, "source_sha256": {}})
    monkeypatch.setattr(run_repair, "check_limits", lambda _: None)
    bad_paths = [[0, 1], [5, 1, 3]]
    result = {"paths": initial["paths"], "metrics": initial["metrics"], "history": [], "budget": {},
              "improvements": [{"attempt": 0, "paths": bad_paths, "metrics": initial["metrics"]}]}
    monkeypatch.setattr(run_repair, "arrival_run", lambda *args, **kwargs: copy.deepcopy(result))
    with pytest.raises(ValueError):
        run_repair.worker("tiny", 0, "arrival")
    destination = package / "runs/tiny-t0-arrival"
    assert json.loads((destination / "candidate.json").read_text())["paths"] == initial["paths"]
    assert json.loads(gzip.decompress((destination / "trace.json.gz").read_bytes())) == result
    assert (destination / "request.json").exists()
    assert json.loads((destination / "failure.json").read_text())["status"] == "verification_failed"
