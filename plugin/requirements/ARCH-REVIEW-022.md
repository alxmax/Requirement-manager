---
id: ARCH-REVIEW-022
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-QUALITY-104]
superseded_by:
milestone: v1.14
lint_exempt: [file-spread]
---

# AI requirement-quality review (deterministic plan + advisory pass)

## Description
> Deterministic lint catches the SHAPE of a requirement (long sentences, vague words, size).
> It cannot judge MEANING — whether a contract clause is actually testable, whether the WHY
> explains intent or just restates the title, whether the acceptance criteria really exercise
> the contract. This emits a deterministic, machine-readable plan of each requirement's prose
> so an AI can make that semantic judgement out of band — advisory only, never the gate, never
> auto-applied. A human always decides; the engine never calls an LLM.
- The `review` command emits a DETERMINISTIC, read-only JSON plan to stdout and writes no
  file; it never invokes an LLM. `review` (no arg) covers the whole corpus; `review <ID>`
  covers one requirement.
- The plan carries, per requirement, its prose (title, intent/WHY, contract, acceptance,
  verify-intent) plus cheap STRUCTURAL anchors that are deterministic facts, not judgements
  (contract-clause count, acceptance count, intent word count, intent-terse, more-contract-than-
  acceptance), and a corpus `coverage_summary` (`total_requirements`, `requirements_in_plan`).
- The plan names exactly three AI categories — `untestable-contract`, `why-restates-title`,
  `acceptance-doesnt-cover-contract` — and a finding contract: every AI finding carries a
  concrete `suggested_rewrite`, only high-confidence findings are emitted, and severity is
  advisory-only (never `error`/`warn`, never carried in the engine's severity vocabulary).
- DETERMINISM WALL: the plan is byte-reproducible across runs (no clock, no randomness, no
  LLM). No gate path (`gate`, `map --check`, the pre-commit hook, the CI action) reads, writes,
  or regenerates the plan or any AI sidecar.
- `gate` behaves identically whether or not an AI sidecar (`requirements/_ai_review.md`) is
  present.
- The AI pass is non-deterministic and advisory: its findings carry an unbounded false-positive
  rate. The near-zero-false-positive property comes from MANDATORY human review of each
  `suggested_rewrite`, not from any LLM confidence value (which is uncalibrated triage only).
- The AI consumer (the `requirement-quality-review` skill) writes findings to a separate,
  clearly-labelled "AI — advisory (non-deterministic)" sidecar — never `_findings.md` (which
  stays deterministic) and never the gate — and never auto-edits a requirement.
- `review` is distinct from `show`: `show` is a human single-requirement dossier; `review` is a
  machine corpus plan with structural anchors, a coverage summary and category guidance for an
  out-of-band AI consumer — a different audience and shape, so they are not merged.

## Verify intent (open questions for the human)
- None — authored from a Senate design audit (runs/senate/2026-06-09_161036-ai-quality-checker-design.json).

## Notes & known limitations (informative)
- The `untestable-contract` / `acceptance-doesnt-cover-contract` categories are deliberately
  judged by the AI, not the engine: a deterministic clause↔acceptance mapping is ARCH-ACVERIFY-019's
  job (`# verifies: <id>#AC-N`), and a reliable semantic "cover" check has no deterministic form.
- `jargon-used-before-defined` was deliberately NOT included — ARCH-LINT-014 deferred it for lack
  of a domain dictionary, and an LLM does not dissolve that false-positive wall.
- The sidecar is its own channel (not folded into `_findings.md`) precisely to keep the
  deterministic findings surface reproducible; mixing a non-deterministic AI pass into it would
  break that property.
- `lint_exempt: file-spread` — the `implements:` members are the engine's `review` command, the
  advisory skill contract and its AI-agnostic variant: one capability whose deterministic half and
  advisory half deliberately live in different files, not a diffuse one.

## Cases (= tests)
CASE-1
  Given  the corpus
  When   `review` runs with no argument (or as `review <ID>`)
  Then   it emits JSON for every requirement (or that one); neither form writes a file nor
         invokes an LLM

CASE-2
  Given  the emitted plan
  When   it is inspected
  Then   it carries a `coverage_summary` with `total_requirements` and `requirements_in_plan`,
         and names the three categories with the suggested_rewrite-required finding contract

CASE-3
  Given  the same corpus
  When   `review` runs twice
  Then   the two outputs are byte-identical (deterministic)

CASE-4
  Given  a `requirements/_ai_review.md` present or absent
  When   `gate` runs
  Then   its exit code and printed output are byte-identical — the gate never reads the AI sidecar

## WHERE — Current implementation
- `cmd_review` in `reqmap.py` (the deterministic plan emitter), dispatched from `main()` for the
  `review` subcommand; the out-of-band consumer is the `requirement-quality-review` skill.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-REVIEW-624
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REVIEW-022]
superseded_by:
---

