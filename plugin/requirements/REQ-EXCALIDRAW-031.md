---
id: REQ-EXCALIDRAW-031
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-EXCALIDRAW-030]
satisfies: [NEED-SSOT-001]
milestone: v2.4
---

# Excalidraw quality gates

> A diagram that ships with overlapping shapes, arrows that cut through
> unrelated boxes, unlegended colours, text that spills outside its box, an
> arrow too short to draw a visible line, or a label wider than the arrow it
> sits on is unreadable to an outsider. Hard-fail gates at `.save()` time make
> these defects impossible to ship silently.

## WHAT — Contract (normative)
- `.save()` supports five named gates, each accepting `"warn"` (default,
  prints) or `"error"` (raises `ValueError`): `crossing_check`, `legend_check`,
  `overflow_check`, `text_overlap_check`, `label_fit_check`.
- `crossing_check`: a bound arrow whose straight centre-to-centre path passes
  through an unrelated box triggers the gate.
- `legend_check`: a fill colour used on any shape but absent from the
  `legend()` key triggers the gate (fires only after `legend()` is
  rendered; a scene with no legend is exempt).
- `overflow_check`: a shape whose bound text is larger than the shape bounds
  (text spills outside) triggers the gate.
- `text_overlap_check`: two free captions or label elements that geometrically
  overlap each other trigger the gate.
- `label_fit_check`: a bound arrow whose text label is wider than the connector
  it sits on — leaving less than ~24px of visible line on each side, measuring
  the label box projected onto the arrow direction — triggers the gate
  (the label crowds the arrowheads or spills onto the joined boxes).
- `.save()` additionally enforces two hard gates that raise `ValueError`
  by default (no `"warn"`/`"error"` mode), each with an opt-out flag for a
  deliberate exception: overlapping non-container shapes (`allow_overlap=True`)
  and a bound arrow clamped too short to render a visible line — only its label
  would show — (`allow_short_arrows=True`).
- The inspection methods `check_overlaps()`, `check_arrow_crossings()`,
  `check_legend_coverage()`, `check_text_overflow()`, `check_text_overlaps()`,
  `check_short_arrows()`, `check_arrow_label_fit()` each return a list of
  offending items (empty list = clean) and are callable before `.save()`.
- `test_excalidraw.py` exercises the five named gates in both `"warn"` and
  `"error"` modes, and the two hard gates, for each maintained example
  generator.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes (informative)
- The canonical pattern for a ship-quality diagram is all five named gates set
  to `"error"` (the two hard gates already raise by default): `save(...,
  crossing_check="error", legend_check="error", overflow_check="error",
  text_overlap_check="error", label_fit_check="error")`.

## HOW — Acceptance (= tests)

AC-1
  Given  a scene where a bound arrow's path passes through an unrelated box
  When   `save(crossing_check="error")` is called
  Then   a `ValueError` is raised; `save(crossing_check="warn")` emits a
         warning and exits normally

AC-2
  Given  a scene with `fill="blue"` on a box and no `legend()` rendered
  When   `save(legend_check="error")` is called
  Then   a `ValueError` is raised naming the unlegended colour

AC-3
  Given  a box whose bound text is wider than the box width
  When   `save(overflow_check="error")` is called
  Then   a `ValueError` is raised; `check_text_overflow()` returns the
         offending shape id

AC-4
  Given  two `label()` elements placed at overlapping coordinates
  When   `save(text_overlap_check="error")` is called
  Then   a `ValueError` is raised naming the overlapping pair

AC-5
  Given  each maintained example generator in `examples/`
  When   `test_excalidraw.py` runs it
  Then   the generator produces zero violations on every gate (the five named
         gates and both hard gates)

AC-6
  Given  two boxes placed close but not overlapping, joined by a bound arrow
  When   `save()` is called with defaults
  Then   a `ValueError` is raised (the connector is too short to render);
         `save(allow_short_arrows=True)` writes the files, and
         `check_short_arrows()` returns the offending pair

AC-7
  Given  a bound arrow whose label is wider than the arrow's visible line
  When   `save(label_fit_check="error")` is called
  Then   a `ValueError` is raised; `check_arrow_label_fit()` returns the
         offending label

## WHERE — Current implementation
- `check_overlaps`, `check_arrow_crossings`, `check_legend_coverage`,
  `check_text_overflow`, `check_text_overlaps`, `check_short_arrows`,
  `check_arrow_label_fit` and the `save()` gate dispatch in
  `skills/excalidraw-diagram/scripts/excalidraw_builder.py`.
- `skills/excalidraw-diagram/scripts/test_excalidraw.py` (gate regression suite).

## Links
- Used by: (auto)
## Members in code (auto)
