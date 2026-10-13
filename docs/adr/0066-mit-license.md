# ADR-0066 — MIT, brought forward from the BSL change date

- **Status:** Superseded by [ADR-0069](0069-apache-2-license.md) (2026-10-13). The
  reasoning below is left exactly as decided on 2026-10-11. It superseded
  [ADR-0013](0013-business-source-license.md).
- **Decided:** 2026-10-11
- **Evidence:** `LICENSE`; ADR-0013's revisit condition; `git shortlog -sn` (one human
  author); `ROADMAP.md` (the parked licence item, now done); `.github/ISSUE_TEMPLATE/tried-on-my-repo.yml`.

## Context

ADR-0013 chose the Business Source License 1.1 on 2026-06-05: non-production use now,
production use under a commercial grant until 2030-06-05, then Apache 2.0. The record
said it was a hypothesis about a project with no contributors and no external users, and
that either a contributor or an external user's licence policy was enough to reopen it.

Neither has appeared. `git shortlog` shows one human author. The licence is still the
review a company runs before it evaluates the tool, which means the project cannot learn
whether anyone wants it while the licence stays. The change date already conceded the end
state: the code becomes an OSI licence. Waiting until 2030 does not buy a user.

## Decision

The licensor, Schipor Alexandru, relicenses the work under the MIT License, effective
with v8.20.0. MIT rather than the Apache 2.0 named as BSL's change licence: one human
author holds the copyright, there is no second contributor's grant to preserve, and MIT
is the text a reviewer already knows.

Copying `scripts/reqmap.py` and `scripts/reqmap_engine/` into a repo stays a supported
install. A paid tier, if one is ever offered, is a separate product (hosting, support),
not a restriction on this engine.

## Consequences

- `plugin.json` says `MIT`. Saying the project is source-available would now be false.
- The BSL text is gone from `LICENSE`. ADR-0013 stays as the record of why BSL was chosen.
- Contributions from this version on are under MIT. `CONTRIBUTING.md` says so.
- The conversion date 2030-06-05 no longer applies.

## Revisit when

A second copyright holder appears whose work cannot be relicensed by the statements
above, or a distributor needs a patent grant the MIT text does not give. Either is a new
record, not an edit of this one.
