# ADR-0090 — C and C++ in an audit: tests, draft signals, stated values

- **Status:** Accepted. Builds on [ADR-0089](0089-c-and-cpp-definitions-key-member-drift.md),
  whose brace reader it reuses.
- **Decided:** 2026-11-21
- **Evidence:** a read-only audit of an existing C/C++ repository with its requirements in
  place. Its tests (GoogleTest, Unity) read as code, `init`'s drafts of its sources asked
  nothing specific because no parser read the language, and a value a requirement stated
  for a named constant had to be compared with the header by hand.

## Context

Three gaps showed in the same audit, all for the same reason: the engine reads Python
closely and every other language by file name. In C/C++:

- The test convention knew `test_*` and `tests/`, not `foo_test.cc`, `foo_unittest.cc`,
  `UnitTests/` or `FooTest.cpp`. A CamelCase `*Test` name cannot be added to the convention:
  embedded code keeps production self-tests in files like `RamTest.c`.
- A code draft's questions (ADR-0075's per-line signals) come from `ast`; a C file had none.
- Requirements in embedded work state values ("the debounce time is 20 ms"), and the code
  holds them as named constants. Nothing compared the two.

## Decision

- **A C/C++ file is a test by GoogleTest's names (`_test`, `_tests`, `_unittest`), by a test
  directory, or by the framework it includes** (GoogleTest/GoogleMock, CppUTest, Unity,
  Catch2, Boost.Test, cmocka, doctest), read in the first 16 KB wherever the caller has the
  path. `FooTest` pairs with `Foo` only when it includes a framework. A generic header name
  such as `check.h` is not on the list.
- **A C/C++ draft reads its signals inside each definition** of the ADR-0089 reader: a
  compared number other than 0, 1, 2, -1; a result cast to `(void)`; a statement after an
  exit on its own line that no `if`, `else` or `do` guards. Unbalanced braces are reported
  as not read, never as clean. `csignals.py` loads only for a C/C++ draft.
- **`RM038` compares a stated value with the code** under `gate --full` only. A claim needs a
  constant in backticks and an explicit connector (`is`, `=`, `:`, `equals`, `set to`, a
  parenthesis), and is compared only with that name's definitions in the requirement's own
  `implements:` files, by value (hex, thousands commas and C suffixes do not differ). It is
  language-neutral: a Python `NAME = 3` is a definition too. It reports and asks which side
  is right; it never decides.

## Consequences

- A C/C++ repository's tests count as tests for the untagged-file report, the design score
  and `init`, and `candidates` pairs them with their code.
- On this repository `RM038` finds nothing: its clauses name commands, not constants with
  values. A corpus that writes "`LIMIT` is 3" in prose about something other than the code's
  `LIMIT` would see a warning; the connector rule keeps that rare, and the bare gate never
  shows it.
- `CORE_LOGICAL_BUDGET` rises from 6,840 to 6,932 for `specvalues.py` (a gate rule is core by
  definition), the test-framework check in `tags.py` and the pairing in `candidates.py`.
  `csignals.py` stays lazy. The physical total is 20,583, under its 21,000 ceiling.

## Revisit when

- `RM038` is read on a corpus and more than one in five warnings is not a real disagreement:
  then the claim grammar narrows, or the rule moves to `gate --audit` only.
- A C/C++ test framework is missing from the list: it is added with a test.
