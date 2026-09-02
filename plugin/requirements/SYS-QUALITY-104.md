---
id: SYS-QUALITY-104
status: confirmed
form: atomic
level: system
layer: need
owner: Alex
priority: must-have
verification: inspection
satisfies: [SYS-SSOT-001]
depends_on: []
superseded_by:
---

# Keeping requirements readable

> As someone who has to read the corpus a year from now, I want the engine to flag prose 
> that is hard to follow or scope that has quietly grown, so that a requirement stays 
> something a newcomer can act on.

Scenario: an overloaded requirement is flagged
  Given  a requirement whose contract and criteria have both outgrown their ceilings
  When   the linter runs
  Then   it reports the overload without changing the exit code, and an author who disagrees can record an exemption in the file

## Requirements in this system (auto)
- `ARCH-LINT-014` — Requirement readability linter  (architecture)  ·  13 detailed design
- `ARCH-LINTCHECKS-025` — Readability & scope checks  (architecture)  ·  19 detailed design
- `ARCH-PIPE-046` — A closed output pipe ends a command quietly  (architecture)  ·  4 detailed design
- `ARCH-REVIEW-022` — AI requirement-quality review (deterministic plan + advisory pass)  (architecture)  ·  8 detailed design
- `ARCH-SIMILAR-016` — Duplicate-capability detector  (architecture)  ·  16 detailed design
- `ARCH-SUGGESTVERIFIES-047` — Suggest per-criterion `verifies:` tags  (architecture)  ·  12 detailed design
