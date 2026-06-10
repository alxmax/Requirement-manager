---
id: REQ-NEW-004
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.02
---

# Scaffold a requirement

> When you want to document a new capability, you need a fresh requirement file with all the right
> sections in place. This command stamps one out from a standard template, so every requirement starts
> in the same predictable shape instead of being hand-typed from memory. Without it, files drift into
> different layouts and the tools that read them start to break.

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
AC-1
  Given  an empty registry
  When   `new FOO-NEW-099` runs
  Then   `requirements/FOO-NEW-099.md` is created with that id

AC-2
  Given  an id that already exists
  When   `new` runs for it
  Then   it exits non-zero and writes nothing

AC-3
  Given  a file created by `new`
  When   it is compared to the template
  Then   it matches with `AREA-NAME-NNN` replaced by the given id

AC-4
  Given  no on-disk template
  When   `new` runs
  Then   the built-in scaffold (Contract + Acceptance sections) is used

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana is about to document a new login feature. She runs `reqmap.py new AUTH-LOGIN-001` and a ready-to-fill `requirements/AUTH-LOGIN-001.md` appears, already carrying the Contract and Acceptance headings with her id filled in. When she accidentally runs the same command again, it refuses and writes nothing, so her half-finished work is never clobbered.

## WHERE — Current implementation
- `cmd_new` and `REQUIREMENT_TEMPLATE` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
