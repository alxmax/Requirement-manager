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
- `draft --plan` emits a single JSON object, to stdout or to `--out PATH`, shaped `{engine_version, bus[], candidates[]}`, and writes no `.md` files. [[REQ-CANDIDATES-826]]
- Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{}, signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc, split_candidate, is_test}`. [[REQ-CANDIDATES-827]]
- The plan and the write path read ONE definition of an already-covered file, so a file the write path would skip is never reported as new. [[REQ-PLANTAGGED-1005]]
- The plan states the rung of every candidate it would draft and the upper rungs the same run would mint, so the pyramid is visible before anything is written. [[REQ-PLANLEVEL-1006]]
- Each candidate the write path would draft also states the id that write path will mint for it, without either id being renamed. [[REQ-PLANDRAFTID-1010]]

## Cases
CASE-1
  Given  any corpus
  When   `draft --plan` runs
  Then   it writes zero `.md` files and emits valid JSON

CASE-2
  Given  a file listed in `.reqmapignore` (including one placed in `requirements/`)
  When   `draft --plan` runs
  Then   that file is absent from every candidate's `files`

CASE-3
  Given  an import of a local module
  When   `draft --plan` runs
  Then   a `depends_on` edge points at that module's candidate

CASE-4
  Given  a `requirements/_capmap.json` grouping two files under one id
  When   `draft --plan` runs
  Then   they appear as a single candidate carrying both files with the declared layer

CASE-5
  Given  a file already carrying an `implements:` tag
  When   `draft --plan` runs
  Then   it is reported via `existing_req`

CASE-6
  Given  a module imported by `BUS_FANIN_THRESHOLD` or more candidates
  When   `draft --plan` runs
  Then   it is suggested as `bus`

CASE-7
  Given  a `.go` file and a `tests/test_x.py` file, and no `_capmap.json`
  When   `draft --plan` runs
  Then   both are candidates; the `.go` one carries empty signatures and the test one carries `is_test: true`

## Context
**Terms**
- a candidate    one proposed capability in the plan: a guess that these files
- belong together and deserve one requirement.
- per-file facts what `draft --plan` reads out of a file without interpreting it —
- docstrings, signatures, imports, size.
- the SSOT dir   the `requirements/` directory itself.
- noise dirs     `.git`, `node_modules`, `__pycache__`.

**Notes**
- Read-only by design — merge/split judgment is left to the Stage-2 authoring agent.
- Import→candidate resolution matches on file stem, so a stdlib-shadowing or same-basename
  import can produce a false `depends_on` edge for the author to prune.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a large untagged service and runs the `draft --plan` command. It prints a JSON
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
milestone: v3.2
satisfies: [ARCH-CANDIDATES-009]
---

# The plan's JSON shape and read-only scanning

## Description
> Everything else in the pipeline — `draft`, `review`, `confirm` — writes files. `draft --plan`
> deliberately does not: it is the look-before-you-leap step for an untagged codebase, so a
> wrong or half-formed plan can be thrown away with zero cleanup. It walks the code with the
> same exclusions as scanning, so it never lists a file a real scan would skip.

Every bullet below is binding.
- `draft --plan` emits a single JSON object, to stdout or to `--out PATH`, shaped
  `{engine_version, bus[], candidates[]}`.
- `draft --plan` writes NO `.md` files. It cannot repeat `draft`'s empty-stub failure.
- `draft --plan` walks the code with the same exclusions as scanning: noise dirs, the SSOT dir,
  and `.reqmapignore` resolved in `requirements/` first.
- `draft --plan` gathers per-file facts: module and symbol docstrings, top-level signatures,
  import targets, and line count.
- `draft --plan` lists every scannable code file as a candidate, the same set `draft` walks.
  A file in a language `draft --plan` cannot parse is still a candidate, with empty facts.
- `draft --plan` reads top-level signatures from Python via `ast` — functions, classes and the
  public methods of each class — and from JS/TS via best-effort parsing.
- An unparseable file yields empty facts. It never aborts the plan.

## Cases
CASE-1 — plan emits one JSON object with the documented shape
  Given  a small codebase
  When   `draft --plan` runs with no `--out`
  Then   stdout parses as one JSON object carrying `engine_version`, `bus` and `candidates`

CASE-2 — plan writes zero .md files
  Given  an untagged codebase
  When   `plan --out plan.json` runs
  Then   no `.md` file appears anywhere in the requirements directory

CASE-3 — plan skips the same paths scanning skips
  Given  a file listed in `.reqmapignore` and a file inside `node_modules`
  When   `draft --plan` runs
  Then   neither file appears in any candidate's `files`

CASE-4 — per-file facts capture docstrings, signatures, imports and size
  Given  a Python file with a module docstring, one function, and one import
  When   `draft --plan` runs
  Then   that file's candidate carries the docstring, the function signature, the import, and a line count

CASE-5 — an unparseable file still becomes a candidate
  Given  a `.go` file among the scanned files
  When   `draft --plan` runs
  Then   that file appears as a candidate with empty facts, not omitted

CASE-6 — Python signatures come from ast, not text matching
  Given  a Python file defining a class with one public and one `_private` method
  When   `draft --plan` reads its signatures
  Then   the public method appears in the candidate's `signatures` and the private one does not

CASE-7 — an unparseable file never aborts the run
  Given  a codebase containing one syntactically broken Python file among valid ones
  When   `draft --plan` runs
  Then   it completes and emits candidates for the valid files, with empty facts for the broken one


--------------------


---
id: REQ-CANDIDATES-827
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
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
- `draft --plan` groups files by `requirements/_capmap.json` when that file is present, and
  treats it as authoritative.
- Absent `_capmap.json`, `draft --plan` falls back to one candidate per file.

## Cases
CASE-1 — every candidate carries the full documented field set
  Given  any file scanned by `draft --plan`
  When   its candidate is built
  Then   the candidate dict carries all of `suggested_id`, `suggested_layer`, `files`, `docstrings`, `signatures`, `imports`, `depends_on`, `tested_by`, `importer_count`, `existing_req`, `loc`, `split_candidate` and `is_test`

CASE-2 — is_test follows test-file convention, not content
  Given  a file at `tests/test_foo.py` alongside an ordinary module
  When   `draft --plan` runs
  Then   the test file's candidate carries `is_test: true` and the ordinary module's does not

CASE-3 — an import edge becomes a depends_on edge
  Given  file `a.py` importing local module `b.py`
  When   `draft --plan` runs
  Then   `a.py`'s candidate lists `b.py`'s candidate in `depends_on`

CASE-4 — high fan-in earns a bus suggestion
  Given  a module imported by at least `BUS_FANIN_THRESHOLD` other candidates
  When   `draft --plan` runs
  Then   that module's candidate carries `suggested_layer: "bus"`

CASE-5 — an already-tagged file reports its existing requirement
  Given  a file carrying `# implements: ARCH-EXAMPLE-001`
  When   `draft --plan` runs
  Then   that file's candidate carries `existing_req: "ARCH-EXAMPLE-001"`

