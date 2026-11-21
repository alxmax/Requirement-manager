---
id: ARCH-CUSTOMTRACE-077
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v8.25
depends_on: [ARCH-CONFIG-060, ARCH-SCAN-002]
satisfies: [SYS-READ-103]
---

# A repository describes its own trace convention

## Description
> A repository that already traces its code has its own tags, its own test-file names and
> its own requirement files, often plain text or HTML in several folders. The tool reads that
> convention from the config instead of asking the repository to rewrite itself. See
> [ADR-0077](../../docs/adr/0077-a-repository-describes-its-own-trace-tags.md).

Every bullet below is binding.
- `TRACE_TAGS` adds tag forms, each a pattern whose first group is the id, and a role. [[REQ-CUSTOMTRACE-1110]]
- `TEST_FILE_PATTERNS` adds globs that make a file a test file. [[REQ-CUSTOMTRACE-1112]]
- `REQUIREMENT_SOURCES` reads requirements kept as text, HTML or Markdown, in folders of the repository's choosing. [[REQ-CUSTOMTRACE-1113]]
- A source can read its glob from the repository instead of the code folder, so one folder is checked against requirements kept elsewhere. [[REQ-CUSTOMTRACE-1137]]
- Requirements kept as CSV rows or a JSON list are read through a field map, and rows marked structural are exempt from code and tests. [[REQ-CUSTOMTRACE-1138]]

## Cases
CASE-1 — a repository in its own convention is read
  Given  a config with a `TRACE_TAGS` form, a `TEST_FILE_PATTERNS` glob and two
         `REQUIREMENT_SOURCES`, and a repository written only in that convention
  When   `gate` runs
  Then   each traced requirement has its code and its test, and a tag to no requirement is RM001

CASE-2 — no config, no change
  Given  a repository with requirements, code and tests and no `_config.json`
  When   `sync` and `gate --full` run
  Then   their output and the map are the same as before this change

CASE-3 — a bad entry is named and skipped
  Given  a `TRACE_TAGS` pattern with no capture group
  When   `gate` and then `gate --strict` run
  Then   it is an `INPUT:config` warning, then an error, and the other keys still apply

--------------------


---
id: REQ-CUSTOMTRACE-1110
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CUSTOMTRACE-077]
---

# Extra tag forms

## Description
> The tag is whatever the repository already writes; the tool only needs to know where the id
> is and what the tag means.

Every bullet below is binding.
- Each `TRACE_TAGS` entry is `{"pattern": <regex>, "role": <role>}`; the pattern's first group is the id.
- `role` is `implements`, `tested-by` or `auto`; `auto` is `tested-by` in a test file and `implements` anywhere else.
- A configured form is read wherever a built-in tag is read: membership, dangling tags and the untagged-file report.
- The built-in `implements:`, `tested-by:` and `verifies:` forms always stay.
- A pattern that does not compile, has no group, or names another role is an `INPUT:config` warning, and that entry is skipped.

## Cases
CASE-1 — a configured form is a member
  Given  a form `\\trace\{([A-Z0-9_]+)\}` with role `implements` and a code file holding `/// \trace{AB_CD12}`
  When   the file is scanned
  Then   it is an `implements` member of `AB_CD12`

CASE-2 — auto follows the file
  Given  the same form with role `auto`, in a code file and in a test file
  When   both are scanned
  Then   the code file implements `AB_CD12` and the test file is its `tested-by`

CASE-3 — a configured tag to no requirement is dangling
  Given  `/// \trace{AB_ZZ99}` and no requirement `AB_ZZ99`
  When   `gate` runs
  Then   it reports RM001 for `AB_ZZ99`

CASE-4 — a bad form is skipped
  Given  one entry with no capture group and one with role `owns`
  When   the config is applied
  Then   both are `INPUT:config` warnings and the built-in forms still work

--------------------


