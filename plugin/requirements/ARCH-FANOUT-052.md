---
id: ARCH-FANOUT-052
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: could-have
depends_on: [ARCH-PARSE-001, ARCH-LINT-014, ARCH-LEVEL-051]
satisfies: [SYS-VMODEL-107]
superseded_by:
---

# Hierarchy breadth

> A level is only useful if it groups. One requirement holding fifty children is a bucket
> wearing a level's name; one holding two is a level that saves nobody any reading. This
> reports a parent whose child count leaves the useful band, so a hierarchy that has
> quietly flattened out gets looked at again.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a child        a requirement that names this one in its `satisfies:` list.
     a parent       a requirement that has at least one child.
     the band       `LINT_FANOUT_MIN` to `LINT_FANOUT_MAX`, default 5 to 20. -->

**What is counted**
- The `fan-out` check counts, per requirement, how many requirements declare `satisfies:` it.
- The count reads the `satisfies:` graph only, never `depends_on`.
- A requirement with no children is skipped, because it is not a parent.

**When it reports**
- The `fan-out` check warns when a parent's child count falls outside the band.
- The finding says whether the count is below the band or above it.
- The `fan-out` check is warn-only and never changes the gate's exit code.
- `lint_exempt: [fan-out]` silences the check for one requirement.

## WHAT — Verify intent (open questions for the human)
- None — authored from stated intent, not reconstructed from code.

## HOW — Acceptance (= tests)
AC-1
  Given  a requirement satisfied by three others
  When   `lint` runs
  Then   one `fan-out` finding names it as below the band, and the exit code is unchanged
AC-2
  Given  a requirement satisfied by eight others
  When   `lint` runs
  Then   no `fan-out` finding is reported for it
AC-3
  Given  a requirement satisfied by twenty-five others
  When   `lint` runs
  Then   one `fan-out` finding names it as above the band
AC-4
  Given  a requirement that nothing satisfies
  When   `lint` runs
  Then   no `fan-out` finding is reported for it
AC-5
  Given  a corpus whose requirements all depend on one another but declare no `satisfies:`
  When   `lint` runs
  Then   no `fan-out` finding is reported at all

## Context (non-binding)
**Notes**
- The band is read against the `satisfies:` graph on purpose. Measured on this corpus, the
  `depends_on` out-degree runs 0 to 3, so a 5-to-20 band read against that axis would flag
  every requirement — a check that fires on correct work gets ignored (ADR-0002).
- 5 and 20 are an engineering heuristic, not a figure from any standard. No requirements
  standard specifies decomposition breadth.
- The leaf exemption is what keeps the check silent on a corpus that has not adopted
  `satisfies:` at all: with no edges, nothing is a parent and nothing is reported.
- The check measures breadth, never correctness of the grouping. A parent with twelve
  children that belong together and one with twelve that do not are indistinguishable to it.

**Example**
- Ana's `NEED-REPORTING-003` starts with six children and stays quiet. Two releases later
  it has twenty-four, and `lint` warns. She reads them, finds that eight are really about
  export rather than reporting, and lifts those under a new sibling need.

**Current implementation**
- `LINT_FANOUT_MIN`/`LINT_FANOUT_MAX` and the `fan-out` block in `lint_requirement`, fed by
  the `kids` count `cmd_lint` builds from every requirement's `satisfies:` list.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-FANOUT-388
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The fan-out check counts, per requirement, how many

> The `fan-out` check counts, per requirement, how many requirements declare `satisfies:`
> it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-389
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The count reads the satisfies: graph only, never

> The count reads the `satisfies:` graph only, never `depends_on`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-390
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# A requirement with no children is skipped, because

> A requirement with no children is skipped, because it is not a parent.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-391
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The fan-out check warns when a parent's child

> The `fan-out` check warns when a parent's child count falls outside the band.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-392
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The finding says whether the count is below

> The finding says whether the count is below the band or above it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-393
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The fan-out check is warn-only and never changes

> The `fan-out` check is warn-only and never changes the gate's exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-394
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# Lint_exempt: fan-out silences the check for one requirement

> `lint_exempt: [fan-out]` silences the check for one requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