CASE-6 — _capmap.json groups files into one candidate
  Given  a `requirements/_capmap.json` grouping two files under one id
  When   `draft --plan` runs
  Then   both files appear together as one candidate carrying the declared layer

CASE-7 — no capmap means one candidate per file
  Given  a codebase with no `requirements/_capmap.json`
  When   `draft --plan` runs
  Then   every file becomes its own separate candidate


--------------------


---
id: REQ-PLANTAGGED-1005
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.10
satisfies: [ARCH-CANDIDATES-009]
---

# One definition of "this file is already accounted for"

## Description
> The plan and the write path each decided for themselves which files already carry a
> requirement, and they disagreed: the plan counted only `implements:`, the write path
> counted every role. A test file linked by `tested-by:` therefore appeared in the plan as
> a NEW draft that `init` would never write. On a 96%-tagged consumer corpus that was 123
> reported candidates of which about 120 were tests — a plan nobody could act on, for a
> command whose whole purpose is to say what the write will do.

Every bullet below is binding.
- `tagged_files` returns `{file: requirement_id}` for every file carrying a membership tag
  of any role, first tag winning per file in scan order.
- `plan` and the write path both derive their notion of an already-covered file from that
  one function, so a file the write path would skip is never reported as a new candidate.
- A file linked only by `tested-by:` counts as covered, and its candidate carries that
  requirement as `existing_req`.

## Cases
CASE-1 — a tested-by link is coverage
  Given  a test file whose only tag is `# tested-by: ARCH-FOO-001`
  When   `init --plan` runs
  Then   its candidate carries `existing_req: "ARCH-FOO-001"` and is not reported as new

CASE-2 — the plan predicts the write
  Given  a repository where every source file already carries some membership tag
  When   `init --plan` runs and then `init` writes
  Then   the plan reports no new candidate and the write path creates no `DRAFT-*` file

CASE-3 — an untagged file is still reported
  Given  a repository holding one tagged file and one file with no tag at all
  When   `init --plan` runs
  Then   only the untagged file is reported as a new candidate, and `init` writes a draft
         for exactly that file

## Context
**Notes**
- The helper returns a mapping rather than a set because the two callers want different
  halves of the same fact: the write path asks "is this file covered", the plan also wants
  the id to report as the idempotency hint. One function answers both.


--------------------


---
id: REQ-PLANLEVEL-1006
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.10
satisfies: [ARCH-CANDIDATES-009]
---

# The plan carries the pyramid it would write

## Description
> `init` writes three rungs (ADR-0030/0036) and the plan named none of them: `plan.json`
> held zero `level` keys. The only way to see what pyramid a run would produce was to let
> it write every file first and read the result — which defeats a dry run. The plan now
> states the rung of each candidate and the upper rungs the same run would mint.

