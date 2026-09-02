---
id: ARCH-CHECK-006
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002, ARCH-DRIFT-003]
satisfies: [SYS-GATE-102]
superseded_by:
milestone: v1.02
lint_exempt: [ac-count-high, over-scoped]
---

# The gate

> Specs rot when the code moves on and nobody updates the file that describes it.
> This is the guard that catches that: run before every commit, it fails the build when
> code and requirements no longer match. The whole tool exists so this check can run.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     the binding hash  the fingerprint of a requirement's normative sections; when it
                       stops matching the lock, the contract has changed.
     drift             a contract whose text has moved on since the lock was written.
     the lock          requirements/_reqlock.json — the saved fingerprint of every
                       contract. `_memberlock.json` is its sidecar.
     a need            a `layer: need` requirement: a stakeholder need other
                       requirements fulfil, rather than code. -->

**What is an error (exit 1)**
- `gate` reports an `ERROR` and exits non-zero for every condition in this group.
- A dangling tag — a code tag referencing a capability no requirement defines — is
  such a condition.
- An invalid `status` or an invalid `layer` is such a condition.
- A `depends_on` pointing at a missing id is such a condition.
- An enforced requirement with no `implements:` member is such a condition.
- A requirement is enforced when its status is `in-progress`, `implemented` or
  `confirmed`.
- A `layer: need` requirement is exempt from that `implements:` rule — see
  [[ARCH-TRACE-020]].

**What is a warning**
- `gate` reports drift as a `WARN`, never an error: a `confirmed` requirement whose
  binding hash differs from the lock.
- The drift warning names the member `file:line` locations to re-check.
- A `confirmed` requirement with no `tested-by:` member is a `WARN`.
- A requirement carrying a `test_exempt: <reason>` opt-out in its frontmatter is exempt
  from that test warning.
- A `layer: need` requirement is exempt from it too.
- A `confirmed` requirement missing a `## WHAT — Contract` section is a `WARN`, in both
  the `bus` and `feature` layers. It does not affect the exit code.
- A `confirmed` requirement missing a `## HOW — Acceptance` section is a `WARN`, in both
  the `bus` and `feature` layers. It does not affect the exit code.
- The requirement `milestone:` field is optional. When present it matches the version
  shape `v<digits>[.<digits>…]`, for example `v1.14`.
- A malformed `milestone:` value is a `WARN`, because that field is roadmap-only
  metadata and never build-critical.
- A `deprecated` requirement is exempt from the `milestone:` shape check.
- A present-but-unreadable `_reqlock.json` is a `WARN`. Drift is skipped for that run
  rather than crashing.
- A lock sidecar (`_reqlock.json` or `_memberlock.json`) that exists on disk but is
  **not git-tracked** is a `WARN` naming the file.
- An uncommitted lock silently disables drift detection on a fresh CI checkout, which
  has no baseline to compare against.
- That git-tracking check is fail-open: `gate` stays silent when git is unavailable or
  the tree is not a work tree.
- `gate` names every requirement whose body lacks a `## WHAT — Verify intent` section in
  one aggregated legacy-schema `WARN`.
- `gate` counts those legacy-schema requirements in the summary.
- The legacy-schema warning does not affect the exit code.
- A confirmed `need` with no `validated-against:` member is a `WARN`, once the repo carries at
  least one such tag (see [[ARCH-VLEVEL-037]]).
- A confirmed `bus` requirement whose levelled `tested-by:` links are all `@system` is a `WARN`.
- A `depends_on` cycle is a `WARN` naming the whole chain, once per distinct cycle.
- The cycle warning stays a warning under `--strict`, so an existing corpus keeps its
  exit code when the engine is upgraded.

**What it prints**
- `gate` prints an advisory line carrying the open verify-intent finding count when that
  count is above zero.
- That advisory line does not affect the exit code.
- `gate` prints a summary of requirements, members, errors and warnings.

**Advancing the lock**
- With `--update-lock`, `gate` writes the current binding hashes to
  `requirements/_reqlock.json`.
- `sync` and the deprecated `check` alias pass `--update-lock`.
- The `gate` verb itself is report-only.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Why `ac-count-high` and `over-scoped` are exempt: this requirement is the gate's severity
  table, not a bundle of checks. Each individual check the gate runs already has its own
  requirement ([[ARCH-TESTLINK-018]], [[ARCH-ACVERIFY-019]], [[ARCH-MEMBERDRIFT-027]],
  [[ARCH-DOCBUNDLE-026]], [[ARCH-ORPHANCODE-034]], [[ARCH-DRIFTIMPACT-035]]). What remains here
  is one behaviour — which condition is an ERROR, which is a WARN, and what that does to the
  exit code — so every clause and criterion shares a single failure mode. Splitting it would
  scatter the exit-code contract across files instead of clarifying it. Revisit this exemption
  if a clause ever lands here that is not about severity or exit code.
