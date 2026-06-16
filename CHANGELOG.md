# Changelog

## Unreleased

**License correction.** `plugin/.claude-plugin/plugin.json` declared `"MIT"` while
the `LICENSE` file and README are Business Source License 1.1 — corrected to the
SPDX id `"BUSL-1.1"`.

**excalidraw-diagram — C4 removed + docs overhaul.**
- **Removed the C4 helpers** (`Scene.c4()` and `Scene.person()`). They were
  undocumented and pulled the skill toward formal C4 notation; the canonical
  poster (`examples/make_full_architecture.py`) now uses plain role-coloured
  `box()`es. ISO 5807 flowchart shapes are unaffected.
- **SKILL.md restructured for its purpose** — a "The goal" statement up front, a
  "Diagramming a repo's architecture" recipe pointing at
  `make_full_architecture.py`, a "Worked examples — ❌ → ✅ variants" section
  (repo poster, pipeline, parallel agents, decision flow, feedback loop), and the
  box-sizing guidance softened to lean on the `overflow_check` gate.
- **Doc↔code drift closed.** The cheat-sheet and `references/excalidraw_format.md`
  now document the previously-undocumented public API the examples rely on
  (`section()`, `pipeline()`, the ISO shapes, `path()`, `glossary()`), the full
  `Scene()` signature, all four `save()` gates (`crossing_check`, `legend_check`,
  `overflow_check`, `text_overlap_check`), and `check_text_overflow()` /
  `check_text_overlaps()`.

> Note: CHANGELOG entries for plugin `v2.2.0` and `v2.3.0` are missing (the
> manifests are at `2.3.0`); backfill or supersede on the next tagged release.

## plugin `v2.1.1` — 2026-06-15

**Audit follow-up (Consilium Trias).** Fixes from a multi-lens audit of the v2.1.0 excalidraw CLI branch:

- **Stale doc references removed.** `README.md` no longer points to the deleted `docs/plugin_architecture.html`; the `SITE_TEMPLATE` comment in `reqmap.py` no longer cites the removed `docs/reqmap_site_prototype.html` (the template is now the canonical source).
- **`render` hardening.** `render_html()` now rejects a scene whose `elements` is a list of non-objects (e.g. `[1, 2, 3]`) instead of writing a viewer that silently fails to render.
- **excalidraw-diagram menu.** The "how to start a diagram" menu gains the missing day-2 path (**re-run / extend your generator**) and a **self-test** entry, each with a when-to-pick-it clause.
- **Tests.** Wrapped three unclosed file handles in the CLI test helpers (no more `ResourceWarning`); added coverage for the `discover` `max_components` truncation path and the non-object-`elements` rejection.

reqmap engine behaviour unchanged (comment-only edit); `MAP_ENGINE_VERSION` stays `2026-06-15`. SRI hashing of the viewer's CDN tags was identified in the audit but deferred — it needs verified per-asset `sha384` hashes (a wrong hash breaks every generated viewer).

---

## plugin `v2.1.0` — 2026-06-15

**excalidraw-diagram CLI.** Two helper verbs on `excalidraw_builder.py` — the authoring path stays Python (no declarative `build <spec>` verb, which would fork a second, divergent format):

- **`render <scene.excalidraw> [out_dir]`** — rebuild the self-contained `.html` viewer from an existing scene file (e.g. one edited on excalidraw.com, where there is no generator script to re-run).
- **`discover <repo> [out.py]`** — scan a repo and emit a runnable Python generator stub (`make_diagram.py`): one box per top-level component on a no-overlap grid, with `TODO`s for the arrows/grouping you fill in, then run it to produce the scene + viewer.
- No-arg `python excalidraw_builder.py` still runs the builder self-test (unchanged — CI relies on it).

reqmap engine unchanged; `MAP_ENGINE_VERSION` stays `2026-06-15`.

---

## plugin `v2.0.0` — 2026-06-15

**Breaking — intent-verb CLI.** Commands renamed to match what the user wants:

| Old | New |
|---|---|
| `check` | `gate` (report-only) — **kept as a deprecation alias**, removed next major |
| `scan` + `check --update-lock` + `map` | `sync` (composite; `--accept-drift` to advance an edited confirmed baseline) |
| `extract` | `draft` |
| `promote` | `confirm` |
| `candidates` | `plan` |
| `similar` | `dupes` |
| `promote-todo "x" --id ID` | `new --from-todo "x" --id ID` |

- **No consumer breakage:** `check` still runs (prints a deprecation notice, forwards to the legacy path), so vendored pre-commit hooks, CI, and the `check@v1` Action keep working. Migrate at leisure: `check`→`gate`, the trio→`sync`.
- **`sync` drift guard:** `sync` refuses to silently re-baseline an edited `confirmed`/`implemented` contract — it prints the changed hashes and exits non-zero unless you pass `--accept-drift`.
- **`gate` is report-only:** it never touches `_reqlock.json`; use `sync` to advance the baseline.
- Requirement IDs are unchanged (`REQ-PROMOTE-011`, `REQ-SIMILAR-016` keep their slugs — only the CLI verb + prose changed).

