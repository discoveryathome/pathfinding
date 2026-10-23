# Attempt B: author-assisted review and correction record

This attempt retains a separate copy of the producer/checker sources to preserve
attempt A's protocol, source identities and failed outputs. That duplication is
intentional evidence retention, not a shared mutable implementation. The fixed
repair policy's bytes are unchanged. All six producer-preflight findings and
their resolved narrow rechecks are documented in A's `REVIEW.md`.

## Declaration and source chronology

Attempt A source was frozen at `5ea28cc`, corrected after preflight at `26a4eba`
and `d961f59`, then cleared before query generation. Inputs were committed at
`ff3cd5a`. All twelve native-default calls aborted under the declared cap; zero
repair jobs were eligible. A complete null attempt was retained at `3503edb`.

Attempt B's explicit `--no-multi-thread` configuration was declared at `d6ef3d0`
before B outcomes, on the same now-exposed query geometries and seeds. The cohort
was frozen at `ac1050e`, all twelve verified native starts at `abd5e89`, then all
72 paired workers completed without policy/configuration/input changes. Native
and repair records bind their committed source manifests. B's auditor checks
all geometry/scenario identities against A as well as recomputing every draw.
This was an infrastructure response to startup failures, not policy tuning.
The exact internal cause of the default aborts remains unestablished.

## Separate-auditor corrections

Before the complete audit, author checks found absolute recorded command paths
would fail in a relocated checkout. `command_root` now validates the recorded
package suffix and binds native paths to that recorded root while reading the
artifacts from the actual current checkout. A regression uses a different root.
No producer or raw outcome was changed. Earlier A auditor versions remain in
Git and their original outputs remain intact.

The first complete B audit failed because it compared the standalone checker's
full return (including diagnostics) with the native record's three objectives.
`audit-failure-v1.json` binds source `b515094`; the three-objective comparison was
corrected at `43caf35`. Original native/repair traces, certificates, journals and
metrics remain unchanged. `verification-v2.json` passed all twelve native routes,
72 final repairs and 1,178 accepted intermediates in 194.4142 seconds.

Additional author hardening rejects labeling a completed verified worker as a
failed row. The control writes a valid completed record and confirms rejection,
while preserving genuine timeouts and malformed-record failures. All 37 tests
pass separately in each attempt package. This guard did not change the actual
all-successful B cohort. A clean relocated checkout runs the latest full auditor
as a separate version, preserving the prior successful report/source.

## Full final reviews at 1b49626

Standards round 3: no remaining supported Standards findings. The reviewer read
the binding guidance and both attempt histories, checked 174 source-bearing
records and complete 13-file manifests, unchanged baseline/policy bytes, both
recomputed cohorts and reported results. Fourteen focused auditor controls
passed across the two packages. Frozen attempt snapshots are intentional
retention; no actionable smell finding arose. It did not rerun optimization,
native builds/upstream tests, proof review or root-owned full route/relocation
audits.

Spec round 3: no actionable Spec findings. The reviewer checked both protocols,
source/cohort/seed/journal/command/cap/history/Pareto bindings, original preservation
(41 A and 353 B files), and exact A/B geometry/scenario equality. It independently
recounted 36 pairs and the 26/9/1, -636/-349, two-SOC-regression/zero-makespan
result. Fourteen focused auditor controls passed. Prior proof/preflight conclusions
were reused; full route validation, checkout relocation, native rebuilds and
optimizer reruns were left to root or explicitly not performed.

## Author index control and narrow round 4

Root then found that an extra intermediate with an out-of-history ID could be
unvisited. Every actual retained ID was already valid. Source `9a2567f` adds
strict range binding before iteration and regressions for -1 and 96. The same
guard was added to PR #8's checker at `fbee9a1`; no optimizer/input/output changed.

Standards round 4: no remaining findings in this delta or its provenance. Five
focused controls passed across both fresh packages and PR #8. All original-base
and raw evidence remains unchanged; paired original/relocated reports agree in
every field except elapsed time. No unexplained scope or useful smell finding.
It did not repeat math/Spec, full suites, optimizer runs or full V4 audits.

Spec round 4: no remaining findings. All three orphan regressions and sixteen
additional in-memory adversarial cases per checker passed, covering missing,
extra, duplicate/boolean/noninteger/negative/out-of-history IDs and accepted-row
mapping with a checker spy. All 1,178 B and 313 PR #8 actual intermediates have
unique valid IDs exactly matching accepted history rows; metrics and hashes
match. Route geometry/full audits and frozen proof were not repeated by this
reviewer. Root separately passed both 38-test suites and full V4/relocation
checks. These are commissioned agent reviews, not independent human signoff.

## Scope and limits

Standards and Spec final reviews cover both attempts and retain findings and
responses above. Reviews are commissioned by the author and
reuse the prior frozen-policy proof; they are not independent human signoff.
The optimizer/native panel has not been rerun. No unseen map/corpus, population
inference, speed claim, full upstream native suite or independent human
scientific acceptance is established. Rejected/partial geometry that the engine
does not return cannot be separately checked. Accepted project records remain
untouched.
