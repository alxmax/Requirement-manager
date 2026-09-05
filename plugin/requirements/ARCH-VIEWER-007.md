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
- The viewer turns a requirement's `[[ID]]` cross-references into navigation, and states only header fields the export actually carries. [[REQ-VIEWER-944]]
- The viewer's registry tally is the control that scopes its outline, and the scope it applies is always visible and clearable. [[REQ-VIEWER-945]]
- The viewer documents the engine's own commands, in the reader's language, from the list the map carries. [[REQ-VIEWER-964]]
- The viewer shows every open signal in one inbox, keeping what a human asked distinguishable from what the engine derived. [[REQ-VIEWER-966]]
- The viewer shows the engine's health and design readings as two rings in the rail, displaying the numbers it was given rather than computing its own. [[REQ-VIEWER-969]]
- The viewer lists the engine's code-review candidates in a tab of their own, kept out of the count of what is open about the corpus. [[REQ-VIEWER-977]]

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

## Context
**Notes**
- `lint_exempt: file-spread` — ranking and acceptance rendering are one obligation about
  what the map export hands the viewer, and it is enforced where the data is built and again
  where it is drawn. The spread is the trace of one rule, not several.
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
---
id: REQ-VIEWER-944
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Cross-references and header fields in a rendered spec

## Description
> Authors write `[[REQ-CHECK-828]]` in a clause to point at the requirement that details it.
> Rendered literally, that is a pair of brackets that leads nowhere — on this corpus every
> architecture requirement carries several. The same document also used to print a frontmatter
> block including `owner:`, a field the engine has never exported, so every repo but the one it
> was hard-coded from read someone else's name.

Every bullet below is binding.
- A `[[ID]]` cross-reference in requirement prose renders as the bare id, without its brackets.
- When the loaded map holds that id, the reference is an activatable control that opens that
  requirement; keyboard activation does the same thing as a click.
- When the loaded map does not hold it, the id renders as marked text that navigates nowhere —
  a dangling reference is reported, not hidden.
- Requirement prose is HTML-escaped before either transform runs, so no authored text can reach
  the DOM as markup.
- A rendered document states only header fields the export carries; a field the engine does not
  emit is absent rather than invented.

## Cases
CASE-1 — a resolvable cross-reference becomes a control
  Given  a clause containing `[[ID]]` and a registry holding that id
  When   the requirement's document is rendered
  Then   the id appears as an activatable link carrying that id, and the brackets are gone

CASE-2 — a dangling cross-reference is marked, not linked
  Given  a clause containing `[[ID]]` and a registry that does not hold that id
  When   the requirement's document is rendered
  Then   the id appears as marked text with no link control

CASE-3 — escaping still wins over both transforms
  Given  a clause containing HTML markup alongside a cross-reference
  When   the requirement's document is rendered
  Then   the markup appears escaped and only the cross-reference is a control

CASE-4 — the header invents no field
  Given  a requirement rendered from an engine export, which carries no `owner`
  When   its document header is rendered
  Then   no owner is shown
---
id: REQ-VIEWER-945
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Scoping the outline from the registry tally

## Description
> The rail's registry tally answers "how many are drafts?" and then leaves you to find them by
> hand. The number and the rows behind it are the same query, so the number is the natural place
> to ask for them — as long as what it applied stays visible, or a reader is left with a filtered
> list and no idea why.

Every bullet below is binding.
- Each row of the registry tally scopes the outline to the slice it counts, and opens the outline
  if another surface was showing.
- The `orphan` row scopes to the gate's own error condition — an enforced requirement with no
  `implements:` member — which is a computed state, not a status value.
- An applied scope is rendered as an active filter chip, and clearing that chip, or clicking the
  same tally row again, restores the full outline.
- The scope applies to the first render, not only after one — the outline is never painted
  unfiltered when a scope was requested.

## Cases
CASE-1 — a tally row narrows the outline
  Given  the outline rendered with the `draft` slice requested
  When   its rows are counted
  Then   fewer rows are shown than with no slice requested

CASE-2 — the orphan row scopes to the gate's condition, not a status
  Given  a registry in which every enforced requirement has an `implements:` member
  When   the outline is rendered with the `orphan` slice requested
  Then   no row matches, and the empty state says so

CASE-3 — the applied scope is visible and clearable
  Given  the outline rendered with a slice requested
  When   its filter row is drawn
  Then   the chip naming that slice is drawn active

---
id: REQ-VIEWER-964
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# The command reference, in the reader's language

## Description
> Someone reading the map to understand a repository is one question away from "how do I run this?"
> — and the answer used to live only in a README they would have to go and find. The viewer shows
> the commands themselves, grouped by the moment of work they belong to.

Every bullet below is binding.
- The viewer renders one entry per command the map carries, grouped by authoring, building and
  reading, showing the invocation, its summary and each flag with its help text.
- A command's summary is shown in the reader's chosen language, falling back to the engine's own
  English when that language has no entry for it.
- Flag names are never translated: they are literals the reader types.
- A map carrying no command list renders a named empty state saying how to regenerate one, never a
  blank page.

## Cases
CASE-1 — the commands are listed with their flags
  Given  a map carrying a command list
  When   the command reference is rendered
  Then   each command appears with its invocation, its summary and one row per flag

CASE-2 — the summary follows the chosen language
  Given  the Romanian locale and a command with a Romanian summary
  When   the reference is rendered
  Then   the Romanian summary is shown and the English one is not

CASE-3 — an untranslated command falls back to English
  Given  a locale with no entry for one command
  When   the reference is rendered
  Then   that command shows the engine's English summary rather than blank

