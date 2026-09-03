---
id: ARCH-DRIFT-003
status: confirmed
level: architecture
layer: bus
owner: Alex
depends_on: []
satisfies: [SYS-GATE-102]
superseded_by:
milestone: v1.00
---

# Contract hashing & lock

## Description
> A requirement file has a "binding" part — the precise promise of what the code must do.
> This takes a tiny fingerprint of just that part and remembers it. The next time anyone
> runs the tool, it can tell whether that promise changed since the code was last checked.
> Without it, someone could quietly rewrite what a capability is supposed to do and no one
> would be told the existing code may no longer match.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     the normative sections  the parts of a requirement that promise something, as
                             opposed to the parts that explain it.
     the binding hash        the short fingerprint taken over those sections.
     the lock                requirements/_reqlock.json — one saved fingerprint
                             per requirement id.
     drift                   the fingerprint no longer matching the lock, meaning
                             the promise changed since the code was last checked. -->

**What it hashes**
- `binding_hash` computes a stable 12-character hex content hash over only the
  normative sections of a requirement body.
- The normative sections are the `Contract` and `Acceptance` headings, plus the legacy
  `Input`/`Output`/`Acceptance` headings kept for back-compat.
- Rationale, notes, verify-intent, links and the member list stay outside the hash, so
  they may change without tripping drift.
- The hash is deterministic for identical normative content.

**Where the baseline lives**
- `load_lock` and `save_lock` read and write the per-id hash baseline at
  `requirements/_reqlock.json`.
- A missing, empty or unparseable lock loads as an empty mapping, never a crash.

**How it writes the lock**
- `save_lock` creates the requirements directory if it is absent.
- `save_lock` writes sorted, indented JSON, so the lock file is diff-stable.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- A heading is matched by its label (anchored): only a `## …` heading whose label —
  optionally after a `WHAT`/`HOW` prefix — starts with "Contract", "Acceptance",
  "Input" or "Output" contributes to the hash; a commentary heading such as
  `## Notes — contract caveats` does not.
- The lock distinguishes "absent" from "corrupt" only at the gate (the gate warns on a
  present-but-unreadable lock); `load_lock` itself fails open to `{}`.
  (The `gate` command surfaces this warning; `check` is its deprecated alias.)

## Cases (= tests)
CASE-1
  Given  a requirement body
  When   only its Description/Notes section is edited
  Then   the binding hash does not change

CASE-2
  Given  a requirement body
  When   its Output (or Contract) section is edited
  Then   the binding hash changes

CASE-3
  Given  a missing or corrupt lock file
  When   `load_lock` runs
  Then   it returns an empty dict (no crash)

CASE-4
  Given  a hash mapping
  When   `save_lock` then `load_lock` run
  Then   the same mapping round-trips

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




--------------------


---
id: REQ-DRIFT-200
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# Binding_hash computes a stable 12-character hex content hash

> `binding_hash` computes a stable 12-character hex content hash over only the normative
> sections of a requirement body.

Scenario: binding_hash returns a fixed-length hex digest
  Given  a requirement body with a `## Description` and `## Cases` section
  When   `binding_hash` runs on that body
  Then   it returns a 12-character lowercase hex string

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-201
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# The normative sections are the Contract and Acceptance

> The normative sections are the `Contract` and `Acceptance` headings, plus the legacy
> `Input`/`Output`/`Acceptance` headings kept for back-compat.

Scenario: the legacy Output heading is still treated as normative
  Given  a requirement body using the legacy `## Output` heading instead of `## Contract`
  When   the clause under `## Output` is edited
  Then   `binding_hash` changes, proving the legacy heading feeds the hash

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-202
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# Rationale, notes, verify-intent, links and the member list

> Rationale, notes, verify-intent, links and the member list stay outside the hash, so
> they may change without tripping drift.

Scenario: editing Notes and the member list leaves the hash unchanged
  Given  a requirement body with `## Notes & known limitations` and `## Members in code` sections
  When   only the text under those sections is edited
  Then   `binding_hash` returns the same value before and after the edit

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-203
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# The hash is deterministic for identical normative content

> The hash is deterministic for identical normative content.

Scenario: binding_hash is deterministic across repeated calls
  Given  the same requirement body
  When   `binding_hash` runs on it twice, independently
  Then   both calls return the identical 12-character hash

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-204
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# Load_lock and save_lock read and write the per-id

> `load_lock` and `save_lock` read and write the per-id hash baseline at
> `requirements/_reqlock.json`.

Scenario: save_lock then load_lock round-trips through _reqlock.json
  Given  the hash mapping `{"A-B-001": "abc123def456", "C-D-002": "0123456789ab"}`
  When   `save_lock` writes it to a directory and `load_lock` reads that same directory
  Then   `load_lock` returns the identical mapping, read from `_reqlock.json`

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-205
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# A missing, empty or unparseable lock loads as

> A missing, empty or unparseable lock loads as an empty mapping, never a crash.

Scenario: a missing or corrupt lock file loads as an empty dict
  Given  a directory with no `_reqlock.json`, and separately one holding non-UTF-8 bytes as `_reqlock.json`
  When   `load_lock` runs on each directory
  Then   both calls return `{}` and neither raises an exception

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-206
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# Save_lock creates the requirements directory if it is

> `save_lock` creates the requirements directory if it is absent.

Scenario: save_lock creates a missing requirements directory
  Given  a target path whose parent directories (`does/not/exist`) do not exist yet
  When   `save_lock` writes a mapping to that path
  Then   the directory tree is created and `_reqlock.json` exists inside it

## Members in code (auto)




--------------------


---
id: REQ-DRIFT-207
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
superseded_by:
---

# Save_lock writes sorted, indented JSON, so the lock

> `save_lock` writes sorted, indented JSON, so the lock file is diff-stable.

Scenario: save_lock writes sorted, indented JSON
  Given  a hash mapping with out-of-order keys (e.g. `{"Z-9": "..", "A-1": ".."}`)
  When   `save_lock` writes it to disk
  Then   the written `_reqlock.json` lists keys alphabetically and spans multiple indented lines

## Members in code (auto)
