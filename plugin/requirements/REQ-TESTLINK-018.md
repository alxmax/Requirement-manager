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

> Make a `tested-by` link mean something: the gate warns when the linked file is missing or holds no tests, so a broken link cannot pose as test coverage.

## WHAT — Contract (normative)
- The gate shall check every `tested-by` link on a confirmed requirement. This is the deterministic half of behavior-sync.
- For each distinct `tested-by` file on a confirmed requirement, the gate shall verify two things: the file exists, and it contains at least one test function.
- A test function is recognized lexically: a Python `def test...(`, a JavaScript `function test...(`, or a `it(` or `test(` call.
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
- Given a confirmed requirement whose `tested-by` file is missing, when the gate runs, then it adds a warning that names the requirement and the file.
- Given a confirmed requirement whose `tested-by` file exists and contains a `def test...(`, when the gate runs, then it adds no warning for that link.
- Given a confirmed requirement whose `tested-by` file exists but contains no test function, when the gate runs, then it adds a warning.
- Given any of the above, when the gate runs, then the error count is unchanged (the check is warn-only).

## WHERE — Current implementation
- `_test_link_problem` in `reqmap.py`, called from `cmd_check` — `_test_link_problem` returns a short reason a file fails the check or an empty string when it passes; `cmd_check` resolves each distinct `tested-by` file against the scan root and appends one warning per failing link.

## Links
- Used by: (auto)
## Members in code (auto)
