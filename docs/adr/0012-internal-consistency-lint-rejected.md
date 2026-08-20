# ADR-0012 — No internal-consistency lint

- **Status:** Rejected (considered, deliberately not built)
- **Decided:** 2026-06-19, after a Senate deliberation; tracked and closed as issue #120
- **Evidence:** `TODO.md` v1.18, item 4

## Context

A requirement's frontmatter and its prose can contradict each other. The motivating case was
real: a `confirmed` requirement's `depends_on` graph had already been updated to a new model
while its prose contract still described the superseded one. The contradiction was sitting in
the file, in machine-readable form, and nothing looked at it.

The proposal was a lint that flags a requirement whose structured fields have moved on from
what its Contract and Acceptance sections assert.

## Decision

Do not build it.

The naive detector — "a `depends_on` id that never appears in the prose" — was measured against
this repo's corpus and produced a **78.6% false-positive rate**. Worse, it would have **missed
the motivating case**, which was an *added* edge, not an absent id.

The only detector that would work is baseline-aware: diff `depends_on` against a persisted
previous state. That needs roughly the machinery of member-hash drift
([ADR-0003](0003-drift-baseline-shape.md)) for a warn-only signal with an observed demand of
n=1 — disproportionate.

## Consequences

- The residual gap is narrow and named: a requirement's own frontmatter versus its own prose.
  It is the kind of contradiction a human PR reviewer sees, sitting in one file, side by side.
- The half of the original problem that *is* mechanical — a member changed while the spec did
  not — is covered by `REQ-MEMBERDRIFT-027`.
- This record exists because a rejection is worth as much as an acceptance here. Without it the
  gap looks unnoticed, and someone re-proposes the 78.6%-false-positive version.

## Revisit when

A second real frontmatter-versus-prose contradiction occurs in practice. Two beats one; the
measurement to repeat is the false-positive rate on a real corpus, not the appeal of the idea.
