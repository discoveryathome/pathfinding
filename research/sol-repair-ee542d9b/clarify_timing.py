"""Derive accurate timer labels without changing frozen experiment records."""
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    sources = [PACKAGE / name for name in ("a1-dev-primary.json", "a1-evaluation.json", "summary.json")]
    batches = [json.loads(path.read_text()) for path in sources[:2]]
    summary = json.loads(sources[2].read_text())
    rows = [row for batch in batches for row in batch["rows"]]
    assert len(rows) == 120
    methods = {}
    for method in ("arrival", "sol"):
        selected = [row for row in rows if row["method"] == method]
        assert len(selected) == 60
        inclusive = sum(row["core_elapsed_seconds"] for row in selected)
        preprocessing = sum(row["preprocess_seconds"] for row in selected)
        assert abs(inclusive - summary["methods"][method]["core_seconds"]) < 1e-8
        assert abs(preprocessing - summary["methods"][method]["preprocess_seconds"]) < 1e-8
        methods[method] = {"runs": 60, "inclusive_engine_seconds": inclusive,
                           "preprocessing_seconds": preprocessing,
                           "core_excluding_preprocessing_seconds": inclusive - preprocessing}
    result = {"correction_scope": "Timer labels and derived accounting only; no optimizer rerun or original evidence edit",
              "historical_record_field": "core_elapsed_seconds includes preprocessing",
              "historical_summary_field": "methods.*.core_seconds includes preprocessing",
              "actual_core_definition": "inclusive engine elapsed minus preprocessing elapsed",
              "methods": methods, "source_sha256": {path.name: sha(path) for path in sources},
              "derivation_sha256": sha(Path(__file__)), "evidence_level": "author-checked"}
    with (PACKAGE / "timing-clarification.json").open("x") as output:
        output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(methods))
