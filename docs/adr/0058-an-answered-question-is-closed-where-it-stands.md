# ADR-0058 — An answered question is closed where it stands

- **Status:** Accepted
- **Decided:** 2026-09-30
- **Evidence:** field feedback from a consumer repository: answered questions kept in ad-hoc
  "closed questions" subsections in five requirement files, and triaged findings whose `fix`
  already said "resolved" still listed under "Confirmed bugs"; `text._verify_bullets`
  (`text.py:196`), `findings._render_findings_triaged` (`findings.py:58`);
  [ADR-0028](0028-one-inbox-for-every-open-signal.md)

## Context

[ADR-0028](0028-one-inbox-for-every-open-signal.md) gives an open `## Verify intent` question one
next step: answer it, fold the answer into the Description, then delete the bullet. That is the
right end state for a question whose answer changes the contract. It is the wrong one for a
question whose answer is "keep it as it is": there is nothing to fold, and deleting the bullet
loses the record that somebody decided. A consumer kept those answers anyway, in subsections of
its own invention, because the engine offered no place for them. Each one still counted as
open: in `_findings.md`, in the Problems tab, in `gate --risk`'s `unverified-intent` signal.

The triaged view has the same gap one level up. `_findings_triage.json` is written by an AI pass
and read as-is; an item the author has resolved has no field that says so, so it stays under
"Confirmed bugs" until the next triage run.

Since v8.10.1 a question asked as a decision is one item whose indented option and label lines
(`a) …`, `*Default:* …`) belong to it. An answer is one more such line.

## Decision

**An indented `*Answer (YYYY-MM-DD):* …` line under a question closes it, where it stands.**

- `_verify_bullets` leaves out a question that carries such a line. It is the single reader every
  count goes through (`_findings.md`, the map, the Problems tab, `unverified-intent`), so a closed
  question leaves all of them at once.
- The label is exact: `Answer`, a space, an ISO date in parentheses, a colon, in italics. A line
  that does not match leaves the question open, so a typo fails in the loud direction.
- The engine never moves or rewrites the question. `sync` writes a requirement's `status:` in
  the cases it already did and never its body; a closed question stays where the author wrote it,
  with its answer under it.
- A triaged item carrying `"status": "resolved"` leaves the triaged view and its counts.

Folding and deleting (ADR-0028) stays the next step for an answer that changes the contract.

## Consequences

- The record of a decision stays next to the question it answered, dated, in the file under
  review, and costs nothing to keep.
- A closed question is invisible to every count. Reading it means opening the requirement file.
- The triage sidecar gains one optional key. An older engine ignores it and keeps showing the item.
- Not chosen: `sync` moving answered questions into a standard subsection (the first engine edit
  of a requirement body, to save a paste); per-item triage staleness by a hash of the question
  text (a sidecar schema the AI pass would have to emit, before anyone uses the answer line).

## Revisit when

- Authors keep closed questions in subsections again, or ask for a list of closed questions:
  then a closed question needs a surface, not only an absence.
- Triage runs keep reporting items whose question was answered: then per-item staleness is due.
