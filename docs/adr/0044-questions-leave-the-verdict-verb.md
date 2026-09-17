# ADR-0044 — Questions leave the verdict verb: `ask`

- **Status:** Accepted. **Supersedes** three decisions of
  [ADR-0037](0037-the-command-surface-is-already-five-the-cut-is-one-mode-per-release.md), each
  only as far as named here:
  - **decision 2**, for the *spelling* of `--search`, `--dupes`, `--design` and `--i18n` under
    `gate`. The capabilities stay KEEP: no module, requirement or behaviour is retired.
  - **decision 4**, "one mode per release": five modes move in one release, because a move
    deletes nothing and the blast radius ADR-0037 ordered by was deleted lines.
  - **decision 6**, for `--review` only: it moves to `ask`, it is not retired, and the
    `requirement-quality-review` skill moves with it in the same release.
  ADR-0037 and ADR-0043 are not edited.
- **Decided:** 2026-09-17, at the maintainer's choice among three options (a new verb, the
  modes under `clarify`, helper flags folded into values), then audited by nine senators
  (`2026-09-17_081414-senate-reqmap-cli-surface-gate-flags-to-9`, all seats on Opus, one round,
  verdict **MODIFY**, GO 3 / MODIFY 6 / STOP 0). Every condition below is theirs.
- **Evidence:** `COMMANDS` on `989714a` — `gate` 16 params, all verbs 37. ROADMAP.md `Next`:
  "`gate` ≤ 12 flag-uri. Audit / risk / show rămân; restul coboară din calea verdictului".

## Context

ADR-0037 refiled the cognitive-surface problem — "five verbs carrying 36 flags, 17 on `gate`" —
as its own item with a numeric ceiling. ADR-0043 then named the same problem from the agent's
side: "an agent choosing between sixteen `gate` flags from prose". The ROADMAP item set the
ceiling at 12 and named what stays.

`gate` is two things under one name: the commit verdict every hook and CI job runs, and every
read-only question the engine can answer. Of its 16 flags, 7 have nothing to do with the
verdict: five question modes (`--search`, `--dupes`, `--design`, `--review`, `--i18n`) and two
helpers that only mean something beside them (`--top`, `--threshold`).

## Decision

1. **A seventh verb, `ask`, owns the questions.** `ask` takes `--search QUERY`, `--dupes`,
   `--design`, `--review [ID]`, `--i18n`, `--top N`, `--threshold X` and `--json`. `gate` keeps
   `--audit --risk --show --all --untagged --badge --strict --json --since`. The ceiling is a
   test, not a sentence: `len(COMMANDS["gate"]["params"]) == 9`. `--all` is read with `--risk`
   only. `ask --review` with no id plans the whole corpus, which is what `cmd_review` and the
   skill always said and the `gate` dispatch refused.
2. **This is a design choice, not a line cut.** The registry grows from 37 flags to 38, because
   `--json` now appears on both verbs. What falls is the number a reader of `gate` has to hold.
3. **The old spellings are an alias for exactly v7.22.x.** `gate --search` and the other six
   run the same function as `ask --search`: exit code and stdout byte-identical, with exactly
   one migration line on **stderr** — never stdout, where it would break `--json` for every
   parser, the MCP server's included. In v8.0.0 the alias goes, and `gate` with a moved flag
   exits 2 with one line pointing at `ask`. It never falls through to a silent verdict run.
4. **`ask` checks its flags against its verb.** A verdict flag on `ask` (`--strict`, `--risk`,
   `--since`, …) exits 2 with one line, and so does `ask` with no mode. The parser stays flat;
   the check reads the registry.
5. **Everything that names the old spellings moves in the same change**: the MCP tools' argv
   (a parity test fails on any tool pairing `gate` with a moved flag), the retired-name guard
   (it now knows verb-scoped moves, so an instruction still naming `gate --search` fails CI
   today, not in v8.0.0), both skills, the engine's printed hints, the viewer, and the
   requirement contracts, with drift accepted. The `requirement-quality-review` skill uses `ask
   --review` and says what to run on an engine vendored before v7.22.0.

## Consequences

- Seven verbs where ADR-0037 counted five. `mcp` (ADR-0043) was the sixth; `ask` is the first
  added to reduce what a verb means rather than to add a capability.
- The CHANGELOG entry for `v7.22.0` names the seven moved flags and v8.0.0 as their removal
  release; that line is the condition, per ADR-0037's note that conditions ride on CHANGELOG
  lines rather than checkboxes.
- The `_planning.json` bar that did this work is the only one moving `--design`; the health bar
  loses its "design review off the verdict path" clause.

## Revisit when

- v8.0.0 is cut: the alias and its test are removed together, and `gate --search` is asserted
  to exit 2.
- A caller outside this repo is found still using a `gate` spelling after v8.0.0 — then the
  alias window was too short, and the next move gets two releases.
- `len(COMMANDS["gate"]["params"])` passes 12 again.
