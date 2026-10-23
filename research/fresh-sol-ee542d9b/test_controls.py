"""Tiny controls only; no fresh-panel output is used for method selection."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PACKAGE, protocol, run_process, sha
from inputs import draw, largest_component
from run_native import parse_certificate


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
    for changed in (text.replace("soc=3", "soc=4"), text.replace("1:", "4:"), text.replace("(1,1)", "(1,0)")):
        with pytest.raises((AssertionError, ValueError)):
            parse_certificate(changed, instance, 2, sha(instance))


def test_process_timeout_and_failed_exit_are_retained():
    timed = run_process([sys.executable, "-c", "import time; time.sleep(5)"], 0.05, 1024)
    assert timed["status"] == "timeout" and timed["returncode"] != 0
    failed = run_process([sys.executable, "-c", "raise SystemExit(7)"], 3, 1024)
    assert failed["status"] == "failed" and failed["returncode"] == 7
