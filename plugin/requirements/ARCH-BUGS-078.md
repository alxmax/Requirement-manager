---
id: ARCH-BUGS-078
status: draft
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-MAP-007, ARCH-VIEWER-007, ARCH-CONFIG-060]
satisfies: [SYS-REPORT-105]
---

# Known bugs are listed by module

## Description
> A repository's known bugs sat in documents nothing could read, so the map showed what was
> traced and said nothing about what was broken. Each repository now lists them by module,
> whether it already keeps them in files or adds them one at a time. See
> [ADR-0080](../../docs/adr/0080-known-bugs-are-listed-by-module.md).

Every bullet below is binding.
- A bug file is Markdown: a heading that names the module, and tables with an id, a title and a priority. [[REQ-BUGS-1116]]
- `requirements/bugs/*.md` and the files `BUG_SOURCES` names reach `_map.json` under `bugs`; the second kind is never written. [[REQ-BUGS-1117]]
- A malformed bug is an `INPUT:bugs` warning, and an open bug never fails the gate. [[REQ-BUGS-1118]]
- `sync --bug` adds one row to the module's file and does nothing else. [[REQ-BUGS-1119]]
- `ask --bugs` lists the known bugs by module, without a verdict. [[REQ-BUGS-1120]]
- The Problems page has a Bugs tab that groups by module and shows each bug's date. [[REQ-BUGS-1121]]
- The tab adds a bug to the repository's own file, or prints the command that does. [[REQ-BUGS-1122]]

## Cases
CASE-1 — a bug goes from the command line to the map
  Given  a repository with no bug folder
  When   `sync --bug` adds a bug and `sync` runs
  Then   `_map.json` carries that bug under `bugs`, with its module and date

CASE-2 — a repository's own files are read and left alone
  Given  a repository whose `_config.json` names a bug document with its own column names
  When   `sync` runs
  Then   `_map.json` carries that document's bugs, and the document is byte-identical

CASE-3 — a repository with no bug list sees nothing change
  Given  a repository with no bug folder and no `BUG_SOURCES`
  When   `sync` runs
  Then   `_map.json` has no `bugs` key

--------------------


---
id: REQ-BUGS-1116
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# A bug file is a heading and tables

## Description
> The format is a table a person can read and edit in any editor, so the same reader serves a
> file the engine wrote and a document that already existed.

Every bullet below is binding.
- The canonical columns are `ID`, `Bug`, `Priority`, `Date`, `Where`, `Why it matters` and `Source`, compared without regard to case.
- A table is a bug table when it has an id, a title and a priority column. Any other table in the file is skipped without a word.
- `BUG_COLUMNS` in `_config.json` adds a repository's own column names beside the canonical ones.
- The first `#` heading gives the module: the text after its last ` — `, without a trailing `(date)`. A file with no heading uses its own name.
- A row's date is `YYYY-MM-DD` or `DD.MM.YYYY`. A row with no date takes the date in the heading, and with neither it has none.
- A priority is the first `P0` to `P4` in its cell. `*` in the priority or id cell marks it estimated.
- A bug's id is `<file stem>:<row id>`, so two modules can each have a `B1`.
- A row with no id, title or priority, an unreal date, a repeated id or an unreadable file is a problem line, and the rows around it are still read.

## Cases
CASE-1 — a canonical file reads back whole
  Given  a file `# Bugs — Payments` with one row in every canonical column
  When   the file is read
  Then   the bug has module `Payments` and every field, with id `Payments:B1`

CASE-2 — a repository's own columns are read
  Given  a table headed `#`, `Issue`, `Sev`, with `BUG_COLUMNS` naming the last two
  When   the file is read
  Then   its rows are bugs, and a canonical table in another file still reads

CASE-3 — the heading gives the module and the date
  Given  a heading `# Known issues — Billing (15.03.2026)` over rows with no date column
  When   the file is read
  Then   each bug has module `Billing` and date `2026-03-15`

CASE-4 — another table is not a bug table
  Given  a file with a contents table and a bug table
  When   the file is read
  Then   only the bug table's rows are bugs, and no problem is reported

CASE-5 — a bad row does not cost the others
  Given  a table with a row with no priority, a repeated id and a date of `31.13.2026`
  When   the file is read
  Then   each gives one problem line naming its file and line, and the good rows are bugs

CASE-6 — an estimated priority is kept apart
  Given  a row whose id is `B2*` and a row whose priority is `P2 (audit), P1`
  When   the file is read
  Then   the first is `B2`, estimated, and the second is `P2`

--------------------


---
id: REQ-BUGS-1117
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# The map carries each repository's own bugs

## Description
> Each repository shows its own list. A repository that keeps none must see no change at all,
> neither a new key in its map nor a module loaded.

