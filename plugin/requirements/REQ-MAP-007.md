---
id: REQ-MAP-007
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
satisfies: [NEED-SSOT-001]
superseded_by:
milestone: v1.04
---

# Requirement map (Mermaid MD + JSON)

> A list of requirement files tells you what exists but not how it all connects. This
> draws the picture: which capability depends on which, what has code, what is at risk —
> as Mermaid diagrams you can read on GitHub and a JSON graph any front-end can consume.
> It turns the registry into something a person can take in at a glance.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a node          one requirement, as drawn in a diagram or listed in the graph.
     an edge         one `depends_on` link between two requirements.
     an area         the group a requirement belongs to: its `area:` field, or the
                     first part of its id when that field is absent.
     a bus node      a `layer: bus` requirement — a foundation many others use.
     a hub           a requirement many others depend on (high fan-in).
     a risk signal   a warning the engine derives about a requirement, such as
                     "confirmed but no code links to it". -->

**What it generates**
- `map` generates two files under `requirements/`: `_map.md` and `_map.json`.
- `_map.md` holds Mermaid diagrams for static GitHub/GitLab rendering.
- `_map.json` holds a `{engine_version, repo, nodes, edges, todos}` graph for an
  external front-end.
- Both files are derived views. They are regenerated, never edited.

**What `_map.json` carries**
- `_map.json` carries one node per requirement and one edge per `depends_on`.
- Each node carries its requirement's id, layer, status, area, title, intent,
  Contract/Verify-intent/Notes bullets, acceptance, members (`role`/`loc`), `deps`,
  `used_by`, and risk signals.
- That is the same `{nodes, edges}` shape the diagrams are built from.
- `_map.json` carries a top-level `repo` field: a best-effort `owner/repo`, else the
  repo directory name, else null.
- `repo` identifies the project the map describes, for display in the viewer header.
- `repo` is derived from the git remote, so it differs across forks and clones. It is
  therefore excluded from the `map --check` freshness diff.
- Resolving `repo` never raises and never blocks map generation, because git may be
  absent or the tree may not be a checkout.
- `_map.json` carries a top-level `todos` array, derived from `TODO.md` via
  `_parse_todos`, so the viewer's Roadmap tab can show planned work alongside
  requirements.

**How a contract is read**
- Reading a requirement's clauses folds a wrapped line back into the clause above it, so a
  multi-line clause is never truncated to its first physical line.
- A clause-group label groups the clauses below it: a bold-only line written flush left.
  A label is a heading, not a clause, and never folds into the clause above.
- Position decides a label, not the bold markers alone. An indented wrapped line folds
  even when it opens and closes on bold spans, so a two-part clause keeps both halves.

**What the diagrams show**
- `_map.md` contains exactly 4 Mermaid code blocks: System Map, Req→Code, Dependencies
  and Risk.
- Each of those 4 blocks carries a legend.
- A node's area is its `area:` field, or its id prefix when that field is absent.
- The System Map groups nodes into per-area subgraphs, and collapses a single-node area
  into a `misc` box.
- The System Map omits a `depends_on` edge whose target is a bus node or a high-fan-in
  hub.
- The Dependency Map is area-level: one node per area, carrying a capability count.
- The Dependency Map draws an edge A→B when some capability in A depends on one in B.
  Per-capability hub edges are not drawn.
- Req→Code colors an enforced-but-unlinked requirement red, and a baseline or draft
  not-yet-linked one muted grey.
- Req→Code collapses multiple members in one file to a min–max line range.
- The Risk diagram shows only requirements with at least one risk signal
  (confirmed with zero members; `draft`/`baseline`; ≥3 dependents).
- The Risk diagram pairs each of them with a scripted recommendation.
- A `draft`'s open verify-intent question is suppressed, subsumed by its `unreviewed`
  signal, so a draft is not double-flagged.
- That dedup lives in `_risk_signals`, shared with the `next` worklist.

**Safety**
- All requirement-derived text is JSON-encoded in `_map.json`, which neutralizes any
  hostile id, title or body by construction. There is no markup context to break out of.

**What is out of scope**
- The self-contained HTML viewer ([[REQ-VIEWER-007]]) and the GitHub Pages publish+gate
  ([[REQ-PAGES-021]]) are separate capabilities. They consume this map's `_map.json` and
  `_map.html`.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- `export` is a thin alias that writes only `_map.json` (or to stdout / `--out PATH`) for
  ad-hoc piping; `map` writes `_map.md` + `_map.json` (and, via [[REQ-VIEWER-007]], `_map.html`
  when the viewer template is present).
- `_map.json` is the committed source of the map's data; the diagrams in `_map.md` and the
  inlined viewer are derived from it and regenerated by `map`.

## HOW — Acceptance (= tests)
AC-1
  Given  the corpus
  When   `map` runs
  Then   the generated files contain one node per requirement and one edge per `depends_on`

AC-2
  Given  the generated `_map.md`
  When   it is inspected
  Then   it contains exactly 4 Mermaid code blocks, each with a legend

AC-3
  Given  the generated `_map.json`
  When   it is parsed
  Then   it yields `{engine_version, repo, nodes, edges, todos}` with one node per requirement carrying
         its members and risk signals. The `repo` field is the project's `owner/repo` (or
         directory name, or null) and is omitted from the freshness comparison.

AC-4
  Given  the System Map diagram
  When   it is rendered
  Then   nodes group into per-area subgraphs, single-node areas collapse into `misc`, and edges
         whose target is a bus node are omitted

AC-5
  Given  the Dependency Map diagram
  When   it is rendered
  Then   it is area-level: one node per area (with a count), an edge A→B when some capability
         in A depends on one in B; per-capability hub edges are not drawn

AC-6
  Given  the Risk diagram
  When   it is rendered
  Then   it shows only requirements with at least one risk signal, each with a scripted recommendation

AC-7
  Given  a requirement id/title containing a quote or `</script>`
  When   `map` runs
  Then   it round-trips through `_map.json` as data (no injection) and a node with no members
         reports an empty member list

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py map`. On GitHub the System Map shows AUTH-LOGIN-001 as a box wired to
  the session capability it depends on, coloured amber because it has no tests yet. One glance
  tells her where the gap is.

## WHERE — Current implementation
- `cmd_map`, `cmd_export`, `render_md`, `render_json`, `_build_map_data`, `_build_json_text`, `_repo_name`, the `_mermaid_*` generators in `reqmap.py`. (HTML viewer moved to [[REQ-VIEWER-007]]; Pages publish/gate to [[REQ-PAGES-021]].)

## Links
- Used by: (auto)
## Members in code (auto)
