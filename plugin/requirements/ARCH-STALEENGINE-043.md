---
id: ARCH-STALEENGINE-043
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-CHECK-006, ARCH-SELFGATE-039]
satisfies: [SYS-SHIP-108]
---

# Stale vendored engine, reported in CI

## Description
> Every consumer repo runs its own vendored copy of `reqmap.py`, and that copy only
> improves when someone re-seeds it. The engine's own staleness notice (`warn_if_stale`)
> is gated on `CLAUDE_PLUGIN_ROOT`, which exists in a Claude Code session and nowhere
> else — so it is silent in CI, the one place that runs on every push and the one place a
> months-old engine actually costs something: checks that shipped since are simply absent,
> and nothing says so.

Every bullet below is binding.
- The gate action's staleness probe compares a consumer's vendored `MAP_ENGINE_VERSION` against the reference engine's and reports the result per `--mode`. [[REQ-STALEENGINE-925]]
- The probe fails open. Nothing it can hit — `off` mode, an already-current engine, an unreadable version, an internal crash — produces a false staleness warning or a non-zero exit. [[REQ-STALEENGINE-926]]

## Cases
CASE-1
  Given  a vendored engine older than the reference engine
  When   the probe runs in `warn` mode
  Then   it prints one message naming both versions and exits 0

CASE-2
  Given  the same pair of engines
  When   the probe runs in `error` mode
  Then   it exits 1

CASE-3
  Given  any pair of engines
  When   the probe runs in `off` mode
  Then   it prints nothing and exits 0

CASE-4
  Given  a vendored engine at or ahead of the reference version
  When   the probe runs in `warn` or `error` mode
  Then   no staleness message appears and it exits 0

CASE-5
  Given  a vendored or reference file that is missing or carries no readable
         `MAP_ENGINE_VERSION`, or a probe that raises unexpectedly
  When   the probe runs in `error` mode
  Then   it reports the probe as skipped and exits 0

CASE-6
  Given  `GITHUB_ACTIONS` is set in the environment
  When   the probe reports a stale engine
  Then   the message is a `::warning::` annotation; without that variable it is a plain
         `WARN` line

## Context
**Terms**
- *vendored engine*: the consumer repo's own `scripts/reqmap.py`, the file the action executes; *reference engine*: `plugin/scripts/reqmap.py` inside the action's own checkout, i.e. the engine the referenced `check@vN` ships.

**Notes**
- Why this cannot live in the engine, next to [[ARCH-CHECK-006]]'s `warn_if_stale`: a stale
  vendored engine does not contain the check that would report it stale. The detector has to
  run from something the consumer does not vendor — the action, which is always current for
  whatever `@vN` they reference.
- The reference version is whatever the pinned action ref ships. A consumer pinned to an
  exact old SHA is compared against that SHA's engine, which is the honest answer: it is the
  engine they asked for.
- Default `warn`, not `error`: adding a step that can newly fail a green build is a breaking
  change for an existing `@v2` pin. A repo that wants the hard stop opts in.

**Example**
- A consumer vendored the engine a year ago and pinned `check@v2`. Their gate has been green
  the whole time, because half the checks it now runs did not exist in their copy. The next
  push shows one annotation: `vendored reqmap.py is stale (2025-08-02 < action 2026-08-20)`.

**Current implementation**
- `check/engine_staleness.py`, invoked by the `reqmap engine staleness` step in
  `check/action.yml`.


--------------------


---
id: REQ-STALEENGINE-925
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
---

# The gate action reports a stale vendored engine

## Description
> `check/action.yml` runs `check/engine_staleness.py` as a step of the published gate. It
> compares the consumer's vendored `reqmap.py` against the engine the action itself ships
> and, when the vendored copy is older, names both versions so a consumer learns their gate
> is missing checks that shipped since — without this, a stale copy stays silently behind.

Every bullet below is binding.
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

## Cases
CASE-1 — a vendored engine older than the reference one is named
  Given  a consumer's `scripts/reqmap.py` whose `MAP_ENGINE_VERSION` predates the action's own copy
  When   `engine_staleness.py` runs
  Then   it annotates the run, naming the vendored version and the reference version

CASE-2 — the gate action wires the staleness probe as its own step
  Given  `check/action.yml`
  When   its steps are inspected
  Then   one step invokes `engine_staleness.py` as part of the action's run

CASE-3 — the stale-engine input defaults to warn
  Given  `check/action.yml` with no `stale-engine` input set by the caller
  When   the action's inputs are read
  Then   `stale-engine` resolves to `warn`

CASE-4 — the stale message names the re-seed remedy
  Given  a vendored engine older than the reference engine
  When   the probe reports it
  Then   the message names the remedy of re-seeding the vendored copy

CASE-5 — warn mode reports and stays green
  Given  a stale vendored engine
  When   the probe runs with `--mode warn`
  Then   it prints a warning and the process exits 0

CASE-6 — error mode turns the same staleness into a failure
  Given  the same stale vendored engine
  When   the probe runs with `--mode error`
  Then   the process exits 1

CASE-7 — GitHub Actions gets an annotation, elsewhere a plain line
  Given  a stale vendored engine, once with `GITHUB_ACTIONS` set and once without
  When   the probe reports it
  Then   the first prints a `::warning::` annotation and the second a plain `WARN` line


--------------------


---
id: REQ-STALEENGINE-926
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-STALEENGINE-043]
---

# The staleness probe fails open, never the gate itself

## Description
> A version check that can crash or false-positive would make the gate less trustworthy, not
> more. So the probe treats `off` mode, an already-current engine, a missing or unreadable
> `MAP_ENGINE_VERSION`, and its own internal errors all the same way: no warning, exit 0. The
> probe is never itself the reason a run goes red.

Every bullet below is binding.
- `off` produces no output and exit 0.
- A vendored engine at or ahead of the reference version produces no warning.
- A version that cannot be read from either file — absent file, unparseable value — is
  reported as a skipped probe with exit 0, in `warn` and `error` mode, because an
  unreadable version is not evidence of staleness. `off` mode never reaches this check —
  it returns before the probe runs, so it reports nothing at all, skipped or otherwise.
- An unexpected internal failure of the probe is reported the same way: a skipped probe,
  exit 0. The probe is never itself the reason a gate run goes red.

## Cases
CASE-1 — off mode is silent
  Given  a stale vendored engine
  When   the probe runs with `--mode off`
  Then   it prints nothing and exits 0

CASE-2 — an up-to-date or newer engine never warns
  Given  a vendored engine at the same version as the reference, or newer
  When   the probe runs in `warn` or `error` mode
  Then   no staleness message appears and it exits 0

CASE-3 — an unreadable version is skipped, not treated as stale
  Given  a vendored `reqmap.py` missing `MAP_ENGINE_VERSION`
  When   the probe runs in `error` mode
  Then   it reports the probe as skipped and exits 0

CASE-4 — an internal probe crash never fails the gate
  Given  a probe run that raises an unexpected exception while comparing versions
  When   the probe runs in `error` mode
  Then   it reports the probe as skipped and exits 0 rather than propagating the exception

