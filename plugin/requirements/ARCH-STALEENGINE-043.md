---
id: ARCH-STALEENGINE-043
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: [ARCH-CHECK-006, ARCH-SELFGATE-039]     # ids of bus/other capabilities this builds on
satisfies: [SYS-SHIP-108]
superseded_by:       # <ID>, if replaced
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Stale vendored engine, reported in CI

> Every consumer repo runs its own vendored copy of `reqmap.py`, and that copy only
> improves when someone re-seeds it. The engine's own staleness notice (`warn_if_stale`)
> is gated on `CLAUDE_PLUGIN_ROOT`, which exists in a Claude Code session and nowhere
> else — so it is silent in CI, the one place that runs on every push and the one place a
> months-old engine actually costs something: checks that shipped since are simply absent,
> and nothing says so.

## WHAT — Contract (normative)
Every line in this section is binding.

**Glossary** — *vendored engine*: the consumer repo's own `scripts/reqmap.py`, the file the
action executes; *reference engine*: `plugin/scripts/reqmap.py` inside the action's own
checkout, i.e. the engine the referenced `check@vN` ships.

**What it does**
- The staleness probe compares the vendored engine's `MAP_ENGINE_VERSION` against the
  reference engine's.
- `check/action.yml` runs the probe as a step of the published gate action.
- The probe's `--mode` selects its behaviour: `warn`, `error`, or `off`.
- The action's `stale-engine` input sets that mode and defaults to `warn`.
- A vendored engine older than the reference produces one message naming both versions and
  the re-seed remedy.
- In `warn` the message is a warning and the exit code stays 0.
- In `error` the same condition exits 1.
- Under GitHub Actions the message is emitted as a `::warning::` workflow annotation, so it
  surfaces on the run rather than only in the log.

**What it never does**
- `off` produces no output and exit 0.
- A vendored engine at or ahead of the reference version produces no warning.
- A version that cannot be read from either file — absent file, unparseable value — is
  reported as a skipped probe with exit 0, in every mode, because an unreadable version is
  not evidence of staleness.
- An unexpected internal failure of the probe is reported the same way: a skipped probe,
  exit 0. The probe is never itself the reason a gate run goes red.

## WHAT — Verify intent (open questions for the human)
- None — the gap is stated in the engine's own comment (`warn_if_stale` is "silent in CI")
  and in `check/action.yml`'s scope note.

## WHAT — Notes & known limitations (informative)
- Why this cannot live in the engine, next to [[ARCH-CHECK-006]]'s `warn_if_stale`: a stale
  vendored engine does not contain the check that would report it stale. The detector has to
  run from something the consumer does not vendor — the action, which is always current for
  whatever `@vN` they reference.
- The reference version is whatever the pinned action ref ships. A consumer pinned to an
  exact old SHA is compared against that SHA's engine, which is the honest answer: it is the
  engine they asked for.
- Default `warn`, not `error`: adding a step that can newly fail a green build is a breaking
  change for an existing `@v2` pin. A repo that wants the hard stop opts in.

## HOW — Acceptance (= tests)
AC-1
  Given  a vendored engine older than the reference engine
  When   the probe runs in `warn` mode
  Then   it prints one message naming both versions and exits 0

AC-2
  Given  the same pair of engines
  When   the probe runs in `error` mode
  Then   it exits 1

AC-3
  Given  any pair of engines
  When   the probe runs in `off` mode
  Then   it prints nothing and exits 0

AC-4
  Given  a vendored engine at or ahead of the reference version
  When   the probe runs in `warn` or `error` mode
  Then   no staleness message appears and it exits 0

AC-5
  Given  a vendored or reference file that is missing or carries no readable
         `MAP_ENGINE_VERSION`, or a probe that raises unexpectedly
  When   the probe runs in `error` mode
  Then   it reports the probe as skipped and exits 0

AC-6
  Given  `GITHUB_ACTIONS` is set in the environment
  When   the probe reports a stale engine
  Then   the message is a `::warning::` annotation; without that variable it is a plain
         `WARN` line

## Example — in practice (optional, non-binding)
- A consumer vendored the engine a year ago and pinned `check@v2`. Their gate has been green
  the whole time, because half the checks it now runs did not exist in their copy. The next
  push shows one annotation: `vendored reqmap.py is stale (2025-08-02 < action 2026-08-20)`.

## WHERE — Current implementation
- `check/engine_staleness.py`, invoked by the `reqmap engine staleness` step in
  `check/action.yml`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-709
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# The staleness probe compares the vendored engine's MAP_ENGINE_VERSION

> The staleness probe compares the vendored engine's `MAP_ENGINE_VERSION` against the
> reference engine's.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-710
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# Check/action.yml runs the probe as a step of

> `check/action.yml` runs the probe as a step of the published gate action.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-711
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# The probe's --mode selects its behaviour: warn, error

> The probe's `--mode` selects its behaviour: `warn`, `error`, or `off`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-712
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# The action's stale-engine input sets that mode and

> The action's `stale-engine` input sets that mode and defaults to `warn`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-713
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# A vendored engine older than the reference produces

> A vendored engine older than the reference produces one message naming both versions and
> the re-seed remedy.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-714
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# In warn the message is a warning and

> In `warn` the message is a warning and the exit code stays 0.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-715
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# In error the same condition exits 1

> In `error` the same condition exits 1.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-716
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# Under GitHub Actions the message is emitted as

> Under GitHub Actions the message is emitted as a `::warning::` workflow annotation, so
> it surfaces on the run rather than only in the log.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-717
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# Off produces no output and exit 0

> `off` produces no output and exit 0.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-718
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# A vendored engine at or ahead of the

> A vendored engine at or ahead of the reference version produces no warning.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-719
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# A version that cannot be read from either

> A version that cannot be read from either file — absent file, unparseable value — is
> reported as a skipped probe with exit 0, in every mode, because an unreadable version is
> not evidence of staleness.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-STALEENGINE-720
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
superseded_by:
---

# An unexpected internal failure of the probe is

> An unexpected internal failure of the probe is reported the same way: a skipped probe,
> exit 0. The probe is never itself the reason a gate run goes red.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
