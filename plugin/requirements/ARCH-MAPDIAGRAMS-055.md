---
id: ARCH-MAPDIAGRAMS-055
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-MAP-007]
satisfies: [SYS-VISUAL-106]
---

# Mermaid diagrams (_map.md)

## Description
> The graph is data; this is the picture. Four Mermaid diagrams that render on GitHub with
> no tooling, so someone reviewing a pull request can see the shape of the system without
> cloning anything or running the engine.

Every bullet below is binding.
- `map` generates `_map.md` under `requirements/` — exactly 5 legended Mermaid blocks, rendered from the graph and never hand-edited. [[REQ-MAPDIAGRAMS-874]]
- The Specification Hierarchy is drawn from the `satisfies:` edges, never from `depends_on:`, folding each code requirement into its parent's count instead of drawing it. [[REQ-MAPDIAGRAMS-875]]
- The System Map groups nodes into per-area subgraphs, an area falling back to the node's id prefix when `area:` is absent, and omits edges into a bus or high-fan-in node. [[REQ-MAPDIAGRAMS-876]]
- The Dependency Map is area-level: one counted node per area, one edge per cross-area dependency. Req→Code draws the system/architecture tiers only, coloured by link status, with same-file members collapsed to a line range. [[REQ-MAPDIAGRAMS-877]]
- The Risk diagram shows only requirements with at least one risk signal (confirmed with zero members; `draft`/`baseline`; ≥3 dependents), each paired with a scripted recommendation. [[REQ-MAPDIAGRAMS-878]]

## Cases
CASE-1
  Given  the generated `_map.md`
  When   it is inspected
  Then   it contains exactly 5 Mermaid code blocks, each with a legend

CASE-2
  Given  a corpus carrying system, architecture and code requirements
  When   the Specification Hierarchy is rendered
  Then   it draws the system and architecture nodes joined by their `satisfies:` edges,
         draws no code node, and shows each architecture's code count on its box

CASE-3
  Given  the System Map diagram
  When   it is rendered
  Then   nodes group into per-area subgraphs, single-node areas collapse into `misc`, and edges
         whose target is a bus node are omitted

CASE-4
  Given  the Dependency Map diagram
  When   it is rendered
  Then   it is area-level: one node per area (with a count), an edge A→B when some capability
         in A depends on one in B; per-capability hub edges are not drawn

CASE-5
  Given  the Risk diagram
  When   it is rendered
  Then   it shows only requirements with at least one risk signal, each with a scripted
         recommendation, and a draft's open question is not shown twice

## Context
**Terms**
- a node       one requirement, as drawn in a diagram.
- an area      the group a requirement belongs to: its `area:` field, or the first
- part of its id when that field is absent.
- a bus node   a `layer: bus` requirement — a foundation many others use.
- a hub        a requirement many others depend on (high fan-in).

**Notes**
- The risk-signal dedup lives in `_risk_signals`, shared with the `next` worklist, so the
  diagram and the worklist cannot disagree about what is at risk.
- Split out of [[ARCH-MAP-007]] on 2026-09-02. That requirement held 35 Contract clauses
  covering two capabilities — the graph and its rendering — and was the only requirement
  over twenty clauses carrying no `lint_exempt:`, i.e. the only one whose size had never
  been judged acceptable in writing.

**Example**
- Ana opens the pull request on GitHub. The System Map shows AUTH-LOGIN-001 wired to the
  session capability it depends on, coloured amber because it has no tests yet. She never
  runs the engine.

**Current implementation**
- `_mermaid_hierarchy`, `_grouped_areas`, `_mermaid_system`, `_mermaid_deps`, `_mermaid_req_to_code`,
  `_mermaid_risk`, `_build_md_text` and `render_md` in `reqmap.py`.


--------------------


---
id: REQ-MAPDIAGRAMS-874
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
---

# _map.md: five legended, always-regenerated Mermaid blocks

