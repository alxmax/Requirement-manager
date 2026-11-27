---
id: ARCH-BUGS-078
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-MAP-007, ARCH-VIEWER-007, ARCH-CONFIG-060]
satisfies: [SYS-REPORT-105]
lint_exempt: [file-spread]
---

# Known bugs are listed by module

## Description
> A repository's known bugs sat in documents nothing could read, so the map showed what was
> traced and said nothing about what was broken. Each repository now lists them by module,
> whether it already keeps them in files or adds them one at a time. See
> [ADR-0080](../../docs/adr/0080-known-bugs-are-listed-by-module.md).

Every bullet below is binding.
- A bug file is Markdown: a heading that names the module, and tables with an id, a title and a priority. [[REQ-BUGS-1116]]
- A bug file's heading gives its module and date, and a section `BUG_SKIP_SECTIONS` names is not read. [[REQ-BUGS-1148]]
- `requirements/bugs/*.md` and the files `BUG_SOURCES` names reach `_map.json` under `bugs`; the second kind is never written. [[REQ-BUGS-1117]]
- A malformed bug is an `INPUT:bugs` warning, and an open bug never fails the gate. [[REQ-BUGS-1118]]
- `sync --bug` adds one row to the module's file and does nothing else. [[REQ-BUGS-1119]]
- `sync --bug` refuses bad input, a module that would leave the folder and an unreadable file, writing nothing. [[REQ-BUGS-1149]]
- `ask --bugs` lists the known bugs by module, without a verdict. [[REQ-BUGS-1120]]
- The Problems page has a Bugs tab that groups by module and shows each bug's date. [[REQ-BUGS-1121]]
- The tab adds a bug to the repository's own file, or prints the command that does. [[REQ-BUGS-1122]]
- The tab exports the list it shows, for a reader who does not open the map. [[REQ-BUGS-1123]]
- `sync --bug` writes in the shape of the file it lands in, and never gives a number twice. [[REQ-BUGS-1126]]
- `sync --fix` moves a row to a register with its dates, version and commit. [[REQ-BUGS-1127]]
- `sync --fix` refuses an unknown or closed id, a declared source, a moved row and an unreadable register, writing nothing. [[REQ-BUGS-1150]]
- `sync` closes the bugs a commit's `Fixes-bug:` trailer names. [[REQ-BUGS-1128]]
- The map carries the register, and the tab shows it over time. [[REQ-BUGS-1129]]
- Fixed draws what was fixed against what is still open, week by week. [[REQ-BUGS-1154]]
- A fix that never had a row reaches the register, and a duplicate closes as one. [[REQ-BUGS-1156]]
- A requirement's dossier and its page list the open bugs that name it, and the verdict does not move. [[REQ-BUGS-1131]]

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

## Context
**Notes**
- `lint_exempt: file-spread` — the bug list is one capability with an engine side (read, add, close, list) and a viewer side (the Bugs tab and its file writer), so its members span the engine package and two viewer directories by design.

--------------------


---
id: REQ-BUGS-1116
status: confirmed
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
- A priority is the first `P0` to `P4` in its cell. `*` in the priority or id cell marks it estimated.
- A bug's id is `<file stem>:<row id>`, so two modules can each have a `B1`. Renaming the file changes the id.
- A bug records its file and the line of its row.
- A row with no id, title or priority, an unreal date, a repeated id or an unreadable file is a problem line, and the rows around it are still read.

## Cases
CASE-1 — a canonical file reads back whole
  Given  a file `# Bugs — Payments` with one row in every canonical column, and a file
         `# Bugs — Billing` whose headers are in other letter case, also holding a `B1`
  When   the files are read
  Then   the bug has module `Payments` and every field, with id `Payments:B1`, and the
         other reads as `Billing:B1` with its title and priority

CASE-2 — a repository's own columns are read
  Given  a table headed `#`, `Issue`, `Sev`, with `BUG_COLUMNS` naming the last two
  When   the file is read
  Then   its rows are bugs, and a canonical table in another file still reads

