---
id: REQ-CHECK-006
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002, CORE-DRIFT-003]
satisfies: [NEED-SSOT-001]
superseded_by:
milestone: v1.02
lint_exempt: [ac-count-high, over-scoped]
---

# The gate

> Specs rot when the code moves on and nobody updates the file that describes it.
> This is the guard that catches that: run before every commit, it fails the build when
> code and requirements no longer match. The whole tool exists so this check can run.

## WHAT — Contract (normative)
- It shall report an `ERROR` and exit non-zero for any of: a code tag referencing a
  non-existent capability (dangling tag); an invalid `status` or `layer`; a `depends_on`
  pointing at a missing id; an enforced (`in-progress`/`implemented`/`confirmed`)
  requirement with no `implements:` member (a `layer: need` requirement is exempt —
  see [[REQ-TRACE-020]]).
- It shall report drift as a `WARN` (never an error): a `confirmed` requirement whose
  binding hash differs from the lock, naming the member `file:line` locations to re-check.
- A `confirmed` requirement with no `tested-by:` member shall be a `WARN`, unless its
  frontmatter carries a `test_exempt: <reason>` opt-out or it is a `layer: need` requirement.
- A `confirmed` requirement missing a `## WHAT — Contract` section shall be a `WARN`
  (both `bus` and `feature` layers; does not affect the exit code).
- A `confirmed` requirement missing a `## HOW — Acceptance` section shall be a `WARN`
  (both `bus` and `feature` layers; does not affect the exit code).
- An optional requirement `milestone:` field, when present, shall match the version shape
  `v<digits>[.<digits>…]` (e.g. `v1.14`); a malformed value is a `WARN` (it is roadmap-only
  metadata, never build-critical) and a `deprecated` requirement is exempt.
- A present-but-unreadable `_reqlock.json` shall be a `WARN` (drift skipped, not a crash).
- A lock sidecar (`_reqlock.json` or `_memberlock.json`) that exists on disk but is **not
  git-tracked** shall be a `WARN` naming the file, because an uncommitted lock silently
  disables drift detection on a fresh CI checkout (no baseline to compare against). The
  check is fail-open: silent when git is unavailable or the tree is not a work tree.
- Requirements whose body lacks a `## WHAT — Verify intent` section shall be named in one
  aggregated legacy-schema `WARN` and counted in the summary; the exit code is unaffected.
- It shall print an advisory line with the open verify-intent finding count when > 0,
  without affecting the exit code, and print a summary (requirements, members, errors, warnings).
- With `--update-lock` (exercised by `sync` and the deprecated `check` alias; the `gate` verb is report-only) it shall write the current binding hashes to `requirements/_reqlock.json`.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Why `ac-count-high` and `over-scoped` are exempt: this requirement is the gate's severity
  table, not a bundle of checks. Each individual check the gate runs already has its own
  requirement ([[REQ-TESTLINK-018]], [[REQ-ACVERIFY-019]], [[REQ-MEMBERDRIFT-027]],
  [[REQ-DOCBUNDLE-026]], [[REQ-ORPHANCODE-034]], [[REQ-DRIFTIMPACT-035]]). What remains here
  is one behaviour — which condition is an ERROR, which is a WARN, and what that does to the
  exit code — so every clause and criterion shares a single failure mode. Splitting it would
  scatter the exit-code contract across files instead of clarifying it. Revisit this exemption
  if a clause ever lands here that is not about severity or exit code.
- Errors stop CI (exit 1); warnings do not. Intent sync (promote `baseline → confirmed`)
  is not automatable and surfaces at human review.
- When `CLAUDE_PLUGIN_ROOT` is set and the vendored engine is older than the installed
  plugin's copy, `gate` prints an advisory staleness notice (`warn_if_stale`); the
  variable is unset in CI, so the notice is silent and exit-neutral there.
- The dev-CI version-coherence script `scripts/check_versions.py` (repo root, never seeded
  into consumer repos) enforces plugin manifest alignment as the first step in this repo's
  own CI pipeline (`check_versions.py → gate → map --check → test_reqmap.py`). It is
  outside the plugin scan root and has no requirement of its own; its invariant (semver
  consistency across `plugin.json` + `marketplace.json`) is documented in `CLAUDE.md`.

## HOW — Acceptance (= tests)
AC-1
  Given  a tag referencing a non-existent capability
  When   `gate` runs
  Then   it produces an `ERROR` and exit 1

AC-2
  Given  a `confirmed` requirement with no `implements` member
  When   `gate` runs
  Then   it produces an `ERROR`

AC-3
  Given  an invalid status or layer, or a `depends_on` pointing at a missing id
  When   `gate` runs
  Then   each produces an `ERROR`

AC-4
  Given  a `confirmed` requirement whose binding hash differs from the lock
  When   `gate` runs
  Then   it produces a `WARN` (not an error) naming the member `file:line` locations

AC-5
  Given  a present-but-corrupt lock file
  When   `gate` runs
  Then   it produces a `WARN` and does not change the exit code

AC-6
  Given  a requirement with a malformed `milestone:` (e.g. `next` or `1.14`)
  When   `gate` runs
  Then   it produces a `WARN`; a valid `v1.14`, an absent milestone, or a `deprecated`
         requirement produces none

AC-7
  Given  a `confirmed` requirement with no `## WHAT — Contract` section
  When   `gate` runs
  Then   it produces a `WARN` and does not affect the exit code

AC-8
  Given  a `confirmed` requirement with no `## HOW — Acceptance` section
  When   `gate` runs
  Then   it produces a `WARN` and does not affect the exit code

AC-9
  Given  a `confirmed` requirement with both sections present
  When   `gate` runs
  Then   it produces no section-lint warning

AC-10
  Given  a `confirmed` requirement with a `test_exempt: <reason>` and no `tested-by` member
  When   `gate` runs
  Then   it produces no test warning

AC-11
  Given  a requirement without a `## WHAT — Verify intent` section
  When   `gate` runs
  Then   it is counted as legacy-schema in the summary

AC-12
  Given  an advancing run (`sync`, or the deprecated `check --update-lock`)
  When   it runs
  Then   the current hashes are written to `requirements/_reqlock.json`

AC-13
  Given  a `_reqlock.json` (or `_memberlock.json`) present on disk but not git-tracked, inside a git work tree
  When   `gate` runs
  Then   it produces a `WARN` naming the file; once the file is tracked, or when run outside a git work tree, it produces none

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tags a function `# implements: AUTH-LOGIN-001`, but there is no such requirement
  file. She commits. The gate prints `ERROR: dangling tag` and exits non-zero, so the
  commit is blocked until she either fixes the typo or writes the requirement.
- Later she edits a confirmed requirement's contract text. Next commit, the gate warns
  `DRIFT — contract changed since lock`, reminding her to re-check the linked code.

## WHERE — Current implementation
- `cmd_check`, `warn_if_stale` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
