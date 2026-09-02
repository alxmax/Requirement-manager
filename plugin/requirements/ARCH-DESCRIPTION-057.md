---
id: ARCH-DESCRIPTION-057
status: confirmed
form: atomic
level: architecture
layer: bus
owner: Alex
priority: should-have
verification: automated test
rationale: A reader met the same capability twice under two headings that both said WHAT — once as rationale, once as obligation — and the acceptance section was named after a sign-off step rather than after the cases it holds.
satisfies: [SYS-AUTHOR-101]
depends_on: [ARCH-PARSE-001, ARCH-DRIFT-003]
superseded_by:
---

# One Description section, and Cases instead of Acceptance

> As someone writing or reading a requirement, I want the intent and the binding clauses in a
> single `## Description` section and the criteria under `## Cases` as `CASE-1`, `CASE-2`, so
> that a requirement reads as one explanation followed by the cases that check it, instead of
> a rationale and a contract split across two headings that both said WHAT.

Scenario: a requirement written under the current names, and one written under the old ones
  Given  a requirement whose `## Description` opens with a `>` intent quote and continues in
         binding bullets, and whose `## Cases` section labels its criteria `CASE-N`
  When   the engine parses it, hashes its contract, lints it and a test tags one criterion
         with `# verifies: <ID>#CASE-N`
  Then   the quote is read as the intent and excluded from the drift hash while the bullets
         are the binding clauses, the criteria are counted and covered exactly as labelled
         criteria always were, and a requirement still written with `## WHAT — Contract`,
         `## HOW — Acceptance` and `AC-N` behaves in every one of those ways unchanged

## Members in code (auto)
