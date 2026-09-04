# ADR-0028 — One inbox for every open signal, with origin as a tab

- **Status:** Accepted
- **Decided:** 2026-09-04
- **Evidence:** the corpus measured on the day of the decision (224 requirements, 0 risk
  signals, 0 real verify-intent questions, 0 drafts); the draft-collapse affordance added to
  `ProblemsView` after the original split; [ADR-0025](0025-three-levels-restored-corpus-folded-to-two-hundred.md)

## Context

The viewer carried two inboxes. **Problems** listed what the engine derived from the corpus on
every load — an orphan, an untested requirement, partial per-criterion coverage, a draft nobody
reviewed. **Findings** listed what a human wrote down in `## Verify intent`: the questions an
author recorded as unresolved.

The separation was never about the taxonomy. It was recorded in `FindingsView`'s own module
comment, and it was about volume:

> Deliberately NOT folded into Problems. Problems is currently ~618 rows of `draft`/`unreviewed`
> review noise; a real finding dropped in there is invisible.

Two things ended that. The corpus folded from 685 requirements to 224
([ADR-0025](0025-three-levels-restored-corpus-folded-to-two-hundred.md)) and now carries **no
drafts at all** — measured the day of this decision: 0 risk signals, 0 open questions, 0 drafts,
both screens empty. And `ProblemsView` had meanwhile grown the affordance the split was standing
in for: `unreviewed` draft rows collapse behind a "N draft review rows hidden — show" chip, which
treats the noise where it occurs instead of evacuating everything else to a second screen.

What remained was a nav row and a concept for a distinction the reader still needs.

## Decision

**One inbox, named Problems. Origin is a first-class tab, never a severity.**

- An author's open `## Verify intent` question is a row in Problems with its own kind,
  `QUESTION`, its own tab, and its own badge on the rail.
- It sorts above `REVIEW` and below `ERROR`/`WARN`: somebody wrote it down on purpose, so it
  outranks an unreviewed draft; it is not a build failure, so it does not outrank one.
- The row keeps the rendering it had as a finding — the question list itself, and the
  "answer it, fold the answer into the Description, then delete the bullet" next step.
- The rail badge for questions stays hidden at zero. Zero authored questions is the honest state
  of this corpus, not an achievement to display.

`Findings` disappears as a surface. The engine's `_findings.md` digest is untouched: that is a
different artifact, aggregated by `sync` for reading outside the viewer.

## Consequences

- One fewer nav row and one fewer concept, without losing the question "what did a human flag?" —
  it is one click, on a labelled tab.
- The volume risk returns in a consumer repository the moment `draft` runs over a legacy codebase:
  `REVIEW` becomes hundreds of rows again. The bet is that the collapse chip, which did not exist
  when the split was made, is enough. If it is not, the split comes back — with data next time.
- A reader who learned the two-screen shape has to relearn one thing. The tab is named for what it
  holds, and the rail badge still marks that something was asked.

## Revisit when

- A consumer reports that a real question was missed because it sat behind the draft collapse.
- The `QUESTION` count routinely exceeds what one tab can show, which would mean the corpus has an
  authoring problem rather than the viewer having a layout one.
