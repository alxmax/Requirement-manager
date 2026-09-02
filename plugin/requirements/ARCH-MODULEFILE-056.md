---
id: ARCH-MODULEFILE-056
status: confirmed
form: atomic
level: architecture
layer: bus
owner: Alex
priority: should-have
verification: automated test
rationale: A capability and the detailed design beneath it belong in one document, the way a requirements module holds many objects; one file per requirement scattered 618 of them across the folder.
satisfies: [SYS-READ-103]
depends_on: [ARCH-PARSE-001]
superseded_by:
---

# Several requirements in one file

> As someone reading or writing a corpus where each capability owns dozens of detailed-design
> requirements, I want one file to hold all of them, so that a capability reads as a single
> document instead of scattering its parts across the folder.

Scenario: a file carrying an architecture requirement and its detailed design
  Given  a file whose text holds one frontmatter block per requirement, each new block
         beginning at a `---` line immediately followed by `id:`
  When   the engine loads the corpus and later confirms one of those requirements
  Then   every block is loaded as its own requirement, a file with a single block is read
         exactly as before, a bare `---` used as a horizontal rule starts no new block, and
         confirming changes the status of that requirement alone

## Members in code (auto)
