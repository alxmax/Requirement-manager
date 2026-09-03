---
id: ARCH-CONTEXT-048
status: confirmed
level: system
layer: feature
owner: Alex
depends_on: [ARCH-MAP-007]
satisfies: [SYS-AUTHOR-101]
superseded_by:
milestone: v2.30
---

# Consolidated Context section

## Description
> A requirement author choosing between `## WHAT — Notes`, `## Example — in practice` and
> `## WHERE — Current implementation` was picking between three near-synonymous informative
> buckets, not making a decision about the contract. This narrows that choice to one
> section — `## Context` — while keeping every existing requirement file that still uses the
> three separate headings working exactly as it does today.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     the legacy form   a requirement body using the separate `## WHAT — Notes`,
                       `## Example — in practice` and `## WHERE — Current implementation`
                       headings.
     the Context form  a requirement body using one `## Context (non-binding)` section with
                       bold `**Notes**` / `**Example**` / `**Current implementation**`
                       sub-groups instead.
     a sub-group       the bullets following one bold label inside `## Context`, up to the
                       next bold label or the next `## ` heading. -->

**What it adds**
- `new`'s built-in template scaffolds the Context form for every newly-created requirement.
- The Context form groups sub-topics with a bold label line (`**Notes**`, `**Example**`,
  `**Current implementation**`), the same clause-group convention the Contract section
  already uses for five-plus clauses.
- `_context_group(body, label)` returns the bullets under one bold sub-group inside
  `## Context`, or an empty list when that sub-group or the section itself is absent.

**What stays unchanged**
- The legacy form remains fully valid. Nothing in the gate, the lint checks, or the drift
  hash reads `## WHAT — Notes`, `## Example — in practice` or `## WHERE — Current
  implementation` by name, so no existing requirement file needs to change.
- `_build_map_data`'s `notes` and `current_impl` fields try the legacy heading first
  (`_bullets`), and fall back to the matching Context sub-group only when the legacy
  heading is absent — never both at once in one file, so the fallback cannot mask real
  content a legacy-form file already has.
- `## Context` and its sub-groups are commentary: not hashed by `binding_hash`, not read by
  `_has_section`, and not linted. Neither form can trip drift or `missing-section`.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Cases (= tests)
CASE-1
  Given  a requirement body with `## Context (non-binding)` holding `**Notes**` and
         `**Current implementation**` sub-groups
  When   `_context_group(body, "notes")` and `_context_group(body, "current implementation")` run
  Then   each returns exactly the bullets under its own sub-group

CASE-2
  Given  a requirement body with no `## Context` section at all (a legacy-form or
         Contract-only body)
  When   `_context_group` runs for any label
  Then   it returns an empty list

CASE-3
  Given  a `## Context` section that has an `**Example**` sub-group but no `**Notes**` sub-group
  When   `_context_group(body, "notes")` runs
  Then   it returns an empty list rather than the Example bullets

CASE-4
  Given  a confirmed requirement using only the Context form
  When   `map` regenerates `_map.json`
  Then   the node's `notes` and `current_impl` fields are populated from the matching
         Context sub-groups

CASE-5
  Given  a confirmed requirement using the legacy `## WHAT — Notes` heading
  When   `map` regenerates `_map.json`
  Then   the node's `notes` field is populated from that legacy heading, unchanged from
         before this requirement existed

## Context (non-binding)
<!-- This file is itself written in the form it describes, as a live example. -->
**Notes**
- The two draft-emitting code paths (`draft`'s prose-capability and code-capability
  branches) were updated to scaffold the Context form too, so a promoted draft needs no
  reshaping — matching the existing "emission schema matches `REQUIREMENT_TEMPLATE`" intent.
- [ADR-0017](../../docs/adr/0017-consolidated-context-section.md) records the decision and
  the Senate audit it came out of, including why the `>` WHY blockquote was deliberately
  left alone (it is not heading-based — `_first_quote` reads the first blockquote in the
  file regardless of section — so merging it into `## Context` would not have simplified
  anything a parser cares about).

**Example**
- Ana scaffolds a new requirement with `reqmap.py new AREA-NAME-NNN`. Instead of deciding
  whether a sentence belongs under Notes, Example, or WHERE, she writes it under `##
  Context`, grouped by whichever of the three bold labels fits — or skips a label entirely
  if she has nothing to say there.

**Current implementation**
- `_context_group` in `reqmap.py`, called from `_build_map_data`'s `notes`/`current_impl`
  emission as a fallback after `_bullets` on the legacy heading.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-CONTEXT-312
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CONTEXT-048]
superseded_by:
---

# New's built-in template scaffolds the Context form for

> `new`'s built-in template scaffolds the Context form for every newly-created
> requirement.

Scenario: a newly scaffolded requirement carries the Context form
  Given  no requirement named `AREA-X-001`
  When   `new AREA-X-001` runs
  Then   the created file holds a `## Context (non-binding)` section

## Members in code (auto)




--------------------


---
id: REQ-CONTEXT-313
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CONTEXT-048]
superseded_by:
---

# The Context form groups sub-topics with a bold

> The Context form groups sub-topics with a bold label line (`**Notes**`, `**Example**`,
> `**Current implementation**`), the same clause-group convention the Contract section
> already uses for five-plus clauses.

Scenario: bold sub-group labels keep each group's bullets separate
  Given  a `## Context` section with `**Notes**` bullets followed by `**Current
         implementation**` bullets
  When   `_context_group(body, "notes")` and `_context_group(body, "current implementation")` run
  Then   each call returns only the bullets under its own label, none from the other

## Members in code (auto)




--------------------


---
id: REQ-CONTEXT-314
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CONTEXT-048]
superseded_by:
---

# _context_group(body, label) returns the bullets under one bold

> `_context_group(body, label)` returns the bullets under one bold sub-group inside `##
> Context`, or an empty list when that sub-group or the section itself is absent.

Scenario: an absent sub-group returns empty instead of a neighboring group's bullets
  Given  a `## Context` section with an `**Example**` sub-group but no `**Notes**` sub-group
  When   `_context_group(body, "notes")` runs
  Then   it returns `[]`, not the Example bullets

## Members in code (auto)




--------------------


---
id: REQ-CONTEXT-316
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CONTEXT-048]
superseded_by:
---

# _build_map_data's notes and current_impl fields try the legacy

> `_build_map_data`'s `notes` and `current_impl` fields try the legacy heading first
> (`_bullets`), and fall back to the matching Context sub-group only when the legacy
> heading is absent — never both at once in one file, so the fallback cannot mask real
> content a legacy-form file already has.

Scenario: notes come from the legacy heading, not the Context fallback, when present
  Given  a confirmed requirement carrying `## WHAT — Notes` with a legacy note (no `##
         Context` section)
  When   `map` regenerates `_map.json` via `_build_map_data`
  Then   the node's `notes` field holds the legacy bullet, unchanged from before this
         feature, because the gate, the lint checks and the drift hash never read that
         heading by name either — the file needs no change

## Members in code (auto)




--------------------


---
id: REQ-CONTEXT-317
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CONTEXT-048]
superseded_by:
---

# ## Context and its sub-groups are commentary: not

> `## Context` and its sub-groups are commentary: not hashed by `binding_hash`, not read
> by `_has_section`, and not linted. Neither form can trip drift or `missing-section`.

Scenario: editing only the Context bullets leaves binding_hash unchanged
  Given  two bodies identical except for the bullets under a `## Context (non-binding)` section
  When   `binding_hash` runs on each body
  Then   both hashes are equal — the Context edit produces no drift

## Members in code (auto)
