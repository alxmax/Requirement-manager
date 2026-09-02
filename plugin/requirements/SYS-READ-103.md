---
id: SYS-READ-103
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
priority: must-have
verification: inspection
satisfies: [SYS-SSOT-001]
depends_on: []
superseded_by:
---

# Reading a repository

> As the engine, I want to read a repository's requirements and find every place the code 
> claims one, so that every other command works from one discovered picture rather than a 
> hand-maintained list.

Scenario: a repository is read end to end
  Given  a repository carrying requirement files and tagged source
  When   the engine scans it
  Then   every requirement is parsed and every tag is resolved to the requirement it names, with no list maintained by hand

## Requirements in this system (auto)
- `ARCH-PARSE-001` — Requirement reading  (architecture)  ·  10 detailed design
- `ARCH-SCAN-002` — Member discovery  (architecture)  ·  15 detailed design
- `ARCH-CANDIDATES-009` — Capability candidates (extraction plan)  (architecture)  ·  14 detailed design
- `ARCH-EXTRACT-008` — Legacy extraction  (architecture)  ·  14 detailed design
- `ARCH-MODULEFILE-056` — Several requirements in one file  (architecture)
- `ARCH-PROSE-024` — Prose capability classification & drafting  (architecture)  ·  9 detailed design
- `ARCH-SCANCACHE-023` — Opt-in scan cache  (architecture)  ·  5 detailed design