### Migration
`extract`/`promote`/`candidates`/`similar`/`promote-todo` are removed (no alias) — they do not appear in consumer CI. Update your own scripts: `sed -i 's/reqmap.py check/reqmap.py gate/' <hook>`. `MAP_ENGINE_VERSION` is `2026-06-15`.

---

## plugin `v1.35.0` — 2026-06-14

The `site` command — keep a project presentation page in sync with the registry. Highlights:

- **`site` command** — `reqmap.py site --attach <page.html> [--regions nav,stats]` injects engine-owned, marker-delimited regions into a presentation page and **preserves the authored prose between them**. `nav` = Live Map / Diagram / GitHub links (from `git remote` + artifact paths, each emitted only when its target resolves); `stats` = requirement / confirmed / layer / edge counts + engine version (from `_map.json`). When the `--attach` target does not exist, `site` scaffolds a full self-contained default page with a placeholder hero (`<!-- author me -->`).
- **Two layers** — the engine is deterministic and headless-safe (never prompts); the `requirement-manager` skill is the interactive front door (`site --detect` → ask which target + regions → call the engine). The engine only *links* an Excalidraw diagram — it never generates one (the `excalidraw-diagram` skill stays independent of `reqmap.py`).
- **`init` integration** — `init` runs a best-effort `site` pass (`nav,stats` into `docs/architecture.html`, scaffolding it plus a GitHub Pages signal — `.nojekyll` + an `index.html` redirect — when absent). Opt out with `reqmap.py init --no-site`; a failure in the step never aborts `init`.
- **`map --check` gate** — flags the page stale when its `stats` region drifts from a fresh render; the `nav` region is exempt (it embeds the fork-specific repo URL, like the `repo` field excluded from `_map.json`). A page with no `stats` marker — or one never generated — is not stale. Reuses the `REQ-PAGES-021` Pages-publish path.
- **New requirement `REQ-SITE-026`** + 14 new `Site` tests (idempotency, prose preservation, no-remote degradation, scaffold mode, region-only staleness, HTML-escaping, CLI dispatch, excalidraw independence).

### Upgrade notes
Re-seed consumer repos with `scripts/reqmap.py` only — the scaffold page is an inline template, so no new vendored file is required. `MAP_ENGINE_VERSION` is `2026-06-14`.

---

## plugin `v1.11.0` — 2026-06-04

First feature release since `v1.0.0`. Highlights:

- **Self-contained HTML viewer** — `map` now emits `requirements/_map.html`: a single-file React app with your real requirements inlined, double-click to open, no server or npm needed. Tabs: System Map, Risk, Dependencies, Spec. Main-bus layout ranks nodes by dependency depth (`bus` nodes on the right, consumers on the left); color-coded, selectable edges; grab-to-pan. Fixed: viewer used to render only its bundled demo fixture — all graph tabs now compute layout from the live registry.
- **`init` command** — one-shot bootstrap: scaffolds `requirements/` + `.reqmapignore`, drafts requirements from existing code, builds the lock + map, prints guided next steps. Idempotent; `--wipe` for a hard reset (strips all tags + deletes non-generated files before re-extracting).
- **`next` command** — terminal "what should I do next": a progress header then the Risk tab's actionable buckets most-urgent-first (Orphans · Needs tests · Needs intent review · Drafts to review). Read-only, always exit 0.
- **`promote` command** — human validation step: flips a reviewed requirement's `status` to `confirmed`. Refuses if it has no `implements:` member; warns if no `tested-by:` is linked.
- **`findings` command** — aggregates open `## WHAT — Verify intent` items across all requirements into `requirements/_findings.md`; accepts an AI-triage sidecar (`_findings_triage.json`) for a classified view.
- **`export` command** — emits `requirements/_map.json` (or `--out PATH` / `--out -`) for feeding an external front-end.
- **Intent triage skill action** — 5th menu item in the `requirement-manager` skill for AI-assisted triage of open verify-intent findings.
- **Prose capability discovery** — `extract`/`init` scan `.md`/`.html` by default and classify each prose file into three buckets: ignore (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), or capability-source (prompts/specs auto-drafted as `draft` stubs).
- **`candidates --md-glob`** — read-only extraction plan from prose/spec markdown (advisory, writes no `.md`).
- **Risk signals** — `untested` (has `implements` but no `tested-by:`) and `unverified-intent` (open verify-intent item) surfaced on the Risk tab, `_map.md` table, and detail panel. Silence per-requirement with `test_exempt: <reason>` in frontmatter.
- **`map --check`** freshness gate — exits non-zero if committed `_map.*` is stale; wire alongside `check` in pre-commit/CI.
- **`check --update-lock` auto-runs `map`** — lock and map stay in sync in one command.

