---
id: ARCH-PROMOTE-011
status: draft
level: architecture
layer: feature
owner: Alex
milestone: v1.08
depends_on: [ARCH-PARSE-001, ARCH-DRIFT-003]
satisfies: [SYS-AUTHOR-101]
---

# Confirmation is a human's answer, and an edit takes it back

## Description
> A requirement is `confirmed` when a human has read it and said so. That was a command
> for a long time, and a command is the wrong shape for it: `confirm <ID>` let anything
> that could type — a script, an agent, a habit — record a human's judgement. Worse, the
> judgement then outlived the thing it was about. A contract could be rewritten line by
> line and keep the `confirmed` its old text earned, because nothing connected editing to
> re-validating. Confirmation is now asked for and written by hand, and an edit takes it
> back automatically.

Every bullet below is binding.
- There is **no `confirm` command.** A status is set by editing the frontmatter, which is
  what a human sign-off is: someone read it and wrote it down. The engine still owns the
  edit mechanics, so nothing else has to get them right. [[REQ-PROMOTE-894]] details the
  behaviour.
- **An edited confirmed contract goes back to `draft`.** When `sync` finds that a
  `confirmed` or `implemented` requirement's binding content no longer matches the lock,
  it writes `draft` into that requirement and advances the baseline.
  [[REQ-PROMOTE-974]] details the behaviour.
- **`--accept-drift` is the escape hatch, and it is a human saying so:** it keeps the
  status and advances the baseline. It exists because "I edited it and it is still valid"
  is a real answer — it just has to be given, not assumed.
- **The invariant that a confirmed requirement points at code is enforced by the gate,
  not by a command.** `RM006` is an error, so a status written by hand with no
  `implements:` member fails at the next run.

## Cases
CASE-1
  Given  a `confirmed` requirement whose contract has just been edited
  When   `sync` runs without `--accept-drift`
  Then   its frontmatter reads `status: draft`, the run says so by name, and the lock
         advances

CASE-2
  Given  the same requirement
  When   `sync --accept-drift` runs instead
  Then   the status stays `confirmed` and the lock advances

CASE-3
  Given  a requirement whose status was set to `confirmed` by hand with no `implements:`
         member
  When   `gate` runs
  Then   it reports `RM006` as an error

## Context
**Notes**
- **What this costs, said plainly:** a demoted requirement stops being enforced. The gate
  no longer requires an `implements:` member for it and no longer drift-checks it, until a
  human confirms it again. That is why the demotion is printed loudly, by name, with the
  sentence "These no longer gate" — the danger is not the demotion, it is a demotion
  nobody noticed.
- `confirm` was removed on 2026-09-05 at the user's request, together with its two guard
  requirements (REQ-PROMOTE-895, REQ-PROMOTE-896), which described refusals a command can
  no longer make. The gate covers the first; the second was advisory.
- The demotion writes through the same surgical status edit the command used, so a
  CRLF-committed file stays CRLF and a `status:` line's inline comment survives.

## WHERE
- `plugin/scripts/reqmap.py` — `_write_frontmatter_status`, and the demotion branch in
  `cmd_check`'s lock update.


--------------------


---
id: REQ-PROMOTE-894
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
---

# A surgical edit to the status line

## Description
> Rewriting `status: confirmed` to `status: draft` risks touching the wrong line, losing a
> trailing comment, or nudging the file's formatting — and on Windows, silently flipping a
> CRLF file to LF. The engine finds and rewrites only the frontmatter's first `status:`
> line, so the rest of the file is guaranteed untouched.

Every bullet below is binding.
- `_write_frontmatter_status` edits only the value of the first `status:` line in the
  leading frontmatter.
- It preserves that line's indentation and any trailing inline comment.
- It leaves the body untouched, byte for byte.
- It preserves the file's own line endings, per line, so a file with mixed endings keeps
  every line it did not touch exactly as it was.
- In a module file holding several requirements, it edits the block of the requirement it
  was given, not the first block in the file.

## Cases
CASE-1 — only the frontmatter's first status line changes
  Given  a requirement whose body also contains the word "status:" in prose
  When   the status is rewritten
  Then   only the frontmatter's first `status:` line changes; the prose text is untouched

CASE-2 — the status line's formatting survives
  Given  a frontmatter line `status: confirmed  # reviewed by A`
  When   the status is rewritten to `draft`
  Then   the line becomes `status: draft  # reviewed by A`, comment and spacing intact

CASE-3 — the body is never touched
  Given  a requirement with a body
  When   the status is rewritten
  Then   every byte after the frontmatter stays identical

CASE-4 — the right block in a module file
  Given  a file holding several requirements, one of the later ones targeted
  When   the status is rewritten
  Then   that block's status changes and the others are untouched


--------------------


---
id: REQ-PROMOTE-974
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
---

# An edited contract loses its confirmation

## Description
> A `confirmed` status is a claim that a human read THIS text. Once the text changes, the
> claim is about something that no longer exists. Before this, `sync` refused to advance
> the baseline and told the caller to pass `--accept-drift`, which made accepting the edit
> the easy path and re-reading it the hard one. Now the safe outcome is the default.

Every bullet below is binding.
- When `sync` updates the lock and finds a `confirmed` or `implemented` requirement whose
  binding hash differs from the committed one, it writes `status: draft` into that
  requirement.
- **A brand-new requirement is not drift.** A requirement absent from the lock has no
  previous text to have changed, so it is never demoted.
- The run **names every demoted requirement**, with its previous status, and states that
  they no longer gate.
- After demoting, the lock and the member lock advance in the same run. The next run is
  clean, so the demotion happens once, not on every sync.
- `--accept-drift` skips the demotion entirely: the status stays and the baseline
  advances.
- The in-memory status is updated too, so the same run's own summary counts the
  requirement as a draft rather than reporting a status it has just changed.

## Cases
CASE-1 — an edited confirmed contract is demoted, and the lock advances
  Given  a `confirmed` requirement, synced once, whose contract is then edited
  When   `sync` runs without `--accept-drift`
  Then   the file reads `status: draft`, the output names it, and a second `sync` reports
         no drift

CASE-2 — a new requirement is not demoted
  Given  a `confirmed` requirement that has never been in the lock
  When   `sync` runs
  Then   its status is unchanged and nothing is reported as demoted

CASE-3 — accept-drift keeps the status
  Given  a `confirmed` requirement whose contract was edited
  When   `sync --accept-drift` runs
  Then   the status stays `confirmed` and the lock advances
