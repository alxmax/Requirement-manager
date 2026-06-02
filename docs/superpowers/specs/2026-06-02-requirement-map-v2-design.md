# Requirement Map v2 — Design Spec

Date: 2026-06-02  
Status: approved

## Summary

Enhance `python reqmap.py map` to generate two files: `_map.md` (5 Mermaid diagrams, GitHub-renderable) and `_map.html` (multi-tab interactive viewer). Both replace the current single HTML with a fixed-width SVG that overflows when there are many nodes.

## Architecture

`cmd_map` in `reqmap.py` builds one shared `data` dict (already exists), then calls two render functions:

- `render_md(data)` → `requirements/_map.md`
- `render_html(data)` → `requirements/_map.html`

No `_map.json` as a separate file. Full JSON data is embedded in `_map.html` as a `<script>` block only. `_map.md` frontmatter contains only lightweight metadata (node count, edge count, generated timestamp).

## The 5 Diagrams

Each is a Mermaid block in `_map.md` and a tab in `_map.html`.

### 1. High-Level System Map
`graph TD` with two subgraphs (`Features` / `Bus`). Nodes labeled `ID`. Edges from `depends_on`. Replaces current SVG — Mermaid handles layout automatically, fixing node overlap.

### 2. Requirement-to-Code
`graph LR`: requirement node → member file node, edge labeled with role (`implements`, `tested-by`, etc.). Requirements with no members rendered in a distinct color.

### 3. Behavioral Flow
`flowchart LR` chain per requirement:
```
Input([input]) --> REQ-ID[REQ-ID] --> Output([output])
```
One row per requirement. Shows the data transformation thread across the whole registry.

### 4. Dependency Map
`graph TD`, only `depends_on` edges. No code members shown. Pure capability topology — cleaner than the System Map for understanding coupling.

### 5. Risk & Unknowns
`graph TD` with filtered nodes only (requirements that have at least one risk signal):

| Signal | Condition | Severity |
|--------|-----------|----------|
| unimplemented | `confirmed` + 0 members | critical (red) |
| unreviewed | `draft` or `baseline` status | unreviewed (orange) |
| high blast radius | 3+ dependents | blast-radius (yellow) |

A table below the diagram: `ID | status | members | dependents | risk reasons`.

## HTML Structure

- Tab bar: `System Map | Req→Code | Behavioral Flow | Dependencies | Risk`
- Each tab: one Mermaid diagram rendered via mermaid.js (CDN)
- Detail panel (existing): click any node → opens intent, input/output, acceptance, members
- WHY→WHAT→WHERE→HOW labeled explicitly in the panel:
  - WHY → intent (italic quote)
  - WHAT → id + description
  - WHERE → members (role: file:lines)
  - HOW → acceptance criteria

Node clicks wired via Mermaid `click` callbacks → existing `sel(id)` JS function.

## Markdown Structure (`_map.md`)

```
---
generated: <timestamp>
nodes: <count>
edges: <count>
---

# Requirement Map

## System Map
```mermaid ... ```

## Requirement-to-Code
```mermaid ... ```

## Behavioral Flow
```mermaid ... ```

## Dependency Map
```mermaid ... ```

## Risk & Unknowns
```mermaid ... ```

### Risk Table
| ID | status | members | dependents | risks |
```

## Changes to REQ-MAP-007

- Rename: "Requirement map (HTML + MD)"
- Output section: add `requirements/_map.md`
- Add acceptance criteria:
  - `_map.md` contains 5 Mermaid diagrams, one per view
  - HTML has a tab per diagram type
  - Risk diagram shows only requirements with at least one risk signal
  - Behavioral Flow shows Input → REQ-ID → Output for every requirement

## Out of Scope

- Interactive Mermaid node clicking in the `.md` file (GitHub doesn't support it)
- Generating `_map.json` as a standalone file
- Any diagram with more than one Mermaid block per view (one block per tab/section)
