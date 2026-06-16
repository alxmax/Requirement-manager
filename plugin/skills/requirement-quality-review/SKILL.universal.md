---
name: requirement-quality-review
description: Use on-demand to AI-review the SEMANTIC quality of requirement files (is a contract clause actually testable, does the WHY explain intent or just restate the title, does the acceptance cover the contract) — judgements deterministic `lint` cannot make. Advisory only, never the gate, never auto-applied. Trigger words: "review my requirements", "are these requirements testable", "AI quality check the specs".
---

<!-- Universal variant: Claude Code-specific wording replaced with generic
     "AI assistant" language. Works with any AI assistant. -->

<!-- implements: REQ-REVIEW-022 -->

# Requirement quality review (AI — advisory)

This skill is the **out-of-band AI consumer** of the deterministic plan emitted by
`reqmap review`. The engine never calls an LLM; the AI assistant makes the semantic
judgements here. **This is advisory only — it is NEVER part of the gate, and the AI
NEVER edits a requirement file.** A human decides what to act on.

## Deterministic complement

Before invoking this skill, run `python scripts/reqmap.py lint` — it catches mechanical
structural issues (missing Contract/Acceptance sections, over-long sentences, stacked
conditions) that do not require AI judgement. Fix lint findings first; this skill covers
the semantic layer lint cannot reach. Add `lint_exempt: [<check>]` to a requirement's
frontmatter to silence a lint check that is intentionally violated (e.g.
`lint_exempt: [ac-count-high]` for a requirement whose many ACs are by design).

## Procedure

1. **Get the plan** (deterministic, read-only — safe to run anywhere):
   ```bash
   python scripts/reqmap.py review            # whole corpus
   python scripts/reqmap.py review AREA-NAME-NNN   # one requirement
   ```
   The JSON carries each requirement's prose + structural `anchors`, a `coverage_summary`,
   and the three `categories` you judge.

2. **Judge ONLY these three categories** (do not invent others; `jargon-before-defined` is
   deliberately out of scope):
   - **untestable-contract** — a contract clause so vague it cannot be verified ("handles
     errors gracefully", "is robust"). Use the `more_contract_than_acceptance` / clause text.
   - **why-restates-title** — the WHY blockquote merely restates the title instead of saying
     what breaks without the capability. The `intent_terse` anchor is a hint, not a verdict.
   - **acceptance-doesnt-cover-contract** — a contract clause with no acceptance criterion
     exercising it. ("Cover" here is your semantic judgement; it is distinct from
     REQ-ACVERIFY-019's deterministic `# verifies: <id>#AC-N` test-to-AC tags.)

3. **Near-zero-false-positive discipline** (the project's prime directive):
   - Emit a finding **only when you are confident** it is a real defect. When unsure, stay silent.
   - **Every finding MUST carry a concrete `suggested_rewrite`** — the exact replacement text.
     A finding without an actionable rewrite is noise; drop it. The human adjudicates each
     rewrite in one glance — that human review, not any confidence number, is what keeps the
     false-positive rate low.
   - Severity is **advisory only**. Never label a finding `error`/`warn`; never imply it blocks
     a commit. Output is non-deterministic — a re-run may differ. Say so.

4. **Write findings to the advisory sidecar** `requirements/_ai_review.md` — **never** to
   `_findings.md` (which stays deterministic) and **never** to the gate. Overwrite it each run
   (never append). Open it with this exact header so no one mistakes it for a gate result:
   ```
   # AI — advisory (non-deterministic). NOT a gate. Generated <ISO date>; engine_version <from plan>.
   # Coverage: <requirements_in_plan>/<total_requirements>. Each item needs human review.
   ```
   Then one section per requirement that has findings; each finding: category · the problem ·
   `suggested_rewrite`. Skip requirements with no findings.

## Hard rules
- Never edit a requirement `.md` file. Propose rewrites; the human applies them.
- Never run as part of `gate` / `map --check` / a pre-commit hook / CI — this is on-demand only.
- If the plan is empty or unreadable, say so and stop; do not fabricate findings.
