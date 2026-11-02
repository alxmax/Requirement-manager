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
- The tab exports the list it shows, for a reader who does not open the map. [[REQ-BUGS-1123]]
- `sync --bug` writes in the shape of the file it lands in, and never gives a number twice. [[REQ-BUGS-1126]]
- `sync --fix` moves a row to a register with its dates, version and commit. [[REQ-BUGS-1127]]
- `sync` closes the bugs a commit's `Fixes-bug:` trailer names. [[REQ-BUGS-1128]]
- The map carries the register, and the tab shows it over time. [[REQ-BUGS-1129]]

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
- The first `#` heading gives the module: the text after its last dash with a space on each side (`—`, `–` or `-`), without a trailing `(date)`. A file with no heading uses its own name.
- A row's date is `YYYY-MM-DD` or `DD.MM.YYYY`. A row with no date takes the date in the heading, and with neither it has none.
- A priority is the first `P0` to `P4` in its cell. `*` in the priority or id cell marks it estimated.
- A bug's id is `<file stem>:<row id>`, so two modules can each have a `B1`. Renaming the file changes the id.
- `BUG_SKIP_SECTIONS` in `_config.json` is a regex on `##` headings: no table under a matching heading is read, down to the next `##`. A regex that does not compile is a problem line, and every table is then read.
- A bug records its file and the line of its row.
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

CASE-7 — a named section is not read
  Given  bug tables under `## Open` and `## Recently fixed`, the second below a `###`
  When   the bugs load with `BUG_SKIP_SECTIONS` set to `(?i)fixed`, and again with it empty
  Then   the first load holds only the open bug, and the second holds both

CASE-8 — a bad pattern loses nothing
  Given  `BUG_SKIP_SECTIONS` set to `(`
  When   the bugs load
  Then   the rows are read and one problem line names the key

CASE-9 — a spaced dash ends the module name
  Given  a heading `# Known — Stock - Orders` and a heading `# Known — Stock-Orders`
  When   each file is read
  Then   the modules are `Orders` and `Stock-Orders`

CASE-10 — a row says where it came from
  Given  a bug on line 5 of a file
  When   the file is read
  Then   the bug carries that file and line

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
- Modules that differ only in case, diacritics or punctuation are one module, under the spelling read first. A bug's id does not change.

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

CASE-6 — two spellings are one module
  Given  files headed `Café, API`, `cafe api` and `Search`
  When   the bugs are loaded
  Then   the first two carry the module `Café, API`, with their own ids

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

CASE-5 — a Unicode line break inside a cell
  Given  a title holding U+2028
  When   the file is read
  Then   the row and every row after it are read

CASE-6 — a byte order mark
  Given  a file that starts with one
  When   it is read
  Then   its heading still names the module

CASE-7 — one id in two files
  Given  two declared files with one stem
  When   they are read
  Then   `INPUT:bugs` names both

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
- `sync --bug TITLE --module M` adds a row to the module's file under `requirements/bugs/`, creating the folder and the file with its heading, and prints the id and the file.
- A new file's name is the module's words joined by `-`, so it cannot leave the folder. A module with no word is refused.
- The id is the next `B<n>`, one past the highest in that file and in the register.
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

CASE-8 — a file that cannot be read
  Given  a file in the bugs folder that is not UTF-8
  When   `sync --bug` runs
  Then   it exits 2 and writes nothing

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
- `ask --bugs` prints each module with its count, then its bugs with priority, id, date and title, highest priority first, and last a total with the count per priority.
- `--module TEXT` keeps modules whose name contains the text, ignoring case, diacritics and punctuation, and `--prio` keeps one priority or a comma-separated list.
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

CASE-5 — a list of priorities, and a total
  Given  bugs at P1, P2 and P3
  When   `ask --bugs --prio p1,P3` runs
  Then   the P2 is left out and the last line reads `2 bugs: P1 1, P3 1`

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
- Opening a row shows why it matters, where, the source and the file with its line. Selecting that text leaves the row open.
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

--------------------


---
id: REQ-BUGS-1123
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# The tab exports what it shows

## Description
> A team sends the list to people who do not open the map. The browser's own "Save as PDF"
> does that with no dependency, so the page only has to lay the list out for paper.

