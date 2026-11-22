---
id: ARCH-NEXT-013
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.12
depends_on: [ARCH-MAP-007]
satisfies: [SYS-REPORT-105]
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
- `next` surfaces exactly the actionable buckets, most urgent first: `unimplemented` (Orphans), `untested` (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review), plus advisory Granularity/Redundancy buckets. [[REQ-NEXT-884]]
- `next` lists every scannable file that carries no membership tag in an Untagged-files bucket, ranked lowest, with a suggestion to run `init`. [[REQ-NEXTUNTAGGED-1050]]
- Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:` score, then by id, and names the file to open. [[REQ-NEXT-885]]
- By default `next` shows at most the top few items of a bucket, truncating each independently with a `... N more` line; `--all` lists everything. [[REQ-NEXT-886]]
- With no requirements at all, `next` prints a distinct message pointing at `init`/`new`; otherwise it prints the all-clear line when nothing is open. Either way it writes no file and always exits 0. [[REQ-NEXT-887]]
- `next` closes with the plan's own gaps — the horizon work `ROADMAP.md` leaves open and `_planning.json` does not schedule — and the health record counts the same gaps. [[REQ-PLANGAPS-1033]]
- `next` names the tests the gate cannot see missing: confirmed cases with no `# verifies:` tag, test files standing for several requirements with no case tagged, and exemption keys left empty. [[REQ-TESTGAPS-1088]]
- `next` names each tagged test that cannot fail, the sync'd map carries the same list, and the viewer's Report counts it. [[REQ-TESTGAPS-1146]]
- The same three shapes are read from C and C++ tests: GoogleTest, Catch2, CppUTest and Unity. [[REQ-TESTGAPS-1147]]

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
  Given  an empty registry, or one with no open signals
  When   `next` runs
  Then   it prints the "no requirements yet" message or the all-clear line respectively,
         writes no files, and returns 0

CASE-4
  Given  an open `ROADMAP.md` item that `_planning.json` does not schedule
  When   `next` runs with a code root
  Then   it is listed last, under "Plan", with what the item is missing

## Context
**Terms**
- risk signal     one open gap the engine spots on a requirement: no code, no test,
- an unanswered question, an unreviewed draft.
- bucket          one named group of items in the report, e.g. "Needs tests".
- the Risk tab    the Risk diagram of the generated map, which reads the same signals.
- membership tag  a comment in code naming a requirement, such as `implements:`.
- code_root       the directory `next` walks to find files; a caller may omit it.

**Notes**
- The cases above exercise the report end to end; each bucket's own cases live on the child that owns that bucket.
- Each bucket is truncated independently, so a higher-priority bucket is never hidden below a longer lower-priority one.
- The dedup of a draft's intent question lives inside the shared `_risk_signals` source, which is why `next` and the Risk tab report the same signals for the same requirement.
- The untagged-files scan is skipped when no `code_root` is supplied — the usual case for unit-test callers.
- A reviewed requirement may legitimately appear in more than one bucket (e.g. a confirmed requirement both `untested` and `unverified-intent`) — these are two distinct actions, by design. A `draft` never double-lists, because its `unverified-intent` is suppressed at the source (subsumed by `unreviewed`).
- `next` is the prioritized worklist; `findings` remains the exhaustive raw list of every open verify-intent bullet (including drafts). The two answer different questions — this divergence is intentional and documented, not drift.
- `risk:` ordering only discriminates extract-authored drafts (hand-authored requirements have no `risk:` field → score 0, ordered by id).
- `next` has printed Granularity and Redundancy since ADR-0020 shipped; this contract omitted both until 2026-09-03, when the gap was fixed alongside unifying Granularity's threshold with lint's `LINT_AC_MAX` — previously `next` used its own unscoped 5-AC threshold with no `lint_exempt` honoring, so `next` and `lint` could report different sets for the same corpus (`ARCH-DECOMPOSE-050`'s notes record the matching fix on lint's side).

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana starts her day unsure what's most important. She runs `reqmap.py gate --risk` and sees a header — "12 requirement(s) · 8 confirmed · 5 tested · 2 unreviewed" — followed by tidy buckets: "Orphans" (requirements with no code) on top, then "Needs tests", then "Drafts to review". One item is tagged `[REVIEW]` and names the exact file to open. She picks the top item and gets to work, no HTML map needed.

