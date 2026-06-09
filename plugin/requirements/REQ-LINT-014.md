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

> Requirement documents are only useful if people can actually read them. This is an
> automatic proofreader: it flags writing that has drifted into hard-to-follow territory —
> missing key sections, sentences that run too long, lines that pile up too many conditions
> at once, or a list of acceptance tests that is suspiciously short or bloated. Without it,
> the clear-writing rules rely on someone re-reading every file by hand, and prose slowly
> degrades until the documents stop being worth opening.

## WHAT — Contract (normative)
- The `lint` command shall report readability and structure violations on requirement files. It writes nothing and is read-only.
- It shall scope its checks to non-draft requirements only (status `baseline`, `in-progress`, `implemented`, or `confirmed`). Drafts are auto-extracted TODO stubs, so linting them would only add noise.
- It shall run two kinds of check. A structural check is severity `error`. A prose-readability check is severity `warn`.
- The `missing-section` check (error) shall flag a non-draft requirement that lacks a `## WHAT — Contract` section or a `## HOW — Acceptance` section.
- The `long-sentence` check (warn) shall flag any sentence in the Contract or Acceptance section longer than the word threshold (`LINT_SENTENCE_WORDS`, default 35).
- The `stacked-conditions` check (warn) shall flag a normative line that piles up too many clauses joined by conjunctions (`LINT_STACKED_CONNECTORS`, default 3 conjunctions).
- The `statement-too-long` check (warn) shall flag a Contract bullet that exceeds `LINT_CONTRACT_WORDS` (default 30) words and spans more than one sentence.
- The `ac-count-low` check (warn) shall flag an Acceptance section holding one or two criteria (fewer than `LINT_AC_MIN`, default 3).
- The `ac-count-high` check (warn) shall flag an Acceptance section holding more than `LINT_AC_MAX` (default 7) criteria, counted as `- ` bullets or `AC-N` labelled blocks.
- The `over-scoped` check (warn) shall flag a requirement whose Contract exceeds `LINT_CONTRACT_MAX` (default 10) clauses AND whose Acceptance exceeds `LINT_AC_MAX` — a composite signal that several capabilities are bundled into one. Requiring both axes at once keeps false positives near zero.
- The `empty-section` check (warn) shall flag a Contract or Acceptance heading that is present but carries no clauses or criteria — it would otherwise pass `missing-section` while documenting nothing.
- The `vague-term` check (warn) shall flag a Contract bullet using a word from the closed `LINT_VAGUE_TERMS` set — untestable quality words like `appropriate`, `robust`, or `user-friendly`.
- Before the `vague-term` scan, backticked code spans are stripped, and one finding is emitted per distinct term.
- Prose checks shall look only at the Contract and Acceptance sections. The "Notes & limitations" section is exempt, because only deep readers reach it and it may stay dense.
- Prose checks shall skip non-prose lines: headings, table rows, blockquotes, and any line inside a fenced code block. A bullet's leading marker is stripped before its text is checked.
- It shall be exit-neutral by default (always returns zero). With `--strict` it shall return non-zero when at least one error-severity finding exists. A warning never changes the exit code.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- `statement-too-long` deliberately ignores a single over-long sentence (that is `long-sentence`'s job), so the two checks never flag the same line twice.
- Jargon-before-definition detection is intentionally out of scope for this version. Without a dictionary of project terms, any heuristic for "undefined jargon" produces too many false positives on prose that carries code references. It may arrive later as an opt-in check.
- Sentence splitting is a deterministic split on `.`, `!`, and `?`. It is crude — an abbreviation can over-split — but it never reads code and only feeds a word count, so the worst case is a missed long sentence, not a false alarm on code.
- The thresholds are module constants, not configurable from the command line. A single well-named constant is enough until a real project needs a different value.

## HOW — Acceptance (= tests)
- Given a confirmed requirement whose body has no `## HOW — Acceptance` heading, when `lint` runs, then it reports a `missing-section` error for that requirement.
- Given a draft requirement with a long sentence, when `lint` runs, then it reports nothing for that requirement, because drafts are out of scope.
- Given a confirmed requirement with a 40-word sentence in its Contract section, when `lint` runs, then it reports a `long-sentence` warning naming the word count.
- Given a confirmed requirement with a normative line that joins four clauses with "and", when `lint` runs, then it reports a `stacked-conditions` warning.
- Given a confirmed requirement with a Contract bullet over 30 words spanning two sentences, when `lint` runs, then it reports a `statement-too-long` warning; given a single 40-word sentence, it reports only `long-sentence` and no `statement-too-long`.
- Given an Acceptance section with one criterion, when `lint` runs, then it reports `ac-count-low`; given one with eight criteria, it reports `ac-count-high`; given one with four, it reports neither.
- Given a requirement over both ceilings (more than ten contract clauses and more than seven acceptance criteria), when `lint` runs, then it reports an `over-scoped` warning; given one over only a single ceiling, it reports no `over-scoped`.
- Given a requirement whose `## HOW — Acceptance` heading is present but has no criteria beneath it, when `lint` runs, then it reports an `empty-section` warning.
- Given a Contract bullet containing "appropriate" and "user-friendly", when `lint` runs, then it reports two `vague-term` warnings; a backticked span and a precise bullet report none.
- Given a long sentence that sits inside a fenced code block in the Acceptance section, when `lint` runs, then it reports no `long-sentence` finding for that line.
- Given a corpus whose non-draft requirements all have both sections, when `lint --strict` runs, then it returns zero even if warnings were printed.
- Given one non-draft requirement missing a section, when `lint --strict` runs, then it returns a non-zero exit code.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana finishes editing a requirement and runs `reqmap.py lint`. It warns that one Contract
  bullet is a 44-word sentence and another line stacks four "and" clauses. She splits both
  and reruns — the warnings are gone. In CI she uses `lint --strict`, which stays green on
  warnings but fails the build the day a teammate deletes a requirement's Acceptance section.

## WHERE — Current implementation
- `cmd_lint`, `lint_requirement`, `_lint_prose`, `_sentences`, `_count_ac` and `_clip` in `reqmap.py` — `cmd_lint` selects non-draft requirements, runs `lint_requirement` on each, prints findings grouped per requirement, and decides the exit code. `_lint_prose` extracts the prose lines of one section; `_sentences` splits a line for the word-count checks; `_count_ac` counts acceptance criteria. The `missing-section` and `ac-count` checks reuse `_has_section` (shared with the gate in `cmd_check`). The `over-scoped` check pairs the Contract clause count (`_bullets`) with `_count_ac` against `LINT_CONTRACT_MAX`/`LINT_AC_MAX`.

## Links
- Used by: (auto)
## Members in code (auto)
