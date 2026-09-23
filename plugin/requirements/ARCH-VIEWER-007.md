---
id: ARCH-VIEWER-007
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.04
depends_on: [ARCH-MAP-007]
satisfies: [SYS-VISUAL-106]
---

# Self-contained HTML map viewer

## Description
> What the viewer shows once it is open: the outline, a requirement's spec, the
> map, the roadmap and its plan, the inbox of open signals, the commands. The file it
> ships in, and the escaping that makes that file safe, is
> [[ARCH-VIEWERFILE-074]].

Every bullet below is binding.
- The viewer ranks nodes by longest dependency path so `depends_on` edges flow one way, and renders a node's acceptance criteria as the author wrote them, not folded to one line. [[REQ-VIEWER-942]]
- The viewer renders its own UI chrome in a chosen language while requirement content and engine vocabulary stay exactly as authored. [[REQ-VIEWER-943]]
- The viewer turns a requirement's `[[ID]]` cross-references into navigation, and states only header fields the export actually carries. [[REQ-VIEWER-944]]
- The viewer's outline applies a requested scope from its first render, and the scope it applies is always visible and clearable. [[REQ-VIEWER-945]]
- Each row of the viewer's registry tally requests the slice it counts and brings the outline forward. [[REQ-VIEWER-1082]]
- The viewer draws the shipped months the engine emitted on the plan's own timeline, and a month opens to every release in it. [[REQ-HISTORY-1081]]
- The viewer documents the engine's own commands, in the reader's language, from the list the map carries. [[REQ-VIEWER-964]]
- The viewer shows every open signal in one inbox, keeping what a human asked distinguishable from what the engine derived. [[REQ-VIEWER-966]]
- The viewer shows the engine's health and design readings as two rings in the rail, displaying the numbers it was given rather than computing its own. [[REQ-VIEWER-969]]
- Each rail reading opens the rows behind its number in Problems, filterable by the reason each row is there. [[REQ-VIEWER-1084]]
- The viewer lists the engine's code-review candidates in a tab of their own, kept out of the count of what is open about the corpus. [[REQ-VIEWER-977]]
- The roadmap chart is readable at a corpus's real width: the reader scales it and chooses how tightly it packs, and both choices survive a reload. [[REQ-VIEWER-984]]
- The roadmap has one lane, Implementations, holding every open `TODO.md` item and every milestoned requirement whatever its `lane:` says. [[REQ-VIEWER-995]]
- Selecting a plan bar opens a detail panel carrying the note its author wrote under the matching `ROADMAP.md` item. [[REQ-VIEWER-999]]
- The Versions view lists the same bars as the Plan chart, each in its milestone's column. [[REQ-VIEWER-999]]
- The plan chart draws every bar where no neighbour covers it, keeps the lane names in place while it scrolls sideways, and ties each bar to its days with guides. [[REQ-PLANSTACK-1012]]
- Under the week row, the plan chart labels every day with its `day/month`. [[REQ-PLANDAYS-1021]]

## Cases
CASE-1
  Given  a registry whose `depends_on` edges form a cycle
  When   the layout is computed
  Then   every node is placed, no rank exceeds the node count, and the closing edge is drawn

CASE-2
  Given  the viewer rendered with a non-English locale selected
  When   a requirement's spec is shown
  Then   the section headers appear in that language while the requirement's own title,
         contract and acceptance text stay exactly as authored, and `status` / `layer`
         values stay literal

CASE-3
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
- Split on 2026-09-22 (ADR-0050) along the seam this note used to defer: the ARTIFACT
  (`_map.html`, its template and the escaping) is [[ARCH-VIEWERFILE-074]]; what the file
  RENDERS stays here. The `over-scoped` and `ac-count-high` exemptions left with it.
- `lint_exempt: file-spread`: the members are one engine function plus the viewer's source
  tree (`app/src/**`, its vendoring script and single-file build config). A UI is many files
  by construction; they are built into ONE artifact, so the spread is not diffuseness.
