---
id: SYS-VMODEL-107
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
milestone: v2.32
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Placing a requirement in the V

> As someone who wants to know whether a requirement is verified at the right depth, I 
> want each one to declare how abstract it is and which level of test discharges it, so 
> that a system-level promise answered only by a unit test stops looking covered.

Scenario: a level and its verification are compared
  Given  a confirmed requirement declaring its specification level and carrying levelled test links
  When   the gate runs
  Then   it reports a requirement whose tests sit at no level that discharges its own, and judges nothing when either declaration is absent

## Requirements in this system (auto)
- `ARCH-FANOUT-052` — Hierarchy breadth  (architecture)  ·  7 detailed design
- `ARCH-LEVEL-051` — Specification level  (architecture)  ·  8 detailed design
- `ARCH-TRACE-020` — Upstream traceability  (architecture)  ·  10 detailed design
- `ARCH-VLEVEL-037` — Verification levels  (architecture)  ·  15 detailed design
- `ARCH-VRUNGS-054` — Level-to-verification correspondence  (architecture)
