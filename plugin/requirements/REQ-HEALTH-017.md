---
id: REQ-HEALTH-017
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002, CORE-DRIFT-003]
superseded_by:
milestone: v1.14
---

# Corpus health snapshot

> A project can have dozens of requirements slowly rotting — some never coded, some
> untested, some out of sync with the code — and nobody notices until it is a mess. This
> boils the whole registry down to a single health score plus a few counts, so a CI badge
> or a reviewer sees at a glance whether things are in good shape. Without it, corpus decay
> stays invisible until it is expensive to fix.

## WHAT — Contract (normative)
Every line in this section is binding.
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
  met, because a need is fulfilled by requirements rather than by code (see [[REQ-TRACE-020]]).
- A confirmed `need` that no requirement satisfies counts as an orphan.

**What it prints**
- `health` prints component counts alongside the score: confirmed, implemented, tested,
  drafts, orphans, untested, open verify-intent, and drift.
- `--json` emits the same numbers as a JSON object, so the console output and a CI badge
  never disagree.
- On an empty corpus `health` prints a score of zero and a hint to bootstrap.

**Exit code**
- `health` always returns zero. The snapshot is a report, not a gate.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The score is deliberately strict: one open question or one drifted contract drops a requirement out of the green count. This makes the number move when real work remains.
- The "tested" line counts actual `tested-by` members, while the green test counts a `test_exempt` reason as covered. The two can differ by the number of exempted requirements.
- Drift reuses the lock that `sync` maintains. A stale or missing lock yields zero drift, the same fail-open behavior the gate uses.
- The `implemented` and `tested` counts stay code-member counts, so a corpus with a satisfied need shows `implemented < total` while still scoring 100.

## HOW — Acceptance (= tests)
AC-1
  Given  a corpus where every requirement is confirmed, implemented, tested, intent-clean, and undrifted
  When   `health` runs
  Then   the score is 100

AC-2
  Given  an all-draft corpus
  When   `health` runs
  Then   the score is zero

AC-3
  Given  `--json`
  When   `health` runs
  Then   the output parses as JSON and carries the `score` and `total` keys

AC-4
  Given  a confirmed requirement with no `implements` member
  When   `health` runs
  Then   it is counted under orphans and not under green

AC-5
  Given  an empty corpus
  When   `health` runs
  Then   the score is zero and the exit code is zero

AC-6
  Given  a confirmed `need` satisfied by at least one requirement in an otherwise green corpus
  When   `health` runs
  Then   the score is 100 and the orphan count is zero

AC-7
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
