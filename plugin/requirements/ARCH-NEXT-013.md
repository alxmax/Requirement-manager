---
id: ARCH-NEXT-013
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.12
depends_on: [ARCH-MAP-007]
satisfies: [SYS-REPORT-105]
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
- `next` groups every requirement's open risk signals — read from the same `_risk_signals`/`RISK_ADVICE` source the Risk tab uses — into action buckets, behind a progress header. [[REQ-NEXT-883]]
- `next` surfaces exactly the actionable buckets, most urgent first: `unimplemented` (Orphans), `untested` (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review), plus advisory Granularity/Redundancy buckets and an Untagged-files bucket. [[REQ-NEXT-884]]
- Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:` score, then by id, and names the file to open. [[REQ-NEXT-885]]
- By default `next` shows at most the top few items of a bucket, truncating each independently with a `... N more` line; `--all` lists everything. [[REQ-NEXT-886]]
- With no requirements at all, `next` prints a distinct message pointing at `init`/`new`; otherwise it prints the all-clear line when nothing is open. Either way it writes no file and always exits 0. [[REQ-NEXT-887]]

## Cases
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

## Context
**Terms**
- risk signal     one open gap the engine spots on a requirement: no code, no test,
- an unanswered question, an unreviewed draft.
- bucket          one named group of items in the report, e.g. "Needs tests".
- the Risk tab    the Risk diagram of the generated map, which reads the same signals.
- membership tag  a comment in code naming a requirement, such as `implements:`.
- code_root       the directory `next` walks to find files; a caller may omit it.

**Notes**
- Each bucket is truncated independently, so a higher-priority bucket is never hidden below a longer lower-priority one.
- The dedup of a draft's intent question lives inside the shared `_risk_signals` source, which is why `next` and the Risk tab report the same signals for the same requirement.
- The untagged-files scan is skipped when no `code_root` is supplied — the usual case for unit-test callers.
- A reviewed requirement may legitimately appear in more than one bucket (e.g. a confirmed requirement both `untested` and `unverified-intent`) — these are two distinct actions, by design. A `draft` never double-lists, because its `unverified-intent` is suppressed at the source (subsumed by `unreviewed`).
- `next` is the prioritized worklist; `findings` remains the exhaustive raw list of every open verify-intent bullet (including drafts). The two answer different questions — this divergence is intentional and documented, not drift.
- `risk:` ordering only discriminates extract-authored drafts (hand-authored requirements have no `risk:` field → score 0, ordered by id).
- `next` has printed Granularity and Redundancy since ADR-0020 shipped; this contract omitted both until 2026-09-03, when the gap was fixed alongside unifying Granularity's threshold with lint's `LINT_AC_MAX` — previously `next` used its own unscoped 5-AC threshold with no `lint_exempt` honoring, so `next` and `lint` could report different sets for the same corpus (`ARCH-DECOMPOSE-050`'s notes record the matching fix on lint's side).

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana starts her day unsure what's most important. She runs `reqmap.py next` and sees a header — "12 requirement(s) · 8 confirmed · 5 tested · 2 unreviewed" — followed by tidy buckets: "Orphans" (requirements with no code) on top, then "Needs tests", then "Drafts to review". One item is tagged `[REVIEW]` and names the exact file to open. She picks the top item and gets to work, no HTML map needed.

**Current implementation**
- `cmd_next`, `_risk_score`, and `_scan_untagged` in `reqmap.py` — prints the header, builds a minimal node per requirement, collects `_risk_signals`, orders each bucket by `risk:` score then id, truncates to the top-N unless `--all`, and prints `RISK_ADVICE` text. The draft intent-dedup is in `_risk_signals` (shared with the Risk tab). `_scan_untagged` adds the untagged-files bucket using the same walk as `scan_members`.


--------------------


---
id: REQ-NEXT-883
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# next reads the same risk signals the Risk tab reads

## Description
> `next` does not run a second analysis: it reads `_risk_signals` and `RISK_ADVICE`, the
> exact source the map's Risk diagram already uses, and groups the results into buckets
> behind a one-line progress header. Sharing the source is what keeps the terminal report
> and the visual map from ever disagreeing about what is wrong with a requirement.

Every bullet below is binding.
- `next` groups every requirement's open risk signals into action buckets.
- `next` reads those signals from `_risk_signals` and their wording from `RISK_ADVICE`, the
  same two sources that drive the Risk tab. There is never a second signal path.
- `next` prints a progress header `N requirement(s) · X confirmed · Y tested · Z unreviewed (draft + baseline, the population of the Drafts bucket)`
  before the buckets.
- In that header, `tested` counts the requirements that have a `tested-by` member.

## Cases
CASE-1 — an untested confirmed requirement lands in the Needs-tests bucket
  Given  a confirmed requirement with an `implements` member but no `tested-by` member
  When   `cmd_next` runs
  Then   its output carries a "Needs tests" bucket naming that requirement

CASE-2 — a bucket's advice line matches RISK_ADVICE verbatim
  Given  a confirmed requirement carrying the `untested` signal
  When   `cmd_next` runs
  Then   the "Needs tests" bucket's `-> ...` line equals `RISK_ADVICE["untested"]` exactly

CASE-3 — the header names all four counts
  Given  one confirmed-and-tested requirement and one draft requirement
  When   `cmd_next` runs
  Then   its first line reads "2 requirement(s) · 1 confirmed · 1 tested · 1 unreviewed"

CASE-4 — implements-only members do not count as tested
  Given  two confirmed requirements: one with a `tested-by` member, one with only an `implements` member
  When   `cmd_next` runs
  Then   the header reads "1 tested", not "2 tested"


--------------------


---
id: REQ-NEXT-884
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# Four action buckets, two advisory ones, and untagged files

## Description
> The four action buckets — Orphans, Needs tests, Needs intent review, Drafts to review —
> print most urgent first, because that order is the point of the whole command: start at
> the top. Granularity and Redundancy print below them, sharing their exact thresholds with
> `lint` and `dupes` so the three commands never disagree about which requirement is
> oversize or duplicated. Untagged files ranks lowest of all.

Every bullet below is binding.
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
- That bucket also omits repository boilerplate that never carries a tag by design: decision
  records under an `adr/` or `decisions/` directory, issue and pull-request templates,
  `SECURITY.md`, `CODE_OF_CONDUCT.md` and dependabot configuration (`_UNTAGGED_NOISE`).
- `next` skips that untagged scan when the caller gives no `code_root`.
- An Orphans item may have members recorded in the committed `_map.json` that this scan did
  not find. Then `next` adds a note naming one such member and suggesting `--code <dir>`.
  The note is advice; the item stays in the bucket.

## Cases
CASE-1 — all four action bucket labels appear for their matching signal
  Given  one confirmed requirement with no members, one confirmed-untested, one confirmed with an open Verify-intent bullet, one draft
  When   `cmd_next` runs
  Then   its output contains "Orphans", "Needs tests", "Needs intent review" and "Drafts to review"

CASE-2 — Orphans prints before Needs tests, before Needs intent review, before Drafts
  Given  one requirement triggering each of the four action signals
  When   `cmd_next` runs
  Then   "Orphans" appears before "Needs tests", which appears before "Needs intent review", which appears before "Drafts to review"

CASE-3 — a high-fan-in requirement's blast-radius signal never prints
  Given  a confirmed, tested requirement with three dependents (triggers `blast-radius`)
  When   `cmd_next` runs
  Then   its output never contains the word "blast-radius"

CASE-4 — Untagged files prints after every action bucket
  Given  a draft requirement (triggers "Drafts to review") plus an untagged `orphan.py` in the code root
  When   `cmd_next` runs with that code root
  Then   "Untagged files" appears after "Drafts to review" in the output

CASE-5 — CLAUDE.md and TODO.md never appear as untagged
  Given  an untagged `CLAUDE.md`, `TODO.md`, `README.md` and `a.py` in the code root
  When   `_scan_untagged` runs
  Then   it lists `a.py` and `README.md` but neither `CLAUDE.md` nor `TODO.md`

CASE-6 — no code_root means no Untagged files section at all
  Given  a draft requirement, called without a `code_root` argument
  When   `cmd_next` runs
  Then   its output never contains "Untagged files"

CASE-7 — an Orphans note names the map-recorded member and --code
  Given  a confirmed requirement with no locally scanned member, whose `_map.json` node records `src/foo.py` as a member
  When   `cmd_next` runs with that `reqs_dir`
  Then   the Orphans bucket still lists the requirement, plus a note naming `src/foo.py` and suggesting `--code <dir>`


--------------------


---
id: REQ-NEXT-885
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# Priority, then risk score, then id decide bucket order

## Description
> A bucket is only useful if the top item really is the most urgent one. `next` sorts by
> declared `priority` first (`must-have` before `should-have` before `could-have` before
> `wont-have`, no-priority last), breaks ties by a draft's extract-authored `risk:` score,
> and falls back to id — and tags a `risk: 2`-or-higher item `[REVIEW]` so it stands out.

Every bullet below is binding.
- Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:`
  score, then by id.
