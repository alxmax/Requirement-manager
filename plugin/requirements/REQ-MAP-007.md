---
id: REQ-MAP-007
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
---

# Requirement map (Mermaid MD + JSON)

> Render the whole registry as navigable diagrams and a machine-readable graph a human or a front-end can read at a glance.

## WHAT — Contract (normative)
- It shall generate two files under `requirements/`: `_map.md` (Mermaid diagrams for
  static GitHub/GitLab rendering) and `_map.json` (a `{engine_version, nodes, edges}`
  graph for an external front-end). Both are derived views, regenerated, never edited.
- There shall be one node per requirement and one edge per `depends_on`. `_map.md` shall
  contain exactly 4 Mermaid code blocks — System Map, Req→Code, Dependencies, Risk — and
  each shall carry a legend.
- `_map.json` shall carry, per node, the requirement's id, layer, status, area, title,
  intent, Contract/Verify-intent/Notes bullets, acceptance, members (`role`/`loc`), `deps`,
  `used_by`, and risk signals — the same `{nodes, edges}` shape the diagrams are built from.
- The System Map shall group nodes into per-area subgraphs (a node's `area:` field, else its
  id prefix), collapse single-node areas into a `misc` box, and omit `depends_on` edges whose
  target is a bus node OR a high-fan-in hub.
- The Dependency Map shall be area-level: one node per area (with a capability count), an edge
  A→B when some capability in A depends on one in B; per-capability hub edges are not drawn.
- Req→Code shall color an enforced-but-unlinked requirement red and a baseline/draft not-yet-
  linked one muted grey, collapsing multiple members in one file to a min–max line range.
- The Risk diagram shall show only requirements with ≥1 risk signal (confirmed+0 members,
  draft/baseline, or ≥3 dependents), each paired with a scripted recommendation. A `draft`'s
  open verify-intent question is suppressed (subsumed by its `unreviewed` signal) so a draft is
  not double-flagged; this dedup lives in `_risk_signals`, shared with the `next` worklist.
- All requirement-derived text shall be JSON-encoded in `_map.json`, which neutralizes any
  hostile id/title/body by construction (no markup context to break out of).

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- `_map.json` is consumed by the standalone front-end under `app/` (a Vite + React viewer);
  the engine stays stdlib-only and ships no HTML UI of its own.
- `export` is a thin alias that writes only `_map.json` (or to stdout / `--out PATH`) for
  ad-hoc piping; `map` writes both `_map.md` and `_map.json`.

## HOW — Acceptance (= tests)
- The generated files contain one node per requirement and one edge per `depends_on`.
- `_map.md` contains exactly 4 Mermaid code blocks, each with a legend.
- `_map.json` parses to `{engine_version, nodes, edges}` and carries one node per requirement
  with its members and risk signals.
- System Map groups nodes into per-area subgraphs, collapses single-node areas into `misc`, and omits edges whose target is a bus node.
- Dependency Map is area-level: one node per area (with a count), an edge A→B when some capability in A depends on one in B; per-capability hub edges are not drawn.
- Risk shows only requirements with at least one risk signal, each with a scripted recommendation.
- A requirement id/title containing a quote or `</script>` round-trips through `_map.json` as data (no injection) and a node with no members reports an empty member list.

## WHERE — Current implementation
- `cmd_map`, `cmd_export`, `render_md`, `render_json`, `_build_json_text`, the `_mermaid_*` generators in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
