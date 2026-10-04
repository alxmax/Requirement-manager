# ADR-0063 — ARCH-VIEWER-007 stays one capability, and its file-spread warning stands

- **Status:** Accepted. Carries on from
  [ADR-0050](0050-the-viewer-artifact-and-what-it-renders-are-two-capabilities.md), which split
  the artifact from what it renders and left the rest whole.
- **Decided:** 2026-10-04, when the gate showed two `file-spread` warnings on the viewer.
- **Evidence:** `reqmap.py gate --full --code ..` on 2026-10-04. ARCH-VIEWER-007 is
  implemented by 39 files in 13 directories (`app/src` and its eight subdirectories, `app/scripts`
  and `app/scripts/smoke`, `plugin/scripts/reqmap_engine`). REQ-VIEWER-1084 was 3 files in 3.

## Context

The check counts the directories of a requirement's own `implements:` members and warns from 3
(ADR-0042). A UI is many files in many directories by construction, and the warning came back
when the exemptions were dropped (`800df76`). To clear it for ARCH-VIEWER-007, every piece
would have to sit in at most two directories: about nine capabilities (plan, explorer, spec,
problems, commands, library and styles, shell, tooling, engine), each with its own cases and
its own `tested-by`. The viewer is one artifact built from one source tree, and the nine would be
named after folders, not after anything a reader asks for.

REQ-VIEWER-1084 was different. It held two things: which tab a ring opens (one handler in
`App.jsx`) and what the tabs list (`ProblemsView.jsx`, `ProblemsPanels.jsx`). They change for
different reasons.

## Decision

1. **REQ-VIEWER-1084 is split.** REQ-VIEWER-1090 takes the routing: the health ring opens the
   Health tab, the design ring the Design tab, and the tab is chosen before the surface is
   shown. REQ-VIEWER-1084 keeps what the tabs list. Both sit in at most two directories.
2. **ARCH-VIEWER-007 is not split.** The warning stays on the report, with no `lint_exempt:`
   hiding it.

## Consequences

- `gate --full` reports one `file-spread` warning, on ARCH-VIEWER-007, instead of two.
- ARCH-VIEWER-007 gains one obligation line, for REQ-VIEWER-1090.
- REQ-VIEWER-1090 starts as `draft`; a human confirms it after reading it.

## Revisit when

- A viewer surface grows a requirement of its own that needs a different owner or milestone:
  split that surface out then, along what changes together.
- The viewer's directories are flattened or regrouped, so the count falls under 3 by itself.
