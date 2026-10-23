# Author-assisted review record

Final narrow Standards and Spec rechecks at `fbee9a1` report no remaining
findings for the intermediate-ID guard and its provenance. Five focused tests
across the two later fresh-study checkers and this one passed; the Spec reviewer
also exercised sixteen additional adversarial mappings per checker. All 313
retained intermediates match unique accepted history rows. Reviewers did not
rerun geometry or full audits; root's V4 audit independently checked all 120
finals and 313 intermediates, and the complete 34-test suite plus quick check
passed. Prior proof/review conclusions were reused, not promoted to human signoff.

An additional author control requires every retained intermediate's attempt ID
to be an integer within the recorded history. Previously an extra negative or
out-of-range entry could remain unvisited. All actual retained intermediates use
valid IDs; original outcomes are unchanged. V4 adds the bounds assertion and a
regression rejecting -1 and 96 on an otherwise valid 96-attempt trace. The full
suite now has 34 passing tests; the new full audit is retained separately.

A later fresh-study preflight identified that both engines' elapsed timer
includes preprocessing. This package's historical fields named
`core_elapsed_seconds` / `core_seconds` therefore mean inclusive engine time.
The original fields and results remain unchanged; `clarify_timing.py` and
`timing-clarification.json` retain the exact derivation of core time after
subtracting preprocessing from all 60 runs per method. README labels now match
that accounting. This is an author-checked documentation/derived-accounting
correction, not an optimizer rerun or an extension of the earlier review scope.

This package receives separate Standards and Spec agent reviews against canonical
base `37823dca1bea271510e3ed62205620466ec6f0f9`. The reviews are commissioned by the
author and do not constitute independent human scientific acceptance.

## Standards round 1 at 0edb0a7

Two P2 documentation findings:

1. README reproduction commands used absolute `/tmp` output paths, but the
   auditor and summarizer accept only unused direct package filenames. Both
   documented commands exited 2 before doing their advertised work. This
   violated DISCOVERY.md's reproducibility requirement.
2. The full replay instructions suggested that a new attempt ID was sufficient,
   although the frozen runner still enforces the absolute session cutoff. An
   in-memory next-day probe completed 0/18 runs without launching a worker.
   DISCOVERY.md and DISTRIBUTION.md require reproducible instructions and a
   separate, freshly identified replay package.

Response: corrected both commands to unused package-relative filenames and
documented a separate replay package with newly recorded cutoffs, committed
source identity and preserved original evidence. The frozen method, protocol and
all original experiment outputs remain unchanged.

The reviewer inspected source/input/artifact hashes, both journals, all 120 run
records, recorded 313 intermediates and resource/result totals. It did not rerun
route auditing, the optimizer panel or native solvers, and did not re-review math.

## Spec round 1 at 0edb0a7

Two P2 findings in the separate auditor:

1. Removing all 96 attempts and 34,813 pops from a development arrival run,
   then updating dependent counts/hashes, passed the outer audit. Protocol
   reporting requires all attempts and failures; the checker needed to require
   96 attempts unless the 100,000-pop budget was consumed.
2. The current-file-hash shortcut accepted an all-zero code commit and the
   canonical base that lacks the method. Protocol source freeze requires a
   recorded source version; current hashes alone did not establish that binding.

Response: require full attempt coverage or total pop exhaustion, and always
compare the complete manifest against recorded Git blobs. Missing history is
explicitly rejected; source-archive provenance is no longer silently accepted.
Regression controls cover empty/partial histories with self-consistent counts
and both invalid commit identities. Original audit output/source remain in
history; `verification-v2.json` records a full audit under the tightened checker.
No optimizer, input, protocol, selection or run output was corrected.

The reviewer passed all 31 prior tests, checked 60 seed derivations and all 120
record/artifact hash sets, and checked geometry for 18 finals and 58 accepted
intermediates. It did not replay the full optimizer, check the remaining route
geometry, run native solvers or establish exhaustive optimality.

## Spec round 2 at 6d7a063

No remaining actionable Spec findings in the narrow follow-up. The original
34,813-pop trace passed; consistently updated 0-, 1- and 95-attempt prefixes
failed. A shortened trace passed at exactly 100,000 pops and failed at 99,999.
Both recorded commits passed source checks; zero/base IDs, a wrong hash and
unavailable history failed. Five focused verifier tests passed. Prior frozen
solver/math conclusions were reused. This reviewer did not run the pending V2
audit, optimizer replay, additional route geometry or native solvers.

## Standards round 2 at 6d7a063

Both original reproduction-documentation findings were verified as resolved.
Two additional P2 provenance findings:

1. Git tree `049b4401263313ecd58e03930e2dc6f87d6eeabf` passed the manifest helper,
   because `git show oid:path` accepts trees as well as commits. AGENTS.md and
   research/REVIEW.md require correct source identity; README promised a commit.
2. In a relocated package the executed worker path changed but the journal's
   hardcoded worker path still named the original package. CONTRIBUTING.md and
   FIRST_REVIEW.md require faithful source/command provenance.

Response at `c88118c`: require the Git object's type to be exactly `commit` and
add a real retained-tree rejection control. Journal the exact command passed to
the subprocess; a copied-package test with a controlled failed worker compares
the recorded command to the executed one. The first new test run exposed a
misplaced test-fixture line (`NameError`); its placement was corrected before
commit, then all 33 tests passed. The runner correction concerns future replay
bookkeeping only; original frozen sources and outputs remain retained.

## Versioned audit evidence

V1 source is recoverable at `0edb0a7`, V2 at `6d7a063` and V3 at `c88118c`.
Each of `verification.json`, `verification-v2.json` and `verification-v3.json`
binds its actual verifier SHA-256 and checks all 120 final plus 313 accepted
intermediate routes. Original experiment source manifests still bind the
development/evaluation commits, including the original runner. Final evidence
does not relabel the earlier checks as independent review or optimizer replay.

## Standards round 3 at c88118c

No new findings; both outstanding P2s resolved. The actual offending tree is
rejected, valid historical manifests pass, and the relocated-worker regression
confirms journal/command equality. Three focused tests passed. All 120 records'
ten-file manifests match retained blobs: 18 development records at `5c54e6e` and
102 evaluation records at `b99c1ec`. Frozen original evidence remains unchanged.
No useful additional smell finding. The reviewer did not run the full 33-test
suite, execute the V3 audit, check route geometry, replay optimizers, run native
solvers or renew math/Spec review. Root separately ran the full suite and V3
audit recorded above. Both axes are author-assisted; human signoff remains pending.
