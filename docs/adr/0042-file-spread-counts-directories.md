# ADR-0042 — `file-spread` counts directories, not files

- **Status:** Accepted. Changes the unit of the `file-spread` readability check
  (`REQ-LINTCHECKS-866`); the threshold `LINT_FILE_SPREAD_MAX` and its default of 3 are unchanged.
- **Decided:** 2026-09-16, while clearing the corpus's readability warnings at the maintainer's
  direction.
- **Evidence:** on this corpus, counting distinct files gave 38 `file-spread` warnings; counting
  the distinct directories of the same `implements` members gives 3.

## Context

`file-spread` was written to catch a capability smeared across the codebase: a requirement whose
`implements` members sit in many places is hard to read as one thing. It counted distinct files,
and it was calibrated when the engine was a single `reqmap.py`, where three files meant three
genuinely different places.

ADR-0035 made the engine a package of one module per capability. A behaviour is now computed in
its own module, reported by `audit` or `health`, and exported by `mapjson` — three files in one
directory, by design. Of the 38 warnings, 35 were that shape: the check was measuring the package
layout, not diffusion, and a warning that fires on the intended structure teaches a reader to
ignore it.

## Decision

`file-spread` counts the distinct directories of a requirement's `implements` members. Files in
one directory are one place to read. The remaining three warnings on this corpus each cross the
engine and two areas of the viewer, which is the diffusion the check exists to name; they are
judged one by one.

## Consequences

- A consumer with a flat layout sees fewer warnings; one whose code for a single requirement
  crosses directories sees the same ones.
- The key keeps its name, `LINT_FILE_SPREAD_MAX`, so an existing `_config.json` override still
  applies; its comment says the unit changed.

## Revisit when

- A requirement's members sit in one directory that holds unrelated code (a flat `src/`), and a
  diffuse requirement goes unreported because of it.
