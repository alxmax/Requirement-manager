---
id: REQ-NEW-004
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-PARSE-001]
superseded_by:
---

# Scaffold a requirement

> Create a new requirement file from the template, so every capability starts in the same shape.

## Input
- A capability id `AREA-NAME-NNN` (CLI argument). The scaffold is the engine's
  built-in template (an on-disk `templates/requirement.md` overrides it if present).

## Description
A consistent shape is what makes the registry scannable by both humans and the
parser. Rather than let people invent their own layout, `new` stamps the template
with the given id. It refuses to overwrite an existing file so a requirement is
never silently clobbered.

## Output
- A new `requirements/AREA-NAME-NNN.md` with the id substituted into the template.

## Acceptance (= tests)
- `new FOO-NEW-099` on an empty registry creates `requirements/FOO-NEW-099.md` with that id.
- Running `new` for an id that already exists exits non-zero and writes nothing.
- The created file matches the template with `AREA-NAME-NNN` replaced by the given id.

## Links
- Used by: (auto)
## Members in code (auto)
