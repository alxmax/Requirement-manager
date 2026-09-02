---
id: REQ-ATOMICITY-049
status: confirmed    # draft | baseline | in-progress | implemented | confirmed | deprecated
layer: feature       # bus | feature | need | aggregate
owner: Alex
priority: should-have
depends_on: [CORE-PARSE-001, REQ-LINT-014]
superseded_by:
---

# Statement atomicity

> A requirement file here is a capability dossier, not one sentence — its Contract holds
> many clauses, and each clause is the real unit a test answers to. This says what makes
> a clause well-formed: one obligation, verifiable on its own. It also ships a word-count
> heuristic that points a reader at clauses worth re-reading. The two are deliberately
> not the same thing, and the second never decides the first.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a clause          one bullet in a requirement's Contract section — the unit a test
                       answers to.
     an obligation     one thing the system does, or one constraint it holds to.
     atomicity         the property of a clause carrying exactly one obligation.
     decomposition     splitting one clause into several, each stating one obligation,
                       rather than shortening the prose.
     the threshold     `LINT_STATEMENT_WORDS`, the word count above which a clause is
                       reported. -->

**The normative rule**
- A clause in a Contract section describes a single obligation that can be verified independently.
- A clause carrying two independent obligations counts as two clauses, not one.
- Atomicity is judged by a human reader. No check in the engine determines it.

**The `statement-size` heuristic**
- A clause normally holds no more than `LINT_STATEMENT_WORDS` words, default 75.
- The `statement-size` check reports a Contract clause above that threshold.
- The threshold is advisory. A clause above it stays valid, and the exit code is unchanged.
- `lint_exempt: [statement-size]` silences the check for one requirement.

**What the check measures, and what it does not**
- The `statement-size` check measures textual size, never semantic atomicity.
- A short clause may carry several independent obligations and still pass the check.
- A finding asks the author to re-read the clause for decomposition, and asserts no defect.

**How a clause is counted**
- The check counts words after each backticked code span is replaced by one token.
- A nested sub-bullet is counted as its own clause, because it states its own obligation.
- The check reads the Contract section only. Acceptance prose is judged by `long-sentence`.

## WHAT — Verify intent (open questions for the human)
- None — authored from stated intent, not reconstructed from code.

## HOW — Acceptance (= tests)
AC-1
  Given  a Contract clause of 80 plain words
  When   `lint` runs
  Then   exactly one `statement-size` finding names that clause, and the exit code is unchanged
AC-2
  Given  a Contract clause of 70 plain words
  When   `lint` runs
  Then   no `statement-size` finding is reported for it
AC-3
  Given  a Contract clause of 80 words, 60 of them inside one backticked span
  When   `lint` runs
  Then   the span counts as one word, the clause counts 21, and nothing is reported
AC-4
  Given  a parent clause of 40 words carrying a nested sub-bullet of 80 words
  When   `lint` runs
  Then   the sub-bullet alone is reported, and the parent is not
AC-5
  Given  a requirement carrying `lint_exempt: [statement-size]` and an over-threshold clause
  When   `lint` runs
  Then   no `statement-size` finding is reported for that requirement
AC-6
  Given  a 20-word Contract clause stating two independent obligations
  When   `lint` runs
  Then   no `statement-size` finding is reported, because the check reads size and not
         atomicity

## Context (non-binding)
**Notes**
- The two halves are not the same kind of statement, and the file keeps them apart on
  purpose. Atomicity is the **normative rule**: a clause carrying two obligations is
  malformed, whoever notices it. The 75 words are a **heuristic threshold**: a coarse
  proxy for clause complexity, advisory only, and never a determination of atomicity.
  Promoting the threshold into a validity criterion would assert something the engine
  cannot observe.
- The rule as the author stated it: *"A clause shall describe a single independently
  verifiable obligation"* (normative), and *"A clause should normally not exceed 75
  words"* (heuristic) — with *"Exceeding 75 words does not make a clause invalid and
  shall not affect the lint exit code"* and *"shall not be interpreted as a determination
  of atomicity."* The Contract restates these without `shall`/`should`, because the
  section header already binds every clause and `redundant-modal` flags the modal
  (REQ-LINTCHECKS-025).
- The epistemic limit is stated in the Contract rather than left here, so no later reader
  or tool can promote the heuristic into the rule. AC-6 pins it as behaviour: a short
  clause with two obligations passes, and that is correct, not a gap to close.
- Measured on this corpus before the check was specified: 586 Contract clauses across 52
  requirements, mean 18.4 words, median 16, p90 31, **max 62**. At a 75-word threshold
  **0 of 586 clauses (0.0%) are over**, in 0 of 52 files. So the heuristic ships as a line
  already held, not as a defect hunt — its value is the clause written next year.
- The two checks that already read this text measure a different unit, which is why this
  one could not reuse them. `long-sentence` (25 words) and `statement-too-long` (22 words)
  run over `_lint_prose`, which yields physical LINES. These files are hard-wrapped near 95
  columns, so the longest line `_lint_prose` produced for `REQ-CHECK-006` is 15 words, and
  both checks report **0** across the corpus — not because the prose is short, but because a
  clause is never seen whole. `statement-size` joins continuation lines first
  (`_contract_clauses`), so an 80-word clause wrapped over six lines is visible to it and
  invisible to them. The per-line checks are left alone on purpose: widening their unit would
  flip the corpus from 0 warnings to many, on confirmed requirements, which is a separate
  decision.
- At 0% the heuristic sits below ADR-0016's 5-40% pre-ship fire-rate bar. That bar gates
  checks proposed to *find* problems; an advisory line-holder is a different instrument,
  which is why it ships warn-only with an exemption rather than as a gate (ADR-0002,
  ADR-0014).

**Example**
- Ana writes a clause that grows over two releases into 90 words covering both how a token
  is issued and how it is revoked. `lint` reports `statement-size`. She splits it into two
  clauses, each with its own acceptance criterion, and both become separately testable.
  Had she instead only trimmed adjectives to get under 75, the finding would clear while
  the clause still carried two obligations — which is why the finding asks for a re-read
  rather than for a shorter sentence, and why passing the check proves nothing about
  atomicity.

**Current implementation**
- `LINT_STATEMENT_WORDS`, `_clause_words` and `_contract_clauses` in `reqmap.py`. The
  `statement-size` block in `lint_requirement` appends one warn finding per over-threshold
  clause, carrying `clause_n` and `clause_text` so [[REQ-DECOMPOSE-050]] scaffolds from the
  same parse instead of re-reading the file. `_clause_words` collapses a backticked span to a
  bare token with no padding, because `" x "` split trailing punctuation into a second word
  and inflated every such clause by one.

## Links
- Used by: (auto)
## Members in code (auto)
