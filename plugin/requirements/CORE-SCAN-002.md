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
- It shall walk a code root and, for every source file in a known extension, find inline
  tags of the form `role: <ID>` where role is one of `implements`, `generated-from`,
  `validated-against`, `tested-by`, returning `cap_id -> [(role, relative_file, line), ...]`.
- Tag IDs shall match `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`; a left-boundary guard shall prevent
  substring matches such as `reimplements:` or `x-implements:` being read as real tags.
- The same `(role, ID)` appearing twice on one line shall be recorded once.
- File paths shall be reported repo-root-relative with POSIX separators.
- `.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory shall be
  skipped, the latter matched by realpath so a source package merely named `requirements/`
  is still scanned. Paths matching `.reqmapignore` shall be excluded.
- An unreadable file shall be skipped without aborting the scan.

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

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana adds a comment `# implements: CORE-SCAN-002` at the top of a new file and saves it.
  The scan walks the project, skipping folders like `node_modules`, and reports that file —
  with its exact path and line number — as a member of CORE-SCAN-002. A stray comment
  reading `reimplements:` nearby is correctly ignored and never mistaken for a real tag.

## WHERE — Current implementation
- `scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
