---
id: ARCH-LEVEL-051
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.32
priority: should-have
depends_on: [ARCH-PARSE-001, ARCH-CHECK-006]
satisfies: [SYS-VMODEL-107]
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
- A requirement may carry an optional `level:` of `system`, `architecture` or `code`, independent of `layer:`; the gate accepts the three values, ignores an absent field, and errors on anything else, granting no implements-tag exemption. [[REQ-LEVEL-862]] details the behaviour.

## Cases
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

## Context
**Terms**
- a level        how abstract a requirement is: `system`, `architecture` or `code`.
- a layer        the existing graph-position field: `bus`, `feature`, `need`,
- `aggregate`.
- the gate       the pre-commit check that reports errors and warnings.

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


--------------------


---
id: REQ-LEVEL-862
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LEVEL-051]
---

# The level field, validated independently of layer

## Description
> `level:` and `layer:` answer different questions — how abstract a requirement is,
> versus where it sits in the dependency graph — so the gate validates them separately
> and never lets one imply the other. An `architecture`-level requirement still owns
> code and still needs an `implements:` member; only `layer: aggregate` (owning no code
> of its own) is exempt from that, regardless of level.

Every bullet below is binding.
- A requirement may carry a `level:` value of `system`, `architecture` or `code`.
- The `level:` field is optional. A requirement without one is read exactly as before.
- The `level:` axis is independent of `layer:`, and neither value constrains the other.
- An `architecture` requirement owns code, so the gate keeps requiring an `implements:` member for it.
- The `aggregate` layer stays exempt from that rule, because it owns no code of its own.
- No `level:` value is added to the implementation-exemption set.
- The gate reports an error for a `level:` value outside the three named ones.
- The gate says nothing about a requirement that carries no `level:` at all.

## Cases
CASE-1 — the gate accepts each of the three level values
  Given  three requirements carrying `level: system`, `level: architecture` and `level: code` respectively
  When   `gate` runs
  Then   it reports no level-related error for any of the three

CASE-2 — a requirement without level: reads exactly as before
  Given  a corpus of requirements written before `level:` existed, none carrying the field
  When   `gate` runs
  Then   its output matches a run from before the field was introduced, with no
         level-related finding for any requirement

CASE-3 — level and layer combine freely without cross-validation
  Given  a requirement carrying `level: system` and `layer: bus` together
  When   `gate` runs
  Then   it reports no error tying the two fields to each other

CASE-4 — an architecture-level requirement still needs an implements member
  Given  a confirmed requirement carrying `level: architecture` and no `implements:` member
  When   `gate` runs
  Then   it reports the missing-member error, because no `level:` value is in the
         implementation-exemption set

CASE-5 — an aggregate-layer requirement stays exempt regardless of level
  Given  a confirmed `layer: aggregate` requirement carrying `level: architecture` and no `implements:` member
  When   `gate` runs
  Then   it reports no missing-member error

CASE-6 — an invalid level value is a gate error
  Given  a requirement carrying `level: detailed`
  When   `gate` runs
  Then   it reports one error naming the invalid value and exits 1

