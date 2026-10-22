# First contribution packages

Intake is open. Choose one task and return a complete handoff, including failures.
See EVALUATION.md for exposure rules and FIRST_REVIEW.md for independent review.
Budgets are defaults for trial sessions, not a reason to refuse explicitly authorized
larger work. Record extensions and actual resources.

## replication: Produce one verified handoff from the current maze incumbent

Budget: 30 minutes; 3,000 popped search states.

```sh
python tools/contribute.py --case maze-32-32-4-s3-n128 --variant random4 --seed 419 --nodes 3000 --out research/my-first-trial
```

Deliverable: candidate.json, trace.json and handoff.json; verify with tools/verify_candidate.py against data/round2/maze-32-32-4-s3-n128.json. An unchanged valid plan completes the task.

## baseline: Audit the LNS2/LaCAM objective mismatch and common metrics

Budget: 60 minutes; use the fixed baseline protocol, no parameter search.

```sh
python tools/check.py --quick
```

Deliverable: Reproduce one comparison, check route semantics and report SOC, SOL, makespan, failures, wall/CPU time and source identity. A reproduced failure or budget mismatch is useful.

## headroom: Rank current cases by obstacle-aware lower-bound gaps

Budget: 30 minutes; all 20 existing cases.

```sh
python tools/headroom.py --out research/headroom-review.json
```

Deliverable: Audit one lower bound and identify a case whose remaining gap justifies repair. A loose bound is not evidence that the gap is achievable.

## verification: Audit goal revisits and collision rejection

Budget: 30 minutes; one minimized counterexample or scoped audit.

```sh
python -m pytest -q tests
```

Deliverable: Report exact case, claim, commands and outcome; never weaken the checker to accept the witness.
