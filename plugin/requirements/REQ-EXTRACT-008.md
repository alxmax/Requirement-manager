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

## Input
- A code root and the already-discovered members (so tagged files are skipped).

## Description
On a legacy project, writing every requirement by hand is the barrier that stops
the tool ever being adopted. `extract` lowers it: it walks untagged source files
and proposes one `draft` per file. It cannot recover intent — only observed
behavior — so every proposal is `draft` and the body is left as TODO, never
canonized as correct. A cheap risk score (TODO/FIXME markers, suppressions, file
size) routes high-risk files to human review rather than auto-baseline.

## Output
- One `requirements/DRAFT-*.md` per untagged file, each tagged with a risk score and review hint.

## Acceptance (= tests)
- An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.
- A file already carrying a member tag is skipped.
- A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`.
- Re-running does not overwrite an existing draft.

## Links
- Used by: (auto)
## Members in code (auto)
