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

## WHAT — Contract (normative)
- It shall generate two files under `requirements/`: `_map.html` (a multi-tab interactive
  viewer using mermaid.js with a clickable detail panel) and `_map.md` (Mermaid diagrams for
  static GitHub/GitLab rendering). Both are derived views, regenerated, never edited.
- There shall be one node per requirement and one edge per `depends_on`. `_map.md` shall
  contain exactly 4 Mermaid code blocks; `_map.html` shall have a 4-tab bar — System Map,
  Req→Code, Dependencies, Risk — and each pane shall carry a legend.
- The System Map shall group nodes into per-area subgraphs (a node's `area:` field, else its
  id prefix), collapse single-node areas into a `misc` box, and omit `depends_on` edges whose
  target is a bus node OR a high-fan-in hub.
- The Dependency Map shall be area-level: one node per area (with a capability count), an edge
  A→B when some capability in A depends on one in B; per-capability hub edges are not drawn.
- Req→Code shall color an enforced-but-unlinked requirement red and a baseline/draft not-yet-
  linked one muted grey, collapsing multiple members in one file to a min–max line range.
- The Risk diagram shall show only requirements with ≥1 risk signal (confirmed+0 members,
  draft/baseline, or ≥3 dependents), each paired with a scripted recommendation.
- The detail panel shall render the new `Contract`/`Verify intent`/`Notes` split (falling back
  to Input/Output/Description for legacy requirements) and a search box plus a ◎ button that
  centers and highlights a requirement in the currently-open diagram without switching tabs.
- All requirement-derived text shall be escaped so a hostile id/title/body cannot inject HTML
  or JavaScript into the generated map.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- mermaid.js is loaded from a CDN without SRI (pinned to a major range); the map is a local
  developer artifact, so the supply-chain exposure is accepted (see the engine comment).

## HOW — Acceptance (= tests)
- The generated files contain one node per requirement and one edge per `depends_on`.
- `_map.md` contains exactly 4 Mermaid code blocks; `_map.html` has the 4 named tabs, each with a legend.
- The detail panel renders the Contract/Verify-intent/Notes split (and the Given/When/Then acceptance) for new-format requirements and falls back to Input/Output/Description for legacy ones.
- System Map groups nodes into per-area subgraphs, collapses single-node areas into `misc`, and omits edges whose target is a bus node.
- Dependency Map is area-level: one node per area (with a count), an edge A→B when some capability in A depends on one in B; per-capability hub edges are not drawn.
- Risk shows only requirements with at least one risk signal, each with a scripted recommendation.
- The search box opens a requirement's detail panel whose ◎ button centers and highlights it in the active tab without switching tabs; a node with no members renders "(no members found)".
- A requirement id containing a quote or `</script>` does not break out of the generated JS.

## WHERE — Current implementation
- `cmd_map`, `render_html`, `render_md`, `_js_str`, the `_mermaid_*` generators in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
