---
id: ARCH-MEMBERDRIFT-027
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v1.18
depends_on: [ARCH-DRIFT-003, ARCH-SCAN-002, ARCH-CHECK-006]
satisfies: [SYS-GATE-102]
lint_exempt: [ac-count-high]
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

Every bullet below is binding.
- Member content hashes live in a separate, versioned sidecar `_memberlock.json` (`{"_schema": N, "members": {id: {relfile: sha}}}`) computed only for single-requirement member files, on line-ending-normalized bytes, and it fails open when absent, corrupt or newer-schema. [[REQ-MEMBERDRIFT-879]]
- The gate warns for each confirmed requirement whose dedicated member changed since the sidecar while the requirement's own contract hash did not; a requirement whose contract also drifted is skipped, since forward drift already owns it. [[REQ-MEMBERDRIFT-880]]

## Cases
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

## Context
**Notes**
- Why `ac-count-high` is exempt: the eight criteria are the branch table of one decision —
  which (requirement, file) pair is reported as member drift — not eight behaviours that can
  break apart. Six of them (CASE-2 through CASE-6, CASE-8) are the suppression rules of that same
  decision. A split would produce two requirements sharing one contract.
- File-level granularity with a mono-requirement filter trades reach for silence: drift in
  a file shared by many requirements (e.g. a single engine file) is not attributed, by
  design. Repos with one file per capability get the most value.
- It asserts a member's bytes changed, not that the change is behaviourally meaningful —
  a reformat re-baselines like any edit. Re-running sync acknowledges and clears it.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- A team rewrites `modes/trias.md` from a six-step model to a four-step one but never
  re-touches the requirement that owns it. `reqmap.py gate` warns "MEMBER DRIFT —
  modes/trias.md changed since lock but the contract was not re-touched", so the stale
  spec is caught at the next gate run instead of months later during a human review.

**Current implementation**
- `compute_member_hashes`, `member_drift`, `load_memberlock`, `save_memberlock`,
  `_memberlock_path`, `MEMBERLOCK_SCHEMA` in `reqmap.py`, consumed by `cmd_check`
  — `compute_member_hashes` hashes mono-requirement member files, `member_drift` compares
  them to the sidecar while skipping forward-drifted requirements, and `cmd_check` emits a
  strict-promotable warn per result and re-baselines the sidecar on `--update-lock`.


--------------------


---
id: REQ-MEMBERDRIFT-879
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
---

# The member-hash sidecar

## Description
> Member hashes are kept in their own file, `_memberlock.json`, rather than folded into
> `_reqlock.json` — that keeps the requirement lock a byte-stable cross-repo contract an older
> seeded engine can still read, while giving reverse-direction drift its own versioned,
> fail-open storage. Only files dedicated to one requirement get a hash, because a shared
> file's change cannot be attributed to any single spec without noise.

Every bullet below is binding.
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

## Cases
CASE-1 — member hashes live in a separate versioned sidecar
  Given  a repo where `sync --update-lock` has run
  When   the requirements directory is inspected
  Then   `_memberlock.json` exists separately from `_reqlock.json`, holding `{"_schema": N,
         "members": {...}}`

CASE-2 — an absent, corrupt or newer-schema sidecar loads as empty
  Given  `_memberlock.json` is missing, and separately a copy whose `_schema` is above the
         engine's known value
  When   the sidecar is loaded
  Then   both cases yield an empty member map rather than an error

CASE-3 — only single-requirement member files get a hash
  Given  a file that is the sole `implements:` member of one requirement, and a file shared by
         two requirements
  When   member hashes are computed
  Then   the sidecar records the dedicated file's hash and omits the shared file

CASE-4 — member hashes are stable across line-ending styles
  Given  the same member content saved once with LF endings and once with CRLF endings
  When   the member hash is computed for each
  Then   both hashes are identical


--------------------


---
id: REQ-MEMBERDRIFT-880
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MEMBERDRIFT-027]
---

# Warning when code moves ahead of its spec

## Description
> A confirmed requirement's contract can sit untouched while the code implementing it
> quietly changes underneath — "confirmed" then silently means "confirmed several versions
> ago". The gate warns for exactly that case, skipping a requirement whose contract also
> drifted (forward drift already owns that one) and a member with no recorded baseline yet
> (it gets baselined on the next sync instead of nagged on first sight).

Every bullet below is binding.
- The gate warns for each confirmed requirement whose dedicated member changed since
  the sidecar while the requirement's own contract hash did not. A requirement whose
  contract also drifted is skipped (forward drift already owns it).
- A non-confirmed requirement's member drift is never reported; the check only applies once
  a requirement has been confirmed.
- A member with no recorded baseline does not warn, so a freshly-tagged file is baselined
  on the next sync rather than nagged on first sight.
- The check is warn-only by default and is promoted to an error under
  `--strict` (it joins the same strict set as contract drift).
- `--update-lock` re-baselines the sidecar in lockstep with `_reqlock.json`.

## Cases
CASE-1 — the gate warns only when the member drifted and the contract did not
  Given  a confirmed requirement whose dedicated member changed while its contract hash is
         unchanged, and a second requirement where both drifted
  When   member drift is computed
  Then   the first pair is reported and the second is skipped

CASE-2 — a non-confirmed requirement's member drift is never reported
  Given  a `baseline` (not yet confirmed) requirement whose dedicated member changed
  When   member drift is computed
  Then   it produces no warning

CASE-3 — a member with no sidecar baseline is silent
  Given  a freshly-tagged member file absent from `_memberlock.json`
  When   member drift is computed
  Then   it produces no warning

CASE-4 — member drift is a warning by default and an error under --strict
  Given  a baselined dedicated member that was then edited
  When   `gate` runs, then `gate --strict` runs
  Then   the first exits 0 with a warning and the second exits non-zero

CASE-5 — --update-lock re-baselines both lock files together
  Given  a dedicated member edited since the last sidecar baseline
  When   `sync --update-lock` runs
  Then   `_memberlock.json`'s hash for that file matches its current content, alongside
         `_reqlock.json`'s refresh

