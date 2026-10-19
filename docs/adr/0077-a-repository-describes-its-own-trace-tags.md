# ADR-0077 — A repository describes its own trace tags, test files and requirement sources

- **Status:** Accepted.
- **Decided:** 2026-10-19
- **Evidence:**
  - The tag grammar is one fixed expression, `TAG_RE` at `plugin/scripts/reqmap_engine/tags.py:21`:
    a role word from `ROLES`, a colon, and an id matching `_ID_PAT`
    (`[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+`, `tags.py:20`). A `\command{ID}` form, or an id with `_`,
    never matches.
  - A test file is recognised only by convention, `_is_test_path` in `tags.py`: a `test`/`tests`/
    `spec` directory segment, a lower-case `test_` prefix, or a suffix such as `_test.go`. A file
    named `BrakeLightTest.cpp` is not a test file.
  - Requirements are read from one directory, not recursively, and only as this tool's
    Markdown: `load_requirements` at `parse.py:124` lists `reqs_dir` and keeps its `*.md` files.
  - A repository that already traces its code keeps its requirements where and how it always
    has, often as plain text or HTML, one folder per module.
  - `mcp.py:42` already accepts an id with `_` (`[A-Za-z0-9][A-Za-z0-9_-]*`), and
    `load_requirements` accepts any text id.
  - `python scripts/check_engine_budget.py` on this change: core 6,741 logical lines in 61
    modules, 35 above ADR-0076's 6,706. `customtrace.py` is not among them.

## Context

The tool's checks are only as good as its reading of the links. Until now a repository had to
write links the tool's way and keep its requirements as the tool's Markdown. A team whose code
says `/// \trace{AB_CD12}` above every function, whose test files are named `*Test.cpp`, and
whose requirements are paragraphs in text and HTML files spread over module folders, got
nothing until it converted all three, and would have to convert every new file again.

## Decision

The repository describes its convention in `requirements/_config.json`, and the engine reads
it. Every key is optional; with none set, behaviour is exactly as before, and the module that
reads them, `customtrace.py`, is never imported.

1. **`TRACE_TAGS`** — extra tag forms, each `{"pattern": <regex>, "role": <role>}`. The
   pattern's first group is the id. `role` is `implements`, `tested-by`, or `auto`: tested-by in
   a test file, implements anywhere else, so one tag form serves code and tests. The built-in
   forms always stay. In JSON a literal backslash is `\\\\`:
   `{"pattern": "\\\\trace\\{([A-Z0-9_]+)\\}", "role": "auto"}`.
2. **`TEST_FILE_PATTERNS`** — globs that also make a file a test file, added to the built-in
   convention, matched whether the path is relative or absolute. Example: `["**/*Test.cpp"]`.
3. **`REQUIREMENT_SOURCES`** — files that hold requirements, each
   `{"glob", "format", "start", "status", "owner"}`. `format` is `text`, `html` or `md`. For text
   and HTML, `start` is the regex of the line a requirement starts on, its first group the id;
   the requirement runs to the next start line, and each sentence is one clause. HTML is read
   as text first: a block ends a line and a table row reads as one line. `status` (default
   `confirmed`) and `owner` (default `external`) apply to every requirement of the source. The
   lock, the map and every generated file stay in `requirements/`.

A requirement read from text or HTML is not held to this tool's Markdown format: no section,
case or readability check, and `clarify` asks no case of it; it still asks about vague words,
and every link check (dangling tag, no code, no test, drift) applies. A source file is not
reported as untagged code.

A bad `TRACE_TAGS` or `REQUIREMENT_SOURCES` entry (no regex, no group, an unknown role, format
or status) is an `INPUT:config` warning, an error under `--strict`, and only that entry is
skipped (ADR-0054). A source that matches no file and a duplicate id are `INPUT:requirements`
errors, as an unreadable file in `requirements/` already is.

**No `ID_PATTERN`.** The design first proposed one global id regex. It is not needed: a
configured tag's pattern says what its id looks like, a source's `start` says it for
requirements, and the MCP server and the loader already accept an id with `_`. A global regex
would have meant recompiling a pattern six modules import by name, for no reader.

## Alternatives rejected

- **Convert the repository once** (a script or Copilot rewrites the tags and the requirement
  files). Two conventions in one tree, redone on every new file; and a team owns its comments
  and its documents, not the tool.
- **A plugin hook** (Python the repository supplies). Executes a repository's code inside the
  gate; a regex in a JSON file is data, and the gate stays stdlib and side-effect free.
- **Folders of Markdown only** (`REQUIREMENT_DIRS`, the first draft). Covers a repository that
  already writes this tool's format, which is not the case this decision exists for.

## Consequences

- One repository can be read in its own convention; the default corpus is unaffected, and the
  suite pins that the module is not loaded without the keys.
- The core grows by the hooks that consult the config (35 logical lines), so
  `CORE_LOGICAL_BUDGET` rises from 6,706 to 6,741 (ADR-0053).
- `init` and `draft` keep writing the built-in `implements:` form: a configured form is read,
  never written.
- With `--cache`, a changed `TRACE_TAGS` takes effect on a file only once that file changes;
  run without `--cache` after editing the config.

## Revisit when

A repository needs a tag form one regex with one group cannot express (an id list in one tag,
the role written inside the tag), or requirement files whose requirements are not cut by a
start line (a spreadsheet, a ReqIF export).
