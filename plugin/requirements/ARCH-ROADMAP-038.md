---
id: ARCH-ROADMAP-038
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.17
depends_on: [ARCH-HEALTH-017]
satisfies: [SYS-REPORT-105]
distinct_from: [REQ-PLANADVANCE-1020]
---

# Roadmap coherence signals

## Description
> `TODO.md` is this project's roadmap and decision log, and nothing checks that it still
> matches reality. Twice it has fallen behind — once by seven milestones — and once a
> cosmetic heading rename silently re-filed the only open item under the wrong version,
> because a heading that is not a version leaves the previous one in force. These two
> read-only signals surface both, so the roadmap stops drifting unnoticed between manual
> clean-ups.

Every bullet below is binding.
- `health --json` reads `TODO.md` from the code root, or its parent when absent there, and reports three read-only signals. [[REQ-ROADMAP-907]]
- The first signal fires when the roadmap's newest milestone falls behind the newest requirement `milestone:`. The second lists a `## ` heading whose first token is not a version, which silently re-files items under the wrong milestone. [[REQ-ROADMAP-907]]
- The third fires in the opposite direction: the requirements trail the newest milestone the roadmap marks shipped, so work that shipped carries no requirement. [[REQ-ROADMAP-983]]
- A horizon plan in `ROADMAP.md` is read alongside the versioned `TODO.md`, and `gate --audit` reports the two claims in it that can be checked: an item pointing at an id the corpus does not have, and a parked item with no condition to bring it back. [[REQ-ROADMAP-998]]
- A planned milestone in `_planning.json` at or below the highest version the repo has already declared is reported by `gate --audit` and `health`. [[REQ-PLANSTALE-1013]]
- That report covers milestone keys as well as bar milestones, and is never a gate rule. [[REQ-PLANSTALE-1013]]
- An open Now or Next item that no bar in `_planning.json` schedules is counted by `sync`. [[REQ-UNPLANNED-1024]]
- `init` seeds a plan a new repository can plan on, and a plan with no dates still carries a calendar to its horizon. [[REQ-PLANHORIZON-1010]]
- The export carries the branch git is on, and the plan's shipped band is labelled with it. [[REQ-PLANBRANCH-1011]]

## Cases
CASE-1
  Given  a roadmap whose newest milestone is older than the newest requirement milestone
  When   `health --json` runs
  Then   it reports both versions as the behind-signal

CASE-2
  Given  a roadmap at or ahead of the newest requirement milestone
  When   `health --json` runs
  Then   it reports no behind-signal

CASE-3
  Given  a roadmap holding a `## ` heading that does not start with a version
  When   `health --json` runs
  Then   that heading is listed, because items below it are filed under the section above

CASE-4
  Given  a repo with no `TODO.md`
  When   `health --json` runs
  Then   it reports neither roadmap signal

CASE-5
  Given  milestones `v2.9` and `v2.10`
  When   the versions are compared
  Then   `v2.10` ranks above `v2.9`, which a string compare would reverse

CASE-6
  Given  a roadmap that marks work shipped past the newest requirement `milestone:`
  When   `health --json` runs
  Then   it reports that drift too, so neither direction is the only one watched

## Context
**Terms**
- the roadmap      TODO.md — milestone sections holding checklist items.
- a milestone      a `## vX.Y` heading. Items below it belong to that version.
- a version heading  a `## ` heading whose first token is `vX.Y`.

**Notes**
- Both signals compare against requirement `milestone:` fields, not against a
  package version. The engine owns the former in every repo; the latter is
  project-specific. A repo that leaves `milestone:` unset gets neither.
- Only ONE direction was checked from v2.17 to v5.10, and the unchecked one is the
  one that happened: 27 requirements written across six minors carried no
  `milestone:`, so the chart's newest column read v4.0 while the product shipped
  5.10. The signal that would have said so did not exist.
- Neither signal is a gate. The v1.35 roadmap-hygiene note chose manual upkeep over
  automation when demand was n=1; this is the read-only middle ground after n=2.
