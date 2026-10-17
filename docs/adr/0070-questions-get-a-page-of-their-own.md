# ADR-0070 — Questions get a page of their own, and `clarify` rides in the map

- **Status:** Accepted. Supersedes [ADR-0028](0028-one-inbox-for-every-open-signal.md);
  amends the number in [ADR-0067](0067-the-core-budget-rises-for-adopt-dispatch.md).
- **Decided:** 2026-10-17
- **Evidence:** this corpus measured on the day: 320 requirements, 0 open `## Verify
  intent` questions, and 514 `clarify` questions on 247 of them, every one advisory
  (192 `unbounded-quantity`, 118 `clause-without-case`, 48 `vague-term`, 48
  `number-without-unit`, 36 `over-scoped`, 36 `case-monoculture`, 32 `no-failure-case`,
  4 `ambiguous-actor`), 0 blocking. `python scripts/check_engine_budget.py` on this
  commit: core 6,635 logical lines.

## Context

ADR-0028 folded authored questions into Problems as a `QUESTION` tab. Two things it could not
see then:

- A question had three sources, and the viewer showed one. `clarify` asks what a
  requirement's text leaves open, but its questions reached only the terminal and the
  rule-name snapshot in `_clarifylock.json`. `_map.json` never carried them, so the viewer
  could not show them.
- A code draft asked every file the same sentence ("anything that looks like an accident …
  intended, or a bug to fix?"). `_findings.md` held one copy per drafted file and named no
  line. The scan had found the `TODO`, the `noqa` and the swallowed `except`, but kept only
  a risk score.

Adding `clarify` to the `QUESTION` tab would put 514 rows next to 3 health rows, the
volume problem ADR-0028 names as its revisit condition.

## Decision

- **Questions are a Workspace page of their own**, below Commands, grouped by where the
  question came from: observed in code (a `## Verify intent` bullet that starts
  `Observed`, the template's own convention), asked by a person (any other Verify-intent
  bullet) and asked by `clarify`. Problems loses its `QUESTION` tab, and `All` no longer
  counts questions.
- **The rail count is what is open for a human to answer**: Verify-intent questions plus
  blocking `clarify` questions. Advisory `clarify` questions are on the page, filterable by
  rule, but are not counted in the badge. 514 advisory questions in the badge would make it
  noise.
- **`_map.json` carries every `clarify` question per node** (`clarify`: rule, severity,
  where, quote, question, suggest), computed by the same function the CLI runs.
- **A code draft asks one question per signal the scan can point at**, naming
  `file:line` and the code on it: a marker in a comment, a suppression, a swallowed error
  (regex in every language; `ast` in Python), a number hard-coded in a comparison or a
  keyword argument, and a statement after an unconditional exit (both `ast`, Python only).
  At most eight per file; the rest are counted under Context. A file with no signal keeps
  the generic question.
- `CORE_LOGICAL_BUDGET` is 6,635. The six lines are the map export (four, in
  `mapdata.py`) and the call into the question builder (two, in `draft.py`). The builder,
  `draftquestions.py`, is imported at call time and is not in the number.

## Consequences

- `_map.json` grows by the questions' text. The map is committed, so the diff of a `sync`
  that rewords a clause now also shows the question that rewording answered or raised.
- A reader learns one more nav row. "What did a human ask?" is still one click, now on a
  page named for it.
- The engine's own fail-open `except Exception: return None` is asked about in a draft like
  any other swallowed error. That is the point: the scan cannot tell intent, and the
  question says so.

## Revisit when

- The page's advisory volume buries the questions a person wrote, measured on a consumer
  corpus.
- A cut on the gate path brings the measured core under 6,635. The budget drops in that
  commit.
