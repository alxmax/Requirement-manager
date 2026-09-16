---
id: ARCH-RELEASE-072
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v7.21.0
depends_on: [ARCH-ROADMAP-038, ARCH-INIT-012, ARCH-MAP-007]
satisfies: [SYS-SHIP-108]
---

# Releasing from the plan

## Description
> The plan says which version the work goes out in, the CHANGELOG says what shipped, and a
> version file says what the repository is. Keeping the three in step used to be three hand
> edits, and they drifted: the plan scheduled a shipped version three times. This capability
> reads all three in one form, reports where they disagree, and cuts the next planned
> release in one step, so a repository set up by `init` can release without a script of its own.

Every bullet below is binding.
- The engine reads the version a repository declares from the usual version files, or from the files `_config.json` names. [[REQ-VERSIONFILES-1014]]
- A CHANGELOG is read in the dated heading forms its ecosystem uses, and `init` seeds one when the repository has none. [[REQ-CHANGELOGFORMS-1015]]
- `sync`, `gate --audit` and `health` report where the version files, the CHANGELOG and the tags disagree. [[REQ-VERSIONALIGN-1016]]
- A disagreement between the version sources never fails a command. [[REQ-VERSIONALIGN-1016]]
- The next release's number is the lowest planned milestone above the highest version already declared. [[REQ-NEXTVERSION-1017]]
- `sync --release` prints the release it would cut and writes the version files and the CHANGELOG entry only with `--apply`. [[REQ-RELEASECMD-1018]]
- `init` gives a GitHub repository a workflow that tags and releases the declared version once. [[REQ-RELEASEWORKFLOW-1019]]
- Releasing a version removes its milestone and bars from the plan, so the plan never describes the past. [[REQ-PLANADVANCE-1020]]
- `sync` suggests a new date for a bar whose work finished on another day, or ran past its end. [[REQ-PLANDATES-1022]]
- A release names the ROADMAP items its bars carry out, for the author to tick. [[REQ-RELEASEROADMAP-1023]]

## Cases
CASE-1
  Given  a fresh repository with a `package.json` at 0.1.0
  When   `init` runs, a milestone `v0.2.0` is planned, and `sync --release --apply` runs
  Then   `package.json` declares 0.2.0 and the CHANGELOG carries a dated `0.2.0` entry

CASE-2
  Given  a fresh repository with nothing planned above its declared version
  When   `sync --release --apply` runs
  Then   it exits 2 and the version file is unchanged

CASE-3
  Given  a repository whose version file was bumped by hand with no CHANGELOG entry
  When   `gate --audit` runs
  Then   it names the disagreement and exits 0

## Context
**Notes**
- The decision and what it supersedes are in ADR-0040. Tagging stays in CI: the engine
  never tags or pushes.

---
id: REQ-VERSIONFILES-1014
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# The version a repository declares is read where it lives

## Description
> Every ecosystem keeps its version in a different file, and a check that knows only one of
> them is blind in every other repository.

Every bullet below is binding.
- `package.json`, `pyproject.toml`, `Cargo.toml`, `.claude-plugin/plugin.json` and `VERSION`
  are probed at the code root and beside the requirements directory; a TOML version is read
  only from the `project`, `tool.poetry`, `package` or `workspace.package` table.
- A non-empty `VERSION_FILES` list in `_config.json` replaces the probe with the files it names.
- Rewriting a version changes only the version text; every other byte of the file is kept.
- `init` prints which files the version is read from, or that none was found.

## Cases
CASE-1 — the usual files are found and a dependency pin is not
  Given  a `package.json` at 1.4.0 and a `pyproject.toml` whose `[tool.black]` table sets another version
  When   the version files are read
  Then   `package.json` and the `[project]` version are returned, and the tool's is not

CASE-2 — a configured file replaces the probe
  Given  `VERSION_FILES` naming `meta/VERSION`
  When   the version files are read
  Then   only `meta/VERSION` is returned

CASE-3 — a bump rewrites the version and nothing else
  Given  a formatted `package.json` and a `Cargo.toml` with a comment and a dependency version
  When   both are rewritten to 1.5.0
  Then   each file differs from before only in its own version text

CASE-4 — no version file is an empty answer
  Given  a repository with no version file
  When   the version files are read
  Then   the answer is empty

