---
id: ARCH-SITE-026
status: confirmed
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
- `site --attach <page.html>` injects the requested marker-delimited regions (`nav`, `stats`; default `nav`) into the page idempotently, replacing only the bytes between each region's paired markers and preserving all other authored content. [[REQ-SITE-924]]

## Cases
CASE-1
  Given  a page with `nav`/`stats` markers
  When   `site --attach` runs twice
  Then   the second run leaves the file byte-identical and authored prose intact

CASE-2
  Given  a repo with no git remote
  When   `site --attach` injects `nav`
  Then   it exits 0 and emits no GitHub link

CASE-3
  Given  an absent `--attach` target
  When   `sync` runs
  Then   it scaffolds a full page with the regions + the placeholder-hero marker

CASE-4
  Given  a generated site page
  When   its `stats` region is edited to differ from a fresh render
  Then   `map --check` exits non-zero and names the page (it exits 0 before the edit)

CASE-5
  Given  `docs/` present and no `--no-site`
  When   `init` runs
  Then   `docs/architecture.html` exists with engine regions; `--no-site` skips it

## Context
**Notes**
- v1 engine-owns `nav` + `stats`; `commands`/`layers` render as authored content in the
  scaffold and may be promoted to engine-owned regions later.
- The interactive "scan docs/ and ask which target + regions" flow lives in the
  requirement-manager skill, not the engine (the engine is headless-safe).

**Current implementation**
- `cmd_site`, `_render_region`, `_inject_region`/`_extract_region`, `_git_remote_web_url`,
  `_site_default_target`, `_site_pages_bootstrap`, the `cmd_init` hook, and the `_map_check`
  site branch in `reqmap.py`.


--------------------


---
id: REQ-SITE-924
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SITE-026]
---

# Inject engine-owned regions into a presentation page

## Description
> `site --attach docs/architecture.html` writes the `nav` and `stats` regions into a page
> the author still edits by hand, touching only the bytes between each region's markers.
> Without it, keeping a hand-authored page's links and counts in sync with the registry
> would mean either regenerating the whole page (losing authored prose) or manually
> copying numbers every time the corpus changes.

Every bullet below is binding.
- `site --attach <page.html>` injects the requested marker-delimited regions
  (`nav`, `stats`; default `nav`) into the page, replacing only the bytes between each
  region's paired markers and preserving all other (authored) content. A re-run with no
  underlying change produces a byte-identical file (idempotent).
- When the `--attach` target does not exist, `sync` scaffolds a self-contained default
  page (the inline `SITE_TEMPLATE`) with the regions filled and an authored placeholder hero.
- The `nav` region emits a link only when its target resolves: Live Map when a sibling
  `map.html` exists, Diagram when `--diagram <rel>` names an existing file, GitHub when a git
  remote resolves. A missing git remote, missing artifact, or non-checkout never raises.
- The engine never imports or executes the excalidraw skill's builder; the Diagram entry
  is a link only.
- `init`, unless `--no-site` is given, runs a best-effort `sync` step after `map`:
  refreshes `nav`+`stats` in `docs/architecture.html` if it exists, else scaffolds it plus a
  Pages signal (`.nojekyll` + an `index.html` redirect). A failure in this step does not
  abort `init`.
- `map --check` flags the site page stale when its on-disk `stats` region differs from a
  fresh render. The `nav` region is excluded (it embeds the fork-specific repo URL). A page
  that was never generated, or that lacks a `stats` region, is not stale.

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
  Given  a rendering context with no repo URL, no map, and no diagram
  When   `_render_region("nav", ctx)` runs
  Then   it returns markup with no `<a` link and raises nothing

CASE-4 — reqmap.py's own source never references the excalidraw builder
  Given  the `reqmap.py` source file
  When   its text is searched for "excalidraw_builder"
  Then   no occurrence is found

CASE-5 — init scaffolds the site page unless --no-site is passed
  Given  a `docs/` directory with no `architecture.html`
  When   `cmd_init(..., no_site=False)` runs, and separately `cmd_init(..., no_site=True)`
  Then   the first run creates `docs/architecture.html` with a `##REQMAP:NAV##` region;
         the second run creates no such file

CASE-6 — map --check fails only after the stats region is tampered with
  Given  a freshly generated site page with a `stats` region
  When   `_map_check` runs before and after the `stats` region is overwritten with
         "TAMPERED"
  Then   it exits 0 before the edit and exits 1 after it

