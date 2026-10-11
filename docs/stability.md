# What stays still

From `v8.20.0` the command line is six verbs: `init`, `gate`, `sync`, `clarify`, `ask`,
`mcp`. A test reads the registry and fails if that set changes
(`REQ-SURFACE-1095`). Removing or renaming a verb, or a flag a verb already owns, is a
major version. Adding a flag to a verb that exists is a minor version. An existing
invocation keeps working across 8.x.

The MCP tools `reqmap_gate` through `reqmap_release` are the same set they were on
2026-09-21, minus `reqmap_design`. `init --watch` and `init --propose` are command-line
flags, not tools on that server. Removing or renaming one of the thirteen is a change
to `REQ-MCPTOOLS-1028` first.

## Two ways to install

Copy `plugin/scripts/reqmap.py` and `plugin/scripts/reqmap_engine/` into the consumer
repository, under `scripts/`. That is the offline install: stdlib only, no package
index, and it is what the CI action runs.

From a checkout of this repository, `pip install .` installs the same engine as the
`reqmap` command. It is not published to a package index by this version. The offline
viewer template (`_map_viewer.html`) ships with the copy; without it, `sync` still
writes `_map.md` and `_map.json`.

## What the first day looks like

`init --watch <ref>` prints draft suggestions for code files changed since that ref and
lists the commit subjects in between. The ref is resolved to a commit before git sees
it, so a value that is not a commit cannot become a git option. A path listed in
`.reqmapignore` is not a suggestion. It writes nothing and exits 0, including when the
ref cannot be read, so a CI job can run it without failing the build. `init --propose`
prints one draft from a sentence. Set `status: confirmed` only after a person has read
the file. The assistant does not confirm it.
