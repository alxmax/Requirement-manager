---
id: REQ-TESTLINK-018
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-CHECK-006]
superseded_by:
milestone: v1.15
---

# Test-link integrity check

> A requirement can claim it is tested by pointing at a test file — but if that file is gone
> or has no real test in it, the link is a lie and the safety net exists only on paper. This
> makes the gate check those links: it warns when a `tested-by` file is missing or holds no
> test, so a broken link cannot pose as coverage. Without it, a project can look fully tested
> while its tests have quietly disappeared.

## WHAT — Contract (normative)
- The gate shall check every `tested-by` link on a confirmed requirement. This is the deterministic half of behavior-sync.
- For each distinct `tested-by` file on a confirmed requirement, the gate shall verify two things: the file exists, and it contains at least one test function.
- A test function is recognized lexically: a Python `def test...(`, a JavaScript/TypeScript `function test...(` or a `it(`/`test(` call, a Go `func Test/Benchmark/Example/Fuzz(`, or a Rust `#[test]`. A `.py` file that exposes no `def test...` but drives its checks from a `run`/`run_tests`/`main` entry point under an `if __name__ == "__main__"` guard also counts — stdlib-only suites commonly take that form rather than a `def test...` per case, and a `tested-by` tag already declares the file a test.
- When a file is missing, unreadable, or holds no test function, the gate shall add one warning naming the requirement and the file.
- The check shall be warn-only. It never adds an error and never changes the pass or fail of the gate.
- The check shall be silent on a well-formed corpus, so it adds no noise to a green gate run.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- This does not prove that each acceptance criterion is tested. It proves only that real tests exist at the link target. Per-criterion mapping needs a per-criterion tag and is deferred.
- Detection is lexical, not a parse. A file that mentions a test-shaped call in a string could pass without real tests. The check targets the common failure: a renamed, deleted, or placeholder file, not a deliberate fake.
- Only confirmed requirements are checked. A draft or baseline requirement is exempt, matching the rest of the gate's enforcement scope.

## HOW — Acceptance (= tests)
AC-1
  Given  a confirmed requirement whose `tested-by` file is missing
  When   the gate runs
  Then   it adds a warning that names the requirement and the file

AC-2
  Given  a confirmed requirement whose `tested-by` file exists and contains a `def test...(`
  When   the gate runs
  Then   it adds no warning for that link

AC-3
  Given  a confirmed requirement whose `tested-by` file exists but contains no test function
  When   the gate runs
  Then   it adds a warning

AC-4
  Given  any of the above
  When   the gate runs
  Then   the error count is unchanged (the check is warn-only)

AC-5
  Given  a confirmed requirement whose `tested-by` is a `.py` file that has no `def test...` but defines a `run()`/`main()` entry point under an `if __name__ == "__main__"` guard
  When   the gate runs
  Then   it adds no warning for that link

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
