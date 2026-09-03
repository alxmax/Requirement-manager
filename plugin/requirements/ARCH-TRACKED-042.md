---
id: ARCH-TRACKED-042
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: [ARCH-SCAN-002, ARCH-CHECK-006]     # ids of bus/other capabilities this builds on
satisfies: [SYS-GATE-102]
superseded_by:       # <ID>, if replaced
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Untracked members reported

## Description
> A generated artifact this tool commits must depend only on files git tracks. When a
> member lives in a gitignored directory, the map records something a fresh checkout has
> no copy of — so the committed map cannot be regenerated anywhere but the machine that
> wrote it, and the failure lands in CI as a mysterious staleness error about a file the
> reader cannot find.
Every bullet below is binding.

**Glossary** — *tracked*: git has the file in its index; *member*: a file carrying a
membership tag for some requirement.

**What it does**
- `untracked_members` lists the member files git does not track under the scan root.
- `gate` reports those files in one warning naming up to five of them and the total count.
- The warning names the two remedies: commit the files, or exclude them in `.reqmapignore`.

**What it never does**
- `untracked_members` reports nothing and the gate stays silent when the scan root is not
  a git work tree, or git is unavailable.
- The warning never changes the exit code.

## Verify intent (open questions for the human)
- None — the rule comes from two observed failures in this repo, not from inference.

## Notes & known limitations (informative)
- Untracked is the property that matters, not ignored: a file that is merely uncommitted
  breaks reproducibility exactly as a gitignored one does, and one `git ls-files` call
  answers both.
- Warn-only on purpose. A consumer repo may tag an ignored file deliberately; this nudges
  that choice into the open rather than overruling it.
- The check reads the index, so a member staged but not committed counts as tracked.

## Cases (= tests)
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

## Example — in practice (optional, non-binding)
- A contributor runs a subagent in a gitignored worktree, regenerates the map, and the gate
  names the worktree copies instead of letting CI fail later on a file nobody can see.

## WHERE — Current implementation
- `untracked_members` in `reqmap.py`, called from `cmd_check`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-TRACKED-760
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACKED-042]
superseded_by:
---

# Untracked_members lists the member files git does not

> `untracked_members` lists the member files git does not track under the scan root.

Scenario: untracked_members names a git-untracked member file
  Given  a member file that git does not track under the scan root
  When   `untracked_members` runs
  Then   it returns that file's path in its result list

## Members in code (auto)




--------------------


---
id: REQ-TRACKED-761
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACKED-042]
superseded_by:
---

# Gate reports those files in one warning naming

> `gate` reports those files in one warning naming up to five of them and the total count.

Scenario: the gate warning caps the named files and reports the total
  Given  seven untracked member files
  When   `gate` runs inside a git work tree
  Then   its warning names five of them by path and states the total count of 7

## Members in code (auto)




--------------------


---
id: REQ-TRACKED-762
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACKED-042]
superseded_by:
---

# The warning names the two remedies: commit the

> The warning names the two remedies: commit the files, or exclude them in
> `.reqmapignore`.

Scenario: the untracked warning names both fixes
  Given  a gate run reporting an untracked member
  When   the warning text is inspected
  Then   it names committing the file and adding it to `.reqmapignore` as the two remedies

## Members in code (auto)




--------------------


---
id: REQ-TRACKED-763
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACKED-042]
superseded_by:
---

# Untracked_members reports nothing and the gate stays silent

> `untracked_members` reports nothing and the gate stays silent when the scan root is not
> a git work tree, or git is unavailable.

Scenario: the check stays silent outside a git work tree
  Given  a scan root that is not a git repository
  When   `untracked_members` runs
  Then   it returns nothing and `gate` prints no untracked-member warning

## Members in code (auto)




--------------------


---
id: REQ-TRACKED-764
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACKED-042]
superseded_by:
---

# The warning never changes the exit code

> The warning never changes the exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
