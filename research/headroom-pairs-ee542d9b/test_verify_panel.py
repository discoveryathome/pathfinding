"""Failure controls for the separate lower-bound checker."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("verify_panel", Path(__file__).with_name("verify_panel.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_certification_rejects_inflation_and_remains_inconclusive_at_cap():
    adj = {0: (1, 3), 1: (0, 2, 4), 2: (1, 5), 3: (0, 4), 4: (1, 3, 5), 5: (2, 4)}
    ds = [verify.wavefront(adj, goal) for goal in (2, 0)]
    assert verify.certify(adj, (0, 2), (2, 0), ds, 6)["verified"]
    inflated = verify.certify(adj, (0, 2), (2, 0), ds, 7)
    assert not inflated["verified"] and inflated["cost"] == 6
    capped = verify.certify(adj, (0, 2), (2, 0), ds, 6, pop_cap=0)
    assert not capped["verified"] and capped["reason"] == "verification_cap"


def test_checker_handles_goal_departure_and_SOC_SOL_distinction():
    adj = {0: (1,), 1: (0, 2), 2: (1, 3), 3: (2, 4, 8), 4: (3,), 8: (3,)}
    ds = [verify.wavefront(adj, goal) for goal in (3, 4)]
    assert verify.certify(adj, (8, 0), (3, 4), ds, 7)["verified"]
    assert not verify.certify(adj, (8, 0), (3, 4), ds, 8)["verified"]


def test_overlapping_pair_aggregation_is_rejected():
    def edge(i, j):
        return {"witness": {"agents": [i, j]}}
    verify.check_matching([edge(0, 1), edge(2, 3)])
    for pairs in ([edge(0, 1), edge(1, 2)], [edge(0, 0)]):
        with pytest.raises(ValueError, match="Overlapping or malformed"):
            verify.check_matching(pairs)
