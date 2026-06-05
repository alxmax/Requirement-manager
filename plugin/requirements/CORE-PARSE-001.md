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

> Turn the requirement files on disk into structured records the rest of the tool reasons about.

## WHAT — Contract (normative)
- It shall parse each `requirements/*.md` file into a record `{meta, body, path}`, where
  `meta` is the parsed frontmatter and `body` is the markdown after the frontmatter block.
- The frontmatter grammar shall support scalars, inline `[a, b]` lists, and block-style
  (`key:` then indented `- item`) lists. A trailing `# comment` shall be stripped from a
  value; matching surrounding quotes shall be removed from a scalar; an inline list
  missing its closing `]` shall be parsed leniently rather than kept as a literal string.
- The `id` shall come from the frontmatter `id:` field, falling back to the filename stem.
- A file with no leading `---` block shall yield empty `meta` and the whole text as `body`.
- Files whose name starts with `_` (locks, generated map) shall be excluded; a leading
  UTF-8 BOM shall be tolerated.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Deliberately minimal (no YAML library) to keep the engine stdlib-only: nested mappings
  and multi-line scalars are not supported.

## HOW — Acceptance (= tests)
- A file with valid frontmatter yields its scalar and list fields in `meta`.
- A trailing `# comment` on a frontmatter line is stripped from the value.
- A file without a leading `---` block returns empty `meta` and the whole text as body.
- Files starting with `_` are excluded from the result.
- A block-style list and an unclosed inline list both parse to the intended list.

## WHERE — Current implementation
- `parse_frontmatter` (with `_clean_item`) and `load_requirements` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
