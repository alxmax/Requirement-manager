---
id: ARCH-NEXT-013
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-MAP-007]
satisfies: [SYS-REPORT-105]
superseded_by:
milestone: v1.12
lint_exempt: [ac-count-high]
---

# What-should-I-do-next report

## Description
> Faced with a whole project of requirements, it's hard to know what to work on first. This command
> looks at every requirement, spots the gaps — ones with no code, no tests, or unanswered questions —
> and prints them as a short, prioritised to-do list right in the terminal. It puts the most urgent
> work at the top so you can just start. Without it, you'd have to open the visual map and eyeball the
> risk yourself to figure out where to begin.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     risk signal     one open gap the engine spots on a requirement: no code, no test,
                     an unanswered question, an unreviewed draft.
     bucket          one named group of items in the report, e.g. "Needs tests".
     the Risk tab    the Risk diagram of the generated map, which reads the same signals.
     membership tag  a comment in code naming a requirement, such as `implements:`.
     code_root       the directory `next` walks to find files; a caller may omit it. -->

**What it collects**
- `next` groups every requirement's open risk signals into action buckets.
- `next` reads those signals from `_risk_signals` and their wording from `RISK_ADVICE`, the
  same two sources that drive the Risk tab. There is never a second signal path.

**What it prints first**
- `next` prints a progress header `N requirement(s) · X confirmed · Y tested · Z draft(s)`
  before the buckets.
- In that header, `tested` counts the requirements that have a `tested-by` member.

**Which buckets it shows**
- `next` surfaces exactly the actionable buckets: `unimplemented` (Orphans), `untested`
  (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review).
