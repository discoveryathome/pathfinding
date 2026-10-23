"""Derive an honest paired summary and proposed witness index; no archive edits."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="a1")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = (PACKAGE / args.out).resolve()
    if output.parent != PACKAGE or output.exists():
        parser.error("Use a new summary filename")
    protocol = json.loads((PACKAGE / "protocol.json").read_text())
    primary = json.loads((PACKAGE / f"{args.attempt}-dev-primary.json").read_text())
    selection = json.loads((PACKAGE / f"{args.attempt}-development.json").read_text())
    batches = [primary]
    if selection["pivot_batch"]:
        batches.append(json.loads((PACKAGE / selection["pivot_batch"]).read_text()))
    evaluation = PACKAGE / f"{args.attempt}-evaluation.json"
    if evaluation.exists():
        batches.append(json.loads(evaluation.read_text()))
    rows = [row for batch in batches for row in batch["rows"]]
    methods = {}
    for method in sorted({r["method"] for r in rows}):
        selected = [r for r in rows if r["method"] == method]
        status = Counter()
        for row in selected:
            status.update(row["status_counts"])
        methods[method] = {"runs": len(selected), "core_seconds": sum(r["core_elapsed_seconds"] for r in selected),
                           "preprocess_seconds": sum(r["preprocess_seconds"] for r in selected),
                           "worker_user_cpu_seconds": sum(r["worker_user_cpu_seconds"] for r in selected),
                           "worker_system_cpu_seconds": sum(r["worker_system_cpu_seconds"] for r in selected),
                           "search_pops": sum(r["budget"]["nodes_used"] for r in selected),
                           "accepted_steps": sum(r["accepted_routes_checked"] for r in selected),
                           "status_counts": dict(status)}
    proposals = []
    for case in protocol["cases"]:
        choices = [r for r in rows if r["case"] == case["case"]]
        best = min(choices, key=lambda r: (*[r["candidate_metrics"][key] for key in ("sol", "soc", "makespan")],
                                         r["method"], r["trial"]))
        metrics = {key: best["candidate_metrics"][key] for key in ("sol", "soc", "makespan")}
        initial = case["start"]["metrics"]
        proposals.append({"case": case["case"], "inherited": case["start"], "metrics": metrics,
                          "SOL_gain_from_declared_start": initial["sol"] - metrics["sol"],
                          "SOC_gain_from_declared_start": initial["soc"] - metrics["soc"],
                          "makespan_gain_from_declared_start": initial["makespan"] - metrics["makespan"],
                          "method": best["method"], "trial": best["trial"], "candidate": best["candidate"],
                          "candidate_sha256": best["candidate_sha256"],
                          "interpretation": "After-search best of the declared runs; proposed witness only, not policy success rate or accepted archive."})
    paired = {}
    for batch in batches:
        pairs = batch["comparison"]["pairs"]
        paired[batch["stage"]] = {"pairs": len(pairs), "SOL_wins": sum(x["SOL_delta"] < 0 for x in pairs),
                                  "SOL_ties": sum(x["SOL_delta"] == 0 for x in pairs),
                                  "SOL_losses": sum(x["SOL_delta"] > 0 for x in pairs),
                                  "SOL_delta_sum": sum(x["SOL_delta"] for x in pairs),
                                  "SOC_delta_sum": sum(x["SOC_delta"] for x in pairs),
                                  "SOC_regressions": sum(x["SOC_delta"] > 0 for x in pairs),
                                  "makespan_regressions": sum(x["makespan_delta"] > 0 for x in pairs)}
    result = {"selected": selection["selected"], "methods": methods, "paired": paired,
              "proposals": proposals, "proposed_SOL_improved_cases": sum(x["SOL_gain_from_declared_start"] > 0 for x in proposals),
              "summed_proposed_SOL_gain": sum(x["SOL_gain_from_declared_start"] for x in proposals),
              "summed_proposed_SOC_gain": sum(x["SOC_gain_from_declared_start"] for x in proposals),
              "exposed_inputs": True, "evidence_level": "author-checked", "archive_changed": False,
              "protocol_sha256": hashlib.sha256((PACKAGE / "protocol.json").read_bytes()).hexdigest()}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "proposals"}))
