---
id: ARCH-PROMOTE-TODO-001
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-NEW-004]
satisfies: [SYS-AUTHOR-101]
superseded_by:
milestone: v1.14
---

# Promote a TODO item into a requirement draft

## Description
> You plan features as checkbox items in `TODO.md`, grouped by milestone. When you decide to
> build one, you have to turn that line into a real requirement file with a contract and
> acceptance criteria. This command does the scaffolding step: it finds the TODO item, creates
> a requirement seeded with its name, milestone and lane, and (optionally) checks the item off —
> so the roadmap item and its requirement stay connected instead of being retyped by hand.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     an open item  a `TODO.md` line still checkboxed `[ ]`.
     a lane        the `lane:` label a TODO item carries, e.g. `ops`. It is a TODO
                   grouping, not a requirement layer.
     headless      the engine never asks a question at the terminal, because it runs
                   in CI and in git hooks where nobody is there to answer. -->

**What it scaffolds**
- `new --from-todo` scaffolds a new requirement file from an unfinished `TODO.md` item.
- The item is selected by exact name, trimmed and compared case-insensitively.
- `new --from-todo` requires an explicit `--id AREA-NAME-NNN`. There is no interactive
  prompt, because the engine runs headless.

**What it seeds**
- `new --from-todo` seeds the new requirement from the matched item: the title from the
  TODO name, `milestone:` from the item's `## vX.Y` section, `layer:` from the item's
  `lane:`.
- A `lane: ops` maps to `layer: feature`.
- The new requirement's status is `draft`, so the author reviews it and then promotes it.

**When it refuses**
- `new --from-todo` refuses with a non-zero exit and no file written when the `--id` is
  absent.
- The command refuses when the target id already exists.
- The command refuses when no open TODO matches the name.
- The command refuses when the name is ambiguous, meaning more than one open item
  matches.
- Each refusal prints a clear message. For a name with no match, that message lists the
  open items.

**What it does to `TODO.md`**
- `new --from-todo` does not modify `TODO.md` by default.
- With `--mark-done` it flips the matched item's checkbox `[ ]` → `[x]`.
- That flip is best-effort: a write failure warns and does not fail the command.

## Verify intent (open questions for the human)
- None — authored from known intent.

## Notes & known limitations (informative)
- Selection is by exact name within the unfinished items; rename a TODO to disambiguate rather
  than adding index syntax. Batch promotion and an undo command are intentionally out of scope.
- This is orthogonal to [[ARCH-PROMOTE-011]] (`confirm`, which lifts a baseline requirement to
  confirmed): this one creates a *new draft* from a TODO line.

## Cases (= tests)
CASE-1
  Given  an unfinished TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   `requirements/REQ-X-001.md` is created as a `draft` seeded with the item's title,
         milestone and layer, and `TODO.md` is left unchanged

CASE-2
  Given  a TODO `lane: ops`
  When   the requirement is scaffolded
  Then   its `layer:` is `feature`

CASE-3
  Given  `--mark-done`
  When   the command runs
  Then   the matched `TODO.md` line becomes `- [x] <name>` and no other line changes

CASE-4
  Given  a missing `--id`, an already-taken id, a name with no open match, or an ambiguous name
  When   the command runs
  Then   it exits non-zero and writes no requirement file

## WHERE — Current implementation
- `cmd_promote_todo`, `_mark_todo_done` in `reqmap.py`; reuses `_parse_todos` (TODO.md parsing)
  and the `REQUIREMENT_TEMPLATE` scaffold ([[ARCH-NEW-004]]), dispatched from `main()` under
  `new --from-todo`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-580
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# New --from-todo scaffolds a new requirement file from

> `new --from-todo` scaffolds a new requirement file from an unfinished `TODO.md` item.

Scenario: new --from-todo scaffolds a requirement from an unfinished item
  Given  an unfinished TODO.md item named "Add export command"
  When   `new --from-todo "Add export command" --id REQ-X-001` runs
  Then   `requirements/REQ-X-001.md` is created

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-581
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# The item is selected by exact name, trimmed

