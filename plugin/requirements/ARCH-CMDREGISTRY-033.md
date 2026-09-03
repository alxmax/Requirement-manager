---
id: ARCH-CMDREGISTRY-033
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.7
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-SHIP-108]
---

# CLI command registry + generated integration artifacts

## Description
> `tool_definition.json` and the `SKILL.universal.md` command table were
> hand-maintained mirrors of the CLI and silently drifted whenever a command
> was added or renamed. A single declarative `COMMANDS` registry — with
> generation and a gate drift-guard — makes those mirrors impossible to diverge
> undetected.

Every bullet below is binding.
- A `COMMANDS` dict is the single source of truth for the CLI's commands: argparse's choices, the generated `tool_definition.json`, and the `SKILL.universal.md` command table all derive from it, and the gate fails when a generated artifact goes stale. [[REQ-CMDREGISTRY-834]]

## Cases
CASE-1
  Given  the `COMMANDS` registry and the live argparse parser
  When   `_cli_choices()` is called
  Then   its return value equals `list(COMMANDS)` (insertion order) — no literal choices exist

CASE-2
  Given  a committed `tool_definition.json` whose content differs from a fresh generation
  When   `gate` runs
  Then   the gate exits non-zero (stale artifact is a hard error)

CASE-3
  Given  `gen-integration` is run
  When   `tool_definition.json` and the `SKILL.universal.md` command table are written
  Then   their content is byte-for-byte reproducible on a second run with the same `COMMANDS`

CASE-4
  Given  any existing CLI command (e.g. `init`, `gate`, `sync`)
  When   it is invoked via the standard CLI entry point
  Then   it executes without error — no regression from the registry migration

CASE-5
  Given  the generated artifacts are inspected for imports
  When   the generator code runs
  Then   only stdlib modules are imported; no third-party dependency is present

## Context
**Notes**
- `gen-integration` is the only command that writes generated artifacts; running it is required after any `COMMANDS` change before committing.
- The gate check (`_check_integration_fresh`) re-generates in a temp dir and compares byte-for-byte; it is deterministic because `_generate_schema` sorts JSON object keys and `_generate_command_table` iterates `COMMANDS` in insertion order (which is also the order exposed by `_cli_choices()` and `--help`).

**Current implementation**
- `COMMANDS` dict and `_cli_choices()` in `reqmap.py` (registry + choices derivation).
- `_generate_schema()` and `_generate_command_table()` / `_write_region()` in `reqmap.py` (artifact generators).
- `cmd_gen_integration()` and the `gen-integration` verb in `reqmap.py` (runner).
- `_check_integration_fresh()` wired into `gate` in `reqmap.py` (drift guard).


--------------------


---
id: REQ-CMDREGISTRY-834
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
---

# One COMMANDS dict drives argparse, schema and docs

## Description
> `tool_definition.json` and the `SKILL.universal.md` command table used to be hand-maintained
> mirrors of the CLI that silently drifted whenever a command was added or renamed. Deriving
> argparse's choices, the generated function-calling schema, and the docs table from one
> `COMMANDS` dict — plus a gate check that fails on staleness — makes that kind of drift
> impossible to miss.

Every bullet below is binding.
- A `COMMANDS` dict is the single source of truth for the CLI command set; no other location may enumerate commands authoritatively.
- Argparse choices are derived from `COMMANDS` at runtime; no hard-coded choices literal is permitted.
- `tool_definition.json` (the function-calling schema) is generated from `COMMANDS` by the `gen-integration` command.
- The `SKILL.universal.md` command table is generated from `COMMANDS` by `gen-integration` and written into the `<!--##REQMAP:COMMANDS##-->` region; prose outside that region is never touched.
- Internal commands (e.g. `gen-integration`) are excluded from AI-facing generated artifacts.
- The gate fails (exit non-zero) when a committed generated artifact is stale relative to a fresh generation.
- All generators and the gate check are stdlib-only; no third-party imports are permitted.

## Cases
CASE-1 — argparse choices trace back to COMMANDS with no hardcoded list
  Given  the live argparse parser built from `COMMANDS`
  When   `_cli_choices()` is called
  Then   its return value equals `list(COMMANDS)` in insertion order

CASE-2 — gen-integration derives tool_definition.json from COMMANDS
  Given  a `COMMANDS` entry with a summary, a positional arg and a flag
  When   `gen-integration` runs
  Then   `tool_definition.json` carries a matching function-calling schema entry for that command

CASE-3 — gen-integration rewrites only the marked command-table region
  Given  `SKILL.universal.md` with hand-written prose outside `<!--##REQMAP:COMMANDS##-->`
  When   `gen-integration` runs
  Then   the region's table refreshes and the surrounding prose is byte-identical

CASE-4 — gen-integration omits internal commands from AI-facing output
  Given  `COMMANDS` including the internal `gen-integration` entry itself
  When   `gen-integration` runs
  Then   `tool_definition.json` lists no `gen-integration` function

CASE-5 — gate fails on a stale generated artifact
  Given  a committed `tool_definition.json` that differs from a fresh generation
  When   `gate` runs
  Then   it exits non-zero, naming the stale artifact

CASE-6 — the generator and gate-check code import no third-party module
  Given  the source of `_generate_schema`, `_generate_command_table` and `_check_integration_fresh`
  When   their imports are inspected
  Then   every import resolves to the Python standard library

