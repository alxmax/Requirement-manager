---
id: CORE-PARSE-001
status: confirmed
layer: bus
owner: Alex
depends_on: []
superseded_by:
milestone: v1.00
---

# Requirement reading

> Every command in the tool — the gate, the map, the next-steps list — needs the
> requirement files as structured data, not raw text. This is the part that reads each
> Markdown file and hands the rest of the tool clean records to work with. If it breaks,
> nothing downstream can run.

## WHAT — Contract (normative)
Every line in this section is binding.
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Deliberately minimal (no YAML library) to keep the engine stdlib-only: nested mappings
  and multi-line scalars are not supported.

## HOW — Acceptance (= tests)
AC-1
  Given  a file with valid frontmatter
  When   it is parsed
  Then   its scalar and list fields appear in `meta`

AC-2
  Given  a frontmatter line carrying a trailing `# comment`
  When   it is parsed
  Then   the comment is stripped from the value

AC-3
  Given  a file without a leading `---` block
  When   it is parsed
  Then   `meta` is empty and the whole text is the body

AC-4
  Given  a requirements directory containing files starting with `_`
  When   requirements are loaded
  Then   those files are excluded from the result

AC-5
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
