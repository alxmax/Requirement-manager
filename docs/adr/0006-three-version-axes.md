# ADR-0006 — Three independent version numbers

- **Status:** Accepted
- **Decided:** plugin semver + engine date from 2026-06-03; action alias formalised 2026-08-20
- **Evidence:** `CHANGELOG.md` `v2.18.1`; `scripts/check_versions.py`; `CLAUDE.md`

## Context

Three things ship on different clocks and are consumed by different mechanisms:

1. The **plugin** a user installs through the Claude Code marketplace.
2. The **engine file** a repo vendors, which may be years older than the plugin.
3. The **GitHub Action** a workflow references as `check@vN`.

One number cannot serve all three. A plugin bump must be visible to `/plugin update` even when
the engine did not change (a skill edit is invisible to consumers otherwise); a vendored engine
must be able to tell it is behind without knowing anything about marketplaces; a workflow
pinned to `@v2` must keep meaning "the current release on the v2 interface line".

## Decision

Three axes, deliberately not derived from each other:

- **Plugin semver** — `plugin.json` plus twice in `marketplace.json`, kept in lockstep by
  `scripts/check_versions.py --fix`. Any shipped change bumps it. A bump without a matching
  `` `vX.Y.Z` `` CHANGELOG heading fails CI, and the release job cuts the tag from this number.
- **`MAP_ENGINE_VERSION`** — an ISO date with an optional same-day suffix (`2026-08-20.2`)
  inside `reqmap.py`. Engine changes only. It exists so a copy can compare itself to another
  copy, which is all [ADR-0010](0010-staleness-detection-in-the-action.md) needs.
- **`check@vN`** — a major *alias* naming an interface line, not a release. It is force-moved
  onto every released commit, so it never rots behind the repo again.

The `uses:` line in `check/action.yml` **is** the source of truth for the action's major —
there is no separate version file to fall out of step with the docs — and `check_versions.py`
asserts `action.yml`, `README.md` and `CLAUDE.md` all name the same one.

## Consequences

- Conflating them is the recurring confusion, in this repo and in bug reports, which is why the
  issue template asks for two numbers and this record exists.
- The major bumps only for a change that can newly **fail** a green build for an unchanged pin.
  `@v1` gained two default-on enforcing steps and was therefore frozen rather than re-pointed;
  the warn-only staleness step in v2.22.0 stayed on `@v2` under the same test.
- Freezing a major strands its users on old content — `@v1` gets nothing, including security
  fixes. That cost is accepted, and stated in `SECURITY.md`.
- Three axes means three ways to be inconsistent, so all three are machine-checked as the first
  step of CI.

## Revisit when

A fourth artifact ships on its own clock. The rule to apply is the one above: a version number
exists per *consumption mechanism*, never per component.
