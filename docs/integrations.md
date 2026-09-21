# Integrations — AI assistants, and CI

[← back to the README](../README.md)


### Plain CLI (any tool, or no tool)

Copy `reqmap.py` from `plugin/scripts/` into your repo's `scripts/` directory and
run it directly. No AI assistant needed:

```bash
# one-time copy
cp /path/to/plugin/scripts/reqmap.py scripts/reqmap.py

# then from your repo root:
python scripts/reqmap.py init
python scripts/reqmap.py gate
python scripts/reqmap.py sync
```

### Claude Code plugin (most integrated)

Install from the plugin marketplace — Claude Code will auto-trigger the skills,
surface commands via the menu, and update the engine when a new version ships:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

On first use in any repo the skill copies `scripts/reqmap.py` into that repo and
runs `init`. The requirement template is built into the script — nothing else to
download.

### MCP server (Claude Code, VS Code with Copilot, any MCP client)

`reqmap.py mcp` serves the engine over the Model Context Protocol on stdio. The assistant
sees fourteen tools named for what they answer — `reqmap_gate`, `reqmap_next`,
`reqmap_show(id)`, `reqmap_search(query)`, `reqmap_audit`, … — each one `reqmap.py`
invocation in a fresh process, so the answer is exactly what the CLI prints, as JSON wherever
the command has `--json`. It is **read-only by default**; `reqmap_sync` and `reqmap_release`
appear only when the server starts with `--allow-writes`. The committed map
and every requirement are also resources (`reqmap://map`, `reqmap://requirement/<id>`), so a
client can attach a requirement to the conversation instead of calling a tool about it.

`init` writes the client configs when they are absent, and never edits one that exists:
`.mcp.json` for Claude Code and `.vscode/mcp.json` for VS Code. By hand:

```json
{"mcpServers": {"reqmap": {"type": "stdio", "command": "python",
  "args": ["${CLAUDE_PROJECT_DIR:-.}/scripts/reqmap.py", "mcp",
           "--root", "${CLAUDE_PROJECT_DIR:-.}"]}}}
```

The skill tells an assistant when to prefer these tools over the terminal, and which
decisions stay a person's whichever path runs them (confirming, the drift reason, retiring).
Why a server when the CLI already works, and why it is not declared by the plugin:
[ADR-0043](adr/0043-the-engine-is-served-over-mcp.md).

### GitHub Copilot, Gemini CLI, and others

The engine is a plain Python CLI with no AI SDK dependency. Any assistant that
can run shell commands can drive the full workflow. The plugin ships two
interoperability artifacts:

**`plugin/tool_definition.json`** — every `reqmap.py` command in
[OpenAI function-calling schema](https://platform.openai.com/docs/guides/function-calling).
Load this file so your assistant can discover all available commands, their
parameters, and their descriptions without reading source code.

**`SKILL.universal.md` files** — AI-agnostic variants of each skill's instruction
file, with all Claude Code-specific directives removed (`Skill` tool invocations,
`${CLAUDE_PLUGIN_ROOT}` paths). Drop any of these as a plain system prompt or
`AGENTS.md` / `GEMINI.md` instruction:

| File | Skill |
|---|---|
| `plugin/skills/requirement-manager/SKILL.universal.md` | Core SSOT + drift workflow |
| `plugin/skills/requirement-quality-review/SKILL.universal.md` | Advisory quality review |

**Verify AI-agnostic compatibility:**

```bash
python scripts/test_cross_tool.py
```

Stdlib-only headless test: seeds `reqmap.py` in a tempdir, runs `sync → gate → map`,
and asserts a valid `_map.json` is produced. If this passes, the engine works under
any assistant — or with no assistant at all.


Fail the build on drift, on every push and pull request:

```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v8
```

The action runs `reqmap.py gate`, which since `v4.0.0` *is* the lint and the map
freshness check as well — both default-on, both switchable off with
`freshness: 'false'` / `lint: 'false'` (the action passes `--no-map-check` /
`--no-lint`).
It also warns when the `reqmap.py` you vendored is older than the engine the pinned
`check@vN` ships, so a copy that quietly stopped running half the checks says so on the
run instead of staying green in silence (`stale-engine: 'error'` to fail the build on it,
`'off'` to silence it). Inputs `reqmap-path` and `working-directory` adapt it to wherever
you vendored the engine — see [`check/action.yml`](../check/action.yml). Or skip the action
entirely: `- run: python -X utf8 scripts/reqmap.py gate`.

`@v2` is a major-alias tag: it is force-moved onto every released commit, so it always
resolves to the latest release on that interface line. Pin an exact `vX.Y.Z` tag or a
commit SHA instead if you want a frozen ref. `@v1` still works and still runs the
gate-only step list it always did, but it no longer moves — it needs an engine seeded
from plugin v2.0.0+, and `@v2` needs v2.3.4+ (the release that added `lint_exempt:`).


The `excalidraw-diagram` skill used to ship alongside this plugin. It now lives in
[its own repository](https://github.com/alxmax/excalidraw-diagram) and installs on its own:

```
/plugin marketplace add alxmax/excalidraw-diagram
/plugin install excalidraw-diagram
```

It shared this repository and nothing else — no imports in either direction — so a change
to either one took the other's CI with it, and anyone who wanted diagrams had to install a
requirements engine to get them.
