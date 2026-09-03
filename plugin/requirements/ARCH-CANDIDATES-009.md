---
id: ARCH-CANDIDATES-009
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-SCAN-002]
satisfies: [SYS-READ-103]
superseded_by:
milestone: v1.06
---

# Capability candidates (extraction plan)

## Description
> When you point this tool at an old codebase that has no requirements written down yet,
> this is the first, look-but-don't-touch step. It reads the code and produces a tidy
> machine-readable plan that guesses what each capability is — which files belong together,
> what they depend on, how central each one is — without writing or changing a single
> requirement file. An author (or an AI assistant) then uses that plan to decide what to
> actually write up. Without it, you would face a wall of untagged code with no starting map.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a candidate    one proposed capability in the plan: a guess that these files
                    belong together and deserve one requirement.
     per-file facts what `plan` reads out of a file without interpreting it —
                    docstrings, signatures, imports, size.
     the SSOT dir   the `requirements/` directory itself.
     noise dirs     `.git`, `node_modules`, `__pycache__`. -->

**What it emits**
- `plan` emits a single JSON object, to stdout or to `--out PATH`, shaped
  `{engine_version, bus[], candidates[]}`.
- `plan` writes NO `.md` files. It cannot repeat `draft`'s empty-stub failure.

**What it reads**
- `plan` walks the code with the same exclusions as scanning: noise dirs, the SSOT dir,
  and `.reqmapignore` resolved in `requirements/` first.
- `plan` gathers per-file facts: module and symbol docstrings, top-level signatures,
  import targets, and line count.
- `plan` lists every scannable code file as a candidate, the same set `draft` walks.
  A file in a language `plan` cannot parse is still a candidate, with empty facts.
- `plan` reads top-level signatures from Python via `ast` — functions, classes and the
  public methods of each class — and from JS/TS via best-effort parsing.
- An unparseable file yields empty facts. It never aborts the plan.

**What a candidate carries**
- Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{},
  signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc,
  split_candidate, is_test}`.
- `is_test` is true when every file of the candidate is test code by convention: a
  `tests/`-style directory segment, a `test_*` basename, or a `*_test`/`*.spec` suffix.
- `depends_on` is derived from imports resolved to other candidates.
- `suggested_layer` is `bus` when `importer_count ≥ BUS_FANIN_THRESHOLD`, else `feature`.
- A file already carrying an `implements:` tag is reported via `existing_req`.

**How it groups files**
- `plan` groups files by `requirements/_capmap.json` when that file is present, and
  treats it as authoritative.
- Absent `_capmap.json`, `plan` falls back to one candidate per file.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- Read-only by design — merge/split judgment is left to the Stage-2 authoring agent.
- Import→candidate resolution matches on file stem, so a stdlib-shadowing or same-basename
  import can produce a false `depends_on` edge for the author to prune.

## Cases (= tests)
CASE-1
  Given  any corpus
  When   `plan` runs
  Then   it writes zero `.md` files and emits valid JSON

CASE-2
  Given  a file listed in `.reqmapignore` (including one placed in `requirements/`)
  When   `plan` runs
  Then   that file is absent from every candidate's `files`

CASE-3
  Given  an import of a local module
  When   `plan` runs
  Then   a `depends_on` edge points at that module's candidate

CASE-4
  Given  a `requirements/_capmap.json` grouping two files under one id
  When   `plan` runs
  Then   they appear as a single candidate carrying both files with the declared layer

CASE-5
  Given  a file already carrying an `implements:` tag
  When   `plan` runs
  Then   it is reported via `existing_req`

CASE-6
  Given  a module imported by `BUS_FANIN_THRESHOLD` or more candidates
  When   `plan` runs
  Then   it is suggested as `bus`

CASE-7
  Given  a `.go` file and a `tests/test_x.py` file, and no `_capmap.json`
  When   `plan` runs
  Then   both are candidates; the `.go` one carries empty signatures and the test one carries `is_test: true`

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a large untagged service and runs the `plan` command. It prints a JSON
  plan listing each file as a proposed capability, with a suggested id, the functions it
  defines, and which other proposed capabilities it depends on. The shared `db.py` is
  imported by many files, so it is suggested as a `bus` capability — giving Ana a ranked
  starting point to author real requirements, and not one `.md` file was created.

## WHERE — Current implementation
- `cmd_candidates` and the `_py_facts`/`_js_facts`/`_file_facts`/`_load_capmap`/`_collect_files` helpers in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-257
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan emits a single JSON object, to stdout

> `plan` emits a single JSON object, to stdout or to `--out PATH`, shaped
> `{engine_version, bus[], candidates[]}`.

Scenario: plan emits one JSON object with the documented shape
  Given  a small codebase
  When   `plan` runs with no `--out`
  Then   stdout parses as one JSON object carrying `engine_version`, `bus` and `candidates`

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-258
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan writes NO .md files. It cannot repeat

> `plan` writes NO `.md` files. It cannot repeat `draft`'s empty-stub failure.

Scenario: plan writes zero .md files
  Given  an untagged codebase
  When   `plan --out plan.json` runs
  Then   no `.md` file appears anywhere in the requirements directory

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-259
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan walks the code with the same exclusions

> `plan` walks the code with the same exclusions as scanning: noise dirs, the SSOT dir,
> and `.reqmapignore` resolved in `requirements/` first.

Scenario: plan skips the same paths scanning skips
  Given  a file listed in `.reqmapignore` and a file inside `node_modules`
  When   `plan` runs
  Then   neither file appears in any candidate's `files`

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-260
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan gathers per-file facts: module and symbol docstrings

> `plan` gathers per-file facts: module and symbol docstrings, top-level signatures,
> import targets, and line count.

Scenario: per-file facts capture docstrings, signatures, imports and size
  Given  a Python file with a module docstring, one function, and one import
  When   `plan` runs
  Then   that file's candidate carries the docstring, the function signature, the import, and a line count

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-261
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan lists every scannable code file as a

> `plan` lists every scannable code file as a candidate, the same set `draft` walks. A
> file in a language `plan` cannot parse is still a candidate, with empty facts.

Scenario: an unparseable file still becomes a candidate
  Given  a `.go` file among the scanned files
  When   `plan` runs
  Then   that file appears as a candidate with empty facts, not omitted

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-262
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan reads top-level signatures from Python via ast

> `plan` reads top-level signatures from Python via `ast` — functions, classes and the
> public methods of each class — and from JS/TS via best-effort parsing.

Scenario: Python signatures come from ast, not text matching
  Given  a Python file defining a class with one public and one `_private` method
  When   `plan` reads its signatures
  Then   the public method appears in the candidate's `signatures` and the private one does not

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-263
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# An unparseable file yields empty facts. It never

> An unparseable file yields empty facts. It never aborts the plan.

Scenario: an unparseable file never aborts the run
  Given  a codebase containing one syntactically broken Python file among valid ones
  When   `plan` runs
  Then   it completes and emits candidates for the valid files, with empty facts for the broken one

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-264
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Each candidate carries {suggested_id, suggested_layer, files, docstrings{}, signatures

> Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{},
> signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc,
> split_candidate, is_test}`.