Every bullet below is binding.
- `bugs` reads `requirements/bugs/*.md`, then every file `BUG_SOURCES` matches, as globs from the code root, each file once.
- `_map.json` carries the bugs under `bugs` when there are any. With no folder and no `BUG_SOURCES`, `bugs.py` is not imported and the key is absent.
- The engine never writes to a file `BUG_SOURCES` names.
- A `BUG_SOURCES` pattern that matches no file is a problem line.
- A changed bug file makes the committed map stale, as a changed requirement does.

## Cases
CASE-1 — the folder reaches the map
  Given  a repository with one file in `requirements/bugs/`
  When   `sync` runs
  Then   `_map.json` carries its bugs and `gate --full` reports the map fresh

CASE-2 — no list, no key and no module
  Given  a repository with no bug folder and no `BUG_SOURCES`
  When   the map is assembled
  Then   the map has no `bugs` key and `reqmap_engine.bugs` is not imported

CASE-3 — a declared source is read and not written
  Given  `BUG_SOURCES` naming a document
  When   `sync` runs
  Then   its bugs are on the map and the document is byte-identical

CASE-4 — a pattern that matches nothing is named
  Given  `BUG_SOURCES` naming a path that does not exist
  When   the bugs are loaded
  Then   the problem lines quote that pattern

CASE-5 — a changed bug file makes the map stale
  Given  a synced repository
  When   a row is added to a bug file and `gate --full` runs
  Then   it reports the map stale

--------------------


---
id: REQ-BUGS-1118
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# The gate reads the list and does not judge it

## Description
> The gate says whether the traces hold. An open bug is work to do, not a broken link, so a
> repository with a P0 still has a verdict about its traces. A file that cannot be read back
> is a different matter, because the map would silently lose rows.

Every bullet below is binding.
- Every problem line from reading the bugs is an `INPUT:bugs` warning from `gate`, which `--strict` makes an error.
- An open bug of any priority adds no finding.
- Bugs enter neither `_reqlock.json` nor `_memberlock.json`.

## Cases
CASE-1 — a P0 does not fail the gate
  Given  a repository whose only bug is P0
  When   `gate --strict` runs
  Then   it exits 0 and prints no `INPUT:bugs`

CASE-2 — a malformed row is a warning
  Given  a bug file with a row with no priority
  When   `gate` runs
  Then   it exits 0 and prints `INPUT:bugs` with the file and line

CASE-3 — `--strict` promotes it
  Given  the same file
  When   `gate --strict` runs
  Then   it exits 1

CASE-4 — bugs stay out of the locks
  Given  a synced repository
  When   a bug is added and `sync` runs
  Then   `_reqlock.json` is byte-identical

--------------------


---
id: REQ-BUGS-1119
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# `sync --bug` adds one row

## Description
> Adding a bug is a write, and `sync` is where writes live. Like `--release` and `--audit-plan`
> it runs instead of syncing, so one call changes one file.

Every bullet below is binding.
- `sync --bug TITLE --module M` appends a row to `requirements/bugs/<M>.md`, creating the folder and the file with its heading, and prints the id and the file.
- The file name is the module's words joined by `-`, so it cannot leave the folder. A module with no word is refused.
- The id is the next `B<n>` in that file, one past the highest there.
- `--prio` defaults to `P2`, `--date` to today, and `--where`, `--why` and `--source` fill their columns.
- `--prio P2*` writes the `*`, so a priority an assistant chose reads back as an estimate until a person edits the row.
- A `|` in a value is escaped and a line break becomes a space, so the row stays one row.
- With no title, no module, a priority outside `P0` to `P4` or a date that is not real, it prints the reason, exits 2 and writes nothing.
- `moduleFile` and `appendBug` in `app/src/lib/bugFile.js` produce the same bytes, pinned by one fixture.

## Cases
CASE-1 — the first bug creates the file
  Given  a repository with no bug folder
  When   `sync --bug "Refund is applied twice" --module "Payments API" --prio P1` runs
  Then   `requirements/bugs/Payments-API.md` holds its heading and a row with id `B1`

CASE-2 — the next bug takes the next id
  Given  a file holding `B1` and `B7`
  When   `sync --bug` adds to that module
  Then   the new row is the last of the table, with id `B8`, and no other line changes

CASE-3 — a value cannot break the row
  Given  a why of `a|b` over two lines
  When   the bug is added
  Then   it reads back with that text on one line and the row has seven cells

CASE-4 — bad input writes nothing
  Given  a call with priority `P9`, a call with date `2026-13-40` and a call with module `///`
  When   each runs
  Then   each exits 2 and no file exists

