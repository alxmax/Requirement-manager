# ADR-0093 — C and C++ tests that cannot fail are named too

- **Status:** Accepted. Extends [ADR-0092](0092-tests-that-cannot-fail.md), which judged Python
  only, and reuses the brace reader of [ADR-0089](0089-c-and-cpp-definitions-key-member-drift.md).
- **Decided:** 2026-11-22
- **Evidence:** ADR-0090 made C and C++ tests visible to the trace (GoogleTest, Unity), and a
  C/C++ repository tags them with `// verifies:` the way a Python one does. Under ADR-0092 a
  `TEST` body that only runs the code, an `EXPECT_TRUE(true)` or an `EXPECT_EQ(f(x), f(x))`
  closed its case unnamed.

## Decision

- **The same three shapes, read from the same source of bodies.** `vacuouscpp.py` takes each
  test's body from `c_def_spans_text` (ADR-0089), with comments and literals blanked by
  `mask_c`, and reads the compared arguments from the source text at the same offsets, so a
  parenthesis in a string cannot split an argument and a macro named in a string is no
  assertion.
- **A test** is a block opened by a GoogleTest, Catch2 or CppUTest test macro, or a Unity
  `test*` function. **An assertion** is an `EXPECT_*`, `ASSERT_*`, `TEST_ASSERT*`, `REQUIRE*`,
  `CHECK*`, `*_EQUAL*`, `FAIL`/`ADD_FAILURE*` or `assert` call, a call to a same-file helper
  that asserts, or a call named like one (`check_*`, `expect_*`, `verify_*`), as in Python.
- **Loaded only when a tag sits outside Python**, so the reader stays out of what a
  Python-only repository loads; a file whose braces do not balance is skipped.

## Consequences

- `CORE_LOGICAL_BUDGET` rises from 7,129 to 7,132: the call into the C/C++ reader sits in
  `vacuoustests.py`, which `sync` loads. `vacuouscpp.py` itself is not core.
- The engine is 20,995 physical lines against the 21,000 ceiling. The next capability that
  adds lines needs a cut or a decision on the ceiling.
- A custom assertion macro defined in a header (not in the test file) and not named like an
  assertion is not seen, and its tests read as `no assertion`.

## Revisit when

- A C/C++ repository's bucket names a test whose assertion is a header macro, more than once in
  ten: then a repository declares its own assertion names in `_config.json`.
- The brace reader changes how it keys `TEST(...)` blocks: the test name shown here is read
  from the first line of the span and moves with it.
