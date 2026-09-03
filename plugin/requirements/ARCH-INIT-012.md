---
id: ARCH-INIT-012
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-EXTRACT-008, ARCH-CHECK-006, ARCH-MAP-007]
satisfies: [SYS-SHIP-108]
superseded_by:
milestone: v1.10
---

# First-use bootstrap

## Description
> Setting up requirement tracking on a fresh project means doing five fiddly steps in the right order.
> This is the single "get started" command that does all of them for you: it makes the folder, reads
> your existing code and drafts requirements from it, records a baseline, builds the navigable map, and
> tells you the one next thing to do. Without it, a newcomer has to learn and chain those steps by hand,
> and most give up before the project is in a usable state.
Every bullet below is binding.
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
- The starter file also lists `.worktrees/**` and `.claude/worktrees/**` — the two places an
  isolated agent worktree is created. Each holds a full second copy of the repo, so without
  those lines every member is counted twice and the copies' tags read as dangling refs:
  errors that are not in the code, in files a clean CI checkout never has.
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

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
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

## Cases (= tests)
CASE-1
  Given  a repo with no `requirements/`
  When   `init` runs
  Then   it creates the directory and a `.reqmapignore` containing `scripts/reqmap.py`

CASE-2
  Given  a self-hosting repo (an existing requirement whose id is tagged inside `scripts/reqmap.py`)
  When   `init` runs
  Then   the written `.reqmapignore` does **not** ignore `scripts/reqmap.py`, so the engine
         stays scanned and its members are not orphaned

CASE-3
  Given  a repo that already has a `.reqmapignore`
  When   `init` runs
  Then   that file is left unchanged

CASE-4
  Given  a completed `init`
  When   the requirements directory is inspected
  Then   `requirements/_map.html`, `requirements/_map.md` and the drift lock exist

CASE-5
  Given  existing untagged code
  When   `init` runs
  Then   it drafts at least one requirement, reports the tracked count, and its summary
         points at `reqmap.py next`

CASE-6
  Given  a repo with no extractable code
  When   `init` runs
  Then   it prints the distinct "no requirements were extracted" message (not a tracked-count summary)

CASE-7
  Given  a repo with no `.reqmapignore` and a tagged file copied into `.worktrees/` and
         into `.claude/worktrees/` (what an isolated subagent leaves behind)
  When   `init` runs and the repo is then scanned
  Then   the seeded `.reqmapignore` lists both globs and neither copy is scanned as a member

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana inherits a codebase with no requirements at all. She runs `reqmap.py init` once: it creates the `requirements/` folder, seeds a `.reqmapignore`, drafts requirements from her untagged code, builds the drift lock and the map, then prints a short summary that ends with "now run `reqmap.py next`". In one command her repo went from untracked to gate-passing and navigable, and she knows exactly where to go next.

## WHERE — Current implementation
- `cmd_init` in `reqmap.py` — creates `requirements/`, conditionally seeds `.reqmapignore` via `_reqmapignore_seed` (which applies the self-hosting exception), then calls `cmd_extract` → `cmd_check(update_lock=True)` → `cmd_map`, and prints the guided summary.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-INIT-425
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# Init creates the requirements folder if it is

> `init` creates the requirements folder if it is missing.

Scenario: init creates a missing requirements directory
  Given  a repo with no `requirements/` folder
  When   `cmd_init` runs
  Then   `requirements/` exists afterward

## Members in code (auto)




--------------------


---
id: REQ-INIT-426
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# Init writes a starter .reqmapignore only if the

> `init` writes a starter `.reqmapignore` only if the repo has none. It never overwrites
> one that is already there.

Scenario: an existing .reqmapignore is left byte-for-byte
  Given  a repo with `.reqmapignore` already containing `my-custom-glob/**`
  When   `cmd_init` runs
  Then   `.reqmapignore`'s content is unchanged

## Members in code (auto)




--------------------


---
id: REQ-INIT-427
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# The starter file lists scripts/reqmap.py. Without that line

> The starter file lists `scripts/reqmap.py`. Without that line, the engine's own tags
> look like they point at requirements that do not exist.

Scenario: the seeded ignore lists scripts/reqmap.py in a non-self-hosting repo
  Given  a repo with no `.reqmapignore` and no self-hosting requirements
  When   `cmd_init` runs
  Then   the written `.reqmapignore` contains the line `scripts/reqmap.py`

## Members in code (auto)




--------------------


