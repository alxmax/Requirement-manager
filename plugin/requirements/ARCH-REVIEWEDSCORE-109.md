---
id: ARCH-REVIEWEDSCORE-109
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-HEALTH-017]
satisfies: [SYS-REPORT-105]
superseded_by:
milestone: v3.1
---

# Reviewed-only health score

## Description
> The headline health score cannot tell "nobody has reviewed this yet" from "this is
> rotting". Both read as a low number, because the first axis of green is status
> `confirmed`, so a draft can never be green while it still counts in the total. A repo that
> drafts requirements from legacy code therefore reads near-zero health forever, and the one
> number meant to show decay shows only that reviewing has not finished. This adds a second
> number scored over the reviewed part alone, so the two readings separate.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     green            a requirement that passes every health axis at once, per
                      [[ARCH-HEALTH-017]].
     the headline     the existing `score`: green requirements over ALL requirements.
     reviewed         a requirement whose status is `confirmed`. Not merely
                      "not a draft": green requires `confirmed`, so any other
                      status could enter the denominator but never the numerator.
     a consumer       another repository that vendored this engine and reads its output. -->

**What it computes**
- The reviewed-only score is the percentage of green requirements among the reviewed ones.
- The count of green requirements is the same one the headline uses. Only the denominator
  differs.
- The denominator counts `confirmed` requirements only. A requirement at any other
  status is left out of both sides, so it can never depress the score without being
  able to lift it.

**When it is absent**
- The reviewed-only score is absent, rather than zero, when no requirement is confirmed.
  Zero of zero is not zero per cent.
- The reviewed-only score is absent when no requirement is a draft, because it would then
  restate the headline under a second name.
- `health` prints the score as a line of its own, and `--json` carries it as a key, under
  exactly those same conditions.

**What it does not change**
- The headline score keeps its existing definition, so a badge a consumer already publishes
  reads the number it always read.
- A reader who wants the old behaviour alone ignores the new key; its absence in the two
  cases above leaves an existing `--json` schema untouched.

## Verify intent (open questions for the human)
- None — authored from stated intent after the measurement below.

## Notes & known limitations (informative)
- Measured on this repo at commit `1eea8f1`, when the signal was added: the headline read
  `10/100` while every one of the 71 confirmed requirements was green on every axis — the
  detailed-design drafts [[ARCH-DECOMPOSE-050]] seeded were the whole difference. The
  reviewed-only score read `100/100` there. This is a dated snapshot, not a live figure:
  the corpus only grows ([[ARCH-DECOMPOSE-050]], ADR-0021), so run `health` for today's.
- It shares the "absent, not zero" discipline with the untagged-code count
  ([[ARCH-COVERAGE-029]]), which is the same shape of problem: a signal printed by `health`
  that must not silently widen a consumer's JSON schema.
- Redefining the headline's denominator was rejected instead of this: [[ARCH-HEALTH-017]]
  CASE-2 binds an all-draft corpus to a score of zero, and consumer badges already read that
  key, so moving it would change every published number without notice.
- The score still says nothing about whether a draft *should* exist. A corpus can read
  `100/100` reviewed while carrying hundreds of drafts nobody intends to finish.

## Cases (= tests)
CASE-1
  Given  a corpus of one green confirmed requirement and three drafts
  When   `health` runs
  Then   the headline score is 25 and the reviewed-only score is 100

CASE-2
  Given  an all-draft corpus
  When   `health --json` runs
  Then   the output carries no reviewed-only key, and the headline score is still zero

CASE-3
  Given  a corpus holding no draft at all
  When   `health --json` runs
  Then   the output carries no reviewed-only key

CASE-4
  Given  a corpus holding both drafts and reviewed requirements
  When   `health` runs
  Then   the printed line names the confirmed count and how many are not confirmed yet

CASE-5
  Given  a corpus of one green confirmed requirement, one draft, and one requirement at
         `baseline`, `in-progress`, `implemented` or `deprecated`
  When   `health --json` runs
  Then   the reviewed-only score is 100 and its denominator is 1, because the fourth
         status is neither green nor counted against green

## Context (non-binding)
**Example**
- Ana vendors the engine into a legacy repo and runs `draft`, which seeds 400 requirements
  from existing code. `health` reads `2/100`, which looks alarming and is not: nothing has
  decayed, nothing has been reviewed. The second line reads `100/100 (8/8 confirmed, 400
  not confirmed yet)`, so she can see her reviewed corpus is clean and the number to move is
  the review backlog, not decay.

**Current implementation**
- The `reviewed_total` / `reviewed_score` block in `cmd_health` (`reqmap.py`), emitted into
  `data` and printed as the `reviewed only:` line under the conditions above.

## Links
- Used by: (auto)
## Members in code (auto)
