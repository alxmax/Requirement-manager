---
id: ARCH-ROADMAP-038
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-HEALTH-017]
satisfies: [SYS-REPORT-105]
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
- `health --json` reads `TODO.md` from the code root, or its parent when absent there, and reports two read-only signals. [[REQ-ROADMAP-907]]
- The first signal fires when the roadmap's newest milestone falls behind the newest requirement `milestone:`. The second lists a `## ` heading whose first token is not a version, which silently re-files items under the wrong milestone. [[REQ-ROADMAP-907]]

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

## Context
**Terms**
- the roadmap      TODO.md — milestone sections holding checklist items.
- a milestone      a `## vX.Y` heading. Items below it belong to that version.
- a version heading  a `## ` heading whose first token is `vX.Y`.

**Notes**
- The behind-signal compares against requirement `milestone:` fields, not against a
  package version. The engine owns the former in every repo; the latter is
  project-specific. A repo that leaves `milestone:` unset gets no behind-signal.
- Neither signal is a gate. The v1.35 roadmap-hygiene note chose manual upkeep over
  automation when demand was n=1; this is the read-only middle ground after n=2.

**Current implementation**
- `_roadmap_signals` and `_version_key` in `reqmap.py`, read by `cmd_health`.


--------------------


---
id: REQ-ROADMAP-907
status: confirmed
level: code
layer: feature
owner: Alex
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

