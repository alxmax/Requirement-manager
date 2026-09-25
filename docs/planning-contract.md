# Planning rigidity

Two files stay: `ROADMAP.md` (horizons) and `requirements/_planning.json` (bars).
A third list is a bug. Signals about the plan stay read-only on bare `gate` (ADR-0040).

| # | Change | Why |
|---|---|---|
| P1 | `--release --apply` ticks matching `ROADMAP.md` checkboxes | Apply already edits version, CHANGELOG and bars; leaving boxes for a human is how Now describes the past |
| P2 | `gate --strict` fails `REQ-PLANSTALE-1013` | The signal found v7.4 / v7.9 / v7.19 after a human did; warn-only cannot prevent the fourth |
| P3 | `sync --release` refuses an incomplete milestone | A version with Now/Next lines and no bars is not a plan |
| P4 | This repo cuts a release from the plan *or* stops claiming it does | `ci.yml` still tags from `plugin.json` |

Not in scope: generating a roadmap from code, making plan-stale a default `@v8` gate rule, weekly Friday bars for a single maintainer.