CASE-3 — another table is not a bug table
  Given  a file with a contents table and a bug table
  When   the file is read
  Then   only the bug table's rows are bugs, and no problem is reported

CASE-4 — a bad row does not cost the others
  Given  a table with a row with no priority, a repeated id and a date of `31.13.2026`
  When   the file is read
  Then   each gives one problem line naming its file and line, and the good rows are bugs

CASE-5 — an estimated priority is kept apart
  Given  a row whose id is `B2*` and a row whose priority is `P2 (audit), P1`
  When   the file is read
  Then   the first is `B2`, estimated, and the second is `P2`

CASE-6 — a row says where it came from
  Given  a bug on line 5 of a file
  When   the file is read
  Then   the bug carries that file and line

--------------------


---
id: REQ-BUGS-1148
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# A file's heading names its module, and a named section is skipped

## Description
> A team's existing bug document carries its module and date in the heading and keeps
> fixed bugs under their own section. Reading the heading and skipping that section is
> what lets the same reader serve a file nobody wrote for this tool.

Every bullet below is binding.
- The first `#` heading gives the module: the text after its last dash with a space on each side (`—`, `–` or `-`), without a trailing `(date)`. A file with no heading uses its own name.
- A row's date is `YYYY-MM-DD` or `DD.MM.YYYY`. A row with no date takes the date in the heading, and with neither it has none.
- `BUG_SKIP_SECTIONS` in `_config.json` is a regex on `##` headings: no table under a matching heading is read, down to the next `##`. A regex that does not compile is a problem line, and every table is then read.

## Cases
CASE-1 — the heading gives the module and the date
  Given  a heading `# Known issues — Billing (15.03.2026)` over rows with no date column
  When   the file is read
  Then   each bug has module `Billing` and date `2026-03-15`

CASE-2 — a named section is not read
  Given  bug tables under `## Open` and `## Recently fixed`, the second below a `###`
  When   the bugs load with `BUG_SKIP_SECTIONS` set to `(?i)fixed`, and again with it empty
  Then   the first load holds only the open bug, and the second holds both

CASE-3 — a bad pattern loses nothing
  Given  `BUG_SKIP_SECTIONS` set to `(`
  When   the bugs load
  Then   the rows are read and one problem line names the key

CASE-4 — a spaced dash ends the module name
  Given  a heading `# Known — Stock - Orders` and a heading `# Known — Stock-Orders`
  When   each file is read
  Then   the modules are `Orders` and `Stock-Orders`

--------------------


---
id: REQ-BUGS-1117
status: confirmed
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
status: confirmed
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
status: confirmed
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
- The id is the next `B<n>`, one past the highest in that file and in the register.
- `--prio` defaults to `P2`, `--date` to today, and `--where`, `--why` and `--source` fill their columns.
- `--prio P2*` writes the `*`, so a priority an assistant chose reads back as an estimate until a person edits the row.
- A `|` in a value is escaped and a line break becomes a space, so the row stays one row.
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

CASE-4 — the engine and the viewer write the same bytes
  Given  the shared fixture of a text and a bug
  When   `append_bug` and `appendBug` each run
  Then   each returns the fixture's expected text

CASE-5 — an estimate stays an estimate
  Given  a bug added with `--prio P2*`
  When   it is read back
  Then   its priority is `P2` and it is marked estimated

CASE-6 — the defaults, and the columns the flags name
  Given  a bug added with no `--prio` and no `--date`, and with `--where`, `--why` and
         `--source`
  When   it is added and read back
  Then   the command prints the file it wrote, and the bug is `P2`, not estimated, dated
         today, with those three values in their columns

--------------------


---
id: REQ-BUGS-1149
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# `sync --bug` refuses what it cannot write safely

## Description
> A bug added from the command line must never write outside the bugs folder, and never
> half a row: bad input is refused before anything is written.

