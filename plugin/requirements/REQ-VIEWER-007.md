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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     the template   scripts/_map_viewer.html — the pre-built React viewer vendored
                    beside the engine, carrying a `<!--REQMAP_DATA-->` marker.
     the graph      the `{nodes, edges}` registry data [[REQ-MAP-007]] builds.
     a V8 no-op     an escape the browser's JavaScript engine reads as if it were
                    not there, so the data means the same after escaping. -->

**When it writes the viewer**
- `map` generates `_map.html` when the template `_map_viewer.html` is vendored beside
  the engine.
- `_map.html` is a self-contained, single-file copy of the React viewer — the Vite +
  React app under `app/` — with this repo's graph inlined as `window.__REQMAP_DATA__`.
- `_map.html` opens by double-click, with no server.
- Absent the template, `render_html` emits nothing and returns None without failing.
- `map` then still writes `_map.md` and `_map.json`, so the stdlib engine works with no
  extra files.

**How it injects the graph**
- `render_html` replaces the template's `<!--REQMAP_DATA-->` marker with a single inline
  `<script>window.__REQMAP_DATA__=…</script>` assignment.
- That assignment carries the same `{nodes, edges}` graph [[REQ-MAP-007]] builds.

**How it escapes the graph**
- `render_html` makes the injected graph HTML-safe for embedding inside `<script>` by
  applying three escapes in order. All three are V8 no-ops: a backslash is silently
  ignored before `/`, `!` and `-`.
  - `</`   → `<\/`   — prevents `</script>` from closing the element early
  - `<!--` → `<\!--` — prevents the HTML5 parser entering "script data escaped" state
  - `-->`  → `-\->`  — prevents prematurely closing that state if somehow entered
- The first guard alone was the original contract. The `<!--` and `-->` guards were added
  in v2.3.5 after a confirmed bug: requirement bodies that discuss HTML injection (and
  therefore contain literal `<!--`) broke `file://` opening by making
  `window.__REQMAP_DATA__` null.
- `render_html` also escapes U+2028 and U+2029 to their `\\u2028`/`\\u2029` forms.
  Those two characters end a line in JavaScript but not in JSON, so unescaped they turn the
  assignment into an unterminated string on any engine older than ES2019. The escaped forms
  denote the same characters in JSON, so the parsed graph is unchanged.

**What language it shows**
- The viewer renders its own UI chrome in English by default.
- A locale control in the viewer's top bar switches that chrome to another bundled language.
- Requirement content is never translated: id, title, intent, contract clauses, acceptance
  criteria and member paths stay in the language their author wrote them in.
- The engine's own vocabulary is never translated either: `status`, `layer`, tag-role and
  severity values stay the literal strings the requirement files and the gate use.
- A chrome string with no entry in the active locale falls back to its English text.
- The reader's chosen locale is remembered on their machine and is never written into the
  generated file, so `_map.html` stays byte-identical whatever anyone last selected.

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

AC-4
  Given  a requirement field containing `<!--` (e.g. a body that documents HTML injection)
  When   the viewer is rendered
  Then   `<!--` is escaped to `<\!--` in the inlined blob so the HTML5 parser never
         enters "script data escaped" state, and `window.__REQMAP_DATA__` is always
         accessible from the deferred bundle (verified: file:// opens without error)

AC-3
  Given  no template is vendored
  When   `map` runs
  Then   `render_html` returns None and only `_map.md` + `_map.json` are written (no crash)

AC-5
  Given  a requirement whose title or contract contains U+2028 or U+2029
  When   `map` writes `_map.html`
  Then   neither character appears raw in the file, and the inlined graph still parses to
         the original text

AC-6
  Given  the viewer rendered with a non-English locale selected
  When   a requirement's spec is shown
  Then   the section headers appear in that language while the requirement's own title,
         contract and acceptance text stay exactly as authored, and `status` / `layer`
         values stay literal

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py map`, then double-clicks `_map.html`. It opens in her browser with the
  whole requirement graph inlined — no server — even though the engine itself is stdlib-only.

## WHERE — Current implementation
- `render_html`, `_inject_viewer`, `_viewer_template_path` in `reqmap.py`; `render_html` is
  called by `cmd_map` after `_map.json`/`_map.md` are written.
- `check_viewer_data_sync` (+ `_vds_*` helpers) in `reqmap.py`, called from `cmd_check` (`gate`):
  a warn-only heuristic comparing `app/src/lib/data.js`'s hand-authored `BAKED` fallback fixture
  against the live registry, so a stale demo entry is flagged rather than silently shown forever.
  A fixture entry marked `demoOnly:true` is skipped: the demo dataset deliberately invents an
  orphan and a deprecated capability so the Risk and Problems tabs have signals with no engine
  present, and those ids cannot exist in any registry. An id left unmarked and absent from the
  registry is still reported — that is a requirement renamed out from under the fixture.
- The locale dictionary and provider live in `app/src/lib/i18n.jsx`; the toggle is part of the
  top bar in `app/src/App.jsx`. Both are outside the plugin scan root, like the rest of the app,
  so the SSR smoke (`npm run smoke`) is what holds them — it asserts both directions: that a
  header translates, and that requirement content and engine vocabulary do not.
- The Vite+React source lives in `app/src/views/` (repo root, outside the plugin scan root):
  - `MapView.jsx` — force-graph rendering of the requirement graph
  - `ProblemsView.jsx` — gate errors, drift items, and open risk inbox
  - `RoadmapView.jsx` — milestone Gantt built from requirement `milestone:` fields
  - `SpecView.jsx` — full requirement dossier (contract, ACs, members, deps)
  - `app/src/lib/data.js` — loads `window.__REQMAP_DATA__` into the views
  These files carry no `implements:` tags — app/ is deliberately excluded from the widened
  repo-root scan (see the top-level `.reqmapignore`), because the requirement covers the
  engine-side injection contract, not the compiled UX layer. `npm run smoke` (app/CLAUDE.md)
  is the only automated check for the viewer, and it is run manually before vendoring, not
  wired into CI or reqmap's gate — a known gap, tracked in TODO.md, not silently claimed as
  covered.

## Links
- Used by: (auto)
## Members in code (auto)
