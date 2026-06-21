---
id: REQ-CMDREGISTRY-033
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
satisfies: [NEED-SSOT-001]
milestone: v2.7
---

# CLI command registry + generated integration artifacts

> `tool_definition.json` and the `SKILL.universal.md` command table were
> hand-maintained mirrors of the CLI and silently drifted whenever a command
> was added or renamed. A single declarative `COMMANDS` registry — with
> generation and a gate drift-guard — makes those mirrors impossible to diverge
> undetected.

## WHAT — Contract (normative)
- A `COMMANDS` dict shall be the single source of truth for the CLI command set; no other location may enumerate commands authoritatively.
- Argparse choices shall be derived from `COMMANDS` at runtime; no hard-coded choices literal is permitted.
- `tool_definition.json` (the function-calling schema) shall be generated from `COMMANDS` by the `gen-integration` command.
- The `SKILL.universal.md` command table shall be generated from `COMMANDS` by `gen-integration` and written into the `<!--##REQMAP:COMMANDS##-->` region; prose outside that region shall not be touched.
- Internal commands (e.g. `gen-integration`) shall be excluded from AI-facing generated artifacts.
- The gate shall fail (exit non-zero) when a committed generated artifact is stale relative to a fresh generation.
- All generators and the gate check shall be stdlib-only; no third-party imports are permitted.

## WHAT — Verify intent (open questions for the human)
- None — intent and scope confirmed by implementation.

## WHAT — Notes & known limitations (informative)
- `gen-integration` is the only command that writes generated artifacts; running it is required after any `COMMANDS` change before committing.
- The gate check (`_check_integration_fresh`) re-generates in a temp dir and compares byte-for-byte; it is deterministic because `_generate_schema` sorts JSON object keys and `_generate_command_table` iterates `COMMANDS` in insertion order (which is also the order exposed by `_cli_choices()` and `--help`).

## HOW — Acceptance (= tests)

AC-1
  Given  the `COMMANDS` registry and the live argparse parser
  When   `_cli_choices()` is called
  Then   its return value equals `list(COMMANDS)` (insertion order) — no literal choices exist

AC-2
  Given  a committed `tool_definition.json` whose content differs from a fresh generation
  When   `gate` runs
  Then   the gate exits non-zero (stale artifact is a hard error)

AC-3
  Given  `gen-integration` is run
  When   `tool_definition.json` and the `SKILL.universal.md` command table are written
  Then   their content is byte-for-byte reproducible on a second run with the same `COMMANDS`

AC-4
  Given  any existing CLI command (e.g. `init`, `gate`, `sync`)
  When   it is invoked via the standard CLI entry point
  Then   it executes without error — no regression from the registry migration

AC-5
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
