# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `plugin/` (the engine resolves paths relative to its working directory):

```bash
python scripts/reqmap.py init               # first-use bootstrap: scaffold + draft from code + lock + map + next-steps
python scripts/reqmap.py gate               # gate: link sync + drift + test-link integrity (warn) — run before every commit; report-only, never touches the lock
python scripts/reqmap.py sync               # rescan + advance drift baseline + regen map in one step; use --accept-drift when a confirmed/implemented contract changed
python scripts/reqmap.py map                # generate _map.md (Mermaid) + _map.json (graph) + _map.html (viewer, if template vendored)
python scripts/reqmap.py site --attach docs/architecture.html --regions nav,stats   # inject/refresh engine-owned regions (links + counts) into a presentation page; scaffolds one if absent. init runs this best-effort.
python scripts/reqmap.py export             # emit requirements/_map.json for an external front-end (also: --out -)
python scripts/reqmap.py scan               # list code members per capability
python scripts/reqmap.py new AREA-NAME-NNN  # scaffold a new requirement from the template
python scripts/reqmap.py new --from-todo "TODO name" --id AREA-NAME-NNN [--mark-done]  # scaffold a requirement draft from a TODO.md item; --mark-done flips the item to [x]
python scripts/reqmap.py next               # 'what should I do next': counted, actionable risk buckets
python scripts/reqmap.py lint               # readability/structure check on non-draft requirements (--strict fails on errors)
python scripts/reqmap.py show AREA-NAME-NNN  # consolidated dossier for one requirement (contract, deps, members, risk)
python scripts/reqmap.py dupes              # flag requirement pairs with overlapping contracts (TF-IDF cosine; --threshold)
python scripts/reqmap.py health             # corpus coherence score + component counts (--json for a CI badge)
python scripts/reqmap.py draft              # draft requirements from untagged legacy code (input: existing code)
python scripts/reqmap.py plan               # JSON capability-extraction plan, writes no files (AI-assist; use before draft)
python scripts/reqmap.py findings           # aggregate open verify-intent items
python scripts/reqmap.py confirm AREA-NAME-NNN  # confirm a draft/baseline requirement (requires an implements: member); run sync after
python scripts/reqmap.py review [AREA-NAME-NNN]  # emit a JSON review plan (AI-feed: intent, contract, acceptance, anchors) for all or one requirement
```

Run tests (stdlib unittest, no install needed):

```bash
python scripts/test_reqmap.py
python scripts/reqmap.py map --check   # fails if committed _map.* is stale
```

Version coherence gate (run from repo root, not `plugin/`):

```bash
python scripts/check_versions.py       # asserts plugin.json semver == marketplace.json; validates MAP_ENGINE_VERSION shape
```

The gate must pass (`0 errors`) before committing changes to `reqmap.py` or any requirement file. Pre-commit hook lives at `plugin/hooks/pre-commit`. CI runs all four checks: `check_versions.py` → `reqmap.py gate` → `reqmap.py map --check` → `test_reqmap.py`. (`check` is a deprecated alias for `gate` — removed in the next major.)

## Architecture

This repo is a Claude Code plugin that ships **three skills** under `plugin/skills/`:
- `requirement-manager` — the core skill; seeds `reqmap.py` into a target repo and drives the SSOT/drift workflow. Its `SKILL.md` is the authoritative contract.
- `requirement-quality-review` — on-demand AI *advisory* review of requirement files' semantic quality (is a clause testable, does the WHY explain intent). Never part of the gate (`implements: REQ-REVIEW-022`).
- `excalidraw-diagram` — generates Excalidraw scenes + a self-contained HTML viewer from a system description. Fully independent of `reqmap.py`: its own stdlib-only builder at `skills/excalidraw-diagram/scripts/excalidraw_builder.py` (smoke test + auto-layout/overlap self-checks via `python excalidraw_builder.py`). Example generators live in `skills/excalidraw-diagram/examples/` — `make_full_architecture.py` (the complete-architecture poster), `make_iso5807_flowchart.py` (the reqmap flow in ISO 5807 notation), and `make_excalidraw_skill_flow.py`.

**Generating diagrams *of this repo*:** run a maintained generator from `plugin/skills/excalidraw-diagram/examples/` with `diagrams` as the output arg (e.g. `python plugin/skills/excalidraw-diagram/examples/make_full_architecture.py diagrams`). Outputs land in `diagrams/` (gitignored, regenerable, never committed) — **never** `docs/` (the published Pages site). Do not author ad-hoc generators with an absolute plugin-cache import; reuse the examples (they use a portable relative import).

The repo dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Single engine file:** `plugin/scripts/reqmap.py` — ~3700 lines, stdlib only, no external dependencies. All logic (parse, scan, gate, map, draft, plan, findings, init, next) lives here. This is intentional — hermetic deployment into any repo without install friction.

