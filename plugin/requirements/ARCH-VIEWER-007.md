---
id: ARCH-VIEWER-007
status: confirmed
level: system
layer: feature
owner: Alex
depends_on: [ARCH-MAP-007]
satisfies: [SYS-VISUAL-106]
superseded_by:
milestone: v1.04
lint_exempt: [ac-count-high, file-spread]
---

# Self-contained HTML map viewer

## Description
> The Mermaid diagrams render on GitHub, but a richer interactive view needs a browser app.
> This inlines the map's JSON graph into a single self-contained HTML file you open by
> double-click — no server, no install. It is optional: absent the vendored template, the
> engine still emits the diagrams and the JSON.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     the template   scripts/_map_viewer.html — the pre-built React viewer vendored
                    beside the engine, carrying a `<!--REQMAP_DATA-->` marker.
     the graph      the `{nodes, edges}` registry data [[ARCH-MAP-007]] builds.
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
- That assignment carries the same `{nodes, edges}` graph [[ARCH-MAP-007]] builds.

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

**How it places the nodes**
- The viewer ranks nodes by longest dependency path, so `depends_on` edges flow one way.
- The viewer excludes a cycle-closing edge from that ranking, and still draws it.
- No node ranks higher than the number of nodes, whatever the registry's shape.

**How it shows the acceptance criteria**
- A node carries the acceptance section twice: `accept`, the labelled Given/When/Then
  block as the author wrote it, and `acc`, the same criteria folded to one line each.
- The viewer renders `accept` — one line per line, as authored. `acc` is for search and
  counting, never the thing a reader is shown when the authored block exists.

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

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
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

## Cases (= tests)
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
  Every file under `app/src/` carries an `implements:` tag (this requirement for the shell,
  views, styles and data loading; `ARCH-SEARCH-036` for `lib/search.js`; `ARCH-TRANSLATE-044`
  alongside on `lib/i18n.jsx` and `views/SpecView.jsx`), as do `app/scripts/install-viewer.mjs`
  and `app/vite.viewer.config.js` — the vendoring step and the single-file build are part of
  this contract. `app/scripts/ssr-smoke.jsx` is the `tested-by` member; `npm run smoke`
  (app/CLAUDE.md) runs it in CI's `artifacts` job, which also rebuilds the vendored viewer and
  fails when the committed copy differs. The build strips the comments, so the tags never reach
  `_map_viewer.html`; only `app/dist*`, `app/.vite` and the SSR bundle stay in `.reqmapignore`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-VIEWER-782
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Map generates _map.html when the template _map_viewer.html is

> `map` generates `_map.html` when the template `_map_viewer.html` is vendored beside the
> engine.

Scenario: render_html writes _map.html when the vendored template exists
  Given  the vendored `_map_viewer.html` template beside the engine
  When   `render_html(data, reqs_dir)` runs
  Then   it returns the path to a written `_map.html` file

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-783
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# _map.html is a self-contained, single-file copy of the

> `_map.html` is a self-contained, single-file copy of the React viewer — the Vite + React
> app under `app/` — with this repo's graph inlined as `window.__REQMAP_DATA__`.

Scenario: the written _map.html carries the graph as window.__REQMAP_DATA__
  Given  `render_html({"nodes": [...], "edges": []}, reqs_dir)` writing `_map.html`
  When   the file is read back
  Then   it contains `"window.__REQMAP_DATA__="` and no leftover `<!--REQMAP_DATA-->`
         marker, and references no external file — opening by double-click with no server

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-785
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Absent the template, render_html emits nothing and returns

> Absent the template, `render_html` emits nothing and returns None without failing.

Scenario: render_html returns None, not an error, when the template is missing
  Given  no `_map_viewer.html` template beside the engine
  When   `render_html(data, reqs_dir)` runs
  Then   it returns `None` and raises nothing

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-786
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Map then still writes _map.md and _map.json, so

> `map` then still writes `_map.md` and `_map.json`, so the stdlib engine works with no
> extra files.

Scenario: map still writes _map.md and _map.json when the viewer template is absent
  Given  no vendored `_map_viewer.html` template
  When   `cmd_map` runs
  Then   `_map.md` and `_map.json` are written and `map` exits 0

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-787
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Render_html replaces the template's <!--REQMAP_DATA--> marker with a

> `render_html` replaces the template's `<!--REQMAP_DATA-->` marker with a single inline
> `<script>window.__REQMAP_DATA__=…</script>` assignment.

Scenario: the marker is consumed and replaced by a script assignment
  Given  template text `"<head><!--REQMAP_DATA--></head>"` and a graph with one node
  When   `_inject_viewer(template_text, data)` runs
  Then   the marker is gone and the output contains `"window.__REQMAP_DATA__="`

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-788
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# That assignment carries the same {nodes, edges} graph

