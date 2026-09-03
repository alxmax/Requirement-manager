---
id: ARCH-PROMOTE-TODO-001
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.14
depends_on: [ARCH-NEW-004]
satisfies: [SYS-AUTHOR-101]
---

# Promote a TODO item into a requirement draft

## Description
> You plan features as checkbox items in `TODO.md`, grouped by milestone. When you decide to
> build one, you have to turn that line into a real requirement file with a contract and
> acceptance criteria. This command does the scaffolding step: it finds the TODO item, creates
> a requirement seeded with its name, milestone and lane, and (optionally) checks the item off —
> so the roadmap item and its requirement stay connected instead of being retyped by hand.

Every bullet below is binding.
- `new --from-todo` scaffolds a new draft requirement from an unfinished `TODO.md` item, seeded with its title, milestone and lane. [[REQ-PROMOTE-TODO-897]]
- `new --from-todo` refuses with a non-zero exit and writes no file when `--id` is absent, the id is taken, the name matches no open item, or the name is ambiguous. [[REQ-PROMOTE-TODO-898]]
- `new --from-todo` does not modify `TODO.md` by default; `--mark-done` checks off the matched item, best-effort. [[REQ-PROMOTE-TODO-899]]

## Cases
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

## Context
**Terms**
- an open item  a `TODO.md` line still checkboxed `[ ]`.
- a lane        the `lane:` label a TODO item carries, e.g. `ops`. It is a TODO
- grouping, not a requirement layer.
- headless      the engine never asks a question at the terminal, because it runs
- in CI and in git hooks where nobody is there to answer.

**Notes**
- Selection is by exact name within the unfinished items; rename a TODO to disambiguate rather
  than adding index syntax. Batch promotion and an undo command are intentionally out of scope.
- This is orthogonal to [[ARCH-PROMOTE-011]] (`confirm`, which lifts a baseline requirement to
  confirmed): this one creates a *new draft* from a TODO line.

**Current implementation**
- `cmd_promote_todo`, `_mark_todo_done` in `reqmap.py`; reuses `_parse_todos` (TODO.md parsing)
  and the `REQUIREMENT_TEMPLATE` scaffold ([[ARCH-NEW-004]]), dispatched from `main()` under
  `new --from-todo`.


--------------------


---
id: REQ-PROMOTE-TODO-897
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
---

# Scaffolding a draft from a matched TODO item

## Description
> `new --from-todo` turns a `TODO.md` checkbox line into a real requirement file, so a planned
> feature and its eventual contract stay one traceable thing instead of being retyped by hand.
> It requires an explicit `--id` rather than prompting, because the engine also runs headless
> in CI and git hooks.

Every bullet below is binding.
- `new --from-todo` scaffolds a new requirement file from an unfinished `TODO.md` item.
- The item is selected by exact name, trimmed and compared case-insensitively.
- `new --from-todo` requires an explicit `--id AREA-NAME-NNN`. There is no interactive
  prompt, because the engine runs headless.
- `new --from-todo` seeds the new requirement from the matched item: the title from the
  TODO name, `milestone:` from the item's `## vX.Y` section, `layer:` from the item's
  `lane:`.
- A `lane: ops` maps to `layer: feature`.
- The new requirement's status is `draft`, so the author reviews it and then promotes it.

## Cases
CASE-1 — new --from-todo scaffolds a requirement from an unfinished item
  Given  an unfinished TODO.md item named "Add export command"
  When   `new --from-todo "Add export command" --id REQ-X-001` runs
  Then   `requirements/REQ-X-001.md` is created

CASE-2 — matching is case-insensitive and trims whitespace
  Given  a TODO item named "Add Export Command"
  When   `new --from-todo "  add export command  " --id REQ-X-001` runs
  Then   the item is matched and the requirement is scaffolded

CASE-3 — the scaffolded requirement is seeded from the matched item
  Given  a TODO item "Add export command" under `## v2.0` with `lane: cli`
  When   `new --from-todo "Add export command" --id REQ-X-001` runs
  Then   the new file's title comes from the item name, `milestone: v2.0`, and `layer:` reflects
         the `cli` lane

CASE-4 — a lane of ops maps to layer feature
  Given  a TODO item with `lane: ops`
  When   the requirement is scaffolded from it
  Then   the new file's `layer:` reads `feature`

CASE-5 — a scaffolded requirement starts as draft
  Given  an unfinished TODO item
  When   `new --from-todo` scaffolds it
  Then   the new file's `status:` reads `draft`


--------------------


---
id: REQ-PROMOTE-TODO-898
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
---

# Refusing an unresolvable promotion

## Description
> A promotion that can't be pinned to exactly one TODO item and one free id must not silently
> guess. `new --from-todo` refuses outright — no partial requirement file, no half-checked
> `TODO.md` — whenever the id is missing or taken, or the name matches zero or more than one
> open item.

Every bullet below is binding.
- `new --from-todo` refuses with a non-zero exit and no file written when the `--id` is
  absent.
- The command refuses when the target id already exists.
- The command refuses when no open TODO matches the name.
- The command refuses when the name is ambiguous, meaning more than one open item
  matches.
- Each refusal prints a clear message. For a name with no match, that message lists the
  open items.

## Cases
CASE-1 — a missing --id refuses the command
  Given  an unfinished TODO item and no `--id` flag
  When   `new --from-todo "<name>"` runs
  Then   it exits non-zero and writes no requirement file, never prompting for the missing
         value — the engine runs headless

CASE-2 — an already-taken id refuses the command
  Given  `--id REQ-X-001` naming a file that already exists
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   it exits non-zero and the existing file is left unchanged

CASE-3 — an unmatched name refuses the command
  Given  a name matching no open TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   it exits non-zero and writes no requirement file

CASE-4 — an ambiguous name refuses the command
  Given  two open TODO items whose names both match the given name
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   it exits non-zero and writes no requirement file

CASE-5 — a no-match refusal lists the open items
  Given  a name matching no open TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   the printed error message lists the currently open TODO items


--------------------


---
id: REQ-PROMOTE-TODO-899
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-TODO-001]
---

# TODO.md stays untouched unless --mark-done asks otherwise

## Description
> Scaffolding a requirement and checking off its TODO item are two different intents, so the
> default run leaves `TODO.md` byte-identical and only `--mark-done` flips the checkbox. The
> flip is best-effort: a roadmap file the process cannot write to must not turn a successful
> scaffold into a failed command.

Every bullet below is binding.
- `new --from-todo` does not modify `TODO.md` by default.
- With `--mark-done` it flips the matched item's checkbox `[ ]` → `[x]`.
- That flip is best-effort: a write failure warns and does not fail the command.

## Cases
CASE-1 — scaffolding leaves TODO.md untouched by default
  Given  an unfinished TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs without `--mark-done`
  Then   `TODO.md` is byte-identical to before the run

CASE-2 — --mark-done checks off the matched item
  Given  an unfinished TODO item "Add export command"
  When   `new --from-todo "Add export command" --id REQ-X-001 --mark-done` runs
  Then   that line in `TODO.md` reads `- [x] Add export command`

CASE-3 — a TODO.md write failure warns but does not fail the command
  Given  `--mark-done` and a `TODO.md` the process cannot write to
  When   `new --from-todo "<name>" --id REQ-X-001 --mark-done` runs
  Then   it prints a warning, still exits zero, and the requirement file is still created

