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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a capability id  an id of the shape `AREA-NAME-NNN`, e.g. `AUTH-LOGIN-001`.
     the scaffold     the template text a new requirement file is stamped out of. -->

- Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold
  with the placeholder `AREA-NAME-NNN` replaced by that id.
- `new` creates the requirements directory if it is absent.
- The scaffold is the engine's built-in template.
- An on-disk `templates/requirement.md`, when present, overrides the built-in template.
- `new` refuses to overwrite an existing file. It exits non-zero and writes nothing.
- The emitted Contract section opens with "Every line in this section is binding.", so the
  author writes clauses in present tense without a `shall` or `must` on each line.
- The scaffold's guidance names the authoring rules the linter enforces, so a file written
  from it starts clean.
- `new` warns, and still exits zero, when another requirement in the same area already uses
  the same `NNN` number. Ids stay unique by their full text; the warning keeps numbers
  unambiguous in conversation.

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

AC-5
  Given  `REQ-MAP-007.md` already in the registry
  When   `new REQ-VIEWER-007` runs
  Then   the file is created, the exit code is 0, and a warning names `REQ-MAP-007`

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana is about to document a new login feature. She runs `reqmap.py new AUTH-LOGIN-001` and a ready-to-fill `requirements/AUTH-LOGIN-001.md` appears, already carrying the Contract and Acceptance headings with her id filled in. When she accidentally runs the same command again, it refuses and writes nothing, so her half-finished work is never clobbered.

## WHERE — Current implementation
- `cmd_new` and `REQUIREMENT_TEMPLATE` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
