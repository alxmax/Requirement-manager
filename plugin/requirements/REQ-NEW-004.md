---
id: REQ-NEW-004
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
---

# Scaffold a requirement

> Create a new requirement file from the template, so every capability starts in the same shape.

## WHAT — Contract (normative)
- Given a capability id `AREA-NAME-NNN`, it shall write `requirements/<ID>.md` stamped from
  a template with `AREA-NAME-NNN` replaced by the given id, creating the directory if absent.
- The scaffold shall be the engine's built-in template; an on-disk `templates/requirement.md`,
  when present, shall override it.
- It shall refuse to overwrite an existing file (exit non-zero, write nothing).

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The built-in template is the single source of the new-requirement shape; no `templates/`
  directory is required for `new` to work.

## HOW — Acceptance (= tests)
- `new FOO-NEW-099` on an empty registry creates `requirements/FOO-NEW-099.md` with that id.
- Running `new` for an id that already exists exits non-zero and writes nothing.
- The created file matches the template with `AREA-NAME-NNN` replaced by the given id.
- With no on-disk template, the built-in scaffold (Contract + Acceptance sections) is used.

## WHERE — Current implementation
- `cmd_new` and `REQUIREMENT_TEMPLATE` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