---
id: REQ-CHANGELOGFORMS-1015
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# A CHANGELOG is read in the form its ecosystem writes

## Description
> A parser that knew one heading form left every other repository with an empty history and
> nothing to release into.

Every bullet below is binding.
- A dated release heading is read as ``## plugin `vX.Y.Z` — date``, `## [X.Y.Z] - date`,
  `## vX.Y.Z - date` or `## X.Y.Z (date)`, and its version is reported as `vX.Y.Z`.
- A heading without a date, such as `## [Unreleased]`, is not a release.
- A new entry is written in the heading form the file already uses, and in the Keep a
  Changelog form when it has none.
- `init` seeds a `CHANGELOG.md` holding an `Unreleased` heading when the repository has
  none, never overwrites one, and lists it in the seeded `.reqmapignore`.

## Cases
CASE-1 — every form is read, and Unreleased is not
  Given  a CHANGELOG with an Unreleased heading and one release in each of three forms
  When   it is parsed
  Then   the three releases are returned newest first as `vX.Y.Z`, and Unreleased is not

CASE-2 — a new entry follows the form the file uses
  Given  a Keep a Changelog file, a file in this repository's form, and an empty file
  When   a heading is written for each
  Then   each heading takes the file's own form, and the empty file's is Keep a Changelog

CASE-3 — init seeds a CHANGELOG once and does not scan it
  Given  a repository without a CHANGELOG
  When   `init` runs, the file is edited, and `init` runs again
  Then   the first run creates it, the second leaves the edit, and `.reqmapignore` lists it

---
id: REQ-VERSIONALIGN-1016
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# Where the version sources disagree is reported

## Description
> A version bumped in one file and not another, or a release with no CHANGELOG entry, is
> found at release time by whoever reads the tag. It should be found when `sync` runs.

Every bullet below is binding.
- Version files declaring different versions are named in one line, each with its version.
- A newest dated CHANGELOG release different from the declared version is reported, saying
  whether the entry is missing or the CHANGELOG is ahead.
- A tag above the declared version is reported; a tag below it is the normal state between a
  bump and its release and is not.
- The lines are printed by `sync` and `gate --audit` and carried by `health --json` under
  `version_alignment`; no gate rule reads them.

## Cases
CASE-1 — files that disagree are named
  Given  a `package.json` at 1.4.0 and a `VERSION` file at 1.3.0
  When   the alignment is checked
  Then   one line names both files and their versions

CASE-2 — a CHANGELOG behind the files asks for the entry
  Given  version files at 1.4.0 and a CHANGELOG whose newest release is 1.3.0
  When   the alignment is checked
  Then   a line names `v1.3.0` and asks for the entry

CASE-3 — a tag below the files is the normal state
  Given  version files and CHANGELOG at 1.4.0 and a newest tag `v1.3.0`
  When   the alignment is checked
  Then   nothing is reported

CASE-4 — a tag above the files is reported
  Given  version files and CHANGELOG at 1.4.0 and a newest tag `v1.5.0`
  When   the alignment is checked
  Then   one line says `v1.5.0` is above the declared version

---
id: REQ-NEXTVERSION-1017
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# The next release's number comes from the plan

## Description
> The milestone a bar was scheduled on already states which release the work goes out in.
> Reading the number anywhere else makes a second place to state it (ADR-0040).

Every bullet below is binding.
- The next version is the lowest milestone key or bar `milestone` above the highest version
  a version file, tag or CHANGELOG heading has declared, spelled as the plan spells it.
- With nothing planned above that baseline there is no next version.

## Cases
CASE-1 — the lowest planned version above the baseline
  Given  a declared 1.4.0 and milestones `v1.4.0`, `v1.6.0` and `v1.5.0`
  When   the next version is asked for
  Then   it is `v1.5.0`

CASE-2 — nothing planned above the baseline
  Given  a declared 1.4.0 and only a milestone `v1.4.0`
  When   the next version is asked for
  Then   there is none

CASE-3 — a bar's milestone counts as planned
  Given  a declared 1.4.0 and a bar on milestone `v1.4.1` with no milestone entry
  When   the next version is asked for
  Then   it is `v1.4.1`

---
id: REQ-RELEASECMD-1018
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# `sync --release` cuts the next planned version

