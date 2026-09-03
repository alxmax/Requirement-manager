---
id: ARCH-EXCALIDRAW-032
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-EXCALIDRAW-030]
milestone: v2.4
satisfies: [SYS-VISUAL-106]

---

# Excalidraw builder CLI verbs

## Description
> Diagrams need to be rebuilt when source changes: either from a generator
> script (the main authoring path), from a hand-edited `.excalidraw` file
> (viewer rebuild only), or from an existing repo that needs a scaffolded
> starting point (discover). The CLI exposes these as three distinct verbs so
> each use-case has a single, unambiguous entry point.
- Invoking `python excalidraw_builder.py` with **no arguments** runs the
  builder smoke test, prints a human-readable summary, and exits 0 on success.
  This is the CI health-check entry point and is never shadowed by a new
  default verb.
- `python excalidraw_builder.py render <scene.excalidraw> [out_dir]` reads
  an existing `.excalidraw` file and writes a fresh self-contained
  `<basename>.html` viewer beside it (or into `out_dir` when given). The
  source `.excalidraw` file is never modified.
- `python excalidraw_builder.py discover <repo> [out.py]` scans `<repo>`
  for source files and emits a runnable multi-layer poster stub (STRUCTURE layer
  pre-populated, WORKFLOW / INTEGRATION / MODES / MODEL / DATA layers
  commented as scaffolds) to `out.py` (default: `make_diagram.py`).
- Any unrecognised verb exits with code 2 and prints a usage message.

## Verify intent (open questions for the human)
- None — authored from known intent.

## Notes (informative)
- `discover` only scaffolds the *components* it can see; inferring real data
  flow and grouping remains the author's responsibility.
- The smoke test (no-arg invocation) is what CI depends on — do not change the
  no-arg behaviour.

## Cases (= tests)

CASE-1
  Given  no arguments
  When   `python excalidraw_builder.py` is run
  Then   it exits 0 and stdout contains a success/summary line (not an error)

CASE-2
  Given  a valid `.excalidraw` file at `<path>`
  When   `render <path>` is run
  Then   a `<basename>.html` is written; the source `.excalidraw` is unchanged

CASE-3
  Given  a directory containing at least one `.py` source file
  When   `discover <dir>` is run
  Then   a runnable Python stub is emitted that imports `excalidraw_builder`
         and calls `.save()`

CASE-4
  Given  an unknown verb such as `frobnicate`
  When   `python excalidraw_builder.py frobnicate`
  Then   the process exits with code 2 and prints usage

## WHERE — Current implementation
- `_main(argv)` and the `render_html`, `discover_stub` functions in
  `skills/excalidraw-diagram/scripts/excalidraw_builder.py`.
- `skills/excalidraw-diagram/scripts/test_excalidraw.py` (CLI test class).

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-370
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-032]
superseded_by:
---

# Invoking python excalidraw_builder.py with no arguments runs the

> Invoking `python excalidraw_builder.py` with **no arguments** runs the builder smoke
> test, prints a human-readable summary, and exits 0 on success. This is the CI
> health-check entry point and is never shadowed by a new default verb.

Scenario: no-arg invocation runs the smoke test and exits 0
  Given  no command-line arguments
  When   `python excalidraw_builder.py` runs
  Then   it prints a success summary line and exits 0

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-371
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-032]
superseded_by:
---

# Python excalidraw_builder.py render <scene.excalidraw> out_dir reads an existing

> `python excalidraw_builder.py render <scene.excalidraw> [out_dir]` reads an existing
> `.excalidraw` file and writes a fresh self-contained `<basename>.html` viewer beside it
> (or into `out_dir` when given). The source `.excalidraw` file is never modified.

Scenario: render rebuilds the HTML viewer without touching the source
  Given  an existing `<scene>.excalidraw` file
  When   `render <scene>.excalidraw` runs
  Then   a fresh `<scene>.html` is written and the `.excalidraw` file's bytes are unchanged

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-372
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-032]
superseded_by:
---

# Python excalidraw_builder.py discover <repo> out.py scans <repo> for

> `python excalidraw_builder.py discover <repo> [out.py]` scans `<repo>` for source files
> and emits a runnable multi-layer poster stub (STRUCTURE layer pre-populated, WORKFLOW /
> INTEGRATION / MODES / MODEL / DATA layers commented as scaffolds) to `out.py` (default:
> `make_diagram.py`).

Scenario: discover emits a runnable multi-layer stub
  Given  a repository containing at least one source file
  When   `discover <repo> out.py` runs
  Then   `out.py` is written, imports `excalidraw_builder`, and runs without error

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-373
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-032]
superseded_by:
---

# Any unrecognised verb exits with code 2 and

> Any unrecognised verb exits with code 2 and prints a usage message.

Scenario: an unknown verb exits 2 with usage
  Given  the verb `frobnicate`
  When   `python excalidraw_builder.py frobnicate` runs
  Then   it exits with code 2 and prints a usage message

## Members in code (auto)
