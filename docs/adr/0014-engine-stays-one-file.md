# ADR-0014 — The engine stays one file, and gets no size gate

- **Status:** Accepted — closes the open question [ADR-0001](0001-single-file-stdlib-engine.md) left standing
- **Decided:** 2026-08-21, after a nine-senator Senate audit (`runs/senate/2026-08-21_004654-reqmap-module-size.json`, two rounds, verdict MODIFY, 7 MODIFY / 2 GO)
- **Evidence:** measurements below, all reproducible by the command named beside them

## Context

[ADR-0001](0001-single-file-stdlib-engine.md) accepted the single-file, stdlib-only engine but
deliberately left one thing open: the file is large, and the roadmap carried an item asking
whether to split it behind a concatenating build or keep it and add a CI line-count budget.
That item sat open for roughly two months, blocking no release and resolving nothing.

Three candidates were audited:

- **(A)** split into source modules plus a concatenating build emitting the single vendored
  `reqmap.py`, committed and byte-compared in CI — extending the [ADR-0005](0005-committed-build-artifacts.md) pattern.
- **(B)** keep one file and add a CI line-count budget.
- **(C)** close the question by decision, adding no machinery.

**What was measured** (`wc -l`, `git log --numstat`, `coverage`, `ruff`, on 2026-08-21):

| | |
|---|---|
| `plugin/scripts/reqmap.py` | **5,544 lines**, 158 top-level defs/classes, 15 section banners, 1 import line |
| per-commit net delta, 130 commits since 2026-06-01 | median **+11**, p90 +72, max **+1,857** (a squashed release commit) |
| concentration | the **top 10 commits are 59%** of all growth |
| tests / lint | **511 tests**, **92%** statement coverage, `ruff --select E9,F` clean |
| incidents attributable to file size | **none recorded** |

## Decision

Keep the engine as one hand-authored file. **Do not split it. Do not add a line-count gate.**
Record the resolution here, correct [ADR-0001](0001-single-file-stdlib-engine.md)'s stale facts,
and close the roadmap item — with numeric triggers that reopen the question on evidence rather
than on discomfort.

Three findings decided it:

1. **The premise was never established.** Every option argued from line count, and no option
   named a single failure caused by it — against 511 tests, 92% coverage, a clean bug-class
   lint, and 130 commits landing in that file without a size-attributable incident. Machinery
   bought against an unmeasured cost is machinery bought on taste.
2. **A fixed threshold here is not a control limit, it is an arbitrary line.** The growth is
   non-stationary: a median commit adds 11 lines while the top 10 commits carry 59% of the
   total, so a budget fires on a burst feature landing — the moment a maintainer least wants a
   stop — and stays silent across the ordinary commits it was nominally written for. Under
   [ADR-0002](0002-error-versus-warning.md) that is a check which fires on correct work, and
   those get switched off.
3. **The split's own economics are inverted.** [ADR-0005](0005-committed-build-artifacts.md)'s
   byte-compare is cheap because it rarely fires: the viewer and the poster rebuild only when
   `app/` or a generator changes. `reqmap.py` is touched by **130 of ~390 commits**, so the same
   check would fire on roughly one commit in three — the repo's highest-churn file. It also adds
   two *silent* failure modes a byte-compare cannot catch, because it proves reproducibility and
   not correctness: a hand-edit to the committed file quietly reverted by the next build, and a
   same-named top-level symbol shadowed by concatenation order. And the engine hosts **175
   `implements:` tag occurrences** in a tree `plugin/.reqmapignore` deliberately does not
   exclude, so a split relocates member `loc` paths inside the committed, freshness-checked
   `_reqlock.json` and `_map.json`.

## Consequences

- The file keeps growing, and nothing automated will complain. That is the accepted cost, taken
  with eyes open rather than by omission — the triggers below are the compensating control.
- [ADR-0001](0001-single-file-stdlib-engine.md) is corrected in two places: its Status no longer
  carries an open question, and its line count is the measured figure with the date it was
  measured. Its *decision* is unchanged, which is why this is a new record rather than a rewrite
  of that one.
- No CI job is added, so no new way to fail a build, and no threshold anyone has to raise.
- If a size signal is ever wanted, it ships read-only — the `REQ-COVERAGE-029` shape, a reported
  number in `health` — never as a gate.

## Revisit when

Any one of these, each checkable:

- **3 or more merge conflicts touching `plugin/scripts/reqmap.py` in a rolling 90 days.** That is
  the concrete harm a split would prevent, and its absence today is why no split happened.
- **`wc -l plugin/scripts/reqmap.py` crosses 8,000** — roughly another burst-cycle of the same
  character as the one measured here.
- **A named external consumer wants the split-module form**, as opposed to the vendored single
  file every consumer copies today.

On any trigger, re-run the audit *with cost data* — the thing this round could not produce.
