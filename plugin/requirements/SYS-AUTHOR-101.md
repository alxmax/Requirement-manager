---
id: SYS-AUTHOR-101
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
milestone: v2.32
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Authoring and evolving a requirement

> As someone writing down what the system must do, I want one command to scaffold a 
> requirement and one to promote it once code backs it, so that the corpus grows in a 
> shape the engine can read instead of by hand-copying a template.

Scenario: a capability goes from idea to confirmed
  Given  a capability that has just been built
  When   an author scaffolds a requirement for it and confirms it
  Then   the file carries the schema the gate reads, and its status reflects that code now backs it

## Requirements in this system (auto)
- `ARCH-ATOMICFORM-053` — The atomic requirement form  (architecture)
- `ARCH-ATOMICITY-049` — Statement atomicity  (architecture)  ·  13 detailed design
- `ARCH-CONTEXT-048` — Consolidated Context section  (architecture)  ·  6 detailed design
- `ARCH-DECOMPOSE-050` — Clause decomposition scaffold  (architecture)  ·  11 detailed design
- `ARCH-NEW-004` — Scaffold a requirement  (architecture)  ·  8 detailed design
- `ARCH-PROMOTE-011` — confirm  (architecture)  ·  13 detailed design
- `ARCH-PROMOTE-TODO-001` — Promote a TODO item into a requirement draft  (architecture)  ·  14 detailed design
