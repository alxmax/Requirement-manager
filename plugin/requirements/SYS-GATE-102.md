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
lint_exempt: [fan-out]
---
# Keeping code and specification in step

> As someone committing a change, I want the engine to tell me when the code and the 
> requirements have moved apart, so that a spec nobody honours stops passing for 
> documentation.

Scenario: a confirmed contract changes without its code
  Given  a confirmed requirement whose contract text has been edited
  When   the gate runs
  Then   it reports the drift and names the members and dependents to re-check, without advancing the baseline itself

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

## Context
**Notes**
- `lint_exempt: [fan-out]`: eleven architecture requirements satisfy this need since ARCH-RULES-059 joined (ADR-0023's `system` ceiling is ten). One over the band is not a bucket yet; splitting the gate need into link-sync and drift halves is deferred until a twelfth arrives.
