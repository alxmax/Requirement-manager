---
id: ARCH-DECOMPOSE-050
status: confirmed    # draft | baseline | in-progress | implemented | confirmed | deprecated
level: system
layer: feature       # bus | feature | need | aggregate
owner: Alex
priority: could-have
depends_on: [ARCH-ATOMICITY-049, ARCH-LINT-014, ARCH-NEW-004]
satisfies: [SYS-AUTHOR-101]
superseded_by:
---

# Clause decomposition scaffold

## Description
> When `statement-size` reports an over-long clause, the remedy is to split it into its own
> requirement — and that means retyping the clause, inventing an id, and wiring the
> dependency by hand. This does the mechanical half on request. It never runs on its own,
> because `lint` also runs inside the pre-commit hook and CI, where writing a new file
> would break the very commit it was helping.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a reported clause   a Contract clause that `statement-size` named, per
                         [[ARCH-ATOMICITY-049]].
     the parent          the requirement whose Contract holds the reported clause.
     a created draft     the new requirement file this command writes.
     the default run     `lint` invoked without `--decompose`. -->

**When the command writes**
- `lint` writes no file during the default run, whatever `statement-size` or `ac-count-high` reports.
- `lint --decompose` creates one draft requirement for each reported `statement-size` clause.
- The gate, the pre-commit hook and CI never pass `--decompose`, so those runs stay read-only.

**What a created draft holds**
- Each created draft carries `status: draft` and a `depends_on` entry naming its parent.
- The reported clause text is seeded into the created draft's Contract section.
- The created id keeps the parent's area and name, and takes the next free corpus number.

**What the command does not do**
- `lint --decompose` leaves the parent unchanged, so no confirmed contract drifts.
- The command chooses the split by word count, never by obligation, and says so on stdout.
- Each created draft records that its split point was chosen by word count alone.
- `lint --decompose` scaffolds from `statement-size` findings only; an `ac-count-high` finding is reported and nothing is written for it.

**Repeating and undoing**
- Deleting a created draft restores the corpus exactly, because the parent was never edited.
- `lint --decompose` skips a clause whose target file already exists, and reports the skip.

## Verify intent (open questions for the human)
- None — authored from stated intent, not reconstructed from code.

## Cases (= tests)
CASE-1
  Given  a corpus with one clause above the `statement-size` threshold
  When   `lint` runs without `--decompose`
  Then   the finding is reported and the requirements directory holds no new file
CASE-2
  Given  the same corpus
  When   `lint --decompose` runs
  Then   one draft is created, carrying `status: draft` and `depends_on` naming the parent
CASE-3
  Given  the same corpus
  When   `lint --decompose` runs
  Then   the parent file is byte-identical to what it was before the run
CASE-4
  Given  a created draft
  When   its text is read
  Then   it states that the split point was chosen by word count, not by obligation
CASE-5
  Given  a parent `REQ-AUTH-012` in a corpus whose highest number is 049
  When   `lint --decompose` runs
  Then   the created id is `REQ-AUTH-050`
CASE-6
  Given  a corpus where a previous `lint --decompose` already created the target file
  When   `lint --decompose` runs again
  Then   the clause is skipped, the skip is reported, and the existing file is unchanged
CASE-7
  Given  a non-exempt requirement above `LINT_AC_MAX` acceptance criteria
  When   `lint --decompose` runs
  Then   the `ac-count-high` finding is printed and no file is created for it

## Context (non-binding)
**Notes**
- This exists because the author asked for it after the objection below was put to them,
  and reaffirmed it. The objection stands and is recorded here rather than dropped: a word
  count cannot determine that a clause holds two obligations, so a draft created this way
  may split a clause that was atomic all along. That is why every created file is a
  `draft`, carries its provenance in its own text, and is undone by deleting it.
- The `--decompose` flag is opt-in for a mechanical reason, not a stylistic one.
  `.githooks/pre-commit` runs `gate` -> `lint --strict` -> `map --check` in that order.
  A file written during the `lint` step makes the `map --check` step fail in the same hook
  run, because the committed `_map.*` has no node for it — the hook would block the commit
  and blame a stale map it had just caused. In CI the checkout is ephemeral, so the file
  would be written and discarded.
- "When the warning is resolved" is not an observable event. The engine sees a finding as
  present or absent, and absent is indistinguishable from never-fired: an author who
  rewrites the clause shorter without decomposing it clears the finding the same way. So
  creation hangs off an explicit flag rather than off a transition the engine cannot see.
- Ids follow `AREA-NAME-NNN` rather than a derived suffix such as `REQ-AUTH-012-B`. The
  suffix form passes `_ID_PAT`, but `_warn_number_collision` reads `parts[-1]` as the
  number and would compare "B" against real numbers.
- The parent stays untouched on purpose. Rewriting a clause in a `confirmed` requirement
  changes its contract hash, which raises drift and forces `sync --accept-drift` — a large
  consequence for a warn-only finding (ADR-0002).
