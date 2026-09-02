# ADR-0017 — Consolidate Notes/Example/Current-implementation into one Context section

- **Status:** Accepted (modified from the original proposal per Senate feedback)
- **Decided:** 2026-09-02, after a nine-senator Senate audit (`runs/senate/2026-09-02_191837-reqmap-schema-simplify-context-merge-and-traceability.json`, two rounds, verdict MODIFY, 8 MODIFY / 1 GO, all eight blocking)
- **Companion record:** [ADR-0018](0018-no-contract-acceptance-traceability-marker-yet.md) — the second half of the audited proposal, rejected

## Context

The built-in requirement template carried three separate, always-informative headings —
`## WHAT — Notes & known limitations`, `## Example — in practice`, and `## WHERE — Current
implementation` — none of them hashed by `binding_hash`, none read by `_has_section`, none
linted. The only real distinction between them was narrative framing (a caveat vs. a worked
example vs. how the code does it today), not enforcement. An author picking one of the three
was making a choice about vocabulary, not about the contract.

The originally-audited proposal also included merging the `>` WHY blockquote into the same
consolidated section. The Senate's Wittgenstein and Socrate found, independently, that this
would have bought nothing: `_first_quote` (the WHY reader) is not heading-based — it reads
the first blockquote anywhere in the file — so the blockquote was never part of the
heading-choice problem this ADR addresses. It stays exactly where it is.

The Senate's Socrate and Wittgenstein also found the originally-audited proposal's central
premise false: `_build_map_data` reads `## WHAT — Notes` and `## WHERE — Current
implementation` **by heading label** to populate `_map.json`'s `notes` and `current_impl`
fields (48 and 51 of the 51 requirement files in this corpus carry them). A migration that
renamed the headings without also updating that emission code would have silently emptied
those fields, corpus-wide, in the committed `_map.json`/`_map.md` and in the viewer.

## Decision

Ship the consolidation as **purely additive**, not a migration:

1. A new `## Context (non-binding)` section, with bold `**Notes**` / `**Example**` /
   `**Current implementation**` sub-groups — the same clause-group convention the Contract
   section already uses for five-plus clauses (`_is_label_line`), rather than inventing a
   second grouping syntax.
2. `reqmap.py new`'s built-in template scaffolds the Context form for every **newly
   created** requirement.
3. The **legacy three-heading form stays fully valid, unchanged, forever** — this repo's
   own 51 requirement files are not migrated, and no consumer repo's existing corpus needs
   to change on an engine upgrade. `_build_map_data`'s `notes`/`current_impl` emission tries
   the legacy heading first (`_bullets`) and falls back to the matching Context sub-group
   (`_context_group`) only when the legacy heading is absent — never both at once in one
   file, so the fallback cannot mask real content a legacy-form file already has.
4. The two `draft`-emitting code paths scaffold the Context form too, so a promoted draft
   needs no reshaping (matching the pre-existing "emission schema matches
   `REQUIREMENT_TEMPLATE`" intent).

This directly answers the Senate's two structural objections (Musk, Aurelius, Dimon):
attacking the 51-file migration and the consumer-repo `check@v2` breaking-change risk both
assumed the legacy headings would stop being recognized. Neither this decision nor the code
that implements it removes that recognition, so neither risk exists. No batching, no
`_has_section` compatibility window, and no ADR-mandated migration script were needed —
because there is no migration.

The `>` WHY blockquote is explicitly **out of scope** for this decision — see Context above.

## Consequences

- `plugin/requirements/*.md`: zero files renamed or restructured. `git diff --stat` on the
  existing 51 requirement files for this decision: zero lines. (`REQ-CONTEXT-048.md` is a
  new file, not a migration of an existing one, and is itself written in the Context form as
  a live example.)
- `reqmap.py`: new `_context_group` (implements `REQ-CONTEXT-048`), a two-line fallback in
  `_build_map_data`, an updated `REQUIREMENT_TEMPLATE`, and updated `draft` emitters.
- `SKILL.md`: documents both forms; the legacy one is not deprecated, since consumer repos
  may have written extensive corpora against it and nothing about it is inferior — it is
  simply longer to choose from.
- New requirements get 4 named body sections to choose a home in (Contract, Verify intent,
  Acceptance, Context) instead of 6 (Contract, Verify intent, Notes, Acceptance, Example,
  WHERE); existing requirements are unaffected either way.

## Revisit when

- A future engine version wants to retire the legacy three-heading recognition entirely —
  that is a breaking schema change (major version bump per `CLAUDE.md`'s versioning rule)
  and needs its own ADR with a stated consumer-migration path, not a silent removal.
- Adoption data on this repo's own future requirements shows authors still splitting Context
  content across ad-hoc headings instead of the bold sub-groups — a sign the sub-group
  convention itself needs revisiting, not just documenting harder.