# The review command emits a DETERMINISTIC, read-only JSON

> The `review` command emits a DETERMINISTIC, read-only JSON plan to stdout and writes no
> file; it never invokes an LLM. `review` (no arg) covers the whole corpus; `review <ID>`
> covers one requirement.

Scenario: review is deterministic, read-only and LLM-free
  Given  any corpus
  When   `review` runs twice with no edit between the runs
  Then   both runs print byte-identical JSON to stdout, create no file, and make no network call

## Members in code (auto)




--------------------


---
id: REQ-REVIEW-625
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REVIEW-022]
superseded_by:
---

# The plan carries, per requirement, its prose (title

> The plan carries, per requirement, its prose (title, intent/WHY, contract, acceptance,
> verify-intent) plus cheap STRUCTURAL anchors that are deterministic facts, not
> judgements (contract-clause count, acceptance count, intent word count, intent-terse,
> more-contract-than- acceptance), and a corpus `coverage_summary` (`total_requirements`,
> `requirements_in_plan`).

Scenario: the plan carries prose, structural anchors and a coverage summary
  Given  one requirement in the corpus
  When   `review <ID>` runs
  Then   its JSON entry carries title, WHY, contract, acceptance, contract-clause count and acceptance count

## Members in code (auto)




--------------------


---
id: REQ-REVIEW-626
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REVIEW-022]
superseded_by:
---

# The plan names exactly three AI categories —

> The plan names exactly three AI categories — `untestable-contract`,
> `why-restates-title`, `acceptance-doesnt-cover-contract` — and a finding contract: every
> AI finding carries a concrete `suggested_rewrite`, only high-confidence findings are
> emitted, and severity is advisory-only (never `error`/`warn`, never carried in the
> engine's severity vocabulary).

Scenario: the plan names the three AI categories and the finding contract
  Given  the emitted review plan
  When   it is inspected
  Then   it names `untestable-contract`, `why-restates-title`, `acceptance-doesnt-cover-contract`,
         each requiring a `suggested_rewrite` and mandatory human review as its
         false-positive safeguard, never an LLM confidence value

## Members in code (auto)




--------------------


---
id: REQ-REVIEW-627
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REVIEW-022]
superseded_by:
---

# DETERMINISM WALL: the plan is byte-reproducible across runs

> DETERMINISM WALL: the plan is byte-reproducible across runs (no clock, no randomness, no
> LLM). No gate path (`gate`, `map --check`, the pre-commit hook, the CI action) reads,
> writes, or regenerates the plan or any AI sidecar.

Scenario: the plan is byte-identical across runs and gate never reads it
  Given  the same corpus and an absent `_ai_review.md` sidecar
  When   `review` runs twice, then `gate` runs
  Then   the two `review` outputs are byte-identical and `gate`'s output is unaffected by the sidecar's absence

## Members in code (auto)




--------------------


---
id: REQ-REVIEW-628
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REVIEW-022]
superseded_by:
---

# Gate behaves identically whether or not an AI

> `gate` behaves identically whether or not an AI sidecar (`requirements/_ai_review.md`)
> is present.

Scenario: gate ignores the AI sidecar file entirely
  Given  `gate` run once with no `_ai_review.md` and once with one present
  When   both runs complete
  Then   their exit codes and printed output are byte-identical

## Members in code (auto)




--------------------


---
id: REQ-REVIEW-630
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REVIEW-022]
superseded_by:
---

# The AI consumer (the requirement-quality-review skill) writes findings

> The AI consumer (the `requirement-quality-review` skill) writes findings to a separate,
> clearly-labelled "AI — advisory (non-deterministic)" sidecar — never `_findings.md`
> (which stays deterministic) and never the gate — and never auto-edits a requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
