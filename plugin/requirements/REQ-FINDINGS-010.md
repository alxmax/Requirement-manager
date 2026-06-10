---
id: REQ-FINDINGS-010
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.08
---

# Open-findings report

> Every requirement file can carry open questions the author still wants a human to double-check.
> Scattered across dozens of files, those questions are easy to forget. This command gathers them
> all into one review list (`_findings.md`) — optionally sorted by an AI helper into real bugs,
> judgement calls, and false alarms. Without it, the open questions stay buried and never get answered.

## WHAT — Contract (normative)
- The command shall scan all requirements and aggregate the bullet items under each one's `## WHAT — Verify intent` section into a single `_findings.md` written in the requirements directory.
- It shall exclude the "None — …" placeholder bullet (a requirement that recorded no open question contributes nothing).
- In raw mode it shall group findings by requirement, each group and the document header carrying a count; with zero findings it shall still write a well-formed file stating none are open.
- When a `_findings_triage.json` sidecar exists and raw mode is off, it shall render a classified view instead: confirmed bugs first ordered by severity (high → low), then product/config decisions, then intentional, then false-positive; bug entries shall show their location and recommended fix when present.
- It shall emit an advisory staleness note when the count of raw verify-intent items differs from the count of triaged items in the sidecar.
- With the raw flag set it shall ignore any sidecar and emit the raw grouped list.
- It shall be deterministic and stdlib-only: it shall not classify findings itself (classification is produced out-of-band by the AI triage pass and supplied through the sidecar) and shall write no file other than `_findings.md`.
- The drift gate (`check`) shall print a non-error advisory line with the open-findings count when that count is greater than zero, and shall not change its exit code on account of findings.

## WHAT — Verify intent (open questions for the human)
- None — this capability is authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Staleness is detected by comparing item *counts*, not content — a sidecar that is stale but happens to match the raw count is not flagged.
- The sidecar is rendered as the source of truth when present; newly added verify-intent items do not appear in the classified view until the AI triage pass regenerates the sidecar (use `--raw` to see the current raw set).

## HOW — Acceptance (= tests)
AC-1
  Given  two requirements, one with two Verify-intent bullets and one with only the "None —" placeholder
  When   `findings` runs in raw mode
  Then   `_findings.md` lists the two bullets under the first requirement and the summary reports "2 open finding(s) across 1 requirement(s)"

AC-2
  Given  a `_findings_triage.json` sidecar classifying one item REAL_BUG (high) and one USER_DECISION
  When   `findings` runs without `--raw`
  Then   the "Confirmed bugs" section precedes "Your call", the bug shows a HIGH badge with its location, and the summary reports "1 confirmed bug(s)"

AC-3
  Given  a sidecar is present
  When   `findings` runs with `--raw`
  Then   the sidecar is ignored and the raw grouped list is written

AC-4
  Given  three raw verify-intent items but only one triaged item in the sidecar
  When   `findings` runs
  Then   `_findings.md` carries a staleness warning advising a re-run of the triage pass

AC-5
  Given  at least one requirement with an open verify-intent item
  When   `check` runs
  Then   it prints an advisory line naming the open-findings count without affecting the error count

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana has 30 requirement files and can't remember which ones still have unanswered questions. She runs `reqmap.py findings` and opens `_findings.md`: it lists "2 open finding(s) across 1 requirement(s)" with both questions quoted under the requirement they came from. After an AI triage pass fills in `_findings_triage.json`, she re-runs and now sees a HIGH-severity confirmed bug at the top, with its file location and a suggested fix — so she knows exactly what to tackle first.

## WHERE — Current implementation
- `collect_findings(reqs)` pulls each requirement's `## WHAT — Verify intent` bullets via `_bullets`, dropping the "None" placeholder, and returns `(id, title, items)` groups. `cmd_findings` reads an optional `_findings_triage.json`; with valid items it calls `_render_findings_triaged` (buckets by classification, sorts REAL_BUG by `_SEV_RANK`, emits a staleness note when raw≠triaged), otherwise `_render_findings_raw`. `cmd_check` calls `collect_findings` to print the advisory count before its summary.

## Links
- Used by: (auto)
## Members in code (auto)
