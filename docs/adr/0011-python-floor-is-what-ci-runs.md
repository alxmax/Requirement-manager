# ADR-0011 — The Python floor is the oldest version CI runs

- **Status:** Accepted
- **Decided:** 2026-08-20 (`REQ-PYFLOOR-040`)
- **Evidence:** `CHANGELOG.md` `v2.19.0`; `MIN_PYTHON` in `reqmap.py`

## Context

The engine's pitch is "runs anywhere with Python", and the whole proof was one CI job on ubuntu
with `python-version: "3.x"`. The supported floor was therefore *accidental*: the code happened
to need only 3.7, so 3.7 was the implied answer. Meanwhile `-X utf8`, a convention that exists
specifically for Windows codepages, had never once run on Windows in CI.

A floor nothing tests is a claim, not a guarantee — the exact failure mode this project exists
to prevent, committed by the project itself.

## Decision

Declare **3.9**: not the oldest version the code tolerates, but the oldest version CI actually
runs. 3.7 and 3.8 cannot be installed on current GitHub runners, so promising them would be
untestable.

`MIN_PYTHON` in `reqmap.py` refuses an older interpreter before any command runs, with one
ASCII line naming the required version, the running version and the fix, and exit 2. A test
asserts `MIN_PYTHON` equals the oldest Python quoted in the CI matrix, so the two cannot drift
apart.

## Consequences

- Raising the floor means moving the matrix and the constant in one commit. The test makes
  either one alone fail the build.
- Users on 3.7/3.8 get a readable refusal instead of an `AttributeError` from deep inside a
  command — a better failure than the one they had, though still a refusal on an interpreter
  that would probably have worked.
- The check cannot help below 3.6: the module uses f-strings, so an older interpreter fails at
  compile time and never reaches it. That limit is written into the requirement's Notes rather
  than left as a surprise.
- The matrix that makes the floor real paid for itself immediately, exposing three defects a
  single ubuntu job structurally could not see — including `--since` failing **open** on
  Windows, reporting a clean tree that still contained a dangling tag.

## Revisit when

The oldest runner-installable Python moves. The rule survives the revisit: whatever CI runs is
what may be promised.
