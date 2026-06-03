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
- It shall write a minimal `.reqmapignore` only when none exists; it shall never overwrite an existing `.reqmapignore`. The seeded file lists `scripts/reqmap.py` (the vendored engine, whose self-tags would otherwise read as dangling refs) **except** when that file is self-hosting — i.e. it carries membership tags that resolve to requirements already present — in which case the engine is the managed code and must stay scanned, so the line is omitted and a comment explains why.
- It shall draft requirements from existing untagged code by invoking the extract capability, then build the drift lock and the map so the repo is immediately in a gate-passing, navigable state.
- It shall print a guided summary that points at a single next command (`reqmap.py next`) plus wiring the gate, rather than an undifferentiated menu.
- When nothing was extracted (no supported files, or all ignored) it shall say so distinctly and point at `new` — it shall not print a tracked-requirements summary that masks the empty result.
- It shall be safe to re-run: a second invocation refreshes the lock and map and re-prints the summary without destroying authored requirements or an existing ignore file.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The seeded `.reqmapignore` assumes the engine is vendored at `scripts/reqmap.py` (the documented setup path); the self-hosting exception keys off that same path.
- Self-hosting detection requires requirements to already exist when `.reqmapignore` is first created. A from-scratch self-hosting bootstrap (empty `requirements/`) cannot be detected — nothing resolves yet — so the engine line is written; re-running after authoring requirements does not rewrite the existing file, so such a repo must drop the line by hand. This is an accepted edge.
- On a repo with no extractable code files the bootstrap still succeeds, producing an empty-but-valid lock and map.
- `init` orchestrates existing capabilities (extract, check, map); it adds no new analysis of its own.

## HOW — Acceptance (= tests)
- `init` on a repo with no `requirements/` creates the directory and a `.reqmapignore` containing `scripts/reqmap.py`.
- `init` on a self-hosting repo (an existing requirement whose id is tagged inside `scripts/reqmap.py`) writes a `.reqmapignore` that does **not** ignore `scripts/reqmap.py`, so the engine stays scanned and its members are not orphaned.
- `init` on a repo that already has a `.reqmapignore` leaves that file unchanged.
- After `init`, `requirements/_map.html`, `requirements/_map.md` and the drift lock exist.
- `init` over existing untagged code drafts at least one requirement, reports the tracked count, and its summary points at `reqmap.py next`.
- `init` on a repo with no extractable code prints the distinct "no requirements were extracted" message (not a tracked-count summary).

## WHERE — Current implementation
- `cmd_init` in `reqmap.py` — creates `requirements/`, conditionally seeds `.reqmapignore` via `_reqmapignore_seed` (which applies the self-hosting exception), then calls `cmd_extract` → `cmd_check(update_lock=True)` → `cmd_map`, and prints the guided summary.

## Links
- Used by: (auto)
## Members in code (auto)