**Requirement layers:**
- `layer: bus` — foundation capabilities (config, parsing, scanning, drift detection). High fan-in; change behind their contract.
- `layer: feature` — compose the bus via `depends_on`. Currently: new, scan, gate, sync, map, draft, plan, findings, init, next, confirm.
- `layer: need` — an upstream stakeholder need (`NEED-SSOT-001`), satisfied-by feature requirements via `satisfies:`, not implemented by code; exempt from the implements/tested-by gates (see `REQ-TRACE-020`).

**Requirement schema** (`plugin/requirements/*.md`): YAML frontmatter (id, status, layer, owner, depends_on, acceptance criteria) + prose body (WHY / WHAT / WHERE / HOW sections). The frontmatter parser is hand-rolled (scalars + inline lists only — no full YAML library).

**Code tagging:** source files declare membership with inline comments:
```
# implements: CORE-PARSE-001
# tested-by: REQ-CHECK-006
```
`TAG_RE` in the engine enforces a left-boundary guard so `reimplements:` or `x-implements:` are not picked up as real tags. The member list is discovered by scanning — never hand-maintained.

**Gate logic** (`gate`): link sync (every tag points to a real requirement; every `confirmed`/`implemented`/`in-progress` requirement has ≥1 member) and `depends_on` target existence are **error-level** (exit 1). Drift (content hash vs `_reqlock.json`) and **test-link integrity** are **warn-only** (exit 0). `gate` is report-only and never touches `_reqlock.json`; use `sync` (with `--accept-drift` for confirmed/implemented contracts) to advance the baseline. The test-link integrity check: a confirmed requirement's `tested-by` file must exist and contain a test function, else the link asserts coverage it lacks (`_test_link_problem`). It is the deterministic half of behavior-sync. Per-criterion coverage (`REQ-ACVERIFY-019`) is the finer-grained sibling: a `# verifies: <id>#AC-N` tag links one test to one labelled criterion, and the gate warns (warn-only, opt-in) for each labelled `AC-N` left untagged once a requirement carries at least one `verifies` tag.

**Generated outputs** (under `plugin/requirements/`):
- `_map.md` — 4 Mermaid diagrams for static rendering (System Map, Req→Code, Dependencies, Risk) *(committed)*
- `_map.json` — `{engine_version, nodes, edges}` registry graph; consumed by the viewer and any external front-end; also written standalone by `export` *(committed)*
- `_map.html` — a self-contained single-file copy of the React viewer (`app/`) with this repo's `_map.json` inlined; opens by double-click, no server. *Regenerable (template + `_map.json`), gitignored — not committed.*
- `_reqlock.json` — content hash baseline for drift detection *(committed)*
- `_findings.md` — aggregated verify-intent triage *(committed)*

The viewer is the Vite + React app under `app/`. Its single-file build is vendored beside the engine as `plugin/scripts/_map_viewer.html` (carries a `<!--REQMAP_DATA-->` marker); the stdlib engine injects each repo's `_map.json` into that marker to produce `_map.html`. So the engine ships a rich UI without itself depending on Node/npm — and emits only `_map.md` + `_map.json` if the template is absent.

**Rebuilding the vendored viewer** (required after any `app/` change):
```bash
cd app && npm run build:viewer   # rewrites plugin/scripts/_map_viewer.html
```

**Scanning scope:** walks the repo for `.py .js .ts .tsx .jsx .c .cpp .h .go .rs .html .css .sql .yaml .yml .md` (`.md` so prose capabilities — prompts/specs — can carry membership tags). Respects `.reqmapignore` (fnmatch globs). Prunes `.git`, `node_modules`, `__pycache__` automatically. Non-code capability *discovery* (`candidates --md-glob`) is separate and opt-in.

## Plugin packaging

`plugin/.claude-plugin/plugin.json` is the manifest. The plugin is published to a marketplace manifest at `.claude-plugin/marketplace.json` (repo root).

**Two independent version numbers — don't conflate them:**
- **Plugin semver** lives in *three* places kept in lockstep by `check_versions.py`: `version` in `plugin.json`, plus the top-level `version` and `plugins[].version` in `marketplace.json`. **Any** shipped change — engine *or* a skill edit — must bump this semver, or installed copies won't pick it up via `/plugin update` (a skill edit with no bump is silently invisible to consumers).
- **`MAP_ENGINE_VERSION`** inside `reqmap.py` (ISO date `YYYY-MM-DD`, optional `.N` same-day suffix, e.g. `2026-06-03.2`) is engine-only — it lets a seeded copy of `reqmap.py` detect it is behind. Bump it only on engine changes.

The skill contract (authoritative on authoring rules, statuses, and the gate) is `plugin/skills/requirement-manager/SKILL.md`.

**GitHub Action (`check/action.yml`):** published as `alxmax/requirement-manager/check@v1`. The `@v1` git tag is independent of the plugin semver and of `MAP_ENGINE_VERSION` — bump it manually when the action interface changes. Consumer repos use it as:
```yaml
- uses: alxmax/requirement-manager/check@v1
```