## Description
> `_map.md` is the picture that goes with the graph — Specification Hierarchy, System Map,
> Req→Code, Dependencies, Risk — rendered fresh from the registry on every `map` run so it
> can never drift into a hand-edited state. It renders on GitHub with no tooling, so a pull
> request reviewer sees the shape of the system without cloning anything.

Every bullet below is binding.
- `map` generates `_map.md` under `requirements/`, rendered from the graph and never edited.
- `_map.md` contains exactly 5 Mermaid code blocks: Specification Hierarchy, System Map,
  Req→Code, Dependencies and Risk.
- Each of those 5 blocks carries a legend.

## Cases
CASE-1 — map writes _map.md from the graph, overwriting any manual edit
  Given  a `requirements/_map.md` a human hand-edited since the last run
  When   `map` runs
  Then   the file is fully regenerated from the graph, discarding the manual edit

CASE-2 — _map.md carries exactly the five named diagrams
  Given  the generated `_map.md`
  When   its Mermaid code blocks are counted
  Then   there are exactly 5: Specification Hierarchy, System Map, Req→Code, Dependencies, Risk

CASE-3 — every diagram block ships its own legend
  Given  the generated `_map.md`
  When   each of the 5 Mermaid blocks is inspected
  Then   each one carries a legend describing its symbols


--------------------


---
id: REQ-MAPDIAGRAMS-875
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
---

# Specification Hierarchy: satisfies edges only, code counted not drawn

## Description
> The Hierarchy is the pyramid `level:` implies — system requirements over architecture
> ones — and it reads only `satisfies:` edges, never `depends_on:`, because those are
> different axes (one hierarchy, one composition graph). A `code`-level requirement never
> gets its own box; it is folded into its architecture parent's count so the diagram stays
> readable on a corpus with hundreds of them.

Every bullet below is binding.
- The Specification Hierarchy is drawn from the `satisfies:` edges, never from `depends_on:`.
- The Hierarchy draws a node for each `system` and each `architecture` requirement.
- The Hierarchy counts a `code` requirement against its parent and never draws it.
- An architecture box shows how many code requirements sit under it.

## Cases
CASE-1 — the Hierarchy follows satisfies edges, not depends_on
  Given  a system and an architecture requirement linked by `satisfies:` and by an unrelated `depends_on:`
  When   the Specification Hierarchy renders
  Then   it draws the `satisfies:` edge and omits the `depends_on:` edge

CASE-2 — the Hierarchy draws a node per system and architecture requirement
  Given  a corpus with one system and two architecture requirements
  When   the Specification Hierarchy renders
  Then   it draws three nodes, one for the system and one for each architecture requirement

CASE-3 — the Hierarchy folds code requirements into their parent's count
  Given  an architecture requirement with three `satisfies:`-linked code requirements
  When   the Specification Hierarchy renders
  Then   it draws no node for any code requirement, and the parent box shows a count of 3
         code requirements sitting under it


--------------------


---
id: REQ-MAPDIAGRAMS-876
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
---

# System Map: per-area subgraphs, bus edges hidden

## Description
> The System Map groups every node under its area — the `area:` field, or the id prefix when
> that field is absent — so a reviewer sees the system in the shape a team already thinks in.
> A single-node area collapses into `misc` rather than cluttering the diagram with one-box
> subgraphs, and an edge into a foundational (`bus`) or high-fan-in node is omitted, since
> drawing it would turn every diagram into a hairball centred on that one node.

Every bullet below is binding.
- A node's area is its `area:` field, or its id prefix when that field is absent.
- The System Map groups nodes into per-area subgraphs, and collapses a single-node area
  into a `misc` box.
- The System Map omits a `depends_on` edge whose target is a bus node or a high-fan-in hub.

## Cases
CASE-1 — a node's area falls back to its id prefix
  Given  one node carrying `area: payments` and one node with no `area:` field, id `AUTH-LOGIN-001`
  When   the area for each node is computed
  Then   the first node's area is `payments` and the second's is `AUTH`

