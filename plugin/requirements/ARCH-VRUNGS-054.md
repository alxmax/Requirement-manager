---
id: ARCH-VRUNGS-054
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: could-have
depends_on: [ARCH-LEVEL-051, ARCH-VLEVEL-037, ARCH-CHECK-006]
satisfies: [SYS-VMODEL-107]
---

# Level-to-verification correspondence

## Description
> A level that no verification level answers to is a label; pairing them is what makes the V a V rather than two lists.

Every bullet below is binding.
- As someone who has declared both a requirement's specification level and the level its tests run at, I want the gate to tell me when the two do not correspond, so that a system requirement answered only by unit tests stops looking verified.

## Cases
CASE-1 — a level answered by the wrong depth of test warns
  Given  a confirmed requirement carrying `level: system` whose only levelled `tested-by:`
         link is `@unit`
  When   the gate runs
  Then   it warns, naming the level the requirement has and the `@system` link it lacks

CASE-2 — the paired level is silent
  Given  a confirmed requirement carrying `level: architecture` with an `@integration`
         `tested-by:` link — the pairing is `system` to `@system`, `architecture` to
         `@integration`, `code` to `@unit`
  When   the gate runs
  Then   it says nothing about that requirement, and the exit code is unchanged

CASE-3 — an unlevelled or undeclared requirement is never judged
  Given  either a requirement with no levelled `tested-by:` link at all, or one with no
         `level:` declared in its frontmatter
  When   the gate runs
  Then   it never reports that requirement as answered at the wrong depth

