---
id: ARCH-SELFGATE-039
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: [ARCH-CHECK-006]     # ids of bus/other capabilities this builds on
satisfies: [SYS-SHIP-108]
superseded_by:       # <ID>, if replaced
lint_exempt: [file-spread]
test_exempt: pipeline wiring (YAML/shell config invoking the gate) — no unit-testable behavior of its own; correctness is observed by CI/the hook actually running, per CASE-1/CASE-2. CASE-7's alias-coherence check is the one exception and IS unit-tested, in scripts/test_check_versions.py (repo-local dev tooling, outside the scanned engine)
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# This repo's own gate wiring

## Description
> `reqmap.py` ships a gate other repos vendor and run — but until now, none of the files
> that actually WIRE the gate into this repo (CI, the GitHub Action, the git hooks, the
> cache-sync script) carried a single tag pointing back at the capability they invoke.
> "Tag your own pipeline" (v2.9 TODO.md) closes that gap.
Every bullet below is binding.
- `.github/workflows/ci.yml`'s `gate-and-tests` job invokes `reqmap.py gate` / `lint --strict`
  / `map --check` on every push and pull request.
- `check/action.yml` packages the same invocation as a reusable GitHub Action for consumer repos.
- `ci.yml`'s `release` job force-moves the action's major-alias tag — the `@vN` named by the
  `uses:` reference in `check/action.yml` — onto the commit the current `plugin.json` version
  is tagged at, on every push to `main`.
- `.githooks/pre-commit` mirrors the CI order locally, before a commit is created.
- `.githooks/pre-push` blocks a direct push to `main`.
- `sync_reqmap.sh` propagates `plugin/scripts/reqmap.py` (+ the vendored viewer template) into
  the local plugin cache and any consumer repos passed as arguments.

## Verify intent (open questions for the human)
- None — authored from known intent (this repo's own documented dev workflow).

## Notes & known limitations (informative)
- This requirement exists to give these 5 files a member tag, not to re-describe `gate`'s own
  behavior — that contract lives in [[ARCH-CHECK-006]].
- `lint_exempt: file-spread` — spanning CI, the composite action, both dev hooks and the sync
  script is the capability (the gate wired at every entry point), not a sign it is diffuse.

## Cases (= tests)
CASE-1
  Given  a push or pull request to this repo
  When   `ci.yml`'s `gate-and-tests` job runs
  Then   `reqmap.py gate`, `lint --strict`, and `map --check` all exit 0 before any other job runs

CASE-2
  Given  a local commit attempt with the dev hook enabled (`core.hooksPath .githooks`)
  When   `.githooks/pre-commit` runs
  Then   it fails the commit on the same errors CI would fail on, before the commit is created

CASE-3
  Given  a consumer repo referencing `uses: alxmax/requirement-manager/check@v2`
  When   their own CI runs that step
  Then   `check/action.yml` invokes the same gate this repo runs on itself

CASE-4
  Given  a local push attempt with the dev hook enabled and the target branch is `main`
  When   `.githooks/pre-push` runs
  Then   the push is blocked before it reaches the remote

CASE-5
  Given  `sync_reqmap.sh` is run with zero or more consumer-repo paths as arguments
  When   it completes
  Then   `plugin/scripts/reqmap.py` (and the vendored viewer template, if present) in the local
         plugin cache and every named consumer repo matches this repo's current copy

CASE-6
  Given  a push to `main`, whether or not it bumps `plugin.json`
  When   the `release` job's alias step runs
  Then   the major-alias tag read from `check/action.yml` points at the commit tagged with the
         current `plugin.json` version, so `check@vN` resolves to the latest released content

CASE-7
  Given  `check/action.yml`, `README.md` and `CLAUDE.md` do not all name the same `check@vN`
  When   `scripts/check_versions.py` runs in the `gate-and-tests` job
  Then   it exits 1 and names the file that disagrees, before the alias can be published

## Example — in practice (optional, non-binding)
- A contributor enables `git config core.hooksPath .githooks`, edits a requirement with a typo,
  and `git commit` fails locally with the same error CI would have caught later.

## WHERE — Current implementation
- `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/pre-commit`, `.githooks/pre-push`,
  `sync_reqmap.sh` (all repo root).
- The alias axis is asserted by `scripts/check_versions.py` (`ACTION_REF_FILES`), covered by
  `scripts/test_check_versions.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-SELFGATE-668
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
superseded_by:
---

# .github/workflows/ci.yml's gate-and-tests job invokes reqmap.py gate / lint

> `.github/workflows/ci.yml`'s `gate-and-tests` job invokes `reqmap.py gate` / `lint
> --strict` / `map --check` on every push and pull request.

Scenario: the CI job runs all three checks on both triggers
  Given  `.github/workflows/ci.yml`
  When   its `gate-and-tests` job is read
  Then   the job invokes `gate`, `lint --strict` and `map --check`, and the workflow triggers on push and pull_request

## Members in code (auto)




--------------------


---
id: REQ-SELFGATE-669
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
superseded_by:
---

# Check/action.yml packages the same invocation as a reusable

> `check/action.yml` packages the same invocation as a reusable GitHub Action for consumer
> repos.

Scenario: the composite action runs the same three checks
  Given  `check/action.yml`
  When   its `runs.steps` are read
  Then   the composite action invokes `reqmap.py gate`, `map --check` and `lint --strict`, the same commands `ci.yml` runs on itself

## Members in code (auto)




--------------------


---
id: REQ-SELFGATE-670
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
superseded_by:
---

# Ci.yml's release job force-moves the action's major-alias tag

> `ci.yml`'s `release` job force-moves the action's major-alias tag — the `@vN` named by
> the `uses:` reference in `check/action.yml` — onto the commit the current `plugin.json`
> version is tagged at, on every push to `main`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SELFGATE-671
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
superseded_by:
---

# .githooks/pre-commit mirrors the CI order locally, before a

> `.githooks/pre-commit` mirrors the CI order locally, before a commit is created.

Scenario: the hook runs checks in the same relative order as CI
  Given  `.githooks/pre-commit`
  When   its script body is read top to bottom
  Then   it runs `check_versions.py`, `check_engine_bump.py --staged`, `gate`, `lint --strict`, `map --check` in that order, matching `ci.yml`'s `gate-and-tests` job

## Members in code (auto)




--------------------


---
id: REQ-SELFGATE-672
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
superseded_by:
---

# .githooks/pre-push blocks a direct push to main

> `.githooks/pre-push` blocks a direct push to `main`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SELFGATE-673
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
superseded_by:
---

# Sync_reqmap.sh propagates plugin/scripts/reqmap.py (+ the vendored viewer template)

> `sync_reqmap.sh` propagates `plugin/scripts/reqmap.py` (+ the vendored viewer template)
> into the local plugin cache and any consumer repos passed as arguments.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
