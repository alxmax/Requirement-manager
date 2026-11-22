# ADR-0096 — `.mcp.json` uses relative paths, with no client variable

- **Status:** Accepted. Changes how `init` writes `.mcp.json` (REQ-MCPSEED-1029, under
  [ADR-0043](0043-the-engine-is-served-over-mcp.md)); `.vscode/mcp.json` is unchanged.
- **Decided:** 2026-11-22
- **Evidence:** `.mcp.json` wrote every path under `${CLAUDE_PROJECT_DIR:-.}`, Claude Code's
  shell-style expansion. `docs/integrations.md` records that Copilot CLI and VS Code's Copilot
  (since 1.143) read the same file, and VS Code spells an environment variable `${env:NAME}`;
  nothing showed that either expands the `:-` default form. A client that does not would start a
  server at the literal path `${CLAUDE_PROJECT_DIR:-.}/scripts/reqmap.py`, which fails, or list a
  second `reqmap` beside the working one from `.vscode/mcp.json`.

## Decision

- **`.mcp.json` writes paths relative to the repository root** (`./scripts/reqmap.py`,
  `--root .`, `--reqs ./requirements`, `--code .`) and no variable at all, so every client that
  reads it gets the same command.
- **The server already resolves its own paths**: `_workspace_flags` turns a relative `--root`,
  `--reqs` and `--code` absolute against `CLAUDE_PROJECT_DIR` when a client sets it, else against
  the directory it starts in. Only the script path depends on that directory.
- **`.vscode/mcp.json` keeps `${workspaceFolder}`**: it is VS Code's file alone, and that variable
  is VS Code's own.

## Consequences

- The server must start in the repository root. Claude Code starts a project server there, and
  Copilot CLI starts where it is run; a test starts the seeded entry in the repository root with no
  `CLAUDE_PROJECT_DIR` and gets its tools.
- An existing `.mcp.json` is never edited (REQ-MCPSEED-1029), so a consumer seeded before this
  keeps the variable until it rewrites the file or re-runs `init` without one.

## Revisit when

- A client is seen starting a project stdio server outside the repository root: then the script
  path needs that client's own variable, in a file only that client reads.
