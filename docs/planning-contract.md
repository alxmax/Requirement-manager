# Planning rigidity

Two files stay: `ROADMAP.md` (horizons) and `requirements/_planning.json` (bars).
A third list is a bug. Bare `gate` keeps plan signals read-only (ADR-0040).

| # | Change | Why |
|---|---|---|
| P1 | `sync --release --apply` ticks matching `ROADMAP.md` checkboxes (`\| req: ID` of bars on the cut milestone) | Apply already edits version, CHANGELOG and bars; listing boxes on stdout is how Now describes the past |
| P2 | `gate --strict` fails `REQ-PLANSTALE-1013` | The signal found shipped milestones still in the plan after a human did; warn-only cannot prevent the next one |
| P3 | `sync --release` refuses a milestone whose own bars are not done | Already on the ROADMAP (`ARCH-RELEASE-072`); do not retarget it at unrelated Now/Next lines |
| P4 | This repo cuts a tag from `sync --release --json`, or the docs stop saying the plan cuts the tag | `ci.yml` still tags from `plugin.json` |

Not in scope: generating a roadmap from code, making plan-stale a default `@v8` gate rule, weekly Friday bars for a single maintainer, a third sync file.