**Current implementation**
- `cmd_next`, `_risk_score`, and `_scan_untagged` in `reqmap.py` — prints the header, builds a minimal node per requirement, collects `_risk_signals`, orders each bucket by `risk:` score then id, truncates to the top-N unless `--all`, and prints `RISK_ADVICE` text. The draft intent-dedup is in `_risk_signals` (shared with the Risk tab). `_scan_untagged` adds the untagged-files bucket using the same walk as `scan_members`.


--------------------


---
id: REQ-NEXT-883
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
satisfies: [ARCH-NEXT-013]
distinct_from: [REQ-SHOW-919, REQ-MAPDIAGRAMS-878]
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

## Context
**Notes**
- `distinct_from: REQ-SHOW-919` - `REQ-SHOW-919` prints one requirement's signals and exits non-zero on an unknown id; this groups every requirement's signals into buckets. Both read `_risk_signals`, which is the point.
- `distinct_from: REQ-MAPDIAGRAMS-878` - `REQ-MAPDIAGRAMS-878` draws the flagged requirements as the Risk diagram in `_map.md`; this prints them as action buckets.

--------------------


---
id: REQ-NEXT-884
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
satisfies: [ARCH-NEXT-013]
---

# Four action buckets and two advisory ones

## Description
> The four action buckets — Orphans, Needs tests, Needs intent review, Drafts to review —
> print most urgent first, because that order is the point of the whole command: start at
> the top. Granularity and Redundancy print below them, sharing their exact thresholds with
> `lint` and `dupes` so the three commands never disagree about which requirement is
> oversize or duplicated.

Every bullet below is binding.
- `next` surfaces exactly the actionable buckets: `unimplemented` (Orphans), `untested`
  (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review).
- A draft with an open Verify-intent bullet is listed under Drafts to review only, never
  also under Needs intent review.
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

CASE-4 — an Orphans note names the map-recorded member and --code
  Given  a confirmed requirement with no locally scanned member, whose `_map.json` node records `src/foo.py` as a member
  When   `cmd_next` runs with that `reqs_dir`
  Then   the Orphans bucket still lists the requirement, plus a note naming `src/foo.py` and suggesting `--code <dir>`

CASE-5 — a draft's open intent question is not listed twice
  Given  a draft requirement with an open Verify-intent bullet
  When   `cmd_next` runs
  Then   it is listed under "Drafts to review" and NOT under "Needs intent review" (source dedup)

CASE-6 — an oversize requirement is listed under Granularity
  Given  a confirmed requirement with more acceptance criteria than `LINT_AC_MAX`
  When   `cmd_next` runs
  Then   it is listed under "Granularity" with a split suggestion

CASE-7 — identical obligations are listed as one Redundancy group
  Given  two confirmed requirements whose Description states the same obligation, word for word
  When   `next` runs
  Then   they are listed together under "Redundancy" as one group


--------------------


---
id: REQ-NEXTUNTAGGED-1050
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
distinct_from: [REQ-UNTAGGEDSET-1007]
---

# Untagged files, ranked lowest

## Description
> A file that carries no membership tag is invisible to every other bucket, so `next`
> names it. It ranks below every requirement bucket, because tagging a file is housekeeping
> next to a requirement with no code, and it leaves out the prose and boilerplate that never
> carry a tag by design, or the list would bury the real gaps.

Every bullet below is binding.
- `next` surfaces every scannable file that carries no membership tag as an "Untagged files"
  bucket, ranked lowest of all.
- That bucket's advice line suggests running `reqmap.py init`.
- That bucket omits prose in the auto-draft "ignore" bucket (`CLAUDE.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE`, `_`-prefixed files): those are invisible to reqmap by contract.
- That bucket also omits repository boilerplate that never carries a tag by design: decision
  records under an `adr/` or `decisions/` directory, issue and pull-request templates,
  `SECURITY.md`, `CODE_OF_CONDUCT.md` and dependabot configuration (`_UNTAGGED_NOISE`).
- `next` skips that untagged scan when the caller gives no `code_root`.

## Cases
CASE-1 — an untagged file is listed with an init suggestion
  Given  a clean confirmed-tested requirement and an untagged `orphan.py` in the code root
  When   `cmd_next` runs with that code root
  Then   "Untagged files" lists `orphan.py` with a `reqmap.py init` suggestion

CASE-2 — Untagged files prints after every action bucket
  Given  a draft requirement (triggers "Drafts to review") plus an untagged `orphan.py` in the code root
  When   `cmd_next` runs with that code root
  Then   "Untagged files" appears after "Drafts to review" in the output