- The single-file build (`app/` → `npm run build:viewer`) is vendored beside the engine as
  `scripts/_map_viewer.html` with a `<!--REQMAP_DATA-->` marker; the stdlib engine swaps the
  marker for the inline data, so it ships a rich UI without itself depending on Node/npm.
- `_map.html` is a regenerable artifact (template + `_map.json`), not committed; rebuild with
  `map`. `_map.json` (owned by [[ARCH-MAP-007]]) is the committed source of its data.
- Publishing this viewer to a repo's GitHub Pages folder and gating that copy is a separate
  capability — see [[ARCH-PAGES-021]].

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py sync`, then double-clicks `_map.html`. It opens in her browser with the
  whole requirement graph inlined — no server — even though the engine itself is stdlib-only.

**Current implementation**
- `render_html`, `_inject_viewer`, `_viewer_template_path` in `reqmap.py`; `render_html` is
  called by `cmd_map` after `_map.json`/`_map.md` are written.
- `check_viewer_data_sync` in `reqmap_engine/viewer.py`, run by RM017 (`gate`): a warn-only
  comparison of the viewer's hand-authored fallback fixture, `app/src/lib/baked.json` (read as
  JSON; `data.js` imports it), against the live registry, so a stale demo entry is flagged
  rather than silently shown forever. A fixture entry marked `demoOnly: true` is skipped: the demo dataset deliberately invents an
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
id: REQ-VIEWER-942
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
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
- A node carries the acceptance section once, as `accept`, the labelled Given/When/Then
  block as the author wrote it. The viewer derives `acc`, the same criteria folded to one
  line each, from it, criterion for criterion as the engine folds them.
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

CASE-4 — the viewer folds the raw accept block itself
  Given  a map node whose `accept` holds a labelled `## Cases` block of two criteria and
         which carries no `acc`
  When   the viewer adapts the node
  Then   the adapted requirement's `acc` has two folded entries, each `CASE-N — ` followed
         by its Given/When/Then text on one line

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
milestone: v3.2
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
milestone: v4.2
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
milestone: v4.2
satisfies: [ARCH-VIEWER-007]
---

# Scoping the outline from the registry tally

## Description
> The rail's registry tally answers "how many are drafts?" and then leaves you to find them by
> hand. The number and the rows behind it are the same query, so the number is the natural place
> to ask for them — as long as what it applied stays visible, or a reader is left with a filtered
> list and no idea why.

Every bullet below is binding.
- The outline accepts a requested slice: a status value, or `orphan`.
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
milestone: v4.2
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
milestone: v4.2
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
milestone: v4.2
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
- Both rings are controls: the health ring opens the Problems inbox on its Health tab, the
  design ring on its Design tab, where the rows behind each number are listed.
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

CASE-4 — both readings are controls
  Given  both records are present
  When   the rail renders
  Then   both rows are buttons and neither is marked static

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
milestone: v5.6
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
- Design candidates count as problems — each is one computed signal, so the rail's Problems number includes them — but they are listed only under the `Design` tab: none is a row of `All`, of `Warnings` or of any other severity tab, and none opens a requirement.
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

CASE-3 — the candidates are counted, and listed only in their tab
  Given  a map carrying both corpus signals and two design candidates
  When   the open signals are computed and the `All` tab renders
  Then   exactly two computed signals carry the `design` signal at their own severity, each with its `file:line`; neither is rendered in `All`; and a map with no candidates adds none


--------------------


---
id: REQ-VIEWER-984
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-VIEWER-007]
---

# Reading a roadmap wider than the screen

## Description
> One column per milestone and a chip carrying the full requirement title made the chart
> as wide as its longest title times its column count. At 42 milestones that is over
> 15,000px, so three versions were visible and the rest was panning. Scaling and packing
> are two different answers and a reader needs both: zoom shrinks the type along with
> everything else, while a tighter chip keeps the type crisp and gives up the tail of the
> title instead.

Every bullet below is binding.
- The chart scales through the CSS `zoom` property, so its scroll extent shrinks with its
  contents. A `transform` would leave the container at full size and make the reader pan
  across empty space to reach the last column.
