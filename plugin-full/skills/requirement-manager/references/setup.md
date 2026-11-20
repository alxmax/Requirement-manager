# Setup details: `.reqmapignore`, re-seeding, plugin authors

Set `REQMAP_PLUGIN_ROOT` to the installed plugin directory as described in the entry point.

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

**Local files you never commit.** A tagged file git does not track (a local notes
folder, a scratch script) is still scanned, so the local map records a member a CI
checkout never has and the hook reports `map is stale`. The gate names it in the same
run (`RM022 … not tracked by git`). Exclude the folder once in `.reqmapignore`
(e.g. `notes/local/**`) rather than stashing it before each commit. An untagged
untracked file changes nothing.

**What to commit.** Commit `_map.json`, `_map.md`, `_findings.md` and the lock files:
the gate compares them with a fresh build. Never commit `_map.html`: it is rebuilt from
`_map.json` on every sync, so `init` adds it to `.gitignore`, and `sync` tells you how
to stop tracking a copy that is already committed.

**A merge conflict on generated files.** Two branches that both ran `sync` conflict on
`_map.json`, `_map.md`, `_findings.md` or the locks. Do not merge the hunks by hand:
take either side, run `sync`, commit the result, and `gate` confirms the map is fresh.

```bash
git checkout --theirs requirements/_map.json requirements/_map.md   # either side
python scripts/reqmap.py sync && git add requirements/
```

From then on every command below runs against the repo's own `scripts/reqmap.py`.
Commit the script, the package and `.reqmapignore` so the gate works in CI without
the plugin present. When the plugin ships a newer engine, re-seed with:

```bash
cp "${REQMAP_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
rm -rf scripts/reqmap_engine && cp -r "${REQMAP_PLUGIN_ROOT}/scripts/reqmap_engine" scripts/reqmap_engine
cp "${REQMAP_PLUGIN_ROOT}/scripts/_map_viewer.html" scripts/_map_viewer.html   # if you use the viewer
```

**Plugin authors** — use `sync_reqmap.sh` (in the plugin source repo) to propagate
engine changes to the cache and any registered consumer repos in one command:

```bash
./sync_reqmap.sh /path/to/consumer-repo1 /path/to/consumer-repo2
```