- Errors stop CI (exit 1); warnings do not. Intent sync (promote `baseline → confirmed`)
  is not automatable and surfaces at human review.
- When `CLAUDE_PLUGIN_ROOT` is set and the vendored engine is older than the installed
  plugin's copy, `gate` prints an advisory staleness notice (`warn_if_stale`); the
  variable is unset in CI, so the notice is silent and exit-neutral there. The CI half of
  that signal cannot live here — a stale engine does not contain the check that reports it
  stale — so it ships with the published action instead ([[ARCH-STALEENGINE-043]]).
- The dev-CI version-coherence script `scripts/check_versions.py` (repo root, never seeded
  into consumer repos) enforces plugin manifest alignment as the first step in this repo's
  own CI pipeline (`check_versions.py → gate → map --check → test_reqmap.py`). It is
  outside the plugin scan root and has no requirement of its own; its invariant (semver
  consistency across `plugin.json` + `marketplace.json`) is documented in `CLAUDE.md`.

## HOW — Acceptance (= tests)
AC-1
  Given  a tag referencing a non-existent capability
  When   `gate` runs
  Then   it produces an `ERROR` and exit 1

AC-2
  Given  a `confirmed` requirement with no `implements` member
  When   `gate` runs
  Then   it produces an `ERROR`

AC-3
  Given  an invalid status or layer, or a `depends_on` pointing at a missing id
  When   `gate` runs
  Then   each produces an `ERROR`

AC-4
  Given  a `confirmed` requirement whose binding hash differs from the lock
  When   `gate` runs
  Then   it produces a `WARN` (not an error) naming the member `file:line` locations

AC-5
  Given  a present-but-corrupt lock file
  When   `gate` runs
  Then   it produces a `WARN` and does not change the exit code

AC-6
  Given  a requirement with a malformed `milestone:` (e.g. `next` or `1.14`)
  When   `gate` runs
  Then   it produces a `WARN`; a valid `v1.14`, an absent milestone, or a `deprecated`
         requirement produces none

AC-7
  Given  a `confirmed` requirement with no `## WHAT — Contract` section
  When   `gate` runs
  Then   it produces a `WARN` and does not affect the exit code

AC-8
  Given  a `confirmed` requirement with no `## HOW — Acceptance` section
  When   `gate` runs
  Then   it produces a `WARN` and does not affect the exit code

AC-9
  Given  a `confirmed` requirement with both sections present
  When   `gate` runs
  Then   it produces no section-lint warning

AC-10
  Given  a `confirmed` requirement with a `test_exempt: <reason>` and no `tested-by` member
  When   `gate` runs
  Then   it produces no test warning

AC-11
  Given  a requirement without a `## WHAT — Verify intent` section
  When   `gate` runs
  Then   it is counted as legacy-schema in the summary

AC-12
  Given  an advancing run (`sync`, or the deprecated `check --update-lock`)
  When   it runs
  Then   the current hashes are written to `requirements/_reqlock.json`

AC-13
  Given  a `_reqlock.json` (or `_memberlock.json`) present on disk but not git-tracked, inside a git work tree
  When   `gate` runs
  Then   it produces a `WARN` naming the file; once the file is tracked, or when run outside a git work tree, it produces none

AC-14
  Given  two requirements whose `depends_on` fields point at each other
  When   the gate runs
  Then   it warns once, naming the chain, and the exit code stays 0

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tags a function `# implements: AUTH-LOGIN-001`, but there is no such requirement
  file. She commits. The gate prints `ERROR: dangling tag` and exits non-zero, so the
  commit is blocked until she either fixes the typo or writes the requirement.
- Later she edits a confirmed requirement's contract text. Next commit, the gate warns
  `DRIFT — contract changed since lock`, reminding her to re-check the linked code.

## WHERE — Current implementation
- `cmd_check`, `warn_if_stale` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-CHECK-271
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Gate reports an ERROR and exits non-zero for

> `gate` reports an `ERROR` and exits non-zero for every condition in this group.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-272
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A dangling tag — a code tag referencing

> A dangling tag — a code tag referencing a capability no requirement defines — is such a
> condition.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-273
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# An invalid status or an invalid layer is

> An invalid `status` or an invalid `layer` is such a condition.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-274
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A depends_on pointing at a missing id is

