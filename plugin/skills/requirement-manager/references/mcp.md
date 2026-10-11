# MCP server (`reqmap.py mcp`)

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

The engine is also served over the Model Context Protocol (ADR-0043). When the `reqmap_*`
tools are available in this session (in Claude Code they appear as `mcp__reqmap__reqmap_gate`
and so on), **ask the corpus through them instead of the terminal**: they take typed
arguments, return JSON, are marked read-only, and need no per-command approval. Use the
terminal for what the server does not offer. When the tools are absent, every command above
works the same from the shell.

| Question | Tool | Same as |
|---|---|---|
| Is the repo in step? (exit 1 is a FAIL verdict, not a tool error) | `reqmap_gate` | `gate` |
| What should I do next? | `reqmap_next` / `reqmap_health` | `gate --risk` / `--risk --json` |
| What does this requirement say, and where is its code? | `reqmap_show(id)` | `gate --show ID --json` |
| Which requirement covers X? | `reqmap_search(query)` | `ask --search Q --json` |
| Everything that is wrong, at once | `reqmap_audit` | `gate --audit --json` |
| Do two contracts overlap? | `reqmap_dupes` | `ask --dupes --json` |
| What is unanswered in a requirement? | `reqmap_clarify(id)` | `clarify ID --json` |
| Review plan / tag coverage | `reqmap_review(id)` / `reqmap_untagged` | `ask --review` / `gate --risk --untagged` |
| What would the next release cut? | `reqmap_release_plan` | `sync --release --json` |

**Resources.** `reqmap://requirement/<id>` is one requirement's dossier, and `reqmap://map`
the committed `_map.json`. Attach a requirement as a resource when the task is "implement
or change this requirement", so the contract is in context before any code is written.

**Writing is opt-in.** `reqmap_sync`, `reqmap_new` (deprecated) and `reqmap_release` exist only when the
user started the server with `--allow-writes`. Without them, run `sync` in the terminal as
before; never ask the user to restart the server with writes just to save a command. Some
decisions stay with a person whichever path runs them: flipping `status: confirmed`, the
reason passed as `accept_drift`, and `sync --retire`, which the server does not offer at all.

**Setup.** `init` writes `.mcp.json` (Claude Code) and `.vscode/mcp.json` (VS Code with
Copilot) when absent, pointing at the vendored `scripts/reqmap.py`, and never edits an
existing one. Claude Code asks the user once to approve the project server. Each call runs
the CLI in a fresh process and rescans the tree, so batch questions instead of calling a
tool in a tight loop.
