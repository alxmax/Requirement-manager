---
id: CORE-SCAN-002
status: confirmed
layer: bus
owner: Alex
depends_on: []
superseded_by:
milestone: v1.00
---

# Member discovery

> Developers mark a piece of code as belonging to a capability by writing a short note in a
> comment, like "implements: LOGIN-001." This reads through all the project's source files
> and collects every one of those notes, so the tool always knows which code answers to
> which requirement. Without it, the link between a written requirement and the real code
> behind it would have to be tracked by hand, and would quickly fall out of date.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a tag             an inline comment of the form `role: <ID>` marking a piece of
                       code as belonging to a capability.
     a role            what that code does for the capability.
     a member          one recorded `(role, file, line)` place in the code.
     the SSOT dir      the `requirements/` directory itself.
     a left-boundary   a check that the word before `implements:` really ends there,
     guard             so `reimplements:` is not read as a tag. -->

**What it finds**
- `scan_members` walks a code root and, in every source file with a known extension,
  finds the inline tags.
- `scan_members` returns `cap_id -> [(role, relative_file, line), ...]`.
- A role is one of `implements`, `generated-from`, `validated-against` and `tested-by`.
- A tag ID matches `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`.
- A left-boundary guard prevents a substring match such as `reimplements:` or
  `x-implements:` being read as a real tag.
- The same `(role, ID)` appearing twice on one line is recorded once.
- File paths are reported repo-root-relative, with POSIX separators.

**Tags naming several requirements**
- A single tag may bind several requirements through a comma-separated id list,
  written `role: <ID>, <ID>, ...`.
- Each id in that list is recorded as a member of the same `(role, file, line)`.
- A whole-system doc generated from many requirements (`generated-from: A, B, C`) is
  therefore a member of each, and drifts when ANY of them changes.

**What it skips**
- `.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory are
  skipped.
- The SSOT directory is matched by realpath, so a source package merely named
  `requirements/` is still scanned.
- Paths matching `.reqmapignore` are excluded.
- An unreadable file is skipped without aborting the scan.

- `scan_all` returns the members, the per-criterion coverage and the verification levels
  from a single walk, and each result equals what the three separate scanners return.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The member list is discovered, never hand-maintained — that is the first thing to rot.

## HOW — Acceptance (= tests)
AC-1
  Given  a file containing `# implements: <ID>`
  When   the scan runs
  Then   a member `(implements, file, line)` is recorded under `<ID>`

AC-2
  Given  tags using each of the four roles and one unknown role string
  When   the scan runs
  Then   all four roles are recognized and the unknown role produces no member

AC-3
  Given  files under `.git`, `node_modules`, `__pycache__` or the SSOT `requirements/`
  When   the scan runs
  Then   those directories are not scanned

AC-4
  Given  a duplicate tag on a single line
  When   the scan runs
  Then   it is deduplicated and member paths are POSIX-relative

AC-5
  Given  an unreadable file in the tree
  When   the scan runs
  Then   the file is skipped without aborting the scan

AC-6
  Given  a tag `generated-from: <ID-A>, <ID-B>` listing several ids
  When   the scan runs
  Then   the file is recorded as a member of both <ID-A> and <ID-B>

AC-7
  Given  any code tree
  When   `scan_all` runs
  Then   its three results equal those of `scan_members`, `scan_ac_verifies` and
         `scan_test_levels` run separately, and every file is opened once

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana adds a comment `# implements: CORE-SCAN-002` at the top of a new file and saves it.
  The scan walks the project, skipping folders like `node_modules`, and reports that file —
  with its exact path and line number — as a member of CORE-SCAN-002. A stray comment
  reading `reimplements:` nearby is correctly ignored and never mistaken for a real tag.

## WHERE — Current implementation
- `scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE`, `TAG_LIST_RE`, `_findall_tags` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