- `next` prints those four buckets in that order, most urgent first.
- `next` also prints two advisory buckets below the four action buckets: `Granularity` (a
  requirement with more acceptance criteria than lint's `LINT_AC_MAX`) and `Redundancy`
  (requirements whose Description states the same obligation, byte-identical once
  normalized).
- Granularity's set comes from `_oversize`, the one predicate `lint_requirement`'s
  `ac-count-high` check also calls — the same threshold, the same `LINT_STATUSES` scope, and
  the same `lint_exempt: [ac-count-high]` honoring, so `next` and `lint` never disagree on
  which requirement is oversize.
- Redundancy's set comes from `_redundant_groups`, the exact-match floor `dupes` also uses.
- Neither advisory bucket changes `next`'s exit code.
- `next` omits `blast-radius`, because that signal is a caution, not a task.
- `next` surfaces every scannable file that carries no membership tag as an "Untagged files"
  bucket, ranked lowest of all.
- That bucket omits prose in the auto-draft "ignore" bucket (`CLAUDE.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE`, `_`-prefixed files): those are invisible to reqmap by contract.
- `next` skips that untagged scan when the caller gives no `code_root`.
- An Orphans item may have members recorded in the committed `_map.json` that this scan did
  not find. Then `next` adds a note naming one such member and suggesting `--code <dir>`.
  The note is advice; the item stays in the bucket.

**How it orders a bucket**
- Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:`
  score, then by id.
- Priority rank runs `must-have` < `should-have` < `could-have` < `wont-have`. A requirement
  with no `priority` ranks last.
- `next` tags an item whose `risk:` is 2 or more with `[REVIEW]`.
- `next` names the requirement file to open, as `requirements/<ID>.md`.

**How much it shows**
- By default `next` shows at most the top few items of a bucket.
- `next` prints a `... N more` line when a bucket holds more items than it showed.
- With `--all`, `next` lists every item.
- The "Untagged files" bucket truncates the same way as the others.

**When there is nothing to do**
- With a registry that holds no requirements, `next` prints a distinct "no requirements yet"
  message pointing at `init`/`new`. `next` never prints the all-clear line in that case.
- With requirements but no open signal, `next` prints the all-clear line.

**What it never does**
- `next` is deterministic and writes no file.
- `next` always exits zero. The report is advice, not a gate.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- Each bucket is truncated independently, so a higher-priority bucket is never hidden below a longer lower-priority one.
- The dedup of a draft's intent question lives inside the shared `_risk_signals` source, which is why `next` and the Risk tab report the same signals for the same requirement.
- The untagged-files scan is skipped when no `code_root` is supplied — the usual case for unit-test callers.
- A reviewed requirement may legitimately appear in more than one bucket (e.g. a confirmed requirement both `untested` and `unverified-intent`) — these are two distinct actions, by design. A `draft` never double-lists, because its `unverified-intent` is suppressed at the source (subsumed by `unreviewed`).
- `next` is the prioritized worklist; `findings` remains the exhaustive raw list of every open verify-intent bullet (including drafts). The two answer different questions — this divergence is intentional and documented, not drift.
- `risk:` ordering only discriminates extract-authored drafts (hand-authored requirements have no `risk:` field → score 0, ordered by id).
- `next` has printed Granularity and Redundancy since ADR-0020 shipped; this contract omitted both until 2026-09-03, when the gap was fixed alongside unifying Granularity's threshold with lint's `LINT_AC_MAX` — previously `next` used its own unscoped 5-AC threshold with no `lint_exempt` honoring, so `next` and `lint` could report different sets for the same corpus (`ARCH-DECOMPOSE-050`'s notes record the matching fix on lint's side).

## Cases (= tests)
CASE-1
  Given  any corpus
  When   `next` runs
  Then   the output starts with a progress header carrying the confirmed/tested/draft counts

CASE-2
  Given  a confirmed requirement with implementing code but no `tested-by`
  When   `next` runs
  Then   it is listed under "Needs tests" with `requirements/<ID>.md`

CASE-3
  Given  a draft requirement with an open verify bullet
  When   `next` runs
  Then   it is listed under "Drafts to review" and NOT under "Needs intent review" (source dedup)

CASE-4
  Given  a confirmed requirement with an open Verify-intent bullet
  When   `next` runs
  Then   it is listed under "Needs intent review"

CASE-5
  Given  a bucket with more items than the top-N
  When   `next` runs
  Then   the default view truncates and prints a `... N more` line; `--all` lists every item

CASE-6
  Given  a draft with `risk: 2` (REVIEW) and a `risk: 0` draft in one bucket
  When   `next` runs
  Then   the REVIEW draft is ordered first and tagged `[REVIEW]`

CASE-7
  Given  a `must-have`, a `should-have`, and a no-`priority` requirement in one bucket
  When   `next` runs
  Then   they are ordered must-have, should-have, then no-priority

CASE-8
  Given  an empty registry, or one with no open signals
  When   `next` runs
  Then   it prints the "no requirements yet" message or the all-clear line respectively,
         writes no files, and returns 0

CASE-9
  Given  scannable files in the repo with no membership tag
  When   `next` runs with a code_root
  Then   they are listed under "Untagged files" with a `reqmap.py draft` suggestion

CASE-10
  Given  a confirmed requirement with no scanned member, whose node in the committed `_map.json` records one
  When   `next` runs with a `reqs_dir`
  Then   the Orphans bucket carries a note naming that member and `--code`

CASE-11
  Given  a confirmed requirement with more acceptance criteria than `LINT_AC_MAX`, not exempt
  When   `next` runs
  Then   it is listed under "Granularity" with its AC count and `requirements/<ID>.md`

CASE-12
  Given  two confirmed requirements whose Description states the same obligation, word for word
  When   `next` runs
  Then   they are listed together under "Redundancy" as one group

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana starts her day unsure what's most important. She runs `reqmap.py next` and sees a header — "12 requirement(s) · 8 confirmed · 5 tested · 2 draft(s)" — followed by tidy buckets: "Orphans" (requirements with no code) on top, then "Needs tests", then "Drafts to review". One item is tagged `[REVIEW]` and names the exact file to open. She picks the top item and gets to work, no HTML map needed.

## WHERE — Current implementation
- `cmd_next`, `_risk_score`, and `_scan_untagged` in `reqmap.py` — prints the header, builds a minimal node per requirement, collects `_risk_signals`, orders each bucket by `risk:` score then id, truncates to the top-N unless `--all`, and prints `RISK_ADVICE` text. The draft intent-dedup is in `_risk_signals` (shared with the Risk tab). `_scan_untagged` adds the untagged-files bucket using the same walk as `scan_members`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-NEXT-527
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next groups every requirement's open risk signals into

> `next` groups every requirement's open risk signals into action buckets.

Scenario: an untested confirmed requirement lands in the Needs-tests bucket
  Given  a confirmed requirement with an `implements` member but no `tested-by` member
  When   `cmd_next` runs
  Then   its output carries a "Needs tests" bucket naming that requirement

## Members in code (auto)




--------------------


---
id: REQ-NEXT-528
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next reads those signals from _risk_signals and their

> `next` reads those signals from `_risk_signals` and their wording from `RISK_ADVICE`,
> the same two sources that drive the Risk tab. There is never a second signal path.

Scenario: a bucket's advice line matches RISK_ADVICE verbatim
  Given  a confirmed requirement carrying the `untested` signal
  When   `cmd_next` runs
  Then   the "Needs tests" bucket's `-> ...` line equals `RISK_ADVICE["untested"]` exactly

## Members in code (auto)




--------------------


---
id: REQ-NEXT-529
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next prints a progress header N requirement(s) ·

> `next` prints a progress header `N requirement(s) · X confirmed · Y tested · Z draft(s)`
> before the buckets.

Scenario: the header names all four counts
  Given  one confirmed-and-tested requirement and one draft requirement
  When   `cmd_next` runs
  Then   its first line reads "2 requirement(s) · 1 confirmed · 1 tested · 1 draft(s)"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-530
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# In that header, tested counts the requirements that

> In that header, `tested` counts the requirements that have a `tested-by` member.

Scenario: implements-only members do not count as tested
  Given  two confirmed requirements: one with a `tested-by` member, one with only an `implements` member
  When   `cmd_next` runs
  Then   the header reads "1 tested", not "2 tested"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-531
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next surfaces exactly the actionable buckets: unimplemented (Orphans)

> `next` surfaces exactly the actionable buckets: `unimplemented` (Orphans), `untested`
> (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to
> review).

Scenario: all four action bucket labels appear for their matching signal
  Given  one confirmed requirement with no members, one confirmed-untested, one confirmed with an open Verify-intent bullet, one draft
  When   `cmd_next` runs
  Then   its output contains "Orphans", "Needs tests", "Needs intent review" and "Drafts to review"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-532
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next prints those four buckets in that order

> `next` prints those four buckets in that order, most urgent first.

Scenario: Orphans prints before Needs tests, before Needs intent review, before Drafts
  Given  one requirement triggering each of the four action signals
  When   `cmd_next` runs
  Then   "Orphans" appears before "Needs tests", which appears before "Needs intent review", which appears before "Drafts to review"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-533
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next omits blast-radius, because that signal is a

> `next` omits `blast-radius`, because that signal is a caution, not a task.

Scenario: a high-fan-in requirement's blast-radius signal never prints
  Given  a confirmed, tested requirement with three dependents (triggers `blast-radius`)
  When   `cmd_next` runs
  Then   its output never contains the word "blast-radius"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-534
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next surfaces every scannable file that carries no

> `next` surfaces every scannable file that carries no membership tag as an "Untagged
> files" bucket, ranked lowest of all.

Scenario: Untagged files prints after every action bucket
  Given  a draft requirement (triggers "Drafts to review") plus an untagged `orphan.py` in the code root
  When   `cmd_next` runs with that code root
  Then   "Untagged files" appears after "Drafts to review" in the output

## Members in code (auto)




--------------------


---
id: REQ-NEXT-535
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# That bucket omits prose in the auto-draft "ignore"

> That bucket omits prose in the auto-draft "ignore" bucket (`CLAUDE.md`, `TODO.md`,
> `CHANGELOG.md`, `LICENSE`, `_`-prefixed files): those are invisible to reqmap by
> contract.

Scenario: CLAUDE.md and TODO.md never appear as untagged
  Given  an untagged `CLAUDE.md`, `TODO.md`, `README.md` and `a.py` in the code root
  When   `_scan_untagged` runs
  Then   it lists `a.py` and `README.md` but neither `CLAUDE.md` nor `TODO.md`

## Members in code (auto)




--------------------


---
id: REQ-NEXT-536
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next skips that untagged scan when the caller

> `next` skips that untagged scan when the caller gives no `code_root`.

Scenario: no code_root means no Untagged files section at all
  Given  a draft requirement, called without a `code_root` argument
  When   `cmd_next` runs
  Then   its output never contains "Untagged files"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-537
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# An Orphans item may have members recorded in

> An Orphans item may have members recorded in the committed `_map.json` that this scan
> did not find. Then `next` adds a note naming one such member and suggesting `--code
> <dir>`. The note is advice; the item stays in the bucket.

Scenario: an Orphans note names the map-recorded member and --code
  Given  a confirmed requirement with no locally scanned member, whose `_map.json` node records `src/foo.py` as a member
  When   `cmd_next` runs with that `reqs_dir`
  Then   the Orphans bucket still lists the requirement, plus a note naming `src/foo.py` and suggesting `--code <dir>`

## Members in code (auto)




--------------------


---
id: REQ-NEXT-538
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Within a bucket, next orders items by priority

> Within a bucket, `next` orders items by `priority` rank, then by descending extract
> `risk:` score, then by id.

Scenario: equal priority and risk falls back to id order
  Given  two `must-have`, `risk: 0` drafts, "ZZZ-B-002" and "AAA-A-001", in the same bucket
  When   `cmd_next` runs
  Then   "AAA-A-001" is printed before "ZZZ-B-002"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-539
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Priority rank runs must-have < should-have < could-have

> Priority rank runs `must-have` < `should-have` < `could-have` < `wont-have`. A
> requirement with no `priority` ranks last.

Scenario: a no-priority item sorts after a could-have item
  Given  a `could-have` draft and a draft with no `priority` field, in the same bucket
  When   `cmd_next` runs
  Then   the `could-have` draft is printed before the no-priority draft

## Members in code (auto)




--------------------


---
id: REQ-NEXT-540
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next tags an item whose risk: is 2

> `next` tags an item whose `risk:` is 2 or more with `[REVIEW]`.

Scenario: a risk: 2 draft is ordered first and tagged REVIEW
  Given  a `risk: 0` draft and a `risk: 2` draft in the same bucket
  When   `cmd_next` runs
  Then   the `risk: 2` draft prints first and its line carries `[REVIEW]`

## Members in code (auto)




--------------------


---
id: REQ-NEXT-541
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next names the requirement file to open, as

> `next` names the requirement file to open, as `requirements/<ID>.md`.

Scenario: an item's line names its requirement file
  Given  a confirmed, untested requirement `CORE-FOO-001`
  When   `cmd_next` runs
  Then   its "Needs tests" line contains "requirements/CORE-FOO-001.md"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-542
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# By default next shows at most the top

> By default `next` shows at most the top few items of a bucket.

Scenario: only the top 3 of 5 items print without --all
  Given  5 drafts in one bucket
  When   `cmd_next` runs with default `top_n=3`
  Then   exactly 3 of the 5 requirement ids appear in the output

## Members in code (auto)




--------------------


---
id: REQ-NEXT-543
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next prints a ... N more line when

> `next` prints a `... N more` line when a bucket holds more items than it showed.

Scenario: a truncated bucket prints a "... N more" line
  Given  5 drafts in one bucket, shown with default `top_n=3`
  When   `cmd_next` runs
  Then   its output contains "more — run `reqmap.py next --all`"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-544
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# With --all, next lists every item

> With `--all`, `next` lists every item.

Scenario: --all prints every item and drops the "more" line
  Given  5 drafts in one bucket
  When   `cmd_next` runs with `show_all=True`
  Then   all 5 requirement ids appear and no "more — run" line is printed

## Members in code (auto)




--------------------


---
id: REQ-NEXT-545
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# The "Untagged files" bucket truncates the same way

> The "Untagged files" bucket truncates the same way as the others.

Scenario: 5 untagged files show only the top 3 by default
  Given  one clean confirmed-tested requirement and a code root holding 5 unrelated untagged scannable files
  When   `cmd_next` runs with that code root and default `top_n=3`
  Then   the "Untagged files" section lists 3 files and a "... 2 more" line

## Members in code (auto)




--------------------


---
id: REQ-NEXT-546
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# With a registry that holds no requirements, next

> With a registry that holds no requirements, `next` prints a distinct "no requirements
> yet" message pointing at `init`/`new`. `next` never prints the all-clear line in that
> case.

Scenario: an empty registry gets its own message, never the all-clear line
  Given  an empty requirements registry
  When   `cmd_next` runs
  Then   its output contains "No requirements yet" and "reqmap.py init", but never "Nothing pending"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-547
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# With requirements but no open signal, next prints

> With requirements but no open signal, `next` prints the all-clear line.

Scenario: a fully clean registry prints the all-clear line
  Given  one confirmed requirement with both `implements` and `tested-by` members and no open questions
  When   `cmd_next` runs
  Then   its output contains "Nothing pending"

## Members in code (auto)




--------------------


---
id: REQ-NEXT-548
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next is deterministic and writes no file

> `next` is deterministic and writes no file.

Scenario: two runs on the same input print byte-identical output
  Given  a fixed corpus with a mix of confirmed, untested and draft requirements
  When   `cmd_next` runs on it twice
  Then   both runs' captured output are identical strings, and no file was created

## Members in code (auto)




--------------------


---
id: REQ-NEXT-549
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
superseded_by:
---

# Next always exits zero. The report is advice

> `next` always exits zero. The report is advice, not a gate.

Scenario: a corpus full of orphans and drafts still exits 0
  Given  three unimplemented confirmed requirements and two drafts with open verify-intent bullets
  When   `cmd_next` runs
  Then   it returns exit code 0

## Members in code (auto)
