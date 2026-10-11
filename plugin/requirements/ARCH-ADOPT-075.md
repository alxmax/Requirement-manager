---
id: ARCH-ADOPT-075
status: draft
layer: feature
owner: Alex
---

# Adoption before the whole tree is tagged

## Description
> A team that has to tag every file before the tool says anything useful does not start.
> The first run has to be useful on the files a change already touched, and a draft is
> not a contract until a person has read it.

Every bullet below is binding.
- `init --watch REF` reports code files changed since REF that no requirement claims, and the commit subjects since REF, and it writes nothing. [[REQ-WATCH-1092]]
- `init --propose` prints one requirement draft. The MCP tools `reqmap_watch` and `reqmap_propose` do the same work and do not write. A person sets `status: confirmed`. [[REQ-PROPOSE-1093]]
- `gate` run on a copy of a repository outside this one still reports that copy's own drift. [[REQ-EXTREPO-1094]]
- The CLI stays six verbs, and a checkout can install that same engine with `pip install .`. [[REQ-SURFACE-1095]]

## Cases
CASE-1 — a draft is not a confirmed contract
  Given  `init --watch` or `init --propose`
  When   either command finishes
  Then   it has written no requirement file and it has not set `status: confirmed`

--------------------


---
id: REQ-WATCH-1092
status: draft
layer: feature
owner: Alex
---

# Watch the files a change already touched

## Description
> Tagging the whole tree is the adoption wall. The first question is which of the files
> in this change no requirement claims yet, and the answer has to be safe to run in CI.

Every bullet below is binding.
- `init --watch REF` prints JSON and writes no file. A code file changed since REF with no `implements:` tag is one suggestion, with `status` `draft` and `needs_confirmation` true.
- A changed file that already has an `implements:` tag is not a suggestion. A file whose extension is not scanned code is not a suggestion.
- A commit subject since REF is listed with `status` `draft`, except a subject of fewer than 8 characters and a subject that starts with `Merge `.
- Issue trackers are not read, and the report says `issues` is `not read`.
- A ref git cannot read exits 0 and the report's `error` says git could not read that ref.
- `gate --watch` exits 2 and names `init` as the verb that owns the flag.
- At most 40 file suggestions and 40 commit subjects are printed. `truncated` is true only when a suggestion was left out.

## Cases
CASE-1 — an untagged changed file is a draft suggestion
  Given  a commit that adds a code file with no `implements:` tag, and a `.txt` file in the same commit
  When   `init --watch` is run against the parent commit
  Then   the code file is a suggestion with `status` `draft` and `needs_confirmation` true, the `.txt` file is absent, and no requirement file was written

CASE-2 — a file that already has an implements tag is skipped
  Given  a code file changed since REF whose text contains an `implements:` tag
  When   `init --watch REF` runs
  Then   that path is not among the suggestions

CASE-3 — a subject that starts with Merge is omitted
  Given  one commit subject that starts with `Merge ` and one that does not, both since REF
  When   `init --watch REF` runs
  Then   only the second subject is listed, with `status` `draft`, and `issues` is `not read`

CASE-4 — a ref git cannot read exits 0
  Given  a git repository and a ref that does not exist
  When   `init --watch` is given that ref
  Then   the process exits 0 and the report's `error` says git could not read that ref

CASE-5 — gate does not own --watch
  Given  `--watch` passed to `gate`
  When   the command runs
  Then   it exits 2 and the message names `init`

CASE-6 — the caps say when a suggestion was left out
  Given  fewer changed code files than 40 and fewer commit subjects than 40
  When   `init --watch` runs
  Then   `truncated` is false

--------------------


---
id: REQ-PROPOSE-1093
status: draft
layer: feature
owner: Alex
---

# The agent proposes a draft and a person confirms it

## Description
> The gate checks a contract. It does not write one. An assistant that just implemented
> something new can propose the draft, and the status stays `draft` until a person reads it.

Every bullet below is binding.
- `init --propose TEXT` prints one requirement whose frontmatter `status` is `draft`, and it writes no file. The printed body tells a person to set `status: confirmed` after reading it. The frontmatter does not say confirmed.
- `--propose-files` records those paths in the draft. Without `--propose` the command exits 2.
- `--watch` and `--propose` on the same command exit 2 and write nothing.
- `reqmap_watch` and `reqmap_propose` are read-only MCP tools. Their arguments become `init --watch` and `init --propose`. They are offered when the server was started without `--allow-writes`.

## Cases
CASE-1 — propose prints a draft and writes nothing
  Given  a description and one file path
  When   `init --propose` runs with `--propose-files`
  Then   stdout contains `status: draft`, the frontmatter does not say confirmed, the body tells a person to set `status: confirmed`, the path is in the text, and no requirement file exists afterwards

CASE-2 — the two MCP tools are read-only CLI calls
  Given  the MCP tool table
  When   `reqmap_watch` and `reqmap_propose` are read, and a server without `--allow-writes` lists tools
  Then   both are read-only, both are listed, and their arguments are `init --watch` and `init --propose`

CASE-3 — watch and propose together are refused
  Given  both `--watch` and `--propose` on one `init`
  When   the command runs
  Then   it exits 2 and writes no requirement file

--------------------


---
id: REQ-EXTREPO-1094
status: draft
layer: feature
owner: Alex
---

# The gate runs on a repository that is not this one

## Description
> Dogfooding this repository does not show that the engine works on someone else's tree.
> A copy of the hello-drift example, placed outside this checkout, is the smallest such tree.

Every bullet below is binding.
- Running this engine's `gate` with its working directory set to a copy of `examples/hello-drift` reports `RM018` for `HELLO-GREET-001` and exits 0.

## Cases
CASE-1 — a copied hello-drift still shows drift
  Given  a temp directory that is a copy of `examples/hello-drift` and not this repository
  When   `gate` runs with that directory as its working directory
  Then   the output names `RM018` and `HELLO-GREET-001`, and the process exits 0

--------------------


---
id: REQ-SURFACE-1095
status: draft
layer: feature
owner: Alex
---

# The six verbs stay, and pip installs the same engine

## Description
> Adding a verb breaks every document and every caller that lists them. A new flag on a
> verb that already exists does not. The copy-two-files install stays; pip is a second way
> to put that same engine on `PATH`.

Every bullet below is binding.
- The command registry's verbs are `init`, `gate`, `sync`, `clarify`, `ask` and `mcp`.
- `pyproject.toml` names the project `reqmap`, requires Python `>=3.9`, and its console script is `reqmap_engine.watch:console_main`.
- The licence string in that file is MIT.

## Cases
CASE-1 — the verb set is the six
  Given  the command registry
  When   its keys are read
  Then   they are exactly `init`, `gate`, `sync`, `clarify`, `ask` and `mcp`

CASE-2 — the package metadata names reqmap
  Given  `pyproject.toml` at the repository root
  When   it is read
  Then   it names `reqmap`, requires Python `>=3.9`, declares MIT, and points the console script at `reqmap_engine.watch:console_main`
