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
- The `health` command shall print a coherence snapshot of the whole requirement corpus. It writes nothing and is read-only.
- It shall compute a headline score: the percentage of requirements that are green on every axis.
- A requirement is green when it passes every axis at once.
- The axes are: status `confirmed`, coverage, a test signal, no open verify-intent question, and no drift from the lock.
- For a `bus` or `feature` requirement, coverage means an `implements` member and the test signal means a `tested-by` member or a `test_exempt` reason.
- A `need`-layer requirement is covered when at least one requirement `satisfies:` it, and its test axis is always met; a need is fulfilled by requirements, not by code (see [[REQ-TRACE-020]]).
- A confirmed `need` that no requirement satisfies shall count as an orphan.
- It shall print component counts alongside the score: confirmed, implemented, tested, drafts, orphans, untested, open verify-intent, and drift.
- With `--json` it shall emit the same numbers as a JSON object, so the console output and a CI badge never disagree.
- It shall return zero on an empty corpus, printing a score of zero and a hint to bootstrap.
- It shall always return zero. The snapshot is a report, not a gate.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The score is deliberately strict: one open question or one drifted contract drops a requirement out of the green count. This makes the number move when real work remains.
- The "tested" line counts actual `tested-by` members, while the green test counts a `test_exempt` reason as covered. The two can differ by the number of exempted requirements.
- Drift reuses the lock that `check` maintains. A stale or missing lock yields zero drift, the same fail-open behavior the gate uses.
- The `implemented` and `tested` counts stay code-member counts, so a corpus with a satisfied need shows `implemented < total` while still scoring 100.

## HOW — Acceptance (= tests)
- Given a corpus where every requirement is confirmed, implemented, tested, intent-clean, and undrifted, when `health` runs, then the score is 100.
- Given an all-draft corpus, when `health` runs, then the score is zero.
- Given `--json`, when `health` runs, then the output parses as JSON and carries the `score` and `total` keys.
- Given a confirmed requirement with no `implements` member, when `health` runs, then it is counted under orphans and not under green.
- Given an empty corpus, when `health` runs, then the score is zero and the exit code is zero.
- Given a confirmed `need` satisfied by at least one requirement in an otherwise green corpus, when `health` runs, then the score is 100 and the orphan count is zero.
- Given a confirmed `need` that no requirement satisfies, when `health` runs, then it is counted under orphans and not under green.

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
