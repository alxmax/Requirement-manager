---
id: SYS-GATE-102
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
milestone: v2.32
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Keeping code and specification linked

> As someone committing a change, I want the build to fail when a code tag or a
> requirement points at something that is not there, so that the links between the
> specification and the code can be trusted without checking them by hand.

Scenario: a tag names a requirement that does not exist
  Given  a source file tagged `implements:` with an id no requirement declares
  When   the gate runs
  Then   it fails with an error naming the tag and where it is

## Requirements in this system (auto)
- `ARCH-DRIFT-003` — Contract hashing & lock  (architecture)  ·  8 detailed design
- `ARCH-ACVERIFY-019` — Per-criterion test coverage  (architecture)  ·  11 detailed design
- `ARCH-CHECK-006` — The gate  (architecture)  ·  34 detailed design
- `ARCH-DOCBUNDLE-026` — Untagged doc-bundle warning  (architecture)  ·  8 detailed design
- `ARCH-DRIFTIMPACT-035` — Drift blast-radius: name dependents  (architecture)  ·  5 detailed design
- `ARCH-MEMBERDRIFT-027` — Reverse-direction member drift  (architecture)  ·  8 detailed design
- `ARCH-ORPHANCODE-034` — Orphan-code warning  (architecture)  ·  10 detailed design
- `ARCH-TESTLINK-018` — Test-link integrity check  (architecture)  ·  17 detailed design
- `ARCH-TRACKED-042` — Untracked members reported  (architecture)  ·  5 detailed design
- `ARCH-UNSCANNEDTAG-045` — Tags in unscanned file types reported  (architecture)  ·  7 detailed design
