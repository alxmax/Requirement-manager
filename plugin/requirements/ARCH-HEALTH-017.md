---
id: ARCH-HEALTH-017
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002, ARCH-DRIFT-003]
satisfies: [SYS-REPORT-105]
superseded_by:
milestone: v1.14
---

# Corpus health snapshot

## Description
> A project can have dozens of requirements slowly rotting — some never coded, some
> untested, some out of sync with the code — and nobody notices until it is a mess. This
> boils the whole registry down to a single health score plus a few counts, so a CI badge
> or a reviewer sees at a glance whether things are in good shape. Without it, corpus decay
> stays invisible until it is expensive to fix.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     an axis     one pass/fail question asked of a requirement.
     green       a requirement that passes every axis at once.
     a member    a place in the code tagged as belonging to this requirement.
     the lock    requirements/_reqlock.json — the saved fingerprint of every contract.
     a need      a `layer: need` requirement: a stakeholder need other requirements
                 fulfil, rather than code. -->

**What it is**
- `health` prints a coherence snapshot of the whole requirement corpus.
- `health` writes nothing. It only reads and prints.

**How it scores**
- `health` computes a headline score: the percentage of requirements that are green.
- The axes are status `confirmed`, coverage, a test signal, no open verify-intent question,
  and no drift from the lock.
- For a `bus` or `feature` requirement, coverage means an `implements` member.
- For those same layers, the test signal means a `tested-by` member or a `test_exempt` reason.
- A `need` is covered when at least one requirement `satisfies:` it. Its test axis is always
  met, because a need is fulfilled by requirements rather than by code (see [[ARCH-TRACE-020]]).
- A confirmed `need` that no requirement satisfies counts as an orphan.

**What it prints**
- `health` prints component counts alongside the score: confirmed, implemented, tested,
  drafts, orphans, untested, open verify-intent, and drift.
- `health` prints the reviewed-only score defined by [[ARCH-REVIEWEDSCORE-109]] when that
  requirement's conditions hold.
- `--json` emits the same numbers as a JSON object, so the console output and a CI badge
  never disagree.
- On an empty corpus `health` prints a score of zero and a hint to bootstrap.

**Exit code**
- `health` always returns zero. The snapshot is a report, not a gate.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The score is deliberately strict: one open question or one drifted contract drops a requirement out of the green count. This makes the number move when real work remains.
- The "tested" line counts actual `tested-by` members, while the green test counts a `test_exempt` reason as covered. The two can differ by the number of exempted requirements.
- Drift reuses the lock that `sync` maintains. A stale or missing lock yields zero drift, the same fail-open behavior the gate uses.
- The `implemented` and `tested` counts stay code-member counts, so a corpus with a satisfied need shows `implemented < total` while still scoring 100.

## Cases (= tests)
CASE-1
  Given  a corpus where every requirement is confirmed, implemented, tested, intent-clean, and undrifted
  When   `health` runs
  Then   the score is 100

CASE-2
  Given  an all-draft corpus
  When   `health` runs
  Then   the score is zero

CASE-3
  Given  `--json`
  When   `health` runs
  Then   the output parses as JSON and carries the `score` and `total` keys

CASE-4
  Given  a confirmed requirement with no `implements` member
  When   `health` runs
  Then   it is counted under orphans and not under green

CASE-5
  Given  an empty corpus
  When   `health` runs
  Then   the score is zero and the exit code is zero

CASE-6
  Given  a confirmed `need` satisfied by at least one requirement in an otherwise green corpus
  When   `health` runs
  Then   the score is 100 and the orphan count is zero

