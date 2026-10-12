# requirement-manager

A written contract for every feature of your project, and a small Python script that
checks your code still honours it. Each requirement is one Markdown file; your code links
back to it with a one-line comment (`# implements: AUTH-LOGIN-001`). When the contract or
the code moves without the other, the gate says so, and a map shows how the requirements
connect. It keeps an AI agent, or two of them, from re-deciding what you already settled.

This plugin ships two skills and the engine they drive:

- **`requirement-manager`**: set up, draft, sync, confirm, update-engine and triage
  requirements, and run the drift gate before a commit.
- **`requirement-quality-review`**: an advisory review of whether each requirement is
  testable and says why. It never gates anything and its suggestions are never applied
  automatically.

## Install

Claude Code:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

Other assistants through [APM](https://github.com/microsoft/apm):
`apm install alxmax/requirement-manager/plugin`. The skill carries a copy of the engine, so
the install is self-contained. Any assistant that can run a shell command can also drive the
engine directly; see the [integrations guide](https://github.com/alxmax/Requirement-manager/blob/main/docs/integrations.md).

Needs Python 3.9 or newer and `git`. The engine uses only the Python standard library.

## What it runs, reads, writes and sends

**Runs.** `python scripts/reqmap.py <verb>` in your repository, and `git` for read-only
queries (`ls-files`, `log`, `diff`, `status`, `rev-parse`, `show`, `tag -l`,
`config --get remote.origin.url`). It never commits, tags, pushes or changes git
configuration. It does not call a language model.

**Sends.** Nothing. The engine opens no network connection and has no telemetry. Your
requirements and code stay on your machine.

**Reads.** The files under the repository root, minus what `.reqmapignore` excludes.

**Writes.**

- On first use the skill copies `reqmap.py`, `reqmap_engine/` and `_map_viewer.html` into
  the repository's `scripts/` directory.
- `init` creates `requirements/` and `.reqmapignore` and adds `requirements/_map.html` to
  `.gitignore`. Without `--minimal` it also writes `ROADMAP.md`,
  `requirements/_planning.json`, `CHANGELOG.md`, `docs/architecture.html`, the MCP client
  configs `.mcp.json` and `.vscode/mcp.json`, and on a GitHub repository
  `.github/workflows/reqmap-release.yml`. It never overwrites a file that exists.
- `sync` rewrites the files it derives: the drift lock, `requirements/_map.md`,
  `requirements/_map.json` and `requirements/_findings.md`. `sync --release` writes only
  with `--apply`, and tagging is left to CI.
- `gate` and `ask` write nothing.
- No git hook is installed for you. `hooks/pre-commit` is a file to copy yourself.

A requirement becomes `confirmed` only when a person edits its status. The engine and the
skills draft; they do not confirm.

## Licence

MIT. Source, design records and the requirement corpus the engine describes itself with:
<https://github.com/alxmax/Requirement-manager>.