Every bullet below is binding.
- A new file's name is the module's words joined by `-`, so it cannot leave the folder. A module with no word is refused.
- With no title, no module, a priority outside `P0` to `P4` or a date that is not real, it prints the reason, exits 2 and writes nothing.
- A bug file in the folder that cannot be read as UTF-8 makes it exit 2 and write nothing.

## Cases
CASE-1 — bad input writes nothing
  Given  a call with priority `P9`, a call with date `2026-13-40` and a call with module `///`
  When   each runs
  Then   each exits 2 and no file exists

CASE-2 — a module cannot leave the folder
  Given  a module named `../../etc`
  When   `sync --bug` runs
  Then   the file is `etc.md` inside `requirements/bugs/`

CASE-3 — a file that cannot be read
  Given  a file in the bugs folder that is not UTF-8
  When   `sync --bug` runs
  Then   it exits 2 and writes nothing

--------------------


---
id: REQ-BUGS-1120
status: confirmed
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
- A `--module` that no module's name contains says so and lists the modules there are, rather than that no bug matches.
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

CASE-6 — a module that does not exist is named
  Given  modules Payments and Search
  When   `ask --bugs --module refunds` runs
  Then   it prints `no module named 'refunds'` with both module names, exits 0, and a
         module that exists with no bug at that priority still reads `no known bugs match`

--------------------


---
id: REQ-BUGS-1121
status: confirmed
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
- At the right of the chip row, under `Export PDF`, one button opens every group (`Expand all`) or, once all are open, closes them (`Collapse all`).
- Under the chip row a legend names each priority, `P0` critical to `P4` minor, in the colour its rows use, and says that `*` marks an estimated priority.
- Every label goes through `t()`.

## Cases
CASE-1 — the tab counts the bugs
  Given  a map with three bugs
  When   Problems renders
  Then   the tab reads `Bugs` with 3

CASE-2 — bugs group by module with the date on the row
  Given  bugs in two modules, one dated 2026-03-15, and a bug with why, where, source and
         file
  When   the panel renders, and that bug's row is opened and its text clicked
  Then   each module is one group, and `15.03.2026` follows that bug's priority; the opened
         row shows why it matters, where, the source and the file with its line, and the
         click does not reach the row, so it stays open

CASE-3 — the label follows the language
  Given  the same map in Romanian
  When   Problems renders
  Then   the tab reads `Buguri` and the search placeholder is Romanian

CASE-4 — a repository with no bugs still has the tab
  Given  a map with no `bugs` key
  When   the panel renders
  Then   the tab reads 0 and the panel offers `Add bug`

CASE-5 — one button opens or closes every group
  Given  bugs in two modules, both groups closed
  When   `Expand all` is pressed, then the button again
  Then   both groups are open and the button reads `Collapse all`; then both are closed
         and it reads `Expand all`

CASE-6 — a legend says what each priority means
  Given  bugs in two modules
  When   the panel renders
  Then   under the chip row, P0 to P4 appear in order with critical, high, medium, low and
         minor, each in its rows' colour, and `*` is explained as an estimate

CASE-7 — a chip or a search narrows the list and opens its groups
  Given  bugs at P1 and P2 in one module and a P3 in another
  When   the P3 chip is chosen, then the text of one title is searched
  Then   each keeps only the matching bugs, grouped by module, the chip counts still count
         every priority the search found, and a narrowed list opens its groups

--------------------


---
id: REQ-BUGS-1122
status: confirmed
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

CASE-6 — a saved bug shows at once
  Given  a bug the folder accepted as `B4`, beside three known bugs
  When   the tab renders
  Then   the row shows, marked as waiting for `sync`, and the tab counts 4

CASE-7 — cancelling the folder picker keeps the form
  Given  a bug being saved
  When   the folder picker is cancelled, and when the write fails
  Then   a cancel keeps the form open with no error and adds no row, a failure keeps it
         open with the error, and without the API the form closes on the command

