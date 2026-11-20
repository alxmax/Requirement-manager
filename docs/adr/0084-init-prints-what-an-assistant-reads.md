# ADR-0084 — `init` prints what an assistant reads, and Copilot is tested before it is changed for

- **Status:** Accepted. Extends [ADR-0043](0043-the-engine-is-served-over-mcp.md) and
  [ADR-0068](0068-the-skill-carries-the-engine.md); changes neither.
- **Decided:** 2026-11-20
- **Evidence:** GitHub's and VS Code's Copilot documentation and changelogs as of 2026-11-20,
  summarised per surface in [docs/integrations.md](../integrations.md#github-copilot); no Copilot
  client was run against this repository.

## Context

Copilot now reads much of what this repository ships: project skills from `.claude/skills`,
`.github/skills` and `.agents/skills`, a workspace `.mcp.json` with `mcpServers` in VS Code's
Copilot harness and in Copilot CLI, and `AGENTS.md` / `CLAUDE.md` in its cloud agent and CLI.
Three things it does not do for us: its chat on github.com, in Visual Studio and in JetBrains
reads only `.github/copilot-instructions.md`; its cloud agent is not documented to run git hooks,
so the pre-commit gate does not reach it; and outside Visual Studio its MCP clients list tools,
not resources.

Two things nobody has observed: the working directory a stdio server starts in under the
Copilot harness, Copilot CLI and the cloud agent, which decides what `${CLAUDE_PROJECT_DIR:-.}`
in the `.mcp.json` `init` writes resolves to; and whether Copilot expands `${CLAUDE_PLUGIN_ROOT}`
in a `SKILL.md`, which the skill's APM fallback is meant to make irrelevant.

## Decision

- **`init` prints, it does not write.** After a run that tracks a requirement it prints four
  rules under a line naming `.github/copilot-instructions.md` and `AGENTS.md`: run `gate --full`
  before finishing, read a requirement with `gate --show` first, tag code and tests, a person
  confirms. The file belongs to the repository; a printed block can become a written one later,
  and a written one cannot be quietly taken back from every repository that ran `init`.
- **The rules name the engine the repository runs**, and read as no tag, so pasting them into
  a scanned file fails nothing.
- **Resources are named as what they are.** The skill says `reqmap://` resources are listed by
  Claude Code and Visual Studio, and that elsewhere the assistant calls `reqmap_show`.
- **The MCP config and `SKILL.md` stay as they are until a run fails.** The two unknowns above
  are tested first, per surface, from the repository root, from `$HOME` and from a sibling
  repository, on Windows and Linux. `mcpconfig.py` changes only for a failing row, and
  `SKILL.md` only in its platform-setup paragraph.
- **`tool_definition.json` stays.** No Copilot surface reads it, and that is not a reason to
  remove a file a consumer may load; retiring it is a decision of its own, superseding ADR-0008.

## Consequences

- An assistant that does not load the skill learns the gate only if a person pastes the block.
- `docs/integrations.md` carries a per-surface table, dated, with the two unobserved rows marked
  as such until the test is run.
- `init.py` grows; it is lazy, so the core does not.

## Revisit when

- The test is run: a failing row changes `mcpconfig.py` or `SKILL.md`, in a record of its own.
- A repository asks `init` to write the file: then write it only when absent.
- Copilot's MCP clients list resources.
