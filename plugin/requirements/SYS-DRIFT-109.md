---
id: SYS-DRIFT-109
status: draft
form: atomic
level: system
layer: need
owner: Alex
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Noticing what moved without the specification

> As someone committing a change, I want the engine to tell me when the code, the
> requirements or the prose about them have moved apart — in either direction, and
> including code no requirement accounts for — so that a spec nobody honours stops
> passing for documentation.

Scenario: a confirmed contract changes without its code
  Given  a confirmed requirement whose contract text has been edited
  When   the gate runs
  Then   it reports the drift and names the members and dependents to re-check, without advancing the baseline itself

## Context
**Notes**
- Split from SYS-GATE-102 on 2026-09-23, when sixteen architecture requirements
  satisfied it against a ceiling of ten. SYS-GATE-102 keeps the verdict that every
  link resolves; this need holds the signals that something changed or sits outside
  the corpus: drift in both directions, its blast radius, re-measured prose claims,
  and code, documents or members no requirement accounts for.
