---
id: REQ-MAP-007
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
---

# Requirement map (HTML + MD)

> Render the whole registry as navigable diagrams a human can read at a glance.

## Input
- The loaded requirements and the discovered members.

## Description
Text listings do not show shape — which capabilities sit on the bus, what depends
on what, where the code lives. The map is a derived view (never a source of truth):
two output files are generated together:
- `_map.html`: multi-tab interactive viewer with mermaid.js and a clickable detail panel.
- `_map.md`: five Mermaid diagrams for GitHub/GitLab static rendering.

Both are regenerated, never edited, and live under `requirements/` so they travel
with the registry. For legibility at scale the System Map clusters nodes into
per-area subgraphs (a node's `area:` field, else its id prefix), collapses
single-node areas into one `misc` box, and hides `depends_on` edges into the bus /
high-fan-in hubs (the full graph stays in the Dependency Map). Every tab carries a
legend, and Req→Code colors only an enforced-but-unlinked requirement red.

## Output
- `requirements/_map.html`: multi-tab HTML viewer with mermaid.js; clicking a node opens
  its WHY / WHAT / WHERE / HOW detail panel.
- `requirements/_map.md`: 5 Mermaid diagrams + YAML frontmatter with node/edge counts.

## Acceptance (= tests)
- The generated files contain one node per requirement and one edge per `depends_on`.
- `_map.md` contains exactly 5 Mermaid code blocks, one per view.
- `_map.html` has a tab bar with 5 tabs: System Map, Req→Code, Behavioral Flow, Dependencies, Risk, and each pane carries a legend.
- Behavioral Flow shows `Input[...] --> REQ-ID --> Output[...]` for every requirement.
- System Map groups nodes into per-area subgraphs, collapses single-node areas into a `misc` box, and omits edges whose target is a bus node (the Dependency Map keeps them).
- Risk diagram shows only requirements with at least one risk signal (confirmed+0 members, draft/baseline, or 3+ dependents).
- A node with no members renders "(no members found)" in the HTML detail panel.

## Links
- Used by: (auto)
## Members in code (auto)
