---
id: ARCH-FINDINGS-010
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-REPORT-105]
superseded_by:
milestone: v1.08
---

# Open-findings report

## Description
> Every requirement file can carry open questions the author still wants a human to double-check.
> Scattered across dozens of files, those questions are easy to forget. This command gathers them
> all into one review list (`_findings.md`) — optionally sorted by an AI helper into real bugs,
> judgement calls, and false alarms. Without it, the open questions stay buried and never get answered.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     finding          one open question a requirement author left for a human, written as a
                      bullet under `## Verify intent`.
     the sidecar      `_findings_triage.json` — a file an AI triage pass writes, sorting each
                      finding into a class and a severity.
     raw mode         the `--raw` flag: report the findings as written, ignoring the sidecar.
     classified view  the report shaped by the sidecar's classes instead of by requirement.
     the gate         the `gate` command, run before every commit. -->

**What it collects**
- `findings` scans every requirement and collects the bullet items under each one's
  `## Verify intent` section.
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

**How a committed report stays fresh**
- `map` rewrites `_findings.md` when that file already exists. `sync` runs `map`, so it
  refreshes a committed report along with the map.
- `map` never creates `_findings.md`. Running `findings` once opts a repo in.
- `map --check` reports `_findings.md` stale when the committed copy differs from a fresh
  render, the same way it judges `_map.md` and `_map.json`. An absent file is never stale.

**What the gate adds**
- The gate prints a non-error advisory line carrying the open-findings count, whenever that
  count is greater than zero.
- The open-findings count never changes the gate's exit code.

## Verify intent (open questions for the human)
- None — this capability is authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- Classification itself is produced out-of-band by the AI triage pass and supplied through the sidecar; the command only renders what the sidecar already decided.
- Staleness is detected by comparing item *counts*, not content — a sidecar that is stale but happens to match the raw count is not flagged.
- The sidecar is rendered as the source of truth when present; newly added verify-intent items do not appear in the classified view until the AI triage pass regenerates the sidecar (use `--raw` to see the current raw set).

## Cases (= tests)
CASE-1
  Given  two requirements, one with two Verify-intent bullets and one with only the "None —" placeholder
  When   `findings` runs in raw mode
  Then   `_findings.md` lists the two bullets under the first requirement and the summary reports "2 open finding(s) across 1 requirement(s)"

CASE-2
  Given  a `_findings_triage.json` sidecar classifying one item REAL_BUG (high) and one USER_DECISION
  When   `findings` runs without `--raw`
  Then   the "Confirmed bugs" section precedes "Your call", the bug shows a HIGH badge with its location, and the summary reports "1 confirmed bug(s)"

CASE-3
  Given  a sidecar is present
  When   `findings` runs with `--raw`
  Then   the sidecar is ignored and the raw grouped list is written

CASE-4
  Given  three raw verify-intent items but only one triaged item in the sidecar
  When   `findings` runs
  Then   `_findings.md` carries a staleness warning advising a re-run of the triage pass

CASE-5
  Given  at least one requirement with an open verify-intent item
  When   `gate` runs
  Then   it prints an advisory line naming the open-findings count without affecting the error count

CASE-6
  Given  a committed `_findings.md`, and a requirement that then gains a verify-intent item
  When   `map` runs
  Then   `_findings.md` carries the new item, and with no `_findings.md` present `map` creates none

CASE-7
  Given  a committed `_findings.md` that no longer matches the requirements
  When   `map --check` runs
  Then   it names `_findings.md` as stale and exits non-zero

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana has 30 requirement files and can't remember which ones still have unanswered questions. She runs `reqmap.py findings` and opens `_findings.md`: it lists "2 open finding(s) across 1 requirement(s)" with both questions quoted under the requirement they came from. After an AI triage pass fills in `_findings_triage.json`, she re-runs and now sees a HIGH-severity confirmed bug at the top, with its file location and a suggested fix — so she knows exactly what to tackle first.

## WHERE — Current implementation
- `collect_findings(reqs)` pulls each requirement's `## Verify intent` bullets via `_bullets`, dropping the "None" placeholder, and returns `(id, title, items)` groups. `cmd_findings` reads an optional `_findings_triage.json`; with valid items it calls `_render_findings_triaged` (buckets by classification, sorts REAL_BUG by `_SEV_RANK`, emits a staleness note when raw≠triaged), otherwise `_render_findings_raw`. `cmd_check` calls `collect_findings` to print the advisory count before its summary.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-395
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Findings scans every requirement and collects the bullet

