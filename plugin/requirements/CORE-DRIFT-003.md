---
id: CORE-DRIFT-003
status: confirmed
layer: bus
owner: Alex
depends_on: []
superseded_by:
---

# Contract hashing & lock

> Detect when a requirement's binding contract changes, so stale code can be re-checked.

## WHAT — Contract (normative)
- It shall compute a stable 12-char hex content hash over only the NORMATIVE sections of a
  requirement body — the `Contract` and `Acceptance` headings (and, for back-compat, the
  legacy `Input`/`Output`/`Acceptance`) — so that rationale, notes, verify-intent, links
  and the member list may change without tripping drift.
- The hash shall be deterministic for identical normative content.
- It shall read and write the per-id hash baseline at `requirements/_reqlock.json`; a
  missing, empty, or unparseable lock shall load as an empty mapping (no crash).
- `save_lock` shall create the requirements directory if absent and write sorted, indented
  JSON so the lock file is diff-stable.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A heading is matched by substring, so any `## …` whose title contains "contract",
  "acceptan", "input" or "output" contributes to the hash.
- The lock distinguishes "absent" from "corrupt" only at the gate (`check` warns on a
  present-but-unreadable lock); `load_lock` itself fails open to `{}`.

## HOW — Acceptance (= tests)
- Editing only the Description/Notes section does not change the hash.
- Editing the Output (or Contract) section changes the hash.
- `load_lock` on a missing or corrupt lock file returns an empty dict (no crash).
- `save_lock` then `load_lock` round-trips the same mapping.

## WHERE — Current implementation
- `binding_hash`, `lock_path`, `load_lock`, `save_lock` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
