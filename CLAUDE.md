# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `plugin/` (the engine resolves paths relative to its working directory):

```bash
python scripts/reqmap.py init               # first-use bootstrap: scaffold + draft from code + lock + map + next-steps
python scripts/reqmap.py gate --code ..     # gate: link sync + drift + test-link integrity (warn) — run before every commit; report-only, never touches the lock
python scripts/reqmap.py sync --code ..     # rescan + advance drift baseline + regen map in one step; use --accept-drift when a confirmed/implemented contract changed
python scripts/reqmap.py map --code ..      # generate _map.md (Mermaid) + _map.json (graph) + _map.html (viewer, if template vendored)
python scripts/reqmap.py site --attach docs/architecture.html --regions nav,stats   # inject/refresh engine-owned regions (links + counts) into a presentation page; scaffolds one if absent. init runs this best-effort.
python scripts/reqmap.py export             # emit requirements/_map.json for an external front-end (also: --out -)
python scripts/reqmap.py scan               # list code members per capability
python scripts/reqmap.py new AREA-NAME-NNN  # scaffold a new requirement from the template
python scripts/reqmap.py new --from-todo "TODO name" --id AREA-NAME-NNN [--mark-done]  # scaffold a requirement draft from a TODO.md item; --mark-done flips the item to [x]
python scripts/reqmap.py next               # 'what should I do next': counted, actionable risk buckets
python scripts/reqmap.py lint --code ..     # readability/structure check on non-draft requirements (--strict fails on errors)
python scripts/reqmap.py show AREA-NAME-NNN  # consolidated dossier for one requirement (contract, deps, members, risk)
python scripts/reqmap.py dupes              # flag requirement pairs with overlapping contracts (TF-IDF cosine; --threshold)
python scripts/reqmap.py search "query"     # rank requirements by lexical relevance (same TF-IDF cosine as dupes; --top)
python scripts/reqmap.py coverage           # list source files carrying no implements: tag, grouped by directory (--json)
python scripts/reqmap.py health             # corpus coherence score + component counts (--json for a CI badge)
python scripts/reqmap.py draft              # draft requirements from untagged legacy code (input: existing code)
python scripts/reqmap.py plan               # JSON capability-extraction plan, writes no files (AI-assist; use before draft)
python scripts/reqmap.py findings           # aggregate open verify-intent items
python scripts/reqmap.py confirm AREA-NAME-NNN  # confirm a draft/baseline requirement (requires an implements: member); run sync after
python scripts/reqmap.py review [AREA-NAME-NNN]  # emit a JSON review plan (AI-feed: intent, contract, acceptance, anchors) for all or one requirement
python scripts/reqmap.py gen-integration    # regenerate tool_definition.json + the SKILL.universal.md command table from the COMMANDS registry
```

