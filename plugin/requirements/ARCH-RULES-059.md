---
id: ARCH-RULES-059
status: confirmed
level: architecture
layer: bus
owner: Alex
priority: must-have
milestone: v3.3
depends_on: [ARCH-CHECK-006, ARCH-PARSE-001]
satisfies: [SYS-GATE-102]
---

# The gate rule registry

## Description
> `cmd_check` used to be four hundred lines of inline checks, and every other command
> that needed to know "what is wrong with this corpus" re-derived the answer its own
> way. That is how `gate`, `health`, `next` and `confirm` came to disagree about who is
> exempt (ADR-0015) and which requirement is oversize (v3.1.0). This makes the rule
> list one registry that every consumer reads, gives each rule a permanent code, and
> lets a requirement opt out of one rule by that code.

Every bullet below is binding.
- `GATE_RULES` holds every gate rule as a `Rule` with a unique `RMnnn` code, a default severity, a `--strict` promotion flag and the function that produces its findings. [[REQ-RULES-947]]
- Every printed gate line carries its rule code, `--json` carries the same findings as records, and `gate_exempt: [RMnnn]` in a requirement's frontmatter silences that one rule for that one requirement. [[REQ-RULES-948]]
- A repo may raise the drift rules to errors for itself through its own config, without `--strict` and without moving anyone else's default; a requirement's own exemption still wins. [[REQ-RULES-989]]

## Cases
CASE-1
  Given  the engine module is imported
  When   `GATE_RULES` is read
  Then   every rule has a distinct `RM` code and a severity of `error` or `warn`

CASE-2
  Given  a corpus with a dangling tag and a confirmed requirement without code
  When   `gate` and `health` run over it
  Then   `health`'s `gate_errors` count equals the number of RM001 and RM006 findings the gate prints

CASE-3
  Given  a requirement whose `gate_exempt:` names `RM013`
  When   `gate` runs
  Then   no RM013 line names that requirement, and every other rule still applies to it

CASE-4
  Given  a drifted confirmed requirement and no per-repo config
  When   the rules run without `--strict`
  Then   the drift finding is a warning

CASE-5
  Given  the same corpus, with a config raising drift to error
  When   the rules run without `--strict`
  Then   the drift finding is an error

CASE-6
  Given  the same config and a requirement exempting itself from the drift rule
  When   the rules run
  Then   that requirement produces neither an error nor a warning for it

## Context
**Notes**
- A retired rule keeps its number: a consumer may already write it in `gate_exempt:`.
- `RM000` is reserved for the `--since` fallback notice, which is not a rule.

--------------------


---
id: REQ-RULES-947
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-RULES-059]
---

# One registry of gate rules

## Description
> A rule is a function that yields `(requirement id, message)` pairs over a
> `GateContext`, registered with `@gate_rule("RMnnn", severity)`. `cmd_check` is only
> the runner: it builds the context once, runs the registry in order, prints, and
> advances the lock. Without a registry, adding a check means editing the runner, and
> every other consumer of the same fact goes stale.

Every bullet below is binding.
- `gate_rule(code, severity, strict=False, only_source_repo=False)` registers a rule in `GATE_RULES`; registering a code twice raises `ValueError`.
- `run_gate_rules(ctx, strict)` runs every rule in registry order. It returns two `Finding` lists, errors then warnings; each finding carries `rule`, `severity`, `rid`, `msg`.
- A rule with `strict=True` has its findings promoted to errors under `--strict`, except RM012 (test-link integrity) on a requirement that is not `confirmed`, which stays a warning.
- A rule with `only_source_repo=True` runs only when `_is_source_repo(code_root)` is true, that is inside the requirement-manager repository itself.
- `_link_sync_errors`, which `health` reads, returns the messages of RM001 and RM006 taken from the registry, so `health` and `gate` cannot count link-sync errors differently.
- `GateContext` computes once what rules read: the id set, both reverse indexes (`satisfies`, `depends_on`), the lock with the fresh binding hashes, the coverage maps.

## Cases
CASE-1 — codes are unique and severities valid
  Given  the engine module
  When   `GATE_RULES` is inspected
  Then   no two rules share a code and each severity is `error` or `warn`

CASE-2 — a duplicate code is refused
  Given  a rule already registered as `RM001`
  When   `gate_rule("RM001", "warn")` decorates another function
  Then   it raises `ValueError`

CASE-3 — strict promotes a strict-flagged rule only
  Given  a corpus with a confirmed drifted contract and a milestone typo
  When   `run_gate_rules(ctx, strict=True)` runs
  Then   the DRIFT finding is an error and the milestone finding stays a warning

