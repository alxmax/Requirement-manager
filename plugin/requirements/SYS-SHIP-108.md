---
id: SYS-SHIP-108
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Adopting and shipping the engine

> As someone bringing the engine into a repository, or releasing a new version of it, I 
> want the bootstrap, the version guards and the published artifacts to agree, so that a 
> consumer picks up a change instead of silently keeping an old copy.

Scenario: a release reaches a consumer
  Given  an engine change and a repository that vendors it
  When   the release is cut and the consumer updates
  Then   the version guards refuse a change that would ship unannounced, and the consumer is told when its vendored copy has fallen behind

## Requirements in this system (auto)
- `ARCH-CMDREGISTRY-033` — CLI command registry + generated integration artifacts  (architecture)  ·  7 detailed design
- `ARCH-INIT-012` — First-use bootstrap  (architecture)  ·  11 detailed design
- `ARCH-PYFLOOR-040` — Declared Python support floor  (architecture)  ·  5 detailed design
- `ARCH-REPRO-041` — Committed build artifacts stay re-derivable  (architecture)  ·  6 detailed design
- `ARCH-SELFGATE-039` — This repo's own gate wiring  (architecture)  ·  6 detailed design
- `ARCH-STALEENGINE-043` — Stale vendored engine, reported in CI  (architecture)  ·  12 detailed design
- `ARCH-TRANSLATE-044` — Opt-in requirement-content translation  (architecture)  ·  10 detailed design
