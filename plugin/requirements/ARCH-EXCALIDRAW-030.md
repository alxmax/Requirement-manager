---
id: ARCH-EXCALIDRAW-030
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: []
milestone: v2.4
satisfies: [SYS-VISUAL-106]

---

# Excalidraw scene builder — core API

> The excalidraw-diagram skill needs a stdlib-only Python library that turns
> declarative shape and arrow declarations into a valid Excalidraw scene file
> and a self-contained HTML viewer, with no external dependencies, so the skill
> can be vendored into any environment without install friction.

## WHAT — Contract (normative)
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
- Used by: ARCH-EXCALIDRAW-031, ARCH-EXCALIDRAW-032
## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-352
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-353
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes shape primitives: box, ellipse, diamond, frame

> `Scene` exposes shape primitives: `box`, `ellipse`, `diamond`, `frame`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-354
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-355
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-356
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes annotation helpers: title, label, legend, glossary

> `Scene` exposes annotation helpers: `title`, `label`, `legend`, `glossary`, `role`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-357
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene exposes connector helpers: arrow, free_arrow, path, route_under

> `Scene` exposes connector helpers: `arrow`, `free_arrow`, `path`, `route_under`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-358
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-359
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# Scene(seed=<int>) produces byte-identical output across re-runs

> `Scene(seed=<int>)` produces byte-identical output across re-runs.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-360
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-030]
superseded_by:
---

# The builder has no external dependencies — stdlib

> The builder has no external dependencies — stdlib only.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
