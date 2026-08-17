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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     finding          one open question a requirement author left for a human, written as a
                      bullet under `## WHAT — Verify intent`.
     the sidecar      `_findings_triage.json` — a file an AI triage pass writes, sorting each
                      finding into a class and a severity.
     raw mode         the `--raw` flag: report the findings as written, ignoring the sidecar.
     classified view  the report shaped by the sidecar's classes instead of by requirement.
     the gate         the `gate` command, run before every commit. -->

**What it collects**
- `findings` scans every requirement and collects the bullet items under each one's
  `## WHAT — Verify intent` section.
- `findings` writes them into a single `_findings.md` in the requirements directory.
- `findings` excludes the "None — …" placeholder bullet. A requirement that recorded no open
  question therefore contributes nothing.

**The raw report**
- In raw mode, `findings` groups the findings by requirement.
- Each group and the document header carry a count.
- With zero findings, `findings` still writes a well-formed file stating that none are open.
- With the raw flag set, `findings` ignores any sidecar and emits the raw grouped list.

**The classified report**
- When the sidecar exists and raw mode is off, `findings` renders a classified view.
- That view puts confirmed bugs first, ordered by severity from high to low, then
  product/config decisions, then intentional, then false-positive.
- A bug entry shows its location and its recommended fix when those are present.
- `findings` emits an advisory staleness note when the count of raw verify-intent items
  differs from the count of triaged items in the sidecar.

**What it never does**
- `findings` is deterministic and stdlib-only. It never classifies a finding itself.
- `findings` writes no file other than `_findings.md`.

**What the gate adds**
- The gate prints a non-error advisory line carrying the open-findings count, whenever that
  count is greater than zero.
- The open-findings count never changes the gate's exit code.

## WHAT — Verify intent (open questions for the human)
- None — this capability is authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- Classification itself is produced out-of-band by the AI triage pass and supplied through the sidecar; the command only renders what the sidecar already decided.
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
  When   `gate` runs
  Then   it prints an advisory line naming the open-findings count without affecting the error count

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana has 30 requirement files and can't remember which ones still have unanswered questions. She runs `reqmap.py findings` and opens `_findings.md`: it lists "2 open finding(s) across 1 requirement(s)" with both questions quoted under the requirement they came from. After an AI triage pass fills in `_findings_triage.json`, she re-runs and now sees a HIGH-severity confirmed bug at the top, with its file location and a suggested fix — so she knows exactly what to tackle first.

## WHERE — Current implementation
- `collect_findings(reqs)` pulls each requirement's `## WHAT — Verify intent` bullets via `_bullets`, dropping the "None" placeholder, and returns `(id, title, items)` groups. `cmd_findings` reads an optional `_findings_triage.json`; with valid items it calls `_render_findings_triaged` (buckets by classification, sorts REAL_BUG by `_SEV_RANK`, emits a staleness note when raw≠triaged), otherwise `_render_findings_raw`. `cmd_check` calls `collect_findings` to print the advisory count before its summary.

## Links
- Used by: (auto)
## Members in code (auto)
