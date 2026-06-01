---
id: REQ-SCAN-005
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
---

# List members per capability

> Show, for every capability, which code claims it — and which capabilities have no code.

## Input
- The loaded requirements and the discovered members.

## Description
This is the human-facing read of the thread: a flat listing that answers "where is
X implemented?" and, just as importantly, "what is declared but never built?".
Capabilities and members are unioned so an orphan tag (code with no requirement)
and an unimplemented requirement both show up.

## Output
- Printed lines: each capability id, then its `role file:line` members, or `(no members found)`.

## Acceptance (= tests)
- A capability with two tags prints both `role file:line` lines under its id.
- A requirement with no members prints `(no members found)`.
- A tag pointing at an id with no requirement still appears in the listing.

## Links
- Used by: (auto)
## Members in code (auto)