## Description
> Bumping the files, writing the CHANGELOG entry and updating the plan are one decision made
> in three places. One command makes it in all three, and shows what it will do first.

Every bullet below is binding.
- `sync --release` prints the version it would release, the version-file changes, the
  CHANGELOG entry and the plan change, and writes nothing.
- With `--apply` it rewrites every version file, and writes the dated entry — headed by the
  milestone's label in bold, then one bullet per bar planned on that version — directly under
  `Unreleased` when the file has one, otherwise above the newest release.
- A version named after `--release` is released instead of the planned one.
- `sync --release --apply` refuses with exit 2 and writes nothing in three cases: nothing is
  planned above the baseline, the version is not above it, or the gate reports errors.
- An entry for the version that already exists is never written a second time.

## Cases
CASE-1 — a dry run writes nothing
  Given  a plan with `v1.5.0` above a declared 1.4.0
  When   `sync --release` runs without `--apply`
  Then   it names `v1.5.0` and every file is unchanged

CASE-2 — apply bumps the files and writes the entry under Unreleased
  Given  that plan and a CHANGELOG holding an Unreleased item
  When   `sync --release --apply` runs
  Then   `package.json` declares 1.5.0 and the 1.5.0 entry, below Unreleased, lists the planned bar and the collected item

CASE-3 — apply with nothing planned is refused
  Given  a declared 1.4.0 and an empty plan
  When   `sync --release --apply` runs
  Then   it exits 2, says nothing is planned above `v1.4.0`, and `package.json` is unchanged

CASE-4 — a named version not above the baseline is refused
  Given  a declared 1.4.0
  When   `sync --release v1.4.0 --apply` runs
  Then   it exits 2 and says `v1.4.0` is not above `v1.4.0`

CASE-5 — an entry is never written twice
  Given  a release already applied for `v1.5.0`
  When   it is applied again
  Then   the CHANGELOG holds one `1.5.0` heading

---
id: REQ-RELEASEWORKFLOW-1019
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# A GitHub repository gets the workflow that tags a release once

## Description
> The engine decides the version and never tags. CI tags, and it needs to know the version,
> whether it is already tagged, and the notes to publish.

Every bullet below is binding.
- `sync --release --json` carries `declared`, `tag_exists` and `notes`: the declared version
  as `vX.Y.Z`, whether that tag exists, and that version's CHANGELOG entry.
- `init` writes `.github/workflows/reqmap-release.yml` when the repository has a `.github`
  directory or a github.com remote, and never over an existing file.
- The workflow runs the engine vendored in the checkout and creates the tag and GitHub release
  only when the declared version has no tag; with no engine inside the repository, `init`
  writes no workflow and says why.

## Cases
CASE-1 — init seeds the workflow on a GitHub repository
  Given  a repository with a `.github` directory and no release workflow
  When   `init` runs
  Then   `.github/workflows/reqmap-release.yml` is written

CASE-2 — an existing workflow is never overwritten
  Given  a repository whose release workflow already exists
  When   the release files are seeded
  Then   the workflow is unchanged and not reported as created

CASE-3 — a repository off GitHub gets no workflow
  Given  a repository with no `.github` directory and no remote
  When   `init` runs
  Then   no `.github` directory is created

CASE-4 — the workflow runs the vendored engine and releases once
  Given  the engine inside the checkout, and a checkout without it
  When   the workflow text is built for each
  Then   the first runs that engine with `sync --release --json` and skips an existing tag, and the second has no workflow

CASE-5 — the JSON carries what CI needs
  Given  a declared 1.5.0 with a CHANGELOG entry and no tag
  When   `sync --release --json` runs
  Then   it reports `v1.5.0`, no tag, and the entry's text

---
id: REQ-PLANADVANCE-1020
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
---

# Releasing a version advances the plan

## Description
> A plan that keeps a shipped version describes the past, which is worse than no plan. The
> record of what shipped is the CHANGELOG entry written in the same step.

Every bullet below is binding.
- Applying a release removes that version's milestone and every bar planned on it from
  `_planning.json`, keeping every other key, milestone and bar.
- After a release the plan names no version at or below the declared one, and the next
  planned milestone becomes the next release.

## Cases
CASE-1 — the plan drops the released version and keeps the rest
  Given  a plan holding `v1.5.0` and `v1.6.0`, a bar on each, and lanes
  When   `v1.5.0` is released
  Then   only `v1.6.0`, its bar and the lanes remain