> `findings` scans every requirement and collects the bullet items under each one's `##
> WHAT — Verify intent` section.

Scenario: findings collects verify-intent bullets from every requirement
  Given  two requirements, each with one non-placeholder Verify-intent bullet
  When   `findings` runs
  Then   `_findings.md` contains both bullets, one from each requirement

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-396
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Findings writes them into a single _findings.md in

> `findings` writes them into a single `_findings.md` in the requirements directory.

Scenario: findings writes its report to a single file
  Given  a requirement with one open Verify-intent bullet
  When   `findings` runs
  Then   the requirements directory gains one new file, `_findings.md`, holding that
         bullet, and no other file appears

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-397
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Findings excludes the "None — …" placeholder bullet

> `findings` excludes the "None — …" placeholder bullet. A requirement that recorded no
> open question therefore contributes nothing.

Scenario: findings drops the None placeholder bullet
  Given  a requirement whose Verify-intent section holds only the "None — …" bullet
  When   `findings` runs
  Then   that requirement contributes no bullets to `_findings.md`

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-398
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# In raw mode, findings groups the findings by

> In raw mode, `findings` groups the findings by requirement.

Scenario: raw mode groups findings under their requirement
  Given  two requirements each carrying one open Verify-intent bullet
  When   `findings` runs in raw mode
  Then   `_findings.md` lists each bullet nested under its own requirement's heading

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-399
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Each group and the document header carry a

> Each group and the document header carry a count.

Scenario: raw report prints a count per group and in the header
  Given  a requirement with two open Verify-intent bullets
  When   `findings` runs in raw mode
  Then   the requirement's group heading and the document header both show the count 2

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-400
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# With zero findings, findings still writes a well-formed

> With zero findings, `findings` still writes a well-formed file stating that none are
> open.

Scenario: findings writes a clean report when nothing is open
  Given  a corpus where every Verify-intent section holds only the "None —" placeholder
  When   `findings` runs
  Then   `_findings.md` is written and states that no findings are open

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-401
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# With the raw flag set, findings ignores any

> With the raw flag set, `findings` ignores any sidecar and emits the raw grouped list.

Scenario: --raw ignores a present triage sidecar
  Given  a `_findings_triage.json` sidecar and at least one open Verify-intent bullet
  When   `findings` runs with `--raw`
  Then   `_findings.md` shows the raw grouped list, not the sidecar's classified sections

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-402
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# When the sidecar exists and raw mode is

> When the sidecar exists and raw mode is off, `findings` renders a classified view.

Scenario: findings renders a classified view when a sidecar exists
  Given  a `_findings_triage.json` sidecar present and no `--raw` flag
  When   `findings` runs
  Then   `_findings.md` is organized into classified sections using only the classes the
         sidecar already assigned, never ones `findings` computes itself

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-403
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# That view puts confirmed bugs first, ordered by

> That view puts confirmed bugs first, ordered by severity from high to low, then
> product/config decisions, then intentional, then false-positive.

Scenario: classified view orders sections by severity then class
  Given  a sidecar classifying items REAL_BUG (high), REAL_BUG (low), USER_DECISION, INTENTIONAL
         and FALSE_POSITIVE
  When   `findings` runs without `--raw`
  Then   the high-severity bug lists first, then the low-severity bug, then the decision, then
         intentional, then false-positive

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-404
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# A bug entry shows its location and its

> A bug entry shows its location and its recommended fix when those are present.

Scenario: a confirmed bug entry shows its location and fix
  Given  a sidecar classifying one item REAL_BUG with a location and a recommended fix
  When   `findings` runs without `--raw`
  Then   that entry in `_findings.md` prints both the location and the fix

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-405
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Findings emits an advisory staleness note when the

> `findings` emits an advisory staleness note when the count of raw verify-intent items
> differs from the count of triaged items in the sidecar.

Scenario: findings warns when raw and triaged counts diverge
  Given  three raw Verify-intent items but only one item recorded in the sidecar
  When   `findings` runs
  Then   `_findings.md` carries an advisory staleness note

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-408
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Map rewrites _findings.md when that file already exists

> `map` rewrites `_findings.md` when that file already exists. `sync` runs `map`, so it
> refreshes a committed report along with the map.

Scenario: map refreshes an already-committed findings report
  Given  a committed `_findings.md` and a requirement that gained a new Verify-intent item
  When   `map` runs
  Then   the regenerated `_findings.md` includes the new item

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-409
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Map never creates _findings.md. Running findings once opts

> `map` never creates `_findings.md`. Running `findings` once opts a repo in.

Scenario: map never creates a findings report that does not exist yet
  Given  no `_findings.md` file present in the requirements directory
  When   `map` runs
  Then   no `_findings.md` is created; only a subsequent `findings` run creates one

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-410
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# Map --check reports _findings.md stale when the committed

> `map --check` reports `_findings.md` stale when the committed copy differs from a fresh
> render, the same way it judges `_map.md` and `_map.json`. An absent file is never stale.

Scenario: map --check flags a stale findings report but never an absent one
  Given  a committed `_findings.md` that no longer matches the requirements, and separately a
         repo with none committed
  When   `map --check` runs in each case
  Then   it reports the first `_findings.md` as stale and exits non-zero, and reports nothing
         for the absent one

## Members in code (auto)




--------------------


---
id: REQ-FINDINGS-411
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-FINDINGS-010]
superseded_by:
---

# The gate prints a non-error advisory line carrying

> The gate prints a non-error advisory line carrying the open-findings count, whenever
> that count is greater than zero.

Scenario: gate prints the open-findings count as an advisory
  Given  a requirement with one open Verify-intent item
  When   `gate` runs
  Then   its output includes a line naming the open-findings count, and its exit code is
         unaffected

## Members in code (auto)
