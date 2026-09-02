---
id: ARCH-VRUNGS-054
status: confirmed
form: atomic
level: architecture
layer: feature
owner: Alex
priority: could-have
verification: automated test
rationale: A level that no verification level answers to is a label; pairing them is what makes the V a V rather than two lists.
depends_on: [ARCH-LEVEL-051, ARCH-VLEVEL-037, ARCH-CHECK-006]
satisfies: [SYS-VMODEL-107]
superseded_by:
---

# Level-to-verification correspondence

> As someone who has declared both a requirement's specification level and the level its
> tests run at, I want the gate to tell me when the two do not correspond, so that a system
> requirement answered only by unit tests stops looking verified.

Scenario: a declared level verified only at the wrong level
  Given  a confirmed requirement carrying `level: system` whose only levelled `tested-by:`
         link is `@unit`, and a second carrying `level: architecture` with an
         `@integration` link
  When   the gate runs
  Then   it warns about the first, naming the level it has and the `@system` link it lacks,
         says nothing about the second, and its exit code is unchanged

## Members in code (auto)
