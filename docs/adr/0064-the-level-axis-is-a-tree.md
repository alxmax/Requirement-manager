# ADR-0064 — The level axis is a tree: one parent each, needs nested one deep

- **Status:** Accepted. Extends
  [ADR-0036](0036-decomposition-builds-downward-the-system-rung-is-the-authors.md), decision 2
  (RM032), with three checks on the axis's shape. ADR-0036 stands for everything else, RM032
  stays a warning, and no rule code is added.
- **Decided:** 2026-10-05, from three field reports on corpora retrofitted with `init` and
  `clarify --levels`, at the maintainer's direction: the three-level split should be rigid and
  clear, and a system need may have system sub-needs with the architecture under them.
- **Evidence:** `reqmap.py gate --full --code ..` on this corpus before and after the change,
  and the same gate run read-only on two consumer corpora that declare `level:` (their counts
  are not recorded here: both repositories are private).

## Context

RM032 checked that every requirement below the apex has a group one rung up and every group a
member one rung down. It did not check how many parents a requirement has, or how system needs
relate to each other, because `system` has no rung above it. Two consequences were reported:

- A corpus whose architecture requirements each declared several `satisfies:` parents
  passed `gate --full` and `clarify --levels` in silence. So did the same corpus rebuilt
  as a tree. The engine accepted both shapes and the documentation showed
  neither.
- `init` on a repository with every source file in its root wrote one `ARCH-ROOT-001` with
  ten times the children its band allows. `LINT_FANOUT_BANDS` caps an architecture parent
  at 30, but the lint reads only `baseline`, `implemented` and `confirmed` requirements
  (`lintrules.py`, `LINT_STATUSES`), and everything `init` writes is a `draft`.

This corpus already has the intended shape: `SYS-SSOT-001`, nine `SYS-*` sub-needs satisfying
it, and every `ARCH-*` with exactly one parent. One exception: `ARCH-SECTIONS-068` sat on the
apex.

## Decision

1. **One parent each.** A `code` requirement satisfies one `architecture` requirement, an
   `architecture` requirement one `system` requirement, and a `system` sub-need one `system`
   requirement. RM032 warns when a requirement satisfies two or more on the rung its parent
   belongs to. A second relation is a `depends_on`.
2. **Needs nest one deep.** A `system` requirement may be satisfied by `system` sub-needs.
   RM032 warns on a sub-need of a sub-need, and on an `architecture` requirement satisfying an
   apex that has sub-needs: once the apex is split, every capability sits under the sub-need it
   serves.
3. **An apex with sub-needs is a complete group.** The downward half of RM032 accepts a
   `system` requirement whose satisfiers are sub-needs, with no architecture member of its own.
4. **The shape is checked on drafts too.** The checks in 1 and 2 run on every requirement that
   declares a `level:`, whatever its status. A draft is where a second parent is first
   written. The checks ADR-0036 shipped stay limited to enforced requirements.
5. **A rung written past its band is named when it is written.** `init` and
   `clarify --levels` print one `note:` line when a placeholder they write or propose holds
   more children than its level's `LINT_FANOUT_BANDS` ceiling.
6. **The checks load only where the axis is used.** They live in `levelshape.py`, imported at
   call time by RM032 for a requirement that declares a `level:` and by the two commands
   that write rungs, the way the plan's modules load only for a repository that keeps a plan
   (ADR-0057). The core paid for the rest with an equal cut in the same change: the reverse
   `satisfies:` index, built separately in `workspace.py`, `mapdata.py` and `relevel.py`, is
   one helper in `model.py`, and `candidates._arch_id_for`, called from nowhere, is gone.

## Consequences

- This corpus: RM032 fired once, on `ARCH-SECTIONS-068` (an architecture requirement on an
  apex with sub-needs). Single-parent findings: 0 of 67 architecture and 0 of 234 code
  requirements. `ARCH-SECTIONS-068` now satisfies `SYS-READ-103`, beside `ARCH-PARSE-001`,
  and RM032 is silent.
- The two consumer corpora: the new checks fire in one of them and not in the other, each
  finding a single requirement. Nothing about the warning's severity changed.
- `docs/requirements.md` shows the tree, with this corpus's own ids, and states the fan-out
  bands as configured instead of the uniform 5–20 it used to quote.
- A corpus that declares no `level:` sees nothing, as before.

## Revisit when

- **Make the shape checks an error under `--strict`** once `gate --full --strict` has been run
  with them on this corpus and at least two consumer corpora and the per-check counts are
  recorded in a new record. Until then the rule is `strict=False`.
- A consumer needs more than one level of sub-needs: the depth then becomes a configured value,
  not a second check.