---
id: REQ-INIT-428
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# The starter file also lists .worktrees/ and .claude/worktrees/

> The starter file also lists `.worktrees/**` and `.claude/worktrees/**` — the two places
> an isolated agent worktree is created. Each holds a full second copy of the repo, so
> without those lines every member is counted twice and the copies' tags read as dangling
> refs: errors that are not in the code, in files a clean CI checkout never has.

Scenario: the seeded ignore prunes both worktree-copy locations
  Given  a fresh repo with no `.reqmapignore`, after `cmd_init` runs
  When   a tagged file is then copied into `.worktrees/wt1/` and `.claude/worktrees/wt1/`
  Then   `scan_members` counts neither copy — only the original file — as a member

## Members in code (auto)




--------------------


---
id: REQ-INIT-429
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# One exception: if the engine describes itself in

> One exception: if the engine describes itself in this repo, `init` leaves the line out
> and writes a comment saying why. There the engine is ordinary tracked code, so the scan
> keeps reading it.

Scenario: a self-hosting repo's seeded ignore does not ignore the engine
  Given  `requirements/CORE-X-001.md` exists and `scripts/reqmap.py` carries `# implements: CORE-X-001`
  When   `cmd_init` runs
  Then   the written `.reqmapignore` has no live (uncommented) `scripts/reqmap.py` glob, and `scan_members` still counts the engine as a member of `CORE-X-001`

## Members in code (auto)




--------------------


---
id: REQ-INIT-430
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# "Describes itself" means scripts/reqmap.py carries tags whose ids

> "Describes itself" means `scripts/reqmap.py` carries tags whose ids match requirements
> already in the repo.

Scenario: a tag pointing at no local requirement is not self-hosting
  Given  `requirements/CORE-Y-002.md` exists and `scripts/reqmap.py` carries `# implements: CORE-GHOST-999` (an id with no matching file)
  When   `cmd_init` runs
  Then   the self-hosting exception does not fire: the written `.reqmapignore` still ignores `scripts/reqmap.py`

## Members in code (auto)




--------------------


---
id: REQ-INIT-431
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# Init drafts requirements from untagged code, writes the

> `init` drafts requirements from untagged code, writes the lock, then builds the map, in
> that order. When it finishes, the repo passes the gate and has a map.

Scenario: the lock and map cover the requirements init just drafted
  Given  an untagged `app.py` in a repo with no `requirements/`
  When   `cmd_init` runs
  Then   `_reqlock.json` carries a hash for the newly drafted `DRAFT-*` requirement, proving draft ran before the lock was written

## Members in code (auto)




--------------------


---
id: REQ-INIT-432
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# Init ends with a short summary naming one

> `init` ends with a short summary naming one next command: `reqmap.py next`. Not a list
> of every option.

Scenario: the summary names next, not the full command list
  Given  a repo with extractable code
  When   `cmd_init` runs
  Then   its output contains "reqmap.py next" but names none of "confirm", "dupes", "search" or "coverage"

## Members in code (auto)




--------------------


---
id: REQ-INIT-433
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# If nothing was drafted, init says so in

> If nothing was drafted, `init` says so in plain words and points at `new`. It never
> prints a count summary that hides an empty result.

Scenario: an extraction-free repo gets a distinct empty-result message
  Given  a repo containing only `README.txt` (no extractable code)
  When   `cmd_init` runs
  Then   its output says "no requirements were extracted" and points at `reqmap.py new`, never "0 requirement(s) tracked"

## Members in code (auto)




--------------------


---
id: REQ-INIT-434
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# Running init twice is safe. The second run

> Running `init` twice is safe. The second run refreshes the lock and the map, then prints
> the summary again.

Scenario: a second init run exits clean and reprints the summary
  Given  a repo already initialized by one `cmd_init` run
  When   `cmd_init` runs again
  Then   it exits 0 and its output again contains "reqmap.py next"

## Members in code (auto)




--------------------


---
id: REQ-INIT-435
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-INIT-012]
superseded_by:
---

# A second run never deletes a requirement someone

> A second run never deletes a requirement someone wrote, and never edits an existing
> `.reqmapignore`.

Scenario: a hand-authored requirement and .reqmapignore survive a re-run
  Given  a hand-written `requirements/CORE-FOO-001.md` and an existing `.reqmapignore`
  When   `cmd_init` runs (no `--wipe`)
  Then   `CORE-FOO-001.md` still exists and `.reqmapignore`'s content is unchanged

## Members in code (auto)
