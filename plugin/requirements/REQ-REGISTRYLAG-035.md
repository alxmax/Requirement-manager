---
id: REQ-REGISTRYLAG-035
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-HEALTH-017]
satisfies: [NEED-SSOT-001]
milestone: v2.12
---

# Registry-lag signal — commits since the requirements dir was last touched

> `health` reports whether the requirements that exist are coherent, but not
> whether the registry as a whole has gone stale while code moved on. A downstream
> consumer's registry sat frozen for 18 days across ~40 code commits while a
> money value drifted with no requirement update — nothing in `health` surfaced
> that the spec had stopped tracking reality. This adds a read-only count of how
> many commits have landed since the requirements dir was last touched, so a
> reviewer sees at a glance that code is racing ahead of the spec. It is the
> temporal complement to the untagged-code coverage signal ([[REQ-COVERAGE-029]]):
> coverage answers "is this code traced?", lag answers "has the registry moved
> lately at all?". Per the Senate audit that governs the coverage signal
> (2026-06-21), advisory visibility only — never a hard gate.

## WHAT — Contract (normative)
- The capability shall report the number of commits on `HEAD` since the most recent commit that touched the requirements directory (`reqs_dir`), as "registry lag".
- The count shall be computed from git only: the last commit touching `reqs_dir` (`git log -1 -- <reqs_dir>`) and the commit count from there to `HEAD` (`git rev-list --count`). It shall not parse requirement contents.
- The `health` command shall include this count: as a `commits_since_req_touch` integer key in its `--json` output, and as a labelled line in its text output emitted only when the count is greater than zero (a lag of 0 is the healthy case and needs no line).
- The signal shall be read-only and shall never be a gate: it shall not change any exit code, and it shall never lower the health score, because it is a repo-wide temporal fact, not a per-requirement axis.
- The `commits_since_req_touch` key shall be absent (not zero) whenever the value is unmeasurable — no code root supplied, `code_root` is not a git worktree, git is unavailable, or `reqs_dir` has no commit in history — so existing `--json` consumers keep their schema and a missing reading is never mistaken for a fresh registry.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent; scope and severity mirror the settled Senate decision on the sibling coverage signal ([[REQ-COVERAGE-029]]).

## WHAT — Notes & known limitations (informative)
- It measures RECENCY of any touch, not QUALITY of the update: a whitespace edit to one requirement resets the lag to 0. Accepted — like coverage, this is an advisory nudge, not proof the spec is current.
- Granularity is whole-repo, not per requirement; it answers whether the registry as a body has moved, not which requirement is stale.
- A shallow clone or a repo whose first commit already contained `reqs_dir` still reports correctly; only a genuinely absent git history or an untracked `reqs_dir` yields the absent (None) reading.

## HOW — Acceptance (= tests)
AC-1
  Given  a git repo whose requirements dir was committed, then two later commits touched only code
  When   `health --json` runs with that code root
  Then   `commits_since_req_touch` equals 2 and the score is unchanged by it

AC-2
  Given  a git repo whose most recent commit touched the requirements dir
  When   `health --json` runs with that code root
  Then   `commits_since_req_touch` is present and equals 0

AC-3
  Given  a code root that is not a git worktree
  When   `health --json` runs with that code root
  Then   the output carries no `commits_since_req_touch` key

## WHERE — Current implementation
- `_commits_since_reqs_touch(code_root, reqs_dir)` in `reqmap.py`, wired into `cmd_health` alongside the untagged block; surfaced read-only in `health` text output and `--json`.

## Links
- Used by: (auto)
## Members in code (auto)
