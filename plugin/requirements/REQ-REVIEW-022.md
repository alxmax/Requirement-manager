---
id: REQ-REVIEW-022
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.14
---

# AI requirement-quality review (deterministic plan + advisory pass)

> Deterministic lint catches the SHAPE of a requirement (long sentences, vague words, size).
> It cannot judge MEANING — whether a contract clause is actually testable, whether the WHY
> explains intent or just restates the title, whether the acceptance criteria really exercise
> the contract. This emits a deterministic, machine-readable plan of each requirement's prose
> so an AI can make that semantic judgement out of band — advisory only, never the gate, never
> auto-applied. A human always decides; the engine never calls an LLM.

## WHAT — Contract (normative)
- The `review` command shall emit a DETERMINISTIC, read-only JSON plan to stdout and write no
  file; it shall never invoke an LLM. `review` (no arg) covers the whole corpus; `review <ID>`
  covers one requirement.
- The plan shall carry, per requirement, its prose (title, intent/WHY, contract, acceptance,
  verify-intent) plus cheap STRUCTURAL anchors that are deterministic facts, not judgements
  (contract-clause count, acceptance count, intent word count, intent-terse, more-contract-than-
  acceptance), and a corpus `coverage_summary` (`total_requirements`, `requirements_in_plan`).
- The plan shall name exactly three AI categories — `untestable-contract`, `why-restates-title`,
  `acceptance-doesnt-cover-contract` — and a finding contract: every AI finding MUST carry a
  concrete `suggested_rewrite`, only high-confidence findings are emitted, and severity is
  advisory-only (never `error`/`warn`, never carried in the engine's severity vocabulary).
- DETERMINISM WALL: the plan shall be byte-reproducible across runs (no clock, no randomness, no
  LLM). No gate path (`gate`, `map --check`, the pre-commit hook, the CI action) shall read, write,
  or regenerate the plan or any AI sidecar.
- `gate` shall behave identically whether or not an AI sidecar (`requirements/_ai_review.md`) is
  present.
- The AI pass is non-deterministic and advisory: its findings carry an unbounded false-positive
  rate. The near-zero-false-positive property comes from MANDATORY human review of each
  `suggested_rewrite`, not from any LLM confidence value (which is uncalibrated triage only).
- The AI consumer (the `requirement-quality-review` skill) shall write findings to a separate,
  clearly-labelled "AI — advisory (non-deterministic)" sidecar — never `_findings.md` (which
  stays deterministic) and never the gate — and shall never auto-edit a requirement.
- `review` is distinct from `show`: `show` is a human single-requirement dossier; `review` is a
  machine corpus plan with structural anchors, a coverage summary and category guidance for an
  out-of-band AI consumer — a different audience and shape, so they are not merged.

## WHAT — Verify intent (open questions for the human)
- None — authored from a Senate design audit (runs/senate/2026-06-09_161036-ai-quality-checker-design.json).

## WHAT — Notes & known limitations (informative)
- The `untestable-contract` / `acceptance-doesnt-cover-contract` categories are deliberately
  judged by the AI, not the engine: a deterministic clause↔acceptance mapping is REQ-ACVERIFY-019's
  job (`# verifies: <id>#AC-N`), and a reliable semantic "cover" check has no deterministic form.
- `jargon-used-before-defined` was deliberately NOT included — REQ-LINT-014 deferred it for lack
  of a domain dictionary, and an LLM does not dissolve that false-positive wall.
- The sidecar is its own channel (not folded into `_findings.md`) precisely to keep the
  deterministic findings surface reproducible; mixing a non-deterministic AI pass into it would
  break that property.

## HOW — Acceptance (= tests)
AC-1
  Given  the corpus
  When   `review` runs with no argument (or as `review <ID>`)
  Then   it emits JSON for every requirement (or that one); neither form writes a file nor
         invokes an LLM

AC-2
  Given  the emitted plan
  When   it is inspected
  Then   it carries a `coverage_summary` with `total_requirements` and `requirements_in_plan`,
         and names the three categories with the suggested_rewrite-required finding contract

AC-3
  Given  the same corpus
  When   `review` runs twice
  Then   the two outputs are byte-identical (deterministic)

AC-4
  Given  a `requirements/_ai_review.md` present or absent
  When   `gate` runs
  Then   its exit code and printed output are byte-identical — the gate never reads the AI sidecar

## WHERE — Current implementation
- `cmd_review` in `reqmap.py` (the deterministic plan emitter), dispatched from `main()` for the
  `review` subcommand; the out-of-band consumer is the `requirement-quality-review` skill.

## Links
- Used by: (auto)
## Members in code (auto)
