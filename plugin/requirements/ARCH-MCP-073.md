---
id: ARCH-MCP-073
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v7.21.12
depends_on: [ARCH-CMDREGISTRY-033, ARCH-INIT-012]
satisfies: [SYS-SHIP-108]
---

# Serving the engine over MCP

## Description
> An assistant with a shell can already run `reqmap.py`, and one choosing between sixteen
> `gate` flags from prose, or asking its user to approve every terminal command, gets less of
> the engine than one that lists `reqmap_show(id)` as a read-only tool. `reqmap.py mcp` serves
> the same commands over the Model Context Protocol, one fresh process per call, read-only
> unless the user starts it otherwise (ADR-0043).

Every bullet below is binding.
- `reqmap.py mcp` answers MCP over stdio, newline-delimited JSON-RPC at one pinned protocol revision, and writes nothing but protocol messages to stdout. [[REQ-MCPPROTOCOL-1027]]
- Each tool is one `reqmap.py` invocation in a fresh process, named for the question it answers, and only `--allow-writes` offers a tool that writes. [[REQ-MCPTOOLS-1028]]
- `init` writes the Claude Code and VS Code client configs that start the server, and never edits one that exists. [[REQ-MCPSEED-1029]]
- The committed map and every requirement in it are readable as MCP resources. [[REQ-MCPRESOURCES-1030]]

## Cases
CASE-1
  Given  a repository with one requirement
  When   `reqmap.py mcp` is started as a process and sent initialize, tools/list and a
         `reqmap_gate` call over stdin
  Then   it answers all three on stdout, lists no writing tool, and the call returns the
         gate's verdict

## Context
**Notes**
- The decision, and the Senate deferral it supersedes, are ADR-0043.


--------------------


---
id: REQ-MCPPROTOCOL-1027
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MCP-073]
---

# The protocol, over stdio

## Description
> A client reads the server's stdout as a stream of messages, so one stray print breaks the
> session; and no client promises which directory the server starts in.

Every bullet below is binding.
- `initialize` answers with protocol revision `2025-06-18`, the `tools` capability and the
  server's name and engine version.
- A notification gets no reply; `ping` gets an empty result.
- An unknown method is error -32601, a line that is not JSON is error -32700, and a request
  with no `method` is error -32600.
- Only protocol messages are written to stdout, one JSON object per line.
- The server's `--root`, `--reqs` and `--code` are passed to every call as absolute paths, a
  relative one resolved against `CLAUDE_PROJECT_DIR` when the client sets it.

## Cases
CASE-1 — initialize names the pinned revision
  Given  a server
  When   it receives `initialize`
  Then   the result carries `2025-06-18`, a `tools` capability and `serverInfo.name` `reqmap`

CASE-2 — a notification is not answered, a ping is
  Given  a server
  When   it receives `notifications/initialized` and then `ping`
  Then   exactly one line comes back, an empty result for the ping

CASE-3 — malformed input is a protocol error, never a crash
  Given  a server
  When   it receives an unknown method, a line of text that is not JSON, and an object with no method
  Then   it answers -32601, -32700 and -32600 in order and keeps reading

CASE-4 — relative paths resolve against the project directory
  Given  `--reqs plugin/requirements` and `CLAUDE_PROJECT_DIR` set to a project path
  When   the workspace flags are built
  Then   `--reqs` is that project path joined with `plugin/requirements`


--------------------


---
id: REQ-MCPTOOLS-1028
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MCP-073]
---

# Tools named for questions, run as the CLI

## Description
> `gate` alone has sixteen flags, most of them separate modes; an agent picks a named tool
> far more reliably than a flag combination. Running each call as the CLI keeps the CLI the
> only code path and starts every call from clean module state.

Every bullet below is binding.
- Every verb and flag a tool invokes is one the command registry declares.
- `tools/list` offers a writing tool only when the server runs with `--allow-writes`, and a
  call to one without it is error -32602.
- Each argument becomes its own argument to `reqmap.py`, never text for a shell; an unknown,
  missing required or wrongly typed argument is error -32602.
- `reqmap_show`, `reqmap_search` and `reqmap_dupes` run their command with `--json`.
- A call's result carries the command's output as text and, when the exit code is not zero,
  a second item naming it. `isError` is set only for an exit code the tool does not count as
  an answer: `reqmap_gate`'s exit 1 is a FAIL verdict, not an error.

