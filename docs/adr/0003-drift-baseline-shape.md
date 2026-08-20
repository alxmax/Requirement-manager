# ADR-0003 — Contract hash in the lock, member hashes in a sidecar

- **Status:** Accepted
- **Decided:** 2026-06-19 (`REQ-MEMBERDRIFT-027`), line-ending fix 2026-06-26
- **Evidence:** `CHANGELOG.md` `v2.8.1`; `TODO.md` v1.18; `REQ-MEMBERDRIFT-027`

## Context

Drift detection needs a baseline. The original one was a single file,
`requirements/_reqlock.json`, holding **one hash per requirement** — the fingerprint of its
normative sections. That catches drift in one direction only: the prose moved and the code did
not.

The reverse direction is just as real and was structurally invisible. A downstream project's
`confirmed` requirement described a three-skeptic voting model while the shipped code had moved
to a one-skeptic model. The requirement file was never edited, so its hash never changed, so
nothing warned. Behaviour shipped; the spec stayed put.

Recording member hashes in `_reqlock.json` would have fixed that and broken something else:
the lock is read by **every vendored engine, including old ones**, and its byte shape is the
cross-repo contract. A new key there is a compatibility event.

## Decision

Keep `_reqlock.json` byte-stable: one hash per requirement, the contract, nothing else. Put
member-content hashes in a **separate versioned sidecar**, `_memberlock.json`
(`{_schema, members}`), and scope the reverse check to requirements whose members are
*dedicated* to them — a file belonging to one requirement — so an edit to a widely-shared file
does not nag a dozen contracts at once.

Hash after folding line endings to LF, on both sides.

## Consequences

- An older seeded engine reads `_reqlock.json` unchanged and simply ignores the sidecar. No
  flag day, no coordinated upgrade.
- The reverse check is warn-only ([ADR-0002](0002-error-versus-warning.md)) and deliberately
  narrow. Alarm fatigue was the explicit design constraint: every code edit nagging its
  requirement would be worse than the gap it closes.
- The LF fold is not cosmetic. Hashing raw bytes meant a lock generated on a CRLF checkout
  disagreed with the same tree on Linux — every member showing spurious drift, harmless as a
  warning and a wall of false errors under `--strict`.
- Two lock files means two files that must be committed, so `gate` warns when either is present
  but untracked: an uncommitted lock silently disables drift detection on a fresh CI checkout.

## Revisit when

A third drift direction appears that neither hash can express — for instance one requirement
against another's contract. That would be a new sidecar under the same rule, not a wider
`_reqlock.json`.
