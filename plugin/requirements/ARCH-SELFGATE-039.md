---
id: ARCH-SELFGATE-039
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.17
depends_on: [ARCH-CHECK-006]
satisfies: [SYS-SHIP-108]
---

# This repo's own gate wiring

## Description
> `reqmap.py` ships a gate other repos vendor and run — but until now, none of the files
> that actually WIRE the gate into this repo (CI, the GitHub Action, the git hooks, the
> cache-sync script) carried a single tag pointing back at the capability they invoke.
> "Tag your own pipeline" (v2.9 TODO.md) closes that gap.

Every bullet below is binding.
- The CI workflow runs the one verdict after the version checks on every push or pull request, then re-points the published Action's major alias on each push to `main`. [[REQ-SELFGATE-916]]
- The dev git hooks run the same checks in the same order before a commit is created, and refuse a direct push to `main`. [[REQ-SELFGATE-1070]]
- The published Action runs a consumer's vendored engine through the same `gate` this repo runs on itself. [[REQ-SELFGATE-1071]]
- The cache-sync script refreshes the engine in the local plugin cache and in every consumer repo that already vendors one. [[REQ-SELFGATE-1072]]
- The Action's `check@vN` alias is named identically in every file that documents it and equals the plugin's major; `scripts/check_versions.py` refuses a tree where either is untrue.
- The repo's own documentation is checked against the code it describes, because a drift detector whose own front page has drifted is an argument against itself. [[REQ-SELFGATE-990]]
- A live instruction that tells a reader to type a CLI name the engine no longer has is found at merge time, read from the engine's own surface rather than from a list kept beside it. [[REQ-SELFGATE-1011]]

## Cases
CASE-1 — one verdict at every entry point
  Given  `ci.yml`'s `gate-and-tests` job, the dev `.githooks/pre-commit` and the published
         `check/action.yml`
  When   each one's gate invocation is read
  Then   all three run `reqmap.py gate`, the one verdict, with no second copy of its logic

CASE-2 — a documented alias that disagrees is refused
  Given  `check/action.yml`, `README.md` and `CLAUDE.md` do not all name the same `check@vN`
  When   `scripts/check_versions.py` runs in the `gate-and-tests` job
  Then   it exits 1 and names the file that disagrees, before the alias can be published

CASE-3 — the alias tracks the plugin's major
  Given  every documented `check@vN` agrees, but names a major other than `plugin.json`'s
  When   `scripts/check_versions.py` runs in the `gate-and-tests` job
  Then   it exits 1 and says the alias must track the plugin's major, so `v4.0.0` cannot
         ship advertised as `@v3`

## Context
**Notes**
- This requirement does not re-describe `gate`'s own behavior — that contract lives in
  [[ARCH-CHECK-006]]. It says where this repo runs it, and each place is its own child.

**Example**
- A contributor enables `git config core.hooksPath .githooks`, edits a requirement with a typo,
  and `git commit` fails locally with the same error CI would have caught later.

**Current implementation**
- The wiring: `.github/workflows/ci.yml` ([[REQ-SELFGATE-916]]), `.githooks/`
  ([[REQ-SELFGATE-1070]]), `check/action.yml` ([[REQ-SELFGATE-1071]]), `sync_reqmap.sh`
  ([[REQ-SELFGATE-1072]]); `scripts/test_pipeline_wiring.py` reads each one.
- The alias axis is asserted by `scripts/check_versions.py` (`ACTION_REF_FILES`), covered by
  `scripts/test_check_versions.py`.


--------------------


---
id: REQ-SELFGATE-916
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
satisfies: [ARCH-SELFGATE-039]
---

# The CI workflow runs the one verdict and moves the Action's alias

## Description
> `reqmap.py` ships a gate other repos vendor and run, but until "tag your own pipeline"
> (v2.9 TODO.md), the workflow that runs it here carried no tag back to that fact. Without
> it, a change to `ci.yml` could silently stop enforcing the gate, or stop moving the
> alias consumers pin, and nothing in the requirement graph would show it.

Every bullet below is binding.
- `.github/workflows/ci.yml` triggers on every push to `main` and on every pull request.
- Its `gate-and-tests` job runs `reqmap.py gate --full --code ..` from `plugin/`, the one
  verdict that since `v4.0.0` carries the lint and the map-freshness check itself.
- The same job runs `check_versions.py`, `check_engine_bump.py` and
  `check_retired_verbs.py` before that verdict, in that order.
- Its `release` job force-moves the action's major-alias tag — the `@vN` named by the
  `uses:` reference in `check/action.yml` — onto the commit the current `plugin.json` version
  is tagged at, on every push to `main`.

## Cases
CASE-1 — the CI job runs the one verdict on both triggers
  Given  `.github/workflows/ci.yml`
  When   its triggers and its `gate-and-tests` job are read
  Then   the workflow triggers on both push and pull_request, and the job runs
         `reqmap.py gate --full --code ..` from `plugin/`

CASE-2 — the version and engine checks run before the verdict
  Given  `ci.yml`'s `gate-and-tests` job
  When   its steps are read top to bottom
  Then   `check_versions.py`, `check_engine_bump.py --base HEAD~1` and
         `check_retired_verbs.py` run in that order, all before the gate

CASE-3 — the release job moves the action's major-alias tag on every push to main
  Given  a push to `main`, whether or not `plugin.json`'s version changed
  When   `ci.yml`'s `release` job's alias step runs
  Then   the `@vN` tag named in `check/action.yml`'s `uses:` reference is force-moved onto the
         commit tagged with the current `plugin.json` version


---
id: REQ-SELFGATE-1070
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
---

# The dev git hooks run CI's checks before a commit and guard `main`

