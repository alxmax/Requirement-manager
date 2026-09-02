---
id: ARCH-REDUNDANCY-058
status: confirmed
form: atomic
level: architecture
layer: feature
owner: Alex
priority: should-have
verification: automated test
rationale: Decomposing several architecture requirements can mint the same obligation twice, and nothing in the engine noticed; a corpus that only ever grows covers the same code with more requirements each time.
satisfies: [SYS-QUALITY-104]
depends_on: [ARCH-NEXT-013, ARCH-SIMILAR-016]
superseded_by:
---

# Requirements that say the same thing

> As someone whose corpus keeps growing, I want to be told when two requirements state the
> same obligation word for word, so that the code ends up covered by as few requirements as
> it takes rather than by as many as were ever written.

Scenario: two requirements carrying the same clause, and a folder full of fresh drafts
  Given  a corpus where two or more requirements' Description clauses are identical once
         case and whitespace are normalised, alongside scaffolded drafts that all still
         carry the same `TODO:` placeholder
  When   `sync` finishes, or `next` runs
  Then   each duplicate group is reported once with the ids that share the contract and how
         many could be folded away, the placeholder drafts are not reported as duplicates of
         each other, `gate` says nothing about any of it, and no file is written

## Members in code (auto)
