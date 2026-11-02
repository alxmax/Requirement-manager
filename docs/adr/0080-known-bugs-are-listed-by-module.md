# ADR-0080 — Known bugs are listed by module

- **Status:** Accepted. Extends [ADR-0077](0077-a-repository-describes-its-own-trace-tags.md),
  which let a repository describe its own conventions in `_config.json`. Holds to
  [ADR-0040](0040-a-release-is-cut-from-the-plan.md) and
  [ADR-0076](0076-an-audit-is-a-recorded-session.md): a mode of `sync`, not a new verb.
- **Decided:** 2026-11-02
- **Evidence:** a consumer keeps its known bugs in one Markdown document per module: a
  heading naming the module and the date, then tables of id, title, priority, location,
  impact and source, next to tables of open questions. A throwaway viewer over that shape,
  with a tab beside Health and Design, settled two things: module as the only grouping, and
  the date on the row.

## Context

The map shows what is traced. A repository's known bugs lived in documents nothing read, so
the page that answers "what is wrong here" left out the longest list a team has. Two kinds
of repository need it: one that already keeps a list in its own format, and a new one that
starts empty and adds bugs as they are found. `_map.html` has been read-only until now.

## Decision

- **One Markdown file per module.** `requirements/bugs/<module>.md`, a heading and a table.
  A person can read, edit and review it in a diff, and the module is the file, so listing
  by module needs no field to keep consistent. JSON was rejected for that reason.
- **A repository's own files are read and never written.** `BUG_SOURCES` names them,
  `BUG_COLUMNS` names their columns. The default format is the same shape with English
  names, so one reader serves both. Scanning a repository for the word "bug" or for
  `FIXME` was rejected: it would fill the list with candidates nobody chose.
- **`sync --bug` adds a row and `ask --bugs` lists them.** `sync` owns writes and `ask` owns
  read-only questions, so the shape of a command still says whether it can change a file. A
  seventh verb was considered and rejected: the six verbs are in `REQ-SURFACE-1095`, and
  every earlier mode of this kind stayed a flag.
- **The gate reads the list and does not judge it.** A row that cannot be read is
  `INPUT:bugs`, a warning `--strict` promotes, because the map would otherwise lose it in
  silence. An open bug of any priority adds no finding: the gate says whether the traces
  hold, and a P0 does not make a trace false. Bugs enter no lock, so they never report drift.
- **The viewer writes to disk, in the one way a static page can.** With the File System
  Access API the reader picks the requirements folder, once per page, and the row goes
  through a port of the engine's `append_bug`, over the file as it is on disk at that
  moment. A folder with no `_map.json` is refused. A browser without the API gets the
  `sync --bug` command instead. This is the first write from the page.
- **Module is the only grouping.** The filters are priority and text.
- **An assistant is the usual author, and a person sets the worth.** It can read the code a
  report is about, so the skill's `references/bugs.md` tells it to check the list and the
  code first. `*` after a priority marks an estimate, and only a person removes it, as only a
  person confirms a requirement.

## Consequences

- A repository with no bug folder and no `BUG_SOURCES` sees no change: `bugs.py` is not
  imported and its map has no `bugs` key. The tab is still there, so a new repository has
  somewhere to add its first bug.
- A changed bug file makes the committed map stale, so a declared document turns
  `gate --full` red until `sync` runs. That is the price of a map that never shows an old
  list.
- `append_bug` exists twice, in Python and in JavaScript, pinned to one fixture, as search is.
- A bug has no status. A fixed bug is removed from its file, and git holds the history.
- `CORE_LOGICAL_BUDGET` rises for the flags, the dispatch and the two map lines. `bugs.py`
  stays lazy.

## Revisit when

- A repository wants to close a bug without deleting it, which would argue for a `Status`
  column and a filter.
- Two people lose rows to each other from the page: then a save needs a check, not a re-read.
- A second consumer declares `BUG_SOURCES` and its documents need more than column names,
  which would argue for dropping the table reader in favour of `REQUIREMENT_SOURCES`' regexes.
