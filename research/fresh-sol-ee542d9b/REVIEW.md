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
