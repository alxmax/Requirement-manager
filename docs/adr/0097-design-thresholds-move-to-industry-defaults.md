# ADR-0097 — The design thresholds move: seven parameters, five levels, a file warned at 750 and told to split at 1000

- **Status:** Accepted. Supersedes the `DESIGN_FILE_MAX_LINES = 500` of
  [ADR-0056](0056-the-design-review-line-limit-is-120-columns.md) and the parameter and nesting
  defaults [ADR-0051](0051-the-oop-design-review-returns-to-the-engine.md) shipped; the rest of
  both records stands, and the review stays advice.
- **Decided:** 2026-11-28
- **Evidence:** on 2026-11-27 `ask --design` named 10 candidates in 9 of 166 files, all added on
  2026-11-26/27 after [ADR-0095](0095-the-design-candidates-are-cleared.md) had cleared them. Two
  were `app/scripts/smoke/*.jsx`, which are tests (`tested-by: ARCH-VIEWER-007`) the walk took for
  production code. The rest overshot by little: 508 and 512 lines against 500, 7 parameters
  against 6, 91 lines against 80. Over the 157 production files, 36 were over 300 lines, 19 over
  400, 2 over 500 and none over 1000.

## Context

The maintainer asked whether the rules were too strict. Against common linter defaults, as
recalled rather than re-read for this record: pylint allows 5 parameters, 5 nested blocks and
1000-line modules; ESLint 3 parameters, depth 4 and 300 lines; SwiftLint warns at 5 parameters
and 400 lines and errors at 8 and 1000; SonarQube allows 7 parameters, depth 3 and 1000 lines.
Google's style guides fix line width through a formatter and leave function and file size to
review. The old defaults sat inside that range; the maintainer chose the looser end for
parameters and nesting, and two tiers for file length.

## Decision

1. `DESIGN_PARAMS_MAX` is 7 (a list of 8 is a candidate) and `DESIGN_NESTING_MAX` is 5.
2. `DESIGN_FILE_MAX_LINES` is 750: a longer file is a `file-too-long` candidate.
   `DESIGN_FILE_SPLIT_LINES` is 1000: a file past it is one `file-must-split` candidate instead,
   naming 1000. Both stay advice: neither enters the gate (REQ-DESIGN-953).
3. A `smoke/` directory segment is test code, like `tests/` and `e2e/` (REQ-CANDIDATES-827), so
   the review, candidates and every other test-path reader skip it.
4. This repository's own engine shape is checked, not only advised: a test reads the limits
   `CLAUDE.md` states (no file over 1000 lines, no line over 100 columns) and fails on a file of
   `reqmap.py` or `reqmap_engine/` past them (REQ-SELFGATE-990 CASE-6).

## Consequences

- A consumer's design score can only rise: every changed default is looser.
- The remaining candidates here were fixed by naming a step, as ADR-0095 did: two wrapped
  translation lines per file, `BugChart`'s legend and week targets as components, and
  `_duplicate_meta` taking the ids `cmd_bug_fix` already read. The review reads 0 candidates
  over 155 files.

## Revisit when

- A consumer reports a 750–1000-line file its reviewers consider whole, or a shorter one they
  wanted flagged.
- A `smoke/` directory turns up holding production code in a consumer repository.