- The compact density truncates a chip's title and keeps the full text in the chip's
  `title` attribute, rather than scaling the chip down. Nothing a reader can only see by
  hovering is lost, because the tooltip was already there.
- With nothing stored and nothing passed, the chart renders at 100% and `comfy` — the
  view a reader had before either control existed.
- `initialZoom` and `initialDensity` let a host or a render test preset the two controls;
  absent both, the reader's last choice is read from browser storage, and a storage that
  is missing or throws yields the defaults rather than an error.

## Cases
CASE-1 — the chart scales with CSS `zoom`, not with a transform
  Given  `RoadmapView` rendered with `initialZoom` 40
  When   the markup is inspected
  Then   the chart's wrapper carries `zoom:0.4` and no `transform`, so the scroll extent
         scales with the content rather than staying at full width

CASE-2 — compact truncates the title and keeps it in the tooltip
  Given  `RoadmapView` rendered with `initialDensity` `compact`
  When   the markup is inspected
  Then   a chip's label carries `text-overflow:ellipsis` under a max width, and the chip
         still carries the untruncated title as its `title` attribute

CASE-3 — the defaults are the view that existed before the controls
  Given  `RoadmapView` rendered with neither prop and no stored preference
  When   the markup is inspected
  Then   the zoom control reads `100%`, the wrapper carries `zoom:1`, and no label
         is truncated

## Context
**Notes**
- The wheel handler is deliberately NOT covered here, and the omission is the honest one:
  the render harness is `renderToString`, which has no DOM and dispatches no events, so a
  case asserting `ctrl`+wheel would assert nothing. Two failure modes live there and were
  each found by driving the built viewer by hand: a same-frame flick collapsing into one
  zoom step, and the browser's own page zoom firing because a React `onWheel` cannot
  `preventDefault`. Read the absence of a case as untested, not as passing.
- The zoom range is 40-150%. The floor is where a 42-column chart fits a laptop screen at
  compact density; the ceiling is a legibility aid, not a use case anyone asked for.

**Current implementation**
- `app/src/views/RoadmapView.jsx` — `RoadmapView`, `ZoomControl`, the `DENSITY` table.
- `app/scripts/ssr-smoke.jsx` — the three cases above.


--------------------


---
id: REQ-VIEWER-995
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-VIEWER-007]
---

# The roadmap has one lane, and it is named for what the chips are

## Description
> The Y axis carried four swim lanes — bus, feature, need, ops — which is the engine's own
> taxonomy, a requirement's position in the graph. That answered a question no reader was
> asking, so it became two: Bugs and Features. Bugs then rendered empty, and stayed empty,
> because nothing on this roadmap is a defect — the items are work that was not specified
> up front, which is a different thing. An axis with one populated value sorts nothing and
> still costs a row, so the lane stops classifying and names what the chips are.

Every bullet below is binding.
- The roadmap renders exactly one lane, labelled `Implementations`, and no other lane
  label appears.
- Every open `TODO.md` item renders in it, whatever its `lane` field says — `bug`,
  `feature` and the older `bus`/`ops` values all still parse and are never rejected. A
  completed item (`[x]`) still renders nowhere.
- Every requirement with a `milestone:` that is not deprecated renders in it.
- `lane` stays in the engine's output. It is still parsed from `TODO.md` and still emitted
  in `_map.json`, so a repo that files its items by lane loses the split and nothing else,
  and no engine data changes for this.
- A milestone that `TODO.md` groups anything under renders as a column, complete items
  included. A version whose work has all shipped is a finished column, not a missing
  one; the chips inside it stay filtered to the open items.

## Cases
CASE-1 — one lane, named Implementations
  Given  a registry with at least one milestone
  When   the roadmap renders
  Then   exactly one lane label is rendered and it reads `Implementations`

CASE-2 — every lane value lands in that one lane
  Given  open `TODO.md` items marked `lane: bug`, `lane: ops` and `lane: feature` under one
         milestone, and a completed item beside them
  When   the roadmap renders
  Then   all three open titles appear and the completed one does not

