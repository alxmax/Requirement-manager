# ADR-0071 — `clarify` tells a value from a quantity and a handed-on clause from its own

- **Status:** Accepted. Amends the number in [ADR-0070](0070-questions-get-a-page-of-their-own.md).
- **Decided:** 2026-10-17
- **Evidence:** this corpus measured before and after on the same 323 requirements, from
  the committed `_map.json`. `clarify` asked 507 questions before and 425 after: 151 to 127
  resting on a count, 356 to 298 on a word list. By rule: `number-without-unit` 47 → 9,
  `vague-term` 46 → 26, `clause-without-case` 115 → 98, `over-scoped` 36 → 29; the other
  four rules are unchanged. `python scripts/check_engine_budget.py` on this commit: core
  6,640 logical lines.

## Context

Reading the questions one by one showed most of them in three rules were not questions:

- `number-without-unit` asked for the unit of values: `` `>=3.9` ``, `2026-06-21`,
  `U+2028`, "default 150" (the unit is named with the setting), "exits with code 0". It
  missed units it was given: "12-character", "50,000 characters", "3+ letters",
  "4 blocks". 38 of its 47 questions were one of these.
- `vague-term` matched substrings and quoted words: "smaller" was "small", a cited
  `` `appropriate` `` was a hedge, and 17 of 25 hits on "many" were "how many", which asks
  for a count.
- `clause-without-case` and `over-scoped` counted architecture bullets that only point at
  the child carrying their cases (`… [[REQ-X-001]]`). REQ-CLARIFY-956 already named this
  as the counter's known blind spot.

Each was a property of the rule, not of the requirement it fired on, so answering them in
the requirements would have meant 82 edits that changed nothing true.

## Decision

- A number inside a code span, a date, a version, a code point, and the number after
  "default" or an exit-code phrase are values, not quantities. A unit may follow a hyphen
  or a plus sign, a number grouped in thousands is one number, and the unit list gains
  the counted nouns this domain uses (words, letters, columns, blocks, cases, members,
  dependents, requirements).
- A hedge counts only as a whole word outside a code span, and "how many" is not a hedge.
- A clause that ends by naming another requirement hands its cases to it; neither count
  holds it.
- "retries 3 times" still asks for a unit. REQ-CLARIFY-956's CASE-2 says so, and a closed
  unit list is the rule's design, not something this change reopens.
- `CORE_LOGICAL_BUDGET` is 6,640: one line each for the hedge pattern, the delegation
  pattern and the list of a requirement's own clauses, less one for the hedge loop the
  pattern replaces. The number fixes are in the patterns and cost no line.

## Consequences

- The questions left on these rules are ones a person can answer: "ceiling 10" of what,
  "amber below 60" on what scale.
- `unbounded-quantity` (192) is untouched and is now most of the Optional tab. It needs its
  own measurement before anything changes.

## Revisit when

- A requirement the fixes silence turns out to hold a real gap, found by a reader.
- A cut on the gate path brings the measured core under 6,640.