## Cases
CASE-1 — the tools name only what the CLI has
  Given  the tool table and the command registry
  When   every tool's verb and flags are compared with the registry
  Then   each verb is registered and each flag is one of that verb's flags

CASE-2 — writing tools need --allow-writes
  Given  a server started without `--allow-writes`, and one started with it
  When   each lists its tools and calls `reqmap_sync`
  Then   the first lists none of `reqmap_sync`, `reqmap_new`, `reqmap_release` and refuses the call with -32602; the second lists all three

CASE-3 — arguments are checked and passed one by one
  Given  `reqmap_search` called with no query, with `top` as text, and with `query` `a b` and `top` 3
  When   each call is made
  Then   the first two are -32602, and the third runs `gate --search "a b" --top 3` as separate arguments

CASE-4 — a FAIL verdict is an answer, a failed command is an error
  Given  `reqmap_gate` and `reqmap_show` both exiting 1
  When   each is called
  Then   the gate result has `isError` false and the show result has it true, both naming exit code 1

CASE-5 — a release plan passes --release with or without a version
  Given  `reqmap_release_plan` called with no version and with `v1.2.0`
  When   the arguments are built
  Then   they are `sync --json --release` and `sync --json --release v1.2.0`


--------------------


---
id: REQ-MCPSEED-1029
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MCP-073]
---

# init writes the client configs that start the server

## Description
> A server nobody configured is a server nobody runs. Each client reads its own file and
> expands its own variable for the project root, and neither guarantees the directory the
> server starts in, so the paths are written against that variable.

Every bullet below is binding.
- `init` writes `.mcp.json` with `mcpServers.reqmap` and `.vscode/mcp.json` with
  `servers.reqmap`, each a stdio entry running the vendored `reqmap.py mcp` with the
  repository's `--reqs` and `--code`.
- The Claude Code entry writes its paths under `${CLAUDE_PROJECT_DIR:-.}`, the VS Code entry
  under `${workspaceFolder}`.
- An existing config is never edited; one with no `reqmap` server gets a note saying to add it.
- When the engine is not inside the repository, no config is written and a note says why.

## Cases
CASE-1 — both configs start the vendored engine
  Given  a repository vendoring the engine, with its requirements under `requirements/`
  When   the configs are seeded
  Then   `.mcp.json` and `.vscode/mcp.json` each run `reqmap.py mcp` under their client's project variable, with `--reqs` ending in `requirements`

CASE-2 — an existing config is left alone
  Given  a `.vscode/mcp.json` declaring only another server
  When   the configs are seeded
  Then   that file is byte-identical, `.mcp.json` is written, and a note names `.vscode/mcp.json`

CASE-3 — an engine outside the repository writes nothing
  Given  a repository that does not contain the engine
  When   the configs are seeded
  Then   no file is written and a note says the engine is not inside the repository


--------------------


---
id: REQ-MCPRESOURCES-1030
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MCP-073]
---

# The map and each requirement, as resources

## Description
> A tool is something an agent decides to call; a resource is something a person or a client
> attaches as context. A requirement is the second kind as often as the first: "work on
> this, per REQ-X" wants the requirement in the conversation, not a tool call about it.

Every bullet below is binding.
- `resources/list` offers `reqmap://map`, the committed `_map.json`, and one
  `reqmap://requirement/<id>` per requirement the map names, read from the map file without
  running the engine; with no map it offers nothing.
- `resources/templates/list` offers `reqmap://requirement/{id}`.
- Reading `reqmap://requirement/<id>` returns what `reqmap_show` returns for that id; an id
  with no requirement, or a missing map, is error -32002, and a URI the server does not serve
  is error -32602.

## Cases
CASE-1 — the list comes from the committed map
  Given  a `_map.json` naming two requirements, and separately no map
  When   `resources/list` is asked
  Then   the first lists `reqmap://map` and both requirements; the second lists nothing

CASE-2 — a requirement reads as its dossier
  Given  a server whose `gate --json --show` answers for `REQ-A-001` and fails for `NOPE-1`
  When   `resources/read` asks for each
  Then   the first returns that JSON with its URI, the second is error -32002

CASE-3 — the map reads as the file, the template is offered, other URIs are refused
  Given  a committed `_map.json`
  When   `reqmap://map`, `file:///x` and the template list are asked for
  Then   the first returns the file's text, the second is error -32602, and the template is `reqmap://requirement/{id}`