CASE-3 — a milestoned requirement lands in it too
  Given  a confirmed requirement carrying that same milestone
  When   the roadmap renders
  Then   its title appears in the lane

CASE-4 — a milestone whose every item is complete still gets a column
  Given  a `TODO.md` milestone whose items are all completed (`[x]`), and no requirement
         carrying it
  When   the roadmap renders
  Then   that milestone's column is rendered, and it holds no chips

--------------------


---
id: REQ-VIEWER-999
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.7
satisfies: [ARCH-VIEWER-007]
distinct_from: [REQ-UNPLANNED-1024, REQ-ROADMAP-998, ARCH-ROADMAP-038]
---

# A plan bar opens the note its author wrote in ROADMAP.md

## Description
> A Gantt bar is a title and two dates. It says when something is scheduled and nothing
> about what it is, so the reader who does not already know goes to look somewhere else —
> and the place they would look, `ROADMAP.md`, already holds the answer: the lines an
> author writes under an item are where the reasoning lives. The Horizons mode that used
> to render those items as three columns is gone; a plan with dates and a plan with
> horizons were two pictures of one file, and the dated one is the one people read.

Every bullet below is binding.
- The panel reads the `roadmap` items the export carries (REQ-ROADMAP-998) and parses
  none of its own.
- Selecting a plan bar opens a detail panel below the chart carrying that bar's title, its
  milestone, its horizon when one is known, and the `context` of the matching roadmap item.
- A bar matches a roadmap item by `req:`, the one id both sides carry.
- A bar no roadmap item claims opens the panel with its own title and dates, and no note.
- Context written as an HTML comment renders as its text, because the comment markers are
  how a plan file hides a note from a Markdown reader, not part of what the note says.
- The panel names the requirement when the bar carries a `req` the registry has, and opens
  it on request; an id the registry does not have is shown as plain text.
- Nothing renders a Now / Next / Later column: the Roadmap tab offers Versions and Plan.
- The Versions view lists each bar in the column of its `milestone`, the same list the Plan
  chart draws, and reads no `milestones[].items[]`.

## Cases
CASE-1 — selecting a bar shows the note written under its roadmap item
  Given  a bar carrying `req: AREA-A-001` and a roadmap item with the same `req:` whose
         context reads `two sentences of why`
  When   the reader selects that bar
  Then   a panel below the chart shows the bar's title and `two sentences of why`

CASE-2 — a bar with no matching item still opens, with no note
  Given  a bar carrying no `req`, and a roadmap list that does not mention it
  When   the reader selects that bar
  Then   the panel shows its title, milestone and dates, and no note section

CASE-3 — an HTML-comment context renders as text
  Given  a roadmap item whose context is `<!-- the reason -->`
  When   its bar is selected
  Then   the panel shows `the reason` and neither comment marker

CASE-4 — the Horizons mode is gone
  Given  an export whose `roadmap` carries one `now`, one `next` and one `later` item
  When   the Roadmap tab renders
  Then   the only modes offered are Versions and Plan, and no Now/Next/Later column exists

CASE-5 — a bar appears in its version's column
  Given  a plan with a bar on milestone `v99.7` and an `items` list on milestone `v99.8`
  When   the Versions view renders
  Then   the `v99.7` column lists the bar, and the `items` text appears nowhere

## Context
**Notes**
- `distinct_from: REQ-UNPLANNED-1024` - `REQ-UNPLANNED-1024` is an engine line counting unscheduled items; this is the viewer panel for one selected bar.
- `distinct_from: REQ-ROADMAP-998` - `REQ-ROADMAP-998` parses ROADMAP.md; this renders what it parsed.
- `distinct_from: ARCH-ROADMAP-038` - `ARCH-ROADMAP-038` is the engine's roadmap capability; this is its viewer side.

---
id: REQ-PLANSTACK-1012
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Bars are stacked by what is drawn, not by what is scheduled

