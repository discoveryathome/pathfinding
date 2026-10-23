"""Development eligibility and the predeclared pivot denominator."""
import copy
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location("run_study", Path(__file__).with_name("run_study.py"))
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def rows():
    return [{"case": "tiny", "trial": 0, "method": method,
             "candidate_metrics": {"sol": sol, "soc": 10, "makespan": 6},
             "rejections": {"completed_rejected": 10, "SOL_better_SOC_worse": 6}}
            for method, sol in (("arrival", 9), ("sol", 8))]


def test_development_gate_keeps_both_guards():
    initial = rows()
    assert study.compare(initial, "sol")["gate_passed"]
    for key in ("soc", "makespan"):
        bad = copy.deepcopy(initial)
        bad[1]["candidate_metrics"][key] += 1
        assert not study.compare(bad, "sol")["gate_passed"]
    tied = copy.deepcopy(initial)
    tied[1]["candidate_metrics"]["sol"] = 9
    assert not study.compare(tied, "sol")["gate_passed"]


def test_pivot_requires_sufficient_denominator_and_strict_majority():
    initial = rows()
    assert study.compare(initial, "sol")["pivot_trigger"]
    initial[1]["rejections"]["completed_rejected"] = 9
    assert not study.compare(initial, "sol")["pivot_trigger"]
    initial[1]["rejections"] = {"completed_rejected": 10, "SOL_better_SOC_worse": 5}
    assert not study.compare(initial, "sol")["pivot_trigger"]


def test_relocated_replay_journal_records_the_executed_worker(tmp_path, monkeypatch):
    package = tmp_path / "research/fresh-replay"
    package.mkdir(parents=True)
    monkeypatch.setattr(study, "PACKAGE", package)
    monkeypatch.setattr(study, "ROOT", tmp_path)
    commands = []

    def stop_worker(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=7, stdout="", stderr="controlled stop")

    monkeypatch.setattr(study.subprocess, "run", stop_worker)
    seed = hashlib.sha256(bytes.fromhex("00") + b"tiny:0").digest()[:16]
    plan = {"seed_hex": "00", "resource_caps": {"overall_research_cutoff_utc": "2050-01-01T00:00:00Z"},
            "cases": [{"case": "tiny", "panel": "development", "seeds": [
                {"trial": 0, "seed_hex": seed.hex(), "seed_decimal": str(int.from_bytes(seed, "big"))}]}]}
    study.run_batch("probe", "dev-primary", "development", "sol", plan, {})
    event = json.loads((package / "probe-dev-primary.jsonl").read_text())
    assert len(commands) == 1 and event["command"] == commands[0]
    assert Path(event["command"][1]) == package / "run_one.py"
