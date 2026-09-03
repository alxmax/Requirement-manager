---
id: ARCH-SUGGESTVERIFIES-047
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-ACVERIFY-019, ARCH-SCAN-002]
satisfies: [SYS-QUALITY-104]
superseded_by:
milestone: v2.29
---

# Suggest per-criterion `verifies:` tags

## Description
> Per-criterion coverage is easy to adopt on a new requirement and expensive to adopt on an
> old corpus: in one real repo, 205 criteria carried no `verifies:` tag while 110 of them
> already had a test *named* after the criterion (`test_ac3_auditor_refuzat`). The link
> existed; it just was not machine-readable. This command proposes those links, so each
> consumer does not have to write the same matching script — and re-discover, one wrong
> link at a time, the three ways a naive match goes wrong.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a criterion       one labelled acceptance criterion, written `CASE-1`, `CASE-2`, and so on.
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
- A name matches a criterion only as a whole token, so `ac12` never matches `CASE-1`.
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

## Verify intent (open questions for the human)
- None — authored from a documented consumer session, not reconstructed from code.

## Notes & known limitations (informative)
- The proposal is lexical: it asserts a test is NAMED after a criterion, never that its
  assertions exercise it. That is the same trust boundary as `tested-by` ([[ARCH-TESTLINK-018]]).
- A test named after nothing is invisible to this command. The tool closes the naming-to-tag
  gap only, which is exactly the gap measured (110 of 205).

## Cases (= tests)
CASE-1  <!-- verifiable by: automated test -->
  Given  a requirement with an untagged `CASE-1` and a `def test_ac1_x` in its tested-by file
  When   `suggest-verifies` runs
  Then   it prints one proposal naming the file, the line and the tag to add
CASE-2  <!-- verifiable by: automated test -->
  Given  a tested-by file shared by two requirements and a test named `test_ac1_generic`
  When   `suggest-verifies` runs
  Then   no proposal is made for that criterion
CASE-3  <!-- verifiable by: automated test -->
  Given  a test whose name carries another requirement's number, such as `test_ac1_083_x`
  When   `suggest-verifies` runs
  Then   it is not proposed for the requirement whose file it sits in
CASE-4  <!-- verifiable by: automated test -->
  Given  two tests matching the same criterion
  When   `suggest-verifies --apply` runs
  Then   the criterion is reported as ambiguous and no tag is written
CASE-5  <!-- verifiable by: automated test -->
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




--------------------


---
id: REQ-SUGGESTVERIFIES-721
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# Suggest-verifies proposes a # verifies: <id>#AC-N tag for

> `suggest-verifies` proposes a `# verifies: <id>#AC-N` tag for each untagged criterion
> whose requirement has a test named after it.

Scenario: an untagged criterion with a matching test yields a proposal
  Given  a requirement with untagged `CASE-1` and its tested-by file defining `def test_case1_x`
  When   `suggest-verifies` runs
  Then   it proposes the tag `# verifies: <id>#CASE-1` for that test

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-722
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# Suggest-verifies searches only the tested-by files of the

> `suggest-verifies` searches only the `tested-by` files of the requirement that owns the
> criterion.

Scenario: matching is restricted to the owning requirement's tested-by files
  Given  a test named after `CASE-1` sitting in a file that is not this requirement's tested-by
         file
  When   `suggest-verifies` runs
  Then   that test is not proposed for the criterion

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-723
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# Suggest-verifies reads a test name from a def

> `suggest-verifies` reads a test name from a `def`, `function` or `func` declaration
> whose own name contains "test", or from an `it(...)`/`test(...)` label.

Scenario: a test name is read from a def, function, func or it/test label
  Given  a Python `def test_case1_x`, a JS `function test_case1_x()`, and a `it("test_case1_x",
         ...)` call
  When   `suggest-verifies` runs
  Then   each is recognized as a test named `test_case1_x`

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-724
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A criterion already carrying a verifies tag is

> A criterion already carrying a `verifies` tag is never proposed again.

Scenario: an already-tagged criterion is never re-proposed
  Given  a `CASE-1` already carrying a `# verifies:` tag and a matching test name
  When   `suggest-verifies` runs
  Then   no proposal is printed for that criterion

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-725
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A criterion marked as not machine-verifiable is never

> A criterion marked as not machine-verifiable is never proposed.

Scenario: a criterion marked not machine-verifiable is skipped
  Given  a `CASE-1` marked not machine-verifiable and a matching test name
  When   `suggest-verifies` runs
  Then   no proposal is printed for that criterion

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-726
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A name matches a criterion only as a

> A name matches a criterion only as a whole token, so `ac12` never matches `CASE-1`.

Scenario: matching requires a whole token, not a substring
  Given  a test named `test_ac12_x` and an untagged `CASE-1`
  When   `suggest-verifies` runs
  Then   `test_ac12_x` is not proposed as a match for `CASE-1`

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-727
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# When the tested-by file belongs to more than

> When the tested-by file belongs to more than one requirement, the test name also carries
> a distinctive token of this requirement's id, else no proposal is made.

Scenario: a shared tested-by file needs a distinctive id token to match
  Given  a tested-by file shared by two requirements and a test `test_ac1_generic` naming
         neither id distinctly
  When   `suggest-verifies` runs
  Then   no proposal is made for that criterion in either requirement

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-728
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A test whose name carries another requirement's number

> A test whose name carries another requirement's number belongs to that requirement, and
> is never proposed for this one.

Scenario: a test carrying another requirement's number belongs to that requirement
  Given  a test named `test_ac1_083_x` sitting in a file shared with requirement 083
  When   `suggest-verifies` runs
  Then   the test is proposed for requirement 083's `CASE-1`, not for the requirement whose file
         it sits in

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-729
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# When two or more tests match one criterion

> When two or more tests match one criterion, both are reported as ambiguous and neither
> is written.

Scenario: two matching tests report the criterion as ambiguous
  Given  two tests both named after the same untagged `CASE-1`
  When   `suggest-verifies` runs
  Then   the criterion is reported as ambiguous and no tag is proposed

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-730
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# Suggest-verifies writes nothing by default. It prints the

> `suggest-verifies` writes nothing by default. It prints the proposals and the
> ambiguities.

Scenario: a dry run prints proposals without writing
  Given  an untagged criterion with a matching test
  When   `suggest-verifies` runs without `--apply`
  Then   it prints the proposal, and the test file on disk stays unchanged

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-731
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# --apply appends each proposed tag to its test's

> `--apply` appends each proposed tag to its test's declaration line, in that file's
> comment syntax.

Scenario: --apply appends the tag using the file's comment syntax
  Given  a Python test file with an untagged matching test
  When   `suggest-verifies --apply` runs
  Then   the test's declaration line gains a trailing `# verifies: <id>#CASE-N` comment

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-732
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# --apply leaves a line that already carries the

> `--apply` leaves a line that already carries the same tag unchanged, so re-running it is
> safe.

Scenario: re-running --apply is a no-op for an already-tagged test
  Given  a test whose declaration line already carries the proposed `verifies` tag
  When   `suggest-verifies --apply` runs again
  Then   that line is left unchanged and no duplicate tag is added

## Members in code (auto)