### Upgrade notes
Re-seed consumer repos with both `scripts/reqmap.py` **and** `scripts/_map_viewer.html` — the viewer template is new and required for `_map.html` emission. Use `sync_reqmap.sh` or the skill's "update engine" action.

---

## engine `1.11.0` — 2026-06-04

- **Fixed — viewer rendered only its demo fixture**: the `_map.html` graph tabs
  positioned nodes through hardcoded coordinate maps keyed to the bundled sample ids,
  so any real repo's requirements were filtered out and the canvas was blank (registry
  counts were correct, masking it). The System Map, Risk and Dependencies tabs now
  **compute their layout from the live registry** — they render any repo's data.
- **Added — layered "main-bus" layout** (`app/src/lib/layout.js`): nodes are ranked by
  dependency depth so `depends_on` flows left→right (consumers left, shared
  foundation/`bus` nodes right), a barycenter pass minimises edge crossings, and
  edge-less nodes are parked in a side grid.
- **Added — colour-coded, selectable edges**: each dependency edge (arrowhead included,
  via `context-stroke`) is drawn in its source requirement's colour, so overlapping
  lines stay traceable; cards are kept neutral. Click a line to isolate it — it goes
  bold, the rest dim, and its two endpoints are ringed, so `x → y` is unambiguous.
- **Changed — card-avoiding orthogonal routing**: edges run their verticals in the
  inter-column gutters and cross any intermediate column only through a gap between its
  cards, so a line never passes through a card it doesn't connect to (no more
  "x → y → z through a node" look). Rounded right-angle turns.
- **Added — grab-to-pan**: drag anywhere on a map canvas to pan it (no need for the
  scrollbars); a plain click (no drag) still selects a node or edge.
- **Fixed — "center & highlight" button**: it set the highlight but never scrolled; it
  now `scrollIntoView`s the highlighted node.
- **Fixed — `_build_json` area**: emits the ID-prefix fallback (`_area_of`) when a
  requirement has no explicit `area:`, matching the Mermaid path's grouping so the
  JSON graph carries a usable `area` for external front-ends.

## engine `1.10.0` — 2026-06-04

- **Added — React front-end (`app/`)**: the four product surfaces (Map · Problems ·
  Console · Spec) as a real Vite + React app, recreated from the design system. Run
  with `cd app && npm run dev` (dev server pinned to port 5173 via `--strictPort`).
- **Added — `export` command**: `reqmap.py export` emits the registry graph as
  `requirements/_map.json` (`{engine_version, nodes, edges}`) — to stdout (`--out -`),
  a path (`--out PATH`), or the default file — for an external front-end to consume.
- **Added — self-contained viewer (`_map.html`)**: `map` injects this repo's graph
  into a pre-built single-file React viewer (`scripts/_map_viewer.html`, carrying a
  `<!--REQMAP_DATA-->` marker) → a double-click-openable `requirements/_map.html`,
  no server, no npm. Emitted only when the template is vendored beside the engine;
  the injected data is escaped (`</` → `<\/`) against script-breakout. `_map.html` is
  regenerable and gitignored.
- **Behavior change — engine no longer hand-generates HTML**: `render_html` and the
  inline HTML template were removed; `map` now writes `_map.md` + `_map.json`
  (+ `_map.html` from the viewer template when present). The freshness gate
  (`map --check`) now covers `_map.md` + `_map.json`. Re-seed consumer repos with both
  `scripts/reqmap.py` and `scripts/_map_viewer.html` (see SKILL setup / `sync_reqmap.sh`).

## engine `1.8.0` — 2026-06-03

- **Added**: `extract`/`init` now discover prose capabilities (`.md`/`.html`) by
  default, classified by `classify_prose` into three buckets — ignore
  (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), and
  capability-source (prompts/specs). Capability-source prose is auto-drafted as a
  `draft` stub from its title + `##` headings (`_prose_facts`). An advisory
  doc-sync step is emitted in the skill for sync-only docs tagged `generated-from`.
- **Behavior change**: on first post-upgrade `init`/`extract`, repos with
  prompt/spec markdown will see new `draft` requirements. Drafts are NOT enforced
  by the gate (`draft` is not in `ENFORCED`), so this cannot break an existing
  `check`. Review, edit, and `promote` the real ones; delete the rest.
  README/docs/HTML and meta files (`CLAUDE.md`, `SKILL.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE*`) are never auto-drafted.

## engine `1.5.0` — 2026-06-03

