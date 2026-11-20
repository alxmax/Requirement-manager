# ADR-0083 — A bug names the requirement it breaks

- **Status:** Accepted. Extends [ADR-0080](0080-known-bugs-are-listed-by-module.md) and
  [ADR-0082](0082-a-bug-leaves-the-list-into-a-register.md). ADR-0080's rule that an open bug
  adds no finding stands.
- **Decided:** 2026-11-20
- **Evidence:** a consumer's bug rows already wrote requirement ids in their `Source` cell, and
  nothing read them. `gate --show ID` said everything about a requirement except whether a known
  bug touched it.

## Context

The bug list is grouped by module, so it answers "what is broken in this part". A reader of one
requirement asks "is this one broken", and the link was there as text. The same feedback asked
for a warning on a confirmed requirement with an open P0 or P1.

## Decision

- **The id in the row is the link.** A bug names a requirement when the requirement's id is
  written whole in its title, where, why or source. No new column: a repository's existing rows
  already link, and a column would be one more thing `sync --bug` and the page must write.
- **Whole ids, and only ids of the corpus.** The row is split into word tokens (`[\w-]+`) and
  compared with the corpus's ids, so `X-10` does not name `X-1`, while `X-1#CASE-2` and
  `[[X-1]]` do. A token that is no requirement's id links to nothing.
- **Shown in three places, judged in none.** `_map.json` gives each bug `reqs`; `gate --show`
  lists the open bugs that name the requirement, and its `--json` carries them as `bugs`; the
  requirement's page lists them. Only open bugs: one in the register is not listed.
- **No warning for a confirmed requirement with an open bug.** ADR-0080 holds: the gate says
  whether the traces hold, and an open bug is work to do, not a broken trace. A team whose rule
  is "confirmed only with no open bugs" can read `bugs` from `gate --show --json`.
- **The logic is lazy.** `bugreqs.py` is imported at call time. The core grows only by the two
  call sites in `show.py`.

## Consequences

- `CORE_LOGICAL_BUDGET` rises from 6,810 to 6,814 for those call sites. `sync` and the gate do
  not load `bugreqs.py`.
- A bug that names a requirement in a way that is not its id, a title or a paraphrase, is not
  linked. The id is the only spelling the engine can check.
- Ids are matched with their case, so `x-1` does not name `X-1`.

## Revisit when

- A repository asks for the warning again with a rule it applies to every requirement: then it
  is a configured gate rule, in a record of its own.
- Bugs are found linked by a token that is an id by accident (a bug about `REQ-A-1` the word,
  not the requirement).
