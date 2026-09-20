---
id: ARCH-CMDREGISTRY-033
status: draft
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
- The registry is also emitted as data on the map, so a surface can document the CLI without running it. [[REQ-CMDREGISTRY-963]]
- `gate` owns the verdict and the reports on it, and `ask` owns every other read-only question; `gate`'s old spellings of those questions run the same call with one migration line on stderr until v8.0.0. [[REQ-CMDREGISTRY-1031]]
- The registry holds six verbs: `new` and `new --from-todo` are removed, and the template they stamped stays as the documented shape. [[REQ-NEWGONE-1034]]

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
milestone: v3.2
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
- The `SKILL.md` command list is generated the same way, into the same region marker, as a grouped bullet list. It is the contract an assistant reads on a fresh repo, so a verb that exists is documented there and one that does not, is not.
- Internal commands (e.g. `gen-integration`) are excluded from AI-facing generated artifacts.
- A command marked `tool: False` — `mcp`, a server rather than a function to call — is left out
  of the function-calling schema and still documented in both SKILL command regions.
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
  Then   the region's table refreshes, the surrounding prose is byte-identical, and the
         written body carries the file's own line endings, so a rerun leaves no diff

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

CASE-7 — SKILL.md documents exactly the registry
  Given  the committed `SKILL.md`
  When   its command region is compared with a fresh rendering from `COMMANDS`
  Then   they match, every non-internal verb appears exactly once, and no other verb appears

---
id: REQ-CMDREGISTRY-963
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-CMDREGISTRY-033]
---

# The command registry as data on the map

## Description
> A command reference kept by hand goes stale the first time a verb is renamed — which is exactly
> what `v4.0.0` did to eleven of them. Emitting the registry onto `_map.json` means the reference
> a reader sees was generated from the same table the parser was built from, so a command that
> exists is documented and one that was removed disappears on the next `sync`.

Every bullet below is binding.
- The map payload carries a `commands` list generated from the command registry, one entry per
  user-facing command, with its name, its positional argument, its summary and its flags.
- Each entry names the moment of work it belongs to — authoring, building or reading — from a
  grouping declared once beside the registry rather than restated per surface.
- A command marked internal is absent from the list, exactly as it is absent from the generated
  schema and the command table.
- A map produced before this field existed carries no `commands` key, and every reader treats its
  absence as "no reference available" rather than as an error.

## Cases
CASE-1 — every user-facing command appears
  Given  the command registry
  When   the manifest is generated
  Then   it holds one entry per non-internal command, and none for an internal one

CASE-2 — an entry carries what a reader needs
  Given  a command that takes an argument and two flags
  When   its manifest entry is read
  Then   the entry carries its name, argument, summary and both flags with their help text

CASE-3 — each command is placed in a group
  Given  the manifest
  When   its entries are inspected
  Then   every entry names one of the declared groups

---
id: REQ-CMDREGISTRY-1031
status: draft
level: code
layer: feature
owner: Alex
milestone: v7.22.0
satisfies: [ARCH-CMDREGISTRY-033]
---

# `ask` holds the questions, `gate` the verdict

## Description
> `gate` was two things under one name: the commit verdict every hook runs, and every question
> the engine can answer, sixteen flags in all. A reader choosing a flag had to know which of
> them run the verdict and which never do. ADR-0044 moves the questions to their own verb.

Every bullet below is binding.
- The command registry gives `gate` exactly nine flags: `--audit`, `--risk`, `--show`, `--all`,
  `--untagged`, `--badge`, `--strict`, `--json` and `--since`.
- `ask` owns `--search`, `--dupes`, `--design`, `--review`, `--i18n`, `--top`, `--threshold` and
  `--json`. `ask --review` with no id plans the whole corpus.
- Until v8.0.0, `gate` given one of `ask`'s flags runs the same call as `ask`: the same exit code
  and byte-identical stdout, plus exactly one line on stderr naming the `ask` spelling and v8.0.0.
  The line never goes to stdout, where it would break `--json` for every parser.
