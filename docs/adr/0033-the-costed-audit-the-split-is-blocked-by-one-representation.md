# ADR-0033 — The costed audit: still one file, and the split is blocked by one representation

- **Status:** Accepted — discharges the obligation [ADR-0032](0032-the-eight-thousand-line-trigger-fired.md) scheduled, and **retires ADR-0014's line-count trigger** without disturbing its decision
- **Decided:** 2026-09-06, at the maintainer's direction, ahead of the 2026-12-06 date ADR-0032 set
- **Owner:** Alex
- **Evidence:** every number below was measured on `b0bcce8`, by the command named beside it

## Context

[ADR-0032](0032-the-eight-thousand-line-trigger-fired.md) recorded that [ADR-0014](0014-engine-stays-one-file.md)'s
`wc -l > 8,000` trigger had fired, and scheduled the costed re-audit ADR-0014's closing line
demands: *"re-run the audit **with cost data** — the thing this round could not produce."*
It set 2026-12-06 so that three months of churn would exist to measure.

The audit was run early, on 2026-09-06, on the maintainer's instruction and against the
recorded recommendation to wait. That is stated here rather than smoothed over: the reader
should know which numbers are three months thinner than intended. **The churn figures below
are the ones affected**; the structural and relocation figures are not — they are properties of
the tree as it stands.

Since ADR-0014, one thing changed that makes a costed audit possible at all: the engine now
measures its own shape. `gate --design` (`ARCH-DESIGN-061`) did not exist in August. It is the
first instrument this project has ever had that prices the file it lives in.

## What was measured

**Structure** (`ast`, `wc -l`, on 2026-09-06):

| | ADR-0014, 2026-08-21 | today |
|---|---|---|
| lines | 5,544 | **10,239** |
| top-level defs/classes | 158 | **325** |
| functions | — | 351 (median **15** lines, p90 **52**, longest 162) |
| import lines | 1 | **1** |
| tests / statement coverage | 511 / 92% | **1,027 / 93%** |
| lines a bare `gate --code ..` executes | — | **2,312 of 10,238 (23%)** |

**Churn** (`git log --numstat`, rolling 90 days — *the figures thinned by running early*):

| | ADR-0014 | today |
|---|---|---|
| commits touching the engine | 130 of ~390 (33%) | **199 of 551 (36%)** |
| per-commit net delta | median +11, p90 +72 | median **+17**, p90 **+103** |
| top-10 commits' share of growth | **59%** | **42%** |

**The harm ADR-0014 said a split would prevent:**

| signal | threshold | measured |
|---|---|---|
| merge commits touching the engine, rolling 90 days | 3 conflicts | **1, in the whole history** |
| reverts attributable to the engine | — | **0** |
| a named external consumer wanting split modules | 1 | **0** |

**The relocation cost** (`_map.json`, `grep`):

| | ADR-0014 | today |
|---|---|---|
| `implements:` occurrences inside the engine | 175 | **356** |
| member `loc` entries pointing into `reqmap.py` | — | **580** |
| requirements owning at least one engine member | — | **215 of 249** |

**The split map, produced by the tool itself.** `gate --design` reports 45 shape findings on
`reqmap.py`, including `file-too-long` (10,239 over a ceiling of 500) and
`too-many-definitions` (325 over 30). Seven of them are `prefix-family` findings, and a
prefix family is a module boundary the code has already drawn:

| family | defs | lines |
|---|---|---|
| `rule` | 30 | 283 |
| `cmd` | 25 | 1,701 |
| `design` | 21 | 461 |
| `load` | 10 | 187 |
| `lint` | 8 | 314 |
| `render` | 7 | 146 |
| `scan` | 6 | 192 |
| (`build`, `save`, `parse`) | 13 | 389 |
| **total** | **120 of 325** | **3,673 (36% of the file)** |

The `data-clump` findings name the bus those modules would share — `reqs`, `members`,
`reqs_dir`, `code_root` travelling together — and that bus already exists as `Workspace`
(`ARCH-RULES-059`). The seams are drawn and the shared type is written.

## Decision

