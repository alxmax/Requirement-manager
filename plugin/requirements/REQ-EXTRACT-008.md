---
id: REQ-EXTRACT-008
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-SCAN-002]
superseded_by:
---

# Legacy extraction

> Bootstrap a registry on a brownfield codebase by proposing draft requirements from untagged code.

## WHAT — Contract (normative)
- It shall walk untagged source files (`.py`/`.js`/`.ts`/`.c`/`.cpp`) and propose one
  `requirements/DRAFT-*.md` per file, skipping files that already carry a member tag.
- Every proposal shall be `status: draft` with a TODO body — it captures observed behavior,
  never canonizing intent or correctness.
- It shall assign a cheap risk score (TODO/FIXME/HACK/XXX markers, suppressions, file size)
  and route a score ≥ 2 to `REVIEW`, else `auto-baseline`.
- Re-running shall not overwrite an existing draft; the requirements directory shall be
  created if absent and draft ids shall be path-aware so same-basename files do not collide.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- `extract` cannot recover intent; prefer `candidates` (read-only plan) before authoring.
  The draft body uses the same Contract/Acceptance section names as a real requirement so a
  promoted draft needs no reshaping.

## HOW — Acceptance (= tests)
- An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.
- A file already carrying a member tag is skipped.
- A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`.
- Re-running does not overwrite an existing draft; same-basename files in different dirs do not collide.

## WHERE — Current implementation
- `cmd_extract`, `_draft_id`, `_risk` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
