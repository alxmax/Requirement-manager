---
id: REQ-EXCALIDRAW-030
status: confirmed
layer: feature
owner: Alex
depends_on: []
satisfies: [NEED-SSOT-001]
milestone: v2.4
---

# Excalidraw scene builder — core API

> The excalidraw-diagram skill needs a stdlib-only Python library that turns
> declarative shape and arrow declarations into a valid Excalidraw scene file
> and a self-contained HTML viewer, with no external dependencies, so the skill
> can be vendored into any environment without install friction.

## WHAT — Contract (normative)
- `Scene()` shall produce a valid Excalidraw JSON scene (schema version 2) with
  a `type: "excalidraw"` root and a `elements` list compatible with
  excalidraw.com import.
- `Scene` shall expose shape primitives: `box`, `ellipse`, `diamond`, `frame`.
- `Scene` shall expose ISO 5807 flowchart aliases: `process`, `terminator`,
  `decision`, `data`, `predefined_process`, `preparation`, `connector`.
- `Scene` shall expose layout helpers: `row`, `column`, `grid`, `enclose`,
  `lane`, `pipeline`, `section`, `align`, `distribute`.
- `Scene` shall expose annotation helpers: `title`, `label`, `legend`,
  `glossary`, `role`.
- `Scene` shall expose connector helpers: `arrow`, `free_arrow`, `path`,
  `route_under`.
- `.save(basename, out_dir)` shall write both `<basename>.excalidraw` (the
  scene JSON) and `<basename>.html` (a self-contained viewer) in one call and
  raise `RuntimeError` if called more than once on the same `Scene`.
- `Scene(seed=<int>)` shall produce byte-identical output across re-runs.
- The builder shall have no external dependencies — stdlib only.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes (informative)
- The authoritative usage reference is `skills/excalidraw-diagram/SKILL.md`.
- `save()` overlap detection raises on any two non-container shapes that
  overlap (co-ordinates checked after all shapes are added).

## HOW — Acceptance (= tests)

AC-1
  Given  a `Scene` with at least one `box` and one `arrow`
  When   `.save()` is called
  Then   both `<basename>.excalidraw` and `<basename>.html` are written and the
         `.excalidraw` file parses as valid JSON with `type: "excalidraw"`

AC-2
  Given  two `box` shapes placed at overlapping coordinates
  When   `.save()` is called without `allow_overlap=True`
  Then   a `ValueError` is raised naming the overlapping shapes

AC-3
  Given  `Scene(seed=42)` with identical shape declarations run twice
  When   both outputs are compared byte-for-byte
  Then   they are identical

AC-4
  Given  `.save()` has already been called once on a `Scene`
  When   `.save()` is called again
  Then   a `RuntimeError` is raised

AC-5
  Given  a `pipeline([...])` call with step dicts
  When   `.save()` is called
  Then   the resulting scene contains connected flowchart nodes with no
         overlapping shapes

## WHERE — Current implementation
- `class Scene` and all shape/layout/arrow methods in
  `skills/excalidraw-diagram/scripts/excalidraw_builder.py`.

## Links
- Used by: REQ-EXCALIDRAW-031, REQ-EXCALIDRAW-032
## Members in code (auto)
