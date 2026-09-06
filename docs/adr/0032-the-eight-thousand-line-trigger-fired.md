# ADR-0032 — ADR-0014's line-count trigger fired; the audit is scheduled, not pre-empted

- **Status:** Accepted — does **not** supersede [ADR-0014](0014-engine-stays-one-file.md); it records that one of that record's revisit conditions is now met
- **Decided:** 2026-09-06, after a three-personality Trias deliberation (Essentialist / Verifier / Sentinel, unanimous) with a post-vote skeptic
- **Owner:** Alex
- **Audit due:** 2026-12-06
- **Evidence:** measurements below, each reproducible by the command named beside it

## Context

[ADR-0014](0014-engine-stays-one-file.md) kept the engine as one file and added no size gate.
It pre-committed to three numeric conditions that would reopen the question. One of them reads:

> **`wc -l plugin/scripts/reqmap.py` crosses 8,000** — roughly another burst-cycle of the same
> character as the one measured here.

It has fired. A pre-committed trigger that fires and is not recorded is worse than no trigger at
all, because the next reader cannot tell whether it was considered or missed. This record exists
so that question has an answer.

**What was measured** (`wc -l`, `git log --numstat`, `git rev-list`, on 2026-09-06):

| | ADR-0014, 2026-08-21 | today, 2026-09-06 |
|---|---|---|
| `plugin/scripts/reqmap.py` | 5,544 lines | **10,202 lines** |
| top-level defs/classes | 158 | 325 |
| `implements:` occurrences inside the engine | 175 | **356** |
| tests | 511 | 1,045 |
| commits touching the engine | 130 of ~390 (33%) | 197 of 549 (36%) |
| per-commit net delta (rolling 90 days) | median +11, p90 +72 | median +17, p90 +100 |

The trajectory, week by week, read off `main`: **5,544** (08-21) → 6,179 (08-28) → 6,654
(09-01) → 7,561 (09-03) → **10,066** (09-06, at the last merge; the working tree that carries
this record is at 10,202). The file grew **84% in sixteen days**.

The 8,000 line was crossed by a single commit — `c11bd23`, 2026-09-04, *"Add `design`: advisory
OOP + standards review of the repo's code, with a design score in the map"* — which took the file
from 7,561 to 8,298 in one step.

## Decision

**No split. No line-count gate. Schedule the costed audit ADR-0014 asked for, with a date and an
owner attached, and record here what today's evidence already settles.**

ADR-0014's closing instruction on a trigger is explicit: *"re-run the audit with cost data — the
thing this round could not produce."* Splitting now on the strength of a number, with no more cost
data than the round that already refused to, would repeat the exact error that record named:
*machinery bought against an unmeasured cost is machinery bought on taste.*

Three things today's measurements settle in advance, so the audit starts from them rather than
re-deriving them:

1. **The other two triggers are not met.** One merge commit touched the engine in the rolling 90
   days, against a threshold of three conflicts; and no external consumer has asked for the
   split-module form. Only the size trigger fired, and size alone is what ADR-0014 already
   declined to act on.
2. **A ≤1,000-line `gate.py` is arithmetically impossible.** The bare `gate --code ..` executes
   **2,297 of 10,066 lines** under `sys.settrace`. Any artifact carrying the verdict must carry
   the parser, the binding hash, the drift baseline and the rule registry; a thousand-line file
   holding `init`/`new`/`sync`/`gate` would be a different tool wearing the same name. The
   ambition is legitimate; that particular number is not a target, it is a slogan.
3. **The relocation cost has more than doubled and is the audit's real subject.** ADR-0014 named
   175 in-engine `implements:` occurrences as a reason a split rewrites member `loc` paths inside
   the committed, freshness-checked `_reqlock.json` and `_map.json`. That figure is now **356**.
   The audit must price that migration, not assume it.

One further observation this round produced, which the audit should carry: the commit that
crossed the trigger is also the one that put an advisory pass onto the mandatory verdict path
(see [issue #243](https://github.com/alxmax/Requirement-manager/issues/243)). The growth that
fired a *size* trigger and the growth that leaked a *severity* boundary were the same growth.
Whether that is coincidence or a pattern is a question with more decision value than the line
count, and it is not answerable from `wc -l`.

## Consequences

- The engine stays one file for now, and nothing automated complains — unchanged from ADR-0014.
- **A dated obligation now exists** where before there was a fired trigger and silence. On or
  before **2026-12-06** the owner re-runs ADR-0014's audit with cost data, and writes a record
  either way — including "still no split", which is a decision and must be recorded as one.
- The three numbers the audit needs are named above, so the next round does not spend itself
  re-measuring: the relocation cost (356 tag sites), the merge-conflict rate, and a named
  external consumer, if one has appeared.
- ADR-0014 is **not** edited. Its decision and its evidence were correct on its date; this record
  is what happens next, which is why it is a new file rather than a rewrite of that one.

## Revisit when

- **2026-12-06**, unconditionally — the scheduled audit. A date with no owner is a wish; this one
  has both.
- **A named external consumer asks for the split-module form.** Still ADR-0014's trigger, still
  unmet, and still the one that would change the answer fastest.
- **3 or more merge conflicts touching `plugin/scripts/reqmap.py` in a rolling 90 days.** At one
  merge commit in the last 90 days, this remains the concrete harm a split would prevent and the
  concrete harm that has not happened.
- **The file crosses 15,000 lines before the scheduled date.** At the measured rate that is weeks,
  not months, and it would mean the growth is not a burst cycle but the new baseline — which is a
  different question from the one ADR-0014 answered.
