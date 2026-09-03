---
id: ARCH-LINTCHECKS-025
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-LINT-014]
lint_exempt: [ac-count-high]
satisfies: [SYS-QUALITY-104]
superseded_by:
milestone: v1.14
---

# Readability & scope checks

## Description
> The linter's rulebook: the individual checks that catch hard-to-read or overloaded
> requirement prose — sentences that run long, lines that stack conditions, bloated or
> skimpy acceptance lists, contracts that bundle several capabilities, vague quality
> words, and code spread across too many files. The framework that runs them, scopes
> them and decides exit codes is [[ARCH-LINT-014]]; this is what each check flags.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a normative line  any line inside the Contract or Acceptance section. The section
                       it sits in is what makes it binding.
     a scope unit      what the over-scoped check measures: a clause group when the
                       contract groups its clauses, otherwise a single clause.
     a member          a place in the code tagged as belonging to this requirement. -->

**Readability checks**
- The `statement-too-long` check warns on a Contract bullet spanning more than
  `LINT_CLAUSE_SENTENCES` sentences, default 3.
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

**Layer check**
- The `layer-mismatch` check warns on a `layer: bus` requirement that nothing depends on and
  that itself depends on at least `LINT_BUS_FANOUT_MIN`, default 3, requirements.
- `layer-mismatch` is skipped when no fan-in data is supplied.

**Vague-term check**
- The `vague-term` check warns on a Contract bullet using a word from the closed
  `LINT_VAGUE_TERMS` set — untestable quality words such as `appropriate`.
- Backticked code spans are stripped before the `vague-term` scan runs.
- `vague-term` emits one finding per distinct term.

**Redundant-modal check**
- The `redundant-modal` check warns on a Contract bullet using `shall` or `must` —
  the closed `LINT_MODAL_WORDS` set.
- Backticked code spans are stripped before the `redundant-modal` scan runs, same as
  `vague-term`.
- `redundant-modal` emits one finding per distinct term.

## Verify intent (open questions for the human)
- None — split out of [[ARCH-LINT-014]] with intent carried over unchanged.

## Notes & known limitations (informative)
- `statement-too-long` counts sentences and nothing else; words per clause belong to
  `statement-size`, so neither check reports the same clause for the same reason. It used
  to count words as well, which flagged a correct two-sentence clause.
- A per-SENTENCE word ceiling was removed on 2026-09-03. `long-sentence` had warned on any
  sentence over 25 words since the `lint` command shipped (2026-06-07), and it was the only
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

## Cases (= tests)
CASE-1
  Given  a confirmed requirement whose Contract bullet uses the word "appropriate"
  When   `lint` runs
  Then   it reports a `vague-term` warning naming that term

CASE-2
  Given  a normative line joining four clauses with conjunctions, carrying no modal verb
  When   `lint` runs
  Then   it reports a `stacked-conditions` warning

CASE-3
  Given  a Contract bullet spanning four sentences
  When   `lint` runs
  Then   it reports `statement-too-long`; the same bullet cut to three sentences reports
         none, and a single 40-word sentence reports nothing, however long it runs

CASE-4
  Given  an Acceptance section with one criterion
  When   `lint` runs
  Then   it reports `ac-count-low`; with eight criteria, `ac-count-high`; with four, neither

CASE-5
  Given  a requirement over both ceilings (more than ten contract scope units and more
         than seven acceptance criteria)
  When   `lint` runs
  Then   it reports `over-scoped`; over only one ceiling, none

CASE-6
  Given  a Contract holding thirty clauses under three bold group labels, plus eight
         acceptance criteria
  When   `lint` runs
  Then   it reports no `over-scoped`, because three groups is under the ceiling; the same
         thirty clauses ungrouped do report it

CASE-7
  Given  a requirement whose `implements` members span three or more distinct files
  When   `lint` runs with member data
  Then   it reports `file-spread`; a single file or no member data produce none

CASE-8
  Given  a Contract bullet containing "appropriate" and "user-friendly"
  When   `lint` runs
  Then   it reports two `vague-term` warnings; a backticked span and a precise bullet report none

CASE-9
  Given  a Contract bullet reading "It creates the folder."
  When   `lint` runs
  Then   it reports an `anonymous-subject` warning; "`init` creates the folder." reports
         none, and the same bare "It" in an Acceptance criterion reports none

