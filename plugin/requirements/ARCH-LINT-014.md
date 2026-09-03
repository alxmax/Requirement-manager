---
id: ARCH-LINT-014
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.14
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-QUALITY-104]
---

# Requirement readability linter

## Description
> Requirement documents are only useful if people can actually read them. This is the
> automatic proofreader's frame: it decides which files get checked, which sections
> count, how severe a finding is, and whether the build fails. Without it, the
> clear-writing rules rely on someone re-reading every file by hand, and prose slowly
> degrades until the documents stop being worth opening.

Every bullet below is binding.
- `lint` reports readability problems and structure problems in requirement files, scoped to non-draft requirements, and writes no file. [[REQ-LINT-863]]
- The prose checks read the Contract and the Acceptance sections and no other section, skipping non-prose lines; `--strict` fails only on an error-severity finding. [[REQ-LINT-864]]

## Cases
CASE-1
  Given  a confirmed requirement whose body has no `## Cases` heading
  When   `lint` runs
  Then   it reports a `missing-section` error for that requirement

CASE-2
  Given  a draft requirement with a long sentence
  When   `lint` runs
  Then   it reports nothing for that requirement, because drafts are out of scope

CASE-3
  Given  a requirement whose `## Cases` heading is present but has no criteria beneath it
  When   `lint` runs
  Then   it reports an `empty-section` warning

CASE-4
  Given  a normative line with four conjunctions inside a fenced code block in the
         Acceptance section
  When   `lint` runs
  Then   it reports no `stacked-conditions` finding for that line

CASE-5
  Given  a corpus whose non-draft requirements all have both sections
  When   `lint --strict` runs
  Then   it returns zero even if warnings were printed

CASE-6
  Given  one non-draft requirement missing a section
  When   `lint --strict` runs
  Then   it returns a non-zero exit code

## Context
**Terms**
- non-draft    a requirement whose status is baseline, in-progress, implemented
- or confirmed — every status except `draft`.
- draft        a stub the engine wrote from a TODO item; nobody has reviewed it yet.
- Contract     the `## Description` section of a requirement file.
- Acceptance   the `## Cases` section of the same file.
- prose check  a check on how a sentence reads, not on which sections exist.
- error, warn  the two severity levels a finding can carry.

**Notes**
- The individual warn checks (stacked-conditions, statement-too-long,
  ac-count, over-scoped, file-spread, vague-term, redundant-modal) are a separate
  capability — [[ARCH-LINTCHECKS-025]] — running under the same `lint` command.
- Jargon-before-definition detection is intentionally out of scope for this version.
  Without a dictionary of project terms, any heuristic for "undefined jargon" produces
  too many false positives on prose that carries code references. It may arrive later
  as an opt-in check.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana finishes editing a requirement and runs `reqmap.py lint`. Warnings are advisory, so
  her build stays green. In CI she uses `lint --strict`, which fails the build the day a
  teammate deletes a requirement's Acceptance section — but never on a style warning.

**Current implementation**
- `cmd_lint` selects non-draft requirements, runs `lint_requirement` on each, prints
  findings grouped per requirement, and decides the exit code. `_lint_prose` extracts the
  prose lines of one section; `_clip` truncates finding text for display. The
  `missing-section` check reuses `_has_section` (shared with the gate in `cmd_check`).


--------------------


---
id: REQ-LINT-863
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINT-014]
---

# What lint checks and skips

## Description
> `lint` is read-only: it never edits a requirement, only reports on it, so running it carries
> no risk of losing work. Drafts are excluded because they are TODO stubs nobody has reviewed
> yet — linting them would produce noise about prose that is expected to be rough.

Every bullet below is binding.
- `lint` reports readability problems and structure problems in requirement files.
- `lint` writes no file. It only reads and prints.
- `lint` checks non-draft requirements only — status `baseline`, `in-progress`,
  `implemented` or `confirmed`. Drafts are TODO stubs, so linting them would only add noise.
- `lint` gives each finding one of two severities. A structural check reports an `error`;
  a prose check or a scope check reports a `warn`.
- The `missing-section` check reports an `error` when a non-draft requirement has no
  `## Description` section, or no `## Cases` section.
