"""Scope and agent-ID rejection controls for the full-graph checker."""
import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("verify_dual", Path(__file__).with_name("verify_dual.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_pair_ID_validation_rejects_aliases_and_duplicates():
    assert verify.pair_ids({"witness": {"agents": [0, 3]}}, 4) == [0, 3]
    for ids in ([-1, 2], [0, 4], [0, 0], [2, 1], [False, 2], [0.0, 2]):
        with pytest.raises(ValueError):
            verify.pair_ids({"witness": {"agents": ids}}, 4)


def test_exact_case_and_full_pair_scope():
    scope, archive, rows = {}, {}, []
    for name in ("a", "b"):
        witness = {"agents": [0, 1], "time": 1, "kind": "vertex"}
        scope[name] = {"instance": name + ".json", "instance_sha256": name,
                       "pairs": [witness], "fixed_matching": [witness]}
        archive[name] = {"instance": name + ".json", "pareto_candidates": [{"path": name}]}
        rows.append({"case": name, "instance": name + ".json", "instance_sha256": name,
                     "inherited": {"path": name}, "pairs": [{"case": name, "witness": witness}],
                     "fixed_matching": [witness]})
    verify.validate_scope(rows, scope, archive)
    with pytest.raises(ValueError, match="exactly once"):
        verify.validate_scope([rows[0], rows[0]], scope, archive)
    changed = copy.deepcopy(rows)
    changed[0]["pairs"][0]["witness"]["agents"] = [-1, 1]
    with pytest.raises(ValueError, match="full pair scope"):
        verify.validate_scope(changed, scope, archive)
