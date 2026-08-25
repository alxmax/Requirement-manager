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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     .reqmapignore  the list of files the scan skips.
     the lock       requirements/_reqlock.json — the saved fingerprint of every contract.
     the map        requirements/_map.* — the generated diagrams and graph.
     self-hosting   a repo where reqmap.py describes ITSELF: the engine file carries
                    tags pointing at requirements that already live in this same repo. -->

**What it creates**
- `init` creates the requirements folder if it is missing.
- `init` writes a starter `.reqmapignore` only if the repo has none. It never overwrites one
  that is already there.
- The starter file lists `scripts/reqmap.py`. Without that line, the engine's own tags look
  like they point at requirements that do not exist.
- One exception: if the engine describes itself in this repo, `init` leaves the line out and
  writes a comment saying why. There the engine is ordinary tracked code, so the scan keeps
  reading it.
- "Describes itself" means `scripts/reqmap.py` carries tags whose ids match requirements
  already in the repo.

**What it runs**
- `init` drafts requirements from untagged code, writes the lock, then builds the map, in that
  order. When it finishes, the repo passes the gate and has a map.

**What it prints**
- `init` ends with a short summary naming one next command: `reqmap.py next`. Not a list of
  every option.
- If nothing was drafted, `init` says so in plain words and points at `new`. It never prints a
  count summary that hides an empty result.

**Running it again**
- Running `init` twice is safe. The second run refreshes the lock and the map, then prints the
  summary again.
- A second run never deletes a requirement someone wrote, and never edits an existing
  `.reqmapignore`.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The starter `.reqmapignore` assumes the engine sits at `scripts/reqmap.py` — the documented
  place to vendor it. The self-hosting exception looks at that same path.
- Self-hosting can only be detected if requirements already exist when `.reqmapignore` is first
  written. Bootstrapping a self-hosting repo from an empty `requirements/` folder cannot be
  detected — there is nothing for the tags to match yet — so the engine line does get written.
  Re-running later does not rewrite the file, so that repo has to delete the line by hand.
  Known and accepted.
- On a repo with no extractable code `init` still succeeds: the lock and map are empty but valid.
- `init` performs no analysis of its own. It only calls capabilities that already exist
  (draft, gate, map) in a fixed order.

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
