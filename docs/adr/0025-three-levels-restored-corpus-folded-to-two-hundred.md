# 0025 — Three levels restored, the corpus folded from 644 to ~200, and the lean requirement form

**Status.** Accepted. Supersedes [ADR-0024](0024-architecture-level-promoted-into-system.md)
(the `architecture` level is populated again and `fan-out`'s `system` ceiling returns to
ten, [ADR-0023](0023-fan-out-per-level-ceilings-no-floor.md)'s original value). It does
not revisit [ADR-0019](0019-v-model-left-arm-adopted.md) (the level axis stays optional and
warn-only) or [ADR-0021](0021-corpus-grows-only-by-design.md) (the engine still ships no
shrink verb — this fold was a one-off script run over this corpus, not an engine feature).

**Date.** 2026-09-03.

**Evidence.** The corpus before this record: 644 requirements — 9 `layer: need` and 62
promoted grouping nodes at `level: system`, 573 one-sentence atomic leaves at `level: code`,
561 of them `baseline` with 0 members and 0 tests. `next` listed 572 items in one bucket;
`health` read 11/100; `dupes` at its default threshold reported 714 pairs, most of them
siblings or parent-child pairs that duplicate by construction; three of the five Mermaid
blocks in `_map.md` exceeded the 50,000-character limit GitHub renders. Measured in the
session that produced this record. The owner's stated purpose for the tool: *a reader who
does not understand a piece of AI-written code opens the requirement to understand it.*

## Context

The decomposition of 2026-09-03 (ADR-0021's "grow only" measured on a 691-requirement
corpus) split every parent clause into its own atomic requirement. It made the clause the
unit a test answers to, at the cost of the unit a reader opens: a `REQ-` file said one
sentence and its scenario, and understanding a command meant reading twenty of them. The
same day, ADR-0024 relabelled the 62 grouping nodes to `level: system` so that the
`fan-out` band would fit — a label move that left `level: system` meaning two different
things, distinguished by `layer:`.

The owner asked for the middle: not the 35-clause parents of before, not the one-sentence
leaves of after. Roughly 200 requirements, each readable as one page by a developer new to
the repo, with tests attached at every level.

## Decision

1. **Three levels, each with its own test link.** `SYS-*` (`level: system`, a stakeholder
   need, verified by `validated-against:`) → `ARCH-*` (`level: architecture`, one command
   or one shared engine capability, verified by `tested-by: <id> @integration`) → `REQ-*`
   (`level: code`, one behaviour group with 3–7 labelled cases, each case verified by
   `# verifies: <id>#CASE-N`). `LINT_FANOUT_BANDS["system"]` returns to `(None, 10)`.
2. **Leaves fold into behaviour groups.** The 573 atomic leaves become 126 code-level
   requirements, one per bold clause group of the parent's Description (`**When it
   warns**`, `**What it emits**`, …), merged below three cases and split above seven. Each
   child's clauses are the parent's clauses for that group; its cases are the leaves'
   scenarios. Nothing binding was dropped: a clause that had no leaf stays a clause of its
   group's child.
3. **The parent keeps intent and a table of contents.** An `ARCH-*` Description is its
   intent quote plus one obligation sentence per child, ending in `[[REQ-…]]`. The detail
   lives in exactly one place. The parent's own `## Cases` stay as they were, because the
   test suite already points `# verifies:` tags at them.
4. **One lean form.** Frontmatter without comments or empty keys (`superseded_by:`,
   `priority:` with no value); `## Description` (quote + binding clauses), `## Cases`,
   optional `## Context`. No `## Verify intent` once a requirement is confirmed, no
   `## Links`, no `## Members in code (auto)`. The engine's "legacy schema" warning keys on
   the old `## Input`/`## Output` triad only, no longer on a missing Verify-intent section.
   Audience: a developer new to the repo — file and function names welcome, no glossary
   for programming terms.
5. **Module file per `ARCH-*`.** The parent and its children stay in one file
   ([ARCH-MODULEFILE-056](../../plugin/requirements/ARCH-MODULEFILE-056.md)), so a reader
   opens one file to understand one command. `SYS-*` stay one per file.

## Consequences

- 197 requirements: 9 `SYS`, 62 `ARCH`, 126 `REQ`. Every confirmed `ARCH` contract hashes
  differently (its Description shrank to intent + children), accepted once with
  `sync --accept-drift` as part of this migration.
- The `REQ-` ids minted by the 2026-09-03 decomposition (`REQ-ACVERIFY-233` … `REQ-VLEVEL-815`)
  no longer exist; the folded children carry fresh numbers from 821 upward. Old ids in
  this file's predecessors, `CHANGELOG.md` and code comments are historical references,
  per CLAUDE.md's "translating an old id" rule — tails are still unique corpus-wide.
- A code-level child reaches `confirmed` only once it has an `implements:` member; the
  semantic pass that accompanied the fold placed those tags and the per-case `verifies:`
  tags where a test already existed, and recorded the cases with no test yet.
- `_mermaid_hierarchy`'s ADR-0024 change (root style keyed on "has counted code children",
  not on the `level:` string) stays: it draws the 3-tier corpus correctly and cost nothing.

## Revisit when

- A module file passes ~600 lines or a parent passes ~10 children: the group is a bucket
  again and wants a real `architecture`-level split, not a bigger file.
- A reader coming from `# implements: REQ-…` still has to open the parent to understand the
  child: the child's quote is doing too little, and the form, not the count, is the fix.
- The `verifies:` gap list stops shrinking for a release cycle: the per-case link is then
  ceremony, and ADR-0018's "no marker yet" posture should be re-read before adding more.
