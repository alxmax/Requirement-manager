---
id: REQ-SELFGATE-039
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: [REQ-CHECK-006]     # ids of bus/other capabilities this builds on
superseded_by:       # <ID>, if replaced
test_exempt: pipeline wiring (YAML/shell config invoking the gate) — no unit-testable behavior of its own; correctness is observed by CI/the hook actually running, per AC-1/AC-2
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# This repo's own gate wiring

> `reqmap.py` ships a gate other repos vendor and run — but until now, none of the files
> that actually WIRE the gate into this repo (CI, the GitHub Action, the git hooks, the
> cache-sync script) carried a single tag pointing back at the capability they invoke.
> "Tag your own pipeline" (v2.9 TODO.md) closes that gap.

## WHAT — Contract (normative)
Every line in this section is binding.
- `.github/workflows/ci.yml`'s `gate-and-tests` job invokes `reqmap.py gate` / `lint --strict`
  / `map --check` on every push and pull request.
- `check/action.yml` packages the same invocation as a reusable GitHub Action for consumer repos.
- `.githooks/pre-commit` mirrors the CI order locally, before a commit is created.
- `.githooks/pre-push` blocks a direct push to `main`.
- `sync_reqmap.sh` propagates `plugin/scripts/reqmap.py` (+ the vendored viewer template) into
  the local plugin cache and any consumer repos passed as arguments.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent (this repo's own documented dev workflow).

## WHAT — Notes & known limitations (informative)
- This requirement exists to give these 5 files a member tag, not to re-describe `gate`'s own
  behavior — that contract lives in [[REQ-CHECK-006]].

## HOW — Acceptance (= tests)
AC-1
  Given  a push or pull request to this repo
  When   `ci.yml`'s `gate-and-tests` job runs
  Then   `reqmap.py gate`, `lint --strict`, and `map --check` all exit 0 before any other job runs

AC-2
  Given  a local commit attempt with the dev hook enabled (`core.hooksPath .githooks`)
  When   `.githooks/pre-commit` runs
  Then   it fails the commit on the same errors CI would fail on, before the commit is created

AC-3
  Given  a consumer repo referencing `uses: alxmax/requirement-manager/check@v1`
  When   their own CI runs that step
  Then   `check/action.yml` invokes the same gate this repo runs on itself

AC-4
  Given  a local push attempt with the dev hook enabled and the target branch is `main`
  When   `.githooks/pre-push` runs
  Then   the push is blocked before it reaches the remote

AC-5
  Given  `sync_reqmap.sh` is run with zero or more consumer-repo paths as arguments
  When   it completes
  Then   `plugin/scripts/reqmap.py` (and the vendored viewer template, if present) in the local
         plugin cache and every named consumer repo matches this repo's current copy

## Example — in practice (optional, non-binding)
- A contributor enables `git config core.hooksPath .githooks`, edits a requirement with a typo,
  and `git commit` fails locally with the same error CI would have caught later.

## WHERE — Current implementation
- `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/pre-commit`, `.githooks/pre-push`,
  `sync_reqmap.sh` (all repo root).

## Links
- Used by: (auto)
## Members in code (auto)
