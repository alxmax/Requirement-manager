---
id: REQ-NEXT-013
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-MAP-007]
superseded_by:
milestone: v1.12
lint_exempt: [ac-count-high]
---

# What-should-I-do-next report

> Faced with a whole project of requirements, it's hard to know what to work on first. This command
> looks at every requirement, spots the gaps — ones with no code, no tests, or unanswered questions —
> and prints them as a short, prioritised to-do list right in the terminal. It puts the most urgent
> work at the top so you can just start. Without it, you'd have to open the visual map and eyeball the
> risk yourself to figure out where to begin.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     risk signal     one open gap the engine spots on a requirement: no code, no test,
                     an unanswered question, an unreviewed draft.
     bucket          one named group of items in the report, e.g. "Needs tests".
     the Risk tab    the Risk diagram of the generated map, which reads the same signals.
     membership tag  a comment in code naming a requirement, such as `implements:`.
     code_root       the directory `next` walks to find files; a caller may omit it. -->

**What it collects**
- `next` groups every requirement's open risk signals into action buckets.
- `next` reads those signals from `_risk_signals` and their wording from `RISK_ADVICE`, the
  same two sources that drive the Risk tab. There is never a second signal path.

**What it prints first**
- `next` prints a progress header `N requirement(s) · X confirmed · Y tested · Z draft(s)`
  before the buckets.
- In that header, `tested` counts the requirements that have a `tested-by` member.

**Which buckets it shows**
- `next` surfaces exactly the actionable buckets: `unimplemented` (Orphans), `untested`
  (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review).
- `next` prints those four buckets in that order, most urgent first.
- `next` omits `blast-radius`, because that signal is a caution, not a task.
- `next` surfaces every scannable file that carries no membership tag as an "Untagged files"
  bucket, ranked lowest of all.
- `next` skips that untagged scan when the caller gives no `code_root`.

**How it orders a bucket**
- Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:`
  score, then by id.
- Priority rank runs `must-have` < `should-have` < `could-have` < `wont-have`. A requirement
  with no `priority` ranks last.
- `next` tags an item whose `risk:` is 2 or more with `[REVIEW]`.
- `next` names the requirement file to open, as `requirements/<ID>.md`.

**How much it shows**
- By default `next` shows at most the top few items of a bucket.
- `next` prints a `... N more` line when a bucket holds more items than it showed.
- With `--all`, `next` lists every item.
- The "Untagged files" bucket truncates the same way as the others.

**When there is nothing to do**
- With a registry that holds no requirements, `next` prints a distinct "no requirements yet"
  message pointing at `init`/`new`. `next` never prints the all-clear line in that case.
- With requirements but no open signal, `next` prints the all-clear line.

**What it never does**
- `next` is deterministic and writes no file.
- `next` always exits zero. The report is advice, not a gate.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Each bucket is truncated independently, so a higher-priority bucket is never hidden below a longer lower-priority one.
- The dedup of a draft's intent question lives inside the shared `_risk_signals` source, which is why `next` and the Risk tab report the same signals for the same requirement.
- The untagged-files scan is skipped when no `code_root` is supplied — the usual case for unit-test callers.
- A reviewed requirement may legitimately appear in more than one bucket (e.g. a confirmed requirement both `untested` and `unverified-intent`) — these are two distinct actions, by design. A `draft` never double-lists, because its `unverified-intent` is suppressed at the source (subsumed by `unreviewed`).
- `next` is the prioritized worklist; `findings` remains the exhaustive raw list of every open verify-intent bullet (including drafts). The two answer different questions — this divergence is intentional and documented, not drift.
- `risk:` ordering only discriminates extract-authored drafts (hand-authored requirements have no `risk:` field → score 0, ordered by id).

## HOW — Acceptance (= tests)
AC-1
  Given  any corpus
  When   `next` runs
  Then   the output starts with a progress header carrying the confirmed/tested/draft counts

AC-2
  Given  a confirmed requirement with implementing code but no `tested-by`
  When   `next` runs
  Then   it is listed under "Needs tests" with `requirements/<ID>.md`

AC-3
  Given  a draft requirement with an open verify bullet
  When   `next` runs
  Then   it is listed under "Drafts to review" and NOT under "Needs intent review" (source dedup)

AC-4
  Given  a confirmed requirement with an open Verify-intent bullet
  When   `next` runs
  Then   it is listed under "Needs intent review"

AC-5
  Given  a bucket with more items than the top-N
  When   `next` runs
  Then   the default view truncates and prints a `... N more` line; `--all` lists every item

AC-6
  Given  a draft with `risk: 2` (REVIEW) and a `risk: 0` draft in one bucket
  When   `next` runs
  Then   the REVIEW draft is ordered first and tagged `[REVIEW]`

AC-7
  Given  a `must-have`, a `should-have`, and a no-`priority` requirement in one bucket
  When   `next` runs
  Then   they are ordered must-have, should-have, then no-priority

AC-8
  Given  an empty registry, or one with no open signals
  When   `next` runs
  Then   it prints the "no requirements yet" message or the all-clear line respectively,
         writes no files, and returns 0

AC-9
  Given  scannable files in the repo with no membership tag
  When   `next` runs with a code_root
  Then   they are listed under "Untagged files" with a `reqmap.py draft` suggestion

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana starts her day unsure what's most important. She runs `reqmap.py next` and sees a header — "12 requirement(s) · 8 confirmed · 5 tested · 2 draft(s)" — followed by tidy buckets: "Orphans" (requirements with no code) on top, then "Needs tests", then "Drafts to review". One item is tagged `[REVIEW]` and names the exact file to open. She picks the top item and gets to work, no HTML map needed.

## WHERE — Current implementation
- `cmd_next`, `_risk_score`, and `_scan_untagged` in `reqmap.py` — prints the header, builds a minimal node per requirement, collects `_risk_signals`, orders each bucket by `risk:` score then id, truncates to the top-N unless `--all`, and prints `RISK_ADVICE` text. The draft intent-dedup is in `_risk_signals` (shared with the Risk tab). `_scan_untagged` adds the untagged-files bucket using the same walk as `scan_members`.

## Links
- Used by: (auto)
## Members in code (auto)
