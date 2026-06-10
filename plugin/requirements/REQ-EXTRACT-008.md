---
id: REQ-EXTRACT-008
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-SCAN-002]
superseded_by:
milestone: v1.06
---

# Legacy extraction

> When an existing project has lots of code but no requirements written down, this gives you
> a running start: it reads each untagged file and writes a rough draft requirement for it,
> clearly marked as a draft so no one mistakes a guess for a settled decision. Without it,
> someone would have to sit down and describe every existing capability from scratch before
> the tool was useful on an older project. Spec and prompt documents get the same treatment
> from the companion capability [[REQ-PROSE-024]].

## WHAT — Contract (normative)
- It shall walk untagged source files (`.py`/`.js`/`.ts`/`.c`/`.cpp`) and propose one
  `requirements/DRAFT-*.md` per file, skipping files that already carry a member tag.
- It shall honor `.reqmapignore` (the same fnmatch globs `scan` respects): a file matching an
  ignore pattern is never drafted — notably the vendored `scripts/reqmap.py` engine itself.
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
- Prose (`.md`/`.html`) classification and drafting is a separate capability —
  [[REQ-PROSE-024]] — running under the same `extract` command.

## HOW — Acceptance (= tests)
- An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.
- A file already carrying a member tag is skipped.
- A file matching a `.reqmapignore` pattern is skipped (no draft proposed for it).
- A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`.
- Re-running does not overwrite an existing draft; same-basename files in different dirs do not collide.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs extract on a brownfield repo. For each untagged source file it drops a
  `DRAFT-*.md` capturing what the file appears to do; one file full of `TODO` and `FIXME`
  markers scores higher risk and is flagged `REVIEW`. The engine's own `reqmap.py` is in
  `.reqmapignore`, so it is skipped — leaving Ana a pile of starting points to promote
  into real requirements.

## WHERE — Current implementation
- `cmd_extract`, `_draft_id`, `_risk` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