--------------------


---
id: REQ-BUGS-1123
status: confirmed
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
  Given  a list of bugs at P1, P2 and P3, narrowed to P1
  When   its report renders
  Then   its header names P1 and the total shown, and it holds only the P1 bugs

CASE-3 — nothing to export
  Given  an empty list
  When   the panel renders
  Then   the button is disabled

--------------------


---
id: REQ-BUGS-1126
status: confirmed
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
- A title that reads like a row in another module's file, or a `--where` equal to such a row's `Where`, prints that row as a warning, and the row is still written.
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
  Given  sections for `P0-P1` and `P2`, and a file whose `P2` section `BUG_SKIP_SECTIONS`
         matches
  When   a `P4` bug is added to the first, and a `P2` bug to the second
  Then   each joins the first table

CASE-4 — a likely duplicate
  Given  a module holding a bug with nearly the same title
  When   `sync --bug` runs without and then with `--force`
  Then   the first exits 2 and writes nothing, and the second adds the row

CASE-6 — a likely duplicate in another module
  Given  `Billing.md` holding a bug, and `Payments.md` with no bug like it
  When   `sync --bug` adds to Payments a row with nearly the same title, then one with a
         different title and the same `--where`
  Then   each run warns with the Billing row, exits 0 and adds its row to Payments

CASE-5 — the engine and the viewer agree
  Given  the shared fixture of texts, formats and file lists, and a folder holding the
         register beside a module file
  When   each side runs, and the files a row may go to are listed
  Then   each returns the fixture's expected text and file, the register is not listed,
         and `bug_format` is empty for the default format and carries a repository's own

--------------------


---
id: REQ-BUGS-1127
status: confirmed
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

## Cases
CASE-1 — a fix moves the row
  Given  an open bug and a version file
  When   `sync --fix` runs, then with `--version` and `--commit`, then in a repository
         with neither a version file nor git
  Then   `ask --bugs` no longer lists it and the register row has every field; the flags'
         values win, and with neither the version and the commit read `—`

CASE-2 — a number is never given twice
  Given  the highest bug closed
  When   `sync --bug` adds to that file
  Then   the new row takes the next number

CASE-3 — a dismissal
  Given  an open bug
  When   `sync --fix ID --note "works as designed"` runs
  Then   the register says `not a bug` and keeps the note

CASE-4 — a repository's own register
  Given  a register with localized columns and no module column
  When   a bug is closed
  Then   the row fits those columns

CASE-5 — a glob over the folder
  Given  `BUG_SOURCES` matching the bugs folder
  When   the list is read
  Then   the register's rows are not listed

--------------------


---
id: REQ-BUGS-1150
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# `sync --fix` refuses what it cannot close exactly

## Description
> Closing a bug rewrites two files. When the id, the row or the register is not exactly
> what was read, nothing is written, so a refused close never costs a row.

Every bullet below is binding.
- An unknown id, a closed id, or a bug in a file only `BUG_SOURCES` names exits 2 and writes nothing.
- A row that is not on the line it was read from, or a register that cannot be read, exits 2 and writes nothing.

## Cases
CASE-1 — refused closes write nothing
  Given  an unknown id, a closed id and a bug in a declared source
  When   `sync --fix` runs on each
  Then   each exits 2 and every file is byte-identical

CASE-2 — the right row or none
  Given  a stray carriage return above the table, and a row that moved
  When   a bug is closed
  Then   the first closes the named row and the second is refused

CASE-3 — a broken register survives
  Given  a register that is not UTF-8
  When   `sync --fix` runs
  Then   it exits 2 and both files are byte-identical

--------------------


