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

> A diagram that ships with overlapping shapes, uncrossing arrows, unlegended
> colours, or text that spills outside its box is unreadable to an outsider.
> Hard-fail gates at `.save()` time make these defects impossible to ship
> silently.

## WHAT — Contract (normative)
- `.save()` shall support four named gates, each accepting `"warn"` (default,
  prints) or `"error"` (raises `ValueError`): `crossing_check`,
  `legend_check`, `overflow_check`, `text_overlap_check`.
- `crossing_check`: a bound arrow whose straight centre-to-centre path passes
  through an unrelated box shall trigger the gate.
- `legend_check`: a fill colour used on any shape but absent from the
  `legend()` key shall trigger the gate (fires only after `legend()` is
  rendered; a scene with no legend is exempt).
- `overflow_check`: a shape whose bound text is larger than the shape bounds
  (text spills outside) shall trigger the gate.
- `text_overlap_check`: two free captions or label elements that geometrically
  overlap each other shall trigger the gate.
- The inspection methods `check_arrow_crossings()`, `check_legend_coverage()`,
  `check_text_overflow()`, `check_text_overlaps()` shall each return a list of
  offending items (empty list = clean) and be callable before `.save()`.
- `test_excalidraw.py` shall exercise all four gates in both `"warn"` and
  `"error"` modes for each maintained example generator.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes (informative)
- The canonical pattern for a ship-quality diagram is all four gates set to
  `"error"`: `save(..., crossing_check="error", legend_check="error",
  overflow_check="error", text_overlap_check="error")`.

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
  When   `test_excalidraw.py` runs it with all four gates at `"error"`
  Then   the generator produces zero gate violations

## WHERE — Current implementation
- `_check_crossings`, `_check_legend`, `_check_overflow`, `_check_text_overlaps`
  and the `save()` gate dispatch in
  `skills/excalidraw-diagram/scripts/excalidraw_builder.py`.
- `skills/excalidraw-diagram/scripts/test_excalidraw.py` (gate regression suite).

## Links
- Used by: (auto)
## Members in code (auto)
