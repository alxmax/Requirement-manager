---
id: ARCH-MEMBERDRIFT-027
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-DRIFT-003, ARCH-SCAN-002, ARCH-CHECK-006]
satisfies: [SYS-GATE-102]
superseded_by:
lint_exempt: [ac-count-high]
milestone: v1.18
---

# Reverse-direction member drift

## Description
> Drift detection has one eye open. `_reqlock.json` stores one hash per requirement —
> the contract — so it fires when the *prose* moves ahead of the code. The reverse is
> invisible: a member (the code or doc that realises a requirement) can change while the
> contract sits untouched, so behaviour ships and the spec quietly goes stale. This is the
> mechanical half of intent-sync: hash the dedicated members too, and warn when one moves
> while its requirement does not. Without it, "confirmed" can silently mean "confirmed six
> versions ago", and only a human re-reading both sides would ever notice.
- Member content hashes live in a separate, versioned sidecar `_memberlock.json`
  (`{"_schema": N, "members": {id: {relfile: sha}}}`), so `_reqlock.json` stays a
  byte-stable cross-repo contract that an older seeded engine reads unchanged.
- The sidecar fails open (treated as empty) when absent, corrupt, or written by a
  newer `_schema` than the engine knows — degrading to "reverse-drift off this run"
  rather than crashing or mis-comparing.
- Member hashes are recorded only for files dedicated to ONE requirement (an
  `implements:`/`generated-from:` member of exactly one id); a file shared by several
  requirements is excluded, because a change there cannot be attributed without noise.
- Member hashes are computed on line-ending-normalized bytes (CRLF and lone CR folded
  to LF), so a lock generated on a CRLF working tree (Windows `core.autocrlf=true`) matches
  one verified on LF (Linux/CI). Without this every member shows spurious cross-platform
  drift, which `--strict` escalates to errors — mirrors the contract hash, already
  LF-normalized via the text-mode body parse.
- The gate warns for each confirmed requirement whose dedicated member changed since
  the sidecar while the requirement's own contract hash did not. A requirement whose
  contract also drifted is skipped (forward drift already owns it).
- A member with no recorded baseline does not warn, so a freshly-tagged file is baselined
  on the next sync rather than nagged on first sight.
- The check is warn-only by default and is promoted to an error under
  `--strict` (it joins the same strict set as contract drift).
- `--update-lock` re-baselines the sidecar in lockstep with `_reqlock.json`.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- Why `ac-count-high` is exempt: the eight criteria are the branch table of one decision —
  which (requirement, file) pair is reported as member drift — not eight behaviours that can
  break apart. Six of them (CASE-2 through CASE-6, CASE-8) are the suppression rules of that same
  decision. A split would produce two requirements sharing one contract.
- File-level granularity with a mono-requirement filter trades reach for silence: drift in
  a file shared by many requirements (e.g. a single engine file) is not attributed, by
  design. Repos with one file per capability get the most value.
- It asserts a member's bytes changed, not that the change is behaviourally meaningful —
  a reformat re-baselines like any edit. Re-running sync acknowledges and clears it.

## Cases (= tests)
CASE-1
  Given  a file that is a member of one requirement and a file shared by two
  When   member hashes are computed
  Then   only the dedicated file is recorded
CASE-2
  Given  a sidecar that is absent, corrupt, or of a newer schema
  When   it is loaded
  Then   it reads as empty (fail open)
CASE-3
  Given  a confirmed requirement whose dedicated member changed but whose contract did not
  When   member drift is computed
  Then   that (requirement, file) pair is reported
CASE-4
  Given  a requirement whose contract also drifted since the lock
  When   member drift is computed
  Then   it is not reported (forward drift owns it)
CASE-5
  Given  a non-confirmed requirement whose member changed
  When   member drift is computed
  Then   it is not reported
CASE-6
  Given  a member file with no recorded baseline in the sidecar
  When   member drift is computed
  Then   it is not reported
CASE-7
  Given  a baselined dedicated member that is then edited
  When   the gate runs
  Then   it warns (exit 0) and, under `--strict`, exits non-zero
CASE-8
  Given  the same member content saved once with LF and once with CRLF line endings
  When   the member hash is computed for each
  Then   the two hashes are identical (line endings are normalized before hashing)

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- A team rewrites `modes/trias.md` from a six-step model to a four-step one but never
  re-touches the requirement that owns it. `reqmap.py gate` warns "MEMBER DRIFT —
  modes/trias.md changed since lock but the contract was not re-touched", so the stale
  spec is caught at the next gate run instead of months later during a human review.

