---
id: ARCH-TESTLINK-018
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-CHECK-006]
satisfies: [SYS-GATE-102]
superseded_by:
milestone: v1.15
---

# Test-link integrity check

## Description
> A requirement can claim it is tested by pointing at a test file — but if that file is gone
> or has no real test in it, the link is a lie and the safety net exists only on paper. This
> makes the gate check those links: it warns when a `tested-by` file is missing or holds no
> test, so a broken link cannot pose as coverage. Without it, a project can look fully tested
> while its tests have quietly disappeared.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     tested-by      a tag in code naming the file that tests a requirement.
     the gate       the `gate` command, run before every commit.
     lexically      recognised by the shape of the text, without parsing the language.
     behavior-sync  keeping the tests a requirement claims in step with the tests that exist. -->

**What it checks**
- The gate checks every `tested-by` link, at every status. This is the deterministic
  half of behavior-sync.
- For each distinct `tested-by` file, the gate verifies that the file exists.
- For each such file the gate also verifies that it holds at least one test function.

**What counts as a test function**
- The gate recognizes a test function lexically.
- A Python `def test...(` counts.
- A JavaScript or TypeScript `function test...(` counts.
- An `it(` call or a `test(` call counts.
- A Go `func Test/Benchmark/Example/Fuzz(` counts.
- A Rust `#[test]` counts.
- A `.py` file with no `def test...` also counts when it drives its checks from a
  `run`/`run_tests`/`main` entry point under an `if __name__ == "__main__"` guard.
- A shell `test_x()` function, a `function test_x` definition, or a bats `@test` counts.
- A shell file named by a test convention, such as `x.test.sh`, counts on its name alone.

**What it reports**
- When a file is missing, unreadable, or holds no test function, the gate adds one warning.
- That warning names the requirement and the file.

**How loud it is**
- The check is warn-only. It never adds an error, and never changes whether the gate passes.
- Under `--strict` the warning becomes an error only for a confirmed requirement.
- The check stays silent on a well-formed corpus, so a green gate run gains no noise.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The `run`/`main` entry-point form is accepted because stdlib-only suites commonly take that shape rather than a `def test...` per case, and a `tested-by` tag already declares the file a test.
- This does not prove that each acceptance criterion is tested. It proves only that real tests exist at the link target. Per-criterion mapping needs a per-criterion tag and is deferred.
- Detection is lexical, not a parse. A file that mentions a test-shaped call in a string could pass without real tests. The check targets the common failure: a renamed, deleted, or placeholder file, not a deliberate fake.
- Only confirmed requirements are checked. A draft or baseline requirement is exempt, matching the rest of the gate's enforcement scope.

## Cases (= tests)
CASE-1
  Given  a confirmed requirement whose `tested-by` file is missing
  When   the gate runs
  Then   it adds a warning that names the requirement and the file

CASE-2
  Given  a confirmed requirement whose `tested-by` file exists and contains a `def test...(`
  When   the gate runs
  Then   it adds no warning for that link

CASE-3
  Given  a confirmed requirement whose `tested-by` file exists but contains no test function
  When   the gate runs
  Then   it adds a warning

CASE-4
  Given  any of the above
  When   the gate runs
  Then   the error count is unchanged (the check is warn-only)

CASE-5
  Given  a confirmed requirement whose `tested-by` is a `.py` file with no `def test...`,
         but which defines a `run()`/`main()` entry point under an
         `if __name__ == "__main__"` guard
  When   the gate runs
  Then   it adds no warning for that link

CASE-6
  Given  a `tested-by` file that is a shell script holding a `test_x()` function
  When   the gate runs
  Then   it adds no warning for that link

CASE-7
  Given  a draft requirement whose `tested-by` file holds no test function
  When   the gate runs with `--strict`
  Then   it adds a warning and the exit code stays 0

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana renames a test file but forgets to update the requirement that points at it. On her
  next commit the gate warns: `tested-by` target not found for REQ-AUTH-001. She fixes the
  link, and the requirement's claim of test coverage is honest again.

## WHERE — Current implementation
- `_test_link_problem` in `reqmap.py`, called from `cmd_check` — `_test_link_problem` returns a short reason a file fails the check or an empty string when it passes; `cmd_check` resolves each distinct `tested-by` file against the scan root and appends one warning per failing link.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-733
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# The gate checks every tested-by link, at every

> The gate checks every `tested-by` link, at every status. This is the deterministic half
> of behavior-sync.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-734
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# For each distinct tested-by file, the gate verifies

> For each distinct `tested-by` file, the gate verifies that the file exists.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-735
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# For each such file the gate also verifies

> For each such file the gate also verifies that it holds at least one test function.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-736
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# The gate recognizes a test function lexically

> The gate recognizes a test function lexically.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-737
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A Python def test...( counts

> A Python `def test...(` counts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-738
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A JavaScript or TypeScript function test...( counts

> A JavaScript or TypeScript `function test...(` counts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-739
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# An it( call or a test( call counts

> An `it(` call or a `test(` call counts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-740
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A Go func Test/Benchmark/Example/Fuzz( counts

> A Go `func Test/Benchmark/Example/Fuzz(` counts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-741
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A Rust #test counts

> A Rust `#[test]` counts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-742
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A .py file with no def test... also

> A `.py` file with no `def test...` also counts when it drives its checks from a
> `run`/`run_tests`/`main` entry point under an `if __name__ == "__main__"` guard.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-743
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A shell test_x() function, a function test_x definition

> A shell `test_x()` function, a `function test_x` definition, or a bats `@test` counts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-744
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# A shell file named by a test convention

> A shell file named by a test convention, such as `x.test.sh`, counts on its name alone.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-745
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# When a file is missing, unreadable, or holds

> When a file is missing, unreadable, or holds no test function, the gate adds one
> warning.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-746
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# That warning names the requirement and the file

> That warning names the requirement and the file.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-747
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# The check is warn-only. It never adds an

> The check is warn-only. It never adds an error, and never changes whether the gate
> passes.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-748
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# Under --strict the warning becomes an error only

> Under `--strict` the warning becomes an error only for a confirmed requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TESTLINK-749
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TESTLINK-018]
superseded_by:
---

# The check stays silent on a well-formed corpus

> The check stays silent on a well-formed corpus, so a green gate run gains no noise.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
