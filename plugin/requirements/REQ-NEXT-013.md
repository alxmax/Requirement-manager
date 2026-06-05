---
id: REQ-NEXT-013
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-MAP-007]
superseded_by:
---

# What-should-I-do-next report

> Render the map's risk surface in the terminal as counted, actionable buckets, so a human knows where to start without opening the HTML map.

## WHAT — Contract (normative)
- It shall group every requirement's open risk signals into action buckets, reusing the same `_risk_signals` + `RISK_ADVICE` that drive the Risk tab — the dedup of a draft's intent question lives in that shared source, so `next` and the Risk tab show the same signals for the same requirement.
- It shall print a progress header `N requirement(s) · X confirmed · Y tested · Z draft(s)` before the buckets, where `tested` counts requirements with a `tested-by` member.
- It shall surface exactly the actionable buckets — `unimplemented` (Orphans), `untested` (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review) — in that most-urgent-first order, and shall omit `blast-radius` (a caution, not a task).
- Within each bucket it shall order items by descending extract `risk:` score then by id (so REVIEW-flagged drafts come first), tag items with `risk: >= 2` as `[REVIEW]`, and name the requirement file to open (`requirements/<ID>.md`).
- By default it shall show at most the top few items per bucket and, when a bucket has more, print a `... N more — run \`reqmap.py next --all\`` line; with `--all` it shall list every item. Each bucket is truncated independently, so a higher-priority bucket is never hidden below a longer lower-priority one.
- With a registry that has no requirements it shall print a distinct "no requirements yet" message pointing at `init`/`new` (never the all-clear line); with requirements but no open signals it shall print the all-clear line.
- It shall be read-only and deterministic: it writes no files and always exits zero (advice, not a gate).

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A reviewed requirement may legitimately appear in more than one bucket (e.g. a confirmed requirement both `untested` and `unverified-intent`) — these are two distinct actions, by design. A `draft` never double-lists, because its `unverified-intent` is suppressed at the source (subsumed by `unreviewed`).
- `next` is the prioritized worklist; `findings` remains the exhaustive raw list of every open verify-intent bullet (including drafts). The two answer different questions — this divergence is intentional and documented, not drift.
- `risk:` ordering only discriminates extract-authored drafts (hand-authored requirements have no `risk:` field → score 0, ordered by id).

## HOW — Acceptance (= tests)
- The output starts with a progress header carrying the confirmed/tested/draft counts.
- Given a confirmed requirement with implementing code but no `tested-by`, `next` lists it under "Needs tests" with `requirements/<ID>.md`.
- Given a draft requirement, `next` lists it under "Drafts to review" and NOT under "Needs intent review" even when it has an open verify bullet (source dedup).
- Given a confirmed requirement with an open Verify-intent bullet, `next` lists it under "Needs intent review".
- Given a bucket with more items than the top-N, the default view truncates and prints a `... N more` line; `--all` lists every item.
- Within a bucket, a draft with `risk: 2` (REVIEW) is ordered before a `risk: 0` draft and tagged `[REVIEW]`.
- Given an empty registry, `next` prints the "no requirements yet" message; given requirements with no open signals, it prints the all-clear line. Either way it writes no files and returns 0.

## WHERE — Current implementation
- `cmd_next` and `_risk_score` in `reqmap.py` — prints the header, builds a minimal node per requirement, collects `_risk_signals`, orders each bucket by `risk:` score then id, truncates to the top-N unless `--all`, and prints `RISK_ADVICE` text. The draft intent-dedup is in `_risk_signals` (shared with the Risk tab).

## Links
- Used by: (auto)
## Members in code (auto)
