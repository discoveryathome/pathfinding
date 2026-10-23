# Author-assisted review record

The author commissioned separate Standards and Spec preflight reviews against
canonical base `37823dca1bea271510e3ed62205620466ec6f0f9`, at producer freeze
`5ea28cc`. No fresh query had been generated or fresh optimization output opened.
The SOL policy is an exact copy of the previously frozen and reviewed policy;
the new work concerns generation, adapters, fresh evaluation and separate audit.
These are agent reviews, not independent human scientific acceptance.

## Standards preflight round 1

Two P2 findings, reproduced in memory:

1. Native output conversion flattened coordinates before checking bounds.
   Replacing `(0,1)` with out-of-bounds `(3,0)` on the 3x2 control yielded the
   same verified cell 3. DISCOVERY.md requires verifying the exact candidate.
2. The repair worker checked returned routes before saving them. An invalid
   accepted intermediate caused an exception before candidate/trace creation,
   losing the returned bad geometry and history. EVALUATION.md and the protocol
   require retaining attempts and failures.

Response before fresh generation: validate signed coordinates and their bounds
before flattening; reject unparsed state content. The separate auditor also
checks raw coordinate bounds. Save each repair request before search and its
returned full trace and candidate before route checking; persist a failure
record if validation rejects them. Tests cover positive/negative coordinate
aliases and an invalid intermediate whose full returned evidence survives.
All 31 relevant tests pass. Earlier producer sources remain in `5ea28cc`;
there were no fresh-panel outcomes to correct or discard.

The reviewer checked the original 13-file diff, binding standards and connected
producer dependencies, and passed 25 tests. It did not run the panel, rebuild
native code, re-review math or check the subsequently added auditor/evidence/docs.

## Spec preflight round 1

Four P2 findings at `5ea28cc`, all before query exposure:

1. A timed-out repair worker stopped the remaining panel; a two-case probe
   launched only 1/12 scheduled runs. The protocol requires every planned pair
   within global caps, skipping only cases without a verified native start.
2. Both coordinator and worker created new process sessions. A coordinator
   timeout killed its worker but left the nested native process running. The
   reviewer reproduced this with a bounded probe and cleaned up that process.
3. The compressed trace retained the engine's numeric 128-bit seed, contrary
   to the protocol's exact-string interchange contract.
4. `core_wall_seconds` used the engine's inclusive elapsed timer, counting
   preprocessing again rather than separating preprocessing/core/full wall.

Response: preserve explicit failed-worker rows and continue the fixed schedule.
If global time/disk caps stop work, record the remaining jobs as unattempted,
without adding journal entries for calls that never ran. The pinned native is
one OS process with threads and now inherits its worker's process group, so the
coordinator timeout kills both; its own inner timeout kills that native process.
Store the trace seed as a decimal string while still passing the exact integer
to the unchanged optimizer. Record inclusive `engine_wall_seconds` and subtract
preprocessing for `core_wall_seconds`. The separate auditor checks these fields
and reports incomplete pairs separately from policy wins/ties/losses.

Regression controls cover 12 planned worker timeouts continuing to completion,
explicit unattempted cap rows, a real nested-child timeout, exact 128-bit seed
interchange and a 5-second engine / 2-second preprocessing / 3-second core timer.
All 35 relevant tests pass. No fresh queries or panel results existed during
these corrections. Earlier sources remain in the committed history.

The Spec reviewer passed 25 tests against the frozen producer and ran bounded
adapter/failure probes. It did not generate fresh inputs, run either panel,
rebuild native code, inspect later files or re-prove the frozen SOL solver.

## Narrow preflight follow-ups at d961f59

Standards round 2: no remaining actionable findings for its two P2s. Valid raw
coordinates pass, both aliases fail, and invalid returned intermediate geometry
survives in the request/candidate/full trace/failure records. Two targeted tests
passed. Frozen policy bytes match the protocol and all producer revisions.
The reviewer did not rerun the full suite, inspect the new README/auditor,
rebuild native code, generate queries or execute panels.

Spec round 2: no actionable findings; all four P2s resolved. Fourteen
producer/audit-helper controls passed, including the real nested-process timeout
with no running descendant, all 12 failed-worker attempts retained, explicit
cap rows, exact seed text and timing separation. Tracked producer files match
the reviewed commit. No full evidence audit, native rebuild, fresh generation,
panel or SOL proof review was performed in this narrow follow-up.

The complete preflight suite passed 35 tests in 1.49 seconds before any fresh
query generation. All subsequent panel/audit evidence has distinct committed
identities and is described in the final review below.
