---
id: ARCH-NEW-004
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.02
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-AUTHOR-101]
---

# Scaffold a requirement

## Description
> When you want to document a new capability, you need a fresh requirement file with all the right
> sections in place. This command stamps one out from a standard template, so every requirement starts
> in the same predictable shape instead of being hand-typed from memory. Without it, files drift into
> different layouts and the tools that read them start to break.

Every bullet below is binding.
- Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold (an on-disk `templates/requirement.md` if present, else the built-in template) with the placeholder `AREA-NAME-NNN` replaced by that id, creating the requirements directory if needed. [[REQ-NEW-881]]
- `new` refuses to overwrite an existing file, exiting non-zero and writing nothing; it warns but still succeeds on a same-area number collision, and its scaffold is pre-shaped to pass the linter's own authoring rules. [[REQ-NEW-882]]

## Cases
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

## Context
**Terms**
- a capability id  an id of the shape `AREA-NAME-NNN`, e.g. `AUTH-LOGIN-001`.
- the scaffold     the template text a new requirement file is stamped out of.

**Notes**
- The built-in template is the single source of the new-requirement shape; no `templates/`
  directory is required for `new` to work.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana is about to document a new login feature. She runs `reqmap.py new AUTH-LOGIN-001` and a ready-to-fill `requirements/AUTH-LOGIN-001.md` appears, already carrying the Contract and Acceptance headings with her id filled in. When she accidentally runs the same command again, it refuses and writes nothing, so her half-finished work is never clobbered.

**Current implementation**
- `cmd_new` and `REQUIREMENT_TEMPLATE` in `reqmap.py`.


--------------------


---
id: REQ-NEW-881
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
---

# Stamping a fresh requirement file from a template

## Description
> A hand-typed requirement file drifts into its own layout, and the tools that read
> requirements start to break on it. `new` stamps `requirements/<ID>.md` from a template —
> the built-in one, or an on-disk `templates/requirement.md` when a repo wants to customize
> it — with the id placeholder filled in, so every requirement starts in the same
> predictable shape.

Every bullet below is binding.
- Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold
  with the placeholder `AREA-NAME-NNN` replaced by that id.
- `new` creates the requirements directory if it is absent.
- The scaffold is the engine's built-in template.
- An on-disk `templates/requirement.md`, when present, overrides the built-in template.

## Cases
CASE-1 — new stamps the scaffold with the given id
  Given  a template containing the placeholder `AREA-NAME-NNN`
  When   `new CORE-FOO-001` runs
  Then   `requirements/CORE-FOO-001.md` exists, contains "CORE-FOO-001", and no longer
         contains "AREA-NAME-NNN"

CASE-2 — new creates a missing requirements directory
  Given  a `reqs_dir` path that does not exist yet
  When   `new CORE-FOO-001` runs
  Then   the directory is created and `requirements/CORE-FOO-001.md` is written inside it

CASE-3 — new falls back to REQUIREMENT_TEMPLATE with no on-disk template
  Given  no `templates/requirement.md` on disk
  When   `new CORE-FOO-001` runs with `tmpl_path=None`
  Then   the written file carries the built-in scaffold's sections — "## Description",
         "## Cases", and "CASE-1"

CASE-4 — an on-disk template wins over the built-in scaffold
  Given  an on-disk template file distinct from `REQUIREMENT_TEMPLATE`
  When   `new CORE-FOO-001` runs with that template's path
  Then   the written file is stamped from the on-disk template's content, not the
         built-in one


--------------------


---
id: REQ-NEW-882
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-NEW-004]
---

# Refusing to clobber, and a scaffold that lints clean

## Description
> Running `new` twice by accident must never destroy half-finished work, so an existing file
> is left untouched and the command exits non-zero instead. A same-area number collision is
> a softer problem — ids stay unique by their full text, so it only warns — and the scaffold
> itself is written to already satisfy the linter's authoring rules, so a file built from it
> starts clean rather than immediately flagged.

Every bullet below is binding.
- `new` refuses to overwrite an existing file. It exits non-zero and writes nothing.
- The emitted Contract section opens with "Every bullet below is binding.", so the
  author writes clauses in present tense without a `shall` or `must` on each line.
- The scaffold's guidance names the authoring rules the linter enforces, so a file written
  from it starts clean.
- `new` warns, and still exits zero, when another requirement in the same area already uses
  the same `NNN` number. Ids stay unique by their full text; the warning keeps numbers
  unambiguous in conversation.

## Cases
CASE-1 — new refuses to clobber an existing requirement file
  Given  `requirements/CORE-FOO-001.md` already exists with content "existing\n"
  When   `new CORE-FOO-001` runs
  Then   it exits non-zero and the file's content is unchanged

CASE-2 — the template's Description opens with the binding line and no modal verbs
  Given  `REQUIREMENT_TEMPLATE`, comments stripped
  When   its Description clauses are extracted with `_lint_prose`
  Then   the template contains "Every bullet below is binding." and no clause contains
         "shall" or "must"

CASE-3 — the shipped template body passes its own linter
  Given  a requirement built from `REQUIREMENT_TEMPLATE`'s body, status `confirmed`
  When   `lint_requirement` runs on it
  Then   the findings carry no `anonymous-subject`, `statement-too-long`, or
         `statement-size` check

CASE-4 — a same-area number collision warns but still creates the file
  Given  `ARCH-MAP-007.md` already in the registry
  When   `new ARCH-VIEWER-007` runs
  Then   `ARCH-VIEWER-007.md` is created, the exit code is 0, and the output contains
         "WARN" naming "ARCH-MAP-007"

