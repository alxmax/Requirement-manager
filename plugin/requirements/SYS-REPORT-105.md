---
id: SYS-REPORT-105
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
milestone: v2.32
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Answering what is here and what to do next

> As someone picking up the project, I want to ask where a capability lives, what is 
> unfinished and what deserves attention first, so that I can act without reading every 
> file.

Scenario: the corpus is interrogated
  Given  a corpus with confirmed, drafted and unbacked requirements
  When   the reporting commands run
  Then   each answers one question about the corpus from the same scan, and none of them writes to it

## Requirements in this system (auto)
- `ARCH-COVERAGE-029` — Untagged-code coverage signal  (architecture)  ·  10 detailed design
- `ARCH-FINDINGS-010` — Open-findings report  (architecture)  ·  18 detailed design
- `ARCH-HEALTH-017` — Corpus health snapshot  (architecture)  ·  12 detailed design
- `ARCH-NEXT-013` — What-should-I-do-next report  (architecture)  ·  23 detailed design
- `ARCH-REGISTRYLAG-035` — Registry-lag signal — commits since the requirements dir was last touched  (architecture)  ·  10 detailed design
- `ARCH-ROADMAP-038` — Roadmap coherence signals  (architecture)  ·  8 detailed design
- `ARCH-SCAN-005` — List members per capability  (architecture)  ·  4 detailed design
- `ARCH-SEARCH-036` — Free-text requirement search  (architecture)  ·  19 detailed design
- `ARCH-SHOW-015` — Single-requirement dossier  (architecture)  ·  13 detailed design