CASE-10
  Given  a Contract bullet reading "The system shall log the event and must retry once."
  When   `lint` runs
  Then   it reports two `redundant-modal` warnings ("shall" + "must"); a backticked
         `shall_retry` identifier and a plain present-tense bullet report none

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `reqmap.py lint` after an editing session. One bullet is flagged
  `statement-too-long` (four sentences), another `vague-term` for "robust". She rewrites
  both; the next run is quiet.

## WHERE — Current implementation
- The check bodies live in `lint_requirement` (per-requirement checks) and `_lint_prose`
  (per-section prose walk) in `reqmap.py`; `_sentences` splits lines for the word and
  sentence counts.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-457
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The statement-too-long check warns on a Contract bullet

> The `statement-too-long` check warns on a Contract bullet spanning more than
> `LINT_CLAUSE_SENTENCES` sentences, default 3.

Scenario: statement-too-long fires past the sentence ceiling
  Given  a Contract bullet spanning four sentences, one more than `LINT_CLAUSE_SENTENCES`
  When   `lint` runs
  Then   it reports a `statement-too-long` warning naming that bullet

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-458
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The stacked-conditions check warns on a normative line

> The `stacked-conditions` check warns on a normative line that joins at least
> `LINT_STACKED_CONNECTORS` clauses, default 3, with conjunctions.

Scenario: stacked-conditions fires at the connector ceiling
  Given  a normative line joining three clauses with conjunctions, meeting `LINT_STACKED_CONNECTORS`
  When   `lint` runs
  Then   it reports a `stacked-conditions` warning naming that line

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-459
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Stacked-conditions reads every normative line. It does not

> `stacked-conditions` reads every normative line. It does not require a `shall` or `must`
> on the line, because the section already makes the line binding and the authoring voice
> writes no modal.

Scenario: stacked-conditions fires on Acceptance text too, with no modal verb
  Given  an Acceptance criterion joining three clauses with conjunctions and no `shall`/`must`
  When   `lint` runs
  Then   it reports `stacked-conditions`, because any normative line counts, modal or not

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-460
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The anonymous-subject check warns on a Contract clause

> The `anonymous-subject` check warns on a Contract clause opening with a bare "It"
> followed by a verb.

Scenario: anonymous-subject fires on a bare "It" opener
  Given  a Contract clause reading "It logs the event."
  When   `lint` runs
  Then   it reports an `anonymous-subject` warning naming that clause

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-461
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Anonymous-subject reads the Contract only. Acceptance prose may

> `anonymous-subject` reads the Contract only. Acceptance prose may say "it" in a Then
> clause and still read clearly.

Scenario: anonymous-subject ignores Acceptance prose
  Given  an Acceptance Then clause reading "it exits non-zero"
  When   `lint` runs
  Then   it reports no `anonymous-subject` warning for that line

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-462
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The ac-count-low check warns on an Acceptance section

> The `ac-count-low` check warns on an Acceptance section holding fewer than
> `LINT_AC_MIN`, default 3, criteria.

Scenario: ac-count-low fires under the minimum
  Given  an Acceptance section holding two criteria, one under `LINT_AC_MIN`
  When   `lint` runs
  Then   it reports an `ac-count-low` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-463
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The ac-count-high check warns on more than LINT_AC_MAX

> The `ac-count-high` check warns on more than `LINT_AC_MAX`, default 7, criteria, counted
> as `- ` bullets or `AC-N` labelled blocks.

Scenario: ac-count-high fires over the maximum, either counting style
  Given  an Acceptance section holding eight `AC-N` blocks, one over `LINT_AC_MAX`
  When   `lint` runs
  Then   it reports `ac-count-high`; eight `- ` bullets trigger the same warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-464
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The over-scoped check warns on a requirement over

> The `over-scoped` check warns on a requirement over both ceilings at once: more than
> `LINT_CONTRACT_MAX` scope units, default 10, with more than `LINT_AC_MAX` criteria.

Scenario: over-scoped fires only when both ceilings are crossed
  Given  a Contract with eleven scope units and an Acceptance section with eight criteria
  When   `lint` runs
  Then   it reports `over-scoped`; crossing only one ceiling reports none

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-465
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Over-scoped counts clause groups when the Contract carries

