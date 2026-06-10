---
id: CORE-DRIFT-003
status: confirmed
layer: bus
owner: Alex
depends_on: []
superseded_by:
milestone: v1.00
---

# Contract hashing & lock

> A requirement file has a "binding" part — the precise promise of what the code must do.
> This takes a tiny fingerprint of just that part and remembers it. The next time anyone
> runs the tool, it can tell whether that promise changed since the code was last checked.
> Without it, someone could quietly rewrite what a capability is supposed to do and no one
> would be told the existing code may no longer match.

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
- A heading is matched by its label (anchored): only a `## …` heading whose label —
  optionally after a `WHAT`/`HOW` prefix — starts with "Contract", "Acceptance",
  "Input" or "Output" contributes to the hash; a commentary heading such as
  `## Notes — contract caveats` does not.
- The lock distinguishes "absent" from "corrupt" only at the gate (`check` warns on a
  present-but-unreadable lock); `load_lock` itself fails open to `{}`.

## HOW — Acceptance (= tests)
- Editing only the Description/Notes section does not change the hash.
- Editing the Output (or Contract) section changes the hash.
- `load_lock` on a missing or corrupt lock file returns an empty dict (no crash).
- `save_lock` then `load_lock` round-trips the same mapping.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tightens the promise on a login requirement, changing "must reject empty passwords"
  to "must reject empty or whitespace-only passwords." The fingerprint of that requirement
  no longer matches the one saved in the lock file, so when she runs the gate it flags that
  capability as drifted — a reminder to revisit the code before committing.

## WHERE — Current implementation
- `binding_hash`, `lock_path`, `load_lock`, `save_lock` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
