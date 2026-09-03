---
id: ARCH-VLEVEL-037
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-SCAN-002, ARCH-CHECK-006]
satisfies: [SYS-VMODEL-107]
superseded_by:
---

# Verification levels

## Description
> A `tested-by:` link says a test exists, not how close that test sits to the code — a
> whole-system run and a single-function check look identical to the tool. This lets a tag
> name its level, and lets a stakeholder need point at the evidence it was met. Without it
> the engine models only the left side of the V: you can ask what a requirement depends on,
> but not "has anyone ever shown this need was actually satisfied?".
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a verification level  how close a test sits to the code: `@unit`, `@integration`
                           or `@system`.
     validation            evidence that the right thing was built, as opposed to
                           evidence that it was built correctly.
     a need                a `layer: need` requirement: a stakeholder need other
                           requirements fulfil, rather than code.
     the gate              the pre-commit check that reports errors and warnings. -->

**How a level is written**
- A `tested-by:` tag may end with a verification level: `@unit`, `@integration` or `@system`.
- A level written on a tag applies to every id in that tag's comma-separated list.
- A `tested-by:` tag carrying no level, or an unrecognised one, stays an ordinary member link.

**What the engine collects**
- The engine reports, per requirement, each level it is verified at with the `file:line`
  locations that declare it.
- The level scan stays separate from the member scan, so the member shape every consumer
  reads is unchanged.
- The engine skips a levelled tag written inside backticks, so a documented example never
  counts as real coverage.
- In a Python file the engine also skips a levelled tag inside a string literal or a
  docstring. Prose about how to tag is not a claim of coverage.

**When the gate warns**
- The gate warns when a confirmed `need` carries no `validated-against:` member.
- The gate holds that need warning back until the repo carries at least one
  `validated-against:` tag, so adopting the role is opt-in.
- The gate warns when a confirmed `bus` requirement's levelled `tested-by:` links are all
  `@system`.
- The gate judges no requirement that has no levelled link, because an unlevelled link is
  evidence of neither level.
- The gate applies the level-fit rule to the `bus` layer only. A feature may legitimately be
  covered end to end.
- Both rules are warn-only. Neither changes the gate's exit code.

**What `show` prints**
- How `show` renders a levelled member is [[ARCH-SHOW-015]]'s contract, not restated here.
- `show` prints a member whose tag carries no level with no level marker.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The level suffix is invisible to the ordinary tag parser, so an older vendored engine reads a levelled tag, resolves the id, and ignores the level — the annotation is backwards compatible.
- The level is author-declared, not measured: nothing checks that a test tagged `@unit` really isolates one unit. Same lexical-trust limitation as `tested-by` itself (ARCH-TESTLINK-018).
- `validated-against:` had sat unused in the role list since the beginning; this requirement is the first consumer of it.

## Cases (= tests)
CASE-1
  Given  tags declaring two levels for one id, a two-id list at `@integration`, one tag
         with no level and one carrying `@wrong`
  When   the level scan runs
  Then   the first id reports both levels with their `file:line`, both listed ids report
         `integration`, and the unlevelled and unrecognised ones are absent
CASE-2
  Given  a `tested-by:` tag carrying a level suffix
  When   the ordinary tag scan reads it
  Then   it resolves to the same member as an unlevelled tag, so an engine that predates
         levels reads the id and ignores the suffix
CASE-3
  Given  levelled tags that are not real claims — one inside backticks, one in a Python
         docstring, one in a string literal — alongside one real tag in a comment
  When   the level scan runs
  Then   only the real tag produces a level entry
CASE-4
  Given  two confirmed needs, one carrying a `validated-against:` tag and one carrying none
  When   the gate runs
  Then   it warns about the unvalidated need only
CASE-5
  Given  a confirmed need in a repo with no `validated-against:` tag anywhere
  When   the gate runs
  Then   it says nothing about validation
CASE-6
  Given  a confirmed `bus` requirement whose only levelled link is `@system`
  When   the gate runs
  Then   it warns; adding a `@unit` link, dropping to an unlevelled link, or moving to the
         `feature` layer each silences it
CASE-7
  Given  a member whose `tested-by:` tag carries `@integration`
  When   `show` runs
  Then   `@integration` appears beside that member; with no level data the output is unchanged

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tags her parser's unit test `# tested-by: ARCH-PARSE-001 @unit` and her end-to-end
  suite `# tested-by: ARCH-PARSE-001 @system`. Later someone deletes the unit test; the gate
  now warns "bus capability verified only at @system level". She also tags an acceptance test
  `# validated-against: SYS-SSOT-001`, and from then on any confirmed need with no such tag
  is named by the gate — so a need nobody ever checked stops looking finished.

## WHERE — Current implementation
- `TEST_LEVELS`, `TEST_LEVEL_RE` and `scan_test_levels` in `reqmap.py` collect `{cap: {level: [(file, line)]}}`, masking Python strings and backticked spans first. `cmd_check` computes `any_validation` from the member roles and `level_cover` from the scan, then appends the two warn-only findings. `cmd_show` takes the level map as an optional fourth argument and annotates each member line.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-806
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# A tested-by: tag may end with a verification

> A `tested-by:` tag may end with a verification level: `@unit`, `@integration` or
> `@system`.

Scenario: scan_test_levels recognizes all three level suffixes
  Given  `# tested-by: REQ-A-001 @unit`, `# tested-by: REQ-A-001 @system`, and
         `# tested-by: REQ-B-002 @integration` in one file
  When   `scan_test_levels` runs
  Then   `REQ-A-001` reports levels `{"unit", "system"}` and `REQ-B-002` reports
         `{"integration"}`

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-807
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# A level written on a tag applies to

