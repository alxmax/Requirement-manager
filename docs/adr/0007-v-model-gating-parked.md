# ADR-0007 — The V-model's right side is levelled; correspondence gating is parked

- **Status:** Accepted (parked, with a stated unpark trigger)
- **Decided:** 2026-08-17 (`REQ-VLEVEL-037`), parking recorded in `TODO.md` v3
- **Evidence:** `CHANGELOG.md` `v2.16.0`; `REQ-VLEVEL-037`; `REQ-TRACE-020`

## Context

This tool looks like it wants to be a V-model tool. It has requirement layers, traceability
links, test links and a gate — everything except the V-model's defining move: pairing each
specification level with the verification level that discharges it, and *gating* on the pairing
(unit tests answer to detailed design, system tests answer to stakeholder needs, and a gap at
any level is a finding).

Not implementing that is a decision. Left unrecorded it reads as an oversight — the omission an
assessor notices first — which is why it is written down here rather than left implicit.

## Decision

Ship the **vocabulary** and two asymmetric warnings; do **not** ship level-correspondence
gating or a `system` specification layer.

Shipped:

- `tested-by:` takes an optional level suffix — `@unit`, `@integration`, `@system`.
- `validated-against:` is redefined as the *validation* link — evidence the right thing was
  built — as opposed to `tested-by:`, evidence it was built correctly.
- Two warnings, chosen as the two asymmetric mistakes rather than a table: a confirmed `need`
  with no `validated-against:` link, and a confirmed `bus` requirement whose levelled links are
  **all** `@system`.

Rejected: a layer-to-level pairing table. Measured on this repo's corpus it would have flagged
**36 of 40** requirements for unit-testing a feature by calling its function — which is a sound
practice, not a defect ([ADR-0002](0002-error-versus-warning.md)).

## Consequences

- The tool answers "has this stakeholder need ever been validated?", which it could not before,
  without asserting a process model on repos that do not follow one.
- Both rules are silent on arrival: the first holds back until a repo carries at least one
  `validated-against:` tag anywhere, the second until a requirement carries at least one
  levelled link. Updating the engine adds no warnings to any repo.
- Redefining `validated-against:` was a semantic break for anyone using the old documented
  meaning ("config/data, re-validated on change"). Nothing fails, but the tags mean something
  different — called out explicitly in the release notes rather than buried.
- A regulated user evaluating this against IEC 61508 / ISO 26262 expectations will find the
  right-hand side of the V incomplete. That is the honest current state.

## Revisit when

A regulated user asks for it — a real project with an assessor, not an interest in the idea.
Building level-correspondence gating before that would encode one industry's process into a tool
whose users mostly do not have that process, and [ADR-0002](0002-error-versus-warning.md) says
what happens to a check that fires on correct work.
