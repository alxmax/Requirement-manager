---
id: ARCH-SUGGESTVERIFIES-047
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v2.29
depends_on: [ARCH-ACVERIFY-019, ARCH-SCAN-002]
satisfies: [SYS-QUALITY-104]
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
- `suggest-verifies` proposes a `# verifies: <id>#CASE-N` tag for each untagged criterion whose requirement's tested-by file has a test named after it. [[REQ-SUGGESTVERIFIES-927]] details the behaviour.
- A match requires a whole token naming the criterion (and, in a shared file, a distinctive id token too); an ambiguous match proposes nothing. [[REQ-SUGGESTVERIFIES-928]] details the behaviour.
- `suggest-verifies` writes nothing by default, only printing proposals and ambiguities; `--apply` writes the tags and is safe to re-run. [[REQ-SUGGESTVERIFIES-929]] details the behaviour.

## Cases
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

## Context
**Terms**
- a criterion       one labelled acceptance criterion, written `CASE-1`, `CASE-2`, and so on.
- a test name       the test function's own name, not its class and not its parameters.
- a tested-by file  a file a requirement names as its test file.
- a distinctive token  a word of an id that appears in no other requirement's id.

**Notes**
- The proposal is lexical: it asserts a test is NAMED after a criterion, never that its
  assertions exercise it. That is the same trust boundary as `tested-by` ([[ARCH-TESTLINK-018]]).
- A test named after nothing is invisible to this command. The tool closes the naming-to-tag
  gap only, which is exactly the gap measured (110 of 205).

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a repo with 55 requirements whose tests are already named `test_ac1_…`,
  `test_ac2_…`. She runs `reqmap.py sync --suggest-verifies`, reads 110 proposals and 6 ambiguities,
  re-runs with `--apply`, then `sync`. The gate now names the criteria that genuinely have no
  test, instead of the ones nobody had tagged yet.

**Current implementation**
- `cmd_suggest_verifies`, `_verifies_proposals`, `_test_functions`, `_ac_name_re` and
  `_apply_verifies` in `reqmap.py`. `_verifies_proposals` is pure and returns
  `(proposals, ambiguous)`; `_apply_verifies` is the only part that writes.


--------------------


---
id: REQ-SUGGESTVERIFIES-927
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
---

# Proposing a tag from a matching test name

## Description
> A test named `test_case1_x` already proves `CASE-1` — the link just is not
> machine-readable yet. `suggest-verifies` reads the tested-by files of the requirement
> that owns each untagged, machine-verifiable criterion, recognizing a test name from a
> `def`/`function`/`func` declaration or an `it(...)`/`test(...)` label, and proposes the
> tag that would make the link explicit.

Every bullet below is binding.
- `suggest-verifies` proposes a `# verifies: <id>#AC-N` tag for each untagged criterion whose
  requirement has a test named after it.
- `suggest-verifies` searches only the `tested-by` files of the requirement that owns the
  criterion.
- `suggest-verifies` reads a test name from a `def`, `function` or `func` declaration whose
  own name contains "test", or from an `it(...)`/`test(...)` label.
- A criterion already carrying a `verifies` tag is never proposed again.
- A criterion marked as not machine-verifiable is never proposed.

## Cases
CASE-1 — an untagged criterion with a matching test yields a proposal
  Given  a requirement with untagged `CASE-1` and its tested-by file defining `def test_case1_x`
  When   `suggest-verifies` runs
  Then   it proposes the tag `# verifies: <id>#CASE-1` for that test

CASE-2 — matching is restricted to the owning requirement's tested-by files
  Given  a test named after `CASE-1` sitting in a file that is not this requirement's tested-by
         file
  When   `suggest-verifies` runs
  Then   that test is not proposed for the criterion

CASE-3 — a test name is read from a def, function, func or it/test label
  Given  a Python `def test_case1_x`, a JS `function test_case1_x()`, and a `it("test_case1_x",
         ...)` call
  When   `suggest-verifies` runs
  Then   each is recognized as a test named `test_case1_x`

