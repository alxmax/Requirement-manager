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
  assertions exercise it. That is the same trust boundary as `tested-by` ([[ARCH-TESTLINK-018]]).
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




--------------------


---
id: REQ-SUGGESTVERIFIES-721
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-722
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-723
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-724
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A criterion already carrying a verifies tag is

> A criterion already carrying a `verifies` tag is never proposed again.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-725
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A criterion marked as not machine-verifiable is never

> A criterion marked as not machine-verifiable is never proposed.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-726
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
superseded_by:
---

# A name matches a criterion only as a

> A name matches a criterion only as a whole token, so `ac12` never matches `AC-1`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-727
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-728
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-729
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-730
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-731
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SUGGESTVERIFIES-732
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
