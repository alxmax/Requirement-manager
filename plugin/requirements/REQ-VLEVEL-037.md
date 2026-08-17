---
id: REQ-VLEVEL-037
status: draft        # draft | baseline | in-progress | implemented | confirmed | deprecated
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: []       # ids of bus/other capabilities this builds on
superseded_by:       # <ID>, if replaced
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Verification levels

> WHY: 1–3 plain sentences anyone can follow — what this is, why it exists, and
> what breaks without it. No jargon; this is the angle a non-expert reads first.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Audience: a developer new to THIS project. Six rules:
     1. Name the subject: "`init` creates the folder", never "It creates the folder".
     2. Present tense — no "shall", no "must". The line above already binds every clause.
     3. One binding statement per bullet; a second sentence only states the first's
        consequence, never a second obligation.
     4. Define project terms. Two or more: open with a glossary comment like this one.
     5. Group clauses past five, with bold labels (see below).
     6. Keep under 25 words/sentence, 22 words/bullet — `lint` enforces both.
     Scope: one capability = one behavior that fails independently. Many clauses AND
     many acceptance criteria together mean several capabilities — split them
     (`lint` flags this as 'over-scoped'). -->

**What it does**
- `<subject>` does one thing, stated so a test could check it. No function names; true
  regardless of how the code is implemented.
  <!-- Rationale: why this specific behavior, one clause, only when not self-evident -->

**What it produces**
- `<subject>` returns <output shape and allowed values>.
- `<subject>` handles a missing or invalid optional input by <behavior>.

## WHAT — Verify intent (open questions for the human)
- Observed: <a behavior that may be an AI accident — swallowed error, empty-string
  fallback, magic constant, unreachable branch>. Intended, or a bug to fix?

## WHAT — Notes & known limitations (informative)
- A known fragility/footgun the implementer should know but which is NOT enforced.

## HOW — Acceptance (= tests)
<!-- Keep Given/When/Then concrete and self-explanatory; spell out any term the
     Contract introduced. -->
AC-1  <!-- verifiable by: automated test | manual | inspection | load test -->
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>   (one test per AC; each maps to tested-by)

## Example — in practice (optional, non-binding)
<!-- A short plain-language story of the feature in use — the angle anyone reads
     to "get it" fast. NON-BINDING illustration: the Given/When/Then above is the
     precise version; on any conflict the Contract + Acceptance win. This section is
     not hashed and not linted, so it never trips drift. -->
- e.g. Ana marks AUTH-001 confirmed, later edits its contract text; at commit
  `check` tells her "DRIFT — contract changed since lock" so she re-reviews.

## WHERE — Current implementation
- How the code does it today (the volatile narrative — may drift from the contract).

## Links
- Used by: (auto)
## Members in code (auto)
