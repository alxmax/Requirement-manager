# ADR-0048 — The engine's floor is what it must keep, measured by capability

- **Status:** Accepted. Supersedes the second and third stages of
  [ADR-0046](0046-the-engine-has-a-line-budget.md) (≤ 12,500 and ≤ 8,000 lines). The metric,
  the release-time check and the rule that a budget moves down only with the cut that earns it
  all stand.
- **Decided:** 2026-09-22, the same day as ADR-0046. The maintainer set a constraint the
  stages had not accounted for: the ROADMAP stays. Measuring then showed both stages were
  unreachable.
- **Evidence:** `wc -l` per module of `plugin/scripts/reqmap.py` and
  `plugin/scripts/reqmap_engine/*.py` at v8.2.0, grouped by capability (below), and the
  package's module-level import graph.

## Context

ADR-0046 planned two further stages. Its second, ≤ 12,500, assumed release and planning would
leave the shipped engine together, about 1,039 lines. The maintainer then decided that the
ROADMAP (`ROADMAP.md`'s horizons, `_planning.json`, the Gantt, the shipped band and the plan
signals in `gate --risk` and `gate --audit`) stays. Without its plan readers, `sync --release`
alone is about 340 lines.

Its third stage, ≤ 8,000 by v9.0.0, was to come from decoupling: `gate`, `rules` and `init` would
stop importing authoring, search and release modules. Decoupling removes no line, because a
consumer vendors the whole package, every file of it. Lines leave only with modules.

The engine at v8.2.0, 13,372 lines, by capability:

| Lines | Capability | Standing |
|---:|---|---|
| 6,141 | Scan, tags, lock, gate, map, CLI | the product |
| 1,798 | `init`, drafting and the V-model pyramid | kept (ADR-0030) |
| 1,039 | Plan, ROADMAP and release | kept at the maintainer's direction |
| 325 | MCP server | kept (ADR-0043) |
| 1,166 | `gate --risk` / `--audit` (health, risk, audit) | removable |
| 1,001 | `clarify`, decompose, relevel | removable |
| 659 | `ask` search, dupes, review; `gate --show` | removable |
| 604 | Requirement readability lint | removable |
| 448 | `sync --retire` | removable |
| 191 | TODO parsing and status writes | removable |

The first four rows are **9,303 lines**. That is the floor while those four stay. It is above
8,000, so no amount of removal from the other six rows reaches ADR-0046's third stage.

## Decision

1. **The ≤ 12,500 and ≤ 8,000 stages are withdrawn.** Neither can be reached under the standing
   constraints. Keeping them would leave the budget promising what the code cannot do.
2. **The floor is 9,303 lines, and it moves only when a kept capability's standing changes.**
   Only a new record can take `init`'s drafting, the ROADMAP or MCP off the kept list.
3. **The next cut names a removable capability.** Each removal ships as its own change, with
   its ADR, its `sync --retire`, a one-release deprecation of any flag it owned, and
   `ENGINE_LINE_BUDGET` lowered to the measured result in the same commit.
4. **Decoupling is not a size step.** It is worth doing only as preparation for a removal,
   so that deleting a module cannot break `gate`.

## Consequences

- `ENGINE_LINE_BUDGET` stays at 13,550, the stage v8.2.0 reached. The engine is 13,372 lines.
- The ROADMAP's two stage items are replaced by one item: a removal waiting for the maintainer
  to name a capability.
- A reader of ADR-0046 who stops there sees stages that no longer exist. This record's
  status line is what tells them.

## Revisit when

- The maintainer names a removable capability. Measure it, cut it, and lower the budget.
- A kept capability's standing changes (the ROADMAP, MCP or `init`'s drafting). Re-measure
  the floor.
