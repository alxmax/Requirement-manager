---
id: REQ-INIT-012
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-EXTRACT-008, REQ-CHECK-006, REQ-MAP-007]
superseded_by:
---

# First-use bootstrap

> One command that turns a fresh repo into a tracked one — scaffold, draft from existing code, lock, map, and tell the human what to do next.

## WHAT — Contract (normative)
- It shall create the requirements directory if it does not exist.
- It shall write a minimal `.reqmapignore` (ignoring `scripts/reqmap.py`) only when none exists; it shall never overwrite an existing `.reqmapignore`.
- It shall draft requirements from existing untagged code by invoking the extract capability, then build the drift lock and the map so the repo is immediately in a gate-passing, navigable state.
- It shall print a guided summary that points at a single next command (`reqmap.py next`) plus wiring the gate, rather than an undifferentiated menu.
- When nothing was extracted (no supported files, or all ignored) it shall say so distinctly and point at `new` — it shall not print a tracked-requirements summary that masks the empty result.
- It shall be safe to re-run: a second invocation refreshes the lock and map and re-prints the summary without destroying authored requirements or an existing ignore file.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The seeded `.reqmapignore` assumes the engine is vendored at `scripts/reqmap.py` (the documented setup path).
- On a repo with no extractable code files the bootstrap still succeeds, producing an empty-but-valid lock and map.
- `init` orchestrates existing capabilities (extract, check, map); it adds no new analysis of its own.

## HOW — Acceptance (= tests)
- `init` on a repo with no `requirements/` creates the directory and a `.reqmapignore` containing `scripts/reqmap.py`.
- `init` on a repo that already has a `.reqmapignore` leaves that file unchanged.
- After `init`, `requirements/_map.html`, `requirements/_map.md` and the drift lock exist.
- `init` over existing untagged code drafts at least one requirement, reports the tracked count, and its summary points at `reqmap.py next`.
- `init` on a repo with no extractable code prints the distinct "no requirements were extracted" message (not a tracked-count summary).

## WHERE — Current implementation
- `cmd_init` in `reqmap.py` — creates `requirements/`, conditionally seeds `.reqmapignore`, then calls `cmd_extract` → `cmd_check(update_lock=True)` → `cmd_map`, and prints the guided summary.

## Links
- Used by: (auto)
## Members in code (auto)
