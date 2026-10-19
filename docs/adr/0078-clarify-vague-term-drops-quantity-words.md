# ADR-0078 — `clarify`'s `vague-term` drops the words that count or size

- **Status:** Accepted. Narrows the rule [ADR-0071](0071-clarify-reads-values-and-delegation.md)
  kept, in the line of [ADR-0072](0072-retire-unbounded-quantity.md) and
  [ADR-0075](0075-clarify-retires-number-without-unit.md).
- **Decided:** 2026-10-19
- **Evidence:**
  - `vague-term` asked 27 questions on this corpus: "several" 12, "many" 7, "best-effort" 4,
    "small" 3, "large" 1.
  - 20 of the 27, drawn at random (seed `20261019`) and read one by one against their
    clause. A question was counted real when the word sits in a binding clause and a test
    could not assert it without guessing a threshold. 1 was real: REQ-CANDIDATES-826's
    "best-effort parsing" of JS/TS, which never says which signatures are read (Wilson 95%
    interval about 1% to 24%). Leniently 2: REQ-MAP-871's "best-effort `owner/repo`" does not
    name its source.
  - Of the 18 false ones, 13 were "several" or "many" meaning "more than one" ("a tag may
    bind several requirements", "one file may hold many requirements"), and the rest a word
    the same clause sizes ("the small score-only record", "best-effort" followed by the
    fail-open conditions). No question on "several", "many", "small" or "large" was real.
  - `python scripts/check_engine_budget.py` on this commit: core 6,741 logical lines,
    unchanged; the words leave one tuple and the regex loses its "how many" special case.

## Context

`vague-term` asks "What is the measurable threshold behind X?" of a clause holding a word on
`CLARIFY_HEDGES`. The list mixes two kinds of word. Quality words ("quickly", "robust",
"best-effort") stand for a threshold the author did not write. Counting and sizing words
("several", "many", "various", "small", "large") almost never do in a requirement: they say
a set has more than one member, or they are sized by the rest of the clause. The second
kind was 23 of the rule's 27 questions, and none of the sampled ones was real.

ADR-0075's bands, set before that draw: 15 or more real keeps a rule, 8 to 14 moves it,
fewer than 8 retires it. At 1 of 20 the rule as it stood is in the retire band. Retiring it
whole was weighed: the 4 questions left are all on "best-effort", and 1 or 2 of the 4 drawn
were real, which is the only real signal the rule had.

## Decision

- "several", "many", "various", "small" and "large" leave `CLARIFY_HEDGES`. A clause using
  them raises no question. REQ-CLARIFY-1102 says so, with a case.
- "various" was not drawn (it fires nowhere here); it goes with the others because it is
  the same kind of word.
- The rest of the list stays, quality words only. The regex no longer needs its "how many"
  exception, since "many" is gone.
- `lint`'s `vague-term` check reads its own list, `LINT_VAGUE_TERMS`, and is untouched.

## Consequences

- On this corpus `clarify` asks 160 questions instead of 183; `vague-term` asks 4 instead
  of 27.
- A requirement that leaves a count truly open ("keeps several backups") is no longer
  prompted. An author who wants that asked writes it in Verify intent.
- 4 questions is too few to sample. The rule's precision on quality words stays unmeasured
  beyond the 4 drawn.

## Revisit when

- A defect is traced to a count or size a requirement left open that this rule would have
  asked about.
- A corpus gives the quality-word form 20 questions to sample: under 8 real retires the rule.
