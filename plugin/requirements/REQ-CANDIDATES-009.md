---
id: REQ-CANDIDATES-009
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-SCAN-002]
superseded_by:
---

# Capability candidates (extraction plan)

> Stage 1 of AI extraction: emit a deterministic capability plan from legacy code, writing no requirement files.

## Input
- A code root, walked with the same exclusions as scanning (noise dirs, the SSOT
  dir, and `.reqmapignore`), plus the already-discovered members so files that
  already carry an `implements:` tag are flagged rather than re-proposed.
- Optional `requirements/_capmap.json` — a hand-authored capability grouping that
  is authoritative when present.

## Description
`extract` proposes one empty TODO draft per file and cannot recover intent.
`candidates` instead gathers the raw material an authoring step (a human or an LLM
agent) needs to write a real, capability-level requirement: per-file module/symbol
docstrings and top-level signatures (Python via stdlib `ast`, JS/TS via regex), the
import graph resolved into `depends_on` edges, test-file coverage, fan-in (to hint
`bus` vs `feature`), and a grouping of files into capabilities. It is deliberately
READ-ONLY — it emits a JSON plan and writes no `.md`, so it can never repeat the
empty-stub failure mode of `extract`. Grouping uses `_capmap.json` when present and
otherwise falls back to one candidate per file, leaving merge/split judgment to the
Stage-2 authoring agent. Depends on [[CORE-SCAN-002]] for the walk/ignore primitives.

## Output
- A single JSON object on stdout (or `--out PATH`): `{engine_version, bus[],
  candidates[]}`, where each candidate carries `{suggested_id, suggested_layer,
  files[], docstrings{}, signatures[], imports[], depends_on[], tested_by[],
  importer_count, existing_req, loc, split_candidate}`. No requirement `.md` files
  are created.

## Acceptance (= tests)
- Running `candidates` writes zero `.md` files and emits valid JSON.
- A file listed in `.reqmapignore` is absent from every candidate's `files`.
- An import of a local module yields a `depends_on` edge to that module's candidate.
- When `requirements/_capmap.json` groups two files under one id, they appear as a
  single candidate carrying both files with the declared layer.
- A file already carrying an `implements:` tag is reported via `existing_req`.

## Links
- Used by: (auto)
## Members in code (auto)
