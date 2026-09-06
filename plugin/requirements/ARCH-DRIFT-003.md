---
id: ARCH-DRIFT-003
status: confirmed
level: architecture
layer: bus
owner: Alex
milestone: v1.00
satisfies: [SYS-GATE-102]
---

# Contract hashing & lock

## Description
> A requirement file has a "binding" part — the precise promise of what the code must do.
> This takes a tiny fingerprint of just that part and remembers it. The next time anyone
> runs the tool, it can tell whether that promise changed since the code was last checked.
> Without it, someone could quietly rewrite what a capability is supposed to do and no one
> would be told the existing code may no longer match.

Every bullet below is binding.
- `binding_hash` computes a stable 12-character hex content hash over only the normative sections of a requirement body. [[REQ-DRIFT-841]]
- `load_lock`/`save_lock` read and write the per-id hash baseline at `requirements/_reqlock.json`, failing open to `{}` on a missing or corrupt file. [[REQ-DRIFT-842]]
- Waiving the drift check records who was waived and why, in a versioned sidecar the diff shows, so the one escape hatch in the gate is not also the one thing nobody reviews. [[REQ-DRIFT-988]]

## Cases
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

CASE-5
  Given  a confirmed contract that changed
  When   the drift is waived with a reason
  Then   the reason is recorded beside the hash it excuses

CASE-6
  Given  the flag that waives drift
  When   it is followed by another flag rather than a reason
  Then   it reads as a bare waiver and the following flag keeps its own value

## Context
**Terms**
- the normative sections  the parts of a requirement that promise something, as
- opposed to the parts that explain it.
- the binding hash        the short fingerprint taken over those sections.
- the lock                requirements/_reqlock.json — one saved fingerprint
- per requirement id.
- drift                   the fingerprint no longer matching the lock, meaning
- the promise changed since the code was last checked.

**Notes**
- A heading is matched by its label (anchored): only a `## …` heading whose label —
  optionally after a `WHAT`/`HOW` prefix — starts with "Contract", "Acceptance",
  "Input" or "Output" contributes to the hash; a commentary heading such as
  `## Notes — contract caveats` does not.
- The lock distinguishes "absent" from "corrupt" only at the gate (the gate warns on a
  present-but-unreadable lock); `load_lock` itself fails open to `{}`.
  (The `gate` command surfaces this warning; `check` is its deprecated alias.)

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tightens the promise on a login requirement, changing "must reject empty passwords"
  to "must reject empty or whitespace-only passwords." The fingerprint of that requirement
  no longer matches the one saved in the lock file, so when she runs the gate it flags that
  capability as drifted — a reminder to revisit the code before committing.

**Current implementation**
- `binding_hash`, `lock_path`, `load_lock`, `save_lock` in `reqmap.py`.


--------------------


---
id: REQ-DRIFT-841
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-DRIFT-003]
---

# Hashing only the normative sections

## Description
> A requirement file mixes a binding promise with prose that explains it — rationale, open
> questions, the member list. Hashing the whole file would report drift every time someone
> improved a sentence of explanation, training everyone to ignore the warning. Hashing only
> the Contract and Acceptance means the fingerprint changes exactly when the promise does.

Every bullet below is binding.
- `binding_hash` computes a stable 12-character hex content hash over only the
  normative sections of a requirement body.
- The normative sections are the `Contract` and `Acceptance` headings, plus the legacy
  `Input`/`Output`/`Acceptance` headings kept for back-compat.
- Rationale, notes, verify-intent, links and the member list stay outside the hash, so
  they may change without tripping drift.
- The hash is deterministic for identical normative content.

## Cases
CASE-1 — binding_hash returns a fixed-length hex digest
  Given  a requirement body with a `## Description` and `## Cases` section
  When   `binding_hash` runs on that body
  Then   it returns a 12-character lowercase hex string

CASE-2 — the legacy Output heading is still treated as normative
  Given  a requirement body using the legacy `## Output` heading instead of `## Contract`
  When   the clause under `## Output` is edited
  Then   `binding_hash` changes, proving the legacy heading feeds the hash

CASE-3 — editing Notes and the member list leaves the hash unchanged
  Given  a requirement body with `## Notes & known limitations` and `## Members in code` sections
  When   only the text under those sections is edited
  Then   `binding_hash` returns the same value before and after the edit

