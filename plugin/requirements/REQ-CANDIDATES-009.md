---
id: REQ-CANDIDATES-009
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-SCAN-002]
superseded_by:
milestone: v1.06
---

# Capability candidates (extraction plan)

> When you point this tool at an old codebase that has no requirements written down yet,
> this is the first, look-but-don't-touch step. It reads the code and produces a tidy
> machine-readable plan that guesses what each capability is — which files belong together,
> what they depend on, how central each one is — without writing or changing a single
> requirement file. An author (or an AI assistant) then uses that plan to decide what to
> actually write up. Without it, you would face a wall of untagged code with no starting map.

## WHAT — Contract (normative)
Every line in this section is binding.
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
- `plan` reads top-level signatures from Python via `ast`, and from JS/TS via
  best-effort parsing.
- An unparseable file yields empty facts. It never aborts the plan.

**What a candidate carries**
- Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{},
  signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc,
  split_candidate}`.
- `depends_on` is derived from imports resolved to other candidates.
- `suggested_layer` is `bus` when `importer_count ≥ BUS_FANIN_THRESHOLD`, else `feature`.
- A file already carrying an `implements:` tag is reported via `existing_req`.

**How it groups files**
- `plan` groups files by `requirements/_capmap.json` when that file is present, and
  treats it as authoritative.
- Absent `_capmap.json`, `plan` falls back to one candidate per file.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Read-only by design — merge/split judgment is left to the Stage-2 authoring agent.
- Import→candidate resolution matches on file stem, so a stdlib-shadowing or same-basename
  import can produce a false `depends_on` edge for the author to prune.

## HOW — Acceptance (= tests)
AC-1
  Given  any corpus
  When   `plan` runs
  Then   it writes zero `.md` files and emits valid JSON

AC-2
  Given  a file listed in `.reqmapignore` (including one placed in `requirements/`)
  When   `plan` runs
  Then   that file is absent from every candidate's `files`

AC-3
  Given  an import of a local module
  When   `plan` runs
  Then   a `depends_on` edge points at that module's candidate

AC-4
  Given  a `requirements/_capmap.json` grouping two files under one id
  When   `plan` runs
  Then   they appear as a single candidate carrying both files with the declared layer

AC-5
  Given  a file already carrying an `implements:` tag
  When   `plan` runs
  Then   it is reported via `existing_req`

AC-6
  Given  a module imported by `BUS_FANIN_THRESHOLD` or more candidates
  When   `plan` runs
  Then   it is suggested as `bus`

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
