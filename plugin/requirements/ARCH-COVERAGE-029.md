---
id: ARCH-COVERAGE-029
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-SCAN-002, ARCH-NEXT-013]
milestone: v2.6
satisfies: [SYS-REPORT-105]

---

# Untagged-code coverage signal

> reqmap links code to requirements by tags, but nothing reported how much code is
> linked to nothing — code traceable to no requirement was only visible by running
> `draft`/`plan`. This surfaces that gap as a read-only count, so a reviewer sees at
> a glance whether code is drifting ahead of the spec. A Senate audit (2026-06-21)
> rejected enforcing coverage as a hard gate — it is gameable with hollow tags and
> conflicts with the model where a requirement is a behavior, not a file — and
> approved only this non-blocking visibility signal.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     membership tag  a comment in code naming a requirement: `implements`, `tested-by`,
                     `generated-from` or `validated-against`.
     untagged code   a scannable code file carrying no membership tag, so it is traced to
                     no requirement.
     the denominator the set of files the count is taken over.
     health score    the single percentage `health` prints for the whole corpus. -->

**What it counts**
- The capability reports the count of scannable code files that carry no membership tag —
  "untagged code", code traced to no requirement.
- The denominator is exactly `_scan_untagged`'s (see [[ARCH-NEXT-013]]): the files matched by
  the scanner extension walk, minus `.reqmapignore`.
- Any membership tag counts a file as covered. The tags are `implements`, `tested-by`,
  `generated-from` and `validated-against`.

**Where it appears**
- The `health` command includes this count as an `untagged` integer key in its `--json` output.
- The `health` command also includes it as a labelled line in its text output.
- The `untagged` key is absent, not zero, when no code root is scanned — a unit-test caller,
  for example. An existing `--json` consumer therefore keeps its schema.

**What it never does**
- The signal is read-only and is never a gate. It changes no exit code.
- The signal never lowers the health score, because it counts files, not requirements.

**How a file leaves the count**
- A file is silenced from the count either by tagging it, or by adding it to `.reqmapignore`.
- There is no separate exemption mechanism.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent; the Senate audit settled scope and severity.

## WHAT — Notes & known limitations (informative)
- This is the read-only half of coverage; the matching list of which files is the "Untagged files" bucket in `next` ([[ARCH-NEXT-013]]). Same denominator, two surfaces.
- It measures tag PRESENCE, not tag QUALITY: a hollow `# implements:` tag counts as covered. This is accepted — the Senate flagged that a hard gate would make hollow tags the rational way to pass CI, which is why this stays advisory.
- Granularity is per file, not per member; the engine does not parse members.

## HOW — Acceptance (= tests)
AC-1
  Given  a code root with one tagged and one untagged scannable file
  When   `health --json` runs with that code root
  Then   the `untagged` key equals 1 and the score is unchanged by it

AC-2
  Given  no code root (a unit-test caller)
  When   `health --json` runs
  Then   the output carries no `untagged` key

AC-3
  Given  an untagged scannable file that is then tagged or added to `.reqmapignore`
  When   `health --json` runs again with the code root
  Then   the `untagged` count drops by one (the file is silenced from the signal)

## WHERE — Current implementation
- The untagged-count block in `cmd_health` (`reqmap.py`), reusing `_scan_untagged` (ARCH-NEXT-013) when a code root is supplied. Surfaced read-only in `health` text output and `--json`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-318
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The capability reports the count of scannable code

> The capability reports the count of scannable code files that carry no membership tag —
> "untagged code", code traced to no requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-319
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The denominator is exactly _scan_untagged's (see ARCH-NEXT-013): the

> The denominator is exactly `_scan_untagged`'s (see [[ARCH-NEXT-013]]): the files matched
> by the scanner extension walk, minus `.reqmapignore`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-320
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# Any membership tag counts a file as covered

> Any membership tag counts a file as covered. The tags are `implements`, `tested-by`,
> `generated-from` and `validated-against`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-321
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The health command includes this count as an

> The `health` command includes this count as an `untagged` integer key in its `--json`
> output.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-322
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The health command also includes it as a

> The `health` command also includes it as a labelled line in its text output.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-323
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The untagged key is absent, not zero, when

> The `untagged` key is absent, not zero, when no code root is scanned — a unit-test
> caller, for example. An existing `--json` consumer therefore keeps its schema.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-324
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The signal is read-only and is never a

> The signal is read-only and is never a gate. It changes no exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-325
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# The signal never lowers the health score, because

> The signal never lowers the health score, because it counts files, not requirements.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-326
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# A file is silenced from the count either

> A file is silenced from the count either by tagging it, or by adding it to
> `.reqmapignore`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-COVERAGE-327
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-COVERAGE-029]
superseded_by:
---

# There is no separate exemption mechanism

> There is no separate exemption mechanism.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
