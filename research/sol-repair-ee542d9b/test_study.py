"""Development eligibility and the predeclared pivot denominator."""
import copy
import importlib.util
from pathlib import Path
import sys

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
