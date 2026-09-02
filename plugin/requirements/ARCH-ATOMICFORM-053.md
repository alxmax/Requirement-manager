---
id: ARCH-ATOMICFORM-053
status: confirmed
form: atomic
level: architecture
layer: feature
owner: Alex
priority: should-have
verification: automated test
rationale: One obligation per file makes the clause the unit a test answers to, and removes the two headings that only restated each other.
depends_on: [ARCH-PARSE-001, ARCH-DRIFT-003, ARCH-CHECK-006]
satisfies: [SYS-AUTHOR-101]
superseded_by:
---

# The atomic requirement form

> As someone writing a requirement that states a single obligation, I want to write it as a
> story plus one Scenario with no Contract or Acceptance headings, so that the file carries
> the obligation and its proof and nothing else, while drift detection keeps working.

Scenario: an atomic body is read as both normative sections
  Given  a body whose only content before the first `## ` heading is a `>` statement
         followed by a `Scenario:` block
  When   the gate, the linter and the drift hash read it
  Then   `binding_hash` covers the statement and the Scenario rather than the empty string,
         both normative sections count as present, the Scenario counts as one acceptance
         criterion, and no missing-section, legacy-schema or under-specified finding is
         raised

## Members in code (auto)
