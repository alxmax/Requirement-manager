---
id: REQ-PROMOTE-TODO-001
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-NEW-004]
superseded_by:
milestone: v1.14
---

# Promote a TODO item into a requirement draft

> You plan features as checkbox items in `TODO.md`, grouped by milestone. When you decide to
> build one, you have to turn that line into a real requirement file with a contract and
> acceptance criteria. This command does the scaffolding step: it finds the TODO item, creates
> a requirement seeded with its name, milestone and lane, and (optionally) checks the item off —
> so the roadmap item and its requirement stay connected instead of being retyped by hand.

## WHAT — Contract (normative)
Every line in this section is binding.
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes & known limitations (informative)
- Selection is by exact name within the unfinished items; rename a TODO to disambiguate rather
  than adding index syntax. Batch promotion and an undo command are intentionally out of scope.
- This is orthogonal to [[REQ-PROMOTE-011]] (`confirm`, which lifts a baseline requirement to
  confirmed): this one creates a *new draft* from a TODO line.

## HOW — Acceptance (= tests)
AC-1
  Given  an unfinished TODO item
  When   `new --from-todo "<name>" --id REQ-X-001` runs
  Then   `requirements/REQ-X-001.md` is created as a `draft` seeded with the item's title,
         milestone and layer, and `TODO.md` is left unchanged

AC-2
  Given  a TODO `lane: ops`
  When   the requirement is scaffolded
  Then   its `layer:` is `feature`

AC-3
  Given  `--mark-done`
  When   the command runs
  Then   the matched `TODO.md` line becomes `- [x] <name>` and no other line changes

AC-4
  Given  a missing `--id`, an already-taken id, a name with no open match, or an ambiguous name
  When   the command runs
  Then   it exits non-zero and writes no requirement file

## WHERE — Current implementation
- `cmd_promote_todo`, `_mark_todo_done` in `reqmap.py`; reuses `_parse_todos` (TODO.md parsing)
  and the `REQUIREMENT_TEMPLATE` scaffold ([[REQ-NEW-004]]), dispatched from `main()` under
  `new --from-todo`.

## Links
- Used by: (auto)
## Members in code (auto)
