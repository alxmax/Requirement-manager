# ADR-0075 — `clarify` retires `number-without-unit`, and a clause-against-case count is a guess

- **Status:** Accepted. Supersedes in part [ADR-0070](0070-questions-get-a-page-of-their-own.md)
  (the basis of `clause-without-case`) and [ADR-0071](0071-clarify-reads-values-and-delegation.md)
  (the value exclusions, which go with the rule), and lowers the number in
  [ADR-0074](0074-a-baseline-is-checked-and-a-waiver-is-kept.md).
- **Decided:** 2026-10-18
- **Evidence:**
  - `clause-without-case`: 20 of the rule's 95 questions on this corpus, drawn at random
    (seed `20261018`) and read against the requirement's own cases. A question was counted
    real when at least one clause has no case that touches it. 7 were real, 9 were not, and
    4 sat between: every clause touched, part of one not asserted. Read strictly that is
    7 of 20 (95% interval about 18% to 57%), leniently 11 of 20. The number the question
    states ("2 clause(s) have no case") matched the real gap in 4 of the 7 real ones,
    because one case often proves two clauses.
  - `number-without-unit`: all 9 of its questions on this corpus, read one by one. None was
    real: "at line 1" and "block 0" (the unit comes before the number), "a score of 2",
    "`risk:` is 2", "4 Mermaid code blocks", a health band "at or above 90". Twenty could
    not be drawn because there are not twenty.
  - `no-failure-case`: 9 of its 30 questions fall on `layer: need` requirements, each a
    stakeholder story with one Scenario.
  - `python scripts/check_engine_budget.py` on this commit: core 6,688 logical lines.

## Context

ADR-0070 gave each `clarify` question a basis so a reader could tell a fact from a guess,
and put `clause-without-case` under `count`, beside `over-scoped`, with the claim that a count
is never a false positive. The viewer turns that into its "to check" tab. Neither claim was
measured. Once v8.24.5 made `over-scoped` use `lint`'s own predicate, `clause-without-case`
was the whole tab: 95 questions, about half of them false.

The rule compares two numbers and never reads a case, which its own docstring says. A
count that does not read what it counts is a guess about the text, the same kind of thing
a word on a list is.

The sampling bands were set before the draw: 15 or more real keeps the rule under `count`,
8 to 14 moves it, fewer than 8 retires it. The strict reading, 7, is in the retire band;
the lenient one, 11, in the move band. The interval covers both.

## Decision

- `clause-without-case` keeps asking, under basis `wording`. It leaves the "to check" tab
  for Optional. Retiring it was weighed: on the sample it found seven requirements with a
  clause no test proves, and about half of 95 is still dozens of real gaps that nothing else
  names. Under Optional it costs a reader nothing they did not choose to read.
- `number-without-unit` is retired. A number in a clause raises no question; an author who
  wants a unit asked writes it in the requirement's Verify intent. Narrowing it to compared
  numbers ("below 60") was weighed and left: a new pattern with its own errors, for a rule
  that asked 9 questions here.
- `no-failure-case` asks nothing of a `layer: need`. A need is one story with one Scenario,
  so it has no second case to put a failure path in; the failure path belongs to the
  architecture requirement that satisfies it. The layer is used rather than `level: system`
  because `level:` is opt-in (ADR-0019) and `layer: need` is what marks a need either way.
- `CORE_LOGICAL_BUDGET` drops to 6,688, the core measured with the rule gone.

## Consequences

- On this corpus `clarify` asks 177 questions instead of 195. The "to check" tab holds only
  structural questions and `over-scoped`, none of which fire here today, so it reads empty.
  That is the measured state, not a lost signal: the 95 are in Optional.
- REQ-CLARIFY-956 says a number asks nothing and a need is not asked for a failure path;
  REQ-CLARIFY-1102 loses the clause about values, which had nothing left to govern.
- The viewer's note on the Optional tab still says "a word on a list matched", which no
  longer covers `clause-without-case`. Changing it needs a viewer rebuild and is left for
  the next viewer change.

## Revisit when

- A defect is traced to a unit a requirement left unstated that this rule would have asked
  about.
- A form of `clause-without-case` that reads which clause a case proves is proposed with a
  sample of its own showing 15 of 20 real: it would earn `count` back.
