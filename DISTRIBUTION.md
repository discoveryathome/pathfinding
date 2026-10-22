# Multi-agent pathfinding: pre-release distribution

**Open for bounded contributor trials and expert-agent reviews.** Share the source
archive or Git bundle from this release with reviewers and trial contributors.
No remote repository, hub enrollment, external message or public launch is implied.
The local `file:` canonical URI is provenance for this preparation checkout; it is
not a fetchable shared remote. Assign the real canonical URL when a remote is created.

## Scope and evidence

Discrete static-grid planning for labeled point agents; no physical-robot validation.

Read research/ASSESSMENT.md and research/round2/ASSESSMENT.md before making claims.
Round-two evidence is author-run. Scientific review remains pending, independently
of open intake. An unchanged candidate, minimized defect or careful replication
is a valid contribution; no improvement is required for a complete handoff.

## First session

Tested platform: macOS/Apple Clang, Python 3.12. A Linux CI recipe is included but
its result is not claimed until that workflow actually runs. Native artifacts are
rebuilt on the recipient's machine. Source archives exclude vendor code, binaries
and environments; setup retrieves pinned upstream sources with their own licenses.
Requires Git, a C/C++ compiler, Python 3.12 and uv.

```sh
sh tools/setup.sh
source .venv/bin/activate
python tools/check.py --quick
python tools/pick.py --seed 419
python tools/contribute.py --case maze-32-32-4-s3-n128 --variant random4 --seed 419 --nodes 30000 --out research/my-first-trial
python tools/verify_candidate.py data/round2/maze-32-32-4-s3-n128.json research/my-first-trial/candidate.json
```

Use a new output directory for every session. Include the entire handoff folder,
code changes, seed, limits, all failures, environment, baseline and source hashes.
Declare prior exposure and human/agent authorship. Do not call a fresh-query run
on these published corpora/scenarios an unseen holdout. Do not change frozen
results or weaken the oracle to pass a candidate.

`python tools/check.py` runs the suite and original evidence checks;
`python tools/check_round2.py` checks round-two evidence. Full evidence checks can
take several minutes; they are not required after every small candidate.

## Expert handoff

Review research/REVIEW.md. Identify the exact commit and scope, reproduce one
certificate, examine a negative control, and report baseline/semantic gaps with
concrete evidence. Keep agent review distinct from independent human expertise.
Submit the handoff through the channel used to share this package; there is no
configured external posting destination. Local posting permissions do not close
intake. Maintainer acceptance and public claims are separate decisions.

## Reproduction

Original trial outputs remain frozen. Re-run an experiment in a separate copy and
use a fresh research package; native deadlines and performance timings can differ.
Pinned sources, benchmark licenses and data attribution are in THIRD-PARTY.md and
research/round2/. A Git bundle preserves both original and current commits.

## Distribution preparation

Choose a concrete package in [FIRST_TASKS.md](FIRST_TASKS.md); `python tools/pick.py --task replication` selects the first-session task. Read [EVALUATION.md](EVALUATION.md) and [FIRST_REVIEW.md](FIRST_REVIEW.md). Current baseline and platform status is in research/distribution-prep-20261022/STATUS.md.
