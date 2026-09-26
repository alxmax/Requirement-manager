---
id: ARCH-COVERAGE-029
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.6
depends_on: [ARCH-SCAN-002, ARCH-NEXT-013]
satisfies: [SYS-REPORT-105]
---

# Untagged-code coverage signal

## Description
> reqmap links code to requirements by tags, but nothing reported how much code is
> linked to nothing — code traceable to no requirement was only visible by running
> `draft`/`plan`. This surfaces that gap as a read-only count, so a reviewer sees at
> a glance whether code is drifting ahead of the spec. A review on 2026-06-21
> rejected enforcing coverage as a hard gate — it is gameable with hollow tags and
> conflicts with the model where a requirement is a behavior, not a file — and
> approved only this non-blocking visibility signal.

Every bullet below is binding.
- `health` reports the count of scannable code files carrying no membership tag as a read-only `untagged` signal — present only when a code root is scanned, and never affecting the score or exit code. [[REQ-COVERAGE-836]] details the behaviour.
- The untagged bucket and the per-directory coverage ratio exclude the same by-design-untaggable files, named in one list. [[REQ-UNTAGGEDSET-1007]]
- The coverage ratio states which files it excluded. [[REQ-UNTAGGEDSET-1007]]

## Cases
CASE-1
  Given  a code root with one tagged and one untagged scannable file
  When   `health --json` runs with that code root
  Then   the `untagged` key equals 1 and the score is unchanged by it

CASE-2
  Given  no code root (a unit-test caller)
  When   `health --json` runs
  Then   the output carries no `untagged` key

CASE-3
  Given  an untagged scannable file that is then tagged or added to `.reqmapignore`
  When   `health --json` runs again with the code root
  Then   the `untagged` count drops by one (the file is silenced from the signal)

## Context
**Terms**
- membership tag  a comment in code naming a requirement: `implements`, `tested-by`,
- `generated-from` or `validated-against`.
- untagged code   a scannable code file carrying no membership tag, so it is traced to
- no requirement.
- the denominator the set of files the count is taken over.
- health score    the single percentage `health` prints for the whole corpus.

**Notes**
- This is the read-only half of coverage; the matching list of which files is the "Untagged files" bucket in `next` ([[ARCH-NEXT-013]]). Same denominator, two surfaces.
- It measures tag PRESENCE, not tag QUALITY: a hollow `# implements:` tag counts as covered. This is accepted — a hard gate would make hollow tags the rational way to pass CI, which is why this stays advisory.
- Granularity is per file, not per member; the engine does not parse members.

**Current implementation**
- The untagged-count block in `cmd_health` (`reqmap.py`), reusing `_scan_untagged` (ARCH-NEXT-013) when a code root is supplied. Surfaced read-only in `health` text output and `--json`.


--------------------


---
id: REQ-COVERAGE-836
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
satisfies: [ARCH-COVERAGE-029]
---

# Counting untagged code as a read-only signal

## Description
> Code can drift ahead of the spec with nobody noticing, because a tag's absence was
> only visible by running `draft`/`plan`. `health` now counts scannable files with no
> membership tag and reports it as `untagged` — visible, but never a gate: a review
> rejected enforcing it, since a hollow tag would then become the rational way to
> pass CI.

Every bullet below is binding.
- The capability reports the count of scannable code files that carry no membership tag —
  "untagged code", code traced to no requirement.
- The denominator is exactly `_scan_untagged`'s (see [[ARCH-NEXT-013]]): the files matched by
  the scanner extension walk, minus `.reqmapignore`.
- Any membership tag counts a file as covered. The tags are `implements`, `tested-by`,
  `generated-from` and `validated-against`.
- The `health` command includes this count as an `untagged` integer key in its `--json` output.
- The `health` command also includes it as a labelled line in its text output.
- The `untagged` key is absent, not zero, when no code root is scanned — a unit-test caller,
  for example. An existing `--json` consumer therefore keeps its schema.
