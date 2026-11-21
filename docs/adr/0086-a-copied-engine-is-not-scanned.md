# ADR-0086 — A copied engine is not scanned

- **Status:** Accepted.
- **Decided:** 2026-11-20
- **Evidence:** a repository with one requirement, `init` run, then
  `plugin-full/skills/requirement-manager/` copied into `.github/skills/`: `gate` reported 291
  RM001 errors, 290 of them from the copy's engine and viewer. After this record: one, the
  repository's own.

## Context

The skill carries its own engine (ADR-0068), and assistants read a skill from inside the
repository: Copilot from `.github/skills`, `.agents/skills` (where APM now installs it) and
`.claude/skills`. The engine's source is tagged with this repository's requirement ids, which
exist nowhere else, so every one of them is a dangling tag in the repository that installed the
skill. `init` writes `.reqmapignore` lines for `scripts/reqmap.py`, not for a skill folder, and
an ignore file written before is never edited.

## Decision

- **The scan skips a copied engine by its shape, not by a path.** In a directory holding
  `reqmap.py` beside `reqmap_engine/`, it skips `reqmap_engine/`, `reqmap.py` and
  `_map_viewer.html`. Every other file there is scanned: a repository that put the engine in its
  own `scripts/` keeps its own tags.
- **The engine's own repository scans its engine.** It is recognised as before, by its plugin
  manifest and viewer source; the check moves from `workspace` to `scan`, below it.

## Consequences

- A repository's own `reqmap.py` beside its own `reqmap_engine/` package would be skipped. No
  such repository is known.
- `CORE_LOGICAL_BUDGET` rises from 6,825 to 6,828.
- The physical total reached its 20,000 ceiling with this change. ADR-0053 asks for a decision
  there; the maintainer moved `TOTAL_LINE_CEILING` to 21,000 (2026-11-21), so the engine keeps
  room for the next fixes. The ceiling is still an alarm, not a target.

## Revisit when

- A repository reports its own code skipped by this rule.