- **`reqmap.py promote <ID>`** — one-command human-validation step: flips a reviewed
  requirement's `status` to `confirmed` via a single frontmatter edit (preserves
  indentation + trailing comment, body untouched). Refuses when the requirement has
  no `implements:` member (a confirmed requirement must point to code, else the gate
  errors); warns when no `tested-by:` is linked; idempotent on an already-confirmed
  requirement. Dogfooded as `REQ-PROMOTE-011`.
- **owner standardized** to `Alex` across the repo's own requirements + the scaffold
  default (`extract` still emits `owner: auto` for machine-drafted, unreviewed files).

## engine `1.4.0` — 2026-06-03

Drift gates to prevent the version/map skew that slipped past in 1.3.x.

- **`reqmap.py map --check`** — freshness gate: regenerates the map in memory and
  compares it to the committed `_map.html`/`_map.md` (ignoring the volatile
  `generated:` timestamp), exiting non-zero if stale. A map that was never generated
  passes (consumers who don't track maps are unaffected). Wired into the shared
  pre-commit hook and CI so a code/requirement edit that shifts the map can't be
  committed without regenerating it.
- **`check_versions.py --fix`** — propagates `plugin.json`'s version into every
  `marketplace.json` occurrence, so a bump is one edit + one command instead of three
  hand-edits (the exact drift that failed CI in 1.3.0).
- **dev pre-commit hook** (`.githooks/pre-commit`, enable with
  `git config core.hooksPath .githooks`) — runs version coherence + the drift gate +
  map freshness locally, before CI.

## engine `1.3.0` — 2026-06-03

Non-code capability discovery + corpus-health visibility (`MAP_ENGINE_VERSION` 2026-06-03).

- **`candidates --md-glob`** — discover capabilities in authoritative **non-code** files
  (prompt/spec markdown), advisory-only and allowlist-bounded. Off unless a glob is
  given; writes no `.md`. A new `_md_facts()` extractor pulls the H1 title, the first
  blockquote after it (intent), and `## ` H2 headings (no parser). The plan now carries
  `coverage_summary {total_candidates, with_existing_req}` and a `lineage_note` so an
  unfilled plan can't masquerade as coverage, and so a `generated-from`/`implements`
  tag is understood as authoring lineage — not auto-tracking of later source edits.
- **`.md` added to the scan extensions** so prose capabilities can carry membership
  tags (`<!-- implements: ID -->`). The drift hash still anchors only on the authored
  Contract+Acceptance, so source prose may drift freely.
- **`check` health line** — the summary now reports `(N confirmed, M legacy-schema)`,
  and legacy-schema requirements (no `## WHAT — Verify intent` section, for which
  `findings` is silently inactive) are flagged with a non-blocking WARN. Makes an
  all-baseline corpus (gate enforces nothing yet) and an inactive `findings` visible.
- **`extract`** now annotates the emitted `risk:` field as an author triage hint that
  the engine does not read.
- **map risk signals** — two new signals surface on the Risk tab + `_map.md` table +
  detail panel: `untested` (a requirement with an `implements` member but no
  `tested-by`), suppressible per-requirement with a `test_exempt: <reason>` frontmatter
  field; and `unverified-intent` (a requirement with an open `## WHAT — Verify intent`
  item). Both reuse the existing risk machinery.
- **map zoom-fit fix** — diagrams now fit their container on first open *and* on every
  tab switch. Fit is measured after layout (double `requestAnimationFrame`, zero-size
  guard) and centered, with a capped modest upscale (`FIT_MAX`) so small diagrams fill
  the pane without over/under-zooming.

## check action `v1.0.0` — 2026-06-03

First published release of the `requirement-manager` CI action. Run the drift gate
on every push and PR without copying YAML boilerplate into each repo.

### Usage
```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v1
```

### Inputs (optional)
| input | default | purpose |
|---|---|---|
| `reqmap-path` | `scripts/reqmap.py` | path to your vendored engine, relative to `working-directory` |
| `working-directory` | `.` | directory the gate runs from (where `requirements/` lives) |
| `python-version` | `3.x` | Python to set up (engine is stdlib-only — any 3.x works) |

### What it enforces
`reqmap.py check` — link sync (every code tag points to a real requirement; every
confirmed requirement has ≥1 member), content drift vs. the lock, and `depends_on`
target existence. Fails the build on any violation.

### Notes
- **Versioning:** pin to `@v1` (moves with backward-compatible fixes) or to `@v1.0.0`
  / a commit SHA for exact reproducibility. The action ref is independent of the
  plugin/PyPI semver.
- **Scope:** the vendored-copy staleness notice (`warn_if_stale`) is gated on
  `CLAUDE_PLUGIN_ROOT`, unset in CI — silent and exit-neutral there by design.
- **Security:** keep `permissions: contents: read` in the caller workflow; the gate
  needs no secrets and no write scope.