CASE-5 — a module cannot leave the folder
  Given  a module named `../../etc`
  When   `sync --bug` runs
  Then   the file is `etc.md` inside `requirements/bugs/`

CASE-6 — the engine and the viewer write the same bytes
  Given  the shared fixture of a text and a bug
  When   `append_bug` and `appendBug` each run
  Then   each returns the fixture's expected text

CASE-7 — an estimate stays an estimate
  Given  a bug added with `--prio P2*`
  When   it is read back
  Then   its priority is `P2` and it is marked estimated

--------------------


---
id: REQ-BUGS-1120
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# `ask --bugs` lists them by module

## Description
> The same list the page shows, for a terminal or an assistant, read-only like every `ask`.

Every bullet below is binding.
- `ask --bugs` prints each module with its count, then its bugs with priority, id, date and title, highest priority first.
- `--module TEXT` keeps modules whose name contains the text, ignoring case, and `--prio P1` keeps that priority.
- `--json` prints `{bugs, problems}`.
- It writes nothing and exits 0, with or without bugs.

## Cases
CASE-1 — bugs print by module
  Given  two modules with a P2 and a P1 in one of them
  When   `ask --bugs` runs
  Then   each module prints once, the P1 above the P2, and it exits 0

CASE-2 — the filters narrow the list
  Given  the same repository
  When   `ask --bugs --module pay --prio P1` runs
  Then   only that bug prints

CASE-3 — JSON carries the problems
  Given  a file with one good row and one bad row
  When   `ask --bugs --json` runs
  Then   the document holds one bug and one problem

CASE-4 — no bugs is an answer
  Given  a repository with no bug list
  When   `ask --bugs` runs
  Then   it prints that there are none and exits 0

--------------------


---
id: REQ-BUGS-1121
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# The Bugs tab groups by module

## Description
> A list of hundreds is read by component. Module is the only grouping, and a bug's date sits
> under its priority so it can be read without opening the row.

Every bullet below is binding.
- Problems has a tab labelled `Bugs` in English and `Buguri` in Romanian, always present, with the number of known bugs.
- Bugs group by module, in collapsible groups showing the group's total and its count per priority. There is no other grouping.
- A row shows its priority, its date under the priority, its id and its title.
- Opening a row shows why it matters, where, the source and the file.
- Priority chips and a text search narrow the list, and a narrowed list opens its groups.
- Every label goes through `t()`.

## Cases
CASE-1 — the tab counts the bugs
  Given  a map with three bugs
  When   Problems renders
  Then   the tab reads `Bugs` with 3

CASE-2 — bugs group by module with the date on the row
  Given  bugs in two modules, one dated 2026-03-15
  When   the panel renders
  Then   each module is one group, and `15.03.2026` follows that bug's priority

CASE-3 — the label follows the language
  Given  the same map in Romanian
  When   Problems renders
  Then   the tab reads `Buguri` and the search placeholder is Romanian

CASE-4 — a repository with no bugs still has the tab
  Given  a map with no `bugs` key
  When   the panel renders
  Then   the tab reads 0 and the panel offers `Add bug`

--------------------


---
id: REQ-BUGS-1122
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# The tab adds a bug to the repository

## Description
> A static page reaches the disk only through a folder the reader picks. Where a browser
> cannot do that, the form still gives the reader the command, so no input is lost.

Every bullet below is binding.
- The form asks for what is broken, the module, the priority, the date (today by default), where, and why it matters. The first two are required.
- The module field suggests every module with a bug and every non-deprecated architecture requirement's title, and accepts free text.
- With the File System Access API, saving asks once per page for the requirements folder, refuses a folder with no `_map.json`, and writes through `appendBug` over the file as it is on disk at that moment.
- A saved bug shows at once, marked as waiting for `sync`, and the tab's count includes it.
- Without that API, saving prints the `sync --bug` command with its values quoted, and writes nothing.
- Cancelling the folder picker keeps the form as it was.

## Cases
CASE-1 — a saved row keeps what the file already holds
  Given  a folder handle whose module file changed after the map was built
  When   `saveBug` runs
  Then   the file holds the newer rows and the new one, with the next id

CASE-2 — the wrong folder is refused
  Given  a picked folder with no `_map.json`
  When   `saveBug` runs
  Then   it throws the message naming the folder, and no file is written

CASE-3 — no API, a command
  Given  a bug with a quote in its title
  When   `bugCommand` runs
  Then   the command is `sync --bug` with the quote escaped and each value flagged

CASE-4 — a new repository has suggestions
  Given  no bugs and one architecture requirement
  When   `moduleChoices` runs
  Then   it returns that requirement's title

CASE-5 — the form renders its fields
  Given  the form open
  When   it renders
  Then   it has six fields, and the module field names its suggestions
