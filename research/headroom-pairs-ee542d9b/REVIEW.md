# Two-axis author-assisted review

Fixed point: `37823dca1bea271510e3ed62205620466ec6f0f9`.
Reviewed frozen implementation: `92c1d8c74c94f0dc65e6a3a04b63b89253a731af`.
Reviews by separate gpt-6.1-sol code-review-skill agents, not independent human
scientific signoff. Source protocol and repository contribution/evaluation rules
were the spec and standards sources.

## Standards

Round 1 found one P2 issue: the pilot identified protocol-only commit `9f29e7f`
and script hashes whose earlier matching versions were not retained. This breached
CONTRIBUTING.md's reproducible source/evidence retention and EVALUATION.md's source
identity/corrected-attempt preservation requirements. No additional documented
standard or baseline-smell findings were reported.

Response: recover both exact hash-matching script versions in `pilot-source/`,
leave the original output unchanged, and replay in a detached `9f29e7f` checkout.
The replay matches all deterministic fields and all source hashes, excluding
timestamps, timings and peak RSS. Saved replay,
journal and comparison are included. The round-2 Standards task failed at model
capacity without running; a new follow-up will check this repair and later additions.

## Spec

Round 1 reported no spec findings. Goal departures remain available and charged;
stale pops consume the cap; capped bounds use the frontier after complete
expansions; aggregation preserves disjointness and incumbent consistency. The
20-case, 521-pair panel, journals, integer sums and source hashes reconcile. The
reviewer ran all five tiny controls and reproduced both capped pair results;
it did not rerun the full panel or baseline tests.

Round 2 found two P2 issues in the separate threshold checker. Negative IDs could
alias positive Python indices and bypass disjointness; matching validation now
requires integer IDs inside the actual instance range. Counts also permitted a
duplicate case to replace another while retaining 20 rows and 521 pairs. The
checker now requires exact canonical case coverage, instance/incumbent binding,
and pair witness identity against the pinned published headroom scope. Rejecting
regression tests cover both. The saved panel already has canonical IDs/scope, and
all three checker versions certify identical numerical bounds. Original checker
sources/outputs remain in git history; versioned final output is verification-v3.json.

Round 2 also checked the original retained panel, reproduced 124,151 verification
pops and compared the threshold routine with the unpruned oracle on all 1080 tiny
assignments. It did not rerun frozen-solver or baseline tests. A final follow-up
will check the two fixes. Author verification passes all 31 tests and quick hashes.

Round 3 Standards confirmed the source-retention repair and recovered checker
source versions. It found one P3 wording defect: replay peak RSS differs, so the
claim of every non-timing field matching was too broad. Documentation now says
deterministic fields and explicitly excludes timestamps, timings and peak RSS.
The original comparison is retained, with pilot-replay-check-v2.json superseding
its overly broad flag. No other standards or useful smell findings were reported.

Round 3 Spec confirmed both checker fixes with no new findings. Read-only probes
tested 28,561 four-agent combinations (only 24 valid disjoint matchings passed),
rejected 16 invalid coverage/alias mutations, and checked canonical scope, source
hashes, journal equality and V3 bindings. It reused the prior threshold/frozen-solver
correctness review and did not rerun the full panel. The final docs-only wording
correction does not change the reviewed checker.

Final totals: Standards 2 findings (P2 source retention, P3 replay precision; both
repaired); Spec 2 findings (P2 identifier/scope validation; both repaired).
No unresolved finding or frozen-solver defect. All checks remain author-assisted.
