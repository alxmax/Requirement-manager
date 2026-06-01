---
id: CORE-DRIFT-003
status: confirmed
layer: bus
owner: alex
depends_on: []
superseded_by:
---

# Contract hashing & lock

> Detect when a requirement's binding contract changes, so stale code can be re-checked.

## Input
- A requirement body (markdown) and the lock file `requirements/_reqlock.json`
  holding the last-known hash per requirement id.

## Description
Drift is the silent failure mode: someone edits a confirmed requirement and the
code that implements it is never revisited. To catch it without false alarms, the
hash covers only the *binding* sections (`Input`, `Output`, `Acceptance`) — not the
rationale, links or members, which can change freely. A hash mismatch on a
`confirmed` requirement is what the gate reports as drift.

## Output
- A 12-char content hash of the binding sections; read/write helpers for the lock file.

## Acceptance (= tests)
- Editing only the `Description` section does not change the hash.
- Editing the `Output` section changes the hash.
- `load_lock` on a missing lock file returns an empty dict (no crash).
- `save_lock` then `load_lock` round-trips the same mapping.

## Links
- Used by: (auto)
## Members in code (auto)
