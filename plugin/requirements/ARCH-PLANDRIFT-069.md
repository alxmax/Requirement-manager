---
id: ARCH-PLANDRIFT-069
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-SCAN-002, ARCH-GITRUN-067, ARCH-ROADMAP-038]
satisfies: [SYS-SSOT-001]
---

# Plan items whose code has moved on without them

## Description
> The bridge between a plan and the code runs one way: a written item can be turned into a
> requirement, and nothing ever checks the item again. The failure a consumer lived four
> times is the other direction — the code gets fixed and the note stays written. On one
> occasion fourteen of sixteen candidate items were already done, found by opening each file
> by hand. This reads the code references an open item cites and reports two things about
> them, and it closes nothing: a list that verifies itself is the very error it is here to
> catch.

Every bullet below is binding.
- Open plan items are read for the code they cite — file paths and backticked identifiers — and an item citing neither is silent. [[REQ-PLANDRIFT-1002]]
- A cited path that names no file, and a cited identifier absent from the code, are reported as facts; a cited file committed after the item's own date is reported separately, as a reason to re-read. [[REQ-PLANDRIFT-1002]]
- Nothing here changes a plan file, a status or an exit code, and `gate --audit` is the only place it runs.

## Cases
CASE-1
  Given  an open item citing a path that resolves to no file, under a directory that exists
  When   `gate --audit` runs
  Then   the item is reported in the `sure` bucket and the exit code is unchanged

CASE-2
  Given  an open item whose every citation resolves, and one cited file committed after the
         item's date
  When   `gate --audit` runs
  Then   the item is reported as worth re-reading, separately from the `sure` bucket

CASE-3
  Given  a repo whose plan cites nothing that has moved
  When   `gate --audit` runs
  Then   no plan-drift line is printed

## Context
**Notes**
- The four false-positive classes it guards against were measured by a consumer in their
  own first run, not theorised here: extension ordering in the path alternation, a
  shortened path versus a wrong one, the symbol search scope, and a date inherited from the
  section rather than carried per item. Two more were found on this repo's own plan the
  first time it ran: an engine version read as a date, and a path an item exists in order
  to create.
- The known limit, and it is the important one: a fix that leaves the path, the symbol and
  the line exactly where they were is invisible to any check of form. The only signal there
  is the date, and a date is not proof — it is a reason to read.


--------------------


---
id: REQ-PLANDRIFT-1002
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PLANDRIFT-069]
---

# Reading an item's citations, and the six ways that goes wrong

## Description
> Every rule below exists because a specific false positive was paid for. Four came from the
> consumer's first run over their own 56-item list; two more from this repo's plan the first
> time the check ran here. Written as behaviour rather than as comments so that removing one
> breaks a test instead of quietly re-admitting nine false positives.

Every bullet below is binding.
- The path pattern matches its longest extension first, so a `.tsx` file is never read as a
  `.ts` file with a stray character after it.
- A cited path resolves against a real one when its segments are a suffix of that path's
  segments; a shortened path is not a wrong path, and a partial filename is not a match.
- A cited path that names no file is reported only when something like it exists: its
  basename lives elsewhere, or its directory is occupied. A path with neither is ground the
  item exists in order to break.
- A cited identifier is looked for across the whole scanned code, never only in the files
  the item names, and prose files are not searched for it.
- An item with no date of its own inherits the most recent date written in its section's
  prose, and a date followed by a further number is a version, not a date.
- An item already marked done is not examined.

## Cases
CASE-1 — the longest extension wins
  Given  an item citing `src/EmployeeDocumentList.tsx` and a repo holding that file
  When   its citations are read
  Then   the cited path is `src/EmployeeDocumentList.tsx`, not `src/EmployeeDocumentList.ts`

CASE-2 — a shortened path resolves, a wrong one does not
  Given  a repo holding `apps/api/app/common/errors.py`
  When   `app/common/errors.py` and `app/documents/errors.py` are resolved against it
  Then   the first resolves to that file and the second does not

CASE-3 — a partial filename is not a suffix match
  Given  a repo holding `pkg/clarify.py`
  When   `my_clarify.py` is resolved against it
  Then   it resolves to nothing

CASE-4 — a path nothing resembles is a target, not a stale reference
  Given  an open item citing `docs/history/ARCHIVE.md` in a repo with no `docs/` at all
  When   the plan drift is computed
  Then   the item is not reported

CASE-5 — a date is a date only when no number follows it
  Given  an item whose only date-shaped text is the engine version `2026-06-19.1`
  When   its effective date is computed
  Then   it has none of its own, and inherits its section's

CASE-6 — an item with no date inherits its section's
  Given  a section whose prose carries `2026-09-05` and an item under it carrying no date
  When   effective dates are computed
  Then   that item's date is `2026-09-05`
