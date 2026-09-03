---
id: ARCH-ACVERIFY-019
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v1.16
depends_on: [ARCH-CHECK-006, ARCH-SCAN-002]
satisfies: [SYS-GATE-102]
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
- The gate scans code for `# verifies: <id>#AC-N` tags and maps each to the labelled criterion it covers — the per-criterion half of behaviour-sync. [[REQ-ACVERIFY-821]]
- A confirmed requirement with no `verifies` tag, with unlabelled criteria, or with an inspection-only criterion is exempt from the per-criterion warning; the coarser `tested-by` check still applies to it. [[REQ-ACVERIFY-822]]
- The map emits `clauses`/`covered`/`gap` only on a requirement that has adopted per-criterion tagging, and the check never changes the gate's exit code. [[REQ-ACVERIFY-823]]

## Cases
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

## Context
**Terms**
- a labelled criterion  an acceptance criterion written as `CASE-1`, `CASE-2`, and so on,
- so a test can name the exact one it covers.
- the gate              the pre-commit check that reports errors and warnings.

**Notes**
- The link asserts a test *exists* for a criterion, not that the test's assertions actually exercise it — same lexical-trust limitation as `tested-by` (ARCH-TESTLINK-018).
- A criterion can carry more than one `verifies` tag (several tests for one criterion); the check only asks for at least one.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana's login requirement lists CASE-1, CASE-2, CASE-3 but only CASE-1 has a test. She tags that
  test `# verifies: AUTH-LOGIN-001#CASE-1` and runs `reqmap.py gate`. The gate warns
  "CASE-2 has no `# verifies` tag — criterion unverified" and the same for CASE-3, so she sees
  exactly which two criteria still need a test instead of a vague "needs tests".

**Current implementation**
- `scan_ac_verifies`, `_acc_blocks`, `_labeled_acs`, `_automatable_acs`, `AC_VERIFY_RE` in `reqmap.py`, consumed by `cmd_check` and by `_attach_ac_coverage` — `scan_ac_verifies` collects `# verifies: <id>#AC-N` tags into `{cap: {AC-N: locations}}`, `_acc_blocks` is the single parser of the Acceptance section (labels, folded prose, and the `verifiable by:` marker), `_automatable_acs` drops the criteria a machine can never verify, `cmd_check` emits one aggregated warning naming the untagged ones, and `_attach_ac_coverage` puts `clauses`/`covered`/`gap` on the map node only when the requirement has adopted tagging.


--------------------


---
id: REQ-ACVERIFY-821
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
---

# Mapping verifies tags to labelled criteria

## Description
> The gate can prove a requirement has *a* test, but not that each of its criteria is tested
> individually. `scan_ac_verifies` reads `# verifies: <id>#AC-N` tags so the gate can name
> exactly which labelled criterion still has no test, instead of treating the whole
> requirement as pass-or-fail.

Every bullet below is binding.
- The gate scans code for `# verifies: <id>#AC-N` tags and maps each tag to the labelled
  criterion it covers. This is the per-criterion half of behaviour-sync.
- The gate recognises a `verifies` tag only with an `#AC-N` suffix, so a plain requirement
  reference is never mistaken for a per-criterion one.
- For a confirmed requirement that labels its criteria and carries at least one `verifies`
  tag, the gate warns once, naming every labelled criterion that has no tag.
- That single warning also states how many labelled criteria are tagged, so partial adoption
  reads as progress rather than as a growing pile of warnings.

## Cases
CASE-1 — a verifies tag is mapped to its labelled criterion
  Given  a test file carrying `# verifies: AREA-A-001#CASE-1` and a requirement labelling CASE-1 and CASE-2
  When   `gate` runs
  Then   it reports that 1 of the 2 automatable criteria carries a `verifies:` tag, naming CASE-2 as missing

CASE-2 — a verifies tag with no #AC-N suffix is not per-criterion coverage
  Given  a file carrying `# verifies: REQ-X-001` with no trailing `#AC-N`
  When   `scan_ac_verifies` scans it
  Then   it returns an empty mapping for `REQ-X-001`