- Un singur izvor pentru plan (ROADMAP.md și `_planning.json` topite într-unul,
  docs/plan-source-audit.html) a fost respins pe 2026-09-14: 5 din 6 bare se potrivesc
  deja cu un item, deci divergența măsurată e 1, nu 10. Se redeschide numai la ≥ 2
  divergențe item/bară și ≥ 1 recurență de prospețime (o bară rămasă în urma item-ului
  ei după ce a fost corectată o dată). Dacă pe 2027-03-14 cele două numere citesc
  sub 2 și zero, propunerea se marchează respinsă — nu re-argumentată.
- Precedente: Senate `2026-06-21_122415-reqmap-todo-roadmap-coherence` (MODIFY, outcome OK:
  semnal read-only la n=2, niciodată gate) și `2026-09-14_225939-senate-reqmap-plan-single-source`
  (MODIFY, outcome OVR: ștergerea `scores` nu fusese livrată). Auditul
  `2026-09-16_160109-rm-planning-audit` (MODIFY 9-0) a cerut REQ-PLANSTALE-1013.
- Citirea condiției de redeschidere la 2026-09-16: recurențe de prospețime a planului = 2
  (v7.9 în 830df0f, v7.19 cu `plugin.json` deja la 7.19.0), după prima (v7.4);
  divergențe item/bară măsurate = 1 (bara „Server MCP” era planificată pe v7.19 în timp ce
  item-ul ei stă în `Later` cu `unpark:`). Sub pragul de ≥ 2 divergențe: condiția NU e
  îndeplinită, merge-ul rămâne respins.

**Current implementation**
- `_roadmap_signals`, `_version_key` and `_roadmap_behind` in `reqmap.py`, read by
  `cmd_health` and `_audit_summary`.
- `distinct_from: REQ-PLANADVANCE-1020` - `REQ-PLANADVANCE-1020` changes the plan when a release is applied; this capability reads and reports on the plan and never writes it.

--------------------


---
id: REQ-ROADMAP-907
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.2
satisfies: [ARCH-ROADMAP-038]
---

# A behind roadmap and an unversioned heading, both read-only

## Description
> `TODO.md` is this project's roadmap, and nothing used to check that it still matched
> reality: it has fallen seven milestones behind once, and a cosmetic heading rename once
> silently re-filed the only open item under the wrong version, because a heading that is
> not a version leaves the previous one in force. `health --json` now surfaces both as
> read-only signals, neither a gate, so the roadmap stops drifting unnoticed between manual
> clean-ups.

Every bullet below is binding.
- `health` reads `TODO.md` from the code root, or from its parent when absent there.
- `health --json` reports nothing about the roadmap when no `TODO.md` exists, so a repo
  that keeps none sees no new output.
- `health --json` reports the newest milestone in the roadmap against the newest
  `milestone:` recorded on any requirement.
- `health --json` reports the pair only when the roadmap is the older of the two.
- Versions compare segment by segment as numbers, so `v2.10` ranks above `v2.9`.
- `health --json` lists every `## ` heading in the roadmap whose first token is not a
  version.
- Such a heading leaves the previous milestone in force, so items below it are filed
  under the section above instead of their own.
- Both signals are read-only. Neither changes an exit code, and neither lowers the
  health score.

## Cases
CASE-1 — _roadmap_signals falls back to the parent directory for TODO.md
  Given  no `TODO.md` in the code root but one in its parent directory
  When   `_roadmap_signals(root)` runs
  Then   it reads the parent's `TODO.md` and returns its milestone data

CASE-2 — no TODO.md means no roadmap keys in health --json
  Given  a repo with no `TODO.md` anywhere
  When   `health --json` runs
  Then   the payload has no `roadmap_behind` and no `roadmap_unversioned_headings` key

CASE-3 — behind-signal names both the roadmap's and requirements' newest milestone
  Given  a `TODO.md` newest heading `## v2.8` and a requirement with `milestone: v2.13`
  When   `health --json` runs
  Then   `roadmap_behind` equals `{"todo": "v2.8", "requirements": "v2.13"}`, `health`
         exits 0, and the health score is unchanged — the signal is read-only, like its
         unversioned-heading counterpart

