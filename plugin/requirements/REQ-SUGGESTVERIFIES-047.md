---
id: REQ-SUGGESTVERIFIES-047
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [REQ-ACVERIFY-019, CORE-SCAN-002]
superseded_by:
milestone: v2.29
---

# Suggest per-criterion `verifies:` tags

> Per-criterion coverage is easy to adopt on a new requirement and expensive to adopt on an
> old corpus: in one real repo, 205 criteria carried no `verifies:` tag while 110 of them
> already had a test *named* after the criterion (`test_ac3_auditor_refuzat`). The link
> existed; it just was not machine-readable. This command proposes those links, so each
> consumer does not have to write the same matching script — and re-discover, one wrong
> link at a time, the three ways a naive match goes wrong.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a criterion       one labelled acceptance criterion, written `AC-1`, `AC-2`, and so on.
     a test name       the test function's own name, not its class and not its parameters.
     a tested-by file  a file a requirement names as its test file.
     a distinctive token  a word of an id that appears in no other requirement's id. -->

**What it proposes**
- `suggest-verifies` proposes a `# verifies: <id>#AC-N` tag for each untagged criterion whose
  requirement has a test named after it.
- `suggest-verifies` searches only the `tested-by` files of the requirement that owns the
  criterion.
- `suggest-verifies` reads a test name from a `def`, `function` or `func` declaration whose
  own name contains "test", or from an `it(...)`/`test(...)` label.
- A criterion already carrying a `verifies` tag is never proposed again.
- A criterion marked as not machine-verifiable is never proposed.

**When it refuses to propose**
- A name matches a criterion only as a whole token, so `ac12` never matches `AC-1`.
- When the tested-by file belongs to more than one requirement, the test name also carries a
  distinctive token of this requirement's id, else no proposal is made.
- A test whose name carries another requirement's number belongs to that requirement, and is
  never proposed for this one.
- When two or more tests match one criterion, both are reported as ambiguous and neither is
  written.

**What it writes**
- `suggest-verifies` writes nothing by default. It prints the proposals and the ambiguities.
- `--apply` appends each proposed tag to its test's declaration line, in that file's comment
  syntax.
- `--apply` leaves a line that already carries the same tag unchanged, so re-running it is
  safe.

## WHAT — Verify intent (open questions for the human)
- None — authored from a documented consumer session, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The proposal is lexical: it asserts a test is NAMED after a criterion, never that its
  assertions exercise it. That is the same trust boundary as `tested-by` ([[REQ-TESTLINK-018]]).
- A test named after nothing is invisible to this command. The tool closes the naming-to-tag
  gap only, which is exactly the gap measured (110 of 205).

## HOW — Acceptance (= tests)
AC-1  <!-- verifiable by: automated test -->
  Given  a requirement with an untagged `AC-1` and a `def test_ac1_x` in its tested-by file
  When   `suggest-verifies` runs
  Then   it prints one proposal naming the file, the line and the tag to add
AC-2  <!-- verifiable by: automated test -->
  Given  a tested-by file shared by two requirements and a test named `test_ac1_generic`
  When   `suggest-verifies` runs
  Then   no proposal is made for that criterion
AC-3  <!-- verifiable by: automated test -->
  Given  a test whose name carries another requirement's number, such as `test_ac1_083_x`
  When   `suggest-verifies` runs
  Then   it is not proposed for the requirement whose file it sits in
AC-4  <!-- verifiable by: automated test -->
  Given  two tests matching the same criterion
  When   `suggest-verifies --apply` runs
  Then   the criterion is reported as ambiguous and no tag is written
AC-5  <!-- verifiable by: automated test -->
  Given  a single matching test
  When   `suggest-verifies --apply` runs twice
  Then   the tag is written once and the second run finds nothing to propose

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a repo with 55 requirements whose tests are already named `test_ac1_…`,
  `test_ac2_…`. She runs `reqmap.py suggest-verifies`, reads 110 proposals and 6 ambiguities,
  re-runs with `--apply`, then `sync`. The gate now names the criteria that genuinely have no
  test, instead of the ones nobody had tagged yet.

## WHERE — Current implementation
- `cmd_suggest_verifies`, `_verifies_proposals`, `_test_functions`, `_ac_name_re` and
  `_apply_verifies` in `reqmap.py`. `_verifies_proposals` is pure and returns
  `(proposals, ambiguous)`; `_apply_verifies` is the only part that writes.

## Links
- Used by: (auto)
## Members in code (auto)
