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

## Description
> A level is only useful if it groups. One requirement holding fifty children is a bucket
> wearing a level's name; one holding two is a level that saves nobody any reading. This
> reports a parent whose child count leaves the useful band, so a hierarchy that has
> quietly flattened out gets looked at again.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a child        a requirement that names this one in its `satisfies:` list.
     a parent       a requirement that has at least one child.
     the ceiling    the largest child count a parent may carry before the check reports.
                    The ceiling depends on the parent's `level:` — see the contract below. -->

**What is counted**
- The `fan-out` check counts, per requirement, how many requirements declare `satisfies:` it.
- The count reads the `satisfies:` graph only, never `depends_on`.
- A requirement with no children is skipped, because it is not a parent.

**When it reports**
- The `fan-out` check warns when a parent carries more children than its ceiling.
- A `system` parent's ceiling is ten; an `architecture` parent's is thirty.
- A parent declaring no `level:` keeps the older uniform band, five to twenty, so a
  repo that never adopts the level axis sees what it saw before.
- The check reports no floor at either declared level.
- The `fan-out` check is warn-only and never changes the gate's exit code.
- `lint_exempt: [fan-out]` silences the check for one requirement.

## Verify intent (open questions for the human)
- None — authored from stated intent, not reconstructed from code.

## Cases (= tests)
CASE-1
  Given  an `architecture` requirement satisfied by three others
  When   `lint` runs
  Then   no `fan-out` finding is reported for it, because that level carries no floor
CASE-2
  Given  a requirement satisfied by eight others
  When   `lint` runs
  Then   no `fan-out` finding is reported for it
CASE-3
  Given  an `architecture` requirement satisfied by thirty-two others
  When   `lint` runs
  Then   one `fan-out` finding names it as over its ceiling, and the exit code is unchanged
CASE-4
  Given  a requirement that nothing satisfies
  When   `lint` runs
  Then   no `fan-out` finding is reported for it
CASE-5
  Given  a corpus whose requirements all depend on one another but declare no `satisfies:`
  When   `lint` runs
  Then   no `fan-out` finding is reported at all
CASE-6
  Given  a `system` requirement satisfied by twelve others
  When   `lint` runs
  Then   one `fan-out` finding names it as over its ceiling, which is lower than an
         architecture requirement's

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
- `LINT_FANOUT_BANDS` (per-level ceilings), `LINT_FANOUT_MIN`/`LINT_FANOUT_MAX` (the
  fallback band for a parent with no `level:`) and the `fan-out` block in
  `lint_requirement`, fed by
  the `kids` count `cmd_lint` builds from every requirement's `satisfies:` list.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-FANOUT-388
status: baseline
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

Scenario: the finding names the exact child count
  Given  three requirements each declaring `satisfies: [REQ-P-001]`
  When   `lint_requirement` runs with `children=3`
  Then   the `fan-out` finding's detail reads "3 requirement(s) satisfy this one"

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-389
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The count reads the satisfies: graph only, never

> The count reads the `satisfies:` graph only, never `depends_on`.

Scenario: depends_on edges never feed the fan-out count
  Given  a corpus where every requirement declares `depends_on` on one hub but no `satisfies:`
  When   `lint` runs
  Then   the hub gets no `fan-out` finding, because `depends_on` out-degree is never counted

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-390
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# A requirement with no children is skipped, because

> A requirement with no children is skipped, because it is not a parent.

Scenario: a leaf with zero children is never a fan-out finding
  Given  a requirement that nothing declares `satisfies:` on (`children=0`)
  When   `lint_requirement` runs
  Then   no `fan-out` finding appears for it

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-391
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The fan-out check warns when a parent exceeds its ceiling

> The `fan-out` check warns when a parent carries more children than its ceiling.

Scenario: crossing the ceiling flips the finding on
  Given  one `architecture` parent with 30 children (at its ceiling) and another with 31
  When   `lint` runs on each
  Then   the 30-child parent gets no `fan-out` finding and the 31-child parent gets one,
         with the gate's exit code unchanged either way

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-392
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The check reports no floor at either declared level

> The check reports no floor at either declared level.

Scenario: a thin parent at a declared level is not reported
  Given  one `architecture` parent with 3 children and one `system` parent with 2
  When   `lint` runs on each
  Then   neither gets a `fan-out` finding, because neither declared level carries a floor

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-393
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# The fan-out check is warn-only

> The `fan-out` check is warn-only and never changes the gate's exit code.

Scenario: a fan-out finding does not fail the run
  Given  an `architecture` parent with 32 children, over its ceiling
  When   `lint` runs without `--strict`
  Then   one `fan-out` finding is printed and the exit code is zero

## Members in code (auto)




--------------------


---
id: REQ-FANOUT-394
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FANOUT-052]
superseded_by:
---

# Lint_exempt: fan-out silences the check for one requirement

> `lint_exempt: [fan-out]` silences the check for one requirement.

Scenario: lint_exempt: [fan-out] suppresses the finding
  Given  a parent with 3 children and `lint_exempt: [fan-out]` in its frontmatter
  When   `lint_requirement` runs
  Then   no `fan-out` finding is reported for that requirement

## Members in code (auto)