CASE-4 — no behind-signal when the roadmap is current or ahead
  Given  a `TODO.md` newest heading `## v2.16` and a requirement with `milestone: v2.13`
  When   `health --json` runs
  Then   the payload carries no `roadmap_behind` key

CASE-5 — v2.10 sorts above v2.9 under _version_key
  Given  the strings `"v2.10"` and `"v2.9"`
  When   `_version_key` is applied to each and compared
  Then   `_version_key("v2.10") > _version_key("v2.9")`, unlike a plain string compare

CASE-6 — a non-version heading is listed under roadmap_unversioned_headings
  Given  a `TODO.md` with `## v2.16` followed later by `## Deferred work`
  When   `health --json` runs
  Then   `roadmap_unversioned_headings` equals `["Deferred work"]`

CASE-7 — an item under a non-version heading is filed under the prior milestone
  Given  `## v2.16` followed by `## Deferred work` followed by one checklist item
  When   `_parse_todos_from_text` parses the text
  Then   that item's `milestone` reads `"v2.16"`, not `"Deferred work"`


--------------------


---
id: REQ-ROADMAP-983
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-ROADMAP-038]
---

# The roadmap can also be ahead of the requirements

## Description
> The behind-signal asks one question, `is TODO.md older than the corpus`, and the
> answer was no for six minors while the opposite was quietly true: the requirements
> stopped declaring `milestone:` at v4.0 and the roadmap chart ended two majors before
> the product did. A check that watches one direction reports nothing when the drift
> runs the other way, and reads as a clean result.

Every bullet below is binding.
- `health --json` reports `roadmap_unmapped` when the newest requirement `milestone:`
  is older than the newest milestone `TODO.md` marks shipped, naming both versions.
- Shipped means at least one item under that heading is checked `[x]`. An open item
  under a later heading is a plan, so a roadmap that looks ahead of the code raises
  nothing — which is every roadmap worth keeping.
- The signal is one line naming the two versions, never one finding per milestone
  that lacks a requirement.
- `roadmap_unmapped` is read-only, like the behind-signal it mirrors: no exit code
  changes, and the health score is untouched.
- Each roadmap line `sync` and `gate --audit` print ends with the edit that clears it.
- `init` says once that the roadmap chart stays empty when `TODO.md` has headings and
  none of them starts with a version.

## Cases
CASE-1 — the requirements trailing the shipped roadmap is reported
  Given  a `TODO.md` whose `## v2.16` section holds a `[x]` item, and a corpus whose
         newest requirement `milestone:` is `v2.13`
  When   `health --json` runs
  Then   `roadmap_unmapped` equals `{"shipped": "v2.16", "requirements": "v2.13"}` and
         `health` still exits 0

CASE-2 — an open item under a later heading is a plan, not a gap
  Given  a `TODO.md` whose `## v2.16` section holds only an unchecked item, and a
         corpus whose newest requirement `milestone:` is `v2.13`
  When   `health --json` runs
  Then   the payload carries no `roadmap_unmapped` key

CASE-3 — a corpus level with the shipped roadmap raises nothing
  Given  a `TODO.md` whose newest shipped milestone is `v2.13`, and a corpus whose
         newest requirement `milestone:` is `v2.13`
  When   `health --json` runs
  Then   the payload carries no `roadmap_unmapped` key

CASE-4 — each roadmap line names its next step
  Given  a `TODO.md` whose `## v2.16` holds a `[x]` item and whose `## Deferred` is not a
         version, and a corpus whose newest requirement `milestone:` is `v2.13`
  When   the roadmap lines are printed
  Then   one says to add `milestone:` after `v2.13`, and one says to start `Deferred` with
         its version

CASE-5 — init names an inert roadmap
  Given  a repository whose `TODO.md` has only the heading `## Backlog`
  When   `init` runs
  Then   its output says the roadmap chart stays empty, once


--------------------


---
id: REQ-ROADMAP-998
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.7
satisfies: [ARCH-ROADMAP-038]
---

# ROADMAP.md: the horizon plan, and the two claims in it that can be checked

