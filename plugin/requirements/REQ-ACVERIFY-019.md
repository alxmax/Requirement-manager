---
id: REQ-ACVERIFY-019
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [REQ-CHECK-006, CORE-SCAN-002]
superseded_by:
milestone: v1.16
---

# Per-criterion test coverage

> Today the gate can tell you a requirement has *some* test, but not that *each* of
> its acceptance criteria is actually checked — so a requirement with five criteria
> and one test looks just as "covered" as one with five tests. This links each labelled
> criterion to the test that verifies it, so the gate can name the exact criterion that
> nobody tests. Without it, "Verifiable" is only true at the whole-requirement level and
> a half-tested requirement passes silently.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a labelled criterion  an acceptance criterion written as `AC-1`, `AC-2`, and so on,
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The link asserts a test *exists* for a criterion, not that the test's assertions actually exercise it — same lexical-trust limitation as `tested-by` (REQ-TESTLINK-018).
- A criterion can carry more than one `verifies` tag (several tests for one criterion); the check only asks for at least one.

## HOW — Acceptance (= tests)
AC-1
  Given  a requirement with labelled AC-1 and AC-2 and a test tagging `# verifies: REQ-X#AC-1`
  When   the gate runs
  Then   it warns that AC-2 is unverified and says nothing about AC-1
AC-2
  Given  a requirement whose every labelled criterion has a matching `verifies` tag
  When   the gate runs
  Then   it adds no per-criterion warning
AC-3
  Given  a confirmed requirement with labelled criteria but zero `verifies` tags
  When   the gate runs
  Then   it adds no per-criterion warning (per-criterion tagging is opt-in)
AC-4
  Given  a confirmed requirement whose criteria are unlabelled bullets
  When   the gate runs
  Then   it adds no per-criterion warning
AC-5
  Given  a confirmed requirement with a criterion marked `verifiable by: inspection`
  When   the gate runs
  Then   that criterion appears in no warning and in no emitted count
AC-6
  Given  a requirement with two labelled criteria of which one carries a `verifies` tag
  When   the map is generated
  Then   its node carries `clauses: 2`, `covered: 1`, and a `gap` naming the untagged one

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana's login requirement lists AC-1, AC-2, AC-3 but only AC-1 has a test. She tags that
  test `# verifies: AUTH-LOGIN-001#AC-1` and runs `reqmap.py gate`. The gate warns
  "AC-2 has no `# verifies` tag — criterion unverified" and the same for AC-3, so she sees
  exactly which two criteria still need a test instead of a vague "needs tests".

## WHERE — Current implementation
- `scan_ac_verifies`, `_acc_blocks`, `_labeled_acs`, `_automatable_acs`, `AC_VERIFY_RE` in `reqmap.py`, consumed by `cmd_check` and by `_attach_ac_coverage` — `scan_ac_verifies` collects `# verifies: <id>#AC-N` tags into `{cap: {AC-N: locations}}`, `_acc_blocks` is the single parser of the Acceptance section (labels, folded prose, and the `verifiable by:` marker), `_automatable_acs` drops the criteria a machine can never verify, `cmd_check` emits one aggregated warning naming the untagged ones, and `_attach_ac_coverage` puts `clauses`/`covered`/`gap` on the map node only when the requirement has adopted tagging.

## Links
- Used by: (auto)
## Members in code (auto)
