---
id: REQ-SCAN-005
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
milestone: v1.04
---

# List members per capability

> This is the human-readable report that answers two everyday questions: "where is this
> capability actually built?" and "what have we written down but never built?" It lists every
> capability alongside the exact files and lines that claim it, and flags the ones with no
> code behind them at all. Without it, you would have to grep through the whole codebase by
> hand to find out where a feature lives or whether it exists yet.

## WHAT — Contract (normative)
- It shall print every capability id (the union of loaded requirements and discovered
  members, in sorted order) followed by its `role file:line` members, one per line.
- A capability with no members shall print `(no members found)`.
- A tag pointing at an id with no requirement shall still appear in the listing (so orphan
  tags and unimplemented requirements both surface).

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- This is the human-facing read of the thread; it answers "where is X implemented?" and
  "what is declared but never built?".

## HOW — Acceptance (= tests)
AC-1
  Given  a capability with two tags
  When   `scan` runs
  Then   both `role file:line` lines print under its id

AC-2
  Given  a requirement with no members
  When   `scan` runs
  Then   it prints `(no members found)`

AC-3
  Given  a tag pointing at an id with no requirement
  When   `scan` runs
  Then   the id still appears in the listing

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs the scan command before a review. The output lists LOGIN-001 with two lines
  pointing at the exact files that implement and test it, and shows REPORT-EXPORT-004 with
  `(no members found)` — instantly telling her that one capability was written down but
  never built yet.

## WHERE — Current implementation
- `cmd_scan` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