Every bullet below is binding.
- Each candidate the write path would draft carries `level: "code"` and `arch_id`, the
  architecture requirement it would be written under.
- A candidate that is already linked in code carries `level: null` and `arch_id: null` —
  it is not drafted, so no rung is claimed for it.
- The plan carries `pyramid: {architecture: [...], system: <id or null>}`, naming the
  architecture ids one per source directory that would produce drafts, and the system
  placeholder, which is null when no architecture rung would be written.
- The architecture ids in the plan are the ids the write path mints for the same
  directories, minted by the same function.

## Cases
CASE-1 — the plan names the rungs
  Given  two untagged source files in `core/` and `web/`
  When   `init --plan` runs
  Then   `pyramid.architecture` is `["ARCH-CORE-001", "ARCH-WEB-001"]`, `pyramid.system` is
         the placeholder id, and each candidate carries `level: "code"` with its `arch_id`

CASE-2 — the planned pyramid is the written one
  Given  the same repository
  When   `init --plan` runs and then `init` writes
  Then   every id in `pyramid` exists as a requirement at the stated level, and each code
         draft's `satisfies:` is the `arch_id` its candidate named

CASE-3 — nothing to draft means no pyramid
  Given  a repository where every file is already linked in code
  When   `init --plan` runs
  Then   every candidate carries `level: null` and `arch_id: null`, and `pyramid` is
         `{architecture: [], system: null}`

## Context
**Notes**
- The naming helpers (`SYS_PLACEHOLDER_ID`, `_arch_slug`, `_assign_arch_ids`) live in the
  plan module, one layer below the writer, because `draft.py` imports `candidates.py` and
  never the reverse. Naming only: nothing in that block writes a file.
- A candidate group may span directories; its `arch_id` is that of its first file, while
  `pyramid.architecture` covers every directory the run would touch. The set is what the
  write path produces; the per-candidate field is a pointer into it.


--------------------


---
id: REQ-PLANDRAFTID-1010
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.11
satisfies: [ARCH-CANDIDATES-009]
---

# The plan states the id the writer will mint

## Description
> The plan proposed `CORE-ENGINE-001` and the write path minted `DRAFT-CORE-ENGINE`, so a
> reader who ran `init --plan`, then `init`, and diffed the corpus found different ids
> everywhere. The repair is disclosure, not unification: the two ids are different things.
> `suggested_id` is a group-level name an author may adopt — it can span several files
> under a `_capmap.json` grouping — while the writer mints one id per file, and its
> `DRAFT-` prefix is the marker that a requirement is an unreviewed auto-draft, asserted in
> the confirmed contract of [[ARCH-EXTRACT-008]] and keyed on by `init --wipe` and the risk
> report. Renaming either side would break a live marker to fix a reporting gap; stating
> both closes the gap and breaks nothing.

Every bullet below is binding.
- Each candidate the write path would draft carries `draft_id`, the id `init` will mint for
  that candidate's first file.
- A candidate that is already linked in code carries `draft_id: null`, since no draft is
  written for it and no id would be minted.
- Neither `suggested_id` nor the writer's id changes: the `DRAFT-` prefix stays exactly
  what it was.

## Cases
CASE-1 — the plan predicts the written id
  Given  one untagged source file at `core/engine.py`
  When   `init --plan` runs and then `init` writes
  Then   the candidate's `draft_id` is `DRAFT-CORE-ENGINE`, that id exists in the corpus
         afterwards, and its `suggested_id` `CORE-ENGINE-001` does not

CASE-2 — nothing drafted, nothing claimed
  Given  a repository where every source file already carries a membership tag
  When   `init --plan` runs
  Then   every candidate carries `draft_id: null`

CASE-3 — the marker is untouched
  Given  the id-minting function the write path uses
  When   it mints an id for any path
  Then   the result still begins with `DRAFT-`

## Context
**Notes**
- `_draft_id` moved from `draft.py` into `candidates.py` so the plan can call it: the
  dependency runs `draft.py -> candidates.py` and never the reverse, the same reason
  `SYS_PLACEHOLDER_ID` and `_assign_arch_ids` already live there. The function's behaviour
  is unchanged and the flat `reqmap._draft_id` name still resolves.
- `draft_id` is the id before the residual collision suffix the write path appends when two
  different paths slug identically (`DRAFT-X`, `DRAFT-X-2`). That case needs a case or
  extension-only clash and does not arise in a normal tree; the plan states the base id.
- Rejected: making `cmd_candidates` emit `DRAFT-*` as its `suggested_id`. It would make an
  authoring suggestion look like the unreviewed-draft marker, and `_minted_groups` can
  group several files under one id while `_draft_id` is per file — they are different
  granularities, not two spellings of one thing.
