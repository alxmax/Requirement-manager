---
id: ARCH-PARSE-001
status: confirmed
level: architecture
layer: bus
owner: Alex
depends_on: []
satisfies: [SYS-READ-103]
superseded_by:
milestone: v1.00
---

# Requirement reading

## Description
> Every command in the tool — the gate, the map, the next-steps list — needs the
> requirement files as structured data, not raw text. This is the part that reads each
> Markdown file and hands the rest of the tool clean records to work with. If it breaks,
> nothing downstream can run.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     the frontmatter  the `---` header block at the top of a requirement file.
     a scalar         a single-value field, such as `status: confirmed`.
     the body         everything after the frontmatter block.
     the stem         a filename without its `.md` extension. -->

**What it produces**
- `load_requirements` parses each `requirements/*.md` file into a record
  `{meta, body, path}`.
- `meta` is the parsed frontmatter, and `body` is the markdown after the frontmatter
  block.
- The `id` comes from the frontmatter `id:` field, falling back to the filename stem.

**What the frontmatter grammar accepts**
- The grammar supports scalars, inline `[a, b]` lists, and block-style lists written as
  `key:` then indented `- item`.
- A trailing `# comment` is stripped from a value.
- Matching surrounding quotes are removed from a scalar.
- An inline list missing its closing `]` is parsed leniently, rather than kept as a
  literal string.

**Edge cases**
- A file with no leading `---` block yields empty `meta` and the whole text as `body`.
- A file whose name starts with `_` (a lock, the generated map) is excluded.
- A leading UTF-8 BOM is tolerated.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- Deliberately minimal (no YAML library) to keep the engine stdlib-only: nested mappings
  and multi-line scalars are not supported.

## Cases (= tests)
CASE-1
  Given  a file with valid frontmatter
  When   it is parsed
  Then   its scalar and list fields appear in `meta`

CASE-2
  Given  a frontmatter line carrying a trailing `# comment`
  When   it is parsed
  Then   the comment is stripped from the value

CASE-3
  Given  a file without a leading `---` block
  When   it is parsed
  Then   `meta` is empty and the whole text is the body

CASE-4
  Given  a requirements directory containing files starting with `_`
  When   requirements are loaded
  Then   those files are excluded from the result

CASE-5
  Given  a block-style list and an unclosed inline list
  When   they are parsed
  Then   both yield the intended list

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- You have `requirements/AUTH-001.md`: a small header block (`id: AUTH-001`,
  `priority: must-have`) then prose. This reader opens the file, lifts the header
  into a `meta` table (so `priority` becomes a field the map can show) and keeps the
  rest as `body`. A stray `_reqlock.json` next to it is skipped — its name starts `_`.

## WHERE — Current implementation
- `parse_frontmatter` (with `_clean_item`) and `load_requirements` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-PARSE-208
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# Load_requirements parses each requirements/.md file into a record

> `load_requirements` parses each `requirements/*.md` file into a record `{meta, body,
> path}`.

Scenario: load_requirements returns a meta/body/path record per file
  Given  a `requirements/` directory with one valid `REQ-A-001.md`
  When   `load_requirements(dir)` runs
  Then   the returned dict's entry carries `meta`, `body`, and `path` keys

## Members in code (auto)




--------------------


---
id: REQ-PARSE-209
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# Meta is the parsed frontmatter, and body is

> `meta` is the parsed frontmatter, and `body` is the markdown after the frontmatter
> block.

Scenario: parse_frontmatter splits the header fields from the markdown that follows
  Given  `"---\nid: REQ-A-001\nstatus: draft\n---\nbody text\n"`
  When   `parse_frontmatter(text)` runs
  Then   `meta["id"] == "REQ-A-001"` and `body == "body text\n"`, with no `---` markers in either

## Members in code (auto)




--------------------


---
id: REQ-PARSE-210
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# The id comes from the frontmatter id: field

> The `id` comes from the frontmatter `id:` field, falling back to the filename stem.

Scenario: a file with no id: field is keyed by its filename stem
  Given  `REQ-A-001.md` whose frontmatter carries no `id:` line
  When   `load_requirements(dir)` runs
  Then   the returned dict has the key `"REQ-A-001"`, taken from the filename

## Members in code (auto)




--------------------


---
id: REQ-PARSE-211
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# The grammar supports scalars, inline a, b lists

> The grammar supports scalars, inline `[a, b]` lists, and block-style lists written as
> `key:` then indented `- item`.

Scenario: a block-style key: / indented - item list parses to a Python list
  Given  `"---\ndepends_on:\n  - A-B-001\n  - C-D-002\n---\n"`
  When   `parse_frontmatter(text)` runs
  Then   `meta["depends_on"] == ["A-B-001", "C-D-002"]`

## Members in code (auto)




--------------------


---
id: REQ-PARSE-212
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# A trailing # comment is stripped from a

> A trailing `# comment` is stripped from a value.

Scenario: a trailing # comment does not leak into the parsed value
  Given  `"---\nstatus: draft  # not enforced\n---\n"`
  When   `parse_frontmatter(text)` runs
  Then   `meta["status"] == "draft"`, with the comment text absent

## Members in code (auto)




--------------------


---
id: REQ-PARSE-213
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# Matching surrounding quotes are removed from a scalar

> Matching surrounding quotes are removed from a scalar.

Scenario: matching quote characters are stripped from a scalar value
  Given  `'---\nid: "REQ-X-001"\nstatus: \'draft\'\n---\n'`
  When   `parse_frontmatter(text)` runs
  Then   `meta["id"] == "REQ-X-001"` and `meta["status"] == "draft"`, quotes removed

## Members in code (auto)




--------------------


---
id: REQ-PARSE-214
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# An inline list missing its closing is parsed

> An inline list missing its closing `]` is parsed leniently, rather than kept as a
> literal string.

Scenario: an unclosed inline list still parses as a list, not a literal string
  Given  `"---\ntags: [x, y\n---\n"` (no closing `]`)
  When   `parse_frontmatter(text)` runs
  Then   `meta["tags"] == ["x", "y"]`, not the literal string `"[x, y"`

## Members in code (auto)




--------------------


---
id: REQ-PARSE-215
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# A file with no leading --- block yields

> A file with no leading `---` block yields empty `meta` and the whole text as `body`.

Scenario: a file with no frontmatter block yields empty meta and the full text as body
  Given  `"# Title\njust text\n"` (no leading `---`)
  When   `parse_frontmatter(text)` runs
  Then   `meta == {}` and `body == "# Title\njust text\n"`

## Members in code (auto)




--------------------


---
id: REQ-PARSE-216
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# A file whose name starts with _ (a

> A file whose name starts with `_` (a lock, the generated map) is excluded.

Scenario: an underscore-prefixed file is excluded from load_requirements
  Given  a `requirements/` directory holding `_draft.md` and `REQ-A-001.md`
  When   `load_requirements(dir)` runs
  Then   the result contains only `"REQ-A-001"`, not any id from `_draft.md`

## Members in code (auto)




--------------------


---
id: REQ-PARSE-217
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PARSE-001]
superseded_by:
---

# A leading UTF-8 BOM is tolerated

> A leading UTF-8 BOM is tolerated.

Scenario: a leading UTF-8 BOM does not break frontmatter parsing
  Given  a requirement file saved with a leading BOM before `---\nid: REQ-A-001\n...`
  When   `load_requirements(dir)` runs
  Then   `"REQ-A-001"` is a key in the result, with `meta["status"]` read correctly

## Members in code (auto)
