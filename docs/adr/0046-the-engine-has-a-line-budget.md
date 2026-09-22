# ADR-0046 — The engine has a line budget, checked when a release is cut

- **Status:** Accepted. Supersedes [ADR-0014](0014-engine-stays-one-file.md)'s "no line-count
  gate" and brings forward the audit [ADR-0032](0032-the-eight-thousand-line-trigger-fired.md)
  scheduled for 2026-12-06: this record is that audit's decision on size.
- **Decided:** 2026-09-22, at the maintainer's direction ("reduce the engine from 14-15k lines
  toward 5,000"), after a costed review of what that number would require.
- **Evidence:** `wc -l plugin/scripts/reqmap.py plugin/scripts/reqmap_engine/*.py | tail -1`,
  per module, on 2026-09-22 (below).

## Context

ADR-0014 added no size gate and set a reopen trigger at 8,000 lines. ADR-0032 recorded that the
trigger fired at 10,202 lines and scheduled a costed audit rather than acting on the number.
The engine is now **14,910** lines across 61 files, with tests a further 14,549.

Two consumer repositories vendor it, and one has removed it. The cost it put on that one repo
came from the engine's size: 12,141 lines vendored to guard about 4,800 lines of code.

The owner asked for 5,000. Measured, 5,000 cannot be reached while the product keeps what it
exists for. Tag scan and link sync, drift against the lock, test links, the committed map, `init`
and the MCP server (a must-have, ADR-0043) are, with the modules they import, **6,000–8,250
lines** depending on how much of `init`'s drafting and pyramid is counted. The transitive import
closure of `gate` + `init` + the map is 46 modules and 11,214 lines today: `gate` imports
authoring modules, `rules` imports search and i18n, `init` imports release and site. The limit
is coupling, not any single large file. No module is over 500 lines.

## Decision

1. **One metric.** The count is `wc -l plugin/scripts/reqmap.py plugin/scripts/reqmap_engine/*.py
   | tail -1`: newlines over the CLI module and the package's modules, blank lines and comments
   included. `scripts/check_engine_budget.py` computes exactly that, and every CHANGELOG entry that
   quotes a size quotes that number.
2. **A budget, checked only when a release is cut.** CI runs the check inside the release step,
   after the "already released" exit. An over-budget engine blocks a new tag and never an
   ordinary commit or push. ADR-0014's reason for refusing a gate still holds for commits, where a
   size failure would block unrelated work. At release it does not: a release is the moment
   the size is shipped to consumers.
3. **The budget is the stage reached, lowered by the change that earns it.**
   `ENGINE_LINE_BUDGET` moves down in the same commit as the cut that pays for it. The stages,
   from measured module sizes:
   - **≤ 13,550**: design review, site generation and the i18n detector leave (ADR-0047).
   - **≤ 12,500**: `sync --release`'s bump and CHANGELOG writer leave the shipped engine for
     repo-only tooling. The plan readers stay while a consumer ships a `_planning.json`.
   - **≤ 8,000 by v9.0.0**: `gate`/`rules`/`init` stop importing authoring, search and release
     modules, so that what a consumer needs is what it carries.
4. **5,000 is a direction, not a gate.** It is not reachable while MCP and `init`'s drafting stay.
   Writing it as a budget would make the gate a promise the code cannot keep.

## Consequences

- The engine gets a size signal that fails where the cost lands (a release consumers
  install) and nowhere else.
- A budget can only move down with a cut, or up with a new record that says why. A quiet
  edit to the constant is a diff a reviewer sees.
- The ADR-0032 audit due 2026-12-06 is discharged by this record for size; its other question,
  whether advisory passes belong on the verdict path, is answered in part by ADR-0047.

## Revisit when

- A release is blocked by the budget and the cut that would unblock it removes something a
  consumer uses. Record that trade explicitly rather than raising the constant.
- The ≤ 8,000 stage lands, at which point the next stage is priced from the new module sizes.
