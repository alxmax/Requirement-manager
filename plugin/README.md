# requirement-manager — directory edition

The plugin as submitted to the Claude plugin directory: the two skills as Markdown,
the manifest and the icon, and nothing that runs. The directory accepts local MCP
servers, scripts and hooks only from Verified organizations, so this edition ships
none of them.

- With a repository that already vendors the engine (`scripts/reqmap.py` and
  `scripts/reqmap_engine/`), the skill runs that local copy.
- Without one, the skill applies the same conventions by hand
  (`skills/requirement-manager/references/manual-mode.md`) and says what it cannot do.

Install this edition:

```
/plugin install requirement-manager --marketplace alxmax/Requirement-manager
```

This edition is the marketplace's `requirement-manager` entry. The full plugin (engine,
MCP server, pre-commit hook, offline map viewer) lives in
[`plugin-full/`](https://github.com/alxmax/requirement-manager/tree/main/plugin-full) and installs
from the same marketplace as `requirement-manager-full`:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager-full@requirement-manager
```

## Keeping it in step

These files are hand-maintained copies. `references/workflow.md`, `assistant-steps.md`,
`triage.md`, `prose-buckets.md`, `bugs.md` and `ci.md` come from
`plugin-full/skills/requirement-manager/references/`; `workflow.md` differs only in its
opening note, the `update-engine` row and its ADR links. When the originals change,
copy them again. The version in `.claude-plugin/plugin.json` follows `plugin-full/`'s, and
`scripts/check_versions.py` fails the build when it does not.
Only Markdown, JSON and images may live here: anything else gets the submission refused,
and `scripts/check_directory_edition.py` fails CI first.