Scenario: every candidate carries the full documented field set
  Given  any file scanned by `plan`
  When   its candidate is built
  Then   the candidate dict carries all of `suggested_id`, `suggested_layer`, `files`, `docstrings`, `signatures`, `imports`, `depends_on`, `tested_by`, `importer_count`, `existing_req`, `loc`, `split_candidate` and `is_test`

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-265
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Is_test is true when every file of the

> `is_test` is true when every file of the candidate is test code by convention: a
> `tests/`-style directory segment, a `test_*` basename, or a `*_test`/`*.spec` suffix.

Scenario: is_test follows test-file convention, not content
  Given  a file at `tests/test_foo.py` alongside an ordinary module
  When   `plan` runs
  Then   the test file's candidate carries `is_test: true` and the ordinary module's does not

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-266
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Depends_on is derived from imports resolved to other

> `depends_on` is derived from imports resolved to other candidates.

Scenario: an import edge becomes a depends_on edge
  Given  file `a.py` importing local module `b.py`
  When   `plan` runs
  Then   `a.py`'s candidate lists `b.py`'s candidate in `depends_on`

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-267
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Suggested_layer is bus when importer_count ≥ BUS_FANIN_THRESHOLD, else

> `suggested_layer` is `bus` when `importer_count ≥ BUS_FANIN_THRESHOLD`, else `feature`.

Scenario: high fan-in earns a bus suggestion
  Given  a module imported by at least `BUS_FANIN_THRESHOLD` other candidates
  When   `plan` runs
  Then   that module's candidate carries `suggested_layer: "bus"`

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-268
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# A file already carrying an implements: tag is

> A file already carrying an `implements:` tag is reported via `existing_req`.

Scenario: an already-tagged file reports its existing requirement
  Given  a file carrying `# implements: ARCH-EXAMPLE-001`
  When   `plan` runs
  Then   that file's candidate carries `existing_req: "ARCH-EXAMPLE-001"`

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-269
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Plan groups files by requirements/_capmap.json when that file

> `plan` groups files by `requirements/_capmap.json` when that file is present, and treats
> it as authoritative.

Scenario: _capmap.json groups files into one candidate
  Given  a `requirements/_capmap.json` grouping two files under one id
  When   `plan` runs
  Then   both files appear together as one candidate carrying the declared layer

## Members in code (auto)




--------------------


---
id: REQ-CANDIDATES-270
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
superseded_by:
---

# Absent _capmap.json, plan falls back to one candidate

> Absent `_capmap.json`, `plan` falls back to one candidate per file.

Scenario: no capmap means one candidate per file
  Given  a codebase with no `requirements/_capmap.json`
  When   `plan` runs
  Then   every file becomes its own separate candidate

## Members in code (auto)
