---
id: REQ-VIEWER-007
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-MAP-007]
superseded_by:
milestone: v1.04
---

# Self-contained HTML map viewer

> The Mermaid diagrams render on GitHub, but a richer interactive view needs a browser app.
> This inlines the map's JSON graph into a single self-contained HTML file you open by
> double-click — no server, no install. It is optional: absent the vendored template, the
> engine still emits the diagrams and the JSON.

## WHAT — Contract (normative)
- It shall generate `_map.html` — a self-contained, single-file copy of the React viewer
  (the Vite + React app under `app/`) with this repo's graph inlined as
  `window.__REQMAP_DATA__`, openable by double-click with no server — WHEN the viewer
  template `_map_viewer.html` is vendored beside the engine.
- Absent the template it shall emit nothing (return None) without failing, so `map` still
  writes `_map.md` + `_map.json` and the stdlib engine works with no extra files.
- It shall inject the graph by replacing the template's `<!--REQMAP_DATA-->` marker with a
  single inline `<script>window.__REQMAP_DATA__=…</script>` assignment carrying the same
  `{nodes, edges}` graph [[REQ-MAP-007]] builds.
- The injected graph shall be escaped (`</` → `<\/`) so a `</script>` sequence in any
  requirement field cannot break out of the inline-data `<script>` (HTML-injection guard).

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The single-file build (`app/` → `npm run build:viewer`) is vendored beside the engine as
  `scripts/_map_viewer.html` with a `<!--REQMAP_DATA-->` marker; the stdlib engine swaps the
  marker for the inline data, so it ships a rich UI without itself depending on Node/npm.
- `_map.html` is a regenerable artifact (template + `_map.json`), not committed; rebuild with
  `map`. `_map.json` (owned by [[REQ-MAP-007]]) is the committed source of its data.
- Publishing this viewer to a repo's GitHub Pages folder and gating that copy is a separate
  capability — see [[REQ-PAGES-021]].

## HOW — Acceptance (= tests)
AC-1
  Given  the vendored `_map_viewer.html` template is present
  When   `map` runs
  Then   it writes `_map.html` and the `<!--REQMAP_DATA-->` marker is replaced with a
         `window.__REQMAP_DATA__` assignment carrying one node per requirement

AC-2
  Given  a requirement field containing `</script>`
  When   the viewer is rendered
  Then   the sequence is escaped (`<\/`) so it cannot close the inline-data script early

AC-3
  Given  no template is vendored
  When   `map` runs
  Then   `render_html` returns None and only `_map.md` + `_map.json` are written (no crash)

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py map`, then double-clicks `_map.html`. It opens in her browser with the
  whole requirement graph inlined — no server — even though the engine itself is stdlib-only.

## WHERE — Current implementation
- `render_html`, `_inject_viewer`, `_viewer_template_path` in `reqmap.py`; `render_html` is
  called by `cmd_map` after `_map.json`/`_map.md` are written.

## Links
- Used by: (auto)
## Members in code (auto)
