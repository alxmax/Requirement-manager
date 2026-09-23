# ADR-0052 — The line budget moves once, to the measured size

- **Status:** Accepted. Amends [ADR-0046](0046-the-engine-has-a-line-budget.md): its budget
  is raised once. Its staged targets (12,500, then 8,000 by v9.0.0) were already withdrawn by
  [ADR-0048](0048-the-engines-floor-is-what-it-must-keep.md). Nothing else changes.
- **Decided:** 2026-09-23, at the maintainer's direction, as a stop-gap. The alternative,
  cutting 3,203 lines, would undo the work that caused the overrun.
- **Evidence:** `python scripts/check_engine_budget.py` on 2026-09-23 reports 16,753 lines
  in 65 modules against a budget of 13,550.

## Context

ADR-0046 made the line count a release gate, and `scripts/test_check_engine_budget.py`
also checks it on every pull request. Four changes made on the same day took the engine
over the budget:

- **The design review and the site generator came back** ([ADR-0051](0051-the-oop-design-review-returns-to-the-engine.md)),
  about 900 lines.
- **All code was rewrapped from 100 to 80 columns**, about 1,300 lines with no change in
  behaviour.
- **Four modules over 500 lines were split in two**, adding a docstring and imports to each
  new module.
- **Every lint and test exemption was removed**, and the findings were fixed. Several
  functions had to be extracted to do it.

The same work made the gate faster. Median of 7 runs on this corpus: `gate --full` went
from 2.92s to 2.14s and `sync` from 4.94s to 4.40s. The gate no longer builds the design
record it strips before comparing, and string masking no longer walks every character.
Lines went up while every commit got cheaper. That is the case against lines as the only
measure.

## Decision

1. **`ENGINE_LINE_BUDGET` becomes 16,753**, the measured size, with no headroom. It is
   lowered only by a change that earns it, as ADR-0046 says.
2. **The 12,500 and 8,000 stages stay withdrawn**, as ADR-0048 decided. They were set
   against a count that now includes formatting.
3. **This is not the target metric.** A later record replaces it. The planned direction is:
   - a performance budget on the hook path, set from measured medians and report-only at
     first;
   - a budget on the modules `gate` and `sync` actually load, derived from the code rather
     than from a hand-written list;
   - counting logical lines, so rewrapping costs nothing.

## Consequences

- CI passes again without a version bump, and a release can be cut.
- The number can only go down from here until the replacement record lands. A change that
  adds lines must remove as many.

## Revisit when

- The record that replaces the metric lands. This one is then superseded.
