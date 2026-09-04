---
id: ARCH-SCAN-005
status: deprecated
level: architecture
layer: feature
owner: Alex
milestone: v1.04
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002]
satisfies: [SYS-REPORT-105]
---

# List members per capability

## Description
> This is the human-readable report that answers two everyday questions: "where is this
> capability actually built?" and "what have we written down but never built?" It lists every
> capability alongside the exact files and lines that claim it, and flags the ones with no
> code behind them at all. Without it, you would have to grep through the whole codebase by
> hand to find out where a feature lives or whether it exists yet.

Every bullet below is binding.
- `scan` prints every capability id — from requirements and code tags alike, sorted — followed by its `role file:line` members, one per line, or `(no members found)`. [[REQ-SCAN-910]] details the behaviour.

## Cases
CASE-1
  Given  a capability with two tags
  When   `scan` runs
  Then   both `role file:line` lines print under its id

CASE-2
  Given  a requirement with no members
  When   `scan` runs
  Then   it prints `(no members found)`

CASE-3
  Given  a tag pointing at an id with no requirement
  When   `scan` runs
  Then   the id still appears in the listing

## Context
**Terms**
- a capability id  the id a requirement claims, or the id a code tag points at.
- a member         a place in the code tagged as belonging to that id.
- a role           what the member does for it: `implements`, `tested-by`,
- `generated-from` or `validated-against`.

**Notes**
- This is the human-facing read of the thread; it answers "where is X implemented?" and
  "what is declared but never built?".

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs the scan command before a review. The output lists LOGIN-001 with two lines
  pointing at the exact files that implement and test it, and shows REPORT-EXPORT-004 with
  `(no members found)` — instantly telling her that one capability was written down but
  never built yet.

**Current implementation**
- `cmd_scan` in `reqmap.py`.


--------------------


---
id: REQ-SCAN-910
status: deprecated
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-005]
---

# List members per capability

## Description
> Finding where a capability is actually built otherwise means grepping the whole
> codebase by hand. `scan` lists every capability id — whether it comes from a
> requirement file or only from a code tag — with the exact `file:line` of each member,
> so an unimplemented requirement and an orphan tag both surface in one pass.

Every bullet below is binding.
- `scan` prints every capability id, followed by its `role file:line` members, one
  member per line.
- The listed ids are the union of the loaded requirements and the discovered members,
  in sorted order.
- A capability with no members prints `(no members found)`.
- A tag pointing at an id with no requirement still appears in the listing, so orphan
  tags and unimplemented requirements both surface.

## Cases
CASE-1 — every member is printed on its own line under its id
  Given  a corpus of one requirement carrying an `implements` and a `tested-by` member
  When   `scan` runs
  Then   the id is printed, followed by exactly two lines, each reading `role file:line`

CASE-2 — scan lists ids from both requirements and code tags, sorted
  Given  a requirement with no code tag and a code tag pointing at a different, unlisted id
  When   `scan` runs
  Then   both ids appear in the output in sorted order

CASE-3 — a requirement with no members prints the no-members marker
  Given  a requirement with no `implements`/`tested-by` tags anywhere in the code
  When   `scan` runs
  Then   its id is followed by `(no members found)`

CASE-4 — an orphan tag's id still appears in the listing
  Given  a code tag `# implements: GHOST-001` where no requirement `GHOST-001` exists
  When   `scan` runs
  Then   `GHOST-001` appears in the listing with its member line

