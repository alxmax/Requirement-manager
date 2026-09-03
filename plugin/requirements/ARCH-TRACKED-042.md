---
id: ARCH-TRACKED-042
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-SCAN-002, ARCH-CHECK-006]
satisfies: [SYS-GATE-102]
---

# Untracked members reported

## Description
> A generated artifact this tool commits must depend only on files git tracks. When a
> member lives in a gitignored directory, the map records something a fresh checkout has
> no copy of — so the committed map cannot be regenerated anywhere but the machine that
> wrote it, and the failure lands in CI as a mysterious staleness error about a file the
> reader cannot find.

Every bullet below is binding.
- `untracked_members` lists the member files git does not track under the scan root, and the gate warns (never errors) when any exist. [[REQ-TRACKED-936]]

## Cases
CASE-1
  Given  a member file that git does not track
  When   `gate` runs inside a git work tree
  Then   it warns, naming that file and the count of untracked members, and exits 0

CASE-2
  Given  every member file is tracked
  When   `gate` runs
  Then   no untracked-member warning appears

CASE-3
  Given  a scan root that is not a git work tree
  When   `untracked_members` runs
  Then   it returns nothing at all, rather than reporting every member as untracked

## Context
**Terms**
- *tracked*: git has the file in its index; *member*: a file carrying a membership tag for some requirement.

**Notes**
- Untracked is the property that matters, not ignored: a file that is merely uncommitted
  breaks reproducibility exactly as a gitignored one does, and one `git ls-files` call
  answers both.
- Warn-only on purpose. A consumer repo may tag an ignored file deliberately; this nudges
  that choice into the open rather than overruling it.
- The check reads the index, so a member staged but not committed counts as tracked.

**Example**
- A contributor runs a subagent in a gitignored worktree, regenerates the map, and the gate
  names the worktree copies instead of letting CI fail later on a file nobody can see.

**Current implementation**
- `untracked_members` in `reqmap.py`, called from `cmd_check`.


--------------------


---
id: REQ-TRACKED-936
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACKED-042]
---

# Warning when a member is not tracked by git

## Description
> A committed generated artifact — the map — must depend only on files a fresh checkout also
> has. When a member lives in a gitignored or merely-uncommitted file, the local scan can see
> it but CI never will, and the failure shows up later as a mystifying staleness error about a
> file the reader cannot find. This check catches the real cause at the source, before the map
> is even regenerated.

Every bullet below is binding.
- `untracked_members` lists the member files git does not track under the scan root.
- `gate` reports those untracked members in one warning, naming up to five paths and the total count.
- The warning names the two remedies: commit the files, or exclude them in `.reqmapignore`.
- `untracked_members` reports nothing and the gate stays silent when the scan root is not
  a git work tree, or git is unavailable.
- The warning never changes the exit code.

## Cases
CASE-1 — untracked_members names a git-untracked member file
  Given  a member file that git does not track under the scan root
  When   `untracked_members` runs
  Then   it returns that file's path in its result list

CASE-2 — the gate warning caps the named files and reports the total
  Given  seven untracked member files
  When   `gate` runs inside a git work tree
  Then   its warning names five of them by path and states the total count of 7, and
         `gate` exits 0 — the warning never changes the exit code

CASE-3 — the untracked warning names both fixes
  Given  a gate run reporting an untracked member
  When   the warning text is inspected
  Then   it names committing the file and adding it to `.reqmapignore` as the two remedies

CASE-4 — the check stays silent outside a git work tree
  Given  a scan root that is not a git repository
  When   `untracked_members` runs
  Then   it returns nothing and `gate` prints no untracked-member warning

