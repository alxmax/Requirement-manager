---
id: SYS-SSOT-001
status: confirmed
level: system
layer: need
owner: Alex
priority: must-have
depends_on: []
superseded_by:
milestone: v1.00
lint_exempt: [ac-count-low]
---

# Stakeholder need — specs and code stay in sync

> On most projects the "spec" lives in someone's head, a stale wiki, or a ticket nobody
> reads, so over time the code says one thing and the docs say another. The people who own
> this project need the opposite: a single written source of truth for each capability that
> the build itself keeps honest. This is the underlying need the whole tool exists to serve —
> every feature below is here because it fulfils part of it.

## WHAT — Contract (normative)
- The project keeps a single written source of truth for each capability, living next to the code.
- Drift between a capability's description and its code is caught before it ships, not after.
- A reader can navigate from any capability to the code that implements it and the tests that verify it.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A `need` is a stakeholder requirement, not a capability: it is satisfied by other requirements (see "Satisfied by"), not implemented or tested by code directly, so the gate exempts it from the implements/tested-by checks.

## HOW — Acceptance (= tests)
AC-1a
  Given  a repo where a tag points to a non-existent requirement (dangling ref)
         or an enforced requirement (in-progress, implemented, or confirmed) has
         no implements: member (structural gap)
  When   the gate runs
  Then   the build fails (exit 1 — link-sync is an ERROR)

AC-1b
  Given  a repo where a confirmed requirement's contract was edited after the lock
  When   the gate runs
  Then   the drift is surfaced (WARN: "DRIFT — contract changed since lock") and
         the gate exits 0 — drift is reported, not blocking, by design

AC-2
  Given  a confirmed capability
  When   the gate runs
  Then   it has linked, existing code and tests

AC-3
  Given  any capability
  When   a reader runs `show`
  Then   they see its code locations and what depends on it

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- A new contributor joins Ana's team and asks "what is this service supposed to do?" Instead
  of guessing, she points them at the requirement files: each capability has one, the CI gate
  proves they match the code, and `show` walks from any one to its code and tests. The need —
  no more "the docs say X, the code does Y" — is met by the features that satisfy it.

## WHERE — Current implementation
- Not implemented by code — a stakeholder need is fulfilled by the requirements that declare `satisfies: SYS-SSOT-001` (the gate, the map, the dossier, and the traceability feature itself).

## Links
- Used by: (auto)
## Requirements in this system (auto)
- `SYS-AUTHOR-101` — Authoring and evolving a requirement  (system)
- `SYS-GATE-102` — Keeping code and specification in step  (system)
- `SYS-QUALITY-104` — Keeping requirements readable  (system)
- `SYS-READ-103` — Reading a repository  (system)
- `SYS-REPORT-105` — Answering what is here and what to do next  (system)
- `SYS-SHIP-108` — Adopting and shipping the engine  (system)
- `SYS-VISUAL-106` — Seeing the system at a glance  (system)
- `SYS-VMODEL-107` — Placing a requirement in the V  (system)
