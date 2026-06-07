# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `plugin/` (the engine resolves paths relative to its working directory):

```bash
python scripts/reqmap.py init               # first-use bootstrap: scaffold + draft from code + lock + map + next-steps
python scripts/reqmap.py check              # gate: link sync + drift + test-link integrity (warn) — run before every commit
python scripts/reqmap.py map                # generate _map.md (Mermaid) + _map.json (graph) + _map.html (viewer, if template vendored)
python scripts/reqmap.py export             # emit requirements/_map.json for an external front-end (also: --out -)
python scripts/reqmap.py scan               # list code members per capability
python scripts/reqmap.py new AREA-NAME-NNN  # scaffold a new requirement from the template
python scripts/reqmap.py next               # 'what should I do next': counted, actionable risk buckets
python scripts/reqmap.py lint               # readability/structure check on non-draft requirements (--strict fails on errors)
python scripts/reqmap.py show AREA-NAME-NNN  # consolidated dossier for one requirement (contract, deps, members, risk)
python scripts/reqmap.py similar            # flag requirement pairs with overlapping contracts (TF-IDF cosine; --threshold)
python scripts/reqmap.py health             # corpus coherence score + component counts (--json for a CI badge)
python scripts/reqmap.py extract            # draft requirements from untagged legacy code
python scripts/reqmap.py candidates         # JSON capability-extraction plan (AI-assist)
python scripts/reqmap.py findings           # aggregate open verify-intent items
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

The gate must pass (`0 errors`) before committing changes to `reqmap.py` or any requirement file. Pre-commit hook lives at `plugin/hooks/pre-commit`. CI runs all four checks: `check_versions.py` → `reqmap.py check` → `reqmap.py map --check` → `test_reqmap.py`.

## Architecture

This repo is a Claude Code plugin. The plugin exposes one skill (`requirement-manager`) that seeds `reqmap.py` into target repos. The repo dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Single engine file:** `plugin/scripts/reqmap.py` — ~1000 lines, stdlib only, no external dependencies. All logic (parse, scan, check, map, extract, candidates, findings, init, next) lives here. This is intentional — hermetic deployment into any repo without install friction.

**Two-layer requirement model:**
- `layer: bus` — foundation capabilities (config, parsing, scanning, drift detection). High fan-in; change behind their contract.
- `layer: feature` — compose the bus via `depends_on`. Currently: new, scan, check, map, extract, candidates, findings, init, next.

**Requirement schema** (`plugin/requirements/*.md`): YAML frontmatter (id, status, layer, owner, depends_on, acceptance criteria) + prose body (WHY / WHAT / WHERE / HOW sections). The frontmatter parser is hand-rolled (scalars + inline lists only — no full YAML library).

**Code tagging:** source files declare membership with inline comments:
```
# implements: CORE-PARSE-001
# tested-by: REQ-CHECK-006
```
`TAG_RE` in the engine enforces a left-boundary guard so `reimplements:` or `x-implements:` are not picked up as real tags. The member list is discovered by scanning — never hand-maintained.

**Gate logic** (`check`): link sync (every tag points to a real requirement; every `confirmed`/`implemented`/`in-progress` requirement has ≥1 member), drift (content hash vs `_reqlock.json`), and `depends_on` target existence — all error-level. Plus a warn-only **test-link integrity** check: a confirmed requirement's `tested-by` file must exist and contain a test function, else the link asserts coverage it lacks (`_test_link_problem`). It is the deterministic half of behavior-sync; per-criterion AC mapping is deferred (needs a per-AC tag).

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

`plugin/.claude-plugin/plugin.json` is the manifest. The plugin is published to a marketplace manifest at `.claude-plugin/marketplace.json` (repo root). Version is tracked in `plugin.json` and as `MAP_ENGINE_VERSION` (ISO date `YYYY-MM-DD`, with an optional `.N` same-day revision suffix, e.g. `2026-06-03.2`) inside `reqmap.py` — bump both on engine changes so seeded repos can detect they are behind.

The skill contract (authoritative on authoring rules, statuses, and the gate) is `plugin/skills/requirement-manager/SKILL.md`.

**GitHub Action (`check/action.yml`):** published as `alxmax/requirement-manager/check@v1`. The `@v1` git tag is independent of the plugin semver and of `MAP_ENGINE_VERSION` — bump it manually when the action interface changes. Consumer repos use it as:
```yaml
- uses: alxmax/requirement-manager/check@v1
```