CASE-4 — an already-tagged criterion is never re-proposed
  Given  a `CASE-1` already carrying a `# verifies:` tag and a matching test name
  When   `suggest-verifies` runs
  Then   no proposal is printed for that criterion

CASE-5 — a criterion marked not machine-verifiable is skipped
  Given  a `CASE-1` marked not machine-verifiable and a matching test name
  When   `suggest-verifies` runs
  Then   no proposal is printed for that criterion


--------------------


---
id: REQ-SUGGESTVERIFIES-928
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
---

# Refusing a match that could be wrong

## Description
> A naive name match goes wrong in three specific ways: a substring match (`ac12` inside
> `CASE-1`), a generic name that fits any requirement sharing a test file, and a name that
> actually belongs to a different requirement's criterion. `suggest-verifies` checks for
> all three before proposing anything, and reports — rather than guesses at — a criterion
> matched by more than one test.

Every bullet below is binding.
- A name matches a criterion only as a whole token, so `ac12` never matches `CASE-1`.
- When the tested-by file belongs to more than one requirement, the test name also carries a
  distinctive token of this requirement's id, else no proposal is made.
- A test whose name carries another requirement's number belongs to that requirement, and is
  never proposed for this one.
- When two or more tests match one criterion, both are reported as ambiguous and neither is
  written.

## Cases
CASE-1 — matching requires a whole token, not a substring
  Given  a test named `test_ac12_x` and an untagged `CASE-1`
  When   `suggest-verifies` runs
  Then   `test_ac12_x` is not proposed as a match for `CASE-1`

CASE-2 — a shared tested-by file needs a distinctive id token to match
  Given  a tested-by file shared by two requirements and a test `test_ac1_generic` naming
         neither id distinctly
  When   `suggest-verifies` runs
  Then   no proposal is made for that criterion in either requirement

CASE-3 — a test carrying another requirement's number belongs to that requirement
  Given  a test named `test_ac1_083_x` sitting in a file shared with requirement 083
  When   `suggest-verifies` runs
  Then   the test is proposed for requirement 083's `CASE-1`, not for the requirement whose file
         it sits in

CASE-4 — two matching tests report the criterion as ambiguous
  Given  two tests both named after the same untagged `CASE-1`
  When   `suggest-verifies` runs
  Then   the criterion is reported as ambiguous and no tag is proposed


--------------------


---
id: REQ-SUGGESTVERIFIES-929
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SUGGESTVERIFIES-047]
---

# A dry run by default, --apply to write

## Description
> Proposing hundreds of tags across an old corpus should be reviewable before it is
> permanent, so `suggest-verifies` only prints by default. `--apply` appends each
> proposed tag to its test's declaration line in that file's own comment syntax, and
> leaves an already-tagged line untouched, so running it twice is safe.

Every bullet below is binding.
- `suggest-verifies` writes nothing by default. It prints the proposals and the ambiguities.
- `--apply` appends each proposed tag to its test's declaration line, in that file's comment
  syntax.
- `--apply` leaves a line that already carries the same tag unchanged, so re-running it is
  safe.

## Cases
CASE-1 — a dry run prints proposals without writing
  Given  an untagged criterion with a matching test
  When   `suggest-verifies` runs without `--apply`
  Then   it prints the proposal, and the test file on disk stays unchanged

CASE-2 — --apply appends the tag using the file's comment syntax
  Given  a Python test file with an untagged matching test
  When   `suggest-verifies --apply` runs
  Then   the test's declaration line gains a trailing `# verifies: <id>#CASE-N` comment

CASE-3 — re-running --apply is a no-op for an already-tagged test
  Given  a test whose declaration line already carries the proposed `verifies` tag
  When   `suggest-verifies --apply` runs again
  Then   that line is left unchanged and no duplicate tag is added

