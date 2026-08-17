---
id: REQ-LINTCHECKS-025
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, REQ-LINT-014]
lint_exempt: [ac-count-high]
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
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a normative line  any line inside the Contract or Acceptance section. The section
                       it sits in is what makes it binding.
     a scope unit      what the over-scoped check measures: a clause group when the
                       contract groups its clauses, otherwise a single clause.
     a member          a place in the code tagged as belonging to this requirement. -->

**Readability checks**
- The `long-sentence` check warns on any sentence in the Contract or Acceptance section
  longer than `LINT_SENTENCE_WORDS`, default 25.
- The `statement-too-long` check warns on a Contract bullet over `LINT_CONTRACT_WORDS`,
  default 22, that also spans more than one sentence.
- The `stacked-conditions` check warns on a normative line that joins at least
  `LINT_STACKED_CONNECTORS` clauses, default 3, with conjunctions.
- `stacked-conditions` reads every normative line. It does not require a `shall` or `must` on
  the line, because the section already makes the line binding and the authoring voice writes
  no modal.

**Named-subject check**
- The `anonymous-subject` check warns on a Contract clause opening with a bare "It"
  followed by a verb.
- `anonymous-subject` reads the Contract only. Acceptance prose may say "it" in a Then clause
  and still read clearly.

**Scope checks**
- The `ac-count-low` check warns on an Acceptance section holding fewer than
  `LINT_AC_MIN`, default 3, criteria.
- The `ac-count-high` check warns on more than `LINT_AC_MAX`, default 7, criteria,
  counted as `- ` bullets or `AC-N` labelled blocks.
- The `over-scoped` check warns on a requirement over both ceilings at once: more than
  `LINT_CONTRACT_MAX` scope units, default 10, with more than `LINT_AC_MAX` criteria.
- `over-scoped` counts clause groups when the Contract carries bold group labels, and counts
  clauses when it does not. Writing one obligation per bullet multiplies clauses without
  widening scope, so counting clauses alone would punish the authoring voice.
- The `file-spread` check warns on a requirement whose `implements` members span at least
  `LINT_FILE_SPREAD_MAX`, default 3, distinct files.
- `file-spread` is an architectural-diffuseness signal and is skipped when no member data is
  supplied.

**Vague-term check**
- The `vague-term` check warns on a Contract bullet using a word from the closed
  `LINT_VAGUE_TERMS` set — untestable quality words such as `appropriate`.
- Backticked code spans are stripped before the `vague-term` scan runs.
- `vague-term` emits one finding per distinct term.

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
- `anonymous-subject` reads physical lines, not folded clauses. A wrapped bullet whose
  continuation line happens to begin with "It " is flagged as though that line opened a
  clause. Rewriting the sentence is the fix; the alternative — folding continuations first —
  would make every other prose check measure a different unit than the one it measures now.
- `ac-count-high` is exempted here because this requirement is a table of checks: each of
  the nine criteria pins exactly one check's behaviour. Merging them to reach the ceiling
  would leave checks tested only implicitly, which is the outcome the count exists to
  prevent. Same reasoning as [[REQ-CHECK-006]]'s severity table.

## HOW — Acceptance (= tests)
AC-1
  Given  a confirmed requirement with a 40-word sentence in its Contract section
  When   `lint` runs
  Then   it reports a `long-sentence` warning naming the word count

AC-2
  Given  a normative line joining four clauses with conjunctions, carrying no modal verb
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
  Given  a requirement over both ceilings (more than ten contract scope units and more
         than seven acceptance criteria)
  When   `lint` runs
  Then   it reports `over-scoped`; over only one ceiling, none

AC-6
  Given  a Contract holding thirty clauses under three bold group labels, plus eight
         acceptance criteria
  When   `lint` runs
  Then   it reports no `over-scoped`, because three groups is under the ceiling; the same
         thirty clauses ungrouped do report it

AC-7
  Given  a requirement whose `implements` members span three or more distinct files
  When   `lint` runs with member data
  Then   it reports `file-spread`; a single file or no member data produce none

AC-8
  Given  a Contract bullet containing "appropriate" and "user-friendly"
  When   `lint` runs
  Then   it reports two `vague-term` warnings; a backticked span and a precise bullet report none

AC-9
  Given  a Contract bullet reading "It creates the folder."
  When   `lint` runs
  Then   it reports an `anonymous-subject` warning; "`init` creates the folder." reports
         none, and the same bare "It" in an Acceptance criterion reports none

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