## Description
> Every roadmap signal before this one read `TODO.md`, a file organised by version. A plan
> organised by HORIZON — Now, Next, Later — is a different shape, and this repo's own
> `ROADMAP.md` was invisible to the engine while carrying the live plan. What can be checked
> about a plan file is narrow and worth being honest about: whether an item points at a real
> requirement, and whether a parked item says what would bring it back. Whether a `[x]` item
> is TRUE is not decidable from the file — an item naming a change nobody made reads exactly
> like one naming a change that landed — so nothing here claims to know.

Every bullet below is binding.
- `ROADMAP.md` is parsed for `- [ ]` / `- [x]` items under the reserved headings `Now`,
  `Next`, `Later` and `Not now`, each item carrying its horizon, its `req:` id when present
  and its `unpark:` condition when present.
- An item under a heading that is not one of the four reserved horizons is skipped, as an
  item before the first milestone is skipped in `TODO.md`.
- A `### ` heading inside a horizon names the category of the items under it, until the next
  `### ` or horizon; it is never read as prose belonging to the item above it.
- `gate --audit` reports an item whose `req:` names an id absent from the corpus.
- `gate --audit` reports an open `Later` item carrying no `unpark:`.
- Both signals are read-only and advisory: they never change an exit code, and a repo with
  no `ROADMAP.md` sees nothing.

## Cases
CASE-1 — items are read under the reserved horizons
  Given  a `ROADMAP.md` with one item under `## Now` and one under `## Later`
  When   the roadmap is parsed
  Then   both items are returned, each carrying its own horizon

CASE-2 — an item under an invented heading is skipped
  Given  a `ROADMAP.md` whose only item sits under `## Someday`
  When   the roadmap is parsed
  Then   no item is returned

CASE-3 — a req: that names nothing is reported
  Given  a `ROADMAP.md` item carrying `req:` an id no requirement declares
  When   `gate --audit` runs
  Then   it names the id and says the plan points at nothing, and the exit code is unchanged

CASE-4 — a parked item with no condition is reported
  Given  an open item under `## Later` carrying no `unpark:`
  When   `gate --audit` runs
  Then   it counts the item and says parked with no condition is parked forever

CASE-5 — a repo with no ROADMAP.md sees nothing
  Given  a code root holding no `ROADMAP.md`
  When   `gate --audit` runs
  Then   it prints no roadmap-plan line

CASE-6 — a category heading groups the items under it
  Given  `## Now`, an item, `### Viewer`, an item, then `## Later` and an item
  When   the roadmap is parsed
  Then   the first item has no category and empty context, the second is in `Viewer`, and the
         Later item has no category

---
id: REQ-PLANHORIZON-1010
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
---

# A repo with no plan still gets a calendar to plan on

## Description
> A plan file a repo does not have is a plan nobody writes. `init` scaffolded neither
> `ROADMAP.md` nor `_planning.json`, so a fresh repo's Plan tab said "add milestones with
> due dates or bars" — the empty case being the one with nothing to look at, which is
> backwards: the repo that has planned nothing is exactly the one that needs a calendar
> to plan ON. And a horizon written once into a file goes stale by definition, so the
> engine computes it instead of freezing it.

Every bullet below is binding.
- `init` writes a `ROADMAP.md` holding the four reserved headings and the format it
  expects, and a `requirements/_planning.json` holding lanes and a cadence; it never
  overwrites either when one is already there.
- The seeded `_planning.json` carries no `until`, so its calendar is recomputed on every
  run rather than ending on the date it was written.
- `default_horizon` answers the end of the current year, or three months out, whichever
  is later — so the calendar covers the year for most of it and rolls into the next one
  near the close.
- A plan covering no dates at all runs its cadence from today to that horizon, and the
  chart draws it instead of reporting an empty plan.
- The seeded `ROADMAP.md` is not scanned as a capability: `init` adds it to a freshly
  seeded `.reqmapignore`, because `_read_roadmap` opens it by name.

