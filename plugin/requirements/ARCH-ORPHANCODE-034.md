---
id: ARCH-ORPHANCODE-034
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v2.10
depends_on: [ARCH-CHECK-006, ARCH-SCAN-002]
satisfies: [SYS-GATE-102]
---

# Orphan-code warning

## Description
> A substantial new source file with no membership tag is invisible to every
> drift signal: it implements behavior no requirement describes, so "the spec
> covers the code" quietly stops being true as the repo grows. `health` counts
> untagged files ([[ARCH-COVERAGE-029]]) but nothing says it at the moment it
> matters — the commit gate. This warns, at gate time, about each sizeable
> program file that carries no tag, so the author links it, drafts a
> requirement for it, or marks it out of scope — the same nudge-not-block
> pattern as the untagged doc-bundle warning ([[ARCH-DOCBUNDLE-026]]).

Every bullet below is binding.
- The gate warns, without affecting its exit code, for each program file at least `ORPHAN_CODE_MIN_LOC` lines long carrying no membership tag and no `verifies:` tag — silenced by tagging the file or listing it in `.reqmapignore`. [[REQ-ORPHANCODE-888]] details the behaviour.

## Cases
CASE-1
  Given  an untagged program file at or above the LOC threshold
  When   the scan runs
  Then   the file is reported as orphan code
CASE-2
  Given  an untagged program file below the LOC threshold
  When   the scan runs
  Then   it is not reported
CASE-3
  Given  a program file at or above the threshold that carries a membership
         tag or a `verifies:` tag
  When   the scan runs
  Then   it is not reported
CASE-4
  Given  a large untagged non-program file (e.g. `.md`, `.html`)
  When   the scan runs
  Then   it is not reported
CASE-5
  Given  a large untagged program file matched by a `.reqmapignore` pattern
  When   the scan runs
  Then   it is not reported
CASE-6
  Given  a large untagged program file
  When   the gate runs (with and without `--strict`)
  Then   its output names the file with a warn line and the exit code is
         unchanged by this check

## Context
**Terms**
- a membership tag   a comment naming a requirement this file belongs to.
- a `verifies:` tag  a comment linking one test to one labelled acceptance
- criterion of a requirement.
- a program file     a source file whose extension is on the program list below.
- the scan walk      the shared file walk every command uses.

**Notes**
- The LOC threshold is a deterministic proxy for "substantial", not a semantic
  one: a 149-line untagged file stays silent. Tune `ORPHAN_CODE_MIN_LOC` in
  the engine, not per repo.
- Like [[ARCH-COVERAGE-029]] this measures tag PRESENCE, not quality: one
  hollow tag silences the file. Accepted — the signal is advisory precisely
  because presence is gameable.
- Granularity is per file: a tagged file with three untagged capabilities
  inside it is silent. `dupes`/`draft` remain the tools for that.

**Example**
- Dan vibe-codes a 400-line `exporter.py` in an afternoon and commits. The
  gate warns: "exporter.py: 400-line code file has no membership tag". He runs
  `reqmap.py new`, tags the file `# implements: REQ-EXPORT-036`, and the next
  contract drift on that requirement now lists his file to re-check.

**Current implementation**
- `orphan_code_files`, `ORPHAN_CODE_MIN_LOC`, `ORPHAN_CODE_EXTS` in
  `reqmap.py`, consumed by `cmd_check` — the covered set is derived from the
  already-scanned member map plus the `verifies:` coverage map, so the check
  adds no second tag scan; `cmd_check` emits one warn-only line per result.


--------------------


---
id: REQ-ORPHANCODE-888
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-ORPHANCODE-034]
---

# Warning on a sizeable file with no requirement link

## Description
> A big new source file with no membership tag implements behavior no requirement
> describes, and nothing said so at commit time — only `health` counted it later. The
> gate now warns on each program file past a line-count threshold with no membership
> or `verifies:` tag, so the author links it, drafts a requirement, or marks it out of
> scope; it never fails the build, at any flag combination, because tag presence alone
> is gameable.

Every bullet below is binding.
- The gate warns for each program file that carries no membership tag and no
  `verifies:` tag, once that file is at least `ORPHAN_CODE_MIN_LOC` physical
  lines long.
- A program file is one ending in `.py .js .ts .tsx .jsx .c .cc .cpp .h .hpp
  .java .go .rs`.
- A membership tag is one of `implements`, `tested-by`, `generated-from` and
  `validated-against`.
- The gate does not consider the prose, styling and config extensions
  (`.md .html .css .sql .yaml .yml`). Prose coverage is
  [[ARCH-DOCBUNDLE-026]]'s concern.
- The check honors `.reqmapignore` and the standard scan walk, so a repo can
  mark generated or vendored code out of scope rather than tag it.
- The walk itself — what it prunes, what it ignores, and how it treats a file it cannot
  read — is [[ARCH-SCAN-002]]'s contract, not restated here.
- The check is warn-only and never changes the gate's exit code, including
  under `--strict`. <!-- Rationale: the 2026-06-21 Senate audit on
  ARCH-COVERAGE-029 rejected coverage as a hard gate (hollow tags become the
  rational way to pass CI); this stays advisory at any flag combination. -->
- An author silences a file by tagging it or by adding it to `.reqmapignore`.
- There is no separate exemption mechanism.

## Cases
CASE-1 — an untagged file at the LOC threshold triggers the warning
  Given  an untagged 400-line `.py` file with no `implements`/`verifies` tag
  When   `gate` runs
  Then   it prints a warn line naming that file as orphan code, and the gate's exit code is unchanged, including under `--strict`

CASE-2 — only files on the program-extension list are considered
  Given  an untagged 400-line `.go` file and an untagged 400-line `.txt` file
  When   `gate` runs
  Then   the `.go` file is reported as orphan code and the `.txt` file is not

CASE-3 — any of the four membership tags silences the warning
  Given  four large untagged files, each carrying one of `implements`, `tested-by`,
         `generated-from`, `validated-against`
  When   `gate` runs
  Then   none of the four is reported as orphan code

CASE-4 — prose and config extensions are never checked for orphan code
  Given  a large untagged `.md` file and a large untagged `.yaml` file
  When   `gate` runs
  Then   neither is reported as orphan code

CASE-5 — a .reqmapignore pattern exempts a large untagged file
  Given  a large untagged `.py` file matched by a `.reqmapignore` pattern
  When   `gate` runs
  Then   it is not reported as orphan code, with no separate exemption mechanism beyond tagging or `.reqmapignore`

