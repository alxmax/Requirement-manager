# ADR-0072 — `clarify` retires `unbounded-quantity`

- **Status:** Accepted. Lowers the number in [ADR-0071](0071-clarify-reads-values-and-delegation.md).
- **Decided:** 2026-10-17
- **Evidence:** 20 of the rule's 192 questions on this corpus, drawn at random (seed
  `20261017`) and read one by one. One was real: REQ-SIMILAR-923's `dupes --json` "prints
  every pair … whatever `--top` says", whose output can grow with the square of the corpus.
  The other 19 ranged over a finite set the engine owns ("every candidate it would draft",
  "every scanner", "on every push to `main`"), or were a negation or a remainder ("never …
  any", "any other value", "every other byte"). `python scripts/check_engine_budget.py` on
  this commit: core 6,637 logical lines.

## Context

`unbounded-quantity` asked "Is there an upper bound, and what happens when it is reached?"
of every clause that said "all", "every" or "any" without a limit word. It was the largest
rule by far, 192 of the 427 questions `clarify` asked after ADR-0071, two thirds of the
Optional tab. One real question in twenty does not earn that space: a reader learns to skip
the tab, and the questions beside it that are real go unread with it.

Narrowing it was weighed. Firing only when the clause produces or accepts something over
outside input ("prints every match", "accepts any file") would have caught the real one and
also two of the false ones in the sample, about one in three, on a few dozen questions, for
a new pattern that can be wrong in its own ways.

## Decision

- The rule is removed. "All", "every" and "any" raise no question. REQ-CLARIFY-1102 says
  so, with a case, and REQ-CLARIFY-956 no longer lists it.
- The one real question is not lost by the decision: an author who wants it asked writes it
  in the requirement's Verify intent, where it is listed under Asked by a person.
- `CORE_LOGICAL_BUDGET` drops to 6,637, the core measured with the rule gone.

## Consequences

- On this corpus `clarify` asks 235 questions instead of 427: 129 to check, as before, and
  106 Optional instead of 298.
- A requirement that really leaves a limit open is no longer prompted to say so. The rule
  that asked was wrong too often for its prompt to be read.

## Revisit when

- A defect is traced to a limit a requirement left open that this rule would have asked
  about.
- A narrower form is proposed with its own sample showing most of its questions are real.
