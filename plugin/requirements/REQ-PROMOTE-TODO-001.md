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
- The `new --from-todo` command shall scaffold a new requirement file from an unfinished `TODO.md`
  item selected by exact name (trimmed, case-insensitive). It shall require an explicit
  `--id AREA-NAME-NNN`; there is no interactive prompt (the engine runs headless — CI, hooks).
- It shall seed the new requirement from the matched item: the title from the TODO name,
  `milestone:` from the item's `## vX.Y` section, and `layer:` from the item's `lane:` — where
  `lane: ops` maps to `feature` (ops is a TODO lane, not a requirement layer). The new
  requirement's status shall be `draft` (the author reviews, then promotes).
- It shall refuse (non-zero exit, no file written) when the `--id` is absent, the target id
  already exists, no open TODO matches the name, or the name is ambiguous (more than one open
  match) — printing a clear message (and, for no match, the list of open items).
- It shall not modify `TODO.md` by default. With `--mark-done` it shall flip the matched item's
  checkbox `[ ]` → `[x]` (best-effort: a write failure warns and does not fail the command).

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