---
id: REQ-CUSTOMTRACE-1112
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CUSTOMTRACE-077]
---

# Test files by the repository's own naming

## Description
> A team names its test files its own way; the tool should know them as tests.

Every bullet below is binding.
- A file matching a `TEST_FILE_PATTERNS` glob is a test file, whether the path is relative or absolute.
- The built-in convention still applies; the globs only add.
- Being a test file decides an `auto` tag's role.

## Cases
CASE-1 — a glob makes a test file
  Given  `TEST_FILE_PATTERNS` `["**/*Test.cpp"]` and `src/BrakeLightTest.cpp`
  When   the file is classified
  Then   it is a test file

CASE-2 — the convention still holds
  Given  the same config and `tests/brake_light.cpp`
  When   the file is classified
  Then   it is a test file

CASE-3 — without the glob it is code
  Given  no `TEST_FILE_PATTERNS` and `src/BrakeLightTest.cpp`
  When   the file is classified
  Then   it is not a test file, as before

--------------------


---
id: REQ-CUSTOMTRACE-1113
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CUSTOMTRACE-077]
---

# Requirements kept as text, HTML or Markdown, in any folders

## Description
> Requirements live where the team keeps them, often as plain text or HTML, one folder per
> module. The tool cuts them into requirements with one pattern: the line a requirement
> starts on.

Every bullet below is binding.
- Each `REQUIREMENT_SOURCES` entry names a `glob` of files, relative to the code root, searched recursively.
- `format` is `text`, `html` or `md`; `md` files are read as requirement files of this tool.
- For `text` and `html`, `start` is the regex of the line a requirement starts on; its first group is the id.
- A requirement runs from its start line to the next start line or the end of the file; each sentence is one clause.
- HTML is read as text first: a block ends a line, and a table row reads as one line.
- `status` (`confirmed` by default, or `draft`) and `owner` (`external` by default) apply to every requirement of the source.
- A requirement read from text or HTML gets no finding about this tool's Markdown format: sections, cases, readability.
- `clarify` asks no case of a requirement read from text or HTML.
- A source file is not reported as untagged code.
- A source that matches no file, and a duplicate id, are `INPUT:requirements` errors, as for `requirements/`.
- The lock, the map and every generated file stay in `requirements/`.

## Cases
CASE-1 — text in two module folders is read
  Given  a text source on `modules/*/reqs/**/*.txt` with `start` `^([A-Z][A-Z0-9_]+):`, and requirements in `modules/brake/reqs/` and `modules/door/reqs/sub/`
  When   the workspace loads
  Then   every requirement is found, with its own file and one clause per sentence

CASE-2 — an HTML table row is one requirement
  Given  an HTML source whose table row holds an id cell and a text cell
  When   the workspace loads
  Then   the row is one requirement with that id and that text

CASE-3 — a text requirement is not held to the Markdown format
  Given  a confirmed requirement read from text, with code and a test
  When   `gate --full` runs
  Then   it reports no missing section, no missing case and no readability finding for it

CASE-4 — a source that matches nothing is named
  Given  a source on `nowhere/**/*.txt`
  When   `gate` runs
  Then   it is an `INPUT:requirements` error naming the glob

CASE-5 — the generated files stay put, and a source is not untagged code
  Given  an HTML source and a code tree
  When   `sync` and `gate --risk` run
  Then   `_reqlock.json` and `_map.json` are written in `requirements/` only, and the HTML file is not listed as untagged

--------------------


---
id: REQ-CUSTOMTRACE-1137
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CUSTOMTRACE-077]
---

# A source reads from the code folder or from the repository

## Description
> Checking one folder means pointing `--code` at it, and a source's glob is read from there:
> requirements kept beside it, in `specs/`, were only reached with `../`. A source can name
> where its glob starts instead. See
> [ADR-0087](../../docs/adr/0087-a-source-reads-from-the-repository.md).

