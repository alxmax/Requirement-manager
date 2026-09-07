# ADR-0036 — Decomposition builds downward; the system rung is the author's

- **Status:** Accepted — confirms [ADR-0030](0030-the-engine-drafts-the-pyramid.md) and
  [ADR-0031](0031-a-tagged-corpus-can-be-given-the-rungs.md) against a proposal to extend them
- **Decided:** 2026-09-07, after a nine-senator Senate audit, all seats on Opus
  (`runs/senate/2026-09-07_163654-senate-reqmap-sys-after-decompose-and-corpus-efficiency.json`,
  two rounds, verdict **MODIFY**, 9 MODIFY / 0 GO / 0 STOP, all nine blocking after Round 2;
  Law 8 promoted nothing)
- **Owner:** Alex
- **Evidence:** every number below was measured by a senator on the committed tree (`b08e7af`)
  or the working tree of that day, by the command named beside it

## Context

The maintainer observed that `clarify --decompose` never produces a `SYS-*` requirement: the
children it writes carry `satisfies: [<parent>]`, and nothing above the parent is created,
linked or checked. That is true. The only place the engine mints a system-level node is `init`
(`draft.py::_write_sys_placeholder`, ADR-0030's "named hole"); `clarify --levels` never writes a
`satisfies:` edge (ADR-0031); and no gate rule reports an architecture-level requirement that
declares no `satisfies:` at all.

Two proposals were put to the Senate together, because both touch the corpus's shape:

- **A** — draft the missing top after decomposition: A1 (the engine writes the placeholder and
  the edge from `--decompose --apply` and `--levels --apply`), A2 (a warn-only gate rule), A0
  (document that decomposition builds downward).
- **B** — a leaner corpus, as a menu: B1 `dupes` skips sibling pairs; B2 merge the true
  duplicates; B3 a word budget on `## Context`; B4 a lint for ADR-0025 rule 3; B5 fold the
  under-sized leaves.

Direct precedents, both one day old and both cited by Tacitus: the three-levels audit
(`2026-09-06_003141`, MODIFY, resolved OK with zero engine changes) and the code-rung
decomposition audit (`2026-09-06_141350`, MODIFY, resolved OVR with Deming's confirmation-sample
request still unmet). Over eight resolved runs on this repo's corpus shape, six of six that asked
"should the engine build new shape machinery" resolved as "nothing built"; the one engine change
that resolved OK was a measured false-positive reduction to an existing read-only report.

## What the Senate found

**On A1.** Refused by every seat, on four independent grounds. (1) It reverses a recorded
refusal three times over: ADR-0031's Decision bullet, the four printed lines of `cmd_levels`
("`satisfies:` edges are NOT proposed … the conflation the engine refuses to make"), and clause 3
of the **confirmed** `REQ-LEVELRETROFIT-987` with its verifying test
(`test_satisfies_edges_are_never_proposed_or_written`) — Napoleon priced the deletion of a
binding clause at 6–9 hours plus a drift baseline advance, for a trigger measured at **0 of 67**
architecture requirements. (2) It converts a visible hole into an invisible one: an ARCH with no
`satisfies:` is legible in a blank frontmatter field; after A1 it reads as a filled field pointing
at a permanently-draft node that RM008 and RM015 never see, because both key on enforced statuses
(Aristotel, Dimon). (3) It would be the first engine write of `satisfies:` into a file the engine
did not create — every existing write lands in an engine-created file — and it carries no
provenance marker the way `level_source: auto` does, so the undo drops from a mechanical
predicate to per-file judgement (Aurelius, who moved from advisory to blocking on this). (4) It
forecloses the measurement: once the engine fills every hole, the rate at which real corpora
lack a top can never be observed, so A2 can never afterwards clear ADR-0016's floor (Dimon).

**On A2.** Not justified either: it fires on 0 of 67 here, and 0% is not a low rate but an
unmeasured one — ADR-0020's below-floor exception rested on zero false positives *by
construction*, an argument a detector that has never fired cannot make (Deming, answering
Confucius).

**On B.** Only B1 survived every re-measurement: on the committed tree `gate --dupes` reports 38
pairs, 23 of them siblings under one parent — a 60.5% false-positive rate in a report that ships
today, deterministic, reproduced by four seats with two tools. B4's headline figure ("30% of ARCH
violate ADR-0025 rule 3") was an instrument reading: five defensible readings of the rule span
1.2% to 31.3% on one frozen tree, three senators got 20, 21 and 24, and the substantive gap —
a parent that does not name a declared child — is **2 of 60**: `ARCH-CLARIFY-062` missing
`REQ-CLARIFY-975` and `ARCH-DESIGN-061` missing `REQ-DESIGN-991`. B3's instrument is sound
(word count, zero cross-implementation variance) but its threshold was unset: 250 words fires on
8.5% of the corpus, 300 on 4.5%. B5's three under-sized leaves were the uncommitted residue of
the decomposition run made that morning; on the committed tree its n is 0. B2 has no numeric
target and, as Dimon showed, `sync --retire` strips the loser's tags without repointing them —
the "no tag left dangling" guard is cleared by the very operation it guards.

**On the proposal's own facts.** Its Fact block was measured on a working tree carrying three
untracked decomposition children and the whole uncommitted v7.0.0 engine split, and it used the
`ARCH-` id prefix and `level: architecture` as one concept when they differ by exactly those
three files (Wittgenstein, Deming, Napoleon). Both errors are recorded here rather than corrected
away.

## Decision

1. **Decomposition builds downward, and stays that way.** `clarify --decompose` and
   `clarify --levels` write nothing at the system rung and no `satisfies:` edge above the
   requirement they act on. ADR-0030 and ADR-0031 stand as written; `init` remains the one
   place the engine mints the named hole. The skill says so in one sentence beside the
   decompose instructions (A0).
2. **One warn-only rule for the whole axis, at the maintainer's direction — RM032.** The
   Senate refused A2 (a rule for the missing top alone) at 0 of 67, and the first draft of this
   record said "no rule". The same afternoon the maintainer stated the shape he wants as a
   rule: *the code is what matters; because there is a lot of it, it is grouped into
   architecture teams, and the teams into system needs* — so every SYS has at least one ARCH,
   every ARCH at least one REQ, and every REQ and ARCH belongs to a group one rung up. RM032
   (`axis.py`) checks exactly that, in both directions, for enforced requirements that declare
   a `level:`, and nothing for a corpus without the axis (ADR-0019). Measured the day it was
   written: the downward half fires on **5 of 67** architecture requirements
   (`ARCH-ATOMICFORM-053`, `-DESCRIPTION-057`, `-MODULEFILE-056`, `-REDUNDANCY-058`,
   `-VRUNGS-054` — each is its own leaf, with cases and code but no code-rung child); the
   upward half on 0 of 241. That is 2% of the corpus, under ADR-0016's 5% floor, and the
   Senate's objection to A2 stands on the record: this rule ships on the maintainer's
   definition of a well-formed corpus, not on a measured harm. What the rule does NOT do is
   what the Senate refused: it writes nothing, it guesses no need, and a need nothing
   satisfies at all stays RM015's finding. The five it names are the author's to resolve —
   decompose, re-level as `code` under the right architecture group, or merge.
3. **B1 ships alone.** `dupes` skips two children of one parent the way it already skips a
   parent and its child; a cousin under another parent is still compared. One helper, one test,
   one clause and one case on `REQ-SIMILAR-921`, one engine bump.
4. **The two real gaps are closed by hand.** `ARCH-CLARIFY-062` and `ARCH-DESIGN-061` each gain
   the one obligation sentence naming the child they did not name. Two edits to confirmed
   contracts, drift accepted with this record as the reason.
5. **B2, B3, B4-as-a-rule and B5 are not authorised.** B3 may return with `LINT_CONTEXT_MAX`
   fixed on the record against ADR-0016's floor (250 → 8.5%, 300 → 4.5%); B4 only in the form
   that tests what rule 3 says (every declared child linked from the parent's Description) and
   only past the floor it currently fails; B2 only with a stated numeric target and a per-file
   tag-conservation check that survives `sync --retire`; B5 only when its n is not zero.
6. **The docstring of `_write_sys_placeholder` now says what the code does.** Three senators
   found it promising "skipped when the corpus already has a `layer: need`" while the guard is
   the placeholder file's existence. The guard is unchanged — a hand-named need cannot suppress
   the placeholder without leaving every new architecture draft pointing at an id that was never
   written — and the docstring now says that, and why.

## Consequences

- The maintainer's observation is answered as a documented property, not a defect: after
  `decompose`, no SYS appears because none is the engine's to invent.
- `gate --dupes` on this corpus drops from 38 reported pairs to 15 with no requirement file
  changed by the engine; the 15 that remain are the list a human reads.
- Nothing from this record lands in the same release as the v7.0.0 split; the Senate's
  precondition was to commit the split first and re-baseline on the committed tree. The
  maintainer chose to continue in the same working tree, uncommitted; that choice is recorded
  here rather than smoothed over, and the numbers above name which tree each was measured on.

## Revisit when

- **Three or more architecture-level requirements across two or more corpora that are not
  requirement-manager** are observed with no `satisfies:` after a `clarify --decompose` or
  `--levels` run, at least one of those corpora not having come through `init`. Then A2 has a
  population to be measured on, and A1 has a case.
- A consumer reports that the blank `satisfies:` field was not enough to notice a missing top.
- Any of B2–B5 arrives with the evidence rule 5 names.