- Priority rank runs `must-have` < `should-have` < `could-have` < `wont-have`. A requirement
  with no `priority` ranks last.
- `next` tags an item whose `risk:` is 2 or more with `[REVIEW]`.
- `next` names the requirement file to open, as `requirements/<ID>.md`.

## Cases
CASE-1 — equal priority and risk falls back to id order
  Given  two `must-have`, `risk: 0` drafts, "ZZZ-B-002" and "AAA-A-001", in the same bucket
  When   `cmd_next` runs
  Then   "AAA-A-001" is printed before "ZZZ-B-002"

CASE-2 — a no-priority item sorts after a could-have item
  Given  a `could-have` draft and a draft with no `priority` field, in the same bucket
  When   `cmd_next` runs
  Then   the `could-have` draft is printed before the no-priority draft

CASE-3 — a risk: 2 draft is ordered first and tagged REVIEW
  Given  a `risk: 0` draft and a `risk: 2` draft in the same bucket
  When   `cmd_next` runs
  Then   the `risk: 2` draft prints first and its line carries `[REVIEW]`

CASE-4 — an item's line names its requirement file
  Given  a confirmed, untested requirement `CORE-FOO-001`
  When   `cmd_next` runs
  Then   its "Needs tests" line contains "requirements/CORE-FOO-001.md"


