---
id: ARCH-VIEWER-007
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.04
depends_on: [ARCH-MAP-007]
satisfies: [SYS-VISUAL-106]
lint_exempt: [ac-count-high, file-spread]
---

# Self-contained HTML map viewer

## Description
> The Mermaid diagrams render on GitHub, but a richer interactive view needs a browser app.
> This inlines the map's JSON graph into a single self-contained HTML file you open by
> double-click — no server, no install. It is optional: absent the vendored template, the
> engine still emits the diagrams and the JSON.

Every bullet below is binding.
- `map` generates `_map.html` when the template `_map_viewer.html` is vendored beside the engine, and skips it (no crash) when the template is absent. [[REQ-VIEWER-940]]
- `render_html` makes the injected graph HTML-safe for embedding inside `<script>` by applying three escapes in order, each a V8 no-op that reads the same after parsing. [[REQ-VIEWER-941]]
- The viewer ranks nodes by longest dependency path so `depends_on` edges flow one way, and renders a node's acceptance criteria as the author wrote them, not folded to one line. [[REQ-VIEWER-942]]
- The viewer renders its own UI chrome in a chosen language while requirement content and engine vocabulary stay exactly as authored. [[REQ-VIEWER-943]]

## Cases
CASE-1
  Given  the vendored `_map_viewer.html` template is present
  When   `map` runs
  Then   it writes `_map.html` and the `<!--REQMAP_DATA-->` marker is replaced with a
         `window.__REQMAP_DATA__` assignment carrying one node per requirement

CASE-2
  Given  a requirement field containing `</script>`
  When   the viewer is rendered
  Then   the sequence is escaped (`<\/`) so it cannot close the inline-data script early

CASE-7
  Given  a registry whose `depends_on` edges form a cycle
  When   the layout is computed
  Then   every node is placed, no rank exceeds the node count, and the closing edge is drawn

