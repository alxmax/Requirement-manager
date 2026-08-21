# ADR-0013 — Business Source License 1.1

- **Status:** Accepted, with an open revisit trigger
- **Decided:** 2026-06-05 (change date set), SPDX id corrected 2026-06-16
- **Evidence:** `LICENSE`; `CHANGELOG.md` `v2.3.1`; `TODO.md` v3

## Context

The project is source-available and solo-maintained. The two conventional options are a
permissive OSS licence (maximum adoption, no commercial protection) and a proprietary one
(protection, near-zero adoption for a developer tool nobody can read).

## Decision

Business Source License 1.1: copy, modify, redistribute and **non-production** use are granted
now; production use requires a commercial licence until the **Change Date, 2030-06-05**, when
the whole thing converts to **Apache 2.0**.

## Consequences

- It is **not** an open-source licence, and saying otherwise would be false. `plugin.json` once
  declared `"MIT"` while the LICENSE file said BSL — corrected to the SPDX id `BUSL-1.1`, and
  the mismatch is worth remembering as the kind of claim this project exists to catch.
- Some potential users are excluded outright: companies with a policy against non-OSI licences
  will not evaluate it, whatever it does. That directly taxes the "get one external user"
  roadmap goal.
- Every contribution ships under the same terms, which a contributor must accept —
  `CONTRIBUTING.md` says so plainly rather than leaving it to be discovered.
- The conversion is automatic and dated, so the worst case for an adopter is bounded: the code
  they can read today becomes Apache 2.0 on a date already written down.

## Revisit when

Someone actually wants to contribute, or an external user's licence policy is the only thing
blocking adoption. Both are on the roadmap as open items, and either is enough to reopen this —
a licence chosen for a project with no contributors and no external users is a hypothesis about
the future, not a settled position.