- `ask` given a flag the registry gives another verb, or given no mode at all, exits 2 with one
  line and runs nothing.
- No MCP tool invokes `gate` with a flag `ask` owns.

## Cases
CASE-1 — the registry splits the flags
  Given  the command registry
  When   the flags of `gate` and `ask` are read
  Then   `gate` has nine, none of them a moved flag, and `ask` has every moved flag

CASE-2 — the old spelling is the same call plus one stderr line
  Given  a corpus and each moved spelling, with and without `--json`
  When   it runs as `gate …` and as `ask …`
  Then   both exit 0 with identical stdout, JSON output parses, and `gate`'s stderr adds exactly
         one line naming `ask` and v8.0.0

CASE-3 — `ask` refuses what it does not own
  Given  a corpus
  When   `ask` runs with no mode, or with `--strict`, `--risk`, `--since` or `--show`
  Then   it exits 2 and no verdict is printed

CASE-4 — the MCP tools ask `ask`
  Given  the MCP tool table
  When   each tool's verb and flags are read
  Then   no tool pairs `gate` with a flag `ask` owns

--------------------


---
id: REQ-NEWGONE-1034
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CMDREGISTRY-033]
---

# `new` is gone; six verbs remain, and the template stays

## Description
> `new` stamped a blank requirement out of the built-in template and `new --from-todo`
> pre-filled one from a `TODO.md` item. Neither was used: this corpus keeps its
> requirements as module files a command cannot write into, and the verb still cost a
> registry entry, a parser branch, an MCP writing tool and about twenty tests. ADR-0045
> deprecated it in v7.22.1 and removes it here. What replaces it is not a command — a
> requirement is a file someone writes, by hand or by asking an assistant.

Every bullet below is binding.
- The command registry holds six verbs — `init`, `gate`, `ask`, `sync`, `clarify`, `mcp` —
  and `new` is not among them. The author group is `init` and `clarify`.
- The verb `new`, with or without `--from-todo`, is refused with exit 2 and writes no
  requirement file. The usage line names the six verbs that remain.
- No MCP tool scaffolds a requirement: `reqmap_new` is gone, and no tool invokes `new`.
- The built-in template stays and keeps the shape it taught: the `Context` section, the
  plain present voice, and a body its own linter does not flag.
- `new` is a retired name, so an instruction that still tells a reader to run it fails
  `check_retired_verbs.py`.

## Cases
CASE-1 — the registry holds six verbs
  Given  the command registry and the command groups
  When   their verbs are read
  Then   they are `init`, `gate`, `ask`, `sync`, `clarify`, `mcp`, and the author group is
         `init` and `clarify`

CASE-2 — the verb is refused and writes nothing
  Given  a repo with a `requirements/` directory and a `TODO.md`
  When   the CLI is called with `new AREA-GONE-001`, and with `new --from-todo … --id …`
  Then   both exit 2 and neither writes a requirement file

CASE-3 — no MCP tool scaffolds
  Given  the MCP tool table
  When   its names and verbs are read
  Then   none is `reqmap_new` and none invokes `new`

CASE-4 — the template outlives the verb
  Given  the built-in requirement template
  When   it is linted the way a requirement is
  Then   it carries the `Context` section, uses no modal in a clause, and its body raises
         none of `anonymous-subject`, `statement-too-long`, `statement-size`

## Context
**Notes**
- The removal is recorded twice on purpose: this requirement says what the CLI is now,
  and ARCH-NEW-004 / ARCH-PROMOTE-TODO-001 stay in the corpus as `deprecated`, so a
  reader who meets an old `# implements:` tag or an old ADR still finds what they named.
- `_warn_number_collision` and the id regex went with the verb — nothing called them once
  `cmd_new` and `cmd_promote_todo` were gone. `_parse_todos`, `_set_frontmatter_status`
  and `_write_frontmatter_status` stay: `gate`, `retire`, `mapcmd` and `mapdata` read them
  (ADR-0045 decision 3).
