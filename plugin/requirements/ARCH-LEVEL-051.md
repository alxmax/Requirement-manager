---
id: ARCH-LEVEL-051
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-PARSE-001, ARCH-CHECK-006]
satisfies: [SYS-VMODEL-107]
superseded_by:
---

# Specification level

## Description
> `layer:` says where a requirement sits in the dependency graph — a `bus` is defined by
> high fan-in, a `need` is covered by an edge instead of a code tag. It says nothing about
> how abstract the requirement is. This adds that second axis, so a corpus can record
> whether a requirement describes a whole system, one architectural piece, or one unit of
> code. Without it the two questions are answered by one field that can only answer the
> first.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a level        how abstract a requirement is: `system`, `architecture` or `code`.
     a layer        the existing graph-position field: `bus`, `feature`, `need`,
                    `aggregate`.
     the gate       the pre-commit check that reports errors and warnings. -->

**What the field holds**
- A requirement may carry a `level:` value of `system`, `architecture` or `code`.
- The `level:` field is optional. A requirement without one is read exactly as before.
- The `level:` axis is independent of `layer:`, and neither value constrains the other.

**Why the two axes stay separate**
- An `architecture` requirement owns code, so the gate keeps requiring an `implements:` member for it.
- The `aggregate` layer stays exempt from that rule, because it owns no code of its own.
- No `level:` value is added to the implementation-exemption set.

**When the gate objects**
- The gate reports an error for a `level:` value outside the three named ones.
- The gate says nothing about a requirement that carries no `level:` at all.

## Verify intent (open questions for the human)
- None — authored from stated intent, not reconstructed from code.

## Cases (= tests)
CASE-1
  Given  a requirement carrying `level: architecture`
  When   the gate runs
  Then   it reports no error about the level
CASE-2
  Given  a requirement carrying `level: detailed`
  When   the gate runs
  Then   it reports one error naming the invalid level, and the exit code is 1
CASE-3
  Given  a corpus in which no requirement carries a `level:` field
  When   the gate runs
  Then   its output is unchanged from a run before the field existed
CASE-4
  Given  a confirmed requirement carrying `level: architecture` and no `implements:` member
  When   the gate runs
  Then   it still reports the missing-member error, because the level grants no exemption

## Context (non-binding)
**Notes**
- The three values are the V-model's left arm, collapsed for a software-only tool: what
  ISO/IEC/IEEE and ASPICE separate into system requirements, system architecture, software
  requirements, software architecture and detailed design becomes three when there is no
  hardware to allocate.
- `level:` is deliberately NOT a rename of `layer:`. The two encode different facts, and
  aliasing them would be a silent behaviour change: `IMPL_EXEMPT_LAYERS` keys on `layer`,
  so making `architecture` a synonym of `aggregate` would remove every architecture
  requirement from the confirmed-code-must-exist check.
- The field is inert until a corpus adopts it. Nothing in the gate, the map or the viewer
  changes for a repo that never writes one.

**Example**
- Ana marks `NEED-AUTH-001` as `level: system`, the five capabilities that satisfy it as
  `level: architecture`, and the unit-sized requirements beneath them as `level: code`.
  Her `layer:` values do not move: `CORE-TOKEN-002` is still `layer: bus` because eleven
  requirements depend on it, and it is `level: code` because it describes one unit.

**Current implementation**
- `VALID_LEVEL` in `reqmap.py` and the validation branch in `cmd_check`, which reports an
  error for an unrecognised value and stays silent when the field is absent.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-LEVEL-436
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# A requirement may carry a level: value of

> A requirement may carry a `level:` value of `system`, `architecture` or `code`.

Scenario: the gate accepts each of the three level values
  Given  three requirements carrying `level: system`, `level: architecture` and `level: code` respectively
  When   `gate` runs
  Then   it reports no level-related error for any of the three

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-437
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# The level: field is optional. A requirement without

> The `level:` field is optional. A requirement without one is read exactly as before.

Scenario: a requirement without level: reads exactly as before
  Given  a corpus of requirements written before `level:` existed, none carrying the field
  When   `gate` runs
  Then   its output matches a run from before the field was introduced

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-438
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# The level: axis is independent of layer:, and

> The `level:` axis is independent of `layer:`, and neither value constrains the other.

Scenario: level and layer combine freely without cross-validation
  Given  a requirement carrying `level: system` and `layer: bus` together
  When   `gate` runs
  Then   it reports no error tying the two fields to each other

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-439
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# An architecture requirement owns code, so the gate

> An `architecture` requirement owns code, so the gate keeps requiring an `implements:`
> member for it.

Scenario: an architecture-level requirement still needs an implements member
  Given  a confirmed requirement carrying `level: architecture` and no `implements:` member
  When   `gate` runs
  Then   it reports the missing-member error

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-440
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# The aggregate layer stays exempt from that rule

> The `aggregate` layer stays exempt from that rule, because it owns no code of its own.

Scenario: an aggregate-layer requirement stays exempt regardless of level
  Given  a confirmed `layer: aggregate` requirement carrying `level: architecture` and no `implements:` member
  When   `gate` runs
  Then   it reports no missing-member error

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-441
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# No level: value is added to the implementation-exemption

> No `level:` value is added to the implementation-exemption set.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-442
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# The gate reports an error for a level

> The gate reports an error for a `level:` value outside the three named ones.

Scenario: an invalid level value is a gate error
  Given  a requirement carrying `level: detailed`
  When   `gate` runs
  Then   it reports one error naming the invalid value and exits 1

## Members in code (auto)




--------------------


---
id: REQ-LEVEL-443
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
superseded_by:
---

# The gate says nothing about a requirement that

> The gate says nothing about a requirement that carries no `level:` at all.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
