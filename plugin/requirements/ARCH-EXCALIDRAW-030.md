---
id: ARCH-EXCALIDRAW-030
status: confirmed
level: system
layer: feature
owner: Alex
depends_on: []
milestone: v2.4
satisfies: [SYS-VISUAL-106]

---

# Excalidraw scene builder — core API

## Description
> The excalidraw-diagram skill needs a stdlib-only Python library that turns
> declarative shape and arrow declarations into a valid Excalidraw scene file
> and a self-contained HTML viewer, with no external dependencies, so the skill
> can be vendored into any environment without install friction.
- `Scene()` produces a valid Excalidraw JSON scene (schema version 2) with
  a `type: "excalidraw"` root and a `elements` list compatible with
  excalidraw.com import.
- `Scene` exposes shape primitives: `box`, `ellipse`, `diamond`, `frame`.
- `Scene` exposes ISO 5807 flowchart aliases: `process`, `terminator`,
  `decision`, `data`, `predefined_process`, `preparation`, `connector`.
- `Scene` exposes layout helpers: `row`, `column`, `grid`, `enclose`,
  `lane`, `pipeline`, `section`, `align`, `distribute`.
- `Scene` exposes annotation helpers: `title`, `label`, `legend`,
  `glossary`, `role`.
- `Scene` exposes connector helpers: `arrow`, `free_arrow`, `path`,
  `route_under`.
- `.save(basename, out_dir)` writes both `<basename>.excalidraw` (the
  scene JSON) and `<basename>.html` (a self-contained viewer) in one call and
  raises `RuntimeError` if called more than once on the same `Scene`.
- `Scene(seed=<int>)` produces byte-identical output across re-runs.
- The builder has no external dependencies — stdlib only.

## Verify intent (open questions for the human)
- None — authored from known intent.

## Notes (informative)
- The authoritative usage reference is `skills/excalidraw-diagram/SKILL.md`.
- `save()` overlap detection raises on any two non-container shapes that
  overlap (co-ordinates checked after all shapes are added).

## Cases (= tests)

CASE-1
  Given  a `Scene` with at least one `box` and one `arrow`
  When   `.save()` is called
  Then   both `<basename>.excalidraw` and `<basename>.html` are written and the
         `.excalidraw` file parses as valid JSON with `type: "excalidraw"`

CASE-2
  Given  two `box` shapes placed at overlapping coordinates
  When   `.save()` is called without `allow_overlap=True`
  Then   a `ValueError` is raised naming the overlapping shapes

CASE-3
  Given  `Scene(seed=42)` with identical shape declarations run twice
  When   both outputs are compared byte-for-byte
  Then   they are identical

CASE-4
  Given  `.save()` has already been called once on a `Scene`
  When   `.save()` is called again
  Then   a `RuntimeError` is raised

CASE-5
  Given  a `pipeline([...])` call with step dicts
  When   `.save()` is called
  Then   the resulting scene contains connected flowchart nodes with no
         overlapping shapes

## WHERE — Current implementation
- `class Scene` and all shape/layout/arrow methods in
  `skills/excalidraw-diagram/scripts/excalidraw_builder.py`.

## Links
- Used by: ARCH-EXCALIDRAW-031, ARCH-EXCALIDRAW-032
## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-352
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene() produces a valid Excalidraw JSON scene (schema

> `Scene()` produces a valid Excalidraw JSON scene (schema version 2) with a `type:
> "excalidraw"` root and a `elements` list compatible with excalidraw.com import.

Scenario: Scene() produces an excalidraw.com-importable JSON scene
  Given  a `Scene` with at least one shape added
  When   `.save()` writes the `.excalidraw` file
  Then   it parses as JSON with `type: "excalidraw"` and an `elements` list

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-353
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes shape primitives: box, ellipse, diamond, frame

> `Scene` exposes shape primitives: `box`, `ellipse`, `diamond`, `frame`.

Scenario: each shape primitive adds one element of its kind
  Given  a `Scene`
  When   `box`, `ellipse`, `diamond` and `frame` are each called once
  Then   the scene gains one element of each corresponding Excalidraw type

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-354
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes ISO 5807 flowchart aliases: process, terminator

> `Scene` exposes ISO 5807 flowchart aliases: `process`, `terminator`, `decision`, `data`,
> `predefined_process`, `preparation`, `connector`.

Scenario: ISO 5807 aliases produce their underlying shapes
  Given  a `Scene`
  When   `process`, `terminator`, `decision`, `data`, `predefined_process`, `preparation` and `connector` are each called
  Then   each adds an element without raising, using its mapped primitive shape

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-355
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes layout helpers: row, column, grid, enclose

> `Scene` exposes layout helpers: `row`, `column`, `grid`, `enclose`, `lane`, `pipeline`,
> `section`, `align`, `distribute`.

Scenario: layout helpers place shapes without overlap
  Given  three boxes
  When   `row([...])` arranges them
  Then   the resulting coordinates place them side by side with no overlapping pair

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-356
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes annotation helpers: title, label, legend, glossary

> `Scene` exposes annotation helpers: `title`, `label`, `legend`, `glossary`, `role`.

Scenario: annotation helpers attach text without raising
  Given  a `Scene` with one shape
  When   `title`, `label`, `legend`, `glossary` and `role` are each called
  Then   each adds its text element and `.save()` still succeeds

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-357
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes connector helpers: arrow, free_arrow, path, route_under

> `Scene` exposes connector helpers: `arrow`, `free_arrow`, `path`, `route_under`.

Scenario: connector helpers link two shapes
  Given  two boxes already placed in a `Scene`
  When   `arrow(a, b)` is called
  Then   the scene gains an arrow element bound to both shapes' ids

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-358
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# .save(basename, out_dir) writes both <basename>.excalidraw (the scene JSON)

> `.save(basename, out_dir)` writes both `<basename>.excalidraw` (the scene JSON) and
> `<basename>.html` (a self-contained viewer) in one call and raises `RuntimeError` if
> called more than once on the same `Scene`.

Scenario: one .save() call writes both output files
  Given  a `Scene` with at least one shape
  When   `.save("demo", out_dir)` is called
  Then   both `demo.excalidraw` and `demo.html` exist in `out_dir` after the single call

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-359
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene(seed=<int>) produces byte-identical output across re-runs

> `Scene(seed=<int>)` produces byte-identical output across re-runs.

Scenario: a fixed seed reproduces byte-identical output
  Given  the same shape declarations built twice with `Scene(seed=42)`
  When   each is saved to its own file
  Then   the two `.excalidraw` files are byte-for-byte identical

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-360
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# The builder has no external dependencies — stdlib

> The builder has no external dependencies — stdlib only.

Scenario: the builder imports only the standard library
  Given  `excalidraw_builder.py`
  When   its top-level imports are inspected
  Then   every imported module belongs to the Python standard library

## Members in code (auto)
