# ADR-0016 — No first-class edge-case marker, section, or heuristic

- **Status:** Rejected (considered, deliberately not built)
- **Decided:** 2026-09-02, after a nine-senator Senate audit (`runs/senate/2026-09-02_084505-reqmap-edge-case-handling.json`, two rounds, verdict MODIFY, 7 MODIFY / 2 GO, six of the MODIFY votes blocking)
- **Evidence:** measurements below, each reproducible by the command named beside it

## Context

The question was whether the engine has, or should have, a first-class notion of *edge-case
handling* per requirement. It has none: no marker, no section, no count, no check. The
question came from the maintainer, not from a consumer — no consumer of the two known corpora
(this repo, 51 confirmed requirements; Management_Dashboard, 55) has asked for one.

Four shapes were audited:

- **(A)** a marker on acceptance criteria (`AC-3 (edge)`), an `edge_acs` count in `_map.json`,
  a warn-only lint firing on a confirmed requirement with three or more contract clauses and
  zero marked criteria, a `next` bucket, and a viewer count;
- **(B)** a new template section `## HOW — Edge cases`, each line pointing at an `AC-N` or
  marked out of scope;
- **(C)** no engine change: a fourth advisory category, `missing-edge-case`, in the AI
  `requirement-quality-review` skill;
- **(D)** a heuristic in `plan`/`draft` that turns error branches in the members
  (`raise`/`except`/`return None`/guard clauses) into Verify-intent questions.

**What was measured** (this repo's corpus, 2026-09-02):

| | | how |
|---|---|---|
| confirmed requirements (A)'s lint would fire on, day one | **47 / 51** by the engine's own clause metric (`groups or len(_bullets(body, "contract"))`, `cmd_lint`); **51 / 51** on raw bullets | the two counts differ because "contract clause" already has two senses in the engine |
| adoption of the closest optional per-criterion marker, `verifiable by:` | **2 / 51**, both being the requirements that document the marker | `grep -l "verifiable by" plugin/requirements/*.md` |
| requirements already carrying a bold `**Edge cases**` contract clause-group | **1 / 51** (`CORE-PARSE-001`) | `grep -l "\*\*Edge cases\*\*" plugin/requirements/*.md` |
| occurrences of the word `edge` in the corpus meaning a *graph* edge | **25 of 26** | `grep -in "edge" plugin/requirements/*.md` |
| real incidents traced to an edge case absent from a requirement | **1** (`REQ-INIT-012` AC-7: an isolated subagent worktree doubling every member, v2.29.2) | `CHANGELOG.md` |
| same-family precedents, resolved | **4 / 4** shipped only the read-only or advisory variant ([ADR-0012](0012-internal-consistency-lint-rejected.md), `REQ-COVERAGE-029`, the MCP deferral, [ADR-0014](0014-engine-stays-one-file.md)) | `runs/senate/outcomes.jsonl` |

## Decision

Build none of the four. Record why, with the numbers, so the next proposer inherits them.

Four findings decided it:

1. **Edge cases already have a home in each state of their lifecycle.** An edge case nobody
   has answered belongs in `## WHAT — Verify intent`: SKILL.md rule 7 names "edge cases not
   covered" as that section's content and says to fold the answer into the Contract. An
   answered one is a bold clause-group in the Contract — `CORE-PARSE-001` does exactly this,
   `_is_label_line` recognises it, and `lint` counts it. A tested one is an `AC-N` a `verifies`
   tag points at. Shapes (A) and (B) add a third home for a fact that has two, against SKILL.md
   rule 4 ("one fact, one home"). What the corpus lacks is not a mechanism but a *definition*
   of the term — and no shape supplied a rejection criterion, a sentence that says what is
   **not** an edge case.
2. **Shape (A) is ADR-0012 with a worse number.** That record rejected a warn-only lint that
   used a syntactic proxy for a semantic property after measuring a 78.6% false-positive rate.
   (A)'s lint fires on 92% of this corpus on day one, all of it authored correctly under the
   current convention, because no criterion carries the marker yet — and the marker's closest
   precedent has 2/51 adoption, so `edge_acs` would report near zero on a corpus that
   demonstrably contains edge-case clauses. A count that is wrong in the reassuring direction
   is worse than no count.
3. **The vocabulary is taken.** `edge` means a `depends_on` link in 25 of its 26 occurrences
   in the corpus. An engine-parsed `(edge)` token is a homonym injected at the single-source-
   of-truth layer. Any future marker must be an HTML comment on the label, as `verifiable by:`
   is, drawn from a closed word list beside `_AC_MANUAL_WORDS` — `_acc_blocks` already strips
   those from the rendered text, so a comment form leaks nothing into `acc` or the viewer,
   while a parenthetical suffix survives `_AC_LABEL_RE` and would leak into both (the
   representation-desync class of `REQ-VIEWER-007` AC-8, fixed in v2.29.2).
4. **Shape (C) is not free either.** The three existing review categories judge text that is
   *present*; "a missing edge case" is an open-world absence judgement an LLM can always
   populate with a plausible invented case. It cannot join a skill whose prime directive is a
   near-zero false-positive rate without that rate being measured first. Musk's second-round
   position — that even (C) duplicates rule 7's exact words — is recorded as the strict
   reading; the majority left (C) eligible on the condition below.

Demand was the other axis. The one real incident (`REQ-INIT-012` AC-7) was not a failure of any
mechanism that claims to catch edge cases, because none does; and one is one short of the bar
ADR-0012 set. Every advisory or warn-only mechanism in this repo has stayed at its launch
severity — `REQ-ACVERIFY-019`, `REQ-COVERAGE-029`, `REQ-REVIEW-022` — so "ship advisory now,
earn a gate later" is not a path this repo has ever walked.

## Consequences

- No change to `reqmap.py`, to the requirement template, to the review skill, or to any
  requirement file. The falsifier is `git diff --stat` on those paths for this decision:
  zero lines.
- Authors keep using the two existing homes. Rule 7 already tells them to; this record is the
  pointer to it.
- The engine's `edge` vocabulary stays single-sense.
- This record exists because a rejection is worth as much as an acceptance here. Without it
  the gap looks unnoticed, and someone re-proposes the 92%-fire-rate version.

## Revisit when

Any one of these, each a number rather than an appeal:

- **(A)** a dry run of a *final* predicate — "contract clause" pinned to the `cmd_lint`
  expression, activation silent until the requirement carries at least one HTML-comment
  marker from a closed list — fires on **5–40%** of confirmed requirements **and** at least
  **8 of 10** sampled flags are confirmed real gaps by a human reader;
- **(B)** at least **5 of 51** requirements have adopted a bold `**Edge cases**` clause-group
  on their own (today: 1) — authors voting for the section with their hands before the engine
  names it;
- **(C)** a trial of the advisory category over at least **10** requirements, with its
  false-positive rate *measured and published*, not assumed; the category must carry both
  halves of a definition (what a boundary behaviour is, and what is not one) and a name that
  does not collide with the graph sense — `missing-boundary-behavior`, not
  `missing-edge-case`;
- **(D)** a recorded incident where a shipped defect traces to an edge case absent from the
  requirement *and* present in code the heuristic would have read;
- or a **second** incident of the `REQ-INIT-012` AC-7 kind. Two beats one, as in ADR-0012.
