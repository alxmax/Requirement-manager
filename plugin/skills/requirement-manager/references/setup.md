# Setup details: `.reqmapignore`, re-seeding, plugin authors

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

**Create `.reqmapignore` immediately after the copy** — `reqmap.py` carries its own
`implements:` self-tags. Without this file the gate fails with dangling-ref errors
on the first run:

```
scripts/reqmap.py
scripts/reqmap_engine/**
.worktrees/**
.claude/worktrees/**
```

The two `worktrees` globs matter the first time you run an isolated subagent: each
worktree is a **full second copy of the repo**, so without them the gate counts every
member twice and reports the copies' tags as dangling refs — errors that do not exist
in your code, in files a clean CI checkout never has. (`.claude/worktrees/` is what
Claude Code creates today; `.worktrees/` is the older parallel-session location.)

Add any other vendored or generated paths that should not be scanned (one fnmatch
glob per line, `#` comments ok). The engine itself is always the first entry.

From then on every command below runs against the repo's own `scripts/reqmap.py`.
Commit the script, the package and `.reqmapignore` so the gate works in CI without
the plugin present. When the plugin ships a newer engine, re-seed with:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
rm -rf scripts/reqmap_engine && cp -r "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap_engine" scripts/reqmap_engine
cp "${CLAUDE_PLUGIN_ROOT}/scripts/_map_viewer.html" scripts/_map_viewer.html   # if you use the viewer
```

**Plugin authors** — use `sync_reqmap.sh` (in the plugin source repo) to propagate
engine changes to the cache and any registered consumer repos in one command:

```bash
./sync_reqmap.sh /path/to/consumer-repo1 /path/to/consumer-repo2
```