## Cases
CASE-1 — the horizon is the later of the year end and three months out
  Given  the dates 2026-09-15, 2026-12-31 and 2027-01-15
  When   `default_horizon` is asked for each
  Then   it answers 2026-12-31, 2027-03-31 and 2027-12-31

CASE-2 — a plan with no dates still carries a calendar
  Given  a `_planning.json` holding a cadence, no bars and no milestone dues
  When   the export is built
  Then   `releases` is non-empty and reaches the horizon

CASE-3 — the chart draws a calendar with no bars on it
  Given  a plan carrying only lanes, a cadence and its release dates
  When   the Plan renders
  Then   the lanes and the calendar are drawn, not the empty-plan message

CASE-4 — init seeds both files, once
  Given  a repo with neither `ROADMAP.md` nor `requirements/_planning.json`
  When   `init` runs, and runs a second time after both are edited
  Then   the first run creates both and the second leaves the edits untouched

CASE-5 — the seeded plan file is not drafted as a capability
  Given  a fresh repo where `init` seeds `.reqmapignore` and `ROADMAP.md`
  When   the extraction pass runs
  Then   no requirement is drafted for `ROADMAP.md` and it carries no membership tag

---
id: REQ-PLANBRANCH-1011
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
---

# The shipped band is named by the branch it shipped on

## Description
> "Shipped" is a label that says nothing a reader did not already know from the band's
> position. What they cannot see is which branch they are looking at — and a map opened
> from a feature branch looks identical to one opened from `main`, right up to the moment
> someone acts on the wrong plan. The name git already knows is the one worth showing.

Every bullet below is binding.
- `_map.json` carries `branch`, the checked-out branch name, when git can answer.
- `branch` is excluded from the freshness comparison, exactly as `repo` is: both are
  git-derived and differ between two checkouts of the same corpus, so comparing them
  would fail `map --check` on every branch and every fork.
- A detached HEAD and a tree git cannot read both answer unknown, and the field is then
  absent rather than guessed.
- The shipped band is labelled with that name; with no name it keeps its former label.

## Cases
CASE-1 — the branch reaches the export
  Given  a work tree checked out on a named branch
  When   `sync` writes the export
  Then   `_map.json` carries that name under `branch`

CASE-2 — a branch change does not make the committed map stale
  Given  a committed `_map.json` written on one branch
  When   `gate` runs on a second branch with the same corpus
  Then   the map is reported fresh

CASE-3 — no branch is not a wrong branch
  Given  a tree with a detached HEAD, or no git at all
  When   the export is written
  Then   it carries no `branch` field and nothing fails

CASE-4 — the band shows the name, or keeps its old label
  Given  one export carrying `branch: feat/x` and one carrying none
  When   the Plan renders each
  Then   the first labels the shipped band `feat/x` and the second labels it `Shipped`

---
id: REQ-PLANSTALE-1013
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
distinct_from: [REQ-NEXTVERSION-1017, REQ-VERSIONALIGN-1016, ARCH-RELEASE-072, REQ-PLANADVANCE-1020, REQ-RELEASECMD-1018]
---

# A plan that schedules a version already declared is reported

## Description
> The plan scheduled a version that had already shipped three times — v7.4, v7.9, then
> v7.19 while `plugin.json` already said 7.19.0 — and each time a human found it by
> rereading the file. The one comparison the engine had read `TODO.md`, which this repo
> archived, so it went silent exactly when the plan moved to `_planning.json`.

Every bullet below is binding.
- The baseline is the highest of three versions: the one the repository's version files
  declare ([[REQ-VERSIONFILES-1014]]), the newest `v*` git tag, and the newest dated
  `vX.Y.Z` heading in `CHANGELOG.md`. With none of them, nothing is reported.
- Every version is compared in one form, `vX.Y.Z`, the form tags and CHANGELOG headings
  use: `plugin.json`'s `7.19.0` is `v7.19.0`, and a short key `vX.Y` is read as `vX.Y.0`.
  A milestone equal to the baseline is stale, because that version has been declared.
  A name that is not a version is never compared.
- Every milestone key in `_planning.json` and every bar `milestone` at or below the
  baseline is named in one `gate --audit` line and in `health --json` under `plan_shipped`,
  together with the baseline and the source it came from.
