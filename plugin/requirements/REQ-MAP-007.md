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

# Requirement map (Mermaid MD + JSON + self-contained viewer)

> A list of requirement files tells you what exists but not how it all connects. This
> draws the picture: which capability depends on which, what has code, what is at risk —
> as diagrams you can read on GitHub and a viewer you open with a double-click. It turns
> the registry into something a person can take in at a glance.

## WHAT — Contract (normative)
- It shall generate two files under `requirements/`: `_map.md` (Mermaid diagrams for
  static GitHub/GitLab rendering) and `_map.json` (a `{engine_version, repo, nodes, edges}`
  graph for an external front-end). Both are derived views, regenerated, never edited.
- `_map.json` shall carry a top-level `repo` field — a best-effort `owner/repo` (else the
  repo directory name, else null) identifying the project the map describes, for display in
  the viewer header. It is derived from the git remote and so differs across forks/clones;
  it is therefore excluded from the `map --check` freshness diff and resolving it shall never
  raise or block map generation (git may be absent or the tree may not be a checkout).
- It shall also generate `_map.html` — a self-contained, single-file copy of the React
  viewer with this repo's graph inlined as `window.__REQMAP_DATA__`, openable by
  double-click with no server — WHEN the viewer template `_map_viewer.html` is vendored
  beside the engine. Absent the template it emits only `_map.md` + `_map.json` (the viewer
  is optional, so the stdlib engine still works with no extra files).
- The injected graph shall be escaped (`</` → `<\/`) so a `</script>` sequence in any
  requirement field cannot break out of the inline data `<script>` (HTML-injection guard).
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
- When `_map.html` is generated AND a `docs/` directory at the git root carries a GitHub
  Pages signal (`.nojekyll` or `index.html` present), it shall also copy `_map.html` to
  `docs/map.html`. When no signal is present or git is absent, `docs/map.html` is not written.
- `map --check` (the freshness gate) shall additionally flag `docs/map.html` as stale when it
  differs from a fresh viewer render of the current registry — but only when the Pages signal
  and the viewer template are both present and `docs/map.html` already exists. A copy that was
  never generated is not stale (the same absent-file rule applied to `_map.*`). The on-disk copy
  is read as text so platform newline differences (CRLF vs LF) never raise a false positive, and
  the injected data carries only the stable `engine_version` (no wall-clock), so the comparison
  is deterministic. This stops the published GitHub Pages copy from silently drifting from the registry.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The viewer is the Vite + React app under `app/`. Its single-file build (`app/` →
  `npm run build:viewer`) is vendored beside the engine as `scripts/_map_viewer.html`
  with a `<!--REQMAP_DATA-->` marker; the engine (stdlib only) swaps the marker for the
  inline data. So the engine ships a rich UI without itself depending on Node/npm.
- `_map.html` is a regenerable artifact (template + `_map.json`), not committed; rebuild
  with `map`. `_map.json` is the committed source of its data.
- `export` is a thin alias that writes only `_map.json` (or to stdout / `--out PATH`) for
  ad-hoc piping; `map` writes `_map.md` + `_map.json` (+ `_map.html` when the template is present).

## HOW — Acceptance (= tests)
- The generated files contain one node per requirement and one edge per `depends_on`.
- `_map.md` contains exactly 4 Mermaid code blocks, each with a legend.
- `_map.json` parses to `{engine_version, repo, nodes, edges}` and carries one node per requirement
  with its members and risk signals; `repo` is the project's `owner/repo` (or directory name, or null)
  and is omitted from the freshness comparison.
- System Map groups nodes into per-area subgraphs, collapses single-node areas into `misc`, and omits edges whose target is a bus node.
- Dependency Map is area-level: one node per area (with a count), an edge A→B when some capability in A depends on one in B; per-capability hub edges are not drawn.
- Risk shows only requirements with at least one risk signal, each with a scripted recommendation.
- A requirement id/title containing a quote or `</script>` round-trips through `_map.json` as data (no injection) and a node with no members reports an empty member list.
- Injecting the graph into the viewer template replaces the `<!--REQMAP_DATA-->` marker with a `window.__REQMAP_DATA__` assignment carrying one node per requirement; a `</script>` in any field is escaped so it cannot close the script early.
- When `docs/` at the git root has `.nojekyll` or `index.html`, `map` also writes `docs/map.html` (same content as `_map.html`); when the signal is absent, `docs/map.html` is not written.
- When `docs/` has no Pages signal (or git is absent), `map` still succeeds and writes only the standard outputs.
- After `map`, `map --check` exits 0; if `docs/map.html` is then edited to differ from a fresh render, `map --check` exits non-zero and names `map.html`.
- When the Pages signal is present but `docs/map.html` does not exist (never generated, or removed), `map --check` does not flag it stale.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py map`. She opens `_map.html` by double-click — no server — and
  sees AUTH-LOGIN-001 as a box wired to the session capability it depends on, coloured
  amber because it has no tests yet. One glance tells her where the gap is.

## WHERE — Current implementation
- `cmd_map`, `cmd_export`, `render_md`, `render_json`, `render_html`, `_build_json_text`, `_repo_name`, `_inject_viewer`, `_viewer_template_path`, `_docs_publish_path`, the `_mermaid_*` generators in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
