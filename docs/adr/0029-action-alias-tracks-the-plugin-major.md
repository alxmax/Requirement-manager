# ADR-0029 — The Action's major alias tracks the plugin's major

- **Status:** Accepted
- **Decided:** 2026-09-04
- **Supersedes:** the third-axis rule recorded in `CLAUDE.md` and in `check_versions.py`'s
  module docstring (never itself an ADR)
- **Evidence:** the alias history below; the ten-minute life of `@v3`

## Context

The published Action carried its own major-alias tag, `alxmax/requirement-manager/check@vN`,
and the rule was that this alias is a **third version axis** — tied neither to the plugin's semver
nor to `MAP_ENGINE_VERSION`. It named the Action's *interface* line and moved only when that
interface broke:

| alias | commit | plugin at the time |
|---|---|---|
| `@v1` | `9478d15` | 2.1.0, then frozen for 193 commits |
| `@v2` | `9adcc9d` | 3.4.0 — lived across 2.x, 3.0, 3.1, 3.3, 3.4 |
| `@v3` | `d2ed632` | 4.0.0 |

The reasoning was sound in itself: an alias that moves for reasons unrelated to its own interface
forces every consumer to re-pin for nothing.

It is also, in practice, a third number to hold in your head. `v4.0.0` shipping as `@v3` reads
like a mistake at every glance, and the person who has to notice it is not the maintainer who
knows the rule but the consumer copying a `uses:` line out of a README.

## Decision

**The Action's alias is the plugin's major.** `check@v5` ships with plugin `4.x`, `check@v5`
with `5.x`, and so on. The alias moves on every plugin major, whether or not the Action's own
interface changed that release.

- `check_versions.py` keeps asserting that every documented `uses:` reference names one major,
  and now also that this major equals `plugin.json`'s major.
- The release job continues to force-move the alias onto each released commit; nothing about the
  mechanism changes, only which number it carries.
- `@v1`, `@v2` and `@v3` stay where they point. A consumer pinned to one keeps the engine that
  was current then. `@v3` was live for ten minutes and is documented nowhere any more; it is left
  in place rather than deleted, because a dangling `uses:` is a broken build and a stale one is
  merely old.

## Consequences

- A consumer on `@vN` re-pins at every plugin major, even one that does not touch the Action.
  That is the cost this record accepts, and it is the exact cost the old rule was avoiding.
- In exchange, one fewer version axis to explain, and a `uses:` line whose number matches the
  release notes it came from.
- The Action's own interface changes are no longer visible in its version. A release that breaks
  a caller must say so in the CHANGELOG, since the alias number no longer carries that signal.

## Revisit when

- A plugin major ships with no Action change and a consumer reports the forced re-pin as friction
  — that is the old rule's argument arriving with evidence.
- The Action's interface breaks *between* plugin majors, which the alias can no longer express.