> A level written on a tag applies to every id in that tag's comma-separated list.

Scenario: one level suffix applies to every id in the list
  Given  `# tested-by: REQ-A-001, REQ-B-002 @integration`
  When   `scan_test_levels` runs
  Then   both `REQ-A-001` and `REQ-B-002` report level `integration`

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-808
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# A tested-by: tag carrying no level, or an

> A `tested-by:` tag carrying no level, or an unrecognised one, stays an ordinary member
> link.

Scenario: a tag with no level, or an unrecognised one, still resolves as a plain member
  Given  `# tested-by: REQ-D-004 @wrong` (an unknown level suffix)
  When   `_findall_tags` parses the line
  Then   it returns `[("tested-by", "REQ-D-004")]`, same as an unlevelled tag — and
         `scan_test_levels` collects no level for `REQ-D-004`

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-809
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The engine reports, per requirement, each level it

> The engine reports, per requirement, each level it is verified at with the `file:line`
> locations that declare it.

Scenario: scan_test_levels records the file:line that declares each level
  Given  `# tested-by: REQ-B-002 @integration` as line 3 of `t_one.py`
  When   `scan_test_levels` runs
  Then   `got["REQ-B-002"]["integration"]` equals `[("t_one.py", 3)]`

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-810
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The level scan stays separate from the member

> The level scan stays separate from the member scan, so the member shape every consumer
> reads is unchanged.

Scenario: a level suffix does not change the ordinary member tuple shape
  Given  `# tested-by: REQ-A-001 @unit`
  When   `_findall_tags` (the member scan) parses it
  Then   it returns the plain `[("tested-by", "REQ-A-001")]` two-tuple, with no level
         field grafted on

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-811
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The engine skips a levelled tag written inside

> The engine skips a levelled tag written inside backticks, so a documented example never
> counts as real coverage.

Scenario: a backticked levelled-tag example does not count as coverage
  Given  a line "write it as `# tested-by: REQ-A-001 @unit` in your test" plus a real
         `# tested-by: REQ-B-002 @unit` tag
  When   `scan_test_levels` runs
  Then   `REQ-A-001` is absent from the result and `REQ-B-002` reports `{"unit"}`

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-812
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# In a Python file the engine also skips

> In a Python file the engine also skips a levelled tag inside a string literal or a
> docstring. Prose about how to tag is not a claim of coverage.

Scenario: a levelled tag inside a docstring or string literal is not coverage
  Given  a `.py` file with `REQ-DOC-001 @unit` inside a docstring, `REQ-STR-001 @unit`
         inside a string literal, and a real `# tested-by: REQ-REAL-001 @unit` comment
  When   `scan_test_levels` runs
  Then   `REQ-DOC-001` and `REQ-STR-001` are absent; `REQ-REAL-001` reports `{"unit"}`

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-813
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The gate warns when a confirmed need carries

> The gate warns when a confirmed `need` carries no `validated-against:` member.

Scenario: an unvalidated confirmed need is named once the repo has opted in
  Given  `NEED-A-001` carrying a `validated-against:` tag and `NEED-B-002` carrying none,
         both confirmed needs
  When   `gate` runs
  Then   its output names `NEED-B-002` alongside "validated-against"

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-814
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The gate holds that need warning back until

> The gate holds that need warning back until the repo carries at least one
> `validated-against:` tag, so adopting the role is opt-in.

Scenario: no validated-against tag anywhere keeps the rule silent
  Given  a confirmed need and no `validated-against:` tag anywhere in the tree
  When   `gate` runs
  Then   its output contains no mention of "validated-against"

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-815
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The gate warns when a confirmed bus requirement's

> The gate warns when a confirmed `bus` requirement's levelled `tested-by:` links are all
> `@system`.

Scenario: a bus requirement verified only at @system level warns
  Given  a confirmed `layer: bus` requirement whose only levelled `tested-by:` link is
         `@system`
  When   `gate` runs
  Then   its output contains "@system"

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-816
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The gate judges no requirement that has no

> The gate judges no requirement that has no levelled link, because an unlevelled link is
> evidence of neither level.

Scenario: a bus requirement with only an unlevelled tested-by link is never judged
  Given  a confirmed `layer: bus` requirement whose only `tested-by:` link carries no
         level suffix
  When   `gate` runs
  Then   its output contains no "verified only at @system" finding

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-817
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# The gate applies the level-fit rule to the

> The gate applies the level-fit rule to the `bus` layer only. A feature may legitimately
> be covered end to end.

Scenario: a feature requirement verified only at @system stays silent
  Given  a confirmed `layer: feature` requirement whose only levelled `tested-by:` link is
         `@system`
  When   `gate` runs
  Then   its output contains no "verified only at @system" finding

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-818
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# Both rules are warn-only. Neither changes the gate's

> Both rules are warn-only. Neither changes the gate's exit code.

Scenario: the unvalidated-need and system-only-bus findings never bump the exit code
  Given  a confirmed need with no `validated-against:` tag, and separately a confirmed
         `bus` requirement verified only at `@system`, each in an opted-in repo
  When   `gate` runs on each
  Then   both runs warn and both return exit code 0

## Members in code (auto)




--------------------




--------------------


---
id: REQ-VLEVEL-820
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VLEVEL-037]
superseded_by:
---

# Show prints a member whose tag carries no

> `show` prints a member whose tag carries no level with no level marker.

Scenario: show prints an unlevelled member with no level marker
  Given  a `tested-by` member at `t.py:2` and no `levels` argument passed to `cmd_show`
  When   `show REQ-X-001` runs with the old 3-argument call
  Then   its output contains "t.py:2" and no "@" marker after the members section

## Members in code (auto)
