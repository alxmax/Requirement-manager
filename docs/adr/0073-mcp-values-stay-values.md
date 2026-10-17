# ADR-0073 — An MCP value stays a value, a message is checked before it is read, and a fan-out band is checked before it is used

- **Status:** Accepted. Amends the number in [ADR-0072](0072-retire-unbounded-quantity.md).
- **Decided:** 2026-10-17
- **Evidence:** each defect was reproduced on `main` at `2146cbd` before any change, and
  each new test fails on that code and passes on this one.
  - `reqmap_release_plan`, a tool declared `writes: False`, built `sync --json --release
    --apply` from `version: "--apply"`. `--apply` is `sync`'s own flag, so the registry's
    foreign-flag check does not catch it, and the call would have bumped the version files,
    written the CHANGELOG entry and dropped the milestone from the plan.
  - Four of five malformed messages ended the server: a `method` that is a list
    (`TypeError`), `params` that is a list or a string (`AttributeError`), and `arguments`
    that is a number (`TypeError`).
  - Eight of ten `LINT_FANOUT_BANDS` overrides were either a traceback in the lint
    (`TypeError`, `ValueError`) or a band nothing can satisfy (`[10, 2]`, `[true, 3]`,
    `[-1, 3]`), accepted without a word.
  - `python scripts/check_engine_budget.py` on this commit: core 6,644 logical lines.

## Context

The MCP server runs each tool as the CLI in a fresh process (ADR-0043), so what a call may
do is whatever the argument list it builds may do. Two things about that list were left to
the parser: a flag and its value were two arguments, so a value that looked like an option
was read as one; and a requirement id or a version was only checked to be text.

The server also read a message's fields before checking what they were, and a failed run
(`FileNotFoundError` from a missing interpreter) was not caught at all.

The fan-out override accepted any list for a level and left the lint to find out.

## Decision

- **A flag and its value are one argument** (`--release=v1.2.0`, `--since=--apply`), so a
  value cannot be read as an option, and a requirement id and a version are checked: an id
  must be `[A-Za-z0-9][A-Za-z0-9_-]*`, a version one `semver3` reads. Anything else is
  -32602 and runs nothing. The tool table still says which tools write; this makes it true
  whatever the arguments say.
- **A message is checked before it is used.** `method` that is not text is -32600; `params`
  that is not an object, and `arguments` that is not an object, are -32602. A call that
  raises is -32603 with the cause, and the server keeps reading after each.
- **A fan-out band is `[low, high]`**, `high` a whole number, `low` one or null, no more
  than `high`. A band that is not is named on stderr, becomes an `INPUT:config` warning
  (an error under `--strict`, ADR-0054) and leaves that level on its default; every other
  entry still applies.
- `CORE_LOGICAL_BUDGET` is 6,644. The seven lines are the band check in `config.py`, which
  every command loads. `mcp.py` is imported only by `reqmap.py mcp` and is not in the number.

## Consequences

- A client that sent `version: "1.2"` to `reqmap_release_plan` still works: `semver3`
  reads `X.Y` as `X.Y.0`, the same as the CLI.
- A free-text argument that begins with `-` (a search for `--apply`) now reaches the engine
  as a value, where before the parser took it for a flag and answered with a usage error.
- A repository whose `_config.json` held a band the lint would have crashed on now gets a
  warning where it got a traceback. One that held a band like `[10, 2]` now gets the
  default for that level, where it got a band no count satisfies.

## Revisit when

- A tool is added that takes a free-text argument the engine treats as a path or a command.
- A cut on the gate path brings the measured core under 6,644.
