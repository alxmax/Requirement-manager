# ADR-0027 — A requirement can be retired, and the engine removes only what it can prove

- **Status:** Accepted
- **Decided:** 2026-09-04
- **Supersedes:** [ADR-0021](0021-corpus-grows-only-by-design.md)
- **Evidence:** the `retire` implementation and its 11 tests (`Retire` in `test_reqmap.py`);
  the blast-radius data the command computes on this repo's own corpus

## Context

[ADR-0021](0021-corpus-grows-only-by-design.md) recorded that the corpus grows only: five paths
create a requirement file and none removes one, the single destructive path being `_wipe`, which
resets everything rather than pruning selectively. `NoShrinkVerb` enforced that asymmetry by
scanning the engine's own source for delete calls outside `_wipe`.

The asymmetry was never a principle. It was an observation with a reason attached: deleting a
requirement by hand leaves its tags behind in code, so the next gate reports dangling tags on
code whose purpose is now unrecorded — a worse state than the duplicate that prompted the
deletion. Removal was therefore left to a human who could be trusted to do both halves.

Two things changed. The corpus reached a size (221 requirements) where a wrong requirement is
routinely cheaper to retire than to keep and explain, and `v4.0.0` cuts five commands, whose
architecture requirements have to go somewhere. Doing that by hand, eleven times, is exactly the
error-prone sequence ADR-0021 was worried about.

## Decision

**`retire` exists, and the corpus can shrink.** The rules that make it safe are in the command,
not in its absence:

1. **The plan precedes the change.** Without `--apply` nothing is written; the blast radius —
   dependents, children, members, prose cross-references, and the files where the requirement
   was the only tagged one — is printed first.
2. **Dependents stop it.** A requirement anything still points at cannot be retired without an
   explicit `--force`. This is the half a tool can check and a human routinely forgets.
3. **Deprecating is the default.** `--apply` alone flips the status to `deprecated`: reversible,
   the code keeps working, and the gates already exempt that status. Removal needs `--delete`.
4. **The engine deletes only what it can prove is dead.** The requirement block, its lock
   entries, and the `implements:` / `tested-by:` / `verifies:` tag tokens for that id. Never a
   function body, a class, or a source file: deciding what code is now unreachable requires
   understanding the code, which this engine deliberately cannot do. The exclusive-file list is
   handed to whoever can.

`NoShrinkVerb` is kept and re-pointed: it still fails when a delete path appears anywhere except
the two functions this record sanctions (`_wipe` and `_remove_requirement_block`), so a third one
routes its author back here.

## Consequences

- A requirement can now be removed in one reviewable diff instead of a manual sequence across
  three files and two lock formats.
- The engine's destructive surface grew from one function to two. Both are named in a test that
  fails if a third appears.
- The dangling-tag failure ADR-0021 feared is now the thing `retire --delete` prevents by
  construction: it strips the tags in the same operation that removes the requirement.
- What the engine cannot do is now stated rather than avoided. A `retire --delete` leaves code
  that nothing references, listed by file, for a human or an agent to finish.

## Revisit when

- A retirement leaves a dangling tag in a real repository — the strip is then incomplete, not the
  policy wrong.
- `--force` becomes the habitual way to run the command, which would mean the dependent check is
  mis-scoped rather than protective.