Every bullet below is binding.
- A source with no `root` reads its glob from the code root, exactly as before.
- With `root: repo`, it reads its glob from the nearest folder at or above the code root that
  holds `.git`; with none, that is a problem naming the source and nothing is read.
- A `root` other than `code` or `repo` is a config problem and the source is ignored.
- A glob that matches no file from the code root but would from the repository is reported
  with that hint, and is not read.

## Cases
CASE-1 — a glob reads from the code folder as before
  Given  a source with no `root`, and the same source written with `../` from a subfolder
  When   each is loaded from its code root
  Then   both read the same requirements

CASE-2 — root: repo reads from the repository
  Given  a repository with `.git` and a source with `root: repo`
  When   it is loaded with a subfolder as the code root
  Then   it reads the requirements under the repository

CASE-3 — no repository above is named
  Given  a source with `root: repo` and no `.git` above the code root
  When   it is loaded
  Then   nothing is read and the problem says no repository holds the code folder

CASE-4 — an unknown root is refused
  Given  a source with `root: up`
  When   the config is validated
  Then   the source is ignored and the problem lists code and repo

CASE-5 — a glob the repository would match is pointed at root: repo
  Given  a source with no `root` whose glob matches only from the repository
  When   it is loaded with a subfolder as the code root
  Then   nothing is read and the problem says to set root: repo

--------------------


---
id: REQ-CUSTOMTRACE-1138
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CUSTOMTRACE-077]
---

# Requirements kept as rows

## Description
> A corpus exported from a requirements tool comes as rows: a CSV file or a JSON list, with its
> own column names, and with headings and information entries among the requirements. Reading
> one took a few hundred lines of glue. A field map does it. See
> [ADR-0088](../../docs/adr/0088-requirements-kept-as-rows.md).

Every bullet below is binding.
- A source with `format: csv` or `json` reads one requirement per row through `fields`, which
  maps `id` (required) and optionally `title`, `contract`, `cases`, `status`, `depends_on` and
  `satisfies` to the source's columns or keys; any other key is a config problem.
- A contract text is one clause per sentence, a list one clause per item; cases are one case
  per item. A title missing from the row is the contract's first sentence.
- `depends_on` and `satisfies` split on `list_separator` (default `,`), or take a JSON list.
- A status of `confirmed`, `draft` or `deprecated` in the row wins over the source's status.
- A CSV file is read without its byte-order mark, with `delimiter` (default `,`); a JSON source
  is a list of objects, or one under the key `items` names.
- A row with no id is a problem naming the file and the row, and the other rows are read.
- A row whose `fields.structural.field` holds one of its `values` is a requirement of layer
  `aggregate`, exempt from code and tests; when more than half the rows of a file are, that is a
  problem naming the count.

## Cases
CASE-1 — each CSV row is a requirement
  Given  a CSV file with a byte-order mark, `;` between columns and its own column names
  When   it is read through a field map
  Then   each row with an id is a requirement with its title, clauses, cases, dependencies
         and status

CASE-2 — a row with no id is a problem
  Given  the same file with one row whose id cell is empty
  When   it is read
  Then   that row is a problem naming its number, and the others are read

CASE-3 — a structural row is exempt, and too many are named
  Given  a row marked as a heading, then a file where most rows are
  When   each is read
  Then   the heading is layer aggregate, and the second file is a problem with its count

CASE-4 — a JSON list under a key is read
  Given  a JSON object whose `requirements` key holds a list
  When   it is read with `items: requirements`
  Then   each object is a requirement, a list contract is one clause per item

CASE-5 — a field map without an id is refused
  Given  field maps with no id, or with an unknown key
  When   the config is validated
  Then   each source is ignored with one problem

CASE-6 — the gate reads a CSV corpus
  Given  a repository whose only requirements are CSV rows, one tagged in code, one a heading
  When   the gate runs
  Then   neither is reported as missing code, and no tag is dangling

