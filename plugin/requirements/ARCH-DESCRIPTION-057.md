---
id: ARCH-DESCRIPTION-057
status: confirmed
level: architecture
layer: bus
owner: Alex
priority: should-have
depends_on: [ARCH-PARSE-001, ARCH-DRIFT-003]
satisfies: [SYS-AUTHOR-101]
---

# One Description section, and Cases instead of Acceptance

## Description
> A reader met the same capability twice under two headings that both said WHAT — once as rationale, once as obligation — and the acceptance section was named after a sign-off step rather than after the cases it holds.

Every bullet below is binding.
- `## Description` merges the intent quote with the binding clauses into one section, and `## Cases` (labelled `CASE-1`, `CASE-2`, …) replaces the older acceptance heading and its `AC-N` labels.
- A requirement still written with the older `## WHAT — Contract`, `## HOW — Acceptance` and `AC-N` spellings parses to the identical clause list and criterion count.
- A `# verifies: <ID>#CASE-N` or `#AC-N` tag resolves under either spelling.
- The intent quote sits inside the normative `## Description` section but is excluded from the drift hash, so improving the WHY never drifts a confirmed contract; editing a Contract clause or a Cases criterion still drifts.

## Cases
CASE-1 — both spellings parse to the same clauses and criterion count
  Given  the same requirement written once in the current form and once in the legacy form
  When   the engine parses each
  Then   both yield the identical Contract clause list and the identical criterion count

CASE-2 — a verifies tag resolves under either label
  Given  a `# verifies: <ID>#CASE-N` tag and a `# verifies: <ID>#AC-N` tag
  When   the engine matches each tag to its requirement's criteria
  Then   both resolve, because the label is an identifier a tag points at, not a fixed spelling

CASE-3 — the intent quote is excluded from the drift hash
  Given  a confirmed requirement whose `>` intent quote is edited but whose Contract and
         Cases are not
  When   `binding_hash` runs before and after the edit
  Then   the hash is unchanged

CASE-4 — editing a Contract clause or a Cases criterion still drifts
  Given  the same requirement edited once in a Contract clause and once in a Cases criterion
  When   `binding_hash` runs before and after each edit
  Then   both edits change the hash

CASE-5 — the intent is still read from inside the section
  Given  a requirement in the current form and one in the legacy form, both with the same
         intent quote
  When   `_first_quote` reads each
  Then   both return the identical intent text

