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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a membership tag   a comment naming a requirement this file belongs to.
     a `verifies:` tag  a comment linking one test to one labelled acceptance
                        criterion of a requirement.
     a program file     a source file whose extension is on the program list below.
     the scan walk      the shared file walk every command uses. -->

**What it warns about**
- The gate warns for each program file that carries no membership tag and no
  `verifies:` tag, once that file is at least `ORPHAN_CODE_MIN_LOC` physical
  lines long.
- A program file is one ending in `.py .js .ts .tsx .jsx .c .cc .cpp .h .hpp
  .java .go .rs`.
- A membership tag is one of `implements`, `tested-by`, `generated-from` and
  `validated-against`.
- The gate does not consider the prose, styling and config extensions
  (`.md .html .css .sql .yaml .yml`). Prose coverage is
  [[REQ-DOCBUNDLE-026]]'s concern.

**What it skips**
- The check honors `.reqmapignore` and the standard scan walk, so a repo can
  mark generated or vendored code out of scope rather than tag it.
- The scan walk prunes `.git`, `node_modules`, `__pycache__` and the SSOT
  `requirements/` directory.
- The check skips a file it cannot read.

**Severity**
- The check is warn-only and never changes the gate's exit code, including
  under `--strict`. <!-- Rationale: the 2026-06-21 Senate audit on
  REQ-COVERAGE-029 rejected coverage as a hard gate (hollow tags become the
  rational way to pass CI); this stays advisory at any flag combination. -->

**Silencing a file**
- An author silences a file by tagging it or by adding it to `.reqmapignore`.
- There is no separate exemption mechanism.

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