- The signal is read-only: no gate rule reads it, and the gate's exit code never depends on it.

## Cases
CASE-1 — a milestone equal to the declared version is stale
  Given  `plugin.json` at 7.19.0 and milestones `v7.19.0` and `v7.20.0`
  When   the audit runs
  Then   exactly one line names `v7.19.0`, against `v7.19.0` from `plugin.json`

CASE-2 — a milestone past the baseline is silent
  Given  `plugin.json` at 7.19.0 and milestone `v7.20.0`
  When   the audit runs
  Then   no plan line is reported

CASE-3 — a patch past the baseline is silent, and a short key is padded
  Given  a CHANGELOG whose newest heading is `v7.19.0`
  When   milestone `v7.19.1`, then milestone `v7.19`, is checked
  Then   the first is silent and the second is stale

CASE-4 — no baseline, no signal
  Given  a plan with milestones and no manifest, tag or CHANGELOG
  When   the audit runs
  Then   nothing is reported

CASE-5 — the highest source wins, and bars count
  Given  `plugin.json` at 7.18.0, a CHANGELOG at `v7.19.0` and a bar on milestone `v7.19.0`
  When   the audit runs
  Then   the bar's milestone is stale against `v7.19.0` from `CHANGELOG.md`

CASE-6 — reported, never gated
  Given  the registered gate rules
  When   they are listed
  Then   none of them comes from the planning module

## Context
**Terms**
- the baseline      the highest version already declared by manifest, tag or CHANGELOG.
- a version         written `vX.Y.Z` everywhere a plan names one, like `v7.18.0`.
- the planned set   `bars`, grouped by `milestone`. The Plan chart and the Versions columns
                    both read it; `milestones` carries only a due date and a label.
- a numbered milestone  valid only for the NEXT release. At about five releases a day
                    (20 in 2026-09-13..16), a number further out is overtaken within hours.
- `distinct_from: REQ-NEXTVERSION-1017` - `REQ-NEXTVERSION-1017` picks the lowest planned version above the baseline; this reports the planned ones at or below it. Same baseline, opposite sides.
- `distinct_from: REQ-VERSIONALIGN-1016` - `REQ-VERSIONALIGN-1016` compares the version sources with one another; this compares the plan with the highest of them.
- `distinct_from: ARCH-RELEASE-072` - `ARCH-RELEASE-072` is the capability that cuts a release from the plan; this is the read-only report on a plan that fell behind.
- `distinct_from: REQ-PLANADVANCE-1020` - `REQ-PLANADVANCE-1020` removes a released version from the plan when a release is applied; this reports one still there because nothing removed it.
- `distinct_from: REQ-RELEASECMD-1018` - `REQ-RELEASECMD-1018` is the command that writes a release; this report never writes.

---
id: REQ-UNPLANNED-1024
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
---

# A Now or Next item with no bar is counted

## Description
> Now and Next say the work is coming; a bar says when. An item in either with no bar is a
> commitment with no date, and nothing said so. The two files stay two (Senate run
> 2026-09-14_225939); this is a read-only line between them.

Every bullet below is binding.
- An open item under Now or Next is scheduled when a bar's title equals its name or a bar
  carries its `req:`; otherwise it is unplanned.
- `sync` prints one line counting unplanned items and naming the first; done items and
  Later items are never counted, and a repo with no ROADMAP.md sees nothing.

## Cases
CASE-1 — Now and Next items without a bar are counted
  Given  open Now/Next items, one matched by a bar's title, two by a bar's `req:`, one by neither
  When   the unplanned items are asked for
  Then   only the one matched by neither is counted and named

CASE-2 — everything scheduled is silent
  Given  every open Now/Next item matched by a bar, and separately no ROADMAP.md at all
  When   the line is asked for
  Then   there is none

CASE-3 — done and Later items are never counted
  Given  a ROADMAP with open Now/Next items, a done item and a Later item, and no bars
  When   the unplanned items are asked for
  Then   only the open Now and Next items are counted

