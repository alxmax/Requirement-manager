---
id: CORE-PARSE-001
status: confirmed
layer: bus
owner: alex
depends_on: []
superseded_by:
---

# Requirement reading

> Turn the requirement files on disk into structured records the rest of the tool reasons about.

## Input
- A `requirements/` directory containing `*.md` files, each with a `---` YAML-ish
  frontmatter block followed by a prose body.

## Description
Every other capability needs requirements as data, not text. This is the single
parser so the frontmatter grammar is defined exactly once. It is deliberately
minimal — scalars and inline `[a, b]` lists only — to avoid a YAML dependency and
keep the tool stdlib-only. Files whose name starts with `_` (locks, generated map)
are not requirements and are skipped.

## Output
- A dict `id -> {meta, body, path}`. `meta` is the parsed frontmatter; `body` is the
  markdown after it; `id` falls back to the filename when absent from frontmatter.

## Acceptance (= tests)
- A file with valid frontmatter yields its scalar and list fields in `meta`.
- A trailing `# comment` on a frontmatter line is stripped from the value.
- A file without a leading `---` block returns empty `meta` and the whole text as body.
- Files starting with `_` are excluded from the result.

## Links
- Used by: (auto)
## Members in code (auto)
