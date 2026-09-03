---
id: ARCH-EXCALIDRAW-031
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-EXCALIDRAW-030]
milestone: v2.4
satisfies: [SYS-VISUAL-106]

---

# Excalidraw quality gates

## Description
> A diagram that ships with overlapping shapes, arrows that cut through
> unrelated boxes, unlegended colours, text that spills outside its box, an
> arrow too short to draw a visible line, or a label wider than the arrow it
> sits on is unreadable to an outsider. Hard-fail gates at `.save()` time make
> these defects impossible to ship silently.
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

## Verify intent (open questions for the human)
- None — authored from known intent.

## Notes (informative)
- The canonical pattern for a ship-quality diagram is all five named gates set
  to `"error"` (the two hard gates already raise by default): `save(...,
  crossing_check="error", legend_check="error", overflow_check="error",
  text_overlap_check="error", label_fit_check="error")`.

## Cases (= tests)

CASE-1
  Given  a scene where a bound arrow's path passes through an unrelated box
  When   `save(crossing_check="error")` is called
  Then   a `ValueError` is raised; `save(crossing_check="warn")` emits a
         warning and exits normally

CASE-2
  Given  a scene with `fill="blue"` on a box and no `legend()` rendered
  When   `save(legend_check="error")` is called
  Then   a `ValueError` is raised naming the unlegended colour

CASE-3
  Given  a box whose bound text is wider than the box width
  When   `save(overflow_check="error")` is called
  Then   a `ValueError` is raised; `check_text_overflow()` returns the
         offending shape id

CASE-4
  Given  two `label()` elements placed at overlapping coordinates
  When   `save(text_overlap_check="error")` is called
  Then   a `ValueError` is raised naming the overlapping pair

CASE-5
  Given  each maintained example generator in `examples/`
  When   `test_excalidraw.py` runs it
  Then   the generator produces zero violations on every gate (the five named
         gates and both hard gates)

CASE-6
  Given  two boxes placed close but not overlapping, joined by a bound arrow
  When   `save()` is called with defaults
  Then   a `ValueError` is raised (the connector is too short to render);
         `save(allow_short_arrows=True)` writes the files, and
         `check_short_arrows()` returns the offending pair

CASE-7
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




--------------------


---
id: REQ-EXCALIDRAW-361
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# .save() supports five named gates, each accepting "warn"

> `.save()` supports five named gates, each accepting `"warn"` (default, prints) or
> `"error"` (raises `ValueError`): `crossing_check`, `legend_check`, `overflow_check`,
> `text_overlap_check`, `label_fit_check`.

Scenario: each named gate accepts warn or error mode
  Given  a scene with a crossing_check violation
  When   `save(crossing_check="warn")` and `save(crossing_check="error")` are each called
  Then   the warn call prints a warning and returns normally, the error call raises `ValueError`

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-362
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# Crossing_check: a bound arrow whose straight centre-to-centre path

> `crossing_check`: a bound arrow whose straight centre-to-centre path passes through an
> unrelated box triggers the gate.

Scenario: crossing_check fires when an arrow's path crosses an unrelated box
  Given  a bound arrow whose straight centre-to-centre path passes through a third, unrelated
         box
  When   `save(crossing_check="error")` is called
  Then   a `ValueError` naming the crossing is raised

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-363
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# Legend_check: a fill colour used on any shape

> `legend_check`: a fill colour used on any shape but absent from the `legend()` key
> triggers the gate (fires only after `legend()` is rendered; a scene with no legend is
> exempt).

Scenario: legend_check fires for an unlegended colour, exempt with no legend
  Given  a shape filled "blue" with `legend()` rendered but "blue" absent from its key
  When   `save(legend_check="error")` is called
  Then   a `ValueError` naming the unlegended colour is raised; the same scene with no
         `legend()` call raises nothing

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-364
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# Overflow_check: a shape whose bound text is larger

> `overflow_check`: a shape whose bound text is larger than the shape bounds (text spills
> outside) triggers the gate.

Scenario: overflow_check fires when bound text exceeds the shape bounds
  Given  a box whose bound text is wider than the box
  When   `save(overflow_check="error")` is called
  Then   a `ValueError` is raised

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-365
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# Text_overlap_check: two free captions or label elements that

> `text_overlap_check`: two free captions or label elements that geometrically overlap
> each other trigger the gate.

Scenario: text_overlap_check fires when two labels geometrically overlap
  Given  two `label()` elements placed at overlapping coordinates
  When   `save(text_overlap_check="error")` is called
  Then   a `ValueError` naming the overlapping pair is raised

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-366
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# Label_fit_check: a bound arrow whose text label is

> `label_fit_check`: a bound arrow whose text label is wider than the connector it sits on
> — leaving less than ~24px of visible line on each side, measuring the label box
> projected onto the arrow direction — triggers the gate (the label crowds the arrowheads
> or spills onto the joined boxes).

Scenario: label_fit_check fires when a label crowds a short arrow
  Given  a bound arrow whose label leaves less than ~24px of visible line on one side
  When   `save(label_fit_check="error")` is called
  Then   a `ValueError` is raised

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-367
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# .save() additionally enforces two hard gates that raise

> `.save()` additionally enforces two hard gates that raise `ValueError` by default (no
> `"warn"`/`"error"` mode), each with an opt-out flag for a deliberate exception:
> overlapping non-container shapes (`allow_overlap=True`) and a bound arrow clamped too
> short to render a visible line — only its label would show —
> (`allow_short_arrows=True`).

Scenario: the two hard gates raise by default and respect their opt-out flags
  Given  two overlapping non-container shapes, and separately a bound arrow clamped too short to
         render
  When   `save()` is called with defaults, then again with `allow_overlap=True` /
         `allow_short_arrows=True`
  Then   the default calls raise `ValueError`, and the opt-out calls write the files without
         raising

## Members in code (auto)




--------------------


---
id: REQ-EXCALIDRAW-368
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXCALIDRAW-031]
superseded_by:
---

# The inspection methods check_overlaps(), check_arrow_crossings(), check_legend_coverage(), check_text_overflow(), check_text_overlaps()

> The inspection methods `check_overlaps()`, `check_arrow_crossings()`,
> `check_legend_coverage()`, `check_text_overflow()`, `check_text_overlaps()`,
> `check_short_arrows()`, `check_arrow_label_fit()` each return a list of offending items
> (empty list = clean) and are callable before `.save()`.

Scenario: an inspection method returns offending items without saving
  Given  a scene with one crossing-arrow violation and no other defects
  When   `check_arrow_crossings()` is called before `.save()`
  Then   it returns a list containing that one item, while an unaffected check like
         `check_text_overflow()` returns an empty list

## Members in code (auto)
