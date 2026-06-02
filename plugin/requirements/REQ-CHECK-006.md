---
id: REQ-CHECK-006
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002, CORE-DRIFT-003]
superseded_by:
---

# The gate

> Fail the build when code and requirements have fallen out of sync.

## Input
- The loaded requirements, the discovered members, and the lock file.
- Optional `--update-lock` to rebaseline the drift hashes.

## Description
This is the one non-optional step, meant to run at commit/merge. It enforces the
invariants a human review would otherwise have to remember: no dangling tags, valid
status and layer, existing `depends_on` targets, and at least one `implements` for
any enforced (in-progress/implemented/confirmed) requirement. Drift is reported as
a warning, not an error, because a changed contract needs human attention, not a
hard block; the drift WARN names the member locations (`file:line`) to re-check so
it is actionable. Errors exit non-zero so CI stops; warnings do not.

## Output
- Printed `ERROR`/`WARN` lines plus a summary; exit code 1 if any error, else 0.

## Acceptance (= tests)
- A tag referencing a non-existent capability produces an `ERROR` and exit 1.
- A `confirmed` requirement with no `implements` member produces an `ERROR`.
- A `depends_on` pointing at a missing id produces an `ERROR`.
- A `confirmed` requirement whose binding hash differs from the lock produces a `WARN` (not an error) that names the member locations (`file:line`) to re-check.
- `--update-lock` writes the current hashes to `requirements/_reqlock.json`.

## Links
- Used by: (auto)
## Members in code (auto)
