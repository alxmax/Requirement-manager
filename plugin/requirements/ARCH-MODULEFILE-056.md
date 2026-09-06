---
id: ARCH-MODULEFILE-056
status: confirmed
level: architecture
layer: bus
owner: Alex
milestone: v2.32
priority: should-have
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-READ-103]
---

# Several requirements in one file

## Description
> A capability and the detailed design beneath it belong in one document, the way a
> requirements module holds many objects, instead of scattering one file per requirement
> across the folder — 618 of them, before this.

Every bullet below is binding.
- A block starts at a `---` line immediately followed by `id:`; each block loads as its own requirement.
- A file holding a single block is read exactly as before — unchanged for every pre-existing one-requirement file.
- A bare `---` used as a horizontal rule, not followed by `id:`, starts no new block.
- Confirming one requirement in a multi-block file changes that block's status alone.
- Only the first block in a file may fall back to the filename for its id; a later block with no `id:` does not.

## Cases
CASE-1 — each id: block becomes its own requirement
  Given  a file whose text holds three `---`/`id:` blocks
  When   the engine loads the corpus
  Then   each block is loaded as its own requirement, keeping its own body and block index

CASE-2 — a single-block file is read exactly as before
  Given  a file holding one requirement, no second `---`/`id:` block
  When   `split_requirement_blocks` runs on its text
  Then   it returns the whole text unchanged, byte for byte

CASE-3 — a horizontal rule starts no new block
  Given  a file whose body contains a bare `---` not followed by `id:`
  When   the engine loads the corpus
  Then   the file still yields exactly one requirement, and the text after the rule stays
         part of that requirement's body

CASE-4 — confirming one block changes only that block's status
  Given  a two-block file, the second block carrying an `implements:` member
  When   `confirm` runs on the second block's id
  Then   only the second block's status becomes `confirmed`; the first block's status and
         body are unchanged

CASE-5 — only the first block may fall back to the filename for its id
  Given  a file whose first block carries no `id:` (so it falls back to the filename) and
         whose second block carries its own explicit `id:`
  When   the engine loads the corpus
  Then   the first block resolves to the filename's id and the second block keeps its own
         distinct id — the fallback claims the filename once, not per block

