# ADR-0092 — The worklist and the map name tagged tests that cannot fail

- **Status:** Accepted. Extends the worklist's test gaps (REQ-TESTGAPS-1088) and the map's
  `trace` block ([ADR-0091](0091-report-reads-an-audit.md)).
- **Decided:** 2026-11-22
- **Evidence:** a `# verifies: ID#CASE-N` tag closes its case whatever the test under it does,
  so every count downstream (`gate`, `next`, the map, the Report) calls the case tested. Read
  on this repository on 2026-11-22: 3 tagged tests compare an expression with itself
  (`assertEqual(f(x), f(x))`), each a determinism check run inside one process, where it passes
  for almost any `f`.

## Context

The engine knows where a test is, never what it checks. Two signals were tried on this
repository before deciding:

- **The shape of a test's assertions** (none, only a constant, only an expression against
  itself) is read from the test's own code with `ast` and found the 3 tests above. The only
  false positive was a script whose failure is its exit code (`scripts/test_cross_tool.py`,
  function `main`).
- **A requirement with no negative case**, read from assertion shape (`assertFalse`,
  `assertRaises`, an asserted empty result, a non-zero exit code), went from 58 requirements
  to 15 after one rule was added, and still named a test that feeds a broken corpus and
  asserts `code == 0`. Whether a case is negative depends on its input, which the assertion
  does not show.

## Decision

- **Only the first signal ships.** A Python function named `test*` that a `# verifies:` tag
  sits in or directly above is named when it asserts nothing, asserts only a constant, or
  only compares an expression with itself. A call to a same-file helper that asserts counts
  as an assertion.
- **What cannot be read is not judged:** a function not named `test*`, and every other
  language. A wrong name on the list costs more trust than a missing one.
- **Advice, never a verdict.** `next` prints a `Tests that cannot fail` bucket; `sync` writes
  the same list as `trace.vacuous`, outside the freshness comparison like the rest of
  `trace`; the Report counts it, lists it under Problem types and recommends a fix.

## Consequences

- `CORE_LOGICAL_BUDGET` rises from 7,058 to 7,129: `sync` writes the `trace` block, and
  `vacuoustests.py` is part of it.
- A map written before this has no `trace.vacuous`; the Report shows `not measured`.
- A consumer whose tests are not Python sees nothing new.

## Revisit when

- A consumer's tests in another language are read by `ast`-like means the engine already
  has (the C/C++ brace reader of ADR-0089): then the same three shapes apply there.
- The bucket names a test a reader judges sound, more than once in ten: then the rule that
  named it is removed, not tuned.
- A negative-case signal is proposed again: it needs the input of the case, not the shape of
  the assertion, and a measured false-positive rate.
