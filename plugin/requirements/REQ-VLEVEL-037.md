---
id: REQ-VLEVEL-037
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [CORE-SCAN-002, REQ-CHECK-006]
superseded_by:
---

# Verification levels

> A `tested-by:` link says a test exists, not how close that test sits to the code — a
> whole-system run and a single-function check look identical to the tool. This lets a tag
> name its level, and lets a stakeholder need point at the evidence it was met. Without it
> the engine models only the left side of the V: you can ask what a requirement depends on,
> but not "has anyone ever shown this need was actually satisfied?".

## WHAT — Contract (normative)
Every line in this section is binding.
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
- `show` prints the verification level beside a member whose `tested-by:` tag carries one.
- `show` prints a member whose tag carries no level with no level marker.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The level suffix is invisible to the ordinary tag parser, so an older vendored engine reads a levelled tag, resolves the id, and ignores the level — the annotation is backwards compatible.
- The level is author-declared, not measured: nothing checks that a test tagged `@unit` really isolates one unit. Same lexical-trust limitation as `tested-by` itself (REQ-TESTLINK-018).
- `validated-against:` had sat unused in the role list since the beginning; this requirement is the first consumer of it.

## HOW — Acceptance (= tests)
AC-1
  Given  tags declaring two levels for one id, a two-id list at `@integration`, one tag
         with no level and one carrying `@wrong`
  When   the level scan runs
  Then   the first id reports both levels with their `file:line`, both listed ids report
         `integration`, and the unlevelled and unrecognised ones are absent
AC-2
  Given  a `tested-by:` tag carrying a level suffix
  When   the ordinary tag scan reads it
  Then   it resolves to the same member as an unlevelled tag, so an engine that predates
         levels reads the id and ignores the suffix
AC-3
  Given  levelled tags that are not real claims — one inside backticks, one in a Python
         docstring, one in a string literal — alongside one real tag in a comment
  When   the level scan runs
  Then   only the real tag produces a level entry
AC-4
  Given  two confirmed needs, one carrying a `validated-against:` tag and one carrying none
  When   the gate runs
  Then   it warns about the unvalidated need only
AC-5
  Given  a confirmed need in a repo with no `validated-against:` tag anywhere
  When   the gate runs
  Then   it says nothing about validation
AC-6
  Given  a confirmed `bus` requirement whose only levelled link is `@system`
  When   the gate runs
  Then   it warns; adding a `@unit` link, dropping to an unlevelled link, or moving to the
         `feature` layer each silences it
AC-7
  Given  a member whose `tested-by:` tag carries `@integration`
  When   `show` runs
  Then   `@integration` appears beside that member; with no level data the output is unchanged

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tags her parser's unit test `# tested-by: CORE-PARSE-001 @unit` and her end-to-end
  suite `# tested-by: CORE-PARSE-001 @system`. Later someone deletes the unit test; the gate
  now warns "bus capability verified only at @system level". She also tags an acceptance test
  `# validated-against: NEED-SSOT-001`, and from then on any confirmed need with no such tag
  is named by the gate — so a need nobody ever checked stops looking finished.

## WHERE — Current implementation
- `TEST_LEVELS`, `TEST_LEVEL_RE` and `scan_test_levels` in `reqmap.py` collect `{cap: {level: [(file, line)]}}`, masking Python strings and backticked spans first. `cmd_check` computes `any_validation` from the member roles and `level_cover` from the scan, then appends the two warn-only findings. `cmd_show` takes the level map as an optional fourth argument and annotates each member line.

## Links
- Used by: (auto)
## Members in code (auto)
