---
id: ARCH-AUDITRUN-076
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v8.25
depends_on: [ARCH-AUDIT-065, ARCH-MCP-073, ARCH-VIEWER-007]
satisfies: [SYS-REPORT-105]
---

# An audit is a recorded session

## Description
> `gate --audit` says what the engine can find. Auditing a repository that is already traced
> asks something else: of what a reviewer looked at, what was really wrong, and how sure we
> are. That takes a plan fixed before anyone looks, a record of every review and decision,
> and figures that carry their denominator. See
> [ADR-0076](../../docs/adr/0076-an-audit-is-a-recorded-session.md).

Every bullet below is binding.
- `sync --audit-plan` writes the audit plan once, ranked and seeded, before the first review. [[REQ-AUDITRUN-1105]]
- Findings and decisions live in `requirements/_audit.json`, which a person edits and the engine only validates. [[REQ-AUDITRUN-1106]]
- `gate --audit` reports every audit rate as k/n with its interval, and the band the result falls in. [[REQ-AUDITRUN-1107]]
- The map shows the audit in a view of its own, and the MCP server stays read-only. [[REQ-AUDITRUN-1108]]
- The review dossier an assistant reads carries the review prompt and the plan. [[REQ-AUDITRUN-1109]]

## Cases
CASE-1 — a whole session runs on the existing verbs
  Given  a repository with requirements, code and tests, and no `_audit.json`
  When   `sync --audit-plan` runs, two findings and their decisions are added to the file, and
         `gate --audit --json` runs
  Then   the report counts both findings, and the command registry still has six verbs

CASE-2 — the MCP tool set does not change
  Given  the server started without `--allow-writes`
  When   its tools are listed while an audit is in progress
  Then   they are the same 11 read-only tools as without an audit

CASE-3 — the map shows the session
  Given  a session with a plan and one decision
  When   `sync` runs
  Then   `_map.json` carries an `audit` block whose counters include that decision

--------------------


---
id: REQ-AUDITRUN-1105
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDITRUN-076]
---

# The plan is fixed before the first review

## Description
> A plan that can change after the first results is not a plan. Writing it to a committed
> file before anyone reviews makes any later change visible in git.

Every bullet below is binding.
- `sync --audit-plan` writes `requirements/_audit.json` with the date, the seed, the ordering key, the ranked ids, the random ids, and the bands from `AUDIT_BANDS`.
- `--ranked N` and `--random N` set the two sizes (default 25 each); `--seed S` sets the seed, and without it the seed is the date as `YYYYMMDD`, printed.
- The ranked set is the first N requirements ordered by untested cases, then `clarify` questions, then linked files, all descending, ties by id ascending.
- The random set is drawn with `random.Random(seed)` from the requirements not ranked, sorted by id before the draw, so one seed always gives one set.
- When `_audit.json` already holds a plan, `--audit-plan` writes nothing and exits 1, naming the file.
- Only requirements with `status: confirmed` that carry code are eligible: a `layer: need` or `aggregate` has none to compare a clause with.

## Cases
CASE-1 — the plan is written with its seed
  Given  a corpus of 60 confirmed requirements and no `_audit.json`
  When   `sync --audit-plan --ranked 5 --random 5 --seed 7` runs
  Then   `_audit.json` holds 5 ranked ids, 5 random ids, seed 7, the date and the bands

CASE-2 — one seed gives one set
  Given  the same corpus, planned twice in two copies with seed 7
  When   the two plans are compared
  Then   the ranked and the random ids are identical

CASE-3 — the ranked set follows the ordering key
  Given  requirement A with 3 untested cases, B with 1 and 4 `clarify` questions, C with 1 and none
  When   `--ranked 3` plans
  Then   the ranked order is A, B, C

CASE-4 — an existing plan is not replaced
  Given  an `_audit.json` that already holds a plan
  When   `sync --audit-plan` runs again
  Then   it exits 1, names the file, and the file is byte-identical

CASE-5 — a draft is never sampled
  Given  a corpus with draft and confirmed requirements
  When   the plan is written
  Then   no draft id is in either set

--------------------


---
id: REQ-AUDITRUN-1106
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDITRUN-076]
---

# Findings and decisions are recorded in one file

## Description
> A finding that lives in a chat transcript cannot be counted, and a decision made in a
> meeting cannot be checked. Like confirming a requirement, deciding a finding is an edit a
> person makes, not a command.

Every bullet below is binding.
- A finding has `id`, `run`, `label`, `clause` and `note`.
- `run` is a whole number from 1; `label` is one of `bug`, `not-implemented`, `false-coverage`, `ok`.
- `clause` is a clause number, or null for the whole requirement.
- Findings with the same `id` and `clause` are one finding over several runs.
- A decision names one finding by `id` and `clause`, who decided as `by`, and exactly one counter: `B`, `F_copilot`, `G`, `A`, `F_tool`, `M`, `U`.
- An `ok` nobody contradicts needs no decision and counts as `ok`.
- A person who finds a bug behind an `ok` decides `M`.
- An entry with a missing field, an unknown label or counter, an id outside the plan, or a second decision for one finding is reported as an `INPUT:audit` warning naming the entry; `--strict` makes it an error.
- The engine never writes findings or decisions, and never rewrites `_audit.json` after the plan.

## Cases
CASE-1 — a valid record is read
  Given  a plan, two findings for one id in runs 1 and 2, and one decision `B`
  When   `gate --audit --json` runs
  Then   the audit section counts one `B` and no `INPUT:audit` warning appears

CASE-2 — a malformed entry is named, not fixed
  Given  a finding with label `maybe` and a decision with counter `X`
  When   `gate` runs, then `gate --strict` runs
  Then   both entries are named as `INPUT:audit` warnings, the second run exits 1, and the file is unchanged

