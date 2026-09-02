---
id: ARCH-REGISTRYLAG-035
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-HEALTH-017]
milestone: v2.12
satisfies: [SYS-REPORT-105]

---

# Registry-lag signal — commits since the requirements dir was last touched

> `health` reports whether the requirements that exist are coherent, but not
> whether the registry as a whole has gone stale while code moved on. A downstream
> consumer's registry sat frozen for 18 days across ~40 code commits while a
> money value drifted with no requirement update — nothing in `health` surfaced
> that the spec had stopped tracking reality. This adds a read-only count of how
> many commits have landed since the requirements dir was last touched, so a
> reviewer sees at a glance that code is racing ahead of the spec. It is the
> temporal complement to the untagged-code coverage signal ([[ARCH-COVERAGE-029]]):
> coverage answers "is this code traced?", lag answers "has the registry moved
> lately at all?". Per the Senate audit that governs the coverage signal
> (2026-06-21), advisory visibility only — never a hard gate.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     registry lag  how many commits have landed since anyone last touched a
                   requirement file. It answers "has the spec moved lately at all?"
     reqs_dir      the requirements directory.
     an axis       one pass/fail question `health` asks of a requirement. -->

**What it measures**
- Registry lag is the number of commits on `HEAD` since the most recent commit that touched
  `reqs_dir`.
- The count comes from git alone: the last commit touching `reqs_dir`
  (`git log -1 -- <reqs_dir>`), then the commit count from there to `HEAD`
  (`git rev-list --count`).
- The capability never parses requirement contents.

**What it reports**
- `health --json` includes the count as a `commits_since_req_touch` integer key.
- Text output carries a labelled line only when the count is above zero. A lag of zero is the
  healthy case and needs no line.

**What it never does**
- The signal is read-only and never a gate. It changes no exit code.
- The signal never lowers the health score, because it is a repo-wide temporal fact rather
  than a per-requirement axis.

**When it cannot measure**
- The `commits_since_req_touch` key is absent, not zero, whenever the value is unmeasurable.
- Unmeasurable means no code root was supplied, `code_root` is not a git worktree, git is
  unavailable, or `reqs_dir` has no commit in history.
- Absence rather than zero preserves the `--json` schema, so a missing reading is never
  mistaken for a fresh registry.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent; scope and severity mirror the settled Senate decision on the sibling coverage signal ([[ARCH-COVERAGE-029]]).

## WHAT — Notes & known limitations (informative)
- It measures RECENCY of any touch, not QUALITY of the update: a whitespace edit to one requirement resets the lag to 0. Accepted — like coverage, this is an advisory nudge, not proof the spec is current.
- Granularity is whole-repo, not per requirement; it answers whether the registry as a body has moved, not which requirement is stale.
- A shallow clone or a repo whose first commit already contained `reqs_dir` still reports correctly; only a genuinely absent git history or an untracked `reqs_dir` yields the absent (None) reading.

## HOW — Acceptance (= tests)
AC-1
  Given  a git repo whose requirements dir was committed, then two later commits touched only code
  When   `health --json` runs with that code root
  Then   `commits_since_req_touch` equals 2 and the score is unchanged by it

AC-2
  Given  a git repo whose most recent commit touched the requirements dir
  When   `health --json` runs with that code root
  Then   `commits_since_req_touch` is present and equals 0

AC-3
  Given  a code root that is not a git worktree
  When   `health --json` runs with that code root
  Then   the output carries no `commits_since_req_touch` key

## WHERE — Current implementation
- `_commits_since_reqs_touch(code_root, reqs_dir)` in `reqmap.py`, wired into `cmd_health` alongside the untagged block; surfaced read-only in `health` text output and `--json`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-608
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# Registry lag is the number of commits on

> Registry lag is the number of commits on `HEAD` since the most recent commit that
> touched `reqs_dir`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-609
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# The count comes from git alone: the last

> The count comes from git alone: the last commit touching `reqs_dir` (`git log -1 --
> <reqs_dir>`), then the commit count from there to `HEAD` (`git rev-list --count`).

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-610
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# The capability never parses requirement contents

> The capability never parses requirement contents.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-611
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# Health --json includes the count as a commits_since_req_touch

> `health --json` includes the count as a `commits_since_req_touch` integer key.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-612
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# Text output carries a labelled line only when

> Text output carries a labelled line only when the count is above zero. A lag of zero is
> the healthy case and needs no line.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-613
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# The signal is read-only and never a gate

> The signal is read-only and never a gate. It changes no exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-614
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# The signal never lowers the health score, because

> The signal never lowers the health score, because it is a repo-wide temporal fact rather
> than a per-requirement axis.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-615
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# The commits_since_req_touch key is absent, not zero, whenever

> The `commits_since_req_touch` key is absent, not zero, whenever the value is
> unmeasurable.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-616
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# Unmeasurable means no code root was supplied, code_root

> Unmeasurable means no code root was supplied, `code_root` is not a git worktree, git is
> unavailable, or `reqs_dir` has no commit in history.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REGISTRYLAG-617
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REGISTRYLAG-035]
superseded_by:
---

# Absence rather than zero preserves the --json schema

> Absence rather than zero preserves the `--json` schema, so a missing reading is never
> mistaken for a fresh registry.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
