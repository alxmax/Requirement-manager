---
id: REQ-SCAN-005
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
---

# List members per capability

> Show, for every capability, which code claims it — and which capabilities have no code.

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
- A capability with two tags prints both `role file:line` lines under its id.
- A requirement with no members prints `(no members found)`.
- A tag pointing at an id with no requirement still appears in the listing.

## WHERE — Current implementation
- `cmd_scan` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
