---
id: NEED-SSOT-001
status: confirmed
layer: need
owner: Alex
priority: must-have
depends_on: []
superseded_by:
milestone: v1.00
---

# Stakeholder need — specs and code stay in sync

> On most projects the "spec" lives in someone's head, a stale wiki, or a ticket nobody
> reads, so over time the code says one thing and the docs say another. The people who own
> this project need the opposite: a single written source of truth for each capability that
> the build itself keeps honest. This is the underlying need the whole tool exists to serve —
> every feature below is here because it fulfils part of it.

## WHAT — Contract (normative)
- The project shall keep a single written source of truth for each capability, living next to the code.
- Drift between a capability's description and its code shall be caught before it ships, not after.
- A reader shall be able to navigate from any capability to the code that implements it and the tests that verify it.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A `need` is a stakeholder requirement, not a capability: it is satisfied by other requirements (see "Satisfied by"), not implemented or tested by code directly, so the gate exempts it from the implements/tested-by checks.

## HOW — Acceptance (= tests)
- Given a repo where a requirement and its code disagree, when the gate runs, then the build fails.
- Given a confirmed capability, when the gate runs, then it has linked, existing code and tests.
- Given any capability, when a reader runs `show`, then they see its code locations and what depends on it.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- A new contributor joins Ana's team and asks "what is this service supposed to do?" Instead
  of guessing, she points them at the requirement files: each capability has one, the CI gate
  proves they match the code, and `show` walks from any one to its code and tests. The need —
  no more "the docs say X, the code does Y" — is met by the features that satisfy it.

## WHERE — Current implementation
- Not implemented by code — a stakeholder need is fulfilled by the requirements that declare `satisfies: NEED-SSOT-001` (the gate, the map, the dossier, and the traceability feature itself).

## Links
- Used by: (auto)
## Members in code (auto)
