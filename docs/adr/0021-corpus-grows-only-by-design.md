# ADR-0021 — The corpus grows only, and that asymmetry is intentional

- **Status:** Accepted
- **Decided:** 2026-09-03
- **Evidence:** exhaustive source audit of `plugin/scripts/reqmap.py` and measurement over
  this repo's 691-requirement corpus, both reproduced below;
  [ADR-0020](0020-redundancy-signal-below-the-fire-rate-bar.md);
  [ADR-0016](0016-no-edge-case-marker.md)

## Context

The engine advises on corpus shape in **both** directions. `next`'s *Granularity* bucket says
one requirement does too much; its *Redundancy* bucket ([ADR-0020](0020-redundancy-signal-below-the-fire-rate-bar.md))
says several say the same thing, and currently names 6 exact-match groups — "6 could be folded
away". `dupes` scores the near-matches.

Only one of those two directions has mechanical assistance.

**Audit, 2026-09-03.** Paths that create a requirement file: `new`, `draft`, `init`, and
`lint --decompose` — and, since `v3.1.0`, a fifth, `--decompose` acting on an `ac-count-high`
finding. Paths that remove one: **none**. Exactly one `os.remove` exists in the 7,169-line
engine (in `_wipe`), and it is reachable only through `init --wipe`, which deletes *every*
non-generated requirement file and strips membership tags from all scanned source so `draft`
can re-extract from scratch. That is a reset to zero, not a reduction. There is no
`os.unlink`, no `shutil.rmtree`, no `os.rename`, and no merge or fold verb. `status:
deprecated` is not an escape either: the file stays on disk and the headline count is
`len(reqs)` across all statuses.

So the corpus is **monotonically non-decreasing by construction**.

## Decision

Ship no shrink verb, and do not drop the `ac-count-low` atomic exemption. Record the
asymmetry as intentional and pin it with a regression test, so a future change cannot add a
delete path without deliberately revisiting this record.

**Why growth and shrink are not symmetric.** Growth-side automation only ever writes a new
`draft` file that a human reads and deletes with `rm` if it makes no sense — the parent is
never touched, so nothing else in the corpus moves. Shrink-side automation must delete a real
file *and* rewrite the `depends_on`/`satisfies` edges pointing at it, potentially crossing a
`confirmed` requirement's drift boundary, and it ships to consumer repos through an Action
whose `@v2` tag force-moves onto every tagged commit. The reversibility is not comparable, so
the same "the human still decides" posture does not license the same mechanical help.

**Why the `ac-count-low` atomic exemption stays.** The check's own premise does not hold for
the atomic form. `reqmap.py` says so at the exemption:

> An atomic requirement holds ONE obligation, so one criterion is the correct number, not an
> under-specified one. `LINT_AC_MIN` guards a dossier.

An atomic requirement with one criterion is correctly specified, not thin. Un-exempting it
would report a defect that is not one.

## Two numbers this record exists to correct

A deliberation on 2026-09-03 reached this decision 2-1, and **two of the three positions
rested on figures that are wrong**. They are recorded here so the decision is not later
defended with them.

| claim made | actual, by execution |
|---|---|
| dropping the atomic exemption fires on 621/691 = **90%** of the corpus, ~18× over ADR-0016's floor | **14 of 70 = 20.0%** — inside ADR-0016's 5–40% band |
| the 621 detailed-design leaves **cost nothing** today | `health` reports **10/100** (70/691 green); `next` lists all 621 under *Drafts to review* |

The first error came from using the whole corpus as the denominator. `lint` only examines
requirements whose status is in `LINT_STATUSES`, which excludes `draft`; all 621 leaves are
`draft`, so `lint` never reaches them. Of the 70 lintable requirements only 13 are atomic
form, and the un-exempted check would fire on 14 — mostly the 9 `SYS-*` records, not the 621.
**The fire-rate argument against dropping the exemption is therefore void**; the semantic
argument above is what carries the decision.

The second error matters more, because it is the premise for *deferring* the larger question.
The 621 leaves are not free: they are the reason the health score reads 10 rather than
something near 100, since the denominator counts every requirement. Whether that layer earns
its place is a real open question — this record does not settle it, and must not be cited as
having settled it.

## Consequences

- The count can only be reduced by hand: edit the files, re-point the tags, run `sync`.
  `next` and `dupes` say *where*; a human does the work. This is the same stance
  [ADR-0020](0020-redundancy-signal-below-the-fire-rate-bar.md) took — "it reports; it never
  merges" — now stated as a property of the whole engine rather than of one signal.
- `init --wipe` remains the only destructive path, and stays loud and total rather than
  selective. A selective delete is what this record declines, not deletion as such.
- A regression test asserts that `os.remove`, `os.unlink` and `shutil.rmtree` appear in
  `reqmap.py` only inside `_wipe`. The test is trivially green today — that is the point: it
  fails the moment someone adds a second delete path, which routes them back here.

## Revisit when

- The health score's denominator is changed to exclude unreviewed drafts, or the 621
  detailed-design leaves are removed — either one invalidates the "costs nothing" framing
  this record already refuses to rely on.
- `next`'s Redundancy bucket exceeds ~25 groups, i.e. hand-folding stops being tractable.
- A consumer repo reports that manual folding, not the missing tool, is what blocked them.
