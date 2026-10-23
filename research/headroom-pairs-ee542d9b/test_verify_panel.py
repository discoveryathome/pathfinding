"""Failure controls for the separate lower-bound checker."""
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("verify_panel", Path(__file__).with_name("verify_panel.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_source_manifest_requires_every_declared_path():
    source = json.loads((verify.PACKAGE / "panel.json").read_text())["source_sha256"]
    verify.validate_sources(source)
    variants = [{}, {**source, "unexpected.py": "0" * 64}]
    variants.extend({key: value for key, value in source.items() if key != missing} for missing in source)
    for invalid in variants:
        with pytest.raises(ValueError, match="complete declared source manifest"):
            verify.validate_sources(invalid)


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
    verify.check_matching([edge(0, 1), edge(2, 3)], 4)
    for pairs in ([edge(0, 1), edge(1, 2)], [edge(0, 0)]):
        with pytest.raises(ValueError, match="Overlapping or malformed"):
            verify.check_matching(pairs, 4)


def test_negative_agent_alias_is_rejected():
    # On four agents, -1 and 3 name the same Python-indexed agent.
    for invalid in (-1, 4, True, 1.0):
        records = [{"witness": {"agents": [invalid, 0]}}, {"witness": {"agents": [3, 1]}}]
        with pytest.raises(ValueError):
            verify.check_matching(records, 4)


def test_canonical_case_coverage_and_pair_identity():
    import copy
    archive = {name: {"instance": name + ".json", "pareto_candidates": [{"path": name}]}
               for name in ("a", "b")}
    fixed = {name: [{"agents": [0, 1], "time": 1, "kind": "vertex"}] for name in archive}
    rows = [{"case": name, "instance": item["instance"], "inherited": item["pareto_candidates"][0],
             "pair_results": [{"case": name, "witness": fixed[name][0]}]}
            for name, item in archive.items()]
    verify.validate_scope(rows, archive, fixed)
    with pytest.raises(ValueError, match="exactly once"):
        verify.validate_scope([rows[0], rows[0]], archive, fixed)
    altered = copy.deepcopy(rows)
    altered[0]["pair_results"][0]["witness"]["agents"] = [0, 2]
    with pytest.raises(ValueError, match="canonical matching"):
        verify.validate_scope(altered, archive, fixed)
    altered = copy.deepcopy(rows)
    altered[0]["instance"] = "another.json"
    with pytest.raises(ValueError, match="canonical instance"):
        verify.validate_scope(altered, archive, fixed)