CASE-3 — an id outside the plan is refused
  Given  a finding for a requirement in neither set
  When   `gate --audit` runs
  Then   the entry is named as an `INPUT:audit` warning and is not counted

CASE-4 — one finding, one counter
  Given  two decisions for the same finding
  When   `gate --audit` runs
  Then   the second is named as an `INPUT:audit` warning and only the first is counted

--------------------


---
id: REQ-AUDITRUN-1107
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDITRUN-076]
---

# The report gives every rate as k/n with its interval

## Description
> Twelve bugs means nothing without the number of requirements reviewed, and three of four
> means little without how wide that could be. The report states the denominator and the
> interval every time, and refuses to judge a rate built on too few cases.

Every bullet below is binding.
- `gate --audit` prints an audit section when `_audit.json` exists, in text and in `--json`, and its exit code is unchanged by it.
- The section gives each counter, Copilot precision `B / (B + F_copilot)`, the miss rate `M / random reviewed`, and the agreement rate between runs, each as k/n with a Wilson 95% interval.
- A finding whose runs disagree on the label counts in `U`, whatever was decided.
- The section names the band the result falls in, from the plan's bands; a rate with fewer than `AUDIT_MIN_POSITIVES` positives (default 5) is printed and marked not judged.
- `reqmap_audit` returns the same section, because it returns `gate --audit --json`.

## Cases
CASE-1 — a rate carries its interval
  Given  decisions giving B = 7 and F_copilot = 13
  When   `gate --audit --json` runs
  Then   precision is 7/20 with a 95% interval of about 0.18 to 0.57

CASE-2 — zero is an upper bound
  Given  25 random requirements reviewed and M = 0
  When   the report runs
  Then   the miss rate is 0/25 with an upper bound of about 0.13

CASE-3 — too few positives are not judged
  Given  B + F_copilot = 4
  When   the report runs
  Then   precision is printed and marked not judged, and no band is named for it

CASE-4 — runs that disagree are unresolved
  Given  one finding labelled `bug` in run 1 and `ok` in run 2, decided `B`
  When   the report runs
  Then   it counts in `U`, not in `B`

CASE-5 — the exit code is the gate's
  Given  a clean gate and an audit whose band is `stop`
  When   `gate --audit` runs
  Then   it exits 0

--------------------


---
id: REQ-AUDITRUN-1108
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDITRUN-076]
lint_exempt: [file-spread]
---

# The map shows the audit, and the server stays read-only

## Description
> The report is for the terminal; the map is what a team opens. Writing the map stays with
> `sync`, run by a person or by the assistant in the terminal when told to, so "the server
> does not write" stays true while an audit runs.

Every bullet below is binding.
- `sync` copies the audit section into `_map.json` under `audit` when `_audit.json` exists, and omits the key otherwise.
- The viewer's Workspace rail lists Audit only when the map carries an `audit` block.
- The Audit view shows: the plan with its seed; each requirement's runs and decisions; the counters; every rate as k/n with its interval.
- The view marks each requirement as not reviewed, reviewed once, reviewed twice, or decided, which is every finding in a counter or settled as `ok`.
- No MCP tool is added, and no tool writes `_audit.json` or `_map.html`.

## Cases
CASE-1 — the map carries the audit
  Given  an `_audit.json` with a plan and two decisions
  When   `sync` runs
  Then   `_map.json` has an `audit` block with both decisions and the plan's seed

CASE-2 — no audit, no key
  Given  no `_audit.json`
  When   `sync` runs
  Then   `_map.json` has no `audit` key and the rail lists no Audit entry

CASE-3 — the view shows progress and rates
  Given  a map whose audit has 4 planned ids: one decided, one reviewed twice, one once, one not at all
  When   the Audit view is rendered
  Then   each id shows its state, and every rate is shown as k/n with its interval

CASE-4 — the server does not write during an audit
  Given  an audit in progress and a server started without `--allow-writes`
  When   every tool is called once
  Then   `_audit.json`, `_map.json` and `_map.html` are byte-identical afterwards

## Context
**Notes**
- `lint_exempt: file-spread` — the audit block is one obligation written in two places: the engine builds it into the map and the viewer draws it, so its members span the engine package and three viewer directories by design.

--------------------


---
id: REQ-AUDITRUN-1109
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDITRUN-076]
---

# The review dossier carries the method

## Description
> An assistant that reads the dossier but not the method will review in its own way. Putting
> the prompt and the plan beside the dossier means every run starts from the same instruction.

Every bullet below is binding.
- While a session is open, `ask --review` adds a top-level `audit` holding the review prompt and the four labels.
- Each requirement in its output gains `in_plan`: `ranked`, `random` or `no`.
- `reqmap_review` returns the same, because it runs `ask --review`.
- For each clause, the prompt asks for the code line that does it and the test that proves it.
- The prompt asks for one label per finding, from the four.
- The skill ships `references/audit.md` with the same prompt and the rules: never edit a requirement or its status, one requirement per conversation, two runs each.
- Without `_audit.json` the dossier is unchanged.

## Cases
CASE-1 — the dossier carries the prompt
  Given  a plan whose ranked set holds REQ-A
  When   `ask --review REQ-A --json` runs
  Then   the requirement's `in_plan` is `ranked`, and `audit.prompt` names the four labels

CASE-2 — a requirement outside the plan says so
  Given  the same plan and REQ-Z in neither set
  When   `ask --review REQ-Z --json` runs
  Then   its `in_plan` is `no`

CASE-3 — no audit, no change
  Given  no `_audit.json`
  When   `ask --review REQ-A --json` runs
  Then   the output has no `audit` key and the requirement no `in_plan`
