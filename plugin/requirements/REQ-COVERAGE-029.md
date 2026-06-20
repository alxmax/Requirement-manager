---
id: REQ-COVERAGE-029
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-SCAN-002, REQ-NEXT-013]
satisfies: [NEED-SSOT-001]
milestone: v2.6
---

# Untagged-code coverage signal

> reqmap links code to requirements by tags, but nothing reported how much code is
> linked to nothing — code traceable to no requirement was only visible by running
> `draft`/`plan`. This surfaces that gap as a read-only count, so a reviewer sees at
> a glance whether code is drifting ahead of the spec. A Senate audit (2026-06-21)
> rejected enforcing coverage as a hard gate — it is gameable with hollow tags and
> conflicts with the model where a requirement is a behavior, not a file — and
> approved only this non-blocking visibility signal.

## WHAT — Contract (normative)
- The capability shall report the count of scannable code files that carry no membership tag — "untagged code", code traced to no requirement.
- The denominator shall be exactly `_scan_untagged`'s (see [[REQ-NEXT-013]]): files matched by the scanner extension walk, minus `.reqmapignore`. Any membership tag (`implements`, `tested-by`, `generated-from`, `validated-against`) counts a file as covered.
- The `health` command shall include this count: as an `untagged` integer key in its `--json` output, and as a labelled line in its text output.
- The signal shall be read-only and shall never be a gate: it shall not change any exit code.
- It shall not lower the health score, because it counts files, not requirements.
- The `untagged` key shall be absent (not zero) when no code root is scanned, e.g. a unit-test caller, so existing `--json` consumers keep their schema.
- A file shall be silenced from the count either by tagging it or by adding it to `.reqmapignore`. There shall be no separate exemption mechanism.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent; the Senate audit settled scope and severity.

## WHAT — Notes & known limitations (informative)
- This is the read-only half of coverage; the matching list of which files is the "Untagged files" bucket in `next` ([[REQ-NEXT-013]]). Same denominator, two surfaces.
- It measures tag PRESENCE, not tag QUALITY: a hollow `# implements:` tag counts as covered. This is accepted — the Senate flagged that a hard gate would make hollow tags the rational way to pass CI, which is why this stays advisory.
- Granularity is per file, not per member; the engine does not parse members.

## HOW — Acceptance (= tests)
AC-1
  Given  a code root with one tagged and one untagged scannable file
  When   `health --json` runs with that code root
  Then   the `untagged` key equals 1 and the score is unchanged by it

AC-2
  Given  no code root (a unit-test caller)
  When   `health --json` runs
  Then   the output carries no `untagged` key

AC-3
  Given  an untagged scannable file that is then tagged or added to `.reqmapignore`
  When   `health --json` runs again with the code root
  Then   the `untagged` count drops by one (the file is silenced from the signal)

## WHERE — Current implementation
- The untagged-count block in `cmd_health` (`reqmap.py`), reusing `_scan_untagged` (REQ-NEXT-013) when a code root is supplied. Surfaced read-only in `health` text output and `--json`.

## Links
- Used by: (auto)
## Members in code (auto)
