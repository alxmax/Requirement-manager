---
id: REQ-CANDIDATES-009
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-SCAN-002]
superseded_by:
---

# Capability candidates (extraction plan)

> Stage 1 of AI extraction: emit a deterministic capability plan from legacy code, writing no requirement files.

## WHAT — Contract (normative)
- It shall emit a single JSON object (stdout or `--out PATH`) `{engine_version, bus[],
  candidates[]}` and write NO `.md` files — it cannot repeat `extract`'s empty-stub failure.
- It shall walk the code with the same exclusions as scanning (noise dirs, the SSOT dir,
  and `.reqmapignore` resolved in `requirements/` first), gathering per-file facts: module
  and symbol docstrings, top-level signatures (Python via `ast`, JS/TS via best-effort
  parsing), import targets, and line count.
- Each candidate shall carry `{suggested_id, suggested_layer, files[], docstrings{},
  signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc,
  split_candidate}`. `depends_on` shall be derived from imports resolved to other candidates;
  `suggested_layer` shall be `bus` when `importer_count ≥ BUS_FANIN_THRESHOLD`, else `feature`.
- Grouping shall use `requirements/_capmap.json` when present (authoritative) and otherwise
  fall back to one candidate per file. A file already carrying an `implements:` tag shall be
  reported via `existing_req`. An unparseable file shall yield empty facts, not abort the plan.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Read-only by design — merge/split judgment is left to the Stage-2 authoring agent.
- Import→candidate resolution matches on file stem, so a stdlib-shadowing or same-basename
  import can produce a false `depends_on` edge for the author to prune.

## HOW — Acceptance (= tests)
- Running `candidates` writes zero `.md` files and emits valid JSON.
- A file listed in `.reqmapignore` (including one placed in `requirements/`) is absent from every candidate's `files`.
- An import of a local module yields a `depends_on` edge to that module's candidate.
- When `requirements/_capmap.json` groups two files under one id, they appear as a single candidate carrying both files with the declared layer.
- A file already carrying an `implements:` tag is reported via `existing_req`.
- A module imported by `BUS_FANIN_THRESHOLD` or more candidates is suggested as `bus`.

## WHERE — Current implementation
- `cmd_candidates` and the `_py_facts`/`_js_facts`/`_file_facts`/`_load_capmap`/`_collect_files` helpers in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
