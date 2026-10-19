# ADR-0076 — An audit is a recorded session: a fixed plan, one file of findings, a report with intervals

- **Status:** Accepted. Builds on [ADR-0043](0043-the-engine-is-served-over-mcp.md) (the MCP
  server, read-only by default) and on the report `gate --audit` already prints
  (ARCH-AUDIT-065).
- **Decided:** 2026-10-19
- **Evidence:**
  - Preparing a walkthrough of auditing an already-traced repository with an assistant: the
    method needs a ranked set, a seeded random set, two assistant runs per requirement, one
    counter per finding, and every rate as k/n with an interval. The engine supplies the
    inputs (`gate --risk --json`, `gate --show --json`, `ask --review`, `clarify --json`)
    but none of the bookkeeping, so each step was done by hand.
  - `mcp.tool_list(False)` returns 11 read-only tools; `tool_list(True)` adds only
    `reqmap_sync` and `reqmap_release`. ARCH-MCP-073 freezes the tool set.
  - The command registry is six verbs (REQ-SURFACE-1095).
  - `python scripts/check_engine_budget.py` on this change: core 6,706 logical lines in 61
    modules, 18 above ADR-0075's 6,688. `auditrun.py` is not among them.

## Context

`gate --audit` answers "what can the engine find". An audit of an existing repository asks a
different question: "of what a reviewer looked at, what was really wrong, and how sure are
we". That needs a plan fixed before anyone looks, a record of what each review said and what
a person decided, and arithmetic that does not let five findings read as a rate.

Done by hand, the plan is easy to change after the first results, the findings live in
chat transcripts, and the figures on the last slide have no denominator.

## Decision

An audit is a **session** with three parts, all on existing verbs.

1. **Plan, written once.** `sync --audit-plan` (with `--ranked N`, `--random N`, `--seed S`)
   writes `requirements/_audit.json` with the date, the seed, the ordering key, the ranked
   ids and the random ids, and the decision bands copied from `_config.json`. The ranked set
   is ordered by untested cases, then `clarify` questions, then linked files, ties by id;
   the random set is drawn with `random.Random(seed)` from the requirements not ranked. An
   existing plan is never overwritten: a new audit starts from a new file.

2. **Findings and decisions, in one file a person edits.** Each review run adds a finding
   (`id`, `run`, `label`: `bug` / `not-implemented` / `false-coverage` / `ok`, `clause`,
   `note`). A person adds the decision, which puts the finding in exactly one counter: `B`,
   `F_copilot`, `G`, `A`, `F_tool`, `M`, `U`. An `ok` nobody contradicts needs no decision
   and is counted as `ok`; only the eligible requirements are planned: confirmed, and not a
   `need` or `aggregate`, which carry no code. Like setting `status: confirmed`, the decision
   is an edit, not a command. The engine validates the file and reports a malformed entry as
   an `INPUT:audit` warning (an error under `--strict`), and never rewrites it.

3. **Report and view, derived.** `gate --audit` gains an audit section, in text and `--json`:
   each counter, Copilot precision `B / (B + F_copilot)`, the miss rate on the random set,
   the agreement rate between runs, each as k/n with a Wilson 95% interval, and the band the
   result falls in; with fewer than `AUDIT_MIN_POSITIVES` positives a rate is printed and not
   judged. `sync` carries the same block into `_map.json`, and the viewer gains an **Audit**
   view, so `_map.html` shows the plan, each requirement's runs and decisions, and the rates.

**The assistant's side.** `reqmap_review(id)` (read-only) adds the review prompt and whether
the id is in the plan, so Copilot gets the method with the dossier. `reqmap_audit` already
returns `gate --audit --json`, so it carries the report. No tool is added, and the server
stays read-only: the plan and `_map.html` are written by `sync`, which Copilot runs in the
terminal when instructed (agent mode asks before running it) or a person runs by hand. The
skill ships `references/audit.md` with the prompt and the rules, to copy into the
repository's assistant instructions.

The module that does this is imported at call time, only when `_audit.json` exists or an
audit flag is given. What stays in the core is what has to: the four flags, the dispatch,
the `INPUT:audit` check in the bare gate and the map's audit block, 18 logical lines, so
`CORE_LOGICAL_BUDGET` rises from 6,688 to 6,706 (ADR-0053).

## Alternatives rejected

- **An `audit` verb.** The surface is six verbs; a seventh breaks every caller that lists them.
- **New MCP tools** (`reqmap_audit_plan`, `reqmap_record`). The tool set is frozen until a
  consumer other than the maintainer uses the server.
- **A writing MCP tool for the plan or the map.** It would make "the server does not write"
  false whenever an audit runs, and the privacy argument rests on it.
- **A separate `audit.html`.** A second page to maintain, beside a viewer that already has a
  rail of views.
- **Recording findings through a command.** Flags for every field are longer to type than the
  JSON, and a person's decision belongs in an edit, as confirmation does.

## Consequences

- One committed file per audit is the evidence: the plan before, the findings during, the
  decisions after. Its git history shows whether the plan moved.
- `sync` gains three flags; `gate --audit` and `_map.json` gain a section; the viewer a view.
  A shipped change: semver, `MAP_ENGINE_VERSION`, CHANGELOG, `build:viewer`.
- `_config.json` gains `AUDIT_BANDS` and `AUDIT_MIN_POSITIVES`.

## Revisit when

After the first audit on a repository the maintainer does not own: if the file format was
edited by hand often enough to cause `INPUT:audit` warnings, give recording a command; if the
bands were changed after the plan was written, make the plan refuse a band change.