CASE-3 — CLAUDE.md and TODO.md never appear as untagged
  Given  an untagged `CLAUDE.md`, `TODO.md`, `README.md` and `a.py` in the code root
  When   `_scan_untagged` runs
  Then   it lists `a.py` and `README.md` but neither `CLAUDE.md` nor `TODO.md`

CASE-4 — no code_root means no Untagged files section at all
  Given  a draft requirement, called without a `code_root` argument
  When   `cmd_next` runs
  Then   its output never contains "Untagged files"

## Context
**Notes**
- `distinct_from: REQ-UNTAGGEDSET-1007` - `REQ-UNTAGGEDSET-1007` defines which files are untagged; this orders that list for the risk report.


--------------------


---
id: REQ-NEXT-885
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
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

CASE-5 — must-have, then should-have, then no priority
  Given  a `must-have`, a `should-have`, and a no-`priority` requirement in one bucket
  When   `cmd_next` runs
  Then   they are ordered must-have, should-have, then no-priority


--------------------


---
id: REQ-NEXT-886
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
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
  Then   its output contains "more — run `reqmap.py gate --risk --all`"

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
milestone: v3.2
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

--------------------


---
id: REQ-PLANGAPS-1033
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# The plan's own gaps are a bucket in the worklist

## Description
> "What should I do next" had two answers in two places: `gate --risk` read the corpus,
> while the three signals that read the PLAN — a `Now`/`Next` item no bar schedules, a
> `Later` item with no `unpark:`, an item naming a requirement that does not exist —
> printed only at the tail of `sync` and inside `gate --audit`. A reader who opens the
> worklist sees a clean screen while the roadmap carries unscheduled work. The signals do
> not change; the screen that asks the question gets them.

Every bullet below is binding.
- `next` prints a `Plan` bucket, after the corpus buckets, naming each open `Now`/`Next`
  item that no bar in `_planning.json` schedules, each open `Later` item carrying no
  `unpark:`, and each item whose `req:` is not in the corpus.
- Each Plan line names which of the three it is, and the item's own text.
- A repo with no `ROADMAP.md` gets no `Plan` bucket and no `plan_gaps` key: the absence of
  a plan is not a finding.
- The health record carries `plan_gaps`, the count of exactly what the bucket names, from
  the same computation — absent, not zero, when there is nothing to count.
- A plan gap alone keeps `next` off the all-clear line, and counts as one of the
  categories in the "N item(s) need attention" header.
- The `Plan` bucket truncates to the same top few as every other bucket, and `--all`
  lists every gap.

## Cases
CASE-1 — an unscheduled Now item is named
  Given  a `ROADMAP.md` with one open `Now` item and a `_planning.json` with no bar for it
  When   `next` runs
  Then   the `Plan` bucket names that item and says it has no bar

CASE-2 — a parked item with no condition is named
  Given  an open `Later` item carrying no `unpark:`
  When   `next` runs
  Then   the `Plan` bucket names it and says it has no `unpark:`

CASE-3 — an item pointing at nothing is named with the id it points at
  Given  a `Now` item carrying `req: ARCH-GONE-999`, absent from the corpus
  When   `next` runs
  Then   the `Plan` bucket names the item and the missing id

CASE-4 — no roadmap, no bucket and no key
  Given  a repo with no `ROADMAP.md`
  When   `next` and `gate --risk --json` run
  Then   no `Plan` bucket is printed and the record carries no `plan_gaps` key

CASE-5 — the count and the bucket cannot disagree
  Given  a corpus whose roadmap holds three gaps
  When   `gate --risk` and `gate --risk --json` run
  Then   `plan_gaps` equals the number the `Plan` bucket heading reports

CASE-6 — a plan gap alone is not "nothing pending"
  Given  a corpus clean on every risk bucket whose roadmap carries one gap
  When   `next` runs
  Then   the all-clear line is not printed and the `Plan` bucket is

## Context
**Notes**
- The three gaps keep their existing definitions: `_roadmap_plan_gaps` is the one
  predicate behind both the audit's line and this bucket, so the two surfaces cannot come
  to mean different things by the same word.
- Deliberately NOT a gate rule. Whether a plan is scheduled is a planning decision, and
  the hook runs `gate` on every commit — see [[ARCH-ROADMAP-038]] and `docs/adr/0020`.
- `risk.py` reads `mapdata` at call time, not at import: `mapdata` reads `_risk_signals`
  from `risk`, so a module-level import would close the cycle. It is the engine's second
  such import, after `health._link_sync_errors`.

