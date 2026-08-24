---
id: REQ-LINT-014
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.14
---

# Requirement readability linter

> Requirement documents are only useful if people can actually read them. This is the
> automatic proofreader's frame: it decides which files get checked, which sections
> count, how severe a finding is, and whether the build fails. Without it, the
> clear-writing rules rely on someone re-reading every file by hand, and prose slowly
> degrades until the documents stop being worth opening.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     non-draft    a requirement whose status is baseline, in-progress, implemented
                  or confirmed — every status except `draft`.
     draft        a stub the engine wrote from a TODO item; nobody has reviewed it yet.
     Contract     the `## WHAT — Contract` section of a requirement file.
     Acceptance   the `## HOW — Acceptance` section of the same file.
     prose check  a check on how a sentence reads, not on which sections exist.
     error, warn  the two severity levels a finding can carry. -->

**What it reads**
- `lint` reports readability problems and structure problems in requirement files.
- `lint` writes no file. It only reads and prints.
- `lint` checks non-draft requirements only — status `baseline`, `in-progress`,
  `implemented` or `confirmed`. Drafts are TODO stubs, so linting them would only add noise.
- `lint` gives each finding one of two severities. A structural check reports an `error`;
  a prose check or a scope check reports a `warn`.

**The two structural checks**
- The `missing-section` check reports an `error` when a non-draft requirement has no
  `## WHAT — Contract` section, or no `## HOW — Acceptance` section.
- The `empty-section` check reports a `warn` when one of those two headings is present but
  carries nothing under it: no clauses, no criteria. Such a section passes `missing-section`
  while documenting nothing.

**What the prose checks look at**
- The prose checks read the Contract and the Acceptance sections, and no other section.
- The "Notes & limitations" section is exempt: only deep readers reach it, and it may stay dense.
- The prose checks skip lines that are not prose — headings, table rows, blockquotes, and any
  line inside a fenced code block.
- `lint` strips a bullet's leading marker before the checks read its text.

**Exit code**
- `lint` returns zero by default, whatever it found.
- With `--strict`, `lint` returns non-zero when at least one finding has `error` severity.
- A warning never changes the exit code.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The individual warn checks (long-sentence, stacked-conditions, statement-too-long,
  ac-count, over-scoped, file-spread, vague-term, redundant-modal) are a separate
  capability — [[REQ-LINTCHECKS-025]] — running under the same `lint` command.
- Jargon-before-definition detection is intentionally out of scope for this version.
  Without a dictionary of project terms, any heuristic for "undefined jargon" produces
  too many false positives on prose that carries code references. It may arrive later
  as an opt-in check.

## HOW — Acceptance (= tests)
AC-1
  Given  a confirmed requirement whose body has no `## HOW — Acceptance` heading
  When   `lint` runs
  Then   it reports a `missing-section` error for that requirement

AC-2
  Given  a draft requirement with a long sentence
  When   `lint` runs
  Then   it reports nothing for that requirement, because drafts are out of scope

AC-3
  Given  a requirement whose `## HOW — Acceptance` heading is present but has no criteria beneath it
  When   `lint` runs
  Then   it reports an `empty-section` warning

AC-4
  Given  a long sentence that sits inside a fenced code block in the Acceptance section
  When   `lint` runs
  Then   it reports no `long-sentence` finding for that line

AC-5
  Given  a corpus whose non-draft requirements all have both sections
  When   `lint --strict` runs
  Then   it returns zero even if warnings were printed

AC-6
  Given  one non-draft requirement missing a section
  When   `lint --strict` runs
  Then   it returns a non-zero exit code

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana finishes editing a requirement and runs `reqmap.py lint`. Warnings are advisory, so
  her build stays green. In CI she uses `lint --strict`, which fails the build the day a
  teammate deletes a requirement's Acceptance section — but never on a style warning.

## WHERE — Current implementation
- `cmd_lint` selects non-draft requirements, runs `lint_requirement` on each, prints
  findings grouped per requirement, and decides the exit code. `_lint_prose` extracts the
  prose lines of one section; `_clip` truncates finding text for display. The
  `missing-section` check reuses `_has_section` (shared with the gate in `cmd_check`).

## Links
- Used by: (auto)
## Members in code (auto)
