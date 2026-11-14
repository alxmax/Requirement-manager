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
- `ARCH-ACVERIFY-019` — Per-criterion test coverage  (architecture)
- `ARCH-CHECK-006` — The gate  (architecture)
- `ARCH-GITRUN-067` — Talking to git  (architecture)
- `ARCH-RETIRE-064` — Taking a requirement out of service  (architecture)
- `ARCH-RULES-059` — The gate rule registry  (architecture)
- `ARCH-TESTLINK-018` — Test-link integrity check  (architecture)
- `ARCH-UNREADABLE-070` — Source files the scan cannot decode  (architecture)
- `ARCH-UNSCANNEDTAG-045` — Tags in unscanned file types reported  (architecture)