---
id: REQ-TESTGAPS-1088
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
distinct_from: [REQ-ACVERIFY-822]
---

# The worklist names the tests the gate cannot see missing

## Description
> The gate checks a requirement's cases only once one of them carries a `# verifies:` tag,
> so a confirmed requirement with none passes in silence: one corpus stood at 3% of its
> cases tagged with a green gate. A `tested-by` line counts one file as the test of every
> requirement it names, and an exemption key left empty reads like an exemption and is
> none. The gate stays as it is; the worklist says what it cannot.

Every bullet below is binding.
- `next` prints a `Cases without a test` bucket naming each confirmed requirement, not
  `test_exempt` and not exempt from implementation, whose automatable cases are not all
  tagged, with how many of how many are missing, most missing first. A requirement with no
  case tagged at all is included.
- `next` prints a `Shared test files` bucket naming each file that is the `tested-by` of
  three requirements or more and carries no `# verifies:` tag for any case.
- `next` prints an `Empty exemptions` bucket naming each `lint_exempt`, `test_exempt` or
  `gate_exempt` key present with no value.
- Each bucket truncates to the same top few as every other bucket, `--all` lists all of
  it, and any of them keeps `next` off the all-clear line.
- None of them is a gate finding, and a repository that runs only `gate` and `sync` never
  loads the code behind them.

## Cases
CASE-1 — a confirmed requirement with no case tagged is named
  Given  a confirmed requirement with three cases and none tagged, and one with every case tagged
  When   `next` runs
  Then   only the first is named, as 3 of 3 cases missing

CASE-2 — a file that stands for several requirements is named
  Given  one test file that is the `tested-by` of three requirements and tags no case
  When   `next` runs
  Then   the `Shared test files` bucket names it with the count 3

CASE-3 — an empty exemption key is named
  Given  a requirement whose frontmatter carries `test_exempt:` with no value
  When   `next` runs
  Then   the `Empty exemptions` bucket names the requirement and the key

CASE-4 — a test gap alone is not "nothing pending"
  Given  a corpus clean on every other bucket, with one confirmed case untagged
  When   `next` runs
  Then   the all-clear line is not printed and the `Cases without a test` bucket is

## Context
**Notes**
- `distinct_from: REQ-ACVERIFY-822` - `REQ-ACVERIFY-822` warns in the gate about a requirement's untagged cases once it has adopted per-case tagging; this names, outside the gate, the requirements that never adopted it.
- Measured on 2026-09-28 across four corpora: 27, 21 and 97 confirmed requirements had
  a `tested-by` file and no case tagged, and one corpus carried 17 empty exemption keys.

---
id: REQ-TESTGAPS-1146
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# The worklist names the tagged tests that cannot fail

## Description
> A `# verifies:` tag closes a case however the test under it is written. A test that
> asserts nothing, asserts only a constant, or compares an expression with itself proves
> the case on paper and checks nothing, and every count downstream calls the case tested.
> The tag cannot tell; the test's own code can.

Every bullet below is binding.
- `next` prints a `Tests that cannot fail` bucket naming each Python function whose name
  starts with `test`, that a `# verifies:` tag sits in or directly above, and whose body
  makes no assertion, makes only assertions on a constant, or makes only
  `assertEqual`/`assertIs` calls whose two arguments are the same expression; each row gives
  the file, the line, the test, which of the three it is and the cases it closes.
- An assertion is an `assert` statement, a call whose name starts with `assert`, `fail`,
  `raises`, `check`, `expect` or `verify`, or a call to a function of the same file that
  itself asserts.
- A function not named `test*` is not judged. C and C++ tests are read by
  `REQ-TESTGAPS-1147`; a test in any other language is not judged.
- `sync` writes the same list under `trace.vacuous` in `_map.json`, outside the freshness
  comparison like the rest of `trace`; the viewer's Report counts it in its numbers, lists
  it under Problem types and recommends a fix when it is not empty.
- The bucket truncates like every other bucket and is never a gate finding.

## Cases
CASE-1 — a test with no assertion is named
  Given  a `test_*` function tagged `# verifies: REQ-A-001#CASE-1` whose body only calls the code
  When   the tagged tests are read
  Then   it is named as `no assertion`, closing `REQ-A-001#CASE-1`

CASE-2 — a constant or a self-comparison is named, a real assertion is not
  Given  one tagged test asserting `assertTrue(True)`, one asserting `assertEqual(f(x), f(x))`
         and one asserting `assertEqual(f(x), 3)`
  When   the tagged tests are read
  Then   the first is `constant assertion`, the second `compares a value with itself`, and the
         third is not named