CASE-2 — after a release the plan is current and names the next
  Given  that release applied
  When   the plan and version sources are checked
  Then   no milestone is stale, nothing is misaligned, and `v1.6.0` is next

CASE-3 — a dry run leaves the plan as it was
  Given  a plan holding `v1.5.0` and a bar on it
  When   `sync --release` runs without `--apply`
  Then   `_planning.json` is byte-identical

---
id: REQ-PLANDATES-1022
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
distinct_from: [REQ-UNPLANNED-1024]
---

# `sync` suggests a bar's date when the work moved

## Description
> A bar keeps the dates it was planned with. When the work finishes early, or runs over, the
> chart goes on showing the plan as if it were the schedule. The engine can see both from
> the requirement the bar names; it suggests the date and leaves the choice to the author.

Every bullet below is binding.
- A bar whose `req:` names a confirmed or implemented requirement with code implementing it
  is done on the date of the last commit to that code; when that date differs from the bar's
  `end` and is not before its `start`, `sync` names it as the `end` to set.
- A bar whose `end` has passed while the requirement it names is not done is reported as
  needing its `end` moved.
- A bar with no `req:`, or whose requirement does not exist, is never reported.
- Nothing is written to `_planning.json`.

## Cases
CASE-1 — work done early suggests the real end
  Given  a bar ending 2026-10-02 whose confirmed requirement's code was last committed 2026-09-12
  When   `sync` runs
  Then   it suggests setting the bar's `end` to 2026-09-12

CASE-2 — work that matches its plan is silent
  Given  the same bar planned to end 2026-09-12
  When   `sync` runs
  Then   nothing is suggested

CASE-3 — code older than the bar is not its finish
  Given  a bar starting 2026-09-14 whose requirement's code was last committed 2026-09-12
  When   `sync` runs
  Then   nothing is suggested, because the bar's work has not touched the code yet

CASE-4 — an open requirement past its end is overdue
  Given  bars naming a draft requirement, one ending before today and one after, and a bar with no `req:`
  When   `sync` runs
  Then   only the bar that ended before today is reported, asking for its `end` to move

## Context
**Notes**
- `distinct_from: REQ-UNPLANNED-1024` - `REQ-UNPLANNED-1024` finds ROADMAP items with no bar; this suggests new dates for bars that exist.

---
id: REQ-RELEASEROADMAP-1023
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RELEASE-072]
distinct_from: [REQ-VIEWER-999, REQ-UNPLANNED-1024, REQ-ROADMAP-998]
---

# A release names the ROADMAP items it carries out

## Description
> A release drops its bars from the plan, and the ROADMAP item the work came from stayed
> open beside a version that had shipped. Ticking it is the author's call; finding it is not.

Every bullet below is binding.
- An open ROADMAP item belongs to a released bar when its name equals the bar's title, or,
  failing that, when it is the only open item carrying the bar's `req:`.
- `sync --release` lists those items as ones to tick by hand, and never edits `ROADMAP.md`.

## Cases
CASE-1 — the items a release's bars carry out
  Given  open items matched by title, by a `req:` only one item carries, and by a `req:` two items share
  When   the items for the bars are asked for
  Then   the first two are named and neither of the two sharing a `req:` is

CASE-2 — the release plan names the items and writes none
  Given  a release whose bar is titled like an open Now item
  When   `sync --release --apply` runs
  Then   it names the item to tick and `ROADMAP.md` is unchanged

CASE-3 — a done item is never suggested
  Given  a bar titled like an item already ticked
  When   the items for the bars are asked for
  Then   none is named

## Context
**Notes**
- `distinct_from: REQ-VIEWER-999` - `REQ-VIEWER-999` renders a selected bar's ROADMAP note in the viewer; this lists the items to tick when a release ships.
- `distinct_from: REQ-UNPLANNED-1024` - `REQ-UNPLANNED-1024` counts open Now/Next items no bar schedules; this names the items a released bar carried out. It matches a bar by title or any `req:`, this one by title or a `req:` only one item carries, because a tick suggestion must not guess.
- `distinct_from: REQ-ROADMAP-998` - `REQ-ROADMAP-998` parses ROADMAP.md and checks its `req:` and `unpark:`; this reads the parsed items at release time.

