# requirement-manager — directory edition

The plugin as submitted to the Claude plugin directory: the two skills as Markdown,
the manifest and the icon, and nothing that runs. The directory accepts local MCP
servers, scripts and hooks only from Verified organizations, so this edition ships
none of them.

- With a repository that already vendors the engine (`scripts/reqmap.py` and
  `scripts/reqmap_engine/`), the skill runs that local copy.
- Without one, the skill applies the same conventions by hand
  (`skills/requirement-manager/references/manual-mode.md`) and says what it cannot do.

The full plugin (engine, MCP server, pre-commit hook, offline map viewer) lives in
[`plugin/`](https://github.com/alxmax/requirement-manager/tree/main/plugin) and installs from GitHub:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

## Keeping it in step

These files are hand-maintained copies. `references/workflow.md`, `assistant-steps.md`,
`triage.md`, `prose-buckets.md`, `bugs.md` and `ci.md` come from
`plugin/skills/requirement-manager/references/`; `workflow.md` differs only in its
opening note, the `update-engine` row and its ADR links. When the originals change,
copy them again. The version in `.claude-plugin/plugin.json` follows `plugin/`'s.
Only Markdown, JSON and images may live here: anything else gets the submission refused.
