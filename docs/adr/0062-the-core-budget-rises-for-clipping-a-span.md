# ADR-0062 — The core budget rises for clipping a span

- **Status:** Accepted. Amends the measured budget of
  [ADR-0061](0061-the-core-budget-rises-for-release-spans.md).
  The "moves down only" rule of
  [ADR-0046](0046-the-engine-has-a-line-budget.md) still holds for a cut.
- **Decided:** 2026-10-04, because a release with no tag was drawn inside
  the commit span of a later one, and the cut lives where `sync` builds
  the map.
- **Evidence:** `python scripts/check_engine_budget.py --budget 7000` on
  2026-10-04: the core is 6,677 logical lines in 61 modules, up from 6,661.
  The total is 17,479 physical lines, under the 20,000 ceiling.

## Context

A git span runs from the commit after the previous tag to this release's
tag. A changelog heading with no tag is only a date, so it never cuts
that span, and the later release is drawn across it. Stopping the span
at that date is a few statements in `history.py`. `sync` calls them on
every map, so a lazy import would hide the cost.

## Decision

**`CORE_LOGICAL_BUDGET` becomes 6,677, the measured core, with no headroom.**

- Not 7,000: that would leave lines nobody has earned.
- Not a lazy import: the clip is part of the span `sync` writes.

## Consequences

- `check_engine_budget.py` fails on one more logical line than today.
- ADR-0061's 6,661 is the previous stage, not the budget.

## Revisit when

- The next change needs core lines: write the record, measure, raise to
  that measure only.
- The clip leaves `sync`: lower the budget to the measured result in the
  same commit.
