# 0023 — `fan-out` gets per-level ceilings and no floor

**Status.** Accepted. Supersedes [ADR-0019](0019-v-model-left-arm-adopted.md)'s fan-out
Decision ("A 5–20 fan-out band on each level, reported at both edges") and its Consequence
("The fan-out band fires 7 times on this repo and those 7 are left standing … they are
real"). ADR-0019 is otherwise unchanged and remains Accepted: the V-model's left arm, its
warn-only posture, and the `satisfies:`/`depends_on:` split all stand.

**Date.** 2026-09-03.

**Evidence.** This repo's corpus at `b0ce92b` (641 requirements, 72 confirmed);
`runs/senate/2026-09-03_155528-senate-reqmap-pr208-branch-audit.json` (MODIFY, two rounds),
which is what forced this record to exist.

## Context

ADR-0019 shipped a uniform 5–20 fan-out band on the `satisfies:` graph and wrote its own
revisit condition: *"if, after the corpus is deliberately restructured to satisfy it, the
band still reports more than a handful, it should be widened or dropped."* The corpus was
then restructured for an unrelated reason — the leaf pass folded attribute clauses into the
behaviours they qualify — and the band's findings went **up**, from 7 to 10, because folding
moved parents from five children to four.

That is the anti-correlation the floor could not survive: doing the *right* thing to a
requirement (removing a clause that was never a behaviour) makes its parent trip a check
whose message is "too few to be a level". A signal that fires because the corpus improved is
measuring the wrong thing.

Measured on the corpus at `b0ce92b`, over the `satisfies:` graph:

```
children per parent:  3:1  4:6  5:5  6:8  7:5  8:9  9:2  10:6 … 18:1 19:1 22:1 23:1 32:1
below the old floor (<5):   7
above the old ceiling (>20): 3   — ARCH-VIEWER-007 (22), ARCH-NEXT-013 (23), ARCH-CHECK-006 (32)
total findings, old band:  10
```

The distribution is continuous from 3 to 19 and then breaks: 19 → 22 → 23 → **32**. There is
a real cliff at the top and none at the bottom. Ceilings that follow the level are defensible
from that shape; a floor is not.

## Decision

1. `fan-out` reads a per-level ceiling: **ten** for `system`, **thirty** for `architecture`.
2. **There is no floor at either declared level.** A thin parent is not reported.
3. A parent declaring no `level:` keeps the uniform 5–20 band, floor included, so a repo
   that never adopted the level axis sees exactly what it saw before.
4. The check stays warn-only, as ADR-0019 required and [ADR-0002](0002-error-versus-warning.md)
   demands of anything advisory.

On the new bands the corpus reports **one** finding: `ARCH-CHECK-006` at 32 children, over
the architecture ceiling of 30. It is a real one, and it is left standing.

## What this record corrects

ADR-0019's Consequence stated that the seven band findings were *real*. That was the
proposing author's own verdict on his own check, recorded in the commit that shipped it
(`3a34b3d`) — not an independent sample. The Senate that audited that very proposal
(`runs/senate/2026-09-02_223252-senate-reqmap-ten-proposals-traceability-and-layers.json`,
MODIFY 8–1, all blocking) had already recorded the opposite: *"#6 must satisfy the SECOND
half of the ADR-0016 bar: sample 10 flags, require >=8 confirmed real. On today's corpus 3
of the 4 over-20 flags already carry `lint_exempt`, so the sample is **pre-failed**."* The
check shipped anyway; that run's outcome row is `OVR`.

A later re-reading of the band's findings reported "0 of 9 real". **That figure does not
reproduce and is withdrawn.** No commit on the branch produced nine floor findings — the
floor produced 4, then 6, then 7 as the corpus changed — and nine was the floor-plus-ceiling
total at an intermediate commit. Worse, the one flag that reading called plausibly real,
`ARCH-CHECK-006`, is a *ceiling* finding and cannot belong to a floor sample. No artifact in
the tree records who reviewed what, so the reading cannot be repaired, only retracted.

**The floor is therefore dropped on the distribution and the anti-correlation above, which
reproduce from a sha and a filter, and on nothing else.** [ADR-0022](0022-no-minimum-requirement-size-check.md)'s
launch discipline is not claimed as satisfied here: this change ships a *loosening* — the
check can only report less than before — which is the one direction that needs no
confirmation sample, because it cannot create a false positive a reader must triage.

Two further citation defects, recorded so a reader does not hunt for them:

- ADR-0019's Evidence line cites `runs/senate/2026-09-02_*-v-model*.json`, which matches no
  file. The runs are `2026-09-02_201621-senate-reqmap-vmodel-req-size-and-3-classes` and
  `2026-09-02_223252-senate-reqmap-ten-proposals-traceability-and-layers` (`-vmodel-`, not
  `-v-model-`). ADR-0019 is not edited to fix this; this line is the correction.
- Run `2026-09-02_201621` carries two blocking conditions this repo has never delivered nor
  declined in writing: a human pilot classification round over ≥10 requirements, and a
  reverse dangling-`# verifies:`-after-split check. **Both are hereby declined**, on a
  measurement rather than by silence: the branch that prompted this record removed 51
  requirements, and afterwards all 147 `# verifies:` tags in the repo still resolve — every
  unresolved one is a documentation placeholder or a test fixture — with `gate` at 0 errors.
  The harm the second condition guards against did not occur. If a future split does strand
  a real tag, that is the trigger to build the check.

## Consequences

- A thin parent at a declared level is never reported, so a corpus can grow a one-child
  level and nothing says so. Accepted: the alternative fired on six parents that had just
  been improved.
- The two axes now behave differently at the two edges, which is one more thing to hold in
  mind when reading a finding. The finding text says which edge it is.
- A consumer's `lint --strict` can only report *fewer* fan-out findings after this change,
  never more, so no green build can newly fail. This is why it did not take the action's
  `@v2` tag to `@v3`.

## Revisit when

- A consumer repo reports that a genuinely under-populated level went unnoticed and cost
  them something concrete. A hypothetical does not count; the floor was already dropped once
  for firing without a real finding behind it.
- The ceiling fires on more than 20% of parents at either level, which would mean the ceiling
  is now doing what the floor did.
- Someone proposes restoring the floor. The bar is [ADR-0016](0016-no-edge-case-marker.md)'s,
  in full: a fire rate between 5% and 40% of the requirements `lint` actually visits, **and**
  ≥8 of 10 sampled findings confirmed real by someone who did not write the check. The
  history above is what that bar exists to prevent.
