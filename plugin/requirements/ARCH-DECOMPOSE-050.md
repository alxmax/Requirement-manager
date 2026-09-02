---
id: ARCH-DECOMPOSE-050
status: confirmed    # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need | aggregate
owner: Alex
priority: could-have
depends_on: [ARCH-ATOMICITY-049, ARCH-LINT-014, ARCH-NEW-004]
satisfies: [SYS-AUTHOR-101]
superseded_by:
---

# Clause decomposition scaffold

> When `statement-size` reports an over-long clause, the remedy is to split it into its own
> requirement — and that means retyping the clause, inventing an id, and wiring the
> dependency by hand. This does the mechanical half on request. It never runs on its own,
> because `lint` also runs inside the pre-commit hook and CI, where writing a new file
> would break the very commit it was helping.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a reported clause   a Contract clause that `statement-size` named, per
                         [[ARCH-ATOMICITY-049]].
     the parent          the requirement whose Contract holds the reported clause.
     a created draft     the new requirement file this command writes.
     the default run     `lint` invoked without `--decompose`. -->

**When the command writes**
- `lint` writes no file during the default run, whatever `statement-size` reports.
- `lint --decompose` creates one draft requirement for each reported clause.
- The gate, the pre-commit hook and CI never pass `--decompose`, so those runs stay read-only.

**What a created draft holds**
- Each created draft carries `status: draft` and a `depends_on` entry naming its parent.
- The reported clause text is seeded into the created draft's Contract section.
- The created id keeps the parent's area and name, and takes the next free corpus number.

**What the command does not do**
- `lint --decompose` leaves the parent unchanged, so no confirmed contract drifts.
- The command chooses the split by word count, never by obligation, and says so on stdout.
- Each created draft records that its split point was chosen by word count alone.

**Repeating and undoing**
- Deleting a created draft restores the corpus exactly, because the parent was never edited.
- `lint --decompose` skips a clause whose target file already exists, and reports the skip.

## WHAT — Verify intent (open questions for the human)
- None — authored from stated intent, not reconstructed from code.

## HOW — Acceptance (= tests)
AC-1
  Given  a corpus with one clause above the `statement-size` threshold
  When   `lint` runs without `--decompose`
  Then   the finding is reported and the requirements directory holds no new file
AC-2
  Given  the same corpus
  When   `lint --decompose` runs
  Then   one draft is created, carrying `status: draft` and `depends_on` naming the parent
AC-3
  Given  the same corpus
  When   `lint --decompose` runs
  Then   the parent file is byte-identical to what it was before the run
AC-4
  Given  a created draft
  When   its text is read
  Then   it states that the split point was chosen by word count, not by obligation
AC-5
  Given  a parent `REQ-AUTH-012` in a corpus whose highest number is 049
  When   `lint --decompose` runs
  Then   the created id is `REQ-AUTH-050`
AC-6
  Given  a corpus where a previous `lint --decompose` already created the target file
  When   `lint --decompose` runs again
  Then   the clause is skipped, the skip is reported, and the existing file is unchanged

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
  real defect — the first implementation created a second file on every re-run, and AC-6
  caught it.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-328
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint writes no file during the default run

> `lint` writes no file during the default run, whatever `statement-size` reports.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-329
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint --decompose creates one draft requirement for each

> `lint --decompose` creates one draft requirement for each reported clause.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-330
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-331
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Each created draft carries status: draft and a

> Each created draft carries `status: draft` and a `depends_on` entry naming its parent.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-332
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The reported clause text is seeded into the

> The reported clause text is seeded into the created draft's Contract section.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-333
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The created id keeps the parent's area and

> The created id keeps the parent's area and name, and takes the next free corpus number.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-334
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Lint --decompose leaves the parent unchanged, so no

> `lint --decompose` leaves the parent unchanged, so no confirmed contract drifts.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-335
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# The command chooses the split by word count

> The command chooses the split by word count, never by obligation, and says so on stdout.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-336
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Each created draft records that its split point

> Each created draft records that its split point was chosen by word count alone.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-337
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
superseded_by:
---

# Deleting a created draft restores the corpus exactly

> Deleting a created draft restores the corpus exactly, because the parent was never
> edited.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-DECOMPOSE-338
status: draft
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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
