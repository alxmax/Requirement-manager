# ADR-0051 — The OOP design review returns to the engine, with two writing rules

- **Status:** Accepted. Supersedes [ADR-0047](0047-design-review-site-and-i18n-detector-leave-the-engine.md)
  for the design review and, on the same day at the same direction, for the site
  generator (`docs/architecture.html`, `docs/index.html`); the i18n detector stays out. It
  conflicts with [ADR-0046](0046-the-engine-has-a-line-budget.md)'s budget. How that is
  settled is still open (see Consequences).
- **Decided:** 2026-09-23, at the maintainer's direction: back in the engine and not a
  separate tool, reading Python and the brace languages, reporting the four OOP pillars plus
  a 500-line file limit and an 80-column line limit, with its summary back in the map,
  `health`, `audit` and the viewer's ring and Design tab.
- **Evidence:** `wc -l` on 2026-09-23: the four review modules are 588 lines. `ask --design`
  on this repository first reported 103 `line-too-long` candidates across 109 files and 3
  pillar candidates; the pillar candidates were fixed the same day.

## Context

ADR-0047 removed the review, and its revisit condition said the answer to renewed demand is
"a separate tool that reads the code". The maintainer has asked for it again and has chosen
the engine over a separate tool, knowing the budget would be exceeded.

ADR-0047 recorded three costs:

- **The advisory payload in the freshness-checked `_map.json`** (issue #243). The summary
  comes back into `_map.json`, `_map.md`, `health` and `audit`, and the viewer draws its ring
  and Design tab from it. REQ-DESIGN-991 keeps that payload out of every freshness
  comparison, so it can never fail the gate. MCP still has no design tool.
- **The metrics pillar.** Its RFC-only measurement needed a caveat on every surface to stay
  honest. It stays retired, along with the docstring and definitions-per-file rules.

The third cost, lines vendored into every consumer, does come back.

## Decision

1. **Four modules, one per concern.** `design.py` holds the vocabulary and the
   language-neutral checks, `design_python.py` reads through `ast`, `design_brace.py` reads
   masked text, and `design_report.py` dispatches and prints. They follow the engine's layering
   and import only `config`, `orphans`, `scan` and `tags`.
2. **Pillars:** encapsulation (global state, long parameter lists, data clumps), abstraction
   (long functions, deep nesting, prefix families), inheritance (shared and duplicated
   methods) and polymorphism (`isinstance` chains, equality switches). **Standards:**
   `DESIGN_FILE_MAX_LINES = 500` and `DESIGN_LINE_MAX = 80` (it was 100 before v8.2.0), both
   `CONFIG_KEYS` entries.
3. **`ask --design` works again.** It prints no removal note, exits 0 and never enters the
   gate. It is no longer on v9.0.0's refuse list.
4. **Still retired:** `DESIGN_RFC_MAX`, `DESIGN_FILE_MAX_FUNCS` and `DESIGN_DOCSTRING_PUBLIC`.
   A `_config.json` that sets one of them is still ignored without a message.
5. **The requirements come back as `draft`.** ARCH-DESIGN-061 and REQ-DESIGN-950/951/952/953/955
   have new contracts, and REQ-DESIGN-954/976/991 and REQ-VIEWER-977 return too. A human
   confirms them after reading. REQ-DESIGN-978/979/980 stay `deprecated`.

## Consequences

- The engine is over the 13,550 budget, so `check_engine_budget.py` blocks the next release
  until one of these happens: the budget is raised in a record that says why, or a cut lands
  first. This record deliberately does not move the budget; `check_engine_budget.py` prints
  the current overrun.
- The repository adopts its own rule: its code is rewrapped to at most 80 columns, replacing
  the 100-column convention.

## Revisit when

- The budget decision above is made.
- A consumer's `ask --design` output is dominated by `line-too-long`. If so, the 80-column
  default is a house rule of this repository rather than a universal one, and belongs in its
  `_config.json`.