> `over-scoped` counts clause groups when the Contract carries bold group labels, and
> counts clauses when it does not. Writing one obligation per bullet multiplies clauses
> without widening scope, so counting clauses alone would punish the authoring voice.

Scenario: over-scoped counts bold groups, not raw clauses
  Given  a Contract holding thirty clauses under three bold group labels
  When   `lint` runs
  Then   it reports no `over-scoped`, because the scope-unit count is three groups, not thirty

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-466
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The file-spread check warns on a requirement whose

> The `file-spread` check warns on a requirement whose `implements` members span at least
> `LINT_FILE_SPREAD_MAX`, default 3, distinct files.

Scenario: file-spread fires at the distinct-file ceiling
  Given  a requirement whose `implements:` members name three distinct files
  When   `lint` runs with member data
  Then   it reports a `file-spread` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-467
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# File-spread is an architectural-diffuseness signal and is skipped

> `file-spread` is an architectural-diffuseness signal and is skipped when no member data
> is supplied.

Scenario: file-spread is silent without member data
  Given  a requirement whose members span three files, but `lint` runs with no member data
  When   `lint` runs
  Then   it reports no `file-spread` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-468
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The layer-mismatch check warns on a layer: bus

> The `layer-mismatch` check warns on a `layer: bus` requirement that nothing depends on
> and that itself depends on at least `LINT_BUS_FANOUT_MIN`, default 3, requirements.

Scenario: layer-mismatch fires on a fan-out bus with no dependents
  Given  a `layer: bus` requirement nothing depends on, itself depending on three others
  When   `lint` runs with fan-in data
  Then   it reports a `layer-mismatch` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-469
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Layer-mismatch is skipped when no fan-in data is

> `layer-mismatch` is skipped when no fan-in data is supplied.

Scenario: layer-mismatch is silent without fan-in data
  Given  the same fan-out bus requirement, but `lint` runs with no fan-in data supplied
  When   `lint` runs
  Then   it reports no `layer-mismatch` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-470
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The vague-term check warns on a Contract bullet

> The `vague-term` check warns on a Contract bullet using a word from the closed
> `LINT_VAGUE_TERMS` set — untestable quality words such as `appropriate`.

Scenario: vague-term fires on a closed-set word
  Given  a Contract bullet reading "logs an appropriate message"
  When   `lint` runs
  Then   it reports a `vague-term` warning naming "appropriate"

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-471
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Backticked code spans are stripped before the vague-term

> Backticked code spans are stripped before the `vague-term` scan runs.

Scenario: vague-term ignores a backticked span
  Given  a Contract bullet containing only the backticked identifier `` `appropriate_flag` ``
  When   `lint` runs
  Then   it reports no `vague-term` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-472
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Vague-term emits one finding per distinct term

> `vague-term` emits one finding per distinct term.

Scenario: vague-term reports each distinct term once
  Given  a Contract bullet using "appropriate" twice and "user-friendly" once
  When   `lint` runs
  Then   it reports two `vague-term` findings, one per distinct term

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-473
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# The redundant-modal check warns on a Contract bullet

> The `redundant-modal` check warns on a Contract bullet using `shall` or `must` — the
> closed `LINT_MODAL_WORDS` set.

Scenario: redundant-modal fires on shall or must
  Given  a Contract bullet reading "The system shall retry once."
  When   `lint` runs
  Then   it reports a `redundant-modal` warning naming "shall"

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-474
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Backticked code spans are stripped before the redundant-modal

> Backticked code spans are stripped before the `redundant-modal` scan runs, same as
> `vague-term`.

Scenario: redundant-modal ignores a backticked span
  Given  a Contract bullet containing only the backticked identifier `` `shall_retry` ``
  When   `lint` runs
  Then   it reports no `redundant-modal` warning

## Members in code (auto)




--------------------


---
id: REQ-LINTCHECKS-475
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-LINTCHECKS-025]
superseded_by:
---

# Redundant-modal emits one finding per distinct term

> `redundant-modal` emits one finding per distinct term.

Scenario: redundant-modal reports each distinct term once
  Given  a Contract bullet reading "The system shall log the event and must retry once."
  When   `lint` runs
  Then   it reports two `redundant-modal` findings, one for "shall" and one for "must"

## Members in code (auto)
