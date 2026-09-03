---
id: ARCH-CANDIDATES-009
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.06
depends_on: [ARCH-SCAN-002]
satisfies: [SYS-READ-103]
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
- `plan` emits a single JSON object, to stdout or to `--out PATH`, shaped `{engine_version, bus[], candidates[]}`, and writes no `.md` files. [[REQ-CANDIDATES-826]]
- Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{}, signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc, split_candidate, is_test}`. [[REQ-CANDIDATES-827]]

## Cases
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

## Context
**Terms**
- a candidate    one proposed capability in the plan: a guess that these files
- belong together and deserve one requirement.
- per-file facts what `plan` reads out of a file without interpreting it —
- docstrings, signatures, imports, size.
- the SSOT dir   the `requirements/` directory itself.
- noise dirs     `.git`, `node_modules`, `__pycache__`.

**Notes**
- Read-only by design — merge/split judgment is left to the Stage-2 authoring agent.
- Import→candidate resolution matches on file stem, so a stdlib-shadowing or same-basename
  import can produce a false `depends_on` edge for the author to prune.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a large untagged service and runs the `plan` command. It prints a JSON
  plan listing each file as a proposed capability, with a suggested id, the functions it
  defines, and which other proposed capabilities it depends on. The shared `db.py` is
  imported by many files, so it is suggested as a `bus` capability — giving Ana a ranked
  starting point to author real requirements, and not one `.md` file was created.

**Current implementation**
- `cmd_candidates` and the `_py_facts`/`_js_facts`/`_file_facts`/`_load_capmap`/`_collect_files` helpers in `reqmap.py`.


--------------------


---
id: REQ-CANDIDATES-826
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
---

# The plan's JSON shape and read-only scanning

## Description
> Everything else in the pipeline — `draft`, `review`, `confirm` — writes files. `plan`
> deliberately does not: it is the look-before-you-leap step for an untagged codebase, so a
> wrong or half-formed plan can be thrown away with zero cleanup. It walks the code with the
> same exclusions as scanning, so it never lists a file a real scan would skip.

Every bullet below is binding.
- `plan` emits a single JSON object, to stdout or to `--out PATH`, shaped
  `{engine_version, bus[], candidates[]}`.
- `plan` writes NO `.md` files. It cannot repeat `draft`'s empty-stub failure.
- `plan` walks the code with the same exclusions as scanning: noise dirs, the SSOT dir,
  and `.reqmapignore` resolved in `requirements/` first.
- `plan` gathers per-file facts: module and symbol docstrings, top-level signatures,
  import targets, and line count.
- `plan` lists every scannable code file as a candidate, the same set `draft` walks.
  A file in a language `plan` cannot parse is still a candidate, with empty facts.
- `plan` reads top-level signatures from Python via `ast` — functions, classes and the
  public methods of each class — and from JS/TS via best-effort parsing.
- An unparseable file yields empty facts. It never aborts the plan.

## Cases
CASE-1 — plan emits one JSON object with the documented shape
  Given  a small codebase
  When   `plan` runs with no `--out`
  Then   stdout parses as one JSON object carrying `engine_version`, `bus` and `candidates`

CASE-2 — plan writes zero .md files
  Given  an untagged codebase
  When   `plan --out plan.json` runs
  Then   no `.md` file appears anywhere in the requirements directory

CASE-3 — plan skips the same paths scanning skips
  Given  a file listed in `.reqmapignore` and a file inside `node_modules`
  When   `plan` runs
  Then   neither file appears in any candidate's `files`

CASE-4 — per-file facts capture docstrings, signatures, imports and size
  Given  a Python file with a module docstring, one function, and one import
  When   `plan` runs
  Then   that file's candidate carries the docstring, the function signature, the import, and a line count

CASE-5 — an unparseable file still becomes a candidate
  Given  a `.go` file among the scanned files
  When   `plan` runs
  Then   that file appears as a candidate with empty facts, not omitted

CASE-6 — Python signatures come from ast, not text matching
  Given  a Python file defining a class with one public and one `_private` method
  When   `plan` reads its signatures
  Then   the public method appears in the candidate's `signatures` and the private one does not

CASE-7 — an unparseable file never aborts the run
  Given  a codebase containing one syntactically broken Python file among valid ones
  When   `plan` runs
  Then   it completes and emits candidates for the valid files, with empty facts for the broken one


--------------------


---
id: REQ-CANDIDATES-827
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CANDIDATES-009]
---

# Fields a candidate carries

## Description
> A candidate's fields are the raw material a human or an AI author turns into a real
> requirement: what files it groups, what it imports, how central it is, and whether someone
> already tagged it. `is_test`, `existing_req` and `importer_count` exist so the author does
> not have to re-derive them by hand from the files themselves.

Every bullet below is binding.
- Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{},
  signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc,
  split_candidate, is_test}`.
- `is_test` is true when every file of the candidate is test code by convention: a
  `tests/`-style directory segment, a `test_*` basename, or a `*_test`/`*.spec` suffix.
- `depends_on` is derived from imports resolved to other candidates.
- `suggested_layer` is `bus` when `importer_count ≥ BUS_FANIN_THRESHOLD`, else `feature`.
- A file already carrying an `implements:` tag is reported via `existing_req`.
- `plan` groups files by `requirements/_capmap.json` when that file is present, and
  treats it as authoritative.
- Absent `_capmap.json`, `plan` falls back to one candidate per file.

## Cases
CASE-1 — every candidate carries the full documented field set
  Given  any file scanned by `plan`
  When   its candidate is built
  Then   the candidate dict carries all of `suggested_id`, `suggested_layer`, `files`, `docstrings`, `signatures`, `imports`, `depends_on`, `tested_by`, `importer_count`, `existing_req`, `loc`, `split_candidate` and `is_test`

CASE-2 — is_test follows test-file convention, not content
  Given  a file at `tests/test_foo.py` alongside an ordinary module
  When   `plan` runs
  Then   the test file's candidate carries `is_test: true` and the ordinary module's does not

CASE-3 — an import edge becomes a depends_on edge
  Given  file `a.py` importing local module `b.py`
  When   `plan` runs
  Then   `a.py`'s candidate lists `b.py`'s candidate in `depends_on`

CASE-4 — high fan-in earns a bus suggestion
  Given  a module imported by at least `BUS_FANIN_THRESHOLD` other candidates
  When   `plan` runs
  Then   that module's candidate carries `suggested_layer: "bus"`

CASE-5 — an already-tagged file reports its existing requirement
  Given  a file carrying `# implements: ARCH-EXAMPLE-001`
  When   `plan` runs
  Then   that file's candidate carries `existing_req: "ARCH-EXAMPLE-001"`

CASE-6 — _capmap.json groups files into one candidate
  Given  a `requirements/_capmap.json` grouping two files under one id
  When   `plan` runs
  Then   both files appear together as one candidate carrying the declared layer

CASE-7 — no capmap means one candidate per file
  Given  a codebase with no `requirements/_capmap.json`
  When   `plan` runs
  Then   every file becomes its own separate candidate

