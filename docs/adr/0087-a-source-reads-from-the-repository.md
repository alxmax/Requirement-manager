# ADR-0087 — A source reads from the code folder or from the repository

- **Status:** Accepted. Extends [ADR-0077](0077-a-repository-describes-its-own-trace-tags.md).
- **Decided:** 2026-11-21
- **Evidence:** a scratch repository checked one folder at a time (`--code src`), its
  requirements in `specs/`: the source had to be written `../specs/*.txt`, and the same config
  could not serve two folders at different depths.

## Context

`REQUIREMENT_SOURCES` globs are joined to the code root. That was the repository root while a
scan always covered the repository. Checking one folder, the way a person or an assistant asks
for it, moves the code root and leaves the requirements behind.

## Decision

- **A source may say `root: repo`.** Its glob is then read from the nearest folder at or above
  the code root that holds `.git`. With no `root`, or `root: code`, nothing changes: an
  existing config reads the same files.
- **Never a silent fallback.** A glob that matches nothing from the code root but would from the
  repository is a problem with that hint; it is not read. A `root: repo` with no repository
  above is a problem too.
- **In the lazy module.** It lives in `customtrace.py`, loaded only with a source configured;
  the core does not change.

## Consequences

- One `_config.json` can serve checks of several folders.
- "Repository" means a folder with `.git`. A checkout without one (an archive) needs `root:
  code` and a relative glob, as before.

## Revisit when

- A repository needs a root that is neither, such as the folder holding `_config.json`.