CASE-4 — a map with no command list says so
  Given  a map produced before the list existed
  When   the reference is rendered
  Then   a named empty state appears naming the command that regenerates it
---
id: REQ-VIEWER-966
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# One inbox, with the origin of a signal as a tab

## Description
> Two inboxes stood side by side because one of them used to be six hundred rows of draft noise,
> and a question a human had written down was invisible in there. That corpus is gone, and the
> noise is collapsed where it occurs. What is worth keeping is not the second screen but the
> distinction it protected: a warning the engine computed and a question a person wrote are
> different news, and a reader should be able to ask for one without reading the other.
> See [ADR-0028](../../docs/adr/0028-one-inbox-for-every-open-signal.md).

Every bullet below is binding.
- A requirement's open `## Verify intent` questions appear in the problems inbox as rows of their
  own kind, carrying the question text and the step that closes it.
- The authored placeholder is not a question, exactly as it is not one for the engine's own
  digest: a requirement that recorded nothing contributes no row.
- The inbox offers the origin as a filter of its own, so "what did a human ask?" is one click and
  never a severity ranked among computed signals.
- A question sorts above an unreviewed draft and below an error or a warning.
- The rail badge for authored questions is hidden at zero rather than rendered as a proud `0`.

## Cases
CASE-1 — an authored question is a row in the inbox
  Given  a requirement carrying one real Verify-intent question
  When   the problems inbox is computed
  Then   it holds a row for that requirement, of the question kind

CASE-2 — the placeholder is still not a question
  Given  a requirement whose Verify-intent section holds only the authored placeholder
  When   the inbox is computed
  Then   no question row is raised for it, whatever else its state raises

CASE-3 — authored questions are counted apart from computed signals
  Given  an inbox holding both kinds of row
  When   the questions are counted for the rail badge
  Then   only the authored ones are counted

CASE-4 — the origin is offered as a filter, with the question text shown
  Given  an inbox holding a question row
  When   it is rendered
  Then   a tab for questions is offered and the question's own text is displayed
--------------------


---
id: REQ-VIEWER-969
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Two engine-emitted readings in the rail

## Description
> `reqmap.py gate --risk` opens with two numbers — how much of the corpus is green, and how much
> of the code is free of design candidates — and the viewer showed neither. They belong
> where a reader already looks for the shape of the repo: the rail, under the navigation.
> The viewer displays the records the map hands it; recomputing either one here is what
> would let the terminal and the browser report different repos.

Every bullet below is binding.
- The rail renders one ring per reading, showing the score, its label and the fraction
  behind it, from the `health` and `design` records the map carries.
- The health ring is coloured by band, since it is a verdict: green while at or above 90,
  amber down to 60, red below. The design ring stays in one neutral ink — that score is
  advice the gate never enforces, and a red ring would read as a failure the repo does not
  have.
- The health ring opens the Problems inbox, where the reasons behind the score are listed.
  The design ring is not a control, because there is no view to open.
- A map carrying neither record renders no ring at all. An older map has neither key, and a
  reading invented client-side would be worse than an absent one.
- Both labels and both captions follow the chosen interface language, like the rest of the
  chrome.

## Cases
CASE-1 — the rings show the numbers the engine emitted
  Given  a map carrying a health record of 39 of 50 and a design record of 7 of 30
  When   the rail renders
  Then   both scores and both fractions appear as given, with nothing recomputed

CASE-2 — the health band follows the score
  Given  a health score of 78
  When   the rail renders
  Then   the health ring is drawn in the partial tone, not the green one

CASE-3 — an older map renders no ring
  Given  a map carrying neither a health nor a design record
  When   the rail renders
  Then   no gauge is present in the output

CASE-4 — only the verdict is a control
  Given  both records are present
  When   the rail renders
  Then   the design row is marked static and carries no click target, while the health row does

CASE-5 — the labels follow the interface language
  Given  the interface language is Romanian
  When   a label and a caption are translated
  Then   both come back in Romanian, numbers interpolated unchanged

---
id: REQ-VIEWER-977
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# The advisory design tab

## Description
> The rail already showed a design score, and a reader who wanted to know which shapes
> cost the missing points had to leave the viewer for a terminal. The candidates now
> travel in the map, so the Problems screen lists them — in a tab of their own, because
> they are the only rows here that are about a file rather than a requirement, and the
> only ones that gate nothing.

Every bullet below is binding.
- `ProblemsView` offers a `Design` tab, labelled with the number of candidates the map carries, and offers it only when the map carries at least one.
- The tab groups candidates by pillar, shows each one's kind, name, detail and `file:line`, and prints each kind's advice once per group — the same shape the CLI prints.
- Design candidates are absent from the `All` tab and from every severity count, so the inbox keeps reporting what is open about the corpus.
- The tab states that a candidate is advisory and never enters the gate, so a reader does not mistake the list for a build failure.
- A map written before the engine carried candidates leaves the tab unoffered rather than rendering an empty one.

## Cases
CASE-1 — the tab appears with its count
  Given  a map whose `design` record carries two candidates
  When   `ProblemsView` renders
  Then   a `Design` tab is offered showing the count 2

CASE-2 — an older map offers nothing
  Given  a map whose `design` record carries a score but no candidates
  When   `ProblemsView` renders
  Then   no `Design` tab is offered

CASE-3 — the inbox is unchanged
  Given  a map carrying both corpus signals and design candidates
  When   the open signals are computed
  Then   no computed row carries a design severity, and the `All` count is the corpus count alone