CASE-4 — health and gate agree on link-sync errors
  Given  a corpus with one dangling tag and one confirmed requirement without an implements member
  When   `_link_sync_errors` runs
  Then   it returns exactly the two messages RM001 and RM006 produce

CASE-5 — a source-repo-only rule never runs in a consumer repo
  Given  a temporary consumer repo with an `app/src/lib/data.js` fixture that disagrees with its corpus
  When   `gate` runs there
  Then   no RM017 finding is printed

--------------------


---
id: REQ-RULES-948
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-RULES-059]
---

# Codes on every finding, and per-requirement exemption

## Description
> A finding you can name is a finding you can silence, count, or document. Each gate
> line starts with its severity and its code, `WARN  RM013 <message>`, the JSON output
> carries the same finding as a record, and a requirement can declare
> `gate_exempt: [RM013]` to switch that one rule off for itself, the way `lint_exempt:`
> already works for the linter.

Every bullet below is binding.
- `gate` prints each finding as `WARN  RMnnn <message>` or `ERROR RMnnn <message>`; the message text is unchanged from before codes existed.
- `gate --json` emits `errors` and `warnings` as message lists, unchanged, plus `findings`, a list of `{rule, severity, rid, msg}` records.
- A requirement whose `gate_exempt:` list names a rule's code is skipped by that rule; a finding with no requirement id (a corpus-wide finding) cannot be exempted.
- An exemption is per requirement and per rule: naming `RM013` on one requirement changes nothing for any other requirement or rule.
- Rule codes are permanent: a retired rule's code is never reassigned.

## Cases
CASE-1 — the code is printed with the severity
  Given  a corpus with a malformed `milestone:`
  When   `gate` runs
  Then   the output contains `WARN  RM004` followed by the milestone message

CASE-2 — JSON carries findings as records
  Given  the same corpus
  When   `gate --json` runs
  Then  the object has a `findings` list whose entry for RM004 carries `severity` `warn` and the requirement's id, and `warnings` still lists the message string

CASE-3 — gate_exempt silences one rule for one requirement
  Given  two requirements with malformed milestones, one carrying `gate_exempt: [RM004]`
  When   `gate` runs
  Then   only the other requirement's milestone warning is printed

CASE-4 — an exemption does not reach another rule
  Given  a requirement carrying `gate_exempt: [RM004]` that is also confirmed without a `tested-by` member
  When   `gate` runs
  Then   its RM007 warning is still printed


---
id: REQ-RULES-989
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RULES-059]
---

# Drift severity is a repo's own call

## Description
> Whether an out-of-date contract should fail a build or only warn is a real disagreement
> with no universal answer, and this tool had only one setting for everybody. The default
> stays `warn` on recorded evidence — a spec-first edit legitimately puts the contract ahead
> of the code, and a check that fails on correct work gets `continue-on-error` bolted onto it
> and is never read again. A repo that wants the harder line should be able to take it
> without arguing with the tool, and without moving anyone else's default.

Every bullet below is binding.
- `DRIFT_SEVERITY: "error"` in a repo's `_config.json` promotes the drift rules to errors for
  that repo, without `--strict`.
- The default is `warn` and does not move.
- A requirement's own `gate_exempt:` is honoured first: a repo-wide dial never overrules a
  decision written down per requirement.
- The promotion is resolved per run and never written back onto the registered rule, because
  the rule registry is module state that two checks inside one `audit` share.
- A value outside the accepted spellings is reported and skipped, never silently treated as
  the default.

## Cases
CASE-1 — the default is still warn
  Given  a drifted confirmed requirement and no `_config.json`
  When   the rules run without `--strict`
  Then   the drift finding is a warning

CASE-2 — a repo may promote it for itself
  Given  `_config.json` setting `DRIFT_SEVERITY` to `error`
  When   the rules run without `--strict`
  Then   the drift finding is an error

CASE-3 — a requirement's own exemption still wins
  Given  the same config and a requirement whose `gate_exempt:` names the drift rule
  When   the rules run
  Then   that requirement produces neither an error nor a warning for it

CASE-4 — a mistyped value is reported
  Given  `_config.json` setting `DRIFT_SEVERITY` to an unrecognised spelling
  When   the config is applied
  Then   the key is named on stderr and the default is unchanged

CASE-5 — the registry is not mutated
  Given  a promoted run
  When   it finishes
  Then   every registered rule carries the severity it was declared with
