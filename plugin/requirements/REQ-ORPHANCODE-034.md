---
id: REQ-ORPHANCODE-034
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [REQ-CHECK-006, CORE-SCAN-002]
superseded_by:
milestone: v2.10
---

# Orphan-code warning

> A substantial new source file with no membership tag is invisible to every
> drift signal: it implements behavior no requirement describes, so "the spec
> covers the code" quietly stops being true as the repo grows. `health` counts
> untagged files ([[REQ-COVERAGE-029]]) but nothing says it at the moment it
> matters — the commit gate. This warns, at gate time, about each sizeable
> program file that carries no tag, so the author links it, drafts a
> requirement for it, or marks it out of scope — the same nudge-not-block
> pattern as the untagged doc-bundle warning ([[REQ-DOCBUNDLE-026]]).

## WHAT — Contract (normative)
- The gate shall warn for each program-logic source file (extensions: `.py .js
  .ts .tsx .jsx .c .cc .cpp .h .hpp .java .go .rs`) whose physical line count
  is at least `ORPHAN_CODE_MIN_LOC` and that carries no membership tag
  (`implements`, `tested-by`, `generated-from`, `validated-against`) and no
  per-criterion `verifies:` tag.
- Prose, styling and config extensions (`.md .html .css .sql .yaml .yml`)
  shall not be considered — prose coverage is [[REQ-DOCBUNDLE-026]]'s concern.
- It shall honor `.reqmapignore` and the standard scan walk (prune `.git`,
  `node_modules`, `__pycache__`, the SSOT `requirements/`), so a repo can mark
  generated or vendored code out of scope rather than tag it.
- An unreadable file shall be skipped.
- The check shall be warn-only and shall never change the gate's exit code —
  including under `--strict`. <!-- Rationale: the 2026-06-21 Senate audit on
  REQ-COVERAGE-029 rejected coverage as a hard gate (hollow tags become the
  rational way to pass CI); this stays advisory at any flag combination. -->
- A file shall be silenced by tagging it or adding it to `.reqmapignore`;
  there shall be no separate exemption mechanism.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent; severity ceiling settled by the
  REQ-COVERAGE-029 Senate audit.

## WHAT — Notes & known limitations (informative)
- The LOC threshold is a deterministic proxy for "substantial", not a semantic
  one: a 149-line untagged file stays silent. Tune `ORPHAN_CODE_MIN_LOC` in
  the engine, not per repo.
- Like [[REQ-COVERAGE-029]] this measures tag PRESENCE, not quality: one
  hollow tag silences the file. Accepted — the signal is advisory precisely
  because presence is gameable.
- Granularity is per file: a tagged file with three untagged capabilities
  inside it is silent. `dupes`/`draft` remain the tools for that.

## HOW — Acceptance (= tests)
AC-1
  Given  an untagged program file at or above the LOC threshold
  When   the scan runs
  Then   the file is reported as orphan code
AC-2
  Given  an untagged program file below the LOC threshold
  When   the scan runs
  Then   it is not reported
AC-3
  Given  a program file at or above the threshold that carries a membership
         tag or a `verifies:` tag
  When   the scan runs
  Then   it is not reported
AC-4
  Given  a large untagged non-program file (e.g. `.md`, `.html`)
  When   the scan runs
  Then   it is not reported
AC-5
  Given  a large untagged program file matched by a `.reqmapignore` pattern
  When   the scan runs
  Then   it is not reported
AC-6
  Given  a large untagged program file
  When   the gate runs (with and without `--strict`)
  Then   its output names the file with a warn line and the exit code is
         unchanged by this check

## Example — in practice (optional, non-binding)
- Dan vibe-codes a 400-line `exporter.py` in an afternoon and commits. The
  gate warns: "exporter.py: 400-line code file has no membership tag". He runs
  `reqmap.py new`, tags the file `# implements: REQ-EXPORT-036`, and the next
  contract drift on that requirement now lists his file to re-check.

## WHERE — Current implementation
- `orphan_code_files`, `ORPHAN_CODE_MIN_LOC`, `ORPHAN_CODE_EXTS` in
  `reqmap.py`, consumed by `cmd_check` — the covered set is derived from the
  already-scanned member map plus the `verifies:` coverage map, so the check
  adds no second tag scan; `cmd_check` emits one warn-only line per result.

## Links
- Used by: (auto)
## Members in code (auto)