CASE-3 — partial verifies coverage produces one warning naming every gap
  Given  a confirmed requirement with five labelled criteria, `AC-1` tagged and AC-2..AC-5
         untagged
  When   `gate` runs
  Then   it prints exactly one "automatable criteria" line naming "missing AC-2, AC-3, AC-4, AC-5"

CASE-4 — the warning states the tagged-of-total count
  Given  a confirmed requirement with AC-1 and AC-2 labelled, only AC-1 tagged
  When   `gate` runs
  Then   its output contains "1/2 automatable criteria"


--------------------


---
id: REQ-ACVERIFY-822
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
---

# When per-criterion coverage stays silent

## Description
> Per-criterion tagging is opt-in: a requirement that never adopted it, has no labelled
> criteria, or marks a criterion as manually-verifiable must not be penalized for a check it
> never signed up for. Without these exemptions every confirmed requirement lacking full
> `verifies` coverage would warn, drowning real gaps in noise nobody can act on.

Every bullet below is binding.
- A confirmed requirement with no `verifies` tag is exempt. Per-criterion tagging is opt-in,
  and the coarser `tested-by` check still applies to it.
- A requirement whose criteria are unlabelled bullets is exempt, because there is no criterion
  label for a tag to address.
- A criterion marked `<!-- verifiable by: inspection -->` or `manual` is excluded from the
  warning and from the counts. No tag can ever cover it.

## Cases
CASE-1 — zero verifies tags is silent, not a violation
  Given  a confirmed requirement with two labelled criteria and zero `# verifies:` tags
         anywhere in the tree
  When   `gate` runs
  Then   its output contains no "criterion unverified" finding

CASE-2 — unlabelled bullet criteria never trigger the per-criterion warning
  Given  a confirmed requirement whose Cases are plain bullets, no `AC-N`/`CASE-N` labels,
         and a `# verifies:` tag present in code
  When   `gate` runs
  Then   its output contains no "criterion unverified" finding

CASE-3 — an inspection-only criterion never triggers the automatable-criteria warning
  Given  a confirmed requirement with `AC-1` tagged and `AC-2` marked
         `<!-- verifiable by: inspection -->`
  When   `gate` runs
  Then   its output contains no "automatable criteria" line


--------------------


---
id: REQ-ACVERIFY-823
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ACVERIFY-019]
---

# Emitting clauses, covered and gap on the map

## Description
> Once a requirement adopts per-criterion tagging, the map records how many criteria exist,
> how many are covered, and which are not — so a reviewer sees partial coverage without
> reading the gate output. An absent `clauses` field means the requirement was never
> measured, never a substituted zero.

Every bullet below is binding.
- The map emits `clauses` and `covered` on a requirement that has adopted per-criterion
  tagging, and omits both fields otherwise.
- The map emits a `gap` naming the untagged criteria when coverage is partial.
- An absent `clauses` means "not measured". No reader may substitute a number of its own.
- The check is warn-only. It never changes the gate's exit code.

## Cases
CASE-1 — clauses/covered appear only once tagging is adopted
  Given  a requirement with two labelled criteria and no `verifies` coverage passed to
         `_build_map_data`, and separately the same requirement with `AC-1` covered
  When   `_build_map_data` builds each node
  Then   the untagged node has no `clauses`/`covered` keys — absent means not measured,
         never a substituted zero — and the tagged node has `clauses: 2, covered: 1`

CASE-2 — gap names the untagged criteria only when coverage is partial
  Given  a two-criterion requirement with only `AC-1` covered, and separately one with
         both `AC-1` and its only criterion covered
  When   `_build_map_data` builds each node
  Then   the partial node's `gap` contains "AC-2" and the fully-covered node carries no
         `gap` key

CASE-3 — an unverified criterion warns but the gate exits 0
  Given  a confirmed requirement with `AC-1` tagged and `AC-2` untagged, nothing else
         causing an error
  When   `gate` runs
  Then   the run warns about AC-2 and still exits 0

