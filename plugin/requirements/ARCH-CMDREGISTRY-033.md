---
id: ARCH-CMDREGISTRY-033
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001]
milestone: v2.7
satisfies: [SYS-SHIP-108]

---

# CLI command registry + generated integration artifacts

## Description
> `tool_definition.json` and the `SKILL.universal.md` command table were
> hand-maintained mirrors of the CLI and silently drifted whenever a command
> was added or renamed. A single declarative `COMMANDS` registry — with
> generation and a gate drift-guard — makes those mirrors impossible to diverge
> undetected.
- A `COMMANDS` dict is the single source of truth for the CLI command set; no other location may enumerate commands authoritatively.
- Argparse choices are derived from `COMMANDS` at runtime; no hard-coded choices literal is permitted.
- `tool_definition.json` (the function-calling schema) is generated from `COMMANDS` by the `gen-integration` command.
- The `SKILL.universal.md` command table is generated from `COMMANDS` by `gen-integration` and written into the `<!--##REQMAP:COMMANDS##-->` region; prose outside that region is never touched.
- Internal commands (e.g. `gen-integration`) are excluded from AI-facing generated artifacts.
- The gate fails (exit non-zero) when a committed generated artifact is stale relative to a fresh generation.
- All generators and the gate check are stdlib-only; no third-party imports are permitted.

## Verify intent (open questions for the human)
- None — intent and scope confirmed by implementation.

## Notes & known limitations (informative)
- `gen-integration` is the only command that writes generated artifacts; running it is required after any `COMMANDS` change before committing.
- The gate check (`_check_integration_fresh`) re-generates in a temp dir and compares byte-for-byte; it is deterministic because `_generate_schema` sorts JSON object keys and `_generate_command_table` iterates `COMMANDS` in insertion order (which is also the order exposed by `_cli_choices()` and `--help`).

## Cases (= tests)

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

## WHERE — Current implementation
- `COMMANDS` dict and `_cli_choices()` in `reqmap.py` (registry + choices derivation).
- `_generate_schema()` and `_generate_command_table()` / `_write_region()` in `reqmap.py` (artifact generators).
- `cmd_gen_integration()` and the `gen-integration` verb in `reqmap.py` (runner).
- `_check_integration_fresh()` wired into `gate` in `reqmap.py` (drift guard).

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-305
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# A COMMANDS dict is the single source of

> A `COMMANDS` dict is the single source of truth for the CLI command set; no other
> location may enumerate commands authoritatively.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-306
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# Argparse choices are derived from COMMANDS at runtime

> Argparse choices are derived from `COMMANDS` at runtime; no hard-coded choices literal
> is permitted.

Scenario: argparse choices trace back to COMMANDS with no hardcoded list
  Given  the live argparse parser built from `COMMANDS`
  When   `_cli_choices()` is called
  Then   its return value equals `list(COMMANDS)` in insertion order

## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-307
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# Tool_definition.json (the function-calling schema) is generated from COMMANDS

> `tool_definition.json` (the function-calling schema) is generated from `COMMANDS` by the
> `gen-integration` command.

Scenario: gen-integration derives tool_definition.json from COMMANDS
  Given  a `COMMANDS` entry with a summary, a positional arg and a flag
  When   `gen-integration` runs
  Then   `tool_definition.json` carries a matching function-calling schema entry for that command

## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-308
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# The SKILL.universal.md command table is generated from COMMANDS

> The `SKILL.universal.md` command table is generated from `COMMANDS` by `gen-integration`
> and written into the `<!--##REQMAP:COMMANDS##-->` region; prose outside that region is
> never touched.

Scenario: gen-integration rewrites only the marked command-table region
  Given  `SKILL.universal.md` with hand-written prose outside `<!--##REQMAP:COMMANDS##-->`
  When   `gen-integration` runs
  Then   the region's table refreshes and the surrounding prose is byte-identical

## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-309
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# Internal commands (e.g. gen-integration) are excluded from AI-facing

> Internal commands (e.g. `gen-integration`) are excluded from AI-facing generated
> artifacts.

Scenario: gen-integration omits internal commands from AI-facing output
  Given  `COMMANDS` including the internal `gen-integration` entry itself
  When   `gen-integration` runs
  Then   `tool_definition.json` lists no `gen-integration` function

## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-310
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# The gate fails (exit non-zero) when a committed

> The gate fails (exit non-zero) when a committed generated artifact is stale relative to
> a fresh generation.

Scenario: gate fails on a stale generated artifact
  Given  a committed `tool_definition.json` that differs from a fresh generation
  When   `gate` runs
  Then   it exits non-zero, naming the stale artifact

## Members in code (auto)




--------------------


---
id: REQ-CMDREGISTRY-311
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
superseded_by:
---

# All generators and the gate check are stdlib-only

> All generators and the gate check are stdlib-only; no third-party imports are permitted.

Scenario: the generator and gate-check code import no third-party module
  Given  the source of `_generate_schema`, `_generate_command_table` and `_check_integration_fresh`
  When   their imports are inspected
  Then   every import resolves to the Python standard library

## Members in code (auto)