CASE-4
  Given  a requirement field containing `<!--` (e.g. a body that documents HTML injection)
  When   the viewer is rendered
  Then   `<!--` is escaped to `<\!--` in the inlined blob so the HTML5 parser never
         enters "script data escaped" state, and `window.__REQMAP_DATA__` is always
         accessible from the deferred bundle (verified: file:// opens without error)

CASE-3
  Given  no template is vendored
  When   `map` runs
  Then   `render_html` returns None and only `_map.md` + `_map.json` are written (no crash)

CASE-5
  Given  a requirement whose title or contract contains U+2028 or U+2029
  When   `map` writes `_map.html`
  Then   neither character appears raw in the file, and the inlined graph still parses to
         the original text

CASE-6
  Given  the viewer rendered with a non-English locale selected
  When   a requirement's spec is shown
  Then   the section headers appear in that language while the requirement's own title,
         contract and acceptance text stay exactly as authored, and `status` / `layer`
         values stay literal

CASE-8
  Given  a node carrying both a labelled `accept` block and the folded `acc` list
  When   its spec is rendered
  Then   the Given/When/Then lines appear as authored, one per line, and the folded
         one-line form is not what the reader sees

## Context
**Terms**
- the template   scripts/_map_viewer.html — the pre-built React viewer vendored
- beside the engine, carrying a `REQMAP_DATA` marker.
- the graph      the `{nodes, edges}` registry data [[ARCH-MAP-007]] builds.
- a V8 no-op     an escape the browser's JavaScript engine reads as if it were
- not there, so the data means the same after escaping. -->

**Notes**
- `lint_exempt: file-spread`: the members are one engine function plus the viewer's source
  tree (`app/src/**`, its vendoring script and single-file build config). A UI is many files
  by construction; they are built into ONE artifact, so the spread is not diffuseness.
- `lint_exempt: [ac-count-high]`: the 8 criteria cover four independent surfaces of one
  artifact — data injection and its three escapes, node placement, UI language, and how
  the acceptance block is rendered. Splitting them would produce requirements that all
  point at the same single vendored file, which is the coupling the count is meant to
  detect, not a fix for it.
- The single-file build (`app/` → `npm run build:viewer`) is vendored beside the engine as
  `scripts/_map_viewer.html` with a `<!--REQMAP_DATA-->` marker; the stdlib engine swaps the
  marker for the inline data, so it ships a rich UI without itself depending on Node/npm.
- `_map.html` is a regenerable artifact (template + `_map.json`), not committed; rebuild with
  `map`. `_map.json` (owned by [[ARCH-MAP-007]]) is the committed source of its data.
- Publishing this viewer to a repo's GitHub Pages folder and gating that copy is a separate
  capability — see [[ARCH-PAGES-021]].

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py map`, then double-clicks `_map.html`. It opens in her browser with the
  whole requirement graph inlined — no server — even though the engine itself is stdlib-only.

**Current implementation**
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
  Every file under `app/src/` carries an `implements:` tag (this requirement for the shell,
  views, styles and data loading; `ARCH-SEARCH-036` for `lib/search.js`; `ARCH-TRANSLATE-044`
  alongside on `lib/i18n.jsx` and `views/SpecView.jsx`), as do `app/scripts/install-viewer.mjs`
  and `app/vite.viewer.config.js` — the vendoring step and the single-file build are part of
  this contract. `app/scripts/ssr-smoke.jsx` is the `tested-by` member; `npm run smoke`
  (app/CLAUDE.md) runs it in CI's `artifacts` job, which also rebuilds the vendored viewer and
  fails when the committed copy differs. The build strips the comments, so the tags never reach
  `_map_viewer.html`; only `app/dist*`, `app/.vite` and the SSR bundle stay in `.reqmapignore`.


--------------------


---
id: REQ-VIEWER-940
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Writing _map.html from the vendored template

## Description
> The viewer ships as one HTML file so it can be opened by double-click, with no server and no
> Node/npm dependency for the stdlib engine itself. When the template is not vendored, `map`
> still succeeds — it degrades to the two artifacts every consumer gets regardless of whether
> they built the viewer.

Every bullet below is binding.
- `map` generates `_map.html` when the template `_map_viewer.html` is vendored beside
  the engine.
- `_map.html` is a self-contained, single-file copy of the React viewer — the Vite +
  React app under `app/` — with this repo's graph inlined as `window.__REQMAP_DATA__`.
- `_map.html` opens by double-click, with no server.
- Absent the template, `render_html` emits nothing and returns None without failing.
- `map` then still writes `_map.md` and `_map.json`, so the stdlib engine works with no
  extra files.
- `render_html` replaces the template's `<!--REQMAP_DATA-->` marker with a single inline
  `<script>window.__REQMAP_DATA__=…</script>` assignment.
- That assignment carries the same `{nodes, edges}` graph [[ARCH-MAP-007]] builds.

## Cases
CASE-1 — render_html writes _map.html when the vendored template exists
  Given  the vendored `_map_viewer.html` template beside the engine
  When   `render_html(data, reqs_dir)` runs
  Then   it returns the path to a written `_map.html` file

CASE-2 — the written _map.html carries the graph as window.__REQMAP_DATA__
  Given  `render_html({"nodes": [...], "edges": []}, reqs_dir)` writing `_map.html`
  When   the file is read back
  Then   it contains `"window.__REQMAP_DATA__="` and no leftover `<!--REQMAP_DATA-->`
         marker, and references no external file — opening by double-click with no server

CASE-3 — render_html returns None, not an error, when the template is missing
  Given  no `_map_viewer.html` template beside the engine
  When   `render_html(data, reqs_dir)` runs
  Then   it returns `None` and raises nothing

CASE-4 — map still writes _map.md and _map.json when the viewer template is absent
  Given  no vendored `_map_viewer.html` template
  When   `cmd_map` runs
  Then   `_map.md` and `_map.json` are written and `map` exits 0

CASE-5 — the marker is consumed and replaced by a script assignment
  Given  template text `"<head><!--REQMAP_DATA--></head>"` and a graph with one node
  When   `_inject_viewer(template_text, data)` runs
  Then   the marker is gone and the output contains `"window.__REQMAP_DATA__="`

CASE-6 — the inlined blob's node id matches the graph handed to _inject_viewer
  Given  a graph `{"nodes": [{"id": "A-1"}], "edges": []}`
  When   `_inject_viewer(template_text, data)` runs
  Then   the injected `<script>` text contains `"A-1"`


--------------------


---
id: REQ-VIEWER-941
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Escaping the inlined graph for embedded <script>

## Description
> The graph is embedded as a `<script>` assignment inside HTML the reader trusts, so any body a
> requirement author wrote — including one that discusses HTML injection and therefore contains
> `<!--` literally — must not be able to break out of that script or corrupt the page. Three
> escapes close three different ways a literal sequence in requirement text could do that, each
> added after a real failure was found.

Every bullet below is binding.
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

## Cases
CASE-1 — a field carrying all three dangerous sequences is fully escaped and still parses
  Given  a node title `"</script><!--x-->"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output has none of `</`, `<!--`, `-->` raw, and re-parsing the blob as JSON
         yields the original title unchanged

CASE-2 — a </script> breakout attempt in a field is neutralized
  Given  a node id `"a</script><img src=x>"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output has no raw `"</script><img"` and contains `"<\\/script>"` instead

CASE-3 — a literal <!-- inside a field is escaped to <\!--
  Given  a node contract clause `"discusses HTML injection via <!-- markers"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output contains `"<\\!--"` and no raw `"<!--"` inside the injected blob,
         keeping `window.__REQMAP_DATA__` parseable instead of null

CASE-4 — a literal --> inside a field is escaped to -\->
  Given  a node title containing the literal sequence `"-->"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output contains `"-\\->"` and no raw `"-->"` inside the injected blob

CASE-5 — U+2028/U+2029 in a title are escaped and still round-trip through JSON
  Given  a node title containing U+2028 and a contract clause containing U+2029
  When   `_inject_viewer(template_text, data)` runs
  Then   neither raw character appears in the output, the literal 6-character
         sequences \u2028 and \u2029 do, and re-parsing the blob as
         JSON yields the original title unchanged


--------------------


---
id: REQ-VIEWER-942
status: confirmed
lint_exempt: [file-spread]
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Ranking nodes and rendering acceptance criteria as authored

## Description
> A force-directed graph with no fixed coordinates would jump around on every reload and
> correlate nothing with the dependency structure it is meant to show. Ranking by longest path
> makes every `depends_on` edge point the same visual direction, so a reader learns the shape of
> the corpus from where a node sits, not only from its label. The acceptance block gets the same
> care: folding it to one line for search must not become what the reader is actually shown.

Every bullet below is binding.
- The viewer ranks nodes by longest dependency path, so `depends_on` edges flow one way.
- The viewer excludes a cycle-closing edge from that ranking, and still draws it.
- No node ranks higher than the number of nodes, whatever the registry's shape.
- A node carries the acceptance section twice: `accept`, the labelled Given/When/Then
  block as the author wrote it, and `acc`, the same criteria folded to one line each.
- The viewer renders `accept` — one line per line, as authored. `acc` is for search and
  counting, never the thing a reader is shown when the authored block exists.

## Cases
CASE-1 — a deep dependency chain ranks by longest path
  Given  an honest 12-node `depends_on` chain with no cycle
  When   the layout is computed
  Then   the deepest node's rank equals 11, one more than each of its direct predecessors

CASE-2 — a cycle-closing edge is excluded from ranking but still drawn
  Given  a registry whose `depends_on` edges close a 3-node cycle, plus a fourth node
         depending on the cycle
  When   the layout is computed
  Then   the cycle-closing edge still appears among the drawn edges, and every node —
         cyclic or not — receives a position

CASE-3 — no rank exceeds the node count even on a cyclic registry
  Given  the same cyclic registry
  When   the layout is computed
  Then   the highest rank is at most the node count minus one, and the canvas width stays
         bounded rather than growing with the number of relaxation passes

CASE-4 — a map node carries both the raw accept block and the folded acc list
  Given  a confirmed requirement with a labelled `## Cases` block of two criteria
  When   `_build_map_data` builds the node
  Then   `node["acc"]` has two folded entries and `node["accept"]` holds the raw block

CASE-5 — the reader sees the authored Given/When/Then lines, not the folded one-liner
  Given  a node whose `accept` field holds a labelled multi-line Given/When/Then case and
         whose `acc` field holds the same case folded to one line
  When   its spec is rendered
  Then   the multi-line block appears as authored, and the folded one-line text is not
         what the reader sees


--------------------


---
id: REQ-VIEWER-943
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# UI chrome language, requirement content untranslated

## Description
> The viewer's own chrome — nav labels, buttons, section headers — is UI text the tool owns and
> can safely translate. A requirement's title, contract and acceptance criteria are the artifact
> under review; translating those live would put words in the author's mouth and silently
> diverge from the `.md` file on disk. The two must never be confused, so this draws the line
> and holds it under every locale.

Every bullet below is binding.
- The viewer renders its own UI chrome in English by default.
- A locale control in the viewer's top bar switches that chrome to another bundled language.
- Requirement content is never translated: id, title, intent, contract clauses, acceptance
  criteria and member paths stay in the language their author wrote them in.
- The engine's own vocabulary is never translated either: `status`, `layer`, tag-role and
  severity values stay the literal strings the requirement files and the gate use.
- A chrome string with no entry in the active locale falls back to its English text.
- The reader's chosen locale is remembered on their machine and is never written into the
  generated file, so `_map.html` stays byte-identical whatever anyone last selected.

## Cases
CASE-1 — the viewer defaults to English chrome
  Given  no locale has been selected before
  When   a requirement's spec is rendered
  Then   its section headers appear in English

CASE-2 — switching locale translates chrome section headers
  Given  the Romanian locale selected
  When   the same spec is rendered
  Then   its section headers appear in Romanian, and the English header text is gone

CASE-3 — an untranslated chrome string falls back to English
  Given  a chrome string with no entry in the active locale's dictionary
  When   it is looked up for display
  Then   it renders as the original English text, not blank

CASE-4 — chrome translations interpolate their placeholders
  Given  a chrome string containing a `{n}`-style placeholder
  When   it is rendered in a non-English locale
  Then   the placeholder's value is substituted into the translated sentence

CASE-5 — requirement content stays in the author's language under any locale
  Given  the Romanian locale selected and a requirement's spec rendered
  Then   the requirement's own title appears exactly as authored, untranslated

CASE-6 — engine vocabulary stays literal under any locale
  Given  the Romanian locale selected and a requirement's spec rendered
  Then   its `status` value appears as the literal engine string, not a translated word

