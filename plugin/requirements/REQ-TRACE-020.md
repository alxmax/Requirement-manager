---
id: REQ-TRACE-020
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [CORE-PARSE-001, REQ-CHECK-006]
satisfies: [NEED-SSOT-001]
superseded_by:
milestone: v1.17
---

# Upstream traceability

> A requirement file tells you what a capability does and which code builds it, but not *why
> it exists* — which stakeholder need it serves. This lets a requirement point upward with a
> `satisfies:` field, so you can trace from a stakeholder need down to every requirement that
> fulfils it, and back up from any requirement to the need behind it. Without it, requirements
> float free of the needs that justify them, and a need can quietly go unaddressed.

## WHAT — Contract (normative)
- A requirement may declare a `satisfies:` frontmatter list of upstream ids (a stakeholder `need`, or a higher-level requirement) that it fulfils.
- The gate shall warn (never error) when a `satisfies:` id resolves to no requirement, because an upstream anchor may be authored later or tracked externally.
- The gate shall warn when a confirmed `need` has no requirement that satisfies it, so an unaddressed stakeholder need is visible.
- The `need` layer shall be exempt from the implements and tested-by checks, because a need is satisfied by other requirements, not implemented or tested by code.
- The dossier (`show`) shall print the upstream ids a requirement satisfies and the requirements that satisfy it, but only when the requirement participates in traceability.
- The map data shall carry `satisfies` and `satisfied_by` per node and a list of upstream edges, so a front-end can draw the trace.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A dangling `satisfies:` is a warning, not an error, so the field can hold an external reference (a ticket id) that the engine cannot resolve — at the cost of not catching a typo in an internal id.
- Traceability is opt-in: a requirement with no `satisfies:` is never flagged, matching the tool's subtle-guidance philosophy.

## HOW — Acceptance (= tests)
AC-1
  Given  a requirement with `satisfies: [GHOST-X-999]` and no such requirement
  When   the gate runs
  Then   it warns about the dangling upstream trace and does NOT raise an error
AC-2
  Given  a confirmed `need` that no requirement satisfies
  When   the gate runs
  Then   it warns that the need is unaddressed
AC-3
  Given  a confirmed `layer: need` requirement with no implements or tested-by tag
  When   the gate runs
  Then   it raises no implements/tested-by finding for that need
AC-4
  Given  a requirement that satisfies a need
  When   `show` runs on either the requirement or the need
  Then   the upstream/satisfied-by relationship is printed

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana writes `NEED-SSOT-001` for "specs and code stay in sync", then adds
  `satisfies: [NEED-SSOT-001]` to the gate and the map requirements. Running `reqmap.py show
  NEED-SSOT-001` now lists those features under "Satisfied by", and `show` on the gate lists
  the need under "Satisfies (upstream)". When she writes a need but forgets to point any
  requirement at it, the gate warns that the need is unaddressed.

## WHERE — Current implementation
- `cmd_check` (satisfies validation + need exemptions + orphan-need warn), `cmd_show` (upstream lines), and `_build_map_data` (`satisfies`/`satisfied_by` node fields + `upstream_edges`) in `reqmap.py`, plus `VALID_LAYER` gaining `need`.

## Links
- Used by: (auto)
## Members in code (auto)
