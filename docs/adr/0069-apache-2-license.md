# ADR-0069 — Apache 2.0, the same licence as the projects that ship this engine

- **Status:** Accepted. Supersedes [ADR-0066](0066-mit-license.md).
- **Decided:** 2026-10-13
- **Evidence:** `LICENSE`; `pyproject.toml`; `plugin/.claude-plugin/plugin.json`;
  `plugin/apm.yml`; the Consilium plugin, which vendors `reqmap.py` and `reqmap_engine/`
  and moved to Apache 2.0 the same day; `git shortlog -sn` (one human author).

## Context

ADR-0066 chose MIT over Apache 2.0 because one author held the copyright and MIT is the
text a reviewer already knows. It named a revisit condition: a distributor that needs a
patent grant the MIT text does not give.

The engine is now distributed inside other plugins by the same author. Consilium vendors
`scripts/reqmap.py` and `scripts/reqmap_engine/` and is relicensed under Apache 2.0, so
its repository carried two licences side by side. Apache 2.0 also states what MIT leaves
unsaid: an express patent grant from every contributor, terminated for anyone who sues
over a patent in the work, and no grant of the project's names.

## Decision

The licensor, Schipor Alexandru, relicenses the work under the Apache License 2.0,
effective with v8.23.0. Releases up to v8.22.4 stay under MIT.

## Consequences

- `LICENSE` holds the Apache 2.0 text. `pyproject.toml`, `plugin.json` and `apm.yml` say
  `Apache-2.0`, and ARCH-ADOPT-075's package-metadata clause names it.
- A repository that copies the engine keeps a `LICENSE` next to the copy, as before.
- Contributions from this version on are under Apache 2.0. `CONTRIBUTING.md` says so.

## Revisit when

A second copyright holder appears whose work cannot be relicensed by the statements
above. That is a new record, not an edit of this one.
