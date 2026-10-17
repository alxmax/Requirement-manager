# ADR-0070 — Questions get a page of their own, and `clarify` rides in the map

- **Status:** Accepted. Supersedes [ADR-0028](0028-one-inbox-for-every-open-signal.md);
  amends the number in [ADR-0067](0067-the-core-budget-rises-for-adopt-dispatch.md).
- **Decided:** 2026-10-17
- **Evidence:** this corpus measured on the day: 320 requirements, 0 open `## Verify
  intent` questions, and 514 `clarify` questions on 247 of them, every one advisory
  (192 `unbounded-quantity`, 118 `clause-without-case`, 48 `vague-term`, 48
  `number-without-unit`, 36 `over-scoped`, 36 `case-monoculture`, 32 `no-failure-case`,
  4 `ambiguous-actor`), 0 blocking. `python scripts/check_engine_budget.py` on this
  commit: core 6,638 logical lines.

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

- **Questions are a Workspace page of their own**, below Commands, with one tab per kind
  of question in the same tab bar Problems uses: All; Must fix, only while a section is
  missing somewhere; Asked by a person; Observed in code (a `## Verify intent` bullet that
  starts `Observed`, the template's own convention); one tab per `clarify` rule resting on
  a count (Clause without case, Over-scoped); and Optional. Problems loses its `QUESTION`
  tab, and its `All` no longer counts questions.
- **All leaves Optional out, and the rail shows All's count** like every other entry's:
  158 on this corpus. 367 word-list questions in that number would make it noise; they
  are one click away, on the Optional tab, filterable by rule.
- **`_map.json` carries every `clarify` question per node** (`clarify`: rule, severity,
  basis, where, quote, question, suggest), computed by the same function the CLI runs.
- **A code draft asks one question per signal the scan can point at**, naming
  `file:line` and the code on it: a marker in a comment, a suppression, a swallowed error
  (regex in every language; `ast` in Python), a number hard-coded in a comparison or a
  keyword argument, and a statement after an unconditional exit (both `ast`, Python only).
  At most eight per file; the rest are counted under Context. A file with no signal keeps
  the generic question.
- **Every `clarify` question names the basis it rests on**: `structure` (a section is
  absent: `no-contract`, `no-cases`), `count` (two numbers disagree: `clause-without-case`,
  `over-scoped`) or `wording` (a word on a list: the other six rules). The viewer shows
  `structure` in red as "must fix", `count` in amber as "to check" and `wording` in grey
  as "optional". A sample of four questions per rule on this corpus found most
  `wording` questions false positives ("every candidate", "how many releases", "4
  blocks"); a `structure` or `count` question states a fact, though acting on a count
  stays a judgment.
- **A deprecated requirement asks nothing.** It is retired, so no question on it waits
  for an answer: `clarify` returns none for it, and the Questions page skips its
  Verify-intent bullets too. On this corpus that removes 21 questions (8 count, 13
  wording) from 7 deprecated requirements.
- `CORE_LOGICAL_BUDGET` is 6,638. The nine lines are the map export (four, in
  `mapdata.py`), the rule-to-basis table and the deprecated check (three, in
  `clarify.py`) and the call into the question builder (two, in `draft.py`). The builder, `draftquestions.py`, is imported at
  call time and is not in the number.

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
- A `wording` rule is made precise enough that its questions are mostly real, which
  moves it to a stronger basis.
- A cut on the gate path brings the measured core under 6,638. The budget drops in that
  commit.
