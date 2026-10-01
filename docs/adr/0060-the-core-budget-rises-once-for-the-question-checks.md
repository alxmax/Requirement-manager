# ADR-0060 — The core budget rises once, for the question checks

- **Status:** Accepted. Amends decision 1 of
  [ADR-0053](0053-the-budget-measures-the-core-in-logical-lines.md), and the "moves down only"
  rule of [ADR-0046](0046-the-engine-has-a-line-budget.md), for this one raise.
- **Decided:** 2026-10-01, at the maintainer's direction.
- **Evidence:** `python scripts/check_engine_budget.py --budget 7000` on 2026-10-01: the core
  is 6,612 logical lines in 61 modules, up from 6,533; the total is 17,349 physical lines,
  under the 20,000 ceiling. The maintainer authorised a raise up to 7,000.

## Context

[ADR-0059](0059-a-decision-question-is-linted-for-whoever-answers-it.md) adds a lint module
that `lint_requirement` calls, so `sync` and `gate --full` load it and the core counts it. The
budget was set to the measured core with no headroom (ADR-0053), and a budget moves down only
with the cut that earns it (ADR-0046). A change that adds behaviour to the gate has no cut to
point at.

The lazy import (as `plandrift` and `release` have) does not fit: the checks run inside the
gate, so a lazy module would stay out of the count while still running on every gate.

## Decision

**`CORE_LOGICAL_BUDGET` becomes 6,612, the measured core, with no headroom.**

- Not 7,000: that would leave 388 lines of headroom nobody has earned, and the next addition
  would pass without a record.
- Not a lazy import: it would hide the cost from the count and not from the gate.
- A later raise needs its own record, with its own measurement.

## Consequences

- `check_engine_budget.py` fails on one more logical line than today, as before.
- The 7,000 the maintainer authorised is a ceiling for the next record, not a budget.

## Revisit when

- The next change needs core lines: write the record, measure, raise to that measure only.
- A check from ADR-0059 is removed: lower the budget to the measured result in the same commit.
- The core approaches 7,000: cut first, then ask.
