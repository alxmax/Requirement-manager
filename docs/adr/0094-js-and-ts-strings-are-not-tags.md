# ADR-0094 — JS and TS strings are not tags, and the line ceiling moves to 23,000

- **Status:** Accepted. Extends the single masking pass of REQ-SCAN-992 to JS and TS, which
  REQ-RETIRE-1130 relied on.
- **Decided:** 2026-11-22
- **Evidence:** REQ-RETIRE-1130 promised that `retire --delete` leaves a tag's text inside a
  string literal alone. That held for Python only: in a `.ts` or `.js` member the scanner read
  `'implements: X'` inside a string as a tag, and `retire --delete` cut it. The read of the
  drafts on 2026-11-21 left the requirement a draft for this, and the maintainer chose to make
  the scanner right rather than narrow the clause.

## Decision

- **`_visible_lines` blanks JS/TS literals** in `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs` and `.cjs`:
  quoted strings, template literals and regex literals, keeping the line's length so `retire`'s
  offsets still line up. `//` and `/* */` comments are kept, and a block comment's state is
  carried across lines.
- **A template literal is blanked to the end of its line only.** Carrying it across lines was
  tried first: a backtick inside a regex literal (`/`([^`]+)`/g` in `app/src/lib/ui.jsx`) opened
  a template that hid every real tag below it. Line-only blanking cannot lose a tag on another
  line; at worst a line of a multi-line template is read as it was before this change.
- **A `/` opens a regex literal** after an operator, an opening bracket, the start of the line,
  `return` or `typeof`, and closes at an unescaped `/` outside `[...]`; anywhere else it is a
  division.
- **`jsmask.py` is imported only when a JS or TS file is read**, like the C/C++ readers.
- **`TOTAL_LINE_CEILING` moves from 21,000 to 23,000**, by the maintainer's decision: this change
  and REQ-CUSTOMTRACE-1138's fix put the engine at 21,085 physical lines.

## Consequences

- On this repository the member set is unchanged: every JS tag here sits in a comment.
- A JSX text apostrophe (`<p>Don't</p>`) reads as an unclosed string and blanks the rest of its
  line, so a tag later on that line is not seen. No line here has that shape.
- `CORE_LOGICAL_BUDGET` rises from 7,132 to 7,139: the lazy import and the JS branch in
  `tags.py`, and the title fix in `sourcerows.py`.

## Revisit when

- A consumer reports a JS/TS tag the scan no longer sees: then the shape that hid it gets a
  case of its own, or JSX text is read as text.
- The engine reaches 22,500 physical lines: the ceiling is an alarm, and that is the point to
  look for cuts before asking again.
