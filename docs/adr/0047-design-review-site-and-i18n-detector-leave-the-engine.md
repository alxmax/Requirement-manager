# ADR-0047 — The design review, the site generator and the i18n detector leave the engine

- **Status:** Accepted. Supersedes [ADR-0044](0044-questions-leave-the-verdict-verb.md) for
  `ask --design` and `ask --i18n`: those two questions are no longer asked at all. The
  retirement of ARCH-DESIGN-061, ARCH-SITE-026, REQ-TRANSLATE-967 and REQ-TRANSLATE-996 is
  recorded here.
- **Decided:** 2026-09-22, at the maintainer's direction, as the first stage of
  [ADR-0046](0046-the-engine-has-a-line-budget.md)'s budget.
- **Evidence:** `wc -l` per module on 2026-09-22. The design review was 722 lines, the site
  generator 512 and the i18n detector about 70. The engine went from 14,910 to 13,405 lines.

## Context

Each of the three is advice or presentation that a consumer vendors and that the verdict never
needs:

- **The design review** (`ask --design`, `design*.py`) reviewed the consumer's code against
  the OOP pillars and a few house standards. It was never part of the gate. The commit that
  added it was also the commit that crossed ADR-0014's 8,000-line trigger (ADR-0032). It
  also put an advisory payload into the freshness-checked `_map.json`, which then needed
  its own exclusion so that a blank line in untagged code could not fail the gate.
- **The site generator** (`site.py`, `site_template.py`) injected nav and stats regions
  into `docs/architecture.html` on every `init` and `sync`. Presentation is not
  traceability.
- **The i18n detector** (`ask --i18n`, RM029, the `LANGUAGE` key) measured a translation
  cache that nothing in the engine can produce. The command that wrote it was removed on
  2026-09-05.

## Decision

1. **The code leaves.** `design.py`, `design_python.py`, `design_brace.py`, `design_report.py`,
   `site.py` and `site_template.py` are deleted, and so are the design thresholds in
   `config.py`, the design record in `_map.json`, `health` and `audit`, the `reqmap_design`
   MCP tool, RM029, `LANGUAGE` and the git helpers only the site used.
2. **The flags stay one release, doing nothing.** Through v8.x, `ask --design`, `ask --i18n`,
   `init --no-site` and `sync --attach` are accepted. Each prints one stderr line naming v8.2.0
   and this record, then exits 0. v9.0.0 refuses them. This is ADR-0037's alias rule, except
   that the flag no longer does its work, because the code that did it is gone.
3. **Translations already made stay visible.** The reader of `requirements/_i18n/<locale>.json`
   stays (`i18n.py`, now 93 lines), so the viewer keeps showing a cached Romanian entry while
   it is fresh. Nothing reports the cache decaying.
4. **A site page is frozen, not deleted.** `init` writes no `docs/architecture.html`. A `sync`
   in a repository whose page still carries the engine's region markers prints one line saying
   the page is no longer refreshed, so a consumer does not watch it go stale in silence.
5. **Retired config keys are silent.** A `_config.json` that still sets a `DESIGN_*` key or
   `LANGUAGE` is ignored without the "unknown key" line on every run.

## Consequences

- The engine is 13,405 lines, within ADR-0046's first stage (13,550).
- The requirement corpus loses sixteen enforced requirements, now `deprecated`, not deleted,
  so an old tag or record that names one still resolves.
- This repository's `docs/architecture.html` is now a hand-maintained page. Its stats region
  stays as the last engine run wrote it.
- The viewer's Design panel receives no data and shows nothing. The viewer is unchanged.

## Revisit when

- A consumer asks for design advice from the engine. The answer is a separate tool that reads
  the code, not a module every consumer vendors.
