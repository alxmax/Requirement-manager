# ADR-0095 — The design candidates are cleared, and the core grows by the names it gained

- **Status:** Accepted.
- **Decided:** 2026-11-22
- **Evidence:** `sync`'s design record named 25 candidates in this repository (88% of 154 source
  files clean): files over 500 lines, lines over 120 columns, parameter lists over 6, functions
  over 80 lines, nesting over 4 levels and parameters travelling together. Fifteen were in the
  viewer, ten in the engine. After this change the record names none (158 of 158 clean), and
  `gate --risk` reads `Design pass-rate: 100%`.

## Decision

- **Each candidate is fixed by naming a step, not by an exemption.** A long function gives up its
  steps (`_sync_write_mode`, `after_passing_sync`, `_dispatch_clarify`, `_force_utf8` out of
  `reqmap.py`; `_apply_special` and `_coerce` out of `apply_config`); deep nesting becomes an
  early `continue` or a generator (`_bug_table_rows`, `_blocks`, `_source_problem`,
  `_dead_after_exit`); a long parameter list becomes the object its values already form (the
  Report's `ctx`, `QuestionPanel`'s `questions`, the Problems tab bar's `counts`,
  `_build_candidates`'s `index`, `_param`'s options); a long file is split where it already
  divides (`ReportSections.jsx`, `i18n.ro.js`, `smoke/plan-notes.jsx`, `synctail.py`).
- **Behaviour does not move.** Every user-visible string, flag and output stays; the suites pass
  unchanged except where a signature changed under a smoke check that calls it directly.
- **`after_passing_sync` leaves `reqmap.py`** for `reqmap_engine/synctail.py`: the CLI file holds
  the parser and the dispatch, and what a passing `sync` rebuilds is engine work.

## Consequences

- `CORE_LOGICAL_BUDGET` rises from 7,139 to 7,168: a named step costs its `def`, its docstring and
  its `return`. The physical total is 21,154 lines against the 23,000 ceiling.
- The design record is advice and stays advice: a new candidate does not fail the gate.

## Revisit when

- A candidate comes back in a file this change split: then the split was along the wrong seam,
  and the file needs a second look rather than a third helper.
