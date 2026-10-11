# ADR-0067 — The core budget rises for the adopt-path dispatch

- **Status:** Accepted. Amends the number in [ADR-0065](0065-the-viewer-ships-no-demo-data.md).
- **Decided:** 2026-10-11
- **Evidence:** `python scripts/check_engine_budget.py` on this commit: core 6,646 logical
  lines, physical total 17,788.

## Context

`init --watch` and `init --propose` have to be flags the parser and the registry know
about, and `main` has to dispatch them before it loads a workspace. Those statements sit
on the path `sync` and `gate --full` already import. The module that does the work,
`reqmap_engine/watch.py`, is imported only when a flag is used, so it is not part of the
6,646.

ADR-0053 set the budget at the measured core with no headroom. Six logical lines over
6,640 fail the release job.

## Decision

`CORE_LOGICAL_BUDGET` is 6,646, the core measured with the dispatch in place. The
physical ceiling stays 20,000.

## Consequences

- The next release job accepts this core. A later change that adds another statement on
  the gate path fails until the budget moves again, in the same commit, with a record.
- `watch.py` staying lazy is the reason the rise is six lines and not the size of the
  module.

## Revisit when

A cut on the gate path brings the measured core under 6,646. The budget drops in that
commit.
