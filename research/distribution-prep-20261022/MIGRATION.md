# Historical migration and reproducible evaluation

The distribution-preparation round updates onboarding and task routing. Original
experiment inputs, sources and results are retained. Every changed historical
entry-point file is saved under prior-files/ and its prior hash remains in
prior-manifest.json. The current manifest is refreshed to describe the current
package. This is an explicit versioned migration, not silent rewriting of evidence.

Intake remains open. Independent first-contributor and scientific reviews are
pending; FIRST_REVIEW.md is the complete uncoached handoff packet. No outside
reviewer or subagent was used in this preparation. No repository was published
or external message sent.

Linux execution was attempted on 2026-10-22 via the installed Docker Desktop.
The engine did not answer a bounded 15-second info request, including after
opening Docker. Existing long-running Docker processes from other work were
left untouched; no reset/restart or privileged reconfiguration was performed.
Dockerfile and CI recipes are prepared, but Linux execution remains unverified.
A successful macOS source-archive smoke is operational author testing only.
