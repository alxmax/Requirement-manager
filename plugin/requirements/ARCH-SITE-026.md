---
id: ARCH-SITE-026
status: draft
level: architecture
layer: feature
owner: Alex
milestone: v1.35
depends_on: [ARCH-MAP-007, ARCH-VIEWER-007]
satisfies: [SYS-VISUAL-106]
---

# Generate & maintain a project presentation page

## Description
> A project is easier to grasp from one presentation page than from a folder of
> files. This capability lets the engine keep that page's links and key numbers
> current — injecting engine-owned regions into a page the author still controls,
> and scaffolding one when none exists — so the page never drifts from the registry.

Every bullet below is binding.
- `sync` refreshes the marker-delimited `nav` and `stats` regions of the project's presentation page idempotently, replacing only the bytes between each region's paired markers and preserving all other authored content; `init` scaffolds the page when it is absent. [[REQ-SITE-924]]

## Cases
CASE-1
  Given  a page with `nav`/`stats` markers
  When   `sync --attach` runs twice
  Then   the second run leaves the file byte-identical and authored prose intact

CASE-2
  Given  a repo with no git remote
  When   `sync --attach` injects `nav`
  Then   it exits 0 and emits no GitHub link

CASE-3
  Given  an absent `--attach` target
  When   `sync --attach` runs
  Then   it scaffolds a full page with the regions + the placeholder-hero marker

CASE-4
  Given  a generated site page
  When   its `stats` region is edited to differ from a fresh render
  Then   the site freshness check names the page (it names nothing before the edit)

CASE-5
  Given  `docs/` present and no `--no-site`
  When   `init` runs
  Then   `docs/architecture.html` exists with engine regions; `--no-site` skips it

## Context
**Notes**
- The engine owns `nav` + `stats` only; everything else on the page, the
  scaffold's hero included, is authored content.
- Plugin v8.2.0 removed this capability (ADR-0047); it was restored at the
  maintainer's direction. `sync --attach` replaces the old `site` verb.
- The interactive "scan docs/ and ask which target" flow lives in the
  requirement-manager skill, not the engine (the engine is headless-safe).

**Current implementation**
- `cmd_site`, `_render_region`, `_inject_region`/`_extract_region` and
  `site_stale` in `site.py`; `_git_remote_web_url` in `git.py`;
  `_site_default_target`, `_site_pages_bootstrap`, `_init_site` in `init.py`
  and the `sync` step in `reqmap.py`.


--------------------


---
id: REQ-SITE-924
status: draft
level: code
layer: feature
owner: Alex
milestone: v3.2
satisfies: [ARCH-SITE-026]
---

# Inject engine-owned regions into a presentation page

## Description
> `sync` writes the `nav` and `stats` regions into `docs/architecture.html`, a page
> the author still edits by hand, touching only the bytes between each region's markers.
> Without it, keeping a hand-authored page's links and counts in sync with the registry
> would mean either regenerating the whole page (losing authored prose) or manually
> copying numbers every time the corpus changes.

Every bullet below is binding.
- `sync --attach <page.html>` injects the marker-delimited `nav` and `stats` regions
  into the page, replacing only the bytes between each region's paired markers and
  preserving all other (authored) content. A re-run with no underlying change produces
  a byte-identical file (idempotent). Without `--attach`, `sync` refreshes
  `docs/architecture.html` at the git root when that file exists, and writes nothing
  when it does not.
- When the `--attach` target does not exist, `sync` scaffolds a self-contained default
  page (the inline `SITE_TEMPLATE`) with the regions filled and an authored placeholder hero.
- The `nav` region emits a link only when its target resolves: Live Map when a sibling
  `map.html` exists, GitHub when a git remote resolves. A missing git remote, missing
  artifact, or non-checkout never raises.
- `init`, unless `--no-site` is given, runs a best-effort site step after `map`:
  refreshes `nav`+`stats` in `docs/architecture.html` if it exists, else scaffolds it plus a
  Pages signal (`.nojekyll` + an `index.html` redirect, each only when absent — an
  existing `index.html` is never overwritten). A failure in this step does not abort
  `init`.
- `site_stale` names the site page when its on-disk `stats` region differs from a fresh
  render. The `nav` region and the `engine` cell are excluded (the first embeds the
  fork-specific repo URL, the second moves on every engine bump). A page that was never
  generated, or that lacks a `stats` region, is not stale.

## Cases
CASE-1 — a second attach run with no change is byte-identical
  Given  a page carrying `<h1>Mine</h1>` and no underlying data change
  When   `cmd_site(..., attach=page, regions=["nav", "stats"])` runs twice
  Then   the file's content after the second run equals the content after the first, and
         `<h1>Mine</h1>` is still present

CASE-2 — site scaffolds a full page when the attach target is absent
  Given  no file at `docs/architecture.html`
  When   `cmd_site(..., attach=target, regions=["nav", "stats"])` runs
  Then   the written page contains both region markers and the "<!-- author me -->"
         placeholder hero

CASE-3 — an absent nav target is omitted, not an error
  Given  a rendering context with no repo URL and no map
  When   `_render_region("nav", ctx)` runs
  Then   it returns markup with no `<a` link and raises nothing

CASE-4 — init writes the Pages signal without clobbering a landing page
  Given  a `docs/` directory holding a hand-written `index.html` and no `.nojekyll`
  When   `_site_pages_bootstrap` runs on it, and separately on an empty `docs/`
  Then   the first leaves `index.html` unchanged and creates `.nojekyll`; the second
         creates both, the index redirecting to `architecture.html`

CASE-5 — init scaffolds the site page unless --no-site is passed
  Given  a `docs/` directory with no `architecture.html`
  When   `cmd_init(..., no_site=False)` runs, and separately `cmd_init(..., no_site=True)`
  Then   the first run creates `docs/architecture.html` with a `##REQMAP:NAV##` region;
         the second run creates no such file

CASE-6 — the freshness check fires only after the stats region is tampered with
  Given  a freshly generated site page with a `stats` region
  When   `site_stale` runs before and after the `stats` region is overwritten with
         "TAMPERED"
  Then   it returns None before the edit and the page's file name after it