## WHERE — Current implementation
- `compute_member_hashes`, `member_drift`, `load_memberlock`, `save_memberlock`,
  `_memberlock_path`, `MEMBERLOCK_SCHEMA` in `reqmap.py`, consumed by `cmd_check`
  — `compute_member_hashes` hashes mono-requirement member files, `member_drift` compares
  them to the sidecar while skipping forward-drifted requirements, and `cmd_check` emits a
  strict-promotable warn per result and re-baselines the sidecar on `--update-lock`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-511
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# Member content hashes live in a separate, versioned

> Member content hashes live in a separate, versioned sidecar `_memberlock.json`
> (`{"_schema": N, "members": {id: {relfile: sha}}}`), so `_reqlock.json` stays a
> byte-stable cross-repo contract that an older seeded engine reads unchanged.

Scenario: member hashes live in a separate versioned sidecar
  Given  a repo where `sync --update-lock` has run
  When   the requirements directory is inspected
  Then   `_memberlock.json` exists separately from `_reqlock.json`, holding `{"_schema": N,
         "members": {...}}`

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-512
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# The sidecar fails open (treated as empty) when

> The sidecar fails open (treated as empty) when absent, corrupt, or written by a newer
> `_schema` than the engine knows — degrading to "reverse-drift off this run" rather than
> crashing or mis-comparing.

Scenario: an absent, corrupt or newer-schema sidecar loads as empty
  Given  `_memberlock.json` is missing, and separately a copy whose `_schema` is above the
         engine's known value
  When   the sidecar is loaded
  Then   both cases yield an empty member map rather than an error

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-513
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# Member hashes are recorded only for files dedicated

> Member hashes are recorded only for files dedicated to ONE requirement (an
> `implements:`/`generated-from:` member of exactly one id); a file shared by several
> requirements is excluded, because a change there cannot be attributed without noise.

Scenario: only single-requirement member files get a hash
  Given  a file that is the sole `implements:` member of one requirement, and a file shared by
         two requirements
  When   member hashes are computed
  Then   the sidecar records the dedicated file's hash and omits the shared file

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-514
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# Member hashes are computed on line-ending-normalized bytes (CRLF

> Member hashes are computed on line-ending-normalized bytes (CRLF and lone CR folded to
> LF), so a lock generated on a CRLF working tree (Windows `core.autocrlf=true`) matches
> one verified on LF (Linux/CI). Without this every member shows spurious cross-platform
> drift, which `--strict` escalates to errors — mirrors the contract hash, already
> LF-normalized via the text-mode body parse.

Scenario: member hashes are stable across line-ending styles
  Given  the same member content saved once with LF endings and once with CRLF endings
  When   the member hash is computed for each
  Then   both hashes are identical

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-515
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# The gate warns for each confirmed requirement whose

> The gate warns for each confirmed requirement whose dedicated member changed since the
> sidecar while the requirement's own contract hash did not. A requirement whose contract
> also drifted is skipped (forward drift already owns it).

Scenario: the gate warns only when the member drifted and the contract did not
  Given  a confirmed requirement whose dedicated member changed while its contract hash is
         unchanged, and a second requirement where both drifted
  When   member drift is computed
  Then   the first pair is reported and the second is skipped

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-516
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# A member with no recorded baseline does not

> A member with no recorded baseline does not warn, so a freshly-tagged file is baselined
> on the next sync rather than nagged on first sight.

Scenario: a member with no sidecar baseline is silent
  Given  a freshly-tagged member file absent from `_memberlock.json`
  When   member drift is computed
  Then   it produces no warning

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-517
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# The check is warn-only by default and is

> The check is warn-only by default and is promoted to an error under `--strict` (it joins
> the same strict set as contract drift).

Scenario: member drift is a warning by default and an error under --strict
  Given  a baselined dedicated member that was then edited
  When   `gate` runs, then `gate --strict` runs
  Then   the first exits 0 with a warning and the second exits non-zero

## Members in code (auto)




--------------------


---
id: REQ-MEMBERDRIFT-518
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
superseded_by:
---

# --update-lock re-baselines the sidecar in lockstep with _reqlock.json

> `--update-lock` re-baselines the sidecar in lockstep with `_reqlock.json`.

Scenario: --update-lock re-baselines both lock files together
  Given  a dedicated member edited since the last sidecar baseline
  When   `sync --update-lock` runs
  Then   `_memberlock.json`'s hash for that file matches its current content, alongside
         `_reqlock.json`'s refresh

## Members in code (auto)