CASE-4 — binding_hash is deterministic across repeated calls
  Given  the same requirement body
  When   `binding_hash` runs on it twice, independently
  Then   both calls return the identical 12-character hash


--------------------


---
id: REQ-DRIFT-842
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-DRIFT-003]
---

# Reading and writing the drift baseline

## Description
> A fingerprint is only useful stored next to the last one seen. `_reqlock.json` is that
> memory: one hash per requirement id, so the next run can tell which contracts changed since
> the code was last checked. It fails open rather than crashing, because a corrupt or missing
> lock should degrade to "nothing recorded yet," not stop the tool from running at all.

Every bullet below is binding.
- `load_lock` and `save_lock` read and write the per-id hash baseline at
  `requirements/_reqlock.json`.
- A missing, empty or unparseable lock loads as an empty mapping, never a crash.
- `save_lock` creates the requirements directory if it is absent.
- `save_lock` writes sorted, indented JSON, so the lock file is diff-stable.

## Cases
CASE-1 — save_lock then load_lock round-trips through _reqlock.json
  Given  the hash mapping `{"A-B-001": "abc123def456", "C-D-002": "0123456789ab"}`
  When   `save_lock` writes it to a directory and `load_lock` reads that same directory
  Then   `load_lock` returns the identical mapping, read from `_reqlock.json`

CASE-2 — a missing or corrupt lock file loads as an empty dict
  Given  a directory with no `_reqlock.json`, and separately one holding non-UTF-8 bytes as `_reqlock.json`
  When   `load_lock` runs on each directory
  Then   both calls return `{}` and neither raises an exception

CASE-3 — save_lock creates a missing requirements directory
  Given  a target path whose parent directories (`does/not/exist`) do not exist yet
  When   `save_lock` writes a mapping to that path
  Then   the directory tree is created and `_reqlock.json` exists inside it

CASE-4 — save_lock writes sorted, indented JSON
  Given  a hash mapping with out-of-order keys (e.g. `{"Z-9": "..", "A-1": ".."}`)
  When   `save_lock` writes it to disk
  Then   the written `_reqlock.json` lists keys alphabetically and spans multiple indented lines



---
id: REQ-DRIFT-988
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFT-003]
---

# The waiver leaves a trace

## Description
> `--accept-drift` advances the baseline on a contract nobody re-validated. It is the one
> escape hatch in the gate, and it used to leave nothing behind: the lock hash moved, and
> why it was allowed to move lived in someone's head. A waiver a reviewer cannot see is a
> waiver nobody reviews.

Every bullet below is binding.
- `--accept-drift` takes an optional reason, and the reason is written to
  `requirements/_driftlog.json` beside the hash it excuses, so both land in the diff.
- A bare `--accept-drift` is recorded too, with a null reason. Recording only the explained
  waivers would make the unexplained one the invisible one.
- A demotion writes no entry: nothing was waived, so there is nothing to justify.
- Entries for requirements that have left the corpus are dropped, the way the lock prunes
  its own.
- The record is a versioned sidecar, never a new key in `_reqlock.json` — that file is the
  byte-stable cross-repo contract an older seeded engine still reads.
- A sidecar written by a newer schema, or unreadable, loads as no reasons on record rather
  than failing the run.

## Cases
CASE-1 — the reason is recorded beside the hash
  Given  a confirmed contract that changed
  When   `sync --accept-drift "renamed the flag"` runs
  Then   `_driftlog.json` holds that requirement's new hash and that reason

CASE-2 — a bare waiver is recorded with no reason
  Given  the same contract
  When   `sync --accept-drift` runs with no reason
  Then   the entry exists and its reason is null

CASE-3 — a demotion records nothing
  Given  the same contract
  When   `sync` runs without `--accept-drift`
  Then   the requirement is demoted to draft and no `_driftlog.json` is written

CASE-4 — a retired id is pruned
  Given  a drift log holding an id no longer in the corpus
  When   a later waiver is recorded
  Then   that id is gone from the log

CASE-5 — a forward schema fails open
  Given  a `_driftlog.json` whose `_schema` is newer than this engine's
  When   it is loaded
  Then   it reads as an empty record and nothing raises
