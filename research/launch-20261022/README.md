# Launch to donated sessions, 2026-10-22

Base commit: `base-commit.txt`. With the maintainer's consent (Douglas Colkitt,
@Mister-Meeseeks) the project is listed on the Discovery@Home hub
(`hubs` in discover.json) with surge review capacity; `process_changed_on` is
2026-10-22. No experiment, witness, oracle, frontier or catalogue weight changed.
Scientific acceptance and independent review remain pending.

## Rebinding

`research/manifest.json` hash-binds every tracked file. The launch edited AGENTS.md,
CONTRIBUTING.md (claim example), DISCOVERY.md, DISTRIBUTION.md, PARTICIPATION.md, README.md, THIRD-PARTY.md,
discover.json, discover/priority-log.md and tools/check.py, and replaced one build log
(below). Their bindings were rebound; the launch-time values are in
`research/manifest.json` under `rebound.original_sha256` (`null` for files that did
not exist). `prior-manifest.json` is the whole manifest as of the base commit, and
`prior-files/` holds the base-commit copies of the edited files. `tools/check.py`
requires every binding in this prior manifest, and in the distribution-preparation
prior manifest, to be met by a live file or an archived copy with the same hash.

## Third-party material

The MAPF-LNS2 build log `research/distribution-prep-20261022/build-lns2.log` quoted
125 lines of upstream source (and a few libc++ header lines) in compiler
diagnostics. MAPF-LNS2 is under the USC Research License, which permits
non-commercial use only, so its source is not redistributed here. The log is replaced
by `build-lns2.redacted.log`: every line is kept except the quoted source and caret
lines, which become one placeholder per excerpt; all 14 warnings and 34 notes remain,
including one warning that was interleaved into a quoted line. The original is cited
under `not_stored` in `research/manifest.json` (upstream URL at the pinned commit,
access date, SHA-256, `"stored": false`) and remains in git history. No check reads
the log, so check outputs are unchanged.

All other stored third-party material is openly licensed: Moving AI maps and
scenarios (ODC Attribution 1.0) and the Discovery@Home schemas (Apache-2.0).