CASE-3 — what cannot be read is not judged
  Given  a tagged function named `main` with no assertion, a tagged test that calls a helper of
         the same file that asserts, and a tagged test in a `.js` file
  When   the tagged tests are read
  Then   none of the three is named

CASE-4 — the worklist and the map carry the list
  Given  a corpus with one tagged test that asserts nothing
  When   `next` runs and `sync` writes the map
  Then   `next` prints `Tests that cannot fail (1)` and `_map.json` carries the test under
         `trace.vacuous`

CASE-5 — the Report shows it
  Given  a map whose `trace.vacuous` names one test
  When   the viewer's Report renders
  Then   its numbers count 1 test that cannot fail and Problem types lists the test

## Context
**Notes**
- Measured on 2026-11-22 on this repository: 3 of the tagged tests compare a value with
  itself, all three determinism checks run in one process; a script whose failure is its exit
  code was the only false positive of a first draft, and is why only `test*` functions are
  judged.

---
id: REQ-TESTGAPS-1147
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEXT-013]
---

# C and C++ tests that cannot fail are named too

## Description
> A C or C++ repository tags its GoogleTest or Unity tests with `// verifies:` the same way a
> Python one does, and the same tests prove nothing: a `TEST` body that only runs the code, an
> `EXPECT_TRUE(true)`, an `EXPECT_EQ(f(x), f(x))`. The brace reader the engine already has for
> C and C++ finds each test's body, so the three shapes can be read there too.

Every bullet below is binding.
- A C or C++ test is a top-level block the brace reader finds, opened by `TEST`, `TEST_F`,
  `TEST_P`, `TYPED_TEST`, `TYPED_TEST_P`, `TEST_CASE`, `TEST_CASE_METHOD` or `SCENARIO`, or a
  function whose name starts with `test`; it is judged when a `verifies:` tag sits in it or in
  the comment block directly above it.
- An assertion is a call to an `EXPECT_*`, `ASSERT_*`, `TEST_ASSERT*`, `TEST_FAIL*`, `FAIL`,
  `ADD_FAILURE*`, `REQUIRE*`, `CHECK*` or `*_EQUAL*` macro or to `assert`; a call to a function
  of the same file that asserts, or to any function whose name starts with `assert`, `fail`,
  `check`, `expect` or `verify`, counts as one.
- The test is named, with the same three kinds as a Python test, when it has no assertion, when
  every assertion has one argument that is `true`, `false`, `nullptr`, `NULL` or an integer, or
  when every assertion is an `EQ`/`EQUAL` macro whose first two arguments are the same text.
- Comments and string literals are blanked before macros and parentheses are read, so a macro
  named in a string is no assertion and a parenthesis in a string does not split an argument.
- A file whose braces do not balance is skipped, and a repository whose tagged tests are all
  Python never loads this reader.

## Cases
CASE-1 — a GoogleTest test with no assertion is named
  Given  a `TEST(Suite, Runs)` whose body only calls the code, tagged in the comment above it
  When   the tagged tests are read
  Then   it is named as `no assertion`, with `TEST(Suite, Runs)` and its line

CASE-2 — a constant or a self-comparison is named, a real assertion is not
  Given  a tagged `TEST` asserting `EXPECT_TRUE(true)`, a tagged `TEST_F` asserting
         `EXPECT_EQ(f(1), f(1))` and a tagged `TEST` asserting `EXPECT_EQ(f(1), 3)`
  When   the tagged tests are read
  Then   the first is `constant assertion`, the second `compares a value with itself`, and the
         third is not named

CASE-3 — a helper or a string does not mislead it
  Given  a tagged test calling a same-file helper that asserts, a tagged test calling
         `check_frame(...)` from another file, a tagged test asserting
         `EXPECT_STREQ(name(), "a(b")`, and a tagged function `helper_main` with no assertion
  When   the tagged tests are read
  Then   none of them is named

CASE-4 — a Unity test is read and the list reaches the worklist
  Given  a `.c` file whose tagged `void test_x(void)` asserts `TEST_ASSERT_EQUAL(f(), f())`
  When   `next` runs
  Then   `Tests that cannot fail (1)` names `void test_x(void)` as `compares a value with itself`

CASE-5 — what the reader cannot read is skipped
  Given  a tagged `.cpp` test file whose braces do not balance
  When   the tagged tests are read
  Then   nothing is named for it and nothing fails