---
id: REQ-BUGS-1128
status: confirmed
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
status: confirmed
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
- A row's priority reaches the map as an open bug's does: `P4*` is `prio: P4` with `estimated: true`.
- A row's commit links to the forge when the remote is GitHub. The forge reaches `_map.html` only, because it differs between a clone and a fork.
- When the register holds a row, the Bugs tab has an Open / Fixed toggle. Fixed shows found, fixed, version, commit and note.
- Fixed shows, by week, the bugs found, the bugs fixed and what was still open, and the median days to fix per priority.
- A `not a bug` row leaves the open count and counts in neither the fixes nor the median.
- Fixed lists its rows only for a chosen week or a search.
- The Bugs tab shows 25 rows of a list at a time, with pages. The export prints every row.
- The export gains a section of what was fixed in the last 30 days.

## Cases
CASE-1 — the register reaches the map
  Given  one closed bug, its priority estimated as `P4*`
  When   `sync` runs
  Then   `_map.json` carries it under `bugs_fixed` and not under `bugs`, with `prio` `P4` and `estimated` true

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

CASE-6 — the rows wait for a choice
  Given  a register with rows
  When   Fixed renders with no week chosen and no search
  Then   it shows no row and asks for a week, and a chosen week holds the rows closed in it

CASE-7 — a long list
  Given  30 open bugs in one module
  When   the tab renders
  Then   it shows 25 rows and says page 1 of 2, and a page past the end is the last page

--------------------


---
id: REQ-BUGS-1131
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# A requirement shows the open bugs that name it

## Description
> A bug list by module answers "what is broken in Billing". The question a reader of one
> requirement has is "is this one broken", and the answer sat in a `Source` cell nothing
> read. A row that writes the id is the link: no new column, nothing to keep in step. See
> [ADR-0083](../../docs/adr/0083-a-bug-names-the-requirement-it-breaks.md).

Every bullet below is binding.
- An open bug names a requirement when the requirement's id is written whole in its title,
  where, why or source: `X-10` does not name `X-1`, and `X-1#CASE-2` or `[[X-1]]` does.
- `_map.json` gives each bug `reqs`, the ids of the corpus it names, sorted.
- `gate --show ID` lists the open bugs that name `ID`, highest priority first, and its
  `--json` record carries them as `bugs`. A repository with no bug list has no `bugs` key.
- A requirement's page in the map lists the same bugs, with priority, id, title and where.
- A bug in the register is not open, and is not listed.
- An open bug that names a requirement adds no finding: the gate's verdict and exit code are
  the same with or without it.

## Cases
CASE-1 — the dossier lists the bugs that name it
  Given  two open bugs, one whose source names the requirement
  When   `gate --show ID` runs
  Then   an `Open bugs (1)` section lists that bug's priority, id and title, and not the other

CASE-2 — the record carries the list
  Given  a repository with no bug list, then one with a bug that names the requirement, then
         one with a bug that names nothing
  When   `gate --show ID --json` runs on each
  Then   the first record has no `bugs` key, the second lists the bug, the third an empty list

CASE-3 — an id is named whole
  Given  bugs writing `X-10 fails`, `X-1#CASE-2`, `[[X-1]]` and `x-1`
  When   they are linked to `X-1` and `X-10`
  Then   they name `X-10`, `X-1`, `X-1` and nothing

CASE-4 — the map carries the ids, and a fixed bug leaves the dossier
  Given  an open bug that names a requirement
  When   `sync` runs, then `sync --fix` closes the bug
  Then   the map's bug carries the id in `reqs`, and the dossier then lists no bug

CASE-5 — the verdict does not move
  Given  an open P0 that names a confirmed requirement
  When   `gate --full --strict` runs
  Then   it exits 0 and no line names the bug

CASE-6 — the page lists them
  Given  a map whose bugs name a requirement, one of them, and one that names nothing
  When   the requirement's page renders
  Then   it lists `Open bugs` with the bug that names it and its where, not the other, in
         Romanian as `Buguri deschise`, and nothing when no bug names it

--------------------


---
id: REQ-BUGS-1154
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# Fixed draws the trend