Every bullet below is binding.
- `Export PDF` opens the browser's print dialog on the list as filtered, with every group open, and is disabled when the list is empty.
- The page holds the repository's name, the total and the filter in force, then for each module a line with its count per priority and its bugs, highest priority first.
- Each bug shows its priority, date, id, title, why it matters, where, the source and the file with its line.
- Printing with the browser's own command, without the button, is unchanged.

## Cases
CASE-1 — the report holds every field of what is shown
  Given  a filtered list of two bugs in one module, one with why, where and source
  When   the report renders
  Then   it holds that module's count per priority and each field, with nothing left closed

CASE-2 — the report states its filter
  Given  a report narrowed to P1
  When   it renders
  Then   its header names P1 and the total shown

CASE-3 — nothing to export
  Given  an empty list
  When   the panel renders
  Then   the button is disabled

--------------------


---
id: REQ-BUGS-1126
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# `sync --bug` writes in the file's own shape

## Description
> A repository that numbers its files, or names its columns in its own language, ended up with
> a second file beside the first. A row belongs where a person would have put it.

Every bullet below is binding.
- The row goes to the file in `requirements/bugs/` whose heading or stem, without an `NN_` prefix, names the module, compared by `module_key`. The register is never that file.
- A new module's file takes the next `NN_` when the existing files are numbered.
- The row uses the columns of the table it joins, and the `BUG_COLUMNS` names count.
- The row joins the table under the `##` section naming its priority, such as `P2` or `P3-P4`, else the file's first bug table. A section `BUG_SKIP_SECTIONS` matches is never used.
- A title that reads like one already in that module prints the candidates and exits 2, writing nothing, unless `--force` is given.
- `bugFile` and `appendBug` in `app/src/lib/bugFile.js` choose the same file and write the same bytes, pinned by one fixture, and `_map.json` carries `bug_format` when a repository's format is not the default.

## Cases
CASE-1 — an existing numbered file with its own columns
  Given  `04_Billing.md` with a localized header and a table under `## P2`
  When   `sync --bug "x" --module Billing --prio P2` runs
  Then   the row is in that table, in those columns, and no `Billing.md` exists

CASE-2 — a new module in a numbered folder
  Given  `04_Billing.md`
  When   `sync --bug` names a module with no file
  Then   the file is `05_<module>.md`

CASE-3 — a section that does not match
  Given  sections for `P0-P1` and `P2`
  When   a `P4` bug is added
  Then   it joins the first table

CASE-4 — a likely duplicate
  Given  a module holding a bug with nearly the same title
  When   `sync --bug` runs without and then with `--force`
  Then   the first exits 2 and writes nothing, and the second adds the row

CASE-5 — the engine and the viewer agree
  Given  the shared fixture of texts, formats and file lists
  When   each side runs
  Then   each returns the fixture's expected text and file

--------------------


---
id: REQ-BUGS-1127
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# `sync --fix` closes one bug

## Description
> A row deleted by hand took its dates with it. The register keeps what the list no longer
> needs: when a bug was found, when it left, and in which version or commit.

Every bullet below is binding.
- `sync --fix ID` takes `FILE:REF` or `FILE REF`, removes the row and adds one to `requirements/bugs/_fixed.md`, instead of syncing.
- The register row holds the id, the title, the module, the priority, the found date, today, the version and the commit.
- The version is `--version`, else the repository's version file, else `—`. The commit is `--commit`, else the short `HEAD`, else `—`.
- `--note TEXT` closes without a fix: the version is `not a bug`, the commit `—`, and the note is kept.
- `BUG_REGISTER` names the register and `BUG_REGISTER_COLUMNS` its columns. A register that exists keeps its own columns.
- The register is not read as open bugs, whatever its columns, even when `BUG_SOURCES` matches it.
- An unknown id, a closed id, or a bug in a file only `BUG_SOURCES` names exits 2 and writes nothing.
- A row that is not on the line it was read from, or a register that cannot be read, exits 2 and writes nothing.

## Cases
CASE-1 — a fix moves the row
  Given  an open bug and a version file
  When   `sync --fix` runs
  Then   `ask --bugs` no longer lists it and the register row has every field

CASE-2 — a number is never given twice
  Given  the highest bug closed
  When   `sync --bug` adds to that file
  Then   the new row takes the next number

