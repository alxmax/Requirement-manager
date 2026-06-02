# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `plugin/` (the engine resolves paths relative to its working directory):

```bash
python scripts/reqmap.py check              # gate: link sync + drift — run before every commit
python scripts/reqmap.py map                # generate requirements/_map.html + _map.md
python scripts/reqmap.py scan               # list code members per capability
python scripts/reqmap.py new AREA-NAME-NNN  # scaffold a new requirement from the template
python scripts/reqmap.py extract            # draft requirements from untagged legacy code
python scripts/reqmap.py candidates         # JSON capability-extraction plan (AI-assist)
python scripts/reqmap.py findings           # aggregate open verify-intent items
```

Run tests (stdlib unittest, no install needed):

```bash
python scripts/test_reqmap.py
```

The gate must pass (`0 errors`) before committing changes to `reqmap.py` or any requirement file. Pre-commit hook lives at `plugin/hooks/pre-commit`.

## Architecture

This repo is a Claude Code plugin. The plugin exposes one skill (`requirement-manager`) that seeds `reqmap.py` into target repos. The repo dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Single engine file:** `plugin/scripts/reqmap.py` — ~1000 lines, stdlib only, no external dependencies. All logic (parse, scan, check, map, extract, candidates, findings) lives here. This is intentional — hermetic deployment into any repo without install friction.

**Two-layer requirement model:**
- `layer: bus` — foundation capabilities (config, parsing, scanning, drift detection). High fan-in; change behind their contract.
- `layer: feature` — compose the bus via `depends_on`. Currently: new, scan, check, map, extract, candidates, findings.

**Requirement schema** (`plugin/requirements/*.md`): YAML frontmatter (id, status, layer, owner, depends_on, acceptance criteria) + prose body (WHY / WHAT / WHERE / HOW sections). The frontmatter parser is hand-rolled (scalars + inline lists only — no full YAML library).

**Code tagging:** source files declare membership with inline comments:
```
# implements: CORE-PARSE-001
# tested-by: REQ-CHECK-006
```
`TAG_RE` in the engine enforces a left-boundary guard so `reimplements:` or `x-implements:` are not picked up as real tags. The member list is discovered by scanning — never hand-maintained.

**Gate logic** (`check`): three checks — link sync (every tag points to a real requirement; every `confirmed`/`implemented`/`in-progress` requirement has ≥1 member), drift (content hash vs `_reqlock.json`), and `depends_on` target existence.

**Generated outputs** (all under `plugin/requirements/`, committed):
- `_map.html` — interactive 4-tab viewer (System Map, Req→Code, Dependencies, Risk)
- `_map.md` — 4 Mermaid diagrams for static rendering
- `_reqlock.json` — content hash baseline for drift detection
- `_findings.md` — aggregated verify-intent triage

**Scanning scope:** walks the repo for `.py .js .ts .tsx .jsx .c .cpp .h .go .rs .html .css .sql .yaml .yml`. Respects `.reqmapignore` (fnmatch globs). Prunes `.git`, `node_modules`, `__pycache__` automatically.

## Plugin packaging

`plugin/.claude-plugin/plugin.json` is the manifest. The plugin is published to a marketplace manifest at `.claude-plugin/marketplace.json` (repo root). Version is tracked in `plugin.json` and as `MAP_ENGINE_VERSION` (ISO date string) inside `reqmap.py` — bump both on engine changes so seeded repos can detect they are behind.

The skill contract (authoritative on authoring rules, statuses, and the gate) is `plugin/skills/requirement-manager/SKILL.md`.