> A `depends_on` pointing at a missing id is such a condition.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-275
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# An enforced requirement with no implements: member is

> An enforced requirement with no `implements:` member is such a condition.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-276
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A requirement is enforced when its status is

> A requirement is enforced when its status is `in-progress`, `implemented` or
> `confirmed`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-277
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A layer: need requirement is exempt from that

> A `layer: need` requirement is exempt from that `implements:` rule — see
> [[ARCH-TRACE-020]].

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-278
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Gate reports drift as a WARN, never an

> `gate` reports drift as a `WARN`, never an error: a `confirmed` requirement whose
> binding hash differs from the lock.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-279
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# The drift warning names the member file:line locations

> The drift warning names the member `file:line` locations to re-check.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-280
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A confirmed requirement with no tested-by: member is

> A `confirmed` requirement with no `tested-by:` member is a `WARN`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-281
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A requirement carrying a test_exempt: <reason> opt-out in

> A requirement carrying a `test_exempt: <reason>` opt-out in its frontmatter is exempt
> from that test warning.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-282
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A layer: need requirement is exempt from it

> A `layer: need` requirement is exempt from it too.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-283
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A confirmed requirement missing a ## WHAT —

> A `confirmed` requirement missing a `## WHAT — Contract` section is a `WARN`, in both
> the `bus` and `feature` layers. It does not affect the exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-284
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A confirmed requirement missing a ## HOW —

> A `confirmed` requirement missing a `## HOW — Acceptance` section is a `WARN`, in both
> the `bus` and `feature` layers. It does not affect the exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-285
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# The requirement milestone: field is optional. When present

> The requirement `milestone:` field is optional. When present it matches the version
> shape `v<digits>[.<digits>…]`, for example `v1.14`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-286
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A malformed milestone: value is a WARN, because

> A malformed `milestone:` value is a `WARN`, because that field is roadmap-only metadata
> and never build-critical.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-287
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A deprecated requirement is exempt from the milestone

> A `deprecated` requirement is exempt from the `milestone:` shape check.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-288
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A present-but-unreadable _reqlock.json is a WARN. Drift is

> A present-but-unreadable `_reqlock.json` is a `WARN`. Drift is skipped for that run
> rather than crashing.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-289
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A lock sidecar (_reqlock.json or _memberlock.json) that exists

> A lock sidecar (`_reqlock.json` or `_memberlock.json`) that exists on disk but is **not
> git-tracked** is a `WARN` naming the file.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-290
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# An uncommitted lock silently disables drift detection on

> An uncommitted lock silently disables drift detection on a fresh CI checkout, which has
> no baseline to compare against.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-291
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# That git-tracking check is fail-open: gate stays silent

> That git-tracking check is fail-open: `gate` stays silent when git is unavailable or the
> tree is not a work tree.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-292
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Gate names every requirement whose body lacks a

> `gate` names every requirement whose body lacks a `## WHAT — Verify intent` section in
> one aggregated legacy-schema `WARN`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-293
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Gate counts those legacy-schema requirements in the summary

> `gate` counts those legacy-schema requirements in the summary.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-294
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# The legacy-schema warning does not affect the exit

> The legacy-schema warning does not affect the exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-295
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A confirmed need with no validated-against: member is

> A confirmed `need` with no `validated-against:` member is a `WARN`, once the repo
> carries at least one such tag (see [[ARCH-VLEVEL-037]]).

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-296
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A confirmed bus requirement whose levelled tested-by: links

> A confirmed `bus` requirement whose levelled `tested-by:` links are all `@system` is a
> `WARN`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-297
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# A depends_on cycle is a WARN naming the

> A `depends_on` cycle is a `WARN` naming the whole chain, once per distinct cycle.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-298
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# The cycle warning stays a warning under --strict

> The cycle warning stays a warning under `--strict`, so an existing corpus keeps its exit
> code when the engine is upgraded.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-299
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Gate prints an advisory line carrying the open

> `gate` prints an advisory line carrying the open verify-intent finding count when that
> count is above zero.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-300
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# That advisory line does not affect the exit

> That advisory line does not affect the exit code.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-301
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Gate prints a summary of requirements, members, errors

> `gate` prints a summary of requirements, members, errors and warnings.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-302
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# With --update-lock, gate writes the current binding hashes

> With `--update-lock`, `gate` writes the current binding hashes to
> `requirements/_reqlock.json`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-303
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# Sync and the deprecated check alias pass --update-lock

> `sync` and the deprecated `check` alias pass `--update-lock`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CHECK-304
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
superseded_by:
---

# The gate verb itself is report-only

> The `gate` verb itself is report-only.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
