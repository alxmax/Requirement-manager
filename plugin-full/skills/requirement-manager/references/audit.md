# Audit session (`sync --audit-plan`)

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here. The design is
ADR-0076.

An audit asks of a repository that is already traced: of what a reviewer looked at, what
was really wrong, and how sure we are. The session lives in one committed file,
`requirements/_audit.json`.

## The steps

1. **Plan, once.** A person runs `sync --audit-plan` (`--ranked N`, `--random N`,
   `--seed S`; defaults 25, 25 and today as `YYYYMMDD`). It writes the ranked set, the
   seeded random set and the decision bands, and never replaces an existing file.
2. **Review, twice.** For each planned id, one fresh conversation per run: read the
   dossier (`reqmap_review(id)` or `reqmap_show(id)`), open the files it names, and answer
   the prompt below. Add one finding per clause to `findings`.
3. **Decide.** A person adds one decision per finding to `decisions`. An `ok` nobody
   contradicts needs none.
4. **Report.** `gate --audit` (or `reqmap_audit`) prints every rate as k/n with its 95%
   interval and the band. `sync` puts the same block in `_map.html`, under Audit.

## The prompt

> For each clause of this requirement: show the line of code that does it and the test
> that proves it. Say where the code does something other than the clause, where there is
> no code for it, and where the test does not actually check the case. Give every finding
> exactly one label: bug, not-implemented, false-coverage, or ok when the clause holds.

`reqmap_review` carries the same text under `audit.prompt` while a session is open.

## The record

```json
{"findings":  [{"id": "AREA-NAME-001", "run": 1, "label": "bug", "clause": 2,
                "note": "a reading of NaN leaves the output off"}],
 "decisions": [{"id": "AREA-NAME-001", "clause": 2, "counter": "B", "by": "reviewer"}]}
```

- `label`: `bug`, `not-implemented`, `false-coverage`, `ok`. `clause`: the clause number,
  or `null` for the whole requirement.
- `counter`: `B` real bug, `F_copilot` not a bug, `G` gap (correct but unproven), `A` the
  requirement is ambiguous, `F_tool` a tool question that was not real, `M` a bug behind an
  `ok` (random set), `U` is set by the engine when two runs disagree.
- A malformed entry is reported as `INPUT:audit` and not counted; the engine never edits
  the file.

## Rules for the assistant

- Never edit a requirement or its `status:`; never write `decisions`.
- One requirement per conversation, and two runs each, the second in a new conversation.
- Use only the four labels. A verdict you are unsure of is `ok` with a note, not a guess.
- The server stays read-only. Run `sync` in the terminal only when asked to refresh the map.
