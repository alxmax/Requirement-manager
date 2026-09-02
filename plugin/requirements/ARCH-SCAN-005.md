---
id: ARCH-SCAN-005
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002]
satisfies: [SYS-REPORT-105]
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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a capability id  the id a requirement claims, or the id a code tag points at.
     a member         a place in the code tagged as belonging to that id.
     a role           what the member does for it: `implements`, `tested-by`,
                      `generated-from` or `validated-against`. -->

- `scan` prints every capability id, followed by its `role file:line` members, one
  member per line.
- The listed ids are the union of the loaded requirements and the discovered members,
  in sorted order.
- A capability with no members prints `(no members found)`.
- A tag pointing at an id with no requirement still appears in the listing, so orphan
  tags and unimplemented requirements both surface.

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




--------------------


---
id: REQ-SCAN-640
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-005]
superseded_by:
---

# Scan prints every capability id, followed by its

> `scan` prints every capability id, followed by its `role file:line` members, one member
> per line.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCAN-641
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-005]
superseded_by:
---

# The listed ids are the union of the

> The listed ids are the union of the loaded requirements and the discovered members, in
> sorted order.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCAN-642
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-005]
superseded_by:
---

# A capability with no members prints (no members

> A capability with no members prints `(no members found)`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCAN-643
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-005]
superseded_by:
---

# A tag pointing at an id with no

> A tag pointing at an id with no requirement still appears in the listing, so orphan tags
> and unimplemented requirements both surface.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
