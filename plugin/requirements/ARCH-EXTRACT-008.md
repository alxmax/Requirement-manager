---
id: ARCH-EXTRACT-008
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-SCAN-002]
satisfies: [SYS-READ-103]
superseded_by:
milestone: v1.06
---

# Legacy extraction

> When an existing project has lots of code but no requirements written down, this gives you
> a running start: it reads each untagged file and writes a rough draft requirement for it,
> clearly marked as a draft so no one mistakes a guess for a settled decision. Without it,
> someone would have to sit down and describe every existing capability from scratch before
> the tool was useful on an older project. Spec and prompt documents get the same treatment
> from the companion capability [[ARCH-PROSE-024]].

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a member tag  a comment naming the requirement a piece of code belongs to.
     a draft       a `requirements/DRAFT-*.md` file: a guess at what a file does,
                   marked so nobody mistakes it for a settled decision.
     the risk score  a cheap number saying how suspect a file looks, used only to
                     decide whether a human should read the draft first. -->

**What it reads**
- `draft` walks every untagged scannable code file — the extensions and basenames the
  scan reads — plus prose in the capability bucket.
- `draft` skips a file that already carries a member tag.
- `draft` honors `.reqmapignore`, the same fnmatch globs `scan` respects.
- A file matching an ignore pattern is never drafted — notably the vendored
  `scripts/reqmap.py` engine itself.

**What it writes**
- `draft` proposes one `requirements/DRAFT-*.md` per remaining file.
- Every proposal carries `status: draft` and a TODO body. It captures observed
  behavior, and never canonizes intent or correctness.
- A proposal's Contract section opens with "Every line in this section is binding.",
  matching what `new` scaffolds, so promoting a draft needs no reshaping.
- `draft` creates the requirements directory if it is absent.
- Draft ids are path-aware, so two files sharing a basename do not collide.

**How it flags risk**
- `draft` assigns a cheap risk score from `TODO`/`FIXME`/`HACK`/`XXX` markers,
  suppressions and file size.
- `draft` routes a score of 2 or more to `REVIEW`, and any lower score to
  `auto-baseline`.

**Running it again**
- Re-running `draft` never overwrites an existing draft.

**What a code proposal shows**
- A code proposal's WHERE section lists the file's observed surface — the module
  docstring's first line and its top-level signatures — when the language has a parser.
- That surface is an authoring hint under WHERE, never a Contract line. The Contract
  stays a TODO until a human writes it.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- `draft` cannot recover intent; prefer `plan` (read-only plan) before authoring.
  The draft body uses the same Contract/Acceptance section names as a real requirement so a
  promoted draft needs no reshaping.
- Prose (`.md`/`.html`) classification and drafting is a separate capability —
  [[ARCH-PROSE-024]] — running under the same `draft` command.
- The drafted file types (`.py`/`.js`/`.ts`/`.c`/`.cpp`) are deliberately narrower than the
  gate's full scan set (which also enforces tags in `.go`/`.rs`/`.tsx` and more): drafting
  targets mainstream source, while the gate enforces tags wherever they appear.

## HOW — Acceptance (= tests)
AC-1
  Given  an untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file
  When   `draft` runs
  Then   it yields one `DRAFT-*` draft

AC-2
  Given  a file already carrying a member tag
  When   `draft` runs
  Then   the file is skipped

AC-3
  Given  a file matching a `.reqmapignore` pattern
  When   `draft` runs
  Then   the file is skipped (no draft proposed for it)

AC-4
  Given  a file containing `TODO`/`FIXME`
  When   `draft` runs
  Then   it scores higher risk and is flagged `REVIEW`

AC-5
  Given  an existing draft and same-basename files in different dirs
  When   `draft` re-runs
  Then   the draft is not overwritten and the basenames do not collide

AC-6
  Given  an untagged `.py` file with a module docstring and two top-level functions
  When   `draft` runs
  Then   its proposal's WHERE section names both signatures, and its Contract is still the TODO placeholder

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `draft` on a brownfield repo. For each untagged source file it drops a
  `DRAFT-*.md` capturing what the file appears to do; one file full of `TODO` and `FIXME`
  markers scores higher risk and is flagged `REVIEW`. The engine's own `reqmap.py` is in
  `.reqmapignore`, so it is skipped — leaving Ana a pile of starting points to promote
  into real requirements.

## WHERE — Current implementation
- `cmd_extract`, `_draft_id`, `_risk` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-374
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft walks every untagged scannable code file —

> `draft` walks every untagged scannable code file — the extensions and basenames the scan
> reads — plus prose in the capability bucket.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-375
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft skips a file that already carries a

> `draft` skips a file that already carries a member tag.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-376
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft honors .reqmapignore, the same fnmatch globs scan

> `draft` honors `.reqmapignore`, the same fnmatch globs `scan` respects.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-377
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# A file matching an ignore pattern is never

> A file matching an ignore pattern is never drafted — notably the vendored
> `scripts/reqmap.py` engine itself.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-378
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft proposes one requirements/DRAFT-.md per remaining file

> `draft` proposes one `requirements/DRAFT-*.md` per remaining file.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-379
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Every proposal carries status: draft and a TODO

> Every proposal carries `status: draft` and a TODO body. It captures observed behavior,
> and never canonizes intent or correctness.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-380
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# A proposal's Contract section opens with "Every line

> A proposal's Contract section opens with "Every line in this section is binding.",
> matching what `new` scaffolds, so promoting a draft needs no reshaping.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-381
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft creates the requirements directory if it is

> `draft` creates the requirements directory if it is absent.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-382
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft ids are path-aware, so two files sharing

> Draft ids are path-aware, so two files sharing a basename do not collide.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-383
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft assigns a cheap risk score from TODO/FIXME/HACK/XXX

> `draft` assigns a cheap risk score from `TODO`/`FIXME`/`HACK`/`XXX` markers,
> suppressions and file size.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-384
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Draft routes a score of 2 or more

> `draft` routes a score of 2 or more to `REVIEW`, and any lower score to `auto-baseline`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-385
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# Re-running draft never overwrites an existing draft

> Re-running `draft` never overwrites an existing draft.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-386
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# A code proposal's WHERE section lists the file's

> A code proposal's WHERE section lists the file's observed surface — the module
> docstring's first line and its top-level signatures — when the language has a parser.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-EXTRACT-387
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
superseded_by:
---

# That surface is an authoring hint under WHERE

> That surface is an authoring hint under WHERE, never a Contract line. The Contract stays
> a TODO until a human writes it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
