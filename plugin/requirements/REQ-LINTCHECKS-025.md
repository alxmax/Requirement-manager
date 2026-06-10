---
id: REQ-LINTCHECKS-025
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, REQ-LINT-014]
superseded_by:
milestone: v1.14
---

# Readability & scope checks

> The linter's rulebook: the individual checks that catch hard-to-read or overloaded
> requirement prose — sentences that run long, lines that stack conditions, bloated or
> skimpy acceptance lists, contracts that bundle several capabilities, vague quality
> words, and code spread across too many files. The framework that runs them, scopes
> them and decides exit codes is [[REQ-LINT-014]]; this is what each check flags.

## WHAT — Contract (normative)
- The `long-sentence` check (warn) shall flag any sentence in the Contract or Acceptance
  section longer than the word threshold (`LINT_SENTENCE_WORDS`, default 35).
- The `stacked-conditions` check (warn) shall flag a normative line that piles up too many
  clauses joined by conjunctions (`LINT_STACKED_CONNECTORS`, default 3 conjunctions).
- The `statement-too-long` check (warn) shall flag a Contract bullet that exceeds
  `LINT_CONTRACT_WORDS` (default 30) words and spans more than one sentence.
- The `ac-count-low` check (warn) shall flag an Acceptance section holding one or two
  criteria (fewer than `LINT_AC_MIN`, default 3); `ac-count-high` shall flag more than
  `LINT_AC_MAX` (default 7), counted as `- ` bullets or `AC-N` labelled blocks.
- The `over-scoped` check (warn) shall flag a requirement whose Contract exceeds
  `LINT_CONTRACT_MAX` (default 10) clauses AND whose Acceptance exceeds `LINT_AC_MAX` —
  a composite signal that several capabilities are bundled into one.
- The `file-spread` check (warn) shall flag a requirement whose `implements` members span
  at least `LINT_FILE_SPREAD_MAX` (default 3) distinct files; it is an
  architectural-diffuseness signal and is skipped when no member data is supplied.
- The `vague-term` check (warn) shall flag a Contract bullet using a word from the closed
  `LINT_VAGUE_TERMS` set — untestable quality words like `appropriate` or `robust`.
- Before the `vague-term` scan, backticked code spans are stripped, and one finding is
  emitted per distinct term.

## WHAT — Verify intent (open questions for the human)
- None — split out of [[REQ-LINT-014]] with intent carried over unchanged.

## WHAT — Notes & known limitations (informative)
- `statement-too-long` deliberately ignores a single over-long sentence (that is
  `long-sentence`'s job), so the two checks never flag the same line twice.
- `file-spread` measures where the code lives; `over-scoped` measures contract/acceptance
  scope — different axes, so one firing says nothing about the other.
- Sentence splitting is a deterministic split on `.`, `!`, and `?` — crude, but it only
  feeds a word count, so the worst case is a missed long sentence, not a false alarm.
- The thresholds are module constants, not configurable from the command line.

## HOW — Acceptance (= tests)
AC-1
  Given  a confirmed requirement with a 40-word sentence in its Contract section
  When   `lint` runs
  Then   it reports a `long-sentence` warning naming the word count

AC-2
  Given  a confirmed requirement with a normative line that joins four clauses with "and"
  When   `lint` runs
  Then   it reports a `stacked-conditions` warning

AC-3
  Given  a Contract bullet over 30 words spanning two sentences
  When   `lint` runs
  Then   it reports `statement-too-long`; a single 40-word sentence reports only `long-sentence`

AC-4
  Given  an Acceptance section with one criterion
  When   `lint` runs
  Then   it reports `ac-count-low`; with eight criteria, `ac-count-high`; with four, neither

AC-5
  Given  a requirement over both ceilings (more than ten contract clauses and more than seven acceptance criteria)
  When   `lint` runs
  Then   it reports `over-scoped`; over only one ceiling, none

AC-6
  Given  a requirement whose `implements` members span three or more distinct files
  When   `lint` runs with member data
  Then   it reports `file-spread`; a single file or no member data produce none

AC-7
  Given  a Contract bullet containing "appropriate" and "user-friendly"
  When   `lint` runs
  Then   it reports two `vague-term` warnings; a backticked span and a precise bullet report none

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py lint` after an editing session. One bullet is flagged `long-sentence`
  (44 words), another `vague-term` for "robust". She rewrites both; the next run is quiet.

## WHERE — Current implementation
- The check bodies live in `lint_requirement` (per-requirement checks) and `_lint_prose`
  (per-section prose walk) in `reqmap.py`; `_sentences` splits lines for the word counts.

## Links
- Used by: (auto)
## Members in code (auto)