CASE-2 — the System Map collapses a lone node into misc
  Given  three nodes sharing one area and one node alone in its own area
  When   the System Map renders
  Then   the three group into one subgraph and the lone node lands in a `misc` box

CASE-3 — the System Map hides edges into a bus node
  Given  a node whose `depends_on:` targets both a `layer: bus` requirement and a normal one
  When   the System Map renders
  Then   it draws the edge to the normal requirement and omits the edge to the bus node


--------------------


---
id: REQ-MAPDIAGRAMS-877
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
---

# Dependency Map is area-level; Req→Code colors and collapses lines

## Description
> The Dependency Map trades per-capability detail for one node per area (with a count) and
> one edge per cross-area dependency, so it stays readable at corpus scale where the System
> Map would not. Req→Code, the other per-file diagram in this group, colors a node by its
> link status and collapses several members in one file to a single line range instead of
> listing each one.

Every bullet below is binding.
- The Dependency Map is area-level: one node per area, carrying a capability count.
- The Dependency Map draws an edge A→B when some capability in A depends on one in B.
  Per-capability hub edges are not drawn.
- Req→Code colors an enforced-but-unlinked requirement red, and a baseline or draft
  not-yet-linked one muted grey.
- Req→Code collapses multiple members in one file to a min–max line range.
- Req→Code omits `level: code` requirements: they are counted in the hierarchy diagram and drawn
  in the viewer, and drawing them here with their function-level members pushed the block past
  the 50,000 characters GitHub renders.

## Cases
CASE-1 — the Dependency Map draws one counted node per area
  Given  an area holding four requirements
  When   the Dependency Map renders
  Then   it draws a single node for that area labelled with a count of 4

CASE-2 — the Dependency Map draws one area edge per cross-area dependency
  Given  two requirements in area A each depending on a requirement in area B
  When   the Dependency Map renders
  Then   it draws exactly one A→B edge, not one per capability pair

CASE-3 — Req→Code colors nodes by link status
  Given  a `confirmed` requirement with no `tested-by:` member and a `draft` requirement with no member
  When   Req→Code renders
  Then   the confirmed node is red and the draft node is muted grey

CASE-4 — Req→Code collapses same-file members to a line range
  Given  a requirement with three members in one file at lines 10, 25 and 40
  When   Req→Code renders
  Then   that file shows a single `10–40` range, not three separate entries

CASE-5 — code-level nodes stay out of Req→Code
  Given  an architecture node and a code node, both with members
  When   the Req→Code block is rendered
  Then   the architecture node appears and the code node does not

--------------------


---
id: REQ-MAPDIAGRAMS-878
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
---

# Risk diagram: only flagged requirements, each with advice

## Description
> The Risk diagram is deliberately not a census — it shows only requirements carrying at
> least one open risk signal, each paired with a scripted recommendation instead of a bare
> label, so a reader knows what to do about it. It shares its dedup with the `next`
> worklist's source, so a draft's open question is never shown twice under two different
> names for the same underlying problem.

Every bullet below is binding.
- The Risk diagram shows only requirements with at least one risk signal
  (confirmed with zero members; `draft`/`baseline`; ≥3 dependents).
- The Risk diagram pairs each of them with a scripted recommendation.
- A `draft`'s open verify-intent question is suppressed, subsumed by its `unreviewed`
  signal, so a draft is not double-flagged.

## Cases
CASE-1 — the Risk diagram omits a requirement with no risk signal
  Given  a `confirmed` requirement with members and few dependents, alongside a `confirmed` requirement with zero members
  When   the Risk diagram renders
  Then   only the zero-member requirement appears

CASE-2 — every Risk node carries a recommendation
  Given  a `draft` requirement shown in the Risk diagram
  When   the diagram renders
  Then   its box carries a scripted recommendation string, not just the risk label

CASE-3 — a draft's verify-intent question does not double-flag it
  Given  a `draft` requirement carrying both an open verify-intent question and the `unreviewed` signal
  When   the Risk diagram renders
  Then   it shows the `unreviewed` signal once and suppresses the separate verify-intent flag