--------------------


---
id: REQ-NEXT-886
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# Each bucket truncates to a top few, --all shows everything

## Description
> A worklist that dumps hundreds of items is not a worklist. `next` caps each bucket
> independently at a small default count, so a long lower-priority bucket can never push a
> shorter, more urgent one off the screen, and prints a `... N more` line naming the
> escape hatch (`--all`) rather than silently hiding items.

Every bullet below is binding.
- By default `next` shows at most the top few items of a bucket.
- `next` prints a `... N more` line when a bucket holds more items than it showed.
- With `--all`, `next` lists every item.
- The "Untagged files" bucket truncates the same way as the others.

## Cases
CASE-1 — only the top 3 of 5 items print without --all
  Given  5 drafts in one bucket
  When   `cmd_next` runs with default `top_n=3`
  Then   exactly 3 of the 5 requirement ids appear in the output

CASE-2 — a truncated bucket prints a "... N more" line
  Given  5 drafts in one bucket, shown with default `top_n=3`
  When   `cmd_next` runs
  Then   its output contains "more — run `reqmap.py next --all`"

CASE-3 — --all prints every item and drops the "more" line
  Given  5 drafts in one bucket
  When   `cmd_next` runs with `show_all=True`
  Then   all 5 requirement ids appear and no "more — run" line is printed

CASE-4 — 5 untagged files show only the top 3 by default
  Given  one clean confirmed-tested requirement and a code root holding 5 unrelated untagged scannable files
  When   `cmd_next` runs with that code root and default `top_n=3`
  Then   the "Untagged files" section lists 3 files and a "... 2 more" line


CASE-5 — repository boilerplate is not an untagged file
  Given  an untagged `a.py`, an ADR under `docs/adr/`, an issue template and a `SECURITY.md`
  When   `next` scans for untagged files
  Then   only `a.py` is listed

--------------------


---
id: REQ-NEXT-887
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# An empty registry and a clean one get different messages

## Description
> "Nothing to show" has two different causes, and `next` says which: a registry with no
> requirements at all points the reader at `init`/`new`, while a registry that is simply
> clean — nothing open — prints the all-clear line instead. Neither case writes a file, and
> `next` always exits 0: it is advice, not a gate.

Every bullet below is binding.
- With a registry that holds no requirements, `next` prints a distinct "no requirements yet"
  message pointing at `init`/`new`. `next` never prints the all-clear line in that case.
- With requirements but no open signal, `next` prints the all-clear line.
- `next` is deterministic and writes no file.
- `next` always exits zero. The report is advice, not a gate.

## Cases
CASE-1 — an empty registry gets its own message, never the all-clear line
  Given  an empty requirements registry
  When   `cmd_next` runs
  Then   its output contains "No requirements yet" and "reqmap.py init", but never "Nothing pending"

CASE-2 — a fully clean registry prints the all-clear line
  Given  one confirmed requirement with both `implements` and `tested-by` members and no open questions
  When   `cmd_next` runs
  Then   its output contains "Nothing pending"

CASE-3 — two runs on the same input print byte-identical output
  Given  a fixed corpus with a mix of confirmed, untested and draft requirements
  When   `cmd_next` runs on it twice
  Then   both runs' captured output are identical strings, and no file was created

CASE-4 — a corpus full of orphans and drafts still exits 0
  Given  three unimplemented confirmed requirements and two drafts with open verify-intent bullets
  When   `cmd_next` runs
  Then   it returns exit code 0

