# ADR-0085 — Drift holds on an existing corpus

- **Status:** Accepted. Extends [ADR-0077](0077-a-repository-describes-its-own-trace-tags.md)
  (requirements read from text and HTML sources) and the member drift of ARCH-MEMBERDRIFT-027.
- **Decided:** 2026-11-20
- **Evidence:** a scratch repository with its requirements in a text file, read through
  `REQUIREMENT_SOURCES`, and tags on the line above each function, as most code writes them.
  Before this record: `_memberlock.json` held no member at all, so a changed function was never
  reported, and an edited requirement was absorbed by the next `sync` and gone from the gate.

## Context

The case this tool is most often brought to is a repository that already has its requirements
and its tags, where the question is whether the two still agree. Two things undid that answer.

A member hash is keyed to the Python definition a tag sits in, and a tag outside one falls back
to the whole file. A tag on the comment line above a function is outside it. A file tagged by
several requirements is then shared, its hash cannot be blamed on one of them, and it is
dropped: member drift said nothing about any of them.

A confirmed requirement whose text changed is set back to draft by `sync`, so a person re-reads
it. A requirement read from a text or HTML source has no `status:` line to set. `sync` printed
that, then advanced the lock as if the demotion had happened, and the change was gone.

## Decision

- **A tag in the unbroken comment block right above a top-level Python definition, or above
  its decorators, keys that definition.** A blank line ends the block. The hash still covers
  the definition only, so editing the comments is not a change of code. Other languages keep
  the whole-file hash: their spans are read by heuristics, and a wrong span is a wrong signal.
- **A requirement `sync` cannot demote keeps its baseline.** Its lock entry stays at the hash it
  was confirmed at, `sync` says so, and the gate reports the drift until `--accept-drift`,
  which records the reason.

## Consequences

- A tag above a definition in a file no other requirement tags used to hash the whole file; it
  now hashes the definition, so a line added elsewhere in that file is no longer drift. That is
  the rule a tag inside a definition already followed (REQ-MEMBERDRIFT-982).
- A member key can change from a file to a definition on the first `sync` after an upgrade. A
  key with no recorded hash is skipped, so the upgrade reports no drift; the next `sync`
  baselines it.
- `CORE_LOGICAL_BUDGET` rises from 6,814 to 6,825 for the span lead and the kept baseline.
  The physical total stays under its 20,000 ceiling.
- A brace-language file shared by several requirements still has no member drift.

## Revisit when

- A repository in a brace language asks for member drift on a shared file: then its spans need
  a reader as trustworthy as Python's `ast`.
- A source format gains a status the engine can write: then it is demoted like Markdown.
