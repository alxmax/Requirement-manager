# ADR-0059 — A decision question is linted for whoever answers it

- **Status:** Accepted
- **Decided:** 2026-10-01
- **Evidence:** aggregate counts from one consumer corpus, measured before its owner rewrote the
  questions (numbers below); `text._verify_bullets` (`text.py:196`);
  `lintquestions._question_lint`; this repository and five local corpora, which hold no
  decision-form question; [ADR-0058](0058-an-answered-question-is-closed-where-it-stands.md);
  [ADR-0022](0022-no-minimum-requirement-size-check.md)

## Context

Since v8.10.1 a `## Verify intent` question can be asked as a decision: the question in bold,
one `a) …` line per option, then labelled lines (`*Default:* …`, `*Context:* …`). The person who
answers it is often not a developer: a client, a lawyer, someone who owns the data. The engine
read the form and said nothing about whether that person could read it.

One consumer corpus showed what unchecked authoring produces. Before its owner rewrote them, it
held 79 decision questions in 51 requirements:

- 17 of 79 bold questions ran two sentences or more, 24 words on average.
- 44 of 79 defaults named a `file:line`.
- 23 of 79 contexts held bold text.
- 39 of 51 requirements carried no marker saying who the reader is.
- 57 options were marked as recommended, and 1 recommendation named its source.
- 3 options handed the decision to somebody else.

## Decision

**Six warnings on a decision-form question, none an error, none promoted by `--strict`.**

1. **Scope.** The checks read the output of `_verify_bullets`, so an answered question
   (ADR-0058) and the authoring-hint line are already out. A bullet is a decision question when
   its first line starts with a bold span and a later line starts `a) `. A plain question gets
   no finding; without that limit one corpus would have drawn 56 `question-no-audience`
   warnings from plain questions.
2. **The checks:** `question-too-long`, `default-has-code`, `context-repeats-question`,
   `recommendation-without-source`, `option-defers-decision` and `question-no-audience`.
3. **Labels stay English in the engine.** `*Default:*`, `*Context:*`, `*(recommended)*`,
   `*Recommendation source:*` and `<!-- audience: … -->` are the canonical spellings, and
   `*Answer (YYYY-MM-DD):*` is read exactly as ADR-0058 says and is never translated. Another
   language's spellings come from nine `_config.json` keys (`LINT_QUESTION_*`); an empty list
   switches that check off. `i18n.py` is untouched.
4. **Only the question's limits are checked in code** (15 words, one sentence). The budgets for
   an option (12 words), the default (20), the context (30) and the whole question (80) live in
   the authoring rules as targets: field data shows overruns nobody could cut.
5. **Lint reads one more section.** ARCH-LINT-014 and REQ-LINT-864 said the prose checks
   read the Contract and the Acceptance; they now say the question checks read only
   `## Verify intent`. Both are confirmed contracts, so the change is accepted as drift.
6. **A new module,** `reqmap_engine/lintquestions.py`, imported by `lint`, so CORE counts it
   (ADR-0060).

## Consequences

- A person answering a question meets a short question, a default in plain words and the
  code references on a line of their own, or the author is told why not.
- A consumer with another language sees warnings until it lists its labels in `_config.json`.
  The changelog names the keys.
- A draft requirement is never linted (REQ-LINT-863), so a question sitting in a draft gets no
  finding.
- The sentence counter splits on "e.g.", so a question using it may warn once too often. The
  check name is 29 characters, wider than the lint output column; that is cosmetic.

## Evidence against ADR-0022's bar

ADR-0022 asks every new lint for two halves.

- **Fire rate:** 79 questions in 51 requirements on the consumer corpus before its rewrite, and
  none in this repository or in five local corpora. The restriction to the decision form is what
  keeps the other corpora silent.
- **Confirmation:** not met as ADR-0022 means it. The owner of the consumer corpus rewrote and
  merged all 79 questions, which is the author's acceptance of the findings, not an independent
  reviewer's sample. This record says so rather than counting it.

## Not done

- Reading the labels from an explicit allow-list in the decision-form reader: every count goes
  through that reader, so it needs its own multi-corpus measurement.
- `draft`, `author` and `decompose` writing the decision form: out of scope here.
- A leftover-text check and a "default names an option" check: no stable predicate across
  languages.
- Word-budget checks on an option, the default, the context and the whole question.
- Grouping findings by audience per question: the section-level marker is accepted.

## Revisit when

- An independent sample of findings confirms fewer than 8 in 10 for a check: remove that check
  and lower the budget with it.
- Decision questions sit mostly in drafts: move the checks to `clarify` instead of widening lint.
- Two consumers configure the same localized labels: ship them as defaults.
