# Development, replication and fresh evaluation

Intake is open. Current published cases, seeds, queries and results are exposed
calibration material. A new random seed on an old case is replication or within-
corpus variation, not a new map/corpus/workload distribution.

Before tuning, save in a new research/<session>/protocol.json: candidate source
hash, baseline commits, objective/error constraints, resource limits, development
inputs, selection rule, evaluation generator/source, planned seeds and stopping
rule. Record all attempts and failures. Freeze the selected implementation before
opening evaluation outputs; retain any subsequent correction as a separate attempt.

For an independent evaluation, a reviewer chooses fresh inputs after that freeze.
Record their provenance and hashes and disclose prior exposure. Do not put supposedly
secret cases in a public archive. Inputs revealed to any candidate-selection author
become exposed for that project. A post-hoc best-of-many archive improvement is
separate from a preselected policy's success rate.

Use the strongest applicable baseline with matched objective and comparable wall
and CPU budgets. Report startup, preprocessing and memory alongside throughput.
Repeat randomized paired timings and A/A controls; replication under shared load
is not isolated-machine performance evidence. Exact verification and a null result
are useful handoffs even without a speed or quality improvement.
