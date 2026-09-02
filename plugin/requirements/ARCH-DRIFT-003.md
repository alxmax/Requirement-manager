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

> A requirement file has a "binding" part — the precise promise of what the code must do.
> This takes a tiny fingerprint of just that part and remembers it. The next time anyone
> runs the tool, it can tell whether that promise changed since the code was last checked.
> Without it, someone could quietly rewrite what a capability is supposed to do and no one
> would be told the existing code may no longer match.

## WHAT — Contract (normative)
Every line in this section is binding.
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A heading is matched by its label (anchored): only a `## …` heading whose label —
  optionally after a `WHAT`/`HOW` prefix — starts with "Contract", "Acceptance",
  "Input" or "Output" contributes to the hash; a commentary heading such as
  `## Notes — contract caveats` does not.
- The lock distinguishes "absent" from "corrupt" only at the gate (the gate warns on a
  present-but-unreadable lock); `load_lock` itself fails open to `{}`.
  (The `gate` command surfaces this warning; `check` is its deprecated alias.)

## HOW — Acceptance (= tests)
AC-1
  Given  a requirement body
  When   only its Description/Notes section is edited
  Then   the binding hash does not change

AC-2
  Given  a requirement body
  When   its Output (or Contract) section is edited
  Then   the binding hash changes

AC-3
  Given  a missing or corrupt lock file
  When   `load_lock` runs
  Then   it returns an empty dict (no crash)

AC-4
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
