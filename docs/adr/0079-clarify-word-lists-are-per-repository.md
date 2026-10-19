# ADR-0079 — `clarify`'s word lists are per repository

- **Status:** Accepted. Extends [ADR-0078](0078-clarify-vague-term-drops-quantity-words.md)
  and [ADR-0075](0075-clarify-retires-number-without-unit.md), whose samples were all drawn
  from this repository, which is written in English.
- **Decided:** 2026-10-19
- **Evidence:** the current engine run read-only over three consumer corpora written in
  Romanian: 935 requirements, 1,579 `clarify` questions. Per rule, 20 questions drawn
  across the three (seed `20261019`), or all of them where there were 20 or fewer, read
  against the requirement's own clauses and cases. Rates are k/n with a Wilson 95%
  interval; a requirement shared by two corpora was drawn as often as it appeared.
  - `vague-term`: 19 questions, 0 real (0% to 17%). Every one fired on an English token in
    Romanian prose: an enum value, a mode name, "etc." before a list a constant defines,
    "best-effort" defined in the same clause.
  - `no-failure-case`: 736 questions, on most of the corpora. 5 of 20 real (11% to 47%).
    Most of the false ones had cases that prove the failure path in Romanian words or by
    status code (a refusal, a missing value, `400`, `404`), none on the English list.
  - `case-monoculture`: the Given head was read with an ASCII-only pattern, so a word
    with a diacritic lost its first letters. The rule still compared heads consistently,
    and 11 of 20 were real (34% to 74%).
  - For scale, on the same corpora `clause-without-case` was 19 of 20 real (76% to 99%)
    and `over-scoped` 16 of 20 (58% to 92%). Neither reads a word list.

## Context

ADR-0072, ADR-0075 and ADR-0078 tuned the word rules on this repository's corpus, the
only one measured. The lists were constants in `clarify.py`, so a consumer writing in
another language could neither add its own failure words nor remove English hedges that
only ever match borrowed tokens. `_config.json` already carries per-repository word
lists for the decision-question lint (`LINT_QUESTION_*`, ADR-0059), with the same shape.

## Decision

- `CLARIFY_HEDGES` and `CLARIFY_FAILURE_WORDS` move to `config.py` and become
  `CONFIG_KEYS` entries. A list set in `_config.json` replaces the default, as the
  `LINT_QUESTION_*` lists do; replacing rather than extending lets a repository drop the
  English words it never uses. Both are compared without regard to case.
- The hedge pattern is compiled per list rather than once at import, since a config can
  change it after the module loads.
- `_given_head` reads a letter in any script.
- The defaults do not change, so this repository's questions are the same before and
  after.

## Consequences

- A consumer writing in another language sets two lists and gets `no-failure-case`
  questions about cases that really lack a failure path. Without setting them nothing
  changes for it either.
- The rates above are for the English lists on Romanian text. The precision of a
  repository's own lists is unmeasured until it samples them.
- The basis of a rule (`count` or `wording`) is still fixed by the engine, although
  `clause-without-case` was far more precise on these corpora than on this one. That is
  left for a decision of its own.

## Revisit when

- A corpus sets its own lists and samples 20 questions of either rule: under 8 real, the
  rule is no better for a translated list than for an English one.
- A rule's precision differs this much between corpora again, which would argue for a
  per-repository basis.
