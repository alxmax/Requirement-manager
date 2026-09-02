---
id: ARCH-ROADMAP-038
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: [ARCH-HEALTH-017]       # ids of bus/other capabilities this builds on
satisfies: [SYS-REPORT-105]
superseded_by:       # <ID>, if replaced
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Roadmap coherence signals

> `TODO.md` is this project's roadmap and decision log, and nothing checks that it still
> matches reality. Twice it has fallen behind — once by seven milestones — and once a
> cosmetic heading rename silently re-filed the only open item under the wrong version,
> because a heading that is not a version leaves the previous one in force. These two
> read-only signals surface both, so the roadmap stops drifting unnoticed between manual
> clean-ups.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     the roadmap      TODO.md — milestone sections holding checklist items.
     a milestone      a `## vX.Y` heading. Items below it belong to that version.
     a version heading  a `## ` heading whose first token is `vX.Y`. -->

**What it reads**
- `health` reads `TODO.md` from the code root, or from its parent when absent there.
- `health --json` reports nothing about the roadmap when no `TODO.md` exists, so a repo
  that keeps none sees no new output.

**When the roadmap is behind**
- `health --json` reports the newest milestone in the roadmap against the newest
  `milestone:` recorded on any requirement.
- `health --json` reports the pair only when the roadmap is the older of the two.
- Versions compare segment by segment as numbers, so `v2.10` ranks above `v2.9`.

**When a heading does not parse**
- `health --json` lists every `## ` heading in the roadmap whose first token is not a
  version.
- Such a heading leaves the previous milestone in force, so items below it are filed
  under the section above instead of their own.

**Severity**
- Both signals are read-only. Neither changes an exit code, and neither lowers the
  health score.

## WHAT — Verify intent (open questions for the human)
- None — built from a failure this repo experienced twice.

## WHAT — Notes & known limitations (informative)
- The behind-signal compares against requirement `milestone:` fields, not against a
  package version. The engine owns the former in every repo; the latter is
  project-specific. A repo that leaves `milestone:` unset gets no behind-signal.
- Neither signal is a gate. The v1.35 roadmap-hygiene note chose manual upkeep over
  automation when demand was n=1; this is the read-only middle ground after n=2.

## HOW — Acceptance (= tests)
AC-1
  Given  a roadmap whose newest milestone is older than the newest requirement milestone
  When   `health --json` runs
  Then   it reports both versions as the behind-signal

AC-2
  Given  a roadmap at or ahead of the newest requirement milestone
  When   `health --json` runs
  Then   it reports no behind-signal

AC-3
  Given  a roadmap holding a `## ` heading that does not start with a version
  When   `health --json` runs
  Then   that heading is listed, because items below it are filed under the section above

AC-4
  Given  a repo with no `TODO.md`
  When   `health --json` runs
  Then   it reports neither roadmap signal

AC-5
  Given  milestones `v2.9` and `v2.10`
  When   the versions are compared
  Then   `v2.10` ranks above `v2.9`, which a string compare would reverse

## WHERE — Current implementation
- `_roadmap_signals` and `_version_key` in `reqmap.py`, read by `cmd_health`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-632
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Health reads TODO.md from the code root, or

> `health` reads `TODO.md` from the code root, or from its parent when absent there.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-633
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Health --json reports nothing about the roadmap when

> `health --json` reports nothing about the roadmap when no `TODO.md` exists, so a repo
> that keeps none sees no new output.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-634
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Health --json reports the newest milestone in the

> `health --json` reports the newest milestone in the roadmap against the newest
> `milestone:` recorded on any requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-635
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Health --json reports the pair only when the

> `health --json` reports the pair only when the roadmap is the older of the two.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-636
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Versions compare segment by segment as numbers, so

> Versions compare segment by segment as numbers, so `v2.10` ranks above `v2.9`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-637
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Health --json lists every ## heading in the

> `health --json` lists every `## ` heading in the roadmap whose first token is not a
> version.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-638
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Such a heading leaves the previous milestone in

> Such a heading leaves the previous milestone in force, so items below it are filed under
> the section above instead of their own.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-ROADMAP-639
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ROADMAP-038]
superseded_by:
---

# Both signals are read-only. Neither changes an exit

> Both signals are read-only. Neither changes an exit code, and neither lowers the health
> score.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