## Description
> CI is the verdict, but it answers after a push. The dev hooks give the same answer
> before a commit exists, and refuse the one push the branch model forbids. A hook that
> drifted from CI's order would pass a commit CI then rejects.

Every bullet below is binding.
- `.githooks/pre-commit` runs `check_versions.py`, `check_engine_bump.py --staged`,
  `check_retired_verbs.py` and `reqmap.py gate --full` over the repo root, in the order
  `ci.yml`'s `gate-and-tests` job runs them.
- The first check that fails stops the hook with exit 1, so the commit is not created.
- `.githooks/pre-push` refuses a push whose target is `main` or `master`, and lets every
  other push through.

## Cases
CASE-1 — the pre-commit hook runs CI's checks in CI's order
  Given  `.githooks/pre-commit` and `ci.yml`'s `gate-and-tests` job
  When   both are read top to bottom
  Then   the hook runs `check_versions.py`, `check_engine_bump.py --staged`,
         `check_retired_verbs.py` and `reqmap.py gate --full` in the same relative order
         as the job

CASE-2 — a failing check refuses the commit
  Given  `.githooks/pre-commit`
  When   any one of its checks exits non-zero
  Then   the hook exits 1 at that check, before the commit is created

CASE-3 — the pre-push hook blocks a direct push to main
  Given  `.githooks/pre-push` enabled and a local push whose target branch is `main`
  When   `git push` runs
  Then   the hook exits 1 before the push reaches the remote; a push to any other branch
         exits 0


---
id: REQ-SELFGATE-1071
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
---

# The published Action runs the consumer's engine through the same gate

## Description
> A consumer adopts the gate by adding one `uses:` line. What that line runs has to be the
> verdict this repo runs on itself, not a second, lighter check, and the two halves a
> consumer may not be ready for have to stay switchable without forking the Action.

Every bullet below is binding.
- `check/action.yml` is a composite action whose gate step runs the consumer's vendored
  `reqmap.py` (`scripts/reqmap.py` by default) as `gate`, the command `ci.yml` runs here.
- Its `lint` and `freshness` inputs default to `'true'`; any other value passes
  `--no-lint` or `--no-map-check` to that gate.
- Its header carries the `uses: alxmax/requirement-manager/check@vN` reference the release
  job derives the alias tag from.

## Cases
CASE-1 — the composite action runs the same verdict
  Given  `check/action.yml`
  When   its `runs.steps` are read
  Then   it is a composite action whose gate step runs the vendored `reqmap.py gate`

CASE-2 — the lint and freshness inputs switch their halves off
  Given  the `lint` and `freshness` inputs of `check/action.yml`
  When   the inputs and the gate step are read
  Then   both default to `'true'`, and a value other than `true` adds `--no-lint` or
         `--no-map-check` to the gate's flags

CASE-3 — the file names the alias the release job moves
  Given  `check/action.yml`
  When   it is searched the way the `release` job's alias step searches it
  Then   it yields one `requirement-manager/check@vN` reference


---
id: REQ-SELFGATE-1072
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SELFGATE-039]
---

# The cache-sync script refreshes an engine, never seeds one

## Description
> A change to the engine reaches this machine's installed plugin and the consumer repos it
> works on only when someone copies it there. `sync_reqmap.sh` is that copy. It must
> carry the whole engine, the CLI and its package, and it must never plant an engine in a
> repo that did not ask for one.

Every bullet below is binding.
- `sync_reqmap.sh` copies `plugin/scripts/reqmap.py` and the `reqmap_engine/` package, less
  `__pycache__`, into the local plugin cache directory named by `plugin.json`'s version,
  with the vendored viewer template when it exists.
- For each consumer repo passed as an argument it refreshes an engine already vendored
  there, wherever it is located, and skips a repo that has none rather than seeding one.
- `sync_reqmap.sh` refreshes a consumer's viewer template only where that repo already has
  one.

## Cases
CASE-1 — the plugin cache gets the whole engine
  Given  `sync_reqmap.sh`
  When   its cache step is read
  Then   the cache directory is derived from `plugin.json`'s version, and `reqmap.py`, the
         `reqmap_engine/` package without `__pycache__` and the viewer template are copied
         into it

CASE-2 — a consumer with no engine is skipped, not seeded
  Given  a consumer-repo argument where no vendored `reqmap.py` is found
  When   the consumer loop reaches it
  Then   the script warns and moves to the next repo before anything is copied

CASE-3 — a viewer template is refreshed only where one exists
  Given  a consumer repo whose vendored engine has no `_map_viewer.html` beside it
  When   the script refreshes that repo
  Then   no viewer template is copied into it


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
- The engine module count and the marked corpus counts `CLAUDE.md` states are asserted
  against the package and the corpus, and a mismatch fails the suite naming both numbers.
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

CASE-4 — a stale count in CLAUDE.md fails
  Given  `CLAUDE.md` stating a module count or a marked corpus count the repo no longer has
  When   the suite runs in the source repo
  Then   it fails and names both numbers

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
- A flag the parser still accepts but that moved to another verb is named in one table beside
  the guard, verb by verb, and reported when a line passes it to its old verb. The parser is
  flat, so it accepts `gate --search` for as long as `ask --search` exists.
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
  verb, a flag or a moved flag, and the line itself.

## Cases
CASE-1 — the live surface comes from the engine, both halves
  Given  the engine's `COMMANDS` registry and the `add_argument` calls of its parser
  When   the guard reads its live surface
  Then   it holds every registered verb and every long flag the parser accepts, including
         flags the registry itself omits

CASE-2 — an instruction to type a retired name is reported
  Given  a line instructing a reader to run a retired verb, to pass a flag the parser does
         not accept, or to pass a moved flag to its old verb, in any of the delimited or bare
         invocation forms
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
