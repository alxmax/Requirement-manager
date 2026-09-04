---
id: ARCH-LINTCHECKS-025
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.14
depends_on: [ARCH-PARSE-001, ARCH-LINT-014]
satisfies: [SYS-QUALITY-104]
lint_exempt: [ac-count-high]
---

# Readability & scope checks

## Description
> The linter's rulebook: the individual checks that catch hard-to-read or overloaded
> requirement prose — sentences that run long, lines that stack conditions, bloated or
> skimpy acceptance lists, contracts that bundle several capabilities, vague quality
> words, code spread across too many files, and an atomic-form leaf that lists more
> facts than its Scenario proves. The framework that runs them, scopes them and
> decides exit codes is [[ARCH-LINT-014]]; this is what each check flags.

Every bullet below is binding.
- `statement-too-long` and `stacked-conditions` warn on a normative line that runs too long or stacks too many conditions; `anonymous-subject` warns on a Contract clause opening with a bare "It". [[REQ-LINTCHECKS-865]] details the behaviour.
- `ac-count-low`/`ac-count-high`/`over-scoped` warn on too few or too many acceptance criteria or contract scope units; `file-spread` warns on an implementation scattered across too many files. [[REQ-LINTCHECKS-866]] details the behaviour.
- `atomic-bullet-then-mismatch` and `atomic-story-overlong` warn on an atomic-form story quote whose fact count disagrees with its Scenario; `layer-mismatch` warns on a fan-out `bus` requirement nothing depends on. [[REQ-LINTCHECKS-867]] details the behaviour.
- `vague-term` warns on a Contract bullet using an untestable quality word from the closed `LINT_VAGUE_TERMS` set. [[REQ-LINTCHECKS-868]] details the behaviour.
- `redundant-modal` warns on a Contract bullet using `shall` or `must` — the closed `LINT_MODAL_WORDS` set. [[REQ-LINTCHECKS-869]] details the behaviour.

## Cases
CASE-1
  Given  a confirmed requirement whose Contract bullet uses the word "appropriate"
  When   `gate` runs
  Then   it reports a `vague-term` warning naming that term

CASE-2
  Given  a normative line joining four clauses with conjunctions, carrying no modal verb
  When   `gate` runs
  Then   it reports a `stacked-conditions` warning

CASE-3
  Given  a Contract bullet spanning four sentences
  When   `gate` runs
  Then   it reports `statement-too-long`; the same bullet cut to three sentences reports
         none, and a single 40-word sentence reports nothing, however long it runs

CASE-4
  Given  an Acceptance section with one criterion
  When   `gate` runs
  Then   it reports `ac-count-low`; with eight criteria, `ac-count-high`; with four, neither

CASE-5
  Given  a requirement over both ceilings (more than ten contract scope units and more
         than seven acceptance criteria)
  When   `gate` runs
  Then   it reports `over-scoped`; over only one ceiling, none

CASE-6
  Given  a Contract holding thirty clauses under three bold group labels, plus eight
         acceptance criteria
  When   `gate` runs
  Then   it reports no `over-scoped`, because three groups is under the ceiling; the same
         thirty clauses ungrouped do report it

CASE-7
  Given  a requirement whose `implements` members span three or more distinct files
  When   `gate` runs with member data
  Then   it reports `file-spread`; a single file or no member data produce none

CASE-8
  Given  a Contract bullet containing "appropriate" and "user-friendly"
  When   `gate` runs
  Then   it reports two `vague-term` warnings; a backticked span and a precise bullet report none

CASE-9
  Given  a Contract bullet reading "It creates the folder."
  When   `gate` runs
  Then   it reports an `anonymous-subject` warning; "`init` creates the folder." reports
         none, and the same bare "It" in an Acceptance criterion reports none

CASE-10
  Given  a Contract bullet reading "The system shall log the event and must retry once."
  When   `gate` runs
  Then   it reports two `redundant-modal` warnings ("shall" + "must"); a backticked
         `shall_retry` identifier and a plain present-tense bullet report none

CASE-11
  Given  an atomic-form story quote listing 3 `- ` facts and a Scenario with 1 `Then` line
  When   `gate` runs
  Then   it reports an `atomic-bullet-then-mismatch` warning, promoted to error under
         `--strict`; the same story with 3 matching `Then` lines reports none

