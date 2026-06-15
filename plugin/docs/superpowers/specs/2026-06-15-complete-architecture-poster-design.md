# Design — `requirement-manager — Complete Architecture` poster

**Date:** 2026-06-15
**Status:** approved (design) — pending spec review

## Goal

One canonical, high-quality, full-detail architecture poster for the
requirement-manager repo, modeled on `Consilium/docs/consilium_full` (stacked
sections, colour-by-role, comprehensive), **including the workflow**. It replaces
the several overlapping ad-hoc diagrams accumulated this session.

Success criterion: a single `.excalidraw` + `.html` built by one committed,
test-covered generator; **zero overlaps, zero arrow crossings, a structured
`legend()`, a `glossary()`, every section ≤ ~20 nodes**; `test_excalidraw.py` and
`check_versions.py` green.

## Artifact

- New generator: `plugin/skills/excalidraw-diagram/examples/make_full_architecture.py`
  - portable relative import (`../scripts`), `Scene(seed=…)` for byte-stability
  - `out_dir = sys.argv[1] or "docs"`; run with `diagrams` → writes to `diagrams/`
  - `save(..., crossing_check="error", legend_check="error")`
- Output (gitignored): `diagrams/full_architecture.{excalidraw,html}`

## Layout — vertically stacked sections (top → bottom)

Title (≈36) + one-line subtitle. One global `legend()` (colour = role) + a
`glossary()` at the bottom. Each section is a labelled region separated by
`s.bounds()` spacing.

1. **STRUCTURE** (C4 container view, uses `c4()`): plugin boundary containing
   `reqmap.py` (engine), `Skills ×3`, `Requirement specs` (SSOT data store),
   `Generated artifacts` (data store), `Map viewer`. ~6 nodes.
2. **WORKFLOW** (numbered pipeline, uses ISO 5807 decision diamond): terminator
   `Start` → `init` → `draft` → `confirm` → `sync` → `◇ gate: drift & links?`
   → `map` → `next` → terminator `Commit`. Gate "no" loops back to `sync`
   (on-page connector); a dashed "dogfood" feedback note. ~10 nodes.
3. **INTEGRATION**: `Developer / AI agent` (person) → `Claude Code` → invokes
   skill → seeds `reqmap.py` into a target repo; `git pre-commit` + `CI action
   @v1` run the gate; `marketplace` distributes; priors/dogfood loop. ~7 nodes.
4. **REQUIREMENT MODEL** (full detail): layers `bus / feature / need`; code tags
   `implements:` / `tested-by:`; `_reqlock.json` drift baseline. ~6 nodes.

## Colour roles (single legend)

`engine` (violet) · `skill` (blue) · `ssot` (indigo) · `artifact` (green) ·
`external` (grey) · `person` (teal) · `gate`/decision (orange). Every section
reuses these. `glossary()`: SSOT, drift, gate, dogfood, @v1, layer, vendored.

Feature coverage preserved after consolidation: the poster exercises `c4()` +
`person()` (Structure/Integration) and the ISO decision diamond (Workflow), so
those builder features stay test-covered even though the focused demos go away.

## Consolidation (retire all overlapping)

**Delete generators:** `make_architecture.py`, `gen_reqmap_workflow.py`,
`make_repo_map.py`, `make_c4_container.py`, `make_c4_full.py`.
**Keep:** `make_full_architecture.py` (new), `make_iso5807_flowchart.py` (ISO
demo), `make_excalidraw_skill_flow.py` (the skill's own flow — not overlapping).
**Delete stale outputs** under `diagrams/` for the retired generators.
**Doc updates:** `CLAUDE.md` and `SKILL.md` reference `make_architecture.py` /
`gen_reqmap_workflow.py` — repoint those to `make_full_architecture.py`.
**Version:** skill edit → keep the in-progress `2.2.0` bump (already applied).

## Verification

1. `python …/examples/make_full_architecture.py diagrams` → clean (error gates).
2. `python …/scripts/test_excalidraw.py` → all green; examples list non-empty.
3. `python scripts/check_versions.py` → 0 errors.
4. `git status` clean except intended changes; `diagrams/*` ignored.

## Phase 2 (deferred — engine)

Only if hand-coding the workflow band proves repetitive: add a `section(title,y)`
and/or `pipeline(steps, gates=…)` helper to `excalidraw_builder.py` to make
high-detail workflow posters first-class. Decide AFTER Phase 1 ships, based on
observed friction. Not part of this spec.