> That assignment carries the same `{nodes, edges}` graph [[ARCH-MAP-007]] builds.

Scenario: the inlined blob's node id matches the graph handed to _inject_viewer
  Given  a graph `{"nodes": [{"id": "A-1"}], "edges": []}`
  When   `_inject_viewer(template_text, data)` runs
  Then   the injected `<script>` text contains `"A-1"`

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-789
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Render_html makes the injected graph HTML-safe for embedding

> `render_html` makes the injected graph HTML-safe for embedding inside `<script>` by
> applying three escapes in order. All three are V8 no-ops: a backslash is silently
> ignored before `/`, `!` and `-`.

Scenario: a field carrying all three dangerous sequences is fully escaped and still parses
  Given  a node title `"</script><!--x-->"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output has none of `</`, `<!--`, `-->` raw, and re-parsing the blob as JSON
         yields the original title unchanged

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-790
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# </ → <\/ — prevents </script> from closing

> `</`   → `<\/`   — prevents `</script>` from closing the element early

Scenario: a </script> breakout attempt in a field is neutralized
  Given  a node id `"a</script><img src=x>"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output has no raw `"</script><img"` and contains `"<\\/script>"` instead

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-791
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# <!-- → <\!-- — prevents the HTML5 parser

> `<!--` → `<\!--` — prevents the HTML5 parser entering "script data escaped" state

Scenario: a literal <!-- inside a field is escaped to <\!--
  Given  a node contract clause `"discusses HTML injection via <!-- markers"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output contains `"<\\!--"` and no raw `"<!--"` inside the injected blob,
         keeping `window.__REQMAP_DATA__` parseable instead of null

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-792
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# --> → -\-> — prevents prematurely closing that

> `-->`  → `-\->`  — prevents prematurely closing that state if somehow entered

Scenario: a literal --> inside a field is escaped to -\->
  Given  a node title containing the literal sequence `"-->"`
  When   `_inject_viewer(template_text, data)` runs
  Then   the output contains `"-\\->"` and no raw `"-->"` inside the injected blob

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-794
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Render_html also escapes U+2028 and U+2029 to their

> `render_html` also escapes U+2028 and U+2029 to their `\\u2028`/`\\u2029` forms. Those
> two characters end a line in JavaScript but not in JSON, so unescaped they turn the
> assignment into an unterminated string on any engine older than ES2019. The escaped
> forms denote the same characters in JSON, so the parsed graph is unchanged.

Scenario: U+2028/U+2029 in a title are escaped and still round-trip through JSON
  Given  a node title containing U+2028 and a contract clause containing U+2029
  When   `_inject_viewer(template_text, data)` runs
  Then   neither raw character appears in the output, the literal 6-character
         sequences \u2028 and \u2029 do, and re-parsing the blob as
         JSON yields the original title unchanged

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-795
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# The viewer ranks nodes by longest dependency path

> The viewer ranks nodes by longest dependency path, so `depends_on` edges flow one way.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-796
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# The viewer excludes a cycle-closing edge from that

> The viewer excludes a cycle-closing edge from that ranking, and still draws it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-797
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# No node ranks higher than the number of

> No node ranks higher than the number of nodes, whatever the registry's shape.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-798
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# A node carries the acceptance section twice: accept

> A node carries the acceptance section twice: `accept`, the labelled Given/When/Then
> block as the author wrote it, and `acc`, the same criteria folded to one line each.

Scenario: a map node carries both the raw accept block and the folded acc list
  Given  a confirmed requirement with a labelled `## Cases` block of two criteria
  When   `_build_map_data` builds the node
  Then   `node["acc"]` has two folded entries and `node["accept"]` holds the raw block

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-799
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# The viewer renders accept — one line per

> The viewer renders `accept` — one line per line, as authored. `acc` is for search and
> counting, never the thing a reader is shown when the authored block exists.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-800
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# The viewer renders its own UI chrome in

> The viewer renders its own UI chrome in English by default.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-801
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# A locale control in the viewer's top bar

> A locale control in the viewer's top bar switches that chrome to another bundled
> language.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-802
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# Requirement content is never translated: id, title, intent

> Requirement content is never translated: id, title, intent, contract clauses, acceptance
> criteria and member paths stay in the language their author wrote them in.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-803
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# The engine's own vocabulary is never translated either

> The engine's own vocabulary is never translated either: `status`, `layer`, tag-role and
> severity values stay the literal strings the requirement files and the gate use.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-804
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# A chrome string with no entry in the

> A chrome string with no entry in the active locale falls back to its English text.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-VIEWER-805
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
superseded_by:
---

# The reader's chosen locale is remembered on their

> The reader's chosen locale is remembered on their machine and is never written into the
> generated file, so `_map.html` stays byte-identical whatever anyone last selected.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