> The item is selected by exact name, trimmed and compared case-insensitively.

Scenario: matching is case-insensitive and trims whitespace
  Given  a TODO item named "Add Export Command"
  When   `new --from-todo "  add export command  " --id REQ-X-001` runs
  Then   the item is matched and the requirement is scaffolded

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-583
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# New --from-todo seeds the new requirement from the

> `new --from-todo` seeds the new requirement from the matched item: the title from the
> TODO name, `milestone:` from the item's `## vX.Y` section, `layer:` from the item's
> `lane:`.

Scenario: the scaffolded requirement is seeded from the matched item
  Given  a TODO item "Add export command" under `## v2.0` with `lane: cli`
  When   `new --from-todo "Add export command" --id REQ-X-001` runs
  Then   the new file's title comes from the item name, `milestone: v2.0`, and `layer:` reflects
         the `cli` lane

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-584
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# A lane: ops maps to layer: feature

> A `lane: ops` maps to `layer: feature`.

Scenario: a lane of ops maps to layer feature
  Given  a TODO item with `lane: ops`
  When   the requirement is scaffolded from it
  Then   the new file's `layer:` reads `feature`

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-585
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# The new requirement's status is draft, so the

> The new requirement's status is `draft`, so the author reviews it and then promotes it.

Scenario: a scaffolded requirement starts as draft
  Given  an unfinished TODO item
  When   `new --from-todo` scaffolds it
  Then   the new file's `status:` reads `draft`

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-586
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# New --from-todo refuses with a non-zero exit and

> `new --from-todo` refuses with a non-zero exit and no file written when the `--id` is
> absent.

Scenario: a missing --id refuses the command
  Given  an unfinished TODO item and no `--id` flag
  When   `new --from-todo "<name>"` runs
  Then   it exits non-zero and writes no requirement file, never prompting for the missing
         value — the engine runs headless

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-587
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# The command refuses when the target id already

> The command refuses when the target id already exists.

Scenario: an already-taken id refuses the command
  Given  `--id REQ-X-001` naming a file that already exists
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   it exits non-zero and the existing file is left unchanged

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-588
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# The command refuses when no open TODO matches

> The command refuses when no open TODO matches the name.

Scenario: an unmatched name refuses the command
  Given  a name matching no open TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   it exits non-zero and writes no requirement file

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-589
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# The command refuses when the name is ambiguous

> The command refuses when the name is ambiguous, meaning more than one open item matches.

Scenario: an ambiguous name refuses the command
  Given  two open TODO items whose names both match the given name
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   it exits non-zero and writes no requirement file

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-590
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# Each refusal prints a clear message. For a

> Each refusal prints a clear message. For a name with no match, that message lists the
> open items.

Scenario: a no-match refusal lists the open items
  Given  a name matching no open TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   the printed error message lists the currently open TODO items

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-591
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# New --from-todo does not modify TODO.md by default

> `new --from-todo` does not modify `TODO.md` by default.

Scenario: scaffolding leaves TODO.md untouched by default
  Given  an unfinished TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs without `--mark-done`
  Then   `TODO.md` is byte-identical to before the run

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-592
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# With --mark-done it flips the matched item's checkbox

> With `--mark-done` it flips the matched item's checkbox `[ ]` → `[x]`.

Scenario: --mark-done checks off the matched item
  Given  an unfinished TODO item "Add export command"
  When   `new --from-todo "Add export command" --id REQ-X-001 --mark-done` runs
  Then   that line in `TODO.md` reads `- [x] Add export command`

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-TODO-593
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
superseded_by:
---

# That flip is best-effort: a write failure warns

> That flip is best-effort: a write failure warns and does not fail the command.

Scenario: a TODO.md write failure warns but does not fail the command
  Given  `--mark-done` and a `TODO.md` the process cannot write to
  When   `new --from-todo "<name>" --id REQ-X-001 --mark-done` runs
  Then   it prints a warning, still exits zero, and the requirement file is still created

## Members in code (auto)
