---
id: REQ-MAP-007
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
---

# Requirement map (HTML)

> Render the whole registry as one navigable graph a human can read at a glance.

## Input
- The loaded requirements and the discovered members.

## Description
Text listings do not show shape — which capabilities sit on the bus, what depends
on what, where the code lives. The map is a derived view (never a source of truth):
features on top, bus at the bottom, edges for `depends_on`, and a detail panel per
node showing intent, input/output, acceptance and members. It is regenerated, never
edited, and lives under `requirements/` so it travels with the registry.

## Output
- `requirements/_map.html`: a self-contained HTML file with the registry embedded as JSON.

## Acceptance (= tests)
- The generated file contains one node per requirement and one edge per `depends_on`.
- Bus and feature nodes are placed on separate rows.
- A node with no members renders "(no members found)" in its panel.

## Links
- Used by: (auto)
## Members in code (auto)
