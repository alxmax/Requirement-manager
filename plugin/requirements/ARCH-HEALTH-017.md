---
id: ARCH-HEALTH-017
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.14
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002, ARCH-DRIFT-003]
satisfies: [SYS-REPORT-105]
---

# Corpus health snapshot

## Description
> A project can have dozens of requirements slowly rotting — some never coded, some
> untested, some out of sync with the code — and nobody notices until it is a mess. This
> boils the whole registry down to a single health score plus a few counts, so a CI badge
> or a reviewer sees at a glance whether things are in good shape. Without it, corpus decay
> stays invisible until it is expensive to fix.

Every bullet below is binding.
- `next` prints a read-only coherence snapshot of the whole corpus, never writing a file. [[REQ-HEALTH-857]]
- The headline score is the percentage of requirements that are green — passing status, coverage, a test signal, no open verify-intent question, and no drift, all at once. [[REQ-HEALTH-858]]
- `next` prints component counts alongside the score (confirmed, implemented, tested, drafts, orphans, untested, open verify-intent, drift), matches them in `--json`, and always exits 0. [[REQ-HEALTH-859]]
- The same snapshot is written into `_map.json` as a `health` record, so a viewer reads the score rather than defining a second one. [[REQ-HEALTH-968]]
- A reviewed-only score, over confirmed requirements alone, rides beside the headline and is absent when it would only restate it. [[REQ-REVIEWEDSCORE-109]]
## Cases
CASE-1
  Given  a corpus where every requirement is confirmed, implemented, tested, intent-clean, and undrifted
  When   `next` runs
  Then   the score is 100

CASE-2
  Given  an all-draft corpus
  When   `next` runs
  Then   the score is zero

CASE-3
  Given  `--json`
  When   `next` runs
  Then   the output parses as JSON and carries the `score` and `total` keys

CASE-4
  Given  a confirmed requirement with no `implements` member
  When   `next` runs
  Then   it is counted under orphans and not under green

CASE-5
  Given  an empty corpus
  When   `next` runs
  Then   the score is zero and the exit code is zero

CASE-6
  Given  a confirmed `need` satisfied by at least one requirement in an otherwise green corpus
  When   `next` runs
  Then   the score is 100 and the orphan count is zero

CASE-7
  Given  a confirmed `need` that no requirement satisfies
  When   `next` runs
  Then   it is counted under orphans and not under green

## Context
**Terms**
- an axis     one pass/fail question asked of a requirement.
- green       a requirement that passes every axis at once.
- a member    a place in the code tagged as belonging to this requirement.
- the lock    requirements/_reqlock.json — the saved fingerprint of every contract.
- a need      a `layer: need` requirement: a stakeholder need other requirements
- fulfil, rather than code.