CASE-7
  Given  a confirmed `need` that no requirement satisfies
  When   `health` runs
  Then   it is counted under orphans and not under green

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py health` and sees `94/100`, with lines noting 2 requirements have
  no tests and 1 has drifted from its lock. The number is high, so the corpus is healthy;
  she wires `health --json` into CI so the score shows as a badge on every pull request.

## WHERE — Current implementation
- `cmd_health` in `reqmap.py` — walks every requirement, classifies each axis using `_member_roles`, `_bullets`, and the lock via `load_lock` + `binding_hash`, then prints the score and counts. `--json` dumps the assembled dictionary instead of the text view.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-HEALTH-413
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# Health prints a coherence snapshot of the whole

> `health` prints a coherence snapshot of the whole requirement corpus.

Scenario: health prints a snapshot covering the whole corpus
  Given  a corpus of several requirements in mixed states
  When   `health` runs
  Then   it prints one coherence snapshot summarizing every requirement, not a subset

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-414
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# Health writes nothing. It only reads and prints

> `health` writes nothing. It only reads and prints.

Scenario: health runs without writing any file
  Given  any corpus
  When   `health` runs
  Then   no requirement file or lock file changes, and output goes only to stdout

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-415
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# Health computes a headline score: the percentage of

> `health` computes a headline score: the percentage of requirements that are green.

Scenario: the headline score is the percentage that are green
  Given  a ten-requirement corpus where six pass every axis
  When   `health` runs
  Then   the printed score is 60

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-416
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# The axes are status confirmed, coverage, a test

> The axes are status `confirmed`, coverage, a test signal, no open verify-intent
> question, and no drift from the lock.

Scenario: an open verify-intent question excludes a requirement from green
  Given  a confirmed, implemented, tested, undrifted requirement carrying one open verify-intent question
  When   `health` runs
  Then   that requirement is excluded from the green count though every other axis passes

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-417
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# For a bus or feature requirement, coverage means

> For a `bus` or `feature` requirement, coverage means an `implements` member.

Scenario: a bus requirement without an implements member is uncovered
  Given  a `layer: bus` requirement with no `implements` member
  When   `health` runs
  Then   that requirement fails the coverage axis

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-418
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# For those same layers, the test signal means

> For those same layers, the test signal means a `tested-by` member or a `test_exempt`
> reason.

Scenario: a test_exempt reason satisfies the test axis without a tested-by member
  Given  a `layer: feature` requirement with no `tested-by` member but a recorded `test_exempt` reason
  When   `health` runs
  Then   that requirement passes the test axis and its green status is unaffected

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-419
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# A need is covered when at least one

> A `need` is covered when at least one requirement `satisfies:` it. Its test axis is
> always met, because a need is fulfilled by requirements rather than by code (see
> [[ARCH-TRACE-020]]).

Scenario: a satisfied need passes its test axis without code
  Given  a `layer: need` requirement satisfied by one other requirement's `satisfies:`
  When   `health` runs
  Then   the need is counted covered and its test axis passes without any code member

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-420
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# A confirmed need that no requirement satisfies counts

> A confirmed `need` that no requirement satisfies counts as an orphan.

Scenario: an unsatisfied confirmed need is an orphan
  Given  a confirmed `layer: need` requirement that no requirement's `satisfies:` names
  When   `health` runs
  Then   it is counted under orphans and excluded from green

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-421
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# Health prints component counts alongside the score: confirmed

> `health` prints component counts alongside the score: confirmed, implemented, tested,
> drafts, orphans, untested, open verify-intent, and drift.

Scenario: the printed counts cover every named category
  Given  a corpus containing at least one draft, one orphan, and one drifted requirement
  When   `health` runs
  Then   it prints counts for confirmed, implemented, tested, drafts, orphans, untested, open verify-intent, and drift

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-422
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# --json emits the same numbers as a JSON

> `--json` emits the same numbers as a JSON object, so the console output and a CI badge
> never disagree.

Scenario: --json and the console report the same numbers
  Given  any corpus
  When   `health` runs once plainly and once with `--json`
  Then   the score and counts in both outputs match exactly

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-423
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# On an empty corpus health prints a score

> On an empty corpus `health` prints a score of zero and a hint to bootstrap.

Scenario: an empty corpus reports zero with a bootstrap hint
  Given  a `requirements/` directory with no requirement files
  When   `health` runs
  Then   it prints a score of zero and a hint to run the bootstrap command

## Members in code (auto)




--------------------


---
id: REQ-HEALTH-424
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-HEALTH-017]
superseded_by:
---

# Health always returns zero. The snapshot is a

> `health` always returns zero. The snapshot is a report, not a gate.

Scenario: health exits zero even when the corpus scores below 100
  Given  a corpus containing orphans and drift, scoring under 100
  When   `health` runs
  Then   the process still exits 0

## Members in code (auto)