- The signal is read-only and is never a gate. It changes no exit code.
- The signal never lowers the health score, because it counts files, not requirements.
- A file is silenced from the count either by tagging it, or by adding it to `.reqmapignore`.
- There is no separate exemption mechanism.

## Cases
CASE-1 — the untagged count reflects untagged files
  Given  a code root with one tagged file and one untagged scannable file
  When   `health --json` runs with that code root
  Then   the `untagged` key equals 1, the health score is unchanged, and the exit code stays 0

CASE-2 — the untagged count shares its denominator with _scan_untagged
  Given  a code root scanned by both `health` and `_scan_untagged` directly
  When   both are run over the same tree
  Then   the `untagged` count equals the length of `_scan_untagged`'s file list

CASE-3 — a tested-by tag alone covers a file
  Given  an untagged file that is then given only a `# tested-by:` comment
  When   `health --json` runs
  Then   that file no longer counts toward `untagged`

CASE-4 — health --json exposes the untagged integer key
  Given  a code root with one untagged scannable file
  When   `health --json` runs
  Then   its output is valid JSON carrying an integer `untagged` key

CASE-5 — health's text output labels the untagged count
  Given  a code root with one untagged scannable file
  When   `health` runs without `--json`
  Then   its text output includes a labelled line naming the untagged count

CASE-6 — the untagged key is absent without a code root
  Given  a `health --json` invocation with no code root supplied
  When   it runs
  Then   the output carries no `untagged` key at all

CASE-7 — tagging or ignoring a file drops it from the count
  Given  an untagged file, then tagged in one run and `.reqmapignore`-listed in another
  When   `health --json` runs after each change
  Then   the `untagged` count drops by one either way, with no separate exemption mechanism


--------------------


---
id: REQ-UNTAGGEDSET-1007
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.10
satisfies: [ARCH-COVERAGE-029]
---

# Two untagged reports, one list

## Description
> Two reports counted untagged files against different denominators. The risk bucket
> skipped files that carry no tag by contract — decision records, CHANGELOG, LICENSE,
> issue templates — while the per-directory ratio counted them. A consumer tagged every
> file the bucket named and the ratio still read 270/272: two root files that appeared in
> no bucket, were named nowhere, and put the ratio's ceiling permanently below 100%. A
> number nobody can move is a number nobody reads.

Every bullet below is binding.
- `untaggable_by_design` is the single predicate for a scannable file that will never carry
  a membership tag: prose in the auto-draft "ignore" bucket, and repo boilerplate.
- The untagged bucket and the per-directory coverage ratio both exclude exactly what that
  predicate excludes, so both name one list.
- The coverage report states how many files it excluded and why, and points at the other
  report, so the exclusion is visible rather than silent.
- The JSON form carries `excluded_by_design` alongside the per-directory rows.
- Both reports skip what git ignores: a file kept out of the repo is not code the repo
  forgot to trace. Without git, nothing is skipped.

## Cases
CASE-1 — the two reports agree
  Given  a repository holding one untagged source file plus a CHANGELOG, a SECURITY.md and
         a decision record
  When   the untagged bucket and the coverage ratio are both computed
  Then   they name the same single file

CASE-2 — only the real gap is listed
  Given  that same repository
  When   the untagged bucket is computed
  Then   it contains the untagged source file and nothing else

CASE-3 — the exclusion is stated
  Given  that same repository
  When   the coverage report runs
  Then   it names the count of excluded files, says they carry no tag by contract, and
         points at the other report; the JSON form carries the same count

CASE-4 — the ratio is reachable
  Given  every file the bucket names has been tagged
  When   the coverage report runs
  Then   it reads 100% and the bucket is empty

CASE-5 — a file git ignores is not a gap
  Given  a git work tree holding an untagged `notes.py` that `.git/info/exclude` names
  When   the untagged bucket and the coverage ratio are both computed
  Then   neither counts `notes.py`, and the same tree without git lists it in the bucket

## Context
**Notes**
- The fix is exclusion, not inclusion: counting a file that cannot be tagged puts the
  ceiling below 100% forever, and the author has no action that moves it. Excluding it and
  saying so leaves a number that reaching is possible and means something.
