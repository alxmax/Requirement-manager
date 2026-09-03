---
id: ARCH-ACVERIFY-019
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-CHECK-006, ARCH-SCAN-002]
satisfies: [SYS-GATE-102]
superseded_by:
milestone: v1.16
---

# Per-criterion test coverage

## Description
> Today the gate can tell you a requirement has *some* test, but not that *each* of
> its acceptance criteria is actually checked — so a requirement with five criteria
> and one test looks just as "covered" as one with five tests. This links each labelled
> criterion to the test that verifies it, so the gate can name the exact criterion that
> nobody tests. Without it, "Verifiable" is only true at the whole-requirement level and
> a half-tested requirement passes silently.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a labelled criterion  an acceptance criterion written as `CASE-1`, `CASE-2`, and so on,
                           so a test can name the exact one it covers.
     the gate              the pre-commit check that reports errors and warnings. -->

**What it reads**
- The gate scans code for `# verifies: <id>#AC-N` tags and maps each tag to the labelled
  criterion it covers. This is the per-criterion half of behaviour-sync.
- The gate recognises a `verifies` tag only with an `#AC-N` suffix, so a plain requirement
  reference is never mistaken for a per-criterion one.

**When it warns**
- For a confirmed requirement that labels its criteria and carries at least one `verifies`
  tag, the gate warns once, naming every labelled criterion that has no tag.
- That single warning also states how many labelled criteria are tagged, so partial adoption
  reads as progress rather than as a growing pile of warnings.

**When it stays silent**
- A confirmed requirement with no `verifies` tag is exempt. Per-criterion tagging is opt-in,
  and the coarser `tested-by` check still applies to it.
- A requirement whose criteria are unlabelled bullets is exempt, because there is no criterion
  label for a tag to address.
- A criterion marked `<!-- verifiable by: inspection -->` or `manual` is excluded from the
  warning and from the counts. No tag can ever cover it.

**What it emits**
- The map emits `clauses` and `covered` on a requirement that has adopted per-criterion
  tagging, and omits both fields otherwise.
- The map emits a `gap` naming the untagged criteria when coverage is partial.
- An absent `clauses` means "not measured". No reader may substitute a number of its own.

**Severity**
- The check is warn-only. It never changes the gate's exit code.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The link asserts a test *exists* for a criterion, not that the test's assertions actually exercise it — same lexical-trust limitation as `tested-by` (ARCH-TESTLINK-018).
- A criterion can carry more than one `verifies` tag (several tests for one criterion); the check only asks for at least one.

## Cases (= tests)
CASE-1
  Given  a requirement with labelled CASE-1 and CASE-2 and a test tagging `# verifies: REQ-X#CASE-1`
  When   the gate runs
  Then   it warns that CASE-2 is unverified and says nothing about CASE-1
CASE-2
  Given  a requirement whose every labelled criterion has a matching `verifies` tag
  When   the gate runs
  Then   it adds no per-criterion warning
CASE-3
  Given  a confirmed requirement with labelled criteria but zero `verifies` tags
  When   the gate runs
  Then   it adds no per-criterion warning (per-criterion tagging is opt-in)
CASE-4
  Given  a confirmed requirement whose criteria are unlabelled bullets
  When   the gate runs
  Then   it adds no per-criterion warning
CASE-5
  Given  a confirmed requirement with a criterion marked `verifiable by: inspection`
  When   the gate runs
  Then   that criterion appears in no warning and in no emitted count
CASE-6
  Given  a requirement with two labelled criteria of which one carries a `verifies` tag
  When   the map is generated
  Then   its node carries `clauses: 2`, `covered: 1`, and a `gap` naming the untagged one

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana's login requirement lists CASE-1, CASE-2, CASE-3 but only CASE-1 has a test. She tags that
  test `# verifies: AUTH-LOGIN-001#CASE-1` and runs `reqmap.py gate`. The gate warns
  "CASE-2 has no `# verifies` tag — criterion unverified" and the same for CASE-3, so she sees
  exactly which two criteria still need a test instead of a vague "needs tests".

## WHERE — Current implementation
- `scan_ac_verifies`, `_acc_blocks`, `_labeled_acs`, `_automatable_acs`, `AC_VERIFY_RE` in `reqmap.py`, consumed by `cmd_check` and by `_attach_ac_coverage` — `scan_ac_verifies` collects `# verifies: <id>#AC-N` tags into `{cap: {AC-N: locations}}`, `_acc_blocks` is the single parser of the Acceptance section (labels, folded prose, and the `verifiable by:` marker), `_automatable_acs` drops the criteria a machine can never verify, `cmd_check` emits one aggregated warning naming the untagged ones, and `_attach_ac_coverage` puts `clauses`/`covered`/`gap` on the map node only when the requirement has adopted tagging.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-233
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# The gate scans code for # verifies: <id>#AC-N