CASE-12
  Given  an atomic-form story quote listing 4 `- ` facts, one over `LINT_ATOMIC_STORY_BULLETS_MAX`
  When   `gate` runs
  Then   it reports `atomic-story-overlong`, not `atomic-bullet-then-mismatch`, regardless of
         how many `Then` lines the Scenario carries

## Context
**Terms**
- a normative line  any line inside the Contract or Acceptance section. The section
- it sits in is what makes it binding.
- a scope unit      what the over-scoped check measures: a clause group when the
- contract groups its clauses, otherwise a single clause.
- a member          a place in the code tagged as belonging to this requirement.

**Notes**
- `statement-too-long` counts sentences and nothing else; words per clause belong to
  `statement-size`, so neither check reports the same clause for the same reason. It used
  to count words as well, which flagged a correct two-sentence clause.
- A per-SENTENCE word ceiling was removed on 2026-09-03. `long-sentence` had warned on any
  sentence over 25 words since the `gate` command shipped (2026-06-07), and it was the only
  check that bounded how long one sentence may run. Nothing replaces it: a clause may now
  hold three sentences of fifty words each and pass. What remains is the sentence count here
  and the 150-word clause ceiling in `statement-size` — both per clause, neither per
  sentence. This is a loosening, recorded so it reads as a decision rather than an
  oversight.
- `file-spread` measures where the code lives; `over-scoped` measures contract/acceptance
  scope — different axes, so one firing says nothing about the other.
- Sentence splitting is a deterministic split on `.`, `!`, and `?` — crude, so an
  abbreviation or a trailing code span reads as a sentence boundary. It feeds a word count
  and a sentence count, so the worst case is one extra sentence counted in a clause.
- The thresholds are module constants, not configurable from the command line.
- `anonymous-subject` reads physical lines, not folded clauses. A wrapped bullet whose
  continuation line happens to begin with "It " is flagged as though that line opened a
  clause. Rewriting the sentence is the fix; the alternative — folding continuations first —
  would make every other prose check measure a different unit than the one it measures now.
- `ac-count-high` is exempted here because this requirement is a table of checks: each of
  the nine criteria pins exactly one check's behaviour. Merging them to reach the ceiling
  would leave checks tested only implicitly, which is the outcome the count exists to
  prevent. Same reasoning as [[ARCH-CHECK-006]]'s severity table.
