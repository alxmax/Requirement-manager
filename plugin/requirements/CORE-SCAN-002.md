---
id: CORE-SCAN-002
status: confirmed
layer: bus
owner: Alex
depends_on: []
superseded_by:
---

# Member discovery

> Find every place in the code that claims membership of a capability, by scanning for tags.

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
- A file containing `# implements: <ID>` produces a member `(implements, file, line)` under `<ID>`.
- All four roles are recognized; an unknown role string produces no member.
- Excluded directories (`.git`, `node_modules`, `__pycache__`, the SSOT `requirements/`) are not scanned.
- A duplicate tag on a single line is deduplicated; member paths are POSIX-relative.
- An unreadable file is skipped without aborting the scan.

## WHERE — Current implementation
- `scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
