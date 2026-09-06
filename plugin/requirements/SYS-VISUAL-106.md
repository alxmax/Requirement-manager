---
id: SYS-VISUAL-106
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
milestone: v2.32
priority: must-have
satisfies: [SYS-SSOT-001]
---
# Seeing the system at a glance

> As someone reviewing a change, I want the shape of the system as a picture I can open 
> without tooling, so that a dependency I would have missed in a list is obvious.

Scenario: the system is rendered
  Given  the requirement graph
  When   the map is generated
  Then   the same graph is available as diagrams that render in a browser with no install, and as a data file any front-end can consume

## Requirements in this system (auto)
- `ARCH-EXCALIDRAW-030` — Excalidraw scene builder — core API  (architecture)  ·  9 detailed design
- `ARCH-EXCALIDRAW-031` — Excalidraw quality gates  (architecture)  ·  9 detailed design
- `ARCH-EXCALIDRAW-032` — Excalidraw builder CLI verbs  (architecture)  ·  4 detailed design
- `ARCH-MAP-007` — Requirement graph (_map.json)  (architecture)  ·  18 detailed design
- `ARCH-MAPDIAGRAMS-055` — Mermaid diagrams (_map.md)  (architecture)  ·  17 detailed design
- `ARCH-SITE-026` — Generate & maintain a project presentation page  (architecture)  ·  6 detailed design
- `ARCH-VIEWER-007` — Self-contained HTML map viewer  (architecture)  ·  24 detailed design
