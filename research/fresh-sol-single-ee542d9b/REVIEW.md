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

## Scope and limits

Standards and Spec final reviews cover both attempts and retain findings and
responses below before submission. Reviews are commissioned by the author and
reuse the prior frozen-policy proof; they are not independent human signoff.
The optimizer/native panel has not been rerun. No unseen map/corpus, population
inference, speed claim, full upstream native suite or independent human
scientific acceptance is established. Rejected/partial geometry that the engine
does not return cannot be separately checked. Accepted project records remain
untouched.