> The gate scans code for `# verifies: <id>#AC-N` tags and maps each tag to the labelled
> criterion it covers. This is the per-criterion half of behaviour-sync.

Scenario: a verifies tag is mapped to its labelled criterion
  Given  a test file carrying `# verifies: AREA-A-001#CASE-1` and a requirement labelling CASE-1 and CASE-2
  When   `gate` runs
  Then   it reports that 1 of the 2 automatable criteria carries a `verifies:` tag, naming CASE-2 as missing

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-234
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# The gate recognises a verifies tag only with

> The gate recognises a `verifies` tag only with an `#AC-N` suffix, so a plain requirement
> reference is never mistaken for a per-criterion one.

Scenario: a verifies tag with no #AC-N suffix is not per-criterion coverage
  Given  a file carrying `# verifies: REQ-X-001` with no trailing `#AC-N`
  When   `scan_ac_verifies` scans it
  Then   it returns an empty mapping for `REQ-X-001`

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-235
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# For a confirmed requirement that labels its criteria

> For a confirmed requirement that labels its criteria and carries at least one `verifies`
> tag, the gate warns once, naming every labelled criterion that has no tag.

Scenario: partial verifies coverage produces one warning naming every gap
  Given  a confirmed requirement with five labelled criteria, `AC-1` tagged and AC-2..AC-5
         untagged
  When   `gate` runs
  Then   it prints exactly one "automatable criteria" line naming "missing AC-2, AC-3,
         AC-4, AC-5"

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-236
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# That single warning also states how many labelled

> That single warning also states how many labelled criteria are tagged, so partial
> adoption reads as progress rather than as a growing pile of warnings.

Scenario: the warning states the tagged-of-total count
  Given  a confirmed requirement with AC-1 and AC-2 labelled, only AC-1 tagged
  When   `gate` runs
  Then   its output contains "1/2 automatable criteria"

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-237
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# A confirmed requirement with no verifies tag is

> A confirmed requirement with no `verifies` tag is exempt. Per-criterion tagging is
> opt-in, and the coarser `tested-by` check still applies to it.

Scenario: zero verifies tags is silent, not a violation
  Given  a confirmed requirement with two labelled criteria and zero `# verifies:` tags
         anywhere in the tree
  When   `gate` runs
  Then   its output contains no "criterion unverified" finding

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-238
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# A requirement whose criteria are unlabelled bullets is

> A requirement whose criteria are unlabelled bullets is exempt, because there is no
> criterion label for a tag to address.

Scenario: unlabelled bullet criteria never trigger the per-criterion warning
  Given  a confirmed requirement whose Cases are plain bullets, no `AC-N`/`CASE-N` labels,
         and a `# verifies:` tag present in code
  When   `gate` runs
  Then   its output contains no "criterion unverified" finding

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-239
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# A criterion marked <!-- verifiable by: inspection -->

> A criterion marked `<!-- verifiable by: inspection -->` or `manual` is excluded from the
> warning and from the counts. No tag can ever cover it.

Scenario: an inspection-only criterion never triggers the automatable-criteria warning
  Given  a confirmed requirement with `AC-1` tagged and `AC-2` marked
         `<!-- verifiable by: inspection -->`
  When   `gate` runs
  Then   its output contains no "automatable criteria" line

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-240
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# The map emits clauses and covered on a

> The map emits `clauses` and `covered` on a requirement that has adopted per-criterion
> tagging, and omits both fields otherwise.

Scenario: clauses/covered appear only once tagging is adopted
  Given  a requirement with two labelled criteria and no `verifies` coverage passed to
         `_build_map_data`, and separately the same requirement with `AC-1` covered
  When   `_build_map_data` builds each node
  Then   the untagged node has no `clauses`/`covered` keys — absent means not measured,
         never a substituted zero — and the tagged node has `clauses: 2, covered: 1`

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-241
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# The map emits a gap naming the untagged

> The map emits a `gap` naming the untagged criteria when coverage is partial.

Scenario: gap names the untagged criteria only when coverage is partial
  Given  a two-criterion requirement with only `AC-1` covered, and separately one with
         both `AC-1` and its only criterion covered
  When   `_build_map_data` builds each node
  Then   the partial node's `gap` contains "AC-2" and the fully-covered node carries no
         `gap` key

## Members in code (auto)




--------------------


---
id: REQ-ACVERIFY-243
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
superseded_by:
---

# The check is warn-only. It never changes the

> The check is warn-only. It never changes the gate's exit code.

Scenario: an unverified criterion warns but the gate exits 0
  Given  a confirmed requirement with `AC-1` tagged and `AC-2` untagged, nothing else
         causing an error
  When   `gate` runs
  Then   the run warns about AC-2 and still exits 0

## Members in code (auto)
