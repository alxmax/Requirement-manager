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

## WHAT — Contract (normative)
- It shall report an `ERROR` and exit non-zero for any of: a code tag referencing a
  non-existent capability (dangling tag); an invalid `status` or `layer`; a `depends_on`
  pointing at a missing id; an enforced (`in-progress`/`implemented`/`confirmed`)
  requirement with no `implements:` member.
- It shall report drift as a `WARN` (never an error): a `confirmed` requirement whose
  binding hash differs from the lock, naming the member `file:line` locations to re-check.
- A `confirmed` requirement with no `tested-by:` member shall be a `WARN`.
- A present-but-unreadable `_reqlock.json` shall be a `WARN` (drift skipped, not a crash).
- It shall print an advisory line with the open verify-intent finding count when > 0,
  without affecting the exit code, and print a summary (requirements, members, errors, warnings).
- With `--update-lock` it shall write the current binding hashes to `requirements/_reqlock.json`.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Errors stop CI (exit 1); warnings do not. Intent sync (promote `baseline → confirmed`)
  is not automatable and surfaces at human review.

## HOW — Acceptance (= tests)
- A tag referencing a non-existent capability produces an `ERROR` and exit 1.
- A `confirmed` requirement with no `implements` member produces an `ERROR`.
- An invalid status or layer, and a `depends_on` pointing at a missing id, each produce an `ERROR`.
- A `confirmed` requirement whose binding hash differs from the lock produces a `WARN` (not an error) naming the member `file:line` locations.
- A present-but-corrupt lock file produces a `WARN` and does not change the exit code.
- `--update-lock` writes the current hashes to `requirements/_reqlock.json`.

## WHERE — Current implementation
- `cmd_check`, `warn_if_stale` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