- Measured reachability, this corpus, 2026-09-03: `statement-size` has never fired here —
  `LINT_STATEMENT_WORDS` is 150 and the longest Contract clause anywhere is 61 words
  (`ARCH-PAGES-021`), so no clause in this corpus is even half the threshold. `ac-count-high`
  is not currently reachable at all: 6 of the 72 non-draft requirements exceed
  `LINT_AC_MAX` (8.3% raw), but all 6 carry `lint_exempt: [ac-count-high]`, so the
  post-exempt count is 0 of 72 (0.0%) today — a deliberate author choice, not a design
  gap. That zero is why `--decompose` covers `statement-size` only: automation over a
  signal with no fire rate and no confirmation sample is what ADR-0022 forbids, and an
  `ac-count-high` triage path was removed before it shipped for exactly that reason.

**Example**
- `lint` tells Ana that clause 3 of `REQ-AUTH-012` runs to 84 words. She runs
  `lint --decompose`, gets `REQ-AUTH-050.md` seeded with that clause and depending on
  `REQ-AUTH-012`, and reads it. Two thirds of it turn out to be one obligation after all,
  so she deletes the file and shortens the clause instead. Nothing else in the corpus
  moved, because the parent was never edited.

**Current implementation**
- `DECOMPOSED_TEMPLATE`, `_next_free_number`, `_already_decomposed` and `_decompose_clause`
  in `reqmap.py`; `cmd_lint` takes `decompose` and `reqs_dir` and writes only when the
  `--decompose` flag is passed. The skip keys off a `<!-- decomposed-from: <parent>#<n> -->`
  marker in the created file, not off the target filename: the id comes from the next free
  number, so a second run picks a fresh name and an existence check never fires. That was a
  real defect — the first implementation created a second file on every re-run, and CASE-6
  caught it.
- There is no `ac-count-high` sibling. One was written (`AC_COUNT_TRIAGE_TEMPLATE`,
  `_decompose_ac_count_high`) and removed before it shipped: it reached nobody, and
  ADR-0022 — adopted in the same change — forbids shipping on a signal with no published
  fire rate and no human-confirmation sample. `OversizeUnify`'s
  `test_no_ac_count_high_decompose_symbols_remain` asserts neither symbol comes back, so
  re-adding one is a deliberate act that has to meet that bar first.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-328
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint writes no file during the default run

> `lint` writes no file during the default run, whatever `statement-size` reports.

Scenario: a default lint run reports the finding but writes no file
  Given  a requirement carrying a clause over the `statement-size` word threshold
  When   `lint` runs without `--decompose`
  Then   stdout names the "statement-size" finding and the requirements directory
         holds no new file

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-329
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint --decompose creates one draft requirement for each

> `lint --decompose` creates one draft requirement for each reported clause.

Scenario: --decompose creates exactly one draft file per reported clause
  Given  a parent with one clause over the `statement-size` threshold
  When   `lint --decompose` runs
  Then   exactly one new file appears in the requirements directory

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-330
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The gate, the pre-commit hook and CI never

> The gate, the pre-commit hook and CI never pass `--decompose`, so those runs stay
> read-only.

Scenario: no invocation site passes --decompose
  Given  `.githooks/pre-commit` and `.github/workflows/ci.yml`
  When   their `lint` invocation lines are read
  Then   neither contains the `--decompose` flag

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-331
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Each created draft carries status: draft and a

> Each created draft carries `status: draft` and a `depends_on` entry naming its parent.

Scenario: the created draft carries status: draft and depends_on the parent
  Given  `lint --decompose` creates a draft from `REQ-AUTH-012`
  When   the created file's frontmatter is read
  Then   it contains `status: draft` and `depends_on: [REQ-AUTH-012]`

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-332
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The reported clause text is seeded into the

> The reported clause text is seeded into the created draft's Contract section.

Scenario: the offending clause's own text appears verbatim in the created draft
  Given  a parent clause of 155 repeated words flagged by `statement-size`
  When   `lint --decompose` creates the draft
  Then   the draft's Contract section contains that exact clause text

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-333
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The created id keeps the parent's area and

> The created id keeps the parent's area and name, and takes the next free corpus number.

Scenario: the created id reuses the parent's area/name with the next free number
  Given  parent `REQ-AUTH-012` in a corpus whose highest existing number is 049
  When   `lint --decompose` runs
  Then   the created file is named `REQ-AUTH-050.md`

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-334
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint --decompose leaves the parent unchanged, so no

> `lint --decompose` leaves the parent unchanged, so no confirmed contract drifts.

Scenario: the parent file is byte-identical after a decompose run
  Given  the parent file's bytes captured before `lint --decompose` runs
  When   the run completes
  Then   the parent file's bytes are unchanged from the captured snapshot, so deleting the
         created draft restores the corpus exactly

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-335
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The command chooses the split by word count

> The command chooses the split by word count, never by obligation, and says so on stdout.

Scenario: stdout discloses the split was by word count, not obligation
  Given  `lint --decompose` running on a flagged clause
  When   the run completes
  Then   stdout includes "word count, not by obligation"

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-336
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Each created draft records that its split point

> Each created draft records that its split point was chosen by word count alone.

Scenario: the created draft's own text discloses the word-count-only split
  Given  a draft created by `lint --decompose`
  When   its file text is read
  Then   it contains "WORD COUNT, never by obligation"

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-338
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint --decompose skips a clause whose target file

> `lint --decompose` skips a clause whose target file already exists, and reports the
> skip.

Scenario: a second decompose run skips the already-decomposed clause and reports it
  Given  a clause already decomposed by a prior `lint --decompose` run
  When   `lint --decompose` runs again
  Then   stdout reports "skipped" and no second file is created for that clause

## Members in code (auto)