**Still one file. Retire ADR-0014's line-count trigger. Name the one thing that actually
blocks the split, and make removing it the precondition for re-opening.**

### 1. ADR-0014's reasoning survives its own trigger firing

Two of its three findings are stronger today than when they were written, and the third is
what fired:

1. *"The premise was never established — no option named a single failure caused by line
   count."* Still true, and better evidenced: **one** merge commit has ever touched the file,
   against a threshold of three in ninety days; zero reverts; 1,027 tests at 93% coverage.
   The harm remains hypothetical after doubling the file.
2. *"A fixed threshold here is not a control limit, it is an arbitrary line."* **The trigger
   proved its own point.** 8,000 was crossed by `c11bd23` — a burst feature landing (`design`,
   +737 lines in one commit), which is precisely the moment ADR-0014 predicted a budget would
   fire and be least wanted. It then told us nothing we did not know.
3. *"The split's own economics are inverted."* **Sharply worse.** The tag count doubled, and
   the truer figure — member `loc` entries inside committed, freshness-checked artifacts — is
   **580 across 215 requirements**. A split rewrites every one of them in a single commit.

### 2. The size trigger is retired, because it fires on the wrong thing

A trigger that fires on a number nobody can act on is worse than none: it manufactures an
obligation, consumes an audit, and returns the answer it started with. 8,000 fired. 15,000
would fire. Neither says anything about whether the file is costing anyone.

It is replaced by the two conditions that describe harm rather than size — the merge-conflict
rate and a named external consumer, both already in ADR-0014 and both still unmet — plus the
one below, which is new and is the point of this record.

### 3. The split is blocked by one representational choice, not by its own difficulty

The dominant cost is not "moving code". It is that **580 member locations are anchored to
line numbers** inside artifacts the gate compares byte-for-byte.

The engine already solved this, elsewhere, and did not notice. `compute_member_hashes`
(`ARCH-MEMBERDRIFT-027`) keys a member as **`relfile#definition`**, because *"the unit of
ownership is the unit the tag sits in"*. `_memberlock.json` has been definition-anchored since
it shipped. `_map.json`'s `loc` is `relfile:line`.

Two representations of one fact, in one engine: one survives a file being split, one does not.

So the honest statement of the cost is not *"a split is expensive"*. It is:

> **A split is expensive because member locations are line-anchored. Make `loc`
> definition-anchored — the representation the member sidecar already uses — and the dominant
> cost of the split largely disappears.**

That is the cost data ADR-0014 asked for, and it points at a much smaller piece of work than
the split itself. It is **not** scheduled here: doing it *in order to* enable a split nobody
has asked for would be the same taste-driven machinery ADR-0014 refused. It is recorded so
that the next round starts from a priced decision instead of an argument about a line count.

## Consequences

- The engine stays one hand-authored file. No build step, no concatenation, no byte-compare on
  the repository's highest-churn file, no second artifact for `sync_reqmap.sh` to half-refresh.
- **ADR-0014's `wc -l > 8,000` trigger no longer stands**, and no line-count trigger replaces
  it. ADR-0014 itself is not edited; its decision is unchanged and this record supersedes only
  that one revisit condition.
- **ADR-0032's 2026-12-06 obligation is discharged**, early. If the maintainer wants the
  three-month churn picture the original date was chosen for, this record is the baseline to
  compare against — the structural and relocation figures are directly re-measurable by the
  commands named above.
- The design review's verdict on its own host — `file-too-long`, `too-many-definitions` — stays
  reported and stays advisory. It is a shape worth a look, and this record is the look.

## Revisit when

- **3 or more merge conflicts touching `plugin/scripts/reqmap.py` in a rolling 90 days.**
  Carried forward from ADR-0014, unchanged, and still the concrete harm. Measured: one merge
  commit in the whole history.
- **A named external consumer wants the split-module form.** Carried forward, still zero.
- **Member locations become definition-anchored.** If `loc` ever moves to the
  `relfile#definition` key `_memberlock.json` already uses — for its own reasons, not for this
  one — the split's dominant cost is gone and the question deserves a fresh audit the same
  week.
- **Not on any line count.** That trigger has been tried, has fired, and returned nothing.
