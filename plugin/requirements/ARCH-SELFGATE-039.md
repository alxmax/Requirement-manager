---
id: ARCH-SELFGATE-039
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.17
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
- The repo's own documentation is checked against the code it describes, because a drift detector whose own front page has drifted is an argument against itself. [[REQ-SELFGATE-990]]
- A live instruction that tells a reader to type a CLI name the engine no longer has is found at merge time, read from the engine's own surface rather than from a list kept beside it. [[REQ-SELFGATE-1011]]

## Cases
CASE-1  <!-- verifiable by: inspection -->
  Given  a push or pull request to this repo
  When   `ci.yml`'s `gate-and-tests` job runs
  Then   `reqmap.py gate --code ..` exits 0 before any other job runs — since `v4.0.0` that one
         command IS the lint and the map-freshness check as well

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

CASE-9
  Given  a README stating an engine line count the file no longer has
  When   the suite runs in the source repo
  Then   it fails and names both numbers

CASE-10
  Given  an ADR file with no row in the ADR index
  When   the suite runs in the source repo
  Then   it fails and names the file

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
milestone: v3.2
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
CASE-1 — the CI job runs the one verdict on both triggers
  Given  `.github/workflows/ci.yml`
  When   its `gate-and-tests` job is read
  Then   the job invokes `gate` — which since `v4.0.0` carries the lint and the map
         freshness check itself; the workflow triggers on both push and pull_request

CASE-2 — the composite action runs the same verdict
  Given  `check/action.yml`
  When   its `runs.steps` are read
  Then   the composite action invokes `reqmap.py gate`, the same command `ci.yml` runs on
         itself, with the lint and freshness halves switched off by `--no-lint` /
         `--no-map-check` when its `lint` / `freshness` inputs say so

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


---
id: REQ-SELFGATE-990
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-SELFGATE-039]
---

# The repo's own documentation is checked, not trusted

## Description
> This tool exists because a claim about code decays the moment the code moves. Its own front
> page asserted an engine line count that was wrong by 843 lines, and an ADR index that named
> a decision count fixed eight records earlier; one ADR sat on disk for nine days in no index
> at all. Nothing noticed, because nothing read them. A drift detector whose own documents
> drift is an argument against itself.

Every bullet below is binding.
- The engine line count stated in `README.md` is asserted against the file, and a stale number
  fails the suite.
- Every ADR file on disk has a row in the ADR index, and one that does not fails the suite.
- The ADR index states no decision count, because a hand-maintained total is one more claim to
  keep true; the index itself is the count.
- The number of design findings the engine package reports on itself is asserted against the
  count `CLAUDE.md` states, and a mismatch fails the suite naming both numbers, so a finding
  can be accepted but not accumulated unread.
- These checks are skipped, not failed, when the suite runs from a seeded copy that has no
  repo root to read.

## Cases
CASE-1 — a stale line count fails
  Given  a README whose stated engine line count differs from the file
  When   the suite runs in the source repo
  Then   it fails and names both numbers

CASE-2 — an unindexed ADR fails
  Given  an ADR file with no row in the index
  When   the suite runs in the source repo
  Then   it fails and names the file

CASE-3 — the index carries no count to maintain
  Given  the ADR index
  When   its prose above the table is read
  Then   it states no number of decisions

CASE-4 — an undocumented design finding fails
  Given  `CLAUDE.md` stating a number of design findings the engine reports on itself, and a
         package that reports a different number
  When   the suite runs in the source repo
  Then   it fails, names both numbers and lists the findings actually reported

--------------------


---
id: REQ-SELFGATE-1011
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.14
satisfies: [ARCH-SELFGATE-039]
---

# A live instruction never names a CLI name the engine dropped

## Description
> Folding one verb into another has happened four times here, and three of those left an
> instruction telling a reader to type a command that no longer resolves: `map --check` in
> three places of a consumer's CLAUDE.md, a script telling the reader to run the `findings`
> verb after it was folded into `sync`, and a SKILL contract that documented `scan` (gone)
> while omitting five verbs that existed.
> None failed at merge. None failed in CI. Each failed later, at the moment a human followed
> a written line. The guard moves that failure to merge time, and it reads the engine rather
> than a second list, because a list of what is live is one more claim to keep true.

Every bullet below is binding.
- The live surface is read from the engine itself: the verbs from the `COMMANDS` registry,
  the flags from the `add_argument` calls the parser is built from, across every file that
  holds them.
- A retired name is reported only where a line instructs a reader to type it — an invocation
  inside backticks, inside a quoted string, or after `python`/`$PY` — so prose that merely
  mentions the name is not a finding.
- A line that states the name is gone is skipped whole, in English and in Romanian, because a
  migration note is the reason a reader stops calling the old name and reporting it would
  retract the retraction.
- A flag belongs to the call it follows and to nothing after a backtick, a quote, `&&`, `||`
  or `;`, so a second command on the same line never hands its flags to `reqmap`.
- When the engine's flags cannot be read the flag half is skipped rather than reported, so a
  guard that cannot read the engine fails open instead of accusing every flag at once.
- Positional arguments are extra consumer roots, scanned against THIS repo's live surface; a
  root that does not exist ends the run with exit 2 rather than a pass.
- A finding ends the run with exit 1 and names the file, the line number, whether it was a
  verb or a flag, and the line itself.

## Cases
CASE-1 — the live surface comes from the engine, both halves
  Given  the engine's `COMMANDS` registry and the `add_argument` calls of its parser
  When   the guard reads its live surface
  Then   it holds every registered verb and every long flag the parser accepts, including
         flags the registry itself omits

CASE-2 — an instruction to type a retired name is reported
  Given  a line instructing a reader to run a retired verb, or to pass a flag the parser does
         not accept, in any of the delimited or bare invocation forms
  When   the guard scans it
  Then   it reports the name with its file, line and kind, and the run exits 1

CASE-3 — a live name and an unrelated word are not findings
  Given  a line naming a verb the engine still has, and another naming a word that was never
         a verb
  When   the guard scans them
  Then   neither is reported

CASE-4 — a removal note retracts the instruction it describes
  Given  a line saying the name was folded, renamed or removed, written in English or in
         Romanian
  When   the guard scans it
  Then   the whole line is skipped and nothing is reported

CASE-5 — a neighbour command keeps its own flags
  Given  a line carrying a `reqmap` call followed by a second command with its own flags,
         separated by a backtick, a quote or a shell operator
  When   the guard attributes flags
  Then   only the flags before that separator are read against the engine

CASE-6 — a guard that cannot read fails open, a missing root does not
  Given  an engine whose flags cannot be read, and separately an extra root that is not a
         directory
  When   the guard runs
  Then   the first reports no flag at all, and the second exits 2 rather than reporting a pass
