"""Tiny controls only; no fresh-panel output is used for method selection."""
import hashlib
import copy
import gzip
import json
import os
from pathlib import Path
import sys
import time

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


def worker_fixture(tmp_path, monkeypatch, seed_value=0):
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
    seed = {"trial": 0, "hex": f"{seed_value:032x}", "decimal": str(seed_value)}
    plan = {"cases": [{"id": "tiny", "repair_seeds": [seed]}]}
    monkeypatch.setattr(run_repair, "PACKAGE", package)
    monkeypatch.setattr(run_repair, "protocol", lambda: plan)
    monkeypatch.setattr(run_repair, "source_identity", lambda _: {"code_commit": "a" * 40, "source_sha256": {}})
    monkeypatch.setattr(run_repair, "check_limits", lambda _: None)
    return initial, package


def test_checker_rejection_retains_returned_routes_and_trace(tmp_path, monkeypatch):
    initial, package = worker_fixture(tmp_path, monkeypatch)
    bad_paths = [[0, 1], [5, 1, 3]]
    result = {"paths": initial["paths"], "metrics": initial["metrics"], "history": [], "budget": {}, "seed": 0,
              "improvements": [{"attempt": 0, "paths": bad_paths, "metrics": initial["metrics"]}]}
    monkeypatch.setattr(run_repair, "arrival_run", lambda *args, **kwargs: copy.deepcopy(result))
    with pytest.raises(ValueError):
        run_repair.worker("tiny", 0, "arrival")
    destination = package / "runs/tiny-t0-arrival"
    assert json.loads((destination / "candidate.json").read_text())["paths"] == initial["paths"]
    assert json.loads(gzip.decompress((destination / "trace.json.gz").read_bytes())) == {**result, "seed": "0"}
    assert (destination / "request.json").exists()
    assert json.loads((destination / "failure.json").read_text())["status"] == "verification_failed"


def test_trace_seed_is_exact_text_and_core_excludes_preprocessing(tmp_path, monkeypatch):
    value = 2 ** 127 + 18446744073709551615
    initial, package = worker_fixture(tmp_path, monkeypatch, value)

    def engine(ins, paths, variant, seed, **kwargs):
        assert type(seed) is int and seed == value
        return {"paths": initial["paths"], "metrics": initial["metrics"], "history": [], "budget": {},
                "seed": seed, "improvements": [], "preprocess_seconds": 2.0, "elapsed_seconds": 5.0}

    monkeypatch.setattr(run_repair, "arrival_run", engine)
    run_repair.worker("tiny", 0, "arrival")
    destination = package / "runs/tiny-t0-arrival"
    stored = json.loads(gzip.decompress((destination / "trace.json.gz").read_bytes()))
    record = json.loads((destination / "run.json").read_text())
    assert type(stored["seed"]) is str and stored["seed"] == str(value)
    assert record["engine_wall_seconds"] == 5 and record["preprocess_seconds"] == 2
    assert record["core_wall_seconds"] == 3


def test_coordinator_timeout_kills_the_nested_native_group(tmp_path):
    pid_path = tmp_path / "native.pid"
    native = f"import os,time; from pathlib import Path; Path({str(pid_path)!r}).write_text(str(os.getpid())); time.sleep(30)"
    worker = (f"import sys; sys.path.insert(0,{str(PACKAGE)!r}); from common import run_process; "
              f"run_process([sys.executable,'-c',{native!r}],30,1024,own_group=False)")
    result = run_process([sys.executable, "-c", worker], 1.0, 1024)
    assert result["status"] == "timeout" and pid_path.exists()
    pid = int(pid_path.read_text())
    stat = Path(f"/proc/{pid}/stat")
    for _ in range(10):
        if not stat.exists() or stat.read_text().split()[2] == "Z":
            break
        time.sleep(0.05)
    else:
        os.kill(pid, 9)
        pytest.fail("Native descendant survived the coordinator timeout")


@pytest.mark.parametrize("stop_at_cap", [False, True])
def test_panel_continues_failed_workers_and_records_unattempted_caps(tmp_path, monkeypatch, stop_at_cap):
    package = tmp_path / "coordinator"
    package.mkdir()
    (package / "native.json").write_text(json.dumps({"rows": [{"case": case, "status": "verified"} for case in ("one", "two")]}))
    plan = {"cases": [{"id": case} for case in ("one", "two")],
            "caps": {"phase_wall_seconds": 3600, "repair_worker_wall_seconds": 600, "address_space_mib": 1024}}
    monkeypatch.setattr(run_repair, "PACKAGE", package)
    monkeypatch.setattr(run_repair, "protocol", lambda: plan)
    monkeypatch.setattr(run_repair, "source_identity", lambda _: {})
    monkeypatch.setattr(run_repair, "remaining_seconds", lambda _: 3600)
    monkeypatch.setattr(sys, "argv", ["run_repair.py", "--all"])

    def limits(_):
        if stop_at_cap:
            raise TimeoutError("controlled cap")

    commands = []

    def fail(command, timeout, memory_mib):
        commands.append(command)
        return {"status": "timeout", "returncode": -9, "stdout": "", "stderr": "", "command": command}

    monkeypatch.setattr(run_repair, "check_limits", limits)
    monkeypatch.setattr(run_repair, "run_process", fail)
    run_repair.main()
    report = json.loads((package / "repair.json").read_text())
    journal = (package / "repair-journal.jsonl").read_text().splitlines()
    assert len(report["rows"]) == 12 and report["skipped"] == []
    assert len(commands) == len(journal) == (0 if stop_at_cap else 12)
    assert {row["status"] for row in report["rows"]} == {"not_attempted" if stop_at_cap else "worker_timeout"}
    assert report["all_jobs_attempted"] is (not stop_at_cap)
