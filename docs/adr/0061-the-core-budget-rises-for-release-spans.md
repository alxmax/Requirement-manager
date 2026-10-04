# ADR-0061 — The core budget rises for release commit spans

- **Status:** Accepted. Amends the measured budget of
  [ADR-0060](0060-the-core-budget-rises-once-for-the-question-checks.md).
  The "moves down only" rule of
  [ADR-0046](0046-the-engine-has-a-line-budget.md) still holds for a cut.
- **Decided:** 2026-10-04, because the Plan has to know when a release was
  worked on, and that reading happens while `sync` builds the map.
- **Evidence:** `python scripts/check_engine_budget.py --budget 7000` on
  2026-10-04: the core is 6,661 logical lines in 61 modules, up from 6,612.
  The total is 17,440 physical lines, under the 20,000 ceiling. ADR-0060
  left 7,000 as a ceiling for the next record, not as headroom.

## Context

A shipped release on the Plan is one block, from its first commit to its
last. Those dates come from the tag history, read while `sync` builds
`history`, so the function lives in `history.py` and the core counts it.
A lazy import would hide the cost: `sync` calls it on every map.

## Decision

**`CORE_LOGICAL_BUDGET` becomes 6,661, the measured core, with no headroom.**

- Not 7,000: that would leave 339 lines nobody has earned.
- Not a lazy import: the spans are part of the map `sync` writes.

## Consequences

- `check_engine_budget.py` fails on one more logical line than today.
- The 7,000 ceiling from ADR-0060 is still only a ceiling.

## Revisit when

- The next change needs core lines: write the record, measure, raise to
  that measure only.
- The span reading leaves `sync`: lower the budget to the measured result
  in the same commit.