## Description
> Two bars a week apart do not overlap as dates, so they were put on one row — and then
> painted 23px on top of each other, the first one's title vanishing under the second.
> The chart floors a bar at a readable width, and at 7px a day a week drew 43px and was
> floored to 72: nearly three days of borrowed room. A wider day gives a week 71px of its
> own and takes it out of the floor entirely, which leaves the floor to the bars that have
> no label room at any scale. The row chooser still has to know what the renderer will
> draw, because the renderer cannot know what the chooser meant — it draws what it is given.

Every bullet below is binding.
- One function answers where a bar is drawn and how wide.
- The renderer reads that function, as does the row chooser; neither computes its own.
- `stackBars` puts two bars on different sub-rows when their DRAWN boxes intersect, even
  where their dates do not.
- Two bars far enough apart that the floor cannot make them touch still share a row, so
  the lane grows only where two bars would otherwise overlap.
- The vertical guides mark the work: a solid rule from the centre of each bar's start day on
  the ruler down to the bar, and a dotted one from its end day, each stopping at the bar; a
  version's rule runs from its due day down to its pill. `today` keeps its pill on the ruler, the
  milestones keep theirs there or in the release lane, and neither rules a line through the lanes.
- The track fills the width the lane column leaves, and keeps its true scale when the
  plan is longer than the viewport.
- A bar's title wraps, to a declared line limit, and the bar is tall enough to hold it.
- The lane column stays in place while the chart scrolls sideways, which means no
  ancestor of it may declare an overflow: an ancestor that does becomes its scrollport,
  and a scrollport that never scrolls never lets its sticky child stick.

## Cases
CASE-1 — two one-day bars on consecutive days take separate rows
  Given  two one-day bars a day apart, each floored to the minimum bar width
  When   the Plan renders
  Then   they carry different sub-rows, and stacking them by date alone would not

CASE-2 — a week-long pair a week apart shares one row
  Given  two seven-day bars starting seven days apart
  When   the Plan renders
  Then   one row holds both, because neither is floored and they never touch

CASE-4 — the lane column survives a sideways scroll
  Given  a plan wide enough to scroll
  When   the reader scrolls the chart sideways
  Then   the lane names stay in place, as the note panel does

CASE-3 — the guides mark the work, not the dates
  Given  a plan carrying a bar and a milestone due date
  When   the Plan renders
  Then   the milestone keeps its header pill and no dashed full-height rule is drawn

---
id: REQ-PLANDAYS-1021
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# Each day on the Plan is labelled

## Description
> A week band says which week a bar falls in; placing a one-day bar or a Friday release
> needs the day itself, and counting ticks from a week's edge is how a reader gets it wrong.

Every bullet below is binding.
- Under the week row the Plan draws one cell per day, labelled `day/month` with no leading
  zero, written across within the width of one day.
- Today's label is drawn in the accent colour, and a Saturday or Sunday is fainter.

## Cases
CASE-1 — each day under the weeks is labelled day/month
  Given  a chart that covers Monday 14 September 2026 through the following Sunday
  When   the Plan renders
  Then   the days read 14/9 through 20/9, and only 19/9 and 20/9 are weekend days

CASE-2 — today stands out and a weekend recedes
  Given  a Friday that is today, a Friday that is not, and a Saturday
  When   each day's label is styled
  Then   today is in the accent colour, the other Friday is not, and the Saturday is fainter
         than the other Friday

CASE-3 — the day row spans the chart
  Given  a plan whose chart covers several weeks
  When   the Plan renders
  Then   it draws one labelled day cell per day the chart covers

--------------------


---
id: REQ-HISTORY-1081
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# The shipped months, drawn beside the plan

## Description
> The engine reads the CHANGELOG and groups it by month (REQ-HISTORY-1003); the reader
> looks at a chart. Drawing the past on the plan's own timeline, from exactly the rows
> the engine emitted, is what lets "what happened" sit next to "what is next" without a
> second, drifting copy of either.

Every bullet below is binding.
- The Plan draws one "Shipped" band row per month the engine emitted in `history`,
  labelled with that month's landmark version, left of today on the plan's own
  timeline.
- The row shows the month's headline, not its list of versions.
- With no `history` in the export, no Shipped band is drawn.
- Selecting a shipped month opens a note listing every release in it, newest first,
  each with its date and headline.