## Description
> The weekly table holds the numbers; a line shows whether what is still open goes down as
> the fixes go up, which a column of numbers does not.

Every bullet below is binding.
- Under the weekly table, Fixed draws one line chart on one axis from 0, one point per row of the table: the fixes so far and what is still open, and the total found only when `Show total` is ticked.
- The last point of still open is the table's last still-open count, and the fixes and the total so far count from the first week, not the first one shown.
- A line is never named by colour alone: a legend, a label at its last point, pushed apart when two are closer than 14 px, and a tooltip on hover or focus.
- A line above the chart gives the fixes, what is still open, and the highest still-open count with its first week.
- Choosing a week in the chart is the same choice as in the table.
- Every string the chart shows is translated where the tab is.

## Cases
CASE-1 — two lines under the table
  Given  a register with twelve weeks of activity
  When   Fixed renders
  Then   the chart follows the table and draws two lines of twelve points, with `Show total`
         unticked

CASE-2 — the last point is what is still open
  Given  the same register
  When   the weeks are computed
  Then   the last week's still open and fixes so far equal the open and fixed rows, and the
         line above the chart names the peak and its first week

CASE-3 — end labels do not overlap
  Given  label positions 100, 105 and 40
  When   they are spread
  Then   they read 100, 114 and 40

CASE-4 — translated
  Given  the same register
  When   Fixed renders in Romanian and in German
  Then   the title, the checkbox, the line above and the week labels are translated and no
         English string of the chart shows

--------------------


---
id: REQ-BUGS-1156
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-BUGS-078]
---

# A fix never listed, and a duplicate

## Description
> A bug found and fixed before anyone listed it left no row, so the register undercounted the
> fixes; a duplicate could only close as `not a bug`, which said something else.

Every bullet below is binding.
- `sync --fix TITLE --new --module M` writes one register row and leaves the module's file as it was.
- The row's id is the module file's next `B<n>`, past every open row and every register row of that file.
- Its found date is `--date`, else the day of the commit `--commit` names, else today, and its note is `--note` or `fixed before it was listed`.
- `sync --fix ID --duplicate-of OTHER` closes the row with version `duplicate` and the note `duplicate of OTHER`, and `ask --bugs` names it under OTHER.
- A duplicate, like a dismissal, counts in neither the fixes nor the time to fix.
- An OTHER that is the same bug or no known bug, `--new` with `--duplicate-of`, and `--new` with no module or a bad priority exit 2 and write nothing.

## Cases
CASE-1 — a fix that was never listed
  Given  a module file holding B1 and B2
  When   `sync --fix "Refund rounds down" --new --module Billing --date 2026-10-03` runs, then
         again with another title
  Then   the register holds `Billing:B3` found on 2026-10-03 with the default note, then
         `Billing:B4`, the module file is unchanged, and the next `sync --bug` gives B5

CASE-2 — the found day is the commit's
  Given  a commit dated 2026-09-14
  When   `sync --fix TITLE --new --module Billing --commit SHA` runs, then once with no commit
  Then   the first row is found on 2026-09-14 with that commit, and the second on the day it was
         fixed

CASE-3 — a duplicate is closed and named
  Given  open bugs Billing:B1 and Billing:B2
  When   `sync --fix Billing:B2 --duplicate-of "Billing B1"` runs
  Then   the register row reads `duplicate`, `—` and `duplicate of Billing:B1`, and `ask --bugs`
         prints `closed as its duplicate: Billing:B2` under B1

CASE-4 — a duplicate is no fix
  Given  a register with a duplicate and a fix closed the same week
  When   the weeks and medians are computed
  Then   the week counts one fix and the median counts only the fix

CASE-5 — refusals write nothing
  Given  the same module file and no register
  When   `--duplicate-of` names an unknown bug or the bug itself, `--new` comes with
         `--duplicate-of`, with no `--module`, or with `--prio high`
  Then   each exits 2, the module file is unchanged and no register is written