- `atomic-bullet-then-mismatch`/`atomic-story-overlong` fire on 0 of the corpus's atomic-form
  requirements at launch — no existing body enumerates more than one `- ` fact in its story
  quote. [ADR-0022](../../docs/adr/0022-no-minimum-requirement-size-check.md)'s launch
  discipline (a published fire rate AND a human-confirmed sample) is satisfied only on the
  fire-rate half here; there is no live finding to sample. This is an explicit, acknowledged
  gap, not a silent one: the check is deterministic and structural (a bullet either has a
  matching `Then` or it does not — no size judgement is made), the same class as
  `missing-section`, not a heuristic threshold like the rejected minimum-size proposal — and
  `warn`+`STRICT_PROMOTE` (not unconditional error) was chosen specifically so a plain `gate`
  run stays exactly as quiet as it was before this check existed.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py lint` after an editing session. One bullet is flagged
  `statement-too-long` (four sentences), another `vague-term` for "robust". She rewrites
  both; the next run is quiet.

**Current implementation**
- The check bodies live in `lint_requirement` (per-requirement checks) and `_lint_prose`
  (per-section prose walk) in `reqmap.py`; `_sentences` splits lines for the word and
  sentence counts.


--------------------


---
id: REQ-LINTCHECKS-865
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
---

# Readability checks: length, stacking, anonymous subjects

## Description
> A requirement is only useful if a reader can hold its obligation in their head. These
> checks catch the three ways prose defeats that: a bullet that runs on past a sentence
> ceiling, a line that stacks several conditions with conjunctions, and a clause that
> opens with a bare "It" instead of naming what does the thing.

Every bullet below is binding.
- The `statement-too-long` check warns on a Contract bullet spanning more than
  `LINT_CLAUSE_SENTENCES` sentences, default 3.
- The `stacked-conditions` check warns on a normative line that joins at least
  `LINT_STACKED_CONNECTORS` clauses, default 3, with conjunctions.
- `stacked-conditions` reads every normative line. It does not require a `shall` or `must` on
  the line, because the section already makes the line binding and the authoring voice writes
  no modal.
- The `anonymous-subject` check warns on a Contract clause opening with a bare "It"
  followed by a verb.
- `anonymous-subject` reads the Contract only. Acceptance prose may say "it" in a Then clause
  and still read clearly.

## Cases
CASE-1 — statement-too-long fires past the sentence ceiling
  Given  a Contract bullet spanning four sentences, one more than `LINT_CLAUSE_SENTENCES`
  When   `gate` runs
  Then   it reports a `statement-too-long` warning naming that bullet

CASE-2 — stacked-conditions fires at the connector ceiling
  Given  a normative line joining three clauses with conjunctions, meeting `LINT_STACKED_CONNECTORS`
  When   `gate` runs
  Then   it reports a `stacked-conditions` warning naming that line

CASE-3 — stacked-conditions fires on Acceptance text too, with no modal verb
  Given  an Acceptance criterion joining three clauses with conjunctions and no `shall`/`must`
  When   `gate` runs
  Then   it reports `stacked-conditions`, because any normative line counts, modal or not

CASE-4 — anonymous-subject fires on a bare "It" opener
  Given  a Contract clause reading "It logs the event."
  When   `gate` runs
  Then   it reports an `anonymous-subject` warning naming that clause

CASE-5 — anonymous-subject ignores Acceptance prose
  Given  an Acceptance Then clause reading "it exits non-zero"
  When   `gate` runs
  Then   it reports no `anonymous-subject` warning for that line


--------------------


---
id: REQ-LINTCHECKS-866
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
---

# Scope checks: acceptance count, over-scoping, file spread

## Description
> A requirement can be under-specified (too few criteria to trust) or a grab-bag (too many
> obligations, or code scattered too widely to be one thing). These checks bound both
> ends: acceptance-count ceilings and floors, a combined contract+acceptance over-scoped
> signal, and a file-spread signal for implementations diffused across too many files.

Every bullet below is binding.
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

## Cases
CASE-1 — ac-count-low fires under the minimum
  Given  an Acceptance section holding two criteria, one under `LINT_AC_MIN`
  When   `gate` runs
  Then   it reports an `ac-count-low` warning

CASE-2 — ac-count-high fires over the maximum, either counting style
  Given  an Acceptance section holding eight `AC-N` blocks, one over `LINT_AC_MAX`
  When   `gate` runs
  Then   it reports `ac-count-high`; eight `- ` bullets trigger the same warning

CASE-3 — over-scoped fires only when both ceilings are crossed
  Given  a Contract with eleven scope units and an Acceptance section with eight criteria
  When   `gate` runs
  Then   it reports `over-scoped`; crossing only one ceiling reports none

CASE-4 — over-scoped counts bold groups, not raw clauses
  Given  a Contract holding thirty clauses under three bold group labels
  When   `gate` runs
  Then   it reports no `over-scoped`, because the scope-unit count is three groups, not thirty

CASE-5 — file-spread fires at the distinct-file ceiling
  Given  a requirement whose `implements:` members name three distinct files
  When   `gate` runs with member data
  Then   it reports a `file-spread` warning

CASE-6 — file-spread is silent without member data
  Given  a requirement whose members span three files, but `gate` runs with no member data
  When   `gate` runs
  Then   it reports no `file-spread` warning


--------------------


---
id: REQ-LINTCHECKS-867
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
---

# Atomic-form parity and layer-mismatch checks

## Description
> An atomic-form story quote is a promise that its facts and its Scenario's `Then` lines
> agree, and a `bus` requirement is a promise that something actually depends on it.
> These checks catch both promises breaking: a story that lists more facts than its
> Scenario proves (or simply lists too many), and a `bus`-layer requirement with fan-out
> but no fan-in.

Every bullet below is binding.
- The `atomic-bullet-then-mismatch` check warns on an atomic-form story quote that lists more
  than one `- ` fact when the count of `Then` lines in the Scenario does not equal the bullet
  count.
- The `atomic-story-overlong` check warns on an atomic-form story quote listing more than
  `LINT_ATOMIC_STORY_BULLETS_MAX`, default 3, `- ` facts — beyond that it is no longer one
  obligation.
- Both checks are promoted to error under `lint --strict`, the same mechanism as
  `ac-count-high` and `over-scoped`.
- The `layer-mismatch` check warns on a `layer: bus` requirement that nothing depends on and
  that itself depends on at least `LINT_BUS_FANOUT_MIN`, default 3, requirements.
- `layer-mismatch` is skipped when no fan-in data is supplied.

## Cases
CASE-1 — atomic-bullet-then-mismatch fires when bullets and Then lines disagree
  Given  an atomic-form story quote listing 3 `- ` facts and a Scenario with 1 `Then` line
  When   `gate` runs
  Then   it reports an `atomic-bullet-then-mismatch` warning; the same story with 3 matching
         `Then` lines reports none

CASE-2 — atomic-story-overlong fires over the ceiling regardless of Then count
  Given  an atomic-form story quote listing 4 `- ` facts, one over the ceiling
  When   `gate` runs
  Then   it reports `atomic-story-overlong`, not `atomic-bullet-then-mismatch`, even when
         the Scenario carries 4 matching `Then` lines

CASE-3 — layer-mismatch fires on a fan-out bus with no dependents
  Given  a `layer: bus` requirement nothing depends on, itself depending on three others
  When   `gate` runs with fan-in data
  Then   it reports a `layer-mismatch` warning

CASE-4 — layer-mismatch is silent without fan-in data
  Given  the same fan-out bus requirement, but `gate` runs with no fan-in data supplied
  When   `gate` runs
  Then   it reports no `layer-mismatch` warning


--------------------


---
id: REQ-LINTCHECKS-868
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
---

# The vague-term check

## Description
> "Appropriate", "robust", "user-friendly" — words that sound like a requirement but
> commit to nothing testable. `vague-term` flags any Contract bullet using one from a
> closed word list, so a reviewer catches the sentence that reads fine and means
> nothing before it ships as a contract.

Every bullet below is binding.
- The `vague-term` check warns on a Contract bullet using a word from the closed
  `LINT_VAGUE_TERMS` set — untestable quality words such as `appropriate`.
- Backticked code spans are stripped before the `vague-term` scan runs.
- `vague-term` emits one finding per distinct term.

## Cases
CASE-1 — vague-term fires on a closed-set word
  Given  a Contract bullet reading "logs an appropriate message"
  When   `gate` runs
  Then   it reports a `vague-term` warning naming "appropriate"

CASE-2 — vague-term ignores a backticked span
  Given  a Contract bullet containing only the backticked identifier `` `appropriate_flag` ``
  When   `gate` runs
  Then   it reports no `vague-term` warning

CASE-3 — vague-term reports each distinct term once
  Given  a Contract bullet using "appropriate" twice and "user-friendly" once
  When   `gate` runs
  Then   it reports two `vague-term` findings, one per distinct term


--------------------


---
id: REQ-LINTCHECKS-869
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
---

# The redundant-modal check

## Description
> A Contract section is binding by construction — the heading already says so — so
> "shall" and "must" inside it add nothing but legalese. `redundant-modal` flags either
> word so a bullet reads as a plain, present-tense statement of fact instead of a
> contract clause pretending to be a legal document.

Every bullet below is binding.
- The `redundant-modal` check warns on a Contract bullet using `shall` or `must` —
  the closed `LINT_MODAL_WORDS` set.
- Backticked code spans are stripped before the `redundant-modal` scan runs, same as
  `vague-term`.
- `redundant-modal` emits one finding per distinct term.

## Cases
CASE-1 — redundant-modal fires on shall or must
  Given  a Contract bullet reading "The system shall retry once."
  When   `gate` runs
  Then   it reports a `redundant-modal` warning naming "shall"

CASE-2 — redundant-modal ignores a backticked span
  Given  a Contract bullet containing only the backticked identifier `` `shall_retry` ``
  When   `gate` runs
  Then   it reports no `redundant-modal` warning

CASE-3 — redundant-modal reports each distinct term once
  Given  a Contract bullet reading "The system shall log the event and must retry once."
  When   `gate` runs
  Then   it reports two `redundant-modal` findings, one for "shall" and one for "must"

