---
id: REQ-SITE-026
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-MAP-007, REQ-VIEWER-007, REQ-PAGES-021]
satisfies: [NEED-SSOT-001]
milestone: v1.35
---

# Generate & maintain a project presentation page

> A project is easier to grasp from one presentation page than from a folder of
> files. This capability lets the engine keep that page's links and key numbers
> current — injecting engine-owned regions into a page the author still controls,
> and scaffolding one when none exists — so the page never drifts from the registry.

## WHAT — Contract (normative)
- `site --attach <page.html>` shall inject the requested marker-delimited regions
  (`nav`, `stats`; default `nav`) into the page, replacing only the bytes between each
  region's paired markers and preserving all other (authored) content. A re-run with no
  underlying change shall produce a byte-identical file (idempotent).
- When the `--attach` target does not exist, `site` shall scaffold a self-contained default
  page (the inline `SITE_TEMPLATE`) with the regions filled and an authored placeholder hero.
- The `nav` region shall emit a link only when its target resolves: Live Map when a sibling
  `map.html` exists, Diagram when `--diagram <rel>` names an existing file, GitHub when a git
  remote resolves. A missing git remote, missing artifact, or non-checkout shall never raise.
- The engine shall never import or execute the excalidraw skill's builder; the Diagram entry
  is a link only.
- `init` shall, unless `--no-site` is given, run a best-effort `site` step after `map`:
  refresh `nav`+`stats` in `docs/architecture.html` if it exists, else scaffold it plus a
  Pages signal (`.nojekyll` + an `index.html` redirect). A failure in this step shall not
  abort `init`.
- `map --check` shall flag the site page stale when its on-disk `stats` region differs from a
  fresh render. The `nav` region is excluded (it embeds the fork-specific repo URL). A page
  that was never generated, or that lacks a `stats` region, is not stale.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes & known limitations (informative)
- v1 engine-owns `nav` + `stats`; `commands`/`layers` render as authored content in the
  scaffold and may be promoted to engine-owned regions later.
- The interactive "scan docs/ and ask which target + regions" flow lives in the
  requirement-manager skill, not the engine (the engine is headless-safe).

## HOW — Acceptance (= tests)
AC-1
  Given  a page with `nav`/`stats` markers
  When   `site --attach` runs twice
  Then   the second run leaves the file byte-identical and authored prose intact

AC-2
  Given  a repo with no git remote
  When   `site --attach` injects `nav`
  Then   it exits 0 and emits no GitHub link

AC-3
  Given  an absent `--attach` target
  When   `site` runs
  Then   it scaffolds a full page with the regions + the placeholder-hero marker

AC-4
  Given  a generated site page
  When   its `stats` region is edited to differ from a fresh render
  Then   `map --check` exits non-zero and names the page (it exits 0 before the edit)

AC-5
  Given  `docs/` present and no `--no-site`
  When   `init` runs
  Then   `docs/architecture.html` exists with engine regions; `--no-site` skips it

## WHERE — Current implementation
- `cmd_site`, `_render_region`, `_inject_region`/`_extract_region`, `_git_remote_web_url`,
  `_site_default_target`, `_site_pages_bootstrap`, the `cmd_init` hook, and the `_map_check`
  site branch in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