**`gate`/`sync`/`lint`/`map` above already carry `--code ..`** so the scan reaches the repo root
(`docs/`, `.github/`, `.githooks/`, root-level `scripts/`), per a NEW repo-root `.reqmapignore`
(kept separate from `plugin/.reqmapignore` — see that file's own comment for why). This is not
optional for these four: the *committed* `_reqlock.json`/`_map.json`/`_map.md`/`docs/map.html`
are generated from the widened scan (member `loc` paths are `code_root`-relative, so a copy
generated without `--code ..` reports every existing member's path one level off and fails
freshness checks against the real committed files). `.githooks/pre-commit` already runs from
the repo root, so it passes `--code .` instead of `--code ..` — same target, different starting
cwd. Read-only exploration commands with no committed-artifact freshness concern (`scan`, `show`,
`search`, `next`, `health`, `coverage`, `dupes`, `findings`, `review`) are unaffected either way
and can be run with or without `--code ..` depending on what you want to inspect.

**A `confirmed` requirement whose members all live outside `plugin/`** (e.g. `REQ-SELFGATE-039`,
whose 5 members are `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/pre-commit`,
`.githooks/pre-push`, `sync_reqmap.sh`) can now only pass `gate`'s implements-tag check under the
widened scan. Running the bare `gate` (no `--code ..`) genuinely ERRORs on such a requirement —
not a silent miss, a real exit-1 failure — because the narrow scope never reaches any file that
proves the tag exists. This is an accepted, permanent consequence of the widened-scan design, not
a bug: CI and the pre-commit hook always run widened, so it never fires there; a human running the
bare command locally sees a loud, immediately-diagnosable error rather than a silent divergence.

Run tests (stdlib unittest, no install needed). On Windows always pass `-X utf8` — the suites print non-ASCII and fail on cp1252:

```bash
python scripts/test_reqmap.py                                      # from plugin/scripts/ or plugin/
python -X utf8 -m unittest test_reqmap.Gate.test_name -v           # single test/class (run from plugin/scripts/)
python scripts/reqmap.py map --check --code ..                     # fails if committed _map.* (or docs/map.html) is stale
```

From the **repo root** (not `plugin/`) — the packaging/release side:

```bash
python scripts/check_versions.py        # plugin.json semver == marketplace.json (x2); validates MAP_ENGINE_VERSION shape. --fix syncs.
python -X utf8 scripts/test_check_versions.py
python -X utf8 scripts/test_changelog_notes.py    # release-notes extraction (CI runs it with cwd=scripts/)
python -X utf8 scripts/test_cross_tool.py         # seeds the engine into a tempdir, runs sync→gate→map: the AI-agnostic falsification test
python -X utf8 plugin/skills/excalidraw-diagram/scripts/excalidraw_builder.py   # builder smoke + layout/overlap self-checks
python -X utf8 -m unittest test_excalidraw -v     # from plugin/skills/excalidraw-diagram/scripts/
```

The gate must pass (`0 errors`) before committing changes to `reqmap.py` or any requirement file. CI (`.github/workflows/ci.yml`, job `gate-and-tests`) runs, in order: `check_versions.py` → `test_check_versions.py` → `test_changelog_notes.py` → the CHANGELOG-entry check → `reqmap.py gate --code ..` → `reqmap.py lint --strict --code ..` → `reqmap.py map --check --code ..` → `test_reqmap.py` → excalidraw builder + tests. (`check` is a deprecated alias for `gate` — removed in the next major.)

**Hooks — two different files, don't confuse them:**
- `.githooks/pre-commit` is *this repo's dev* hook, mirroring the CI order (`check_versions.py` → `gate` → `lint --strict` → `map --check`). Enable once: `git config core.hooksPath .githooks`. `.githooks/pre-push` also blocks direct pushes to `main`.
- `plugin/hooks/pre-commit` is the hook **shipped to consumer repos** — editing it changes consumer behaviour and needs a semver bump.

`sync_reqmap.sh` propagates `plugin/scripts/reqmap.py` (+ the vendored viewer template) into the local plugin cache and any consumer repos passed as args; it only refreshes an *existing* vendored engine, never seeds one.

## Architecture

This repo is a Claude Code plugin that ships **three skills** under `plugin/skills/`:
- `requirement-manager` — the core skill; seeds `reqmap.py` into a target repo and drives the SSOT/drift workflow. Its `SKILL.md` is the authoritative contract.
- `requirement-quality-review` — on-demand AI *advisory* review of requirement files' semantic quality (is a clause testable, does the WHY explain intent). Never part of the gate (`implements: REQ-REVIEW-022`).
- `excalidraw-diagram` — generates Excalidraw scenes + a self-contained HTML viewer from a system description. Fully independent of `reqmap.py`: its own stdlib-only builder at `skills/excalidraw-diagram/scripts/excalidraw_builder.py` (smoke test + auto-layout/overlap self-checks via `python excalidraw_builder.py`). Example generators live in `skills/excalidraw-diagram/examples/` — `make_full_architecture.py` (the complete-architecture poster), `make_iso5807_flowchart.py` (the reqmap flow in ISO 5807 notation), and `make_excalidraw_skill_flow.py`.

**Generating diagrams *of this repo*:** run a maintained generator from `plugin/skills/excalidraw-diagram/examples/` with `diagrams` as the output arg (e.g. `python plugin/skills/excalidraw-diagram/examples/make_full_architecture.py diagrams`). Outputs land in `diagrams/` (gitignored, regenerable, never committed) — **never** `docs/`, which is the published Pages root and holds only reviewed, self-contained HTML (`.gitignore` hard-blocks `docs/*.excalidraw`). Do not author ad-hoc generators with an absolute plugin-cache import; reuse the examples (they use a portable relative import).

The repo dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Single engine file:** `plugin/scripts/reqmap.py` — ~5000 lines, stdlib only, no external dependencies. All logic (parse, scan, gate, map, draft, plan, findings, init, next) lives here. This is intentional — hermetic deployment into any repo without install friction.

**Command registry is the CLI's SSOT** (`COMMANDS` dict near the top of `reqmap.py`, `REQ-CMDREGISTRY-033`): one entry per command (summary, positional arg, flags). `plugin/tool_definition.json` (OpenAI function-calling schema, for non-Claude assistants) and the command-table region in `skills/requirement-manager/SKILL.universal.md` are **generated** from it by `gen-integration` — never hand-edit those two. `gate` warns when they are stale relative to the registry.

**Requirement layers:**
- `layer: bus` — foundation capabilities (config, parsing, scanning, drift detection). High fan-in; change behind their contract.
- `layer: feature` — compose the bus via `depends_on`. One per user-facing command (new, scan, gate, sync, map, draft, plan, findings, init, next, confirm, lint, show, dupes, search, health, coverage, site, review, …); `ls plugin/requirements/` is the live list.
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
- `_reqlock.json` — content hash baseline for drift detection (one hash per requirement = the contract; prose-ahead-of-code direction) *(committed)*
- `_memberlock.json` — versioned sidecar (`{_schema, members}`) of dedicated-member content hashes for reverse-direction (member-ahead-of-spec) drift; kept separate so `_reqlock.json` stays a byte-stable cross-repo contract an older seeded engine reads unchanged (`REQ-MEMBERDRIFT-027`) *(committed)*
- `_findings.md` — aggregated verify-intent triage *(committed)*

**`map` writes outside `plugin/` too.** `_docs_publish_path` (`REQ-PAGES-021`) resolves the **git root**, so a `map` run from `plugin/` also rewrites repo-root `docs/map.html` whenever `docs/` carries a Pages signal (`.nojekyll` or `index.html`) — and `map --check` fails if that published copy drifted. `docs/` is the GitHub Pages root (committed: `map.html`, `architecture.html`, `full_architecture.html`, `index.html`, `.nojekyll`); the `deploy-map` CI job publishes it via OIDC on pushes to `main` and refuses to publish a `map.html` under 10 KB.

The viewer is the Vite + React app under `app/`. Its single-file build is vendored beside the engine as `plugin/scripts/_map_viewer.html` (carries a `<!--REQMAP_DATA-->` marker); the stdlib engine injects each repo's `_map.json` into that marker to produce `_map.html`. So the engine ships a rich UI without itself depending on Node/npm — and emits only `_map.md` + `_map.json` if the template is absent.

See `app/CLAUDE.md` for rebuilding the vendored viewer after `app/` changes.

**Scanning scope:** walks the repo for `.py .js .ts .tsx .jsx .c .cpp .h .go .rs .html .css .sql .yaml .yml .md` (`.md` so prose capabilities — prompts/specs — can carry membership tags). Respects `.reqmapignore` (fnmatch globs). Prunes `.git`, `node_modules`, `__pycache__` automatically. Non-code capability *discovery* (`plan --md-glob`, internally `cmd_candidates`) is separate and opt-in.

## Plugin packaging

`plugin/.claude-plugin/plugin.json` is the manifest. The plugin is published to a marketplace manifest at `.claude-plugin/marketplace.json` (repo root).

**Two independent version numbers — don't conflate them:**
- **Plugin semver** lives in *three* places kept in lockstep by `check_versions.py`: `version` in `plugin.json`, plus the top-level `version` and `plugins[].version` in `marketplace.json`. **Any** shipped change — engine *or* a skill edit — must bump this semver, or installed copies won't pick it up via `/plugin update` (a skill edit with no bump is silently invisible to consumers).
- **`MAP_ENGINE_VERSION`** inside `reqmap.py` (ISO date `YYYY-MM-DD`, optional `.N` same-day suffix, e.g. `2026-06-03.2`) is engine-only — it lets a seeded copy of `reqmap.py` detect it is behind. Bump it only on engine changes.

**A semver bump must ship with a CHANGELOG entry.** CI fails the build when `plugin/.claude-plugin/plugin.json`'s version changed in the commit but `CHANGELOG.md` has no heading containing `` `vX.Y.Z` `` (the backticked form is what the grep matches). On pushes to `main` the `release` job then cuts tag `vX.Y.Z` from `plugin.json` — idempotent, so a non-bumping push creates nothing — with notes extracted from that same CHANGELOG section by `scripts/changelog_notes.py`. Tags therefore follow `plugin.json`, never the other way round.

The skill contract (authoritative on authoring rules, statuses, and the gate) is `plugin/skills/requirement-manager/SKILL.md`.

**GitHub Action (`check/action.yml`):** published as `alxmax/requirement-manager/check@v2`. The `@vN` alias is a third version axis, independent of the plugin semver and of `MAP_ENGINE_VERSION`. It is **not** hand-pushed any more: the `release` job force-moves it onto every commit it tags, and `check_versions.py` asserts the major named in `check/action.yml`, `README.md` and this file agree (the documented `uses:` line is the source of truth — there is no separate version file). Bump the major by editing those three references in one commit, and only for a change that breaks an existing caller — adding a default-on step counts, which is why `@v1` (gate-only, frozen at v2.1.0 content) was left in place rather than re-pointed. Consumer repos use it as:
```yaml
- uses: alxmax/requirement-manager/check@v2
```
