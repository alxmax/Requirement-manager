# ADR-0008 — One command registry; integration artifacts are generated

- **Status:** Accepted
- **Decided:** 2026-06-21 (`REQ-CMDREGISTRY-033`)
- **Evidence:** `TODO.md` v2.7 and the design spec it names; `CLAUDE.md` "Command registry"

## Context

The CLI is described in four places: `argparse`, `plugin/tool_definition.json` (an OpenAI
function-calling schema, so non-Claude assistants can drive the tool), the command table in
`SKILL.universal.md`, and the docs. Three of those were hand-maintained mirrors of the first,
and they were already drifting — a command list that is a *copy* of the truth is a copy that
goes stale the first time someone is in a hurry.

The irony is the point: a tool whose entire purpose is catching a description that no longer
matches its implementation was carrying four descriptions of itself.

## Decision

One declarative `COMMANDS` dict near the top of `reqmap.py` is the CLI's single source of
truth: one entry per command, with its summary, positional argument and flags. `argparse`
choices derive from it. `tool_definition.json` and the delimited command-table region inside
`SKILL.universal.md` are **generated** from it by `gen-integration`, and `gate` regenerates both
in memory and byte-compares against the committed copies — an **error**, mirroring `map --check`.

Curated prose — when to use a command, why it exists — stays hand-authored outside the
generated region.

## Consequences

- Adding a command is one registry entry plus `gen-integration`. Forgetting the regeneration
  step fails the gate instead of shipping a schema that lies.
- Two files in the repo must never be hand-edited, which is a rule a newcomer cannot infer —
  hence the warning in `CLAUDE.md` and `CONTRIBUTING.md`.
- The dispatch ladder was deliberately **not** rewritten to dispatch off the registry. Deriving
  the argparse surface is mechanical and testable; rewriting dispatch would have been a
  behaviour change dressed as a refactor, and CLI behaviour stayed byte-identical.
- The same principle applies elsewhere in the repo: the map, the roadmap chart and the site's
  engine-owned regions are all generated and freshness-checked rather than hand-maintained.

## Revisit when

A second thing about the CLI needs to be *manually* true in more than one place. The answer will
be to move it into the registry, not to accept a second mirror.
