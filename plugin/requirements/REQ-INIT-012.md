---
id: REQ-INIT-012
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-EXTRACT-008, REQ-CHECK-006, REQ-MAP-007]
superseded_by:
milestone: v1.10
---

# First-use bootstrap

> Setting up requirement tracking on a fresh project means doing five fiddly steps in the right order.
> This is the single "get started" command that does all of them for you: it makes the folder, reads
> your existing code and drafts requirements from it, records a baseline, builds the navigable map, and
> tells you the one next thing to do. Without it, a newcomer has to learn and chain those steps by hand,
> and most give up before the project is in a usable state.

## WHAT — Contract (normative)
- It shall create the requirements directory if it does not exist.
- It shall write a minimal `.reqmapignore` only when none exists; it shall never overwrite an existing `.reqmapignore`.
- The seeded file shall list `scripts/reqmap.py`, the vendored engine, whose self-tags would otherwise read as dangling refs.
- That line shall be omitted, with a comment explaining why, when the engine is self-hosting.
- The engine is self-hosting when it carries membership tags that resolve to requirements already present; it is then managed code and must stay scanned.
- It shall draft requirements from existing untagged code by invoking the extract capability, then build the drift lock and the map so the repo is immediately in a gate-passing, navigable state.
- It shall print a guided summary that points at a single next command (`reqmap.py next`) plus wiring the gate, rather than an undifferentiated menu.
- When nothing was extracted (no supported files, or all ignored) it shall say so distinctly and point at `new` — it shall not print a tracked-requirements summary that masks the empty result.
- It shall be safe to re-run: a second invocation refreshes the lock and map, then re-prints the summary.
- A re-run shall never destroy authored requirements or an existing ignore file.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The seeded `.reqmapignore` assumes the engine is vendored at `scripts/reqmap.py` (the documented setup path); the self-hosting exception keys off that same path.
- Self-hosting detection requires requirements to already exist when `.reqmapignore` is first created. A from-scratch self-hosting bootstrap (empty `requirements/`) cannot be detected — nothing resolves yet — so the engine line is written; re-running after authoring requirements does not rewrite the existing file, so such a repo must drop the line by hand. This is an accepted edge.
- On a repo with no extractable code files the bootstrap still succeeds, producing an empty-but-valid lock and map.
- `init` orchestrates existing capabilities (extract, check, map); it adds no new analysis of its own.

## HOW — Acceptance (= tests)
AC-1
  Given  a repo with no `requirements/`
  When   `init` runs
  Then   it creates the directory and a `.reqmapignore` containing `scripts/reqmap.py`

AC-2
  Given  a self-hosting repo (an existing requirement whose id is tagged inside `scripts/reqmap.py`)
  When   `init` runs
  Then   the written `.reqmapignore` does **not** ignore `scripts/reqmap.py`, so the engine
         stays scanned and its members are not orphaned

AC-3
  Given  a repo that already has a `.reqmapignore`
  When   `init` runs
  Then   that file is left unchanged

AC-4
  Given  a completed `init`
  When   the requirements directory is inspected
  Then   `requirements/_map.html`, `requirements/_map.md` and the drift lock exist

AC-5
  Given  existing untagged code
  When   `init` runs
  Then   it drafts at least one requirement, reports the tracked count, and its summary
         points at `reqmap.py next`

AC-6
  Given  a repo with no extractable code
  When   `init` runs
  Then   it prints the distinct "no requirements were extracted" message (not a tracked-count summary)

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a codebase with no requirements at all. She runs `reqmap.py init` once: it creates the `requirements/` folder, seeds a `.reqmapignore`, drafts requirements from her untagged code, builds the drift lock and the map, then prints a short summary that ends with "now run `reqmap.py next`". In one command her repo went from untracked to gate-passing and navigable, and she knows exactly where to go next.

## WHERE — Current implementation
- `cmd_init` in `reqmap.py` — creates `requirements/`, conditionally seeds `.reqmapignore` via `_reqmapignore_seed` (which applies the self-hosting exception), then calls `cmd_extract` → `cmd_check(update_lock=True)` → `cmd_map`, and prints the guided summary.

## Links
- Used by: (auto)
## Members in code (auto)
