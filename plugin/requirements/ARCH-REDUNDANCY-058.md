---
id: ARCH-REDUNDANCY-058
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.34
priority: should-have
depends_on: [ARCH-NEXT-013, ARCH-SIMILAR-016]
satisfies: [SYS-QUALITY-104]
---

# Requirements that say the same thing

## Description
> Decomposing several architecture requirements can mint the same obligation twice, and
> nothing in the engine noticed — a corpus that only ever grows covers the same code with
> more requirements each time. `_redundant_groups` reports requirements whose Description
> clauses are byte-identical once case and whitespace are normalised, so the corpus can be
> folded back down instead of growing without bound.

Every bullet below is binding.
- Two or more requirements whose Description clauses are identical once case and whitespace are normalised form one duplicate group.
- Every scaffolded draft carries the same `TODO:` placeholder text, so draft-status requirements are excluded, or every draft would report as a duplicate of every other.
- `next` reports each group once, naming its ids and how many could be folded away.
- `gate` says nothing about redundancy — it runs on every commit, and corpus shape is not a commit-time concern.
- The check is read-only: it never writes a file and never merges anything itself.

## Cases
CASE-1 — identical Description clauses group together
  Given  two requirements whose Description clause reads exactly "`x` does the thing." and a
         third with a different clause
  When   `_redundant_groups` runs
  Then   it returns one group holding only the two matching ids

CASE-2 — case and whitespace differences do not hide a duplicate
  Given  one requirement's clause reading "`x` does   the thing." and another reading
         "`X` DOES the thing."
  When   `_redundant_groups` runs
  Then   the two are still grouped as one duplicate

CASE-3 — a genuinely different clause is not flagged
  Given  two requirements whose clauses differ by more than case or whitespace
  When   `_redundant_groups` runs
  Then   it returns no group for them

CASE-4 — draft placeholders sharing the same TODO text are not duplicates of each other
  Given  two `status: draft` requirements both carrying the identical scaffolded
         `TODO: the observed behavior.` clause
  When   `_redundant_groups` runs
  Then   it returns no group for them

CASE-5 — next reports each group once and writes nothing; gate stays silent
  Given  two confirmed requirements sharing one identical Description clause
  When   `next` runs, and separately `gate` runs on the same corpus
  Then   `next`'s output names both ids under one "Redundancy" finding and the directory's
         file listing is unchanged afterward; `gate`'s output says nothing about redundancy