- The `empty-section` check reports a `warn` when one of those two headings is present but
  carries nothing under it: no clauses, no criteria. Such a section passes `missing-section`
  while documenting nothing.

## Cases
CASE-1 — one run surfaces both a structural and a readability finding
  Given  a confirmed requirement with no `## Cases` section and a Contract bullet joined by four "and"s
  When   `lint_requirement` runs on it
  Then   the findings include both a `missing-section` error and a `stacked-conditions` warning

CASE-2 — a default lint run leaves the requirements directory untouched
  Given  a requirements directory with findings to report and no `--decompose` flag
  When   `cmd_lint` runs
  Then   the directory's file listing is identical before and after the call

CASE-3 — a draft with a bad clause is silently skipped
  Given  a `draft` requirement whose Contract bullet is a 50-word run-on sentence
  When   `cmd_lint` runs
  Then   it exits 0 and its output names no findings for that requirement

CASE-4 — structural findings are error, prose findings are warn
  Given  a confirmed requirement with no `## Cases` section and a Contract line opening with a bare "It"
  When   `lint_requirement` runs on it
  Then   the `missing-section` finding carries severity `error` and the `anonymous-subject` finding carries `warn`

CASE-5 — a confirmed requirement with no Acceptance heading gets a missing-section error
  Given  a `confirmed` requirement body carrying a Description section but no `## Cases` heading
  When   `lint_requirement` runs on it
  Then   its findings include `("error", "missing-section")`

CASE-6 — a heading with no content beneath it gets an empty-section warning
  Given  a `confirmed` requirement whose Contract and Acceptance headings are both present but carry no bullets
  When   `lint_requirement` runs on it
  Then   its findings include an `empty-section` warning and no `missing-section` error


--------------------


---
id: REQ-LINT-864
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINT-014]
---

# Where the prose checks read from, and what fails a strict run

## Description
> A prose check that also read Notes or a code fence would flag text nobody meant as a
> readable sentence — a footgun explanation, a literal example, a `--strict` flag name. Scoping
> the checks to exactly the Contract and Acceptance sections, and skipping non-prose lines
> inside them, keeps every finding pointed at text an author actually needs to fix.

Every bullet below is binding.
- The prose checks read the Contract and the Acceptance sections, and no other section.
- The "Notes & limitations" section is exempt: only deep readers reach it, and it may stay dense.
- The prose checks skip lines that are not prose — headings, table rows, blockquotes, and any
  line inside a fenced code block.
- `lint` strips a bullet's leading marker before the checks read its text.
- `lint` returns zero by default, whatever it found.
- With `--strict`, `lint` returns non-zero when at least one finding has `error` severity.
- A warning never changes the exit code.

## Cases
CASE-1 — only the first matching Contract heading's text is linted
  Given  a short Contract clause followed by a `## Notes — contract addendum` heading holding a 50-word run-on line
  When   `_lint_prose` runs against "contract"
  Then   it returns only the short Contract line, never the Notes text

CASE-2 — a stacked-conditions line under Notes never fires
  Given  a `confirmed` requirement whose `## Notes & known limitations` section holds a line joined by four "and"s
  When   `lint_requirement` runs on it
  Then   no `stacked-conditions` finding is reported for that line

CASE-3 — a blockquote line with four joins is never linted as prose
  Given  a Contract section whose only content is a stacked-conditions-shaped blockquote line
         (`>` followed by four conjunctions)
  When   `_lint_prose` runs against "contract"
  Then   it returns an empty list — the `>` line is skipped, not read as prose

CASE-4 — a bulleted "It" clause still triggers anonymous-subject
  Given  a Contract bullet written as `- It creates the folder.`
  When   `lint_requirement` runs on it
  Then   it reports an `anonymous-subject` warning, proving the `^It` check saw the text after the `- ` marker was stripped

CASE-5 — a missing-section error does not fail a non-strict run
  Given  a confirmed requirement with no `## Cases` section
  When   `cmd_lint` runs without `--strict`
  Then   it returns exit code 0 despite the error-severity finding

CASE-6 — a missing section fails a strict run
  Given  a confirmed requirement with a Contract section but no `## Cases` heading
  When   `cmd_lint` runs with `--strict`
  Then   it returns exit code 1 because of the error finding; a warning alone would leave
         the exit code at 0

