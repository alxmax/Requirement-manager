---
id: REQ-MEMBERDRIFT-027
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [CORE-DRIFT-003, CORE-SCAN-002, REQ-CHECK-006]
superseded_by:
lint_exempt: [ac-count-high]
milestone: v1.18
---

# Reverse-direction member drift

> Drift detection has one eye open. `_reqlock.json` stores one hash per requirement —
> the contract — so it fires when the *prose* moves ahead of the code. The reverse is
> invisible: a member (the code or doc that realises a requirement) can change while the
> contract sits untouched, so behaviour ships and the spec quietly goes stale. This is the
> mechanical half of intent-sync: hash the dedicated members too, and warn when one moves
> while its requirement does not. Without it, "confirmed" can silently mean "confirmed six
> versions ago", and only a human re-reading both sides would ever notice.

## WHAT — Contract (normative)
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Why `ac-count-high` is exempt: the eight criteria are the branch table of one decision —
  which (requirement, file) pair is reported as member drift — not eight behaviours that can
  break apart. Six of them (AC-2 through AC-6, AC-8) are the suppression rules of that same
  decision. A split would produce two requirements sharing one contract.
- File-level granularity with a mono-requirement filter trades reach for silence: drift in
  a file shared by many requirements (e.g. a single engine file) is not attributed, by
  design. Repos with one file per capability get the most value.
- It asserts a member's bytes changed, not that the change is behaviourally meaningful —
  a reformat re-baselines like any edit. Re-running sync acknowledges and clears it.

## HOW — Acceptance (= tests)
AC-1
  Given  a file that is a member of one requirement and a file shared by two
  When   member hashes are computed
  Then   only the dedicated file is recorded
AC-2
  Given  a sidecar that is absent, corrupt, or of a newer schema
  When   it is loaded
  Then   it reads as empty (fail open)
AC-3
  Given  a confirmed requirement whose dedicated member changed but whose contract did not
  When   member drift is computed
  Then   that (requirement, file) pair is reported
AC-4
  Given  a requirement whose contract also drifted since the lock
  When   member drift is computed
  Then   it is not reported (forward drift owns it)
AC-5
  Given  a non-confirmed requirement whose member changed
  When   member drift is computed
  Then   it is not reported
AC-6
  Given  a member file with no recorded baseline in the sidecar
  When   member drift is computed
  Then   it is not reported
AC-7
  Given  a baselined dedicated member that is then edited
  When   the gate runs
  Then   it warns (exit 0) and, under `--strict`, exits non-zero
AC-8
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
