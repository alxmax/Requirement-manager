---
id: ARCH-SELFGATE-039
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-CHECK-006]
satisfies: [SYS-SHIP-108]
lint_exempt: [file-spread, ac-count-high]
# ac-count-high: eight cases, one root cause — this repository gating itself across CI, the
# two hooks, the published action and the version checks. Splitting by surface would give
# five requirements that fail together and are read together.
test_exempt: pipeline wiring (YAML/shell config invoking the gate) — no unit-testable behavior of its own; correctness is observed by CI/the hook actually running, per CASE-1/CASE-2. CASE-7's alias-coherence check is the one exception and IS unit-tested, in scripts/test_check_versions.py (repo-local dev tooling, outside the scanned engine)
---

# This repo's own gate wiring

## Description
> `reqmap.py` ships a gate other repos vendor and run — but until now, none of the files
> that actually WIRE the gate into this repo (CI, the GitHub Action, the git hooks, the
> cache-sync script) carried a single tag pointing back at the capability they invoke.
> "Tag your own pipeline" (v2.9 TODO.md) closes that gap.

Every bullet below is binding.
- Five repo-root files — `ci.yml`, `check/action.yml`, both dev git hooks, and `sync_reqmap.sh` — each wire the gate into a real entry point (CI, a consumer's Action, a local commit/push, the cache-sync script), and each carries a member tag pointing back at this requirement. [[REQ-SELFGATE-916]]

## Cases
CASE-1  <!-- verifiable by: inspection -->
  Given  a push or pull request to this repo
  When   `ci.yml`'s `gate-and-tests` job runs
  Then   `reqmap.py gate`, `lint --strict`, and `map --check` all exit 0 before any other job runs

CASE-2  <!-- verifiable by: inspection -->
  Given  a local commit attempt with the dev hook enabled (`core.hooksPath .githooks`)
  When   `.githooks/pre-commit` runs
  Then   it fails the commit on the same errors CI would fail on, before the commit is created

CASE-3  <!-- verifiable by: inspection -->
  Given  a consumer repo referencing `uses: alxmax/requirement-manager/check@v5`
  When   their own CI runs that step
  Then   `check/action.yml` invokes the same gate this repo runs on itself

CASE-4  <!-- verifiable by: inspection -->
  Given  a local push attempt with the dev hook enabled and the target branch is `main`
  When   `.githooks/pre-push` runs
  Then   the push is blocked before it reaches the remote

CASE-5  <!-- verifiable by: inspection -->
  Given  `sync_reqmap.sh` is run with zero or more consumer-repo paths as arguments
  When   it completes
  Then   `plugin/scripts/reqmap.py` (and the vendored viewer template, if present) in the local
         plugin cache and every named consumer repo matches this repo's current copy

CASE-6  <!-- verifiable by: inspection -->
  Given  a push to `main`, whether or not it bumps `plugin.json`
  When   the `release` job's alias step runs
  Then   the major-alias tag read from `check/action.yml` points at the commit tagged with the
         current `plugin.json` version, so `check@vN` resolves to the latest released content

CASE-7
  Given  `check/action.yml`, `README.md` and `CLAUDE.md` do not all name the same `check@vN`
  When   `scripts/check_versions.py` runs in the `gate-and-tests` job
  Then   it exits 1 and names the file that disagrees, before the alias can be published

CASE-8
  Given  every documented `check@vN` agrees, but names a major other than `plugin.json`'s
  When   `scripts/check_versions.py` runs in the `gate-and-tests` job
  Then   it exits 1 and says the alias must track the plugin's major, so `v4.0.0` cannot
         ship advertised as `@v3`

## Context
**Notes**
- `lint_exempt: ac-count-high` — the capability is "the gate runs at every entry point", and
  each case is one of those entry points. They cannot fail independently of the obligation
  they share, which is the test for whether a clause deserves its own requirement.
- This requirement exists to give these 5 files a member tag, not to re-describe `gate`'s own
  behavior — that contract lives in [[ARCH-CHECK-006]].
- `lint_exempt: file-spread` — spanning CI, the composite action, both dev hooks and the sync
  script is the capability (the gate wired at every entry point), not a sign it is diffuse.

**Example**
- A contributor enables `git config core.hooksPath .githooks`, edits a requirement with a typo,
  and `git commit` fails locally with the same error CI would have caught later.

**Current implementation**
- `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/pre-commit`, `.githooks/pre-push`,
  `sync_reqmap.sh` (all repo root).
- The alias axis is asserted by `scripts/check_versions.py` (`ACTION_REF_FILES`), covered by
- The alias major equals the plugin's major, and the same check refuses a release where they disagree.
  `scripts/test_check_versions.py`.


--------------------


---
id: REQ-SELFGATE-916
status: confirmed
lint_exempt: [file-spread]
test_exempt: pipeline wiring (CI, hooks, the Action) observed by running it, not by a unit test
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
---

# Five files wire the gate into CI, hooks, and a consumer's Action

## Description
> `reqmap.py` ships a gate other repos vendor and run, but until "tag your own pipeline"
> (v2.9 TODO.md), none of the files that actually invoke it here — CI, the published
> Action, the local git hooks, the cache-sync script — carried a tag back to that fact.
> Without the tag, a change to any of these five could silently stop enforcing the gate
> and nothing in the requirement graph would show it.

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

## Cases
CASE-1 — the CI job runs all three checks on both triggers
  Given  `.github/workflows/ci.yml`
  When   its `gate-and-tests` job is read
  Then   the job invokes `gate`, `lint --strict`, `map --check`; the workflow triggers on
         both push and pull_request

CASE-2 — the composite action runs the same three checks
  Given  `check/action.yml`
  When   its `runs.steps` are read
  Then   the composite action invokes `reqmap.py gate`, `map --check` and `lint --strict`, the same commands `ci.yml` runs on itself

CASE-3 — the release job moves the action's major-alias tag on every push to main
  Given  a push to `main`, whether or not `plugin.json`'s version changed
  When   `ci.yml`'s `release` job's alias step runs
  Then   the `@vN` tag named in `check/action.yml`'s `uses:` reference is force-moved onto the
         commit tagged with the current `plugin.json` version

CASE-4 — the hook runs checks in the same relative order as CI
  Given  `.githooks/pre-commit`
  When   its script body is read top to bottom
  Then   it runs `check_versions.py`, `check_engine_bump.py --staged`, `gate`, `lint --strict`, `map --check` in that order, matching `ci.yml`'s `gate-and-tests` job

CASE-5 — the pre-push hook blocks a direct push to main
  Given  `.githooks/pre-push` enabled and a local push whose target branch is `main`
  When   `git push` runs
  Then   the hook rejects the push before it reaches the remote

CASE-6 — sync_reqmap.sh propagates the engine to the local cache and named consumers
  Given  `sync_reqmap.sh` run with zero or more consumer-repo paths as arguments
  When   it completes
  Then   `plugin/scripts/reqmap.py` (and the vendored viewer template, if present) in the local
         plugin cache and every named consumer repo matches this repo's current copy

## Context
**Notes**
- `lint_exempt: file-spread` — the five files ARE this requirement. Spanning CI, the
  composite action, both dev hooks and the sync script is the capability, not a sign it is
  diffuse; a version of it that touched one file would assert nothing.