**Notes**
- The score is deliberately strict: one open question or one drifted contract drops a requirement out of the green count. This makes the number move when real work remains.
- The "tested" line counts actual `tested-by` members, while the green test counts a `test_exempt` reason as covered. The two can differ by the number of exempted requirements.
- Drift reuses the lock that `sync` maintains. A stale or missing lock yields zero drift, the same fail-open behavior the gate uses.
- The `implemented` and `tested` counts stay code-member counts, so a corpus with a satisfied need shows `implemented < total` while still scoring 100.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py gate --risk` and sees `94/100`, with lines noting 2 requirements have
  no tests and 1 has drifted from its lock. The number is high, so the corpus is healthy;
  she wires `health --json` into CI so the score shows as a badge on every pull request.

**Current implementation**
- `cmd_health` in `reqmap.py` — walks every requirement, classifies each axis using `_member_roles`, `_bullets`, and the lock via `load_lock` + `binding_hash`, then prints the score and counts. `--json` dumps the assembled dictionary instead of the text view.


--------------------


---
id: REQ-HEALTH-857
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
---

# health is a read-only snapshot of the whole corpus

## Description
> `next` boils dozens of slowly-rotting requirements down to one report: it walks every
> requirement, classifies each against a fixed set of axes, and prints the result. It never
> writes a file — not the lock, not a requirement — so running it carries no risk and needs
> no confirmation.

Every bullet below is binding.
- `next` prints a coherence snapshot of the whole requirement corpus.
- `next` writes nothing. It only reads and prints.

## Cases
CASE-1 — health prints a snapshot covering the whole corpus
  Given  a corpus of several requirements in mixed states
  When   `next` runs
  Then   it prints one coherence snapshot summarizing every requirement, not a subset

CASE-2 — health runs without writing any file
  Given  any corpus
  When   `next` runs
  Then   no requirement file or lock file changes, and output goes only to stdout

CASE-3 — the headline score is the percentage that are green
  Given  a ten-requirement corpus where six pass every axis
  When   `next` runs
  Then   the printed score is 60

CASE-4 — an open verify-intent question excludes a requirement from green
  Given  a confirmed, implemented, tested, undrifted requirement carrying one open verify-intent question
  When   `next` runs
  Then   that requirement is excluded from the green count though every other axis passes


--------------------


---
id: REQ-HEALTH-858
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
---

# The headline score: green means every axis passes at once

## Description
> A requirement is "green" only when status, coverage, a test signal, an intent-clean
> history, and an undrifted contract all hold together — one failing axis is enough to drop
> it. `bus`/`feature` requirements need code (`implements`, `tested-by`); a `need` is
> covered once some requirement `satisfies:` it, since a need is fulfilled by requirements,
> not by code, and is otherwise an orphan.

Every bullet below is binding.
- `next` computes a headline score: the percentage of requirements that are green.
- The axes are status `confirmed`, coverage, a test signal, no open verify-intent question,
  and no drift from the lock.
- For a `bus` or `feature` requirement, coverage means an `implements` member.
- For those same layers, the test signal means a `tested-by` member or a `test_exempt` reason.
- A `need` is covered when at least one requirement `satisfies:` it. Its test axis is always
  met, because a need is fulfilled by requirements rather than by code (see [[ARCH-TRACE-020]]).
- A confirmed `need` that no requirement satisfies counts as an orphan.

## Cases
CASE-1 — a bus requirement without an implements member is uncovered
  Given  a `layer: bus` requirement with no `implements` member
  When   `next` runs
  Then   that requirement fails the coverage axis

CASE-2 — a test_exempt reason satisfies the test axis without a tested-by member
  Given  a `layer: feature` requirement with no `tested-by` member but a recorded `test_exempt` reason
  When   `next` runs
  Then   that requirement passes the test axis and its green status is unaffected

CASE-3 — a satisfied need passes its test axis without code
  Given  a `layer: need` requirement satisfied by one other requirement's `satisfies:`
  When   `next` runs
  Then   the need is counted covered and its test axis passes without any code member

CASE-4 — an unsatisfied confirmed need is an orphan
  Given  a confirmed `layer: need` requirement that no requirement's `satisfies:` names
  When   `next` runs
  Then   it is counted under orphans and excluded from green


--------------------


---
id: REQ-HEALTH-859
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
---

# Component counts, --json parity, and an always-zero exit

## Description
> The headline score alone does not say WHAT to fix, so `next` also prints the counts
> behind it — confirmed, implemented, tested, drafts, orphans, untested, open verify-intent,
> drift. `--json` emits the identical numbers so a CI badge and the console view can never
> disagree, and the command always exits 0: it reports on the corpus, it is not a gate.

Every bullet below is binding.
- `next` prints component counts alongside the score: confirmed, implemented, tested,
  drafts, orphans, untested, open verify-intent, and drift.
- `next` prints the reviewed-only score defined by [[REQ-REVIEWEDSCORE-109]] when that
  requirement's conditions hold.
- `--json` emits the same numbers as a JSON object, so the console output and a CI badge
  never disagree.
- On an empty corpus `next` prints a score of zero, with no error and nothing to divide by
  zero.
- `next` always returns zero. The snapshot is a report, not a gate.

## Cases
CASE-1 — the printed counts cover every named category
  Given  a corpus containing at least one draft, one orphan, and one drifted requirement
  When   `next` runs
  Then   it prints counts for confirmed, implemented, tested, drafts, orphans, untested, open verify-intent, and drift

CASE-2 — --json and the console report the same numbers
  Given  any corpus
  When   `next` runs once plainly and once with `--json`
  Then   the score and counts in both outputs match exactly

CASE-3 — an empty corpus reports a score of zero without error
  Given  a `requirements/` directory with no requirement files
  When   `next` runs
  Then   it prints a score of zero, and the run does not raise a division-by-zero error

CASE-4 — health exits zero even when the corpus scores below 100
  Given  a corpus containing orphans and drift, scoring under 100
  When   `next` runs
  Then   the process still exits 0
--------------------


---
id: REQ-HEALTH-968
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
---

# The health record travels with the map

## Description
> The map viewer showed a registry tally but not the headline number `next` opens with,
> and the obvious fix — recomputing the score in JavaScript — is how two surfaces come to
> disagree about how the repo is doing. The engine emits the record it already computes;
> the viewer displays it and defines nothing.

Every bullet below is binding.
- `_health_record` computes the snapshot from the requirements, their members and the lock
  alone, printing nothing. `cmd_health` reads it and layers on the signals that need a code
  root, so there is one computation of the score and one place it is defined.
- `_map.json` carries that record under a `health` key, beside the existing `design` record.
- The record is a pure function of inputs the map already depends on, so a map carrying it
  stays deterministic and `gate`'s freshness check keeps working unchanged.

## Cases
CASE-1 — the map carries the score the console prints
  Given  any corpus
  When   `map` writes `_map.json` and `next --json` runs over the same corpus
  Then   the map's `health.score` equals the score in the JSON snapshot

CASE-2 — the record needs no code root
  Given  a caller with the requirements and members but no code root
  When   `_health_record` runs
  Then   it returns the score and component counts without raising

CASE-3 — regenerating the map twice produces the same bytes
  Given  an unchanged corpus and lock
  When   `map` runs twice
  Then   both runs write byte-identical `_map.json`, so freshness checks stay stable

--------------------


---
id: REQ-REVIEWEDSCORE-109
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v3.1
satisfies: [ARCH-HEALTH-017]
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

## Cases
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

## Context
**Terms**
- green            a requirement that passes every health axis at once, per
- [[ARCH-HEALTH-017]].
- the headline     the existing `score`: green requirements over ALL requirements.
- reviewed         a requirement whose status is `confirmed`. Not merely
- "not a draft": green requires `confirmed`, so any other
- status could enter the denominator but never the numerator.
- a consumer       another repository that vendored this engine and reads its output.

**Notes**
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

**Example**
- Ana vendors the engine into a legacy repo and runs `draft`, which seeds 400 requirements
  from existing code. `health` reads `2/100`, which looks alarming and is not: nothing has
  decayed, nothing has been reviewed. The second line reads `100/100 (8/8 confirmed, 400
  not confirmed yet)`, so she can see her reviewed corpus is clean and the number to move is
  the review backlog, not decay.

**Current implementation**
- The `reviewed_total` / `reviewed_score` block in `cmd_health` (`reqmap.py`), emitted into
  `data` and printed as the `reviewed only:` line under the conditions above.
