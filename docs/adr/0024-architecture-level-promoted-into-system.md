# 0024 — The `architecture` level is promoted into `system`; `fan-out`'s `system` ceiling becomes fifty

**Status.** Accepted. Supersedes [ADR-0023](0023-fan-out-per-level-ceilings-no-floor.md)'s
Decision line 1 ("`fan-out` reads a per-level ceiling: ten for `system`, thirty for
`architecture`") for the `system` half only — the `architecture` ceiling (thirty) is
unchanged. ADR-0019 and ADR-0023 are otherwise unchanged and remain Accepted: the
V-model's `level:`/`layer:` split, the warn-only posture, and the no-floor decision all
stand.

**Date.** 2026-09-03.

**Evidence.** This repo's corpus after the migration this record accompanies: 9
`layer: need` requirements at `level: system` (unchanged), 62 former `level: architecture`
requirements promoted to `level: system`, 0 requirements remaining at `level: architecture`,
573 at `level: code`. Fan-out of the promoted population, measured on the `satisfies:`
graph: max 32 (`ARCH-CHECK-006`), next `ARCH-NEXT-013` 23, `ARCH-VIEWER-007` 22,
`ARCH-LINTCHECKS-025` 21, `ARCH-SEARCH-036` 18 — none over 50. Fan-out of the 9 original
stakeholder-need requirements (children now counted among the promoted 62, an edge this
migration does not touch): 5 to 10. A `/senate` audit (9 senators, 2 rounds,
`senate-reqmap-drop-arch-level-2level-model`) and a Consilium Dialectic deliberation
(`.consilium/runs/2026-09-03_dialectic_vmodel-2level-arch-promote-migration.json`) preceded
this decision.

## Context

A proposal to collapse the three-level V-model (`system` → `architecture` → `code`) to two
levels went to Senate first, in its most literal form: freeze the `system` tier at its
existing 9 requirements, raise their fan-out ceiling to ~30, and re-point all 573
`level: code` `satisfies:` edges directly at those 9. The Senate rejected that form
outright — five senators independently computed that 573 children over 9 parents averages
~64 per node (one node would carry 107), 2–3.5× over any proposed ceiling, before a single
file moved. Two senators (Confucius, Tacitus) read `docs/adr/0007` and `docs/adr/0019`
directly and found the 3-level model's own stated rationale — "a flat list has no place to
say that the second is why the first exists" — directly contradicted by flattening to a
9-node top tier.

The revised proposal that survived: raise the ceiling, but do not freeze the tier. Promote
the 62 `level: architecture` requirements into `level: system` instead of deleting them —
the middle rung's *grouping* stays exactly as populated as it was, only its label at the
top of the pyramid changes. This resolves the arithmetic the Senate found fatal without
inventing new structure: the average child count per `level: system` parent, restricted to
the promoted population, is what it always was (a handful to 32), because the `satisfies:`
edges from `level: code` children to their `architecture`-turned-`system` parents are not
repointed at all.

A Consilium Dialectic deliberation designed the mechanics and caught what the proposal's
own success criteria did not test for: `ARCH-FANOUT-052` — the requirement whose own
Contract states the fan-out ceiling numbers — is itself one of the 62 promoted
requirements. Its Description said "a `system` parent's ceiling is ten; an `architecture`
parent's is thirty," and its `# verifies: ARCH-FANOUT-052#CASE-6` test asserted the system
ceiling is *lower* than architecture's. Both become false the moment the ceiling changes,
so a "pure relabel" cannot ship without also correcting the one requirement that describes
the relabel's own consequence. The Consilium Skeptic stage separately flagged that this
repo's own tier-count documentation (`CLAUDE.md`'s "Ids carry their level" section, citing
SYS-9/ARCH-59/REQ-621) goes stale the same way, and that the promotion leaves the
`architecture` tier with zero members — a fact worth stating outright rather than letting a
reader discover it by counting.

## Decision

1. `fan-out`'s `system` ceiling moves from ten to **fifty** (`LINT_FANOUT_BANDS` in
   `plugin/scripts/reqmap.py`). The `architecture` ceiling (thirty) is unchanged — a
   consumer repo that still uses a real 3-tier split sees no change there.
2. The 62 requirements previously `level: architecture` in this corpus are promoted to
   `level: system`. Nothing else about them changes: same id, same prefix (`ARCH-*` is a
   reading convenience per `CLAUDE.md`, not something the engine parses), same
   `satisfies:` targets, same `layer:` (`bus`/`feature`, unchanged — `layer:` and `level:`
   are orthogonal axes and this migration touches only the latter). `IMPL_EXEMPT_LAYERS`
   keys on `layer:`, confirmed unaffected.
