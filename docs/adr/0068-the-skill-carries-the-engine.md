# ADR-0068 — The skill carries a generated copy of the engine

- **Status:** Accepted
- **Decided:** 2026-10-12
- **Evidence:** `scripts/bundle_skill_engine.py`; `scripts/test_bundle_skill_engine.py`;
  [APM package types](https://microsoft.github.io/apm/reference/package-types/) ("each
  `skills/<name>/` is promoted to `<target>/skills/<name>/`"); a seeded `init --minimal`
  → `sync` → `gate` run from the copy

## Context

An APM install copies one directory per skill, `skills/<name>/`, into the agent's skills
directory. The engine lives in `plugin/scripts/`, beside `skills/`, so a skill installed that
way had instructions to copy `${REQMAP_PLUGIN_ROOT}/scripts/reqmap.py` and no such file.
Under the Claude Code plugin the same instructions work, because the whole plugin directory
is installed.

## Decision

`plugin/skills/requirement-manager/scripts/` holds `reqmap.py`, `reqmap_engine/` and
`_map_viewer.html`, laid out exactly as under `plugin/scripts/`. `REQMAP_PLUGIN_ROOT` may
therefore name the plugin or the skill, and the seeding commands are the same for both.

The copy is generated, committed, and compared byte for byte in CI and the dev hook, the
trade [ADR-0005](0005-committed-build-artifacts.md) already makes for the viewer. It is in
both `.reqmapignore` files: scanned, every member would be counted twice, the failure
`build/**` is ignored for. Tests and bytecode are not carried.

## Consequences

- The repository holds the engine twice (about 1.3 MB). Each engine change is a second,
  identical diff; the cost of forgetting it is a red check, not a stale install.
- No engine code changes, so `MAP_ENGINE_VERSION` does not move for this. A bundle refresh
  rides on the engine bump that caused it.
- `requirement-quality-review` carries no engine. It runs the one `requirement-manager`
  seeded into the consumer repo, as it did.
- A symlink from the skill to `plugin/scripts/` was not taken: a git symlink needs
  privileges on Windows, and APM validates paths in an install.

## Revisit when

APM copies a package's sibling directories, or the engine moves under `skills/`: then the
copy is dead weight and should go.
