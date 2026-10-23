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
The replay matches all non-timing fields and all source hashes. Saved replay,
journal and comparison are included. A follow-up Standards review is requested
before publication.

## Spec

Round 1 reported no spec findings. Goal departures remain available and charged;
stale pops consume the cap; capped bounds use the frontier after complete
expansions; aggregation preserves disjointness and incumbent consistency. The
20-case, 521-pair panel, journals, integer sums and source hashes reconcile. The
reviewer ran all five tiny controls and reproduced both capped pair results;
it did not rerun the full panel or baseline tests.

The later separate threshold checker and its negative controls are additional
author verification. A follow-up Spec review is requested for those additions
before publication.

Initial totals: Standards 1 finding (pilot source retention, repaired); Spec 0.
