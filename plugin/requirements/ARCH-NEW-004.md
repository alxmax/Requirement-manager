---
id: ARCH-NEW-004
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-AUTHOR-101]
superseded_by:
milestone: v1.02
---

# Scaffold a requirement

## Description
> When you want to document a new capability, you need a fresh requirement file with all the right
> sections in place. This command stamps one out from a standard template, so every requirement starts
> in the same predictable shape instead of being hand-typed from memory. Without it, files drift into
> different layouts and the tools that read them start to break.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a capability id  an id of the shape `AREA-NAME-NNN`, e.g. `AUTH-LOGIN-001`.
     the scaffold     the template text a new requirement file is stamped out of. -->

- Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold
  with the placeholder `AREA-NAME-NNN` replaced by that id.
- `new` creates the requirements directory if it is absent.
- The scaffold is the engine's built-in template.
- An on-disk `templates/requirement.md`, when present, overrides the built-in template.
- `new` refuses to overwrite an existing file. It exits non-zero and writes nothing.
- The emitted Contract section opens with "Every bullet below is binding.", so the
  author writes clauses in present tense without a `shall` or `must` on each line.
- The scaffold's guidance names the authoring rules the linter enforces, so a file written
  from it starts clean.
- `new` warns, and still exits zero, when another requirement in the same area already uses
  the same `NNN` number. Ids stay unique by their full text; the warning keeps numbers
  unambiguous in conversation.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The built-in template is the single source of the new-requirement shape; no `templates/`
  directory is required for `new` to work.

## Cases (= tests)
CASE-1
  Given  an empty registry
  When   `new FOO-NEW-099` runs
  Then   `requirements/FOO-NEW-099.md` is created with that id

CASE-2
  Given  an id that already exists
  When   `new` runs for it
  Then   it exits non-zero and writes nothing

CASE-3
  Given  a file created by `new`
  When   it is compared to the template
  Then   it matches with `AREA-NAME-NNN` replaced by the given id

CASE-4
  Given  no on-disk template
  When   `new` runs
  Then   the built-in scaffold (Contract + Acceptance sections) is used

CASE-5
  Given  `ARCH-MAP-007.md` already in the registry
  When   `new ARCH-VIEWER-007` runs
  Then   the file is created, the exit code is 0, and a warning names `ARCH-MAP-007`

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana is about to document a new login feature. She runs `reqmap.py new AUTH-LOGIN-001` and a ready-to-fill `requirements/AUTH-LOGIN-001.md` appears, already carrying the Contract and Acceptance headings with her id filled in. When she accidentally runs the same command again, it refuses and writes nothing, so her half-finished work is never clobbered.

## WHERE — Current implementation
- `cmd_new` and `REQUIREMENT_TEMPLATE` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-NEW-519
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# Given a capability id, new writes requirements/<ID>.md, stamped

> Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold
> with the placeholder `AREA-NAME-NNN` replaced by that id.

Scenario: new stamps the scaffold with the given id
  Given  a template containing the placeholder `AREA-NAME-NNN`
  When   `new CORE-FOO-001` runs
  Then   `requirements/CORE-FOO-001.md` exists, contains "CORE-FOO-001", and no longer
         contains "AREA-NAME-NNN"

## Members in code (auto)




--------------------


---
id: REQ-NEW-520
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# New creates the requirements directory if it is

> `new` creates the requirements directory if it is absent.

Scenario: new creates a missing requirements directory
  Given  a `reqs_dir` path that does not exist yet
  When   `new CORE-FOO-001` runs
  Then   the directory is created and `requirements/CORE-FOO-001.md` is written inside it

## Members in code (auto)




--------------------


---
id: REQ-NEW-521
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# The scaffold is the engine's built-in template

> The scaffold is the engine's built-in template.

Scenario: new falls back to REQUIREMENT_TEMPLATE with no on-disk template
  Given  no `templates/requirement.md` on disk
  When   `new CORE-FOO-001` runs with `tmpl_path=None`
  Then   the written file carries the built-in scaffold's sections — "## Description",
         "## Cases", and "CASE-1"

## Members in code (auto)




--------------------


---
id: REQ-NEW-522
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# An on-disk templates/requirement.md, when present, overrides the built-in

> An on-disk `templates/requirement.md`, when present, overrides the built-in template.

Scenario: an on-disk template wins over the built-in scaffold
  Given  an on-disk template file distinct from `REQUIREMENT_TEMPLATE`
  When   `new CORE-FOO-001` runs with that template's path
  Then   the written file is stamped from the on-disk template's content, not the
         built-in one

## Members in code (auto)




--------------------


---
id: REQ-NEW-523
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# New refuses to overwrite an existing file. It

> `new` refuses to overwrite an existing file. It exits non-zero and writes nothing.

Scenario: new refuses to clobber an existing requirement file
  Given  `requirements/CORE-FOO-001.md` already exists with content "existing\n"
  When   `new CORE-FOO-001` runs
  Then   it exits non-zero and the file's content is unchanged

## Members in code (auto)




--------------------


---
id: REQ-NEW-524
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# The emitted Contract section opens with "Every line

> The emitted Contract section opens with "Every bullet below is binding.", so the
> author writes clauses in present tense without a `shall` or `must` on each line.

Scenario: the template's Description opens with the binding line and no modal verbs
  Given  `REQUIREMENT_TEMPLATE`, comments stripped
  When   its Description clauses are extracted with `_lint_prose`
  Then   the template contains "Every bullet below is binding." and no clause contains
         "shall" or "must"

## Members in code (auto)




--------------------


---
id: REQ-NEW-525
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# The scaffold's guidance names the authoring rules the

> The scaffold's guidance names the authoring rules the linter enforces, so a file written
> from it starts clean.

Scenario: the shipped template body passes its own linter
  Given  a requirement built from `REQUIREMENT_TEMPLATE`'s body, status `confirmed`
  When   `lint_requirement` runs on it
  Then   the findings carry no `anonymous-subject`, `statement-too-long`, or
         `statement-size` check

## Members in code (auto)




--------------------


---
id: REQ-NEW-526
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
superseded_by:
---

# New warns, and still exits zero, when another

> `new` warns, and still exits zero, when another requirement in the same area already
> uses the same `NNN` number. Ids stay unique by their full text; the warning keeps
> numbers unambiguous in conversation.

Scenario: a same-area number collision warns but still creates the file
  Given  `ARCH-MAP-007.md` already in the registry
  When   `new ARCH-VIEWER-007` runs
  Then   `ARCH-VIEWER-007.md` is created, the exit code is 0, and the output contains
         "WARN" naming "ARCH-MAP-007"

## Members in code (auto)