3. **`level: system` now spans two populations in this corpus, distinguished by `layer:`,
   not by `level:`:** the 9 original `layer: need` stakeholder requirements (unpromoted,
   fan-out 5–10, satisfied by the promoted 62) and the 62 promoted `layer: bus`/`feature`
   requirements (fan-out up to 32, satisfied by the 573 `level: code` requirements). A
   reader who wants "is this a root need or a grouping node" reads `layer:`; `level:` alone
   no longer answers it in this corpus.
4. `plugin/requirements/ARCH-FANOUT-052.md`'s Contract is corrected to state the new
   ceiling (fifty) and its `CASE-6` is rewritten to a scenario that still holds (fifty-one
   children over the new ceiling, not twelve over the old one framed as "lower than
   architecture's"). The coupled test in `test_reqmap.py` is renamed
   (`test_system_ceiling_is_lower_than_architecture` → `test_system_ceiling_is_fifty`) and
   rewritten to match.
5. `_mermaid_hierarchy`'s diagram-label logic, which decided "show this node's `<N> code`
   fan-out annotation" by testing `level: architecture` literally, is changed to key on
   "has counted code-level children" instead — the only signal that still tells the two
   `level: system` populations apart once the literal string can't.
6. **The `architecture` level is left declared and unpopulated in this corpus, by design,
   not by accident.** `VALID_LEVEL` and `LINT_FANOUT_BANDS["architecture"]` are unchanged:
   the engine's support for a real 3-tier split is generic infrastructure for any repo that
   wants it, including this one in the future, not something this migration should delete
   because this corpus currently has zero members there.
7. `CLAUDE.md`'s "Ids carry their level" section is updated to state the new counts (9
   `layer: need` + 62 promoted `layer: bus`/`feature`, all `level: system`; 0 at
   `level: architecture`; 573 at `level: code`) and to name the `layer:`-distinguishes-
   populations rule from Decision 3.

## Consequences

- `ARCH-CHECK-006`'s fan-out (32) no longer trips any ceiling — it was already the
  architecture ceiling's sole finding (thirty) before this change and stays well under the
  new system ceiling (fifty). No requirement in this corpus currently has a `fan-out`
  finding at either declared level.
- Every `satisfies:` edge in the corpus is unchanged. `depends_on:` was never in scope.
  621 → 573 code-level children still point at the same 62 parent ids they always did; the
  only thing that moved is what those 62 parents' own `level:` field says.
- 62 confirmed contracts show zero drift from this migration, because `binding_hash` hashes
  only the body's normative span, never the frontmatter dict `level:` lives in — confirmed
  from `plugin/scripts/reqmap.py` before this record was written, not assumed. The one
  exception is `ARCH-FANOUT-052` itself, whose *body* text changed (Decision 4); that one
  contract's drift is accepted via `sync --code .. --accept-drift`.
- A reader of `docs/adr/0007`, `docs/adr/0019`, `docs/adr/0023`, or `CHANGELOG.md` before
  this date will meet `ARCH-*` ids described as `level: architecture`. Those records are
  deliberately not rewritten — they describe what was true when written; `CLAUDE.md`
  carries the standing rule that a changed decision gets a new record, never an edit to an
  old one.
- The `_mermaid_hierarchy` diagram's visual distinction between "root" and "grouping node"
  now depends on the `satisfies:` graph shape (a node with zero counted `level: code`
  children draws as a root) rather than the literal `level:` string, which is a strictly
  more general rule: it produces the identical output on a corpus that still uses a real
  3-tier split, and the correct output on this one.

## Revisit when

- The `system` ceiling (fifty) fires on more than 20% of `level: system` parents — the same
  bar ADR-0023 set for the `architecture` ceiling, applied here on the same reasoning: past
  that point the ceiling is doing what a floor did, and is measuring corpus growth rather
  than a real grouping defect.
- A consumer repo populates `level: architecture` again (in this corpus or another) and
  needs the two ceilings to interact — e.g. a requirement being promoted through both
  `architecture` and `system` in sequence. No such case exists today; this record does not
  anticipate one.
- Someone wants `level:` alone to distinguish root-need from grouping-node requirements
  again without reading `layer:`. That would mean re-splitting `level: system` into two
  values, which is a new proposal, not a revision of this one.
