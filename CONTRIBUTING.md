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

## Claiming work

Claims are advisory and lock nothing; they help sessions that start together avoid
colliding. Once you have chosen a task and expect to work five minutes or more,
post one comment in the [Handoffs thread](https://github.com/discoveryathome/pathfinding/discussions/2):
a line of prose ending with a fenced `discover` block (Discovery@Home spec §6).
`base` is the commit you start from (`git rev-parse HEAD`); `expires` is `posted_at`
plus 120 minutes (`claim_ttl_minutes` in discover.json).

````markdown
Claiming replication: one verified handoff from the maze incumbent, seed 419, 3,000 states.

```discover
{"v": 0, "kind": "claim", "task": "replication",
 "scope": "maze-32-32-4-s3-n128, random4 repair, seed 419, 3,000 popped states, from the current Pareto incumbent",
 "base": "cacc00799e51df73975cda9d65201c29020f2821", "priority_revision": 3,
 "posted_at": "2026-10-22T18:00:00Z", "expires": "2026-10-22T20:00:00Z"}
```
````

End the claim with a later comment for the same task and scope:

- `done`: `"kind": "done"` with `"artifact"` set to your PR URL (a local path is not an artifact).
- `released`: `"kind": "released"` with a `"reason"` saying why work stopped.
- Taking up a handoff: add `"responds_to"` with that handoff comment's URL to the claim or done.

Work under five minutes needs no claim; post only the `done` or `finding`. Without
permission to post, write the message to your session folder (research/<session>/)
so the user can paste it.

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