CASE-3 — a dismissal
  Given  an open bug
  When   `sync --fix ID --note "works as designed"` runs
  Then   the register says `not a bug` and keeps the note

CASE-4 — refused closes write nothing
  Given  an unknown id, a closed id and a bug in a declared source
  When   `sync --fix` runs on each
  Then   each exits 2 and every file is byte-identical

CASE-5 — a repository's own register
  Given  a register with localized columns and no module column
  When   a bug is closed
  Then   the row fits those columns

CASE-6 — the right row or none
  Given  a stray carriage return above the table, and a row that moved
  When   a bug is closed
  Then   the first closes the named row and the second is refused

CASE-7 — a broken register survives
  Given  a register that is not UTF-8
  When   `sync --fix` runs
  Then   it exits 2 and both files are byte-identical

CASE-8 — a glob over the folder
  Given  `BUG_SOURCES` matching the bugs folder
  When   the list is read
  Then   the register's rows are not listed

--------------------


---
id: REQ-BUGS-1128
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# A commit closes the bug it names

## Description
> The commit that fixes a bug already says so, and a second step gets forgotten. `sync` reads
> the history instead, so the register needs no lock and a team without versions loses nothing.

Every bullet below is binding.
- `sync` closes each open bug named by a `Fixes-bug: ID` trailer on the history of `HEAD`, with that commit's short SHA and date.
- `BUG_FIX_TRAILERS` names the trailers, matched without regard to case.
- The version is the repository's version file at that commit, else `—`.
- A bug in the register is left alone, so a second `sync` changes nothing.
- A trailer that names no open bug, or a bug in a `BUG_SOURCES` file, prints an `INPUT:bugs` line from `sync` and does not reach the gate.
- With no git, or no such commit, `sync` does what it did.

## Cases
CASE-1 — a commit closes a bug
  Given  an open bug and a commit whose message has `Fixes-bug: ID`
  When   `sync` runs
  Then   the register holds that commit's SHA and date

CASE-2 — a second sync changes nothing
  Given  that bug closed
  When   `sync` runs again
  Then   the bug files are byte-identical

CASE-3 — the version at that commit
  Given  a version file changed after the fix
  When   `sync` closes the bug
  Then   the register holds the version at the fix

CASE-4 — a trailer that names nothing
  Given  a trailer naming an unknown bug
  When   `sync` runs
  Then   it prints that line, exits 0, and the gate has no finding for it

CASE-5 — no git
  Given  a directory that is not a repository
  When   `sync` runs
  Then   it exits 0 and the bug file is unchanged

CASE-6 — a repository's own trailer
  Given  `BUG_FIX_TRAILERS` naming another word
  When   a commit uses it in lower case
  Then   the bug closes

--------------------


---
id: REQ-BUGS-1129
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# The map shows what was fixed

## Description
> The dates a closed bug keeps add up to a trend, with no new input from anyone.

Every bullet below is binding.
- `_map.json` carries the register under `bugs_fixed`, and has no such key when it is empty.
- A row's commit links to the forge when the remote is GitHub. The forge reaches `_map.html` only, because it differs between a clone and a fork.
- When the register holds a row, the Bugs tab has an Open / Fixed toggle. Fixed shows found, fixed, version, commit and note.
- Fixed shows, by week, the bugs found, the bugs fixed and what was still open, and the median days to fix per module and per priority.
- A `not a bug` row leaves the open count and counts in neither the fixes nor the median.
- The export gains a section of what was fixed in the last 30 days.

## Cases
CASE-1 — the register reaches the map
  Given  one closed bug
  When   `sync` runs
  Then   `_map.json` carries it under `bugs_fixed` and not under `bugs`

CASE-2 — a GitHub remote
  Given  a register row with a commit and a GitHub remote
  When   `sync` runs
  Then   the forge is named for the page and `_map.json` does not carry it

CASE-3 — the toggle
  Given  a map with a closed bug
  When   the history renders
  Then   it shows that bug's dates, version and commit

CASE-4 — the numbers
  Given  bugs found and fixed over two weeks, one dismissed
  When   the weeks and medians are computed
  Then   each week's counts and the median leave the dismissal out of the fixes

CASE-5 — the export
  Given  a bug fixed this month
  When   the report renders
  Then   it holds a section naming that bug
