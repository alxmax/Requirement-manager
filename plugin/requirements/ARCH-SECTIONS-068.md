---
id: ARCH-SECTIONS-068
status: confirmed
level: architecture
layer: bus
owner: Alex
satisfies: [SYS-SSOT-001]
---

# Reading a requirement's sections

## Description
> A requirement file is read by nine different things — the drift hash, the linter, the
> map, `show`, `dupes`, the case counter — and each one has to answer the same two
> questions first: where does this section start, and is this line inside a fenced
> example. When each answered for itself they disagreed, and the disagreement was
> invisible: a `## Description` inside a ```-block satisfied the presence check while
> every reader of that section came back empty, and the drift hash treated the fenced
> example as part of the contract.

Every bullet below is binding.
- One reader answers where a section begins and ends, and every consumer of a requirement
  body — the drift hash included — asks it rather than scanning the body itself.
  [[REQ-SECTIONS-994]]

## Cases
CASE-1 — a heading inside a fence is not a section
  Given  a body whose only `## Description` is inside a fenced example
  When   any reader asks for the Description
  Then   all of them agree the section is absent

CASE-2 — a fenced example is not part of the contract
  Given  a normative section containing a fenced example of another section
  When   the drift hash is computed
  Then   the fenced lines are not hashed

CASE-3 — presence and readability answer to the same fence
  Given  this repository's requirement blocks
  When   the presence check and the section reader run over each of them
  Then   every section the presence check accepts is one the reader can open, and
         every section the reader opens is one the presence check accepts


--------------------


---
id: REQ-SECTIONS-994
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-SECTIONS-068]
---

# One section reader for every consumer

## Description
> Eight functions carried a copy of the same loop — track a ``` fence, watch for a `## `,
> grab the first matching section until the next heading — and `binding_hash` carried a
> ninth copy that did not track the fence at all. The copies had each picked up their own
> guards over time, so what a fence meant depended on which one you asked.

Every bullet below is binding.
- `_body_lines` yields `(is_heading, line)` for every body line outside a fenced code
  block, checking the fence before the heading, so a `## ` inside a fence is code.
- `_section_lines` yields the lines of the FIRST section whose heading label matches, up
  to the next heading, and takes one label or a tuple of them so a renamed section still
  reads under its old spelling.
- `raw=True` preserves the physical line, indentation and blank lines included, for the
  Given/When/Then blocks rendered as authored.
- What the lines mean — bullets, clauses, prose, criteria — stays with each caller. Only
  the boundary is shared.
- `binding_hash` reads the body through `_body_lines`, so a fenced heading neither opens a
  normative span nor closes one.

## Cases
CASE-1 — the fence is checked before the heading
  Given  a body with `## Cases` inside a fenced block
  When   `_body_lines` runs
  Then   that line is not yielded at all, as a heading or otherwise

CASE-2 — a section stops at the next heading
  Given  a Description followed by a Notes section
  When   `_section_lines` reads the Description
  Then   nothing from Notes is included

CASE-3 — a legacy spelling still reads
  Given  a body using `## WHAT — Contract` rather than `## Description`
  When   `_section_lines` is asked for `CONTRACT_LABELS`
  Then   it returns that section's lines

CASE-4 — raw keeps indentation, stripped does not
  Given  a section with an indented continuation line
  When   the same section is read with and without `raw`
  Then   the raw form keeps the leading spaces and the stripped form does not

CASE-5 — a fenced heading changes no hash
  Given  a normative section whose text contains a fenced example of another heading
  When   `binding_hash` runs
  Then   the fenced lines are absent from the hashed span
