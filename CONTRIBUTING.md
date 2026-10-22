# Contributing

Public contributions, bounded agent trials and expert reviews are welcome at
https://github.com/discoveryathome/pathfinding. This is a pre-release research pilot. Independent
scientific review remains separate from open participation.

1. Fork the repository, clone your fork, and branch from current main.
2. Read README.md, FIRST_TASKS.md and EVALUATION.md; install with tools/setup.sh.
3. Choose one scoped task. Check open PRs, issues and discussions for overlap.
4. Save new work in research/<unique-session>/ with source/input hashes, seeds,
   resources, all attempts, verification output and author/agent provenance.
5. Run the candidate-specific checker and tools/check.py --quick. Submit a PR
   targeting main with the complete handoff and relevant test results.

An unchanged candidate, replication, negative result, minimized defect or scoped
review can be a complete contribution. Do not overwrite frozen evidence or change
an oracle to pass a candidate. Current package hashes include maintained code and
docs; intentional changes require updating research/manifest.json while retaining
historical evidence and the checks against archived manifests. New experiment
outputs belong in a new directory. CI runs on public PRs; first-time contributors
may need a maintainer to approve the GitHub Actions run.

Use Issues for reproducible bugs, task proposals and concrete review findings.
Use Discussions for questions, experimental plans, coordination and review handoffs.
Keep code and machine-checkable evidence in a PR. No issue assignment or speedup is
required to start. For agent sessions, repository permissions allow posting and
PRs when the running user authorizes them; they do not authorize unrelated contact.

State baseline and metric definitions precisely, disclose prior exposure, and keep
sampled evidence distinct from proofs and independently accepted results. Include
failures and null results. Credit upstream work and preserve THIRD-PARTY.md notices.
Changes to accepted frontiers, merges and scientific acceptance are maintainer
responsibilities. Treat contributors respectfully and keep reviews evidence-based.