## Cases
CASE-1 — one band row per shipped month, labelled by its landmark
  Given  an export whose `history` holds two months
  When   the Plan renders
  Then   a Shipped band is drawn with one row per month, each labelled by its landmark

CASE-2 — the month's headline is shown
  Given  a month whose landmark release has a headline
  When   the Plan renders
  Then   that headline is shown on the row

CASE-3 — no history means no band
  Given  an export with no `history`
  When   the Plan renders
  Then   no Shipped band is drawn

CASE-4 — a shipped month opens to what was done in it
  Given  a month holding two releases, each with a headline
  When   the reader selects that month on the chart
  Then   a note lists both releases, newest first, each with its date and headline


--------------------


---
id: REQ-VIEWER-1082
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# A registry tally row asks for its slice

## Description
> The tally answers "how many are drafts?" and the next question is "which ones?".
> The row that counts them is the natural place to ask, from wherever the reader is:
> this is the asking half, and the outline applying the answer is REQ-VIEWER-945.

Every bullet below is binding.
- Each row of the rail's registry tally shows the count of the slice it would scope to.
- Choosing a row requests that slice and brings the outline forward, whatever surface
  was showing; choosing the same row again requests no slice.
- The row whose slice is in force is drawn pressed, and only that row.

## Cases
CASE-1 — the requested slice's row is drawn pressed
  Given  the rail rendered with the `draft` slice in force
  When   its tally is drawn
  Then   exactly one row is pressed, and it is the `draft` row

CASE-2 — each row shows its slice's count
  Given  a registry holding some drafts
  When   the rail's tally is drawn
  Then   the `draft` row shows the number of draft requirements

CASE-3 — choosing a row scopes the outline and opens it
  Given  the shell's handler for a tally row
  When   it is called with `orphan`
  Then   the slice becomes `orphan` and the outline is the surface shown


--------------------


---
id: REQ-VIEWER-1084
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-VIEWER-007]
---

# A rail reading opens the rows behind its number

## Description
> A score says how the repo is doing and nothing about what to do. The rows behind it
> are the answer, and they should be one click from the number, already narrowed to
> what the reader is looking at, never recomputed in the browser.

Every bullet below is binding.
- Choosing the health ring opens Problems on its Health tab; choosing the design ring
  opens it on its Design tab.
- The Health tab lists the `unhealthy` rows the map's health record carries, each with
  the axes it fails, followed by the `exempt_ids` it carries; its count is the sum of
  both.
- A row whose only failing axis is `not confirmed` is left out of the Health tab and
  its count, because the Review tab already lists it; the tab says how many it left
  out.
- The Health tab offers one chip per failing axis, each with its count; a chip narrows
  the list to the rows failing that axis, and `All` restores it.
- The Design tab offers one chip per pillar, each with its count; a chip narrows the
  candidates to that pillar, and `All` restores them.

## Cases
CASE-1 — each ring opens its own tab
  Given  the shell's handler for a rail reading
  When   it is called with `DESIGN`
  Then   the tab becomes `DESIGN` and Problems is the surface shown

CASE-2 — the Health tab lists the rows the engine emitted
  Given  a health record whose `unhealthy` holds one draft requirement
  When   Problems renders on its Health tab
  Then   that requirement is listed with the axis it fails

CASE-3 — an axis chip narrows the Health list
  Given  a health record with one row failing `not tested` and one failing `drift`
  When   the Health tab renders with the `drift` chip chosen
  Then   only the drifted row is listed and the `drift` chip is drawn pressed

CASE-4 — a pillar chip narrows the Design tab
  Given  candidates under two pillars
  When   the Design tab renders with one pillar's chip chosen
  Then   only that pillar's group is listed

CASE-5 — a row that only awaits confirmation stays in Review
  Given  a health record with one row failing only `not confirmed` and one failing
         `not tested`
  When   Problems renders on its Health tab
  Then   only the untested row is listed, the Health count is 1, and the tab says 1
         row only awaits confirmation
