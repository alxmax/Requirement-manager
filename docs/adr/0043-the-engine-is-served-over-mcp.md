# ADR-0043 — The engine is served over MCP

- **Status:** Accepted. **Supersedes** the deferral of the Senate run
  `2026-06-21_110220-reqmap-multiplatform-mcp` (verdict MODIFY), which built the MCP server
  only once "a named consumer that genuinely cannot use direct-CLI" appeared. Its four other
  conditions are kept, three as written and one changed (below).
- **Decided:** 2026-09-16, at the maintainer's direction: "MCP is a must have", for a repo on
  Copilot as much as for one on Claude Code.
- **Evidence:** the deferral's premise holds and is not what decides this. Every shell-capable
  assistant can already run `reqmap.py`. What it cannot do from a shell is discover the tools
  with typed parameters without reading `SKILL.md`, have a read-only question approved once
  as a tool rather than per terminal command, or reach the engine where the terminal is off.

## Context

The June run measured demand as n=0 and found MCP unlocked zero platforms. Both were true of
platforms. The case made now is about the assistant inside a platform that already works:
an agent choosing between sixteen `gate` flags from prose, and a client that approves every
terminal command, gets a worse engine than one that lists `reqmap_show(id)` and marks it
read-only.

## Decision

1. **`reqmap.py mcp [--allow-writes]`, a sixth verb.** ADR-0037 cut modes, not verbs, and a
   server is not a mode of `gate`: it runs until its client closes stdin. It is left out of
   the generated function-calling schema, because a server is not a function to call.
2. **Tools named for questions, run as subprocesses.** Fifteen tools (`reqmap_gate`,
   `reqmap_show`, `reqmap_search`, …), each one `reqmap.py` invocation in a fresh process.
   The engine keeps module state (`apply_config`, paths relative to the working directory),
   so a long-lived importer would carry one call's state into the next. A test holds every
   verb and flag a tool uses to the command registry, so the tool list cannot name a flag
   the CLI dropped.
3. **Read-only unless `--allow-writes`** (Senate condition 3). `reqmap_sync`, `reqmap_new`
   and `reqmap_release` are neither listed nor callable without it. Retiring a requirement
   is not offered at all: it deletes or deprecates contracts and stays a human's command.
4. **Stdlib, stdio, one pinned protocol revision, `2025-06-18`** (condition 5), with a
   conformance test that runs initialize, tools/list and tools/call over real stdio
   (condition 2).
5. **`init` writes `.mcp.json` and `.vscode/mcp.json`** when absent and never edits either
   (condition 4). **Changed:** the condition also asked the gate to warn when they are absent.
   It does not: MCP is an adoption choice, and a warning every consumer without a client
   config sees on every commit is the noise ADR-0016 measured the cost of.
6. **The plugin does not declare the server.** A plugin-declared server starts with default
   paths, wrong for any repo whose requirements are not at `requirements/` (this one's are
   under `plugin/`), and beside an `init`-written `.mcp.json` the agent would see every tool
   twice.

## Consequences

- `--show`, `--search` and `--dupes` return text, not JSON, until they gain `--json`.
- A repo whose engine is not vendored inside it gets no client config, and `init` says so.
- Each call pays a process start and a full scan; `--cache` on the server passes through.

## Revisit when

- A client reports that the per-call scan is too slow for interactive use.
- Claude Code gives plugin servers the project's requirement paths, which removes the reason
  in decision 6.
