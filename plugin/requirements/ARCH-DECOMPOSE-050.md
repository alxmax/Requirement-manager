---
id: ARCH-DECOMPOSE-050
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.31
priority: could-have
depends_on: [ARCH-ATOMICITY-049, ARCH-LINT-014, ARCH-NEW-004]
satisfies: [SYS-AUTHOR-101]
---

# Clause decomposition scaffold

## Description
> When a requirement is too big, the remedy is to split it — and that means retyping
> clauses, inventing ids, and wiring the edges by hand. This does the mechanical half on
> request, along two seams. An over-long clause is scaffolded out on its own. A Description
> the author already divided into bold group labels is split along THOSE labels into
> code-rung children: the labels are structure the author wrote, and a behaviour group is
> what the code rung is defined as. Neither ever runs on its own, because `lint` also runs
> inside the pre-commit hook and CI, where writing a new file would break the very commit
> it was helping.

Every bullet below is binding.
- `lint` writes no file during the default run; only the opt-in `--decompose` flag creates one draft per reported `statement-size` clause, and no invocation site (the gate, the pre-commit hook, CI) ever passes it. [[REQ-DECOMPOSE-837]]
- Each created draft carries `status: draft`, a `depends_on` entry naming its parent, the offending clause seeded verbatim, and an id that reuses the parent's area/name at the next free corpus number. [[REQ-DECOMPOSE-838]]
- `lint --decompose` leaves the parent byte-identical, discloses that the split was chosen by word count and not by obligation, skips a clause already decomposed, never scaffolds from an `ac-count-high` finding, and says so when it scaffolds nothing. [[REQ-DECOMPOSE-839]]
- `clarify --decompose` splits a requirement whose Description carries two or more bold group labels into one `level: code` child per group, moves a case to a child only when the case names exactly one group's subject, writes no member tag, refuses above `LINT_AC_MAX` groups, and writes nothing without `--apply`. [[REQ-DECOMPOSE-994]]

## Cases
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

## Context
**Terms**
- a reported clause   a Contract clause that `statement-size` named, per
- [[ARCH-ATOMICITY-049]].
- the parent          the requirement whose Contract holds the reported clause.
- a created draft     the new requirement file this command writes.
- the default run     `lint` invoked without `--decompose`.

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


--------------------


---
id: REQ-DECOMPOSE-837
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
---

# --decompose is opt-in; the default lint run never writes

## Description
> `lint` also runs inside the pre-commit hook and CI, where writing a new file mid-run would
> break the very commit it was helping — the freshly-written draft would have no node in the
> already-committed map, failing the next `map --check` step in the same hook run. So
> scaffolding a draft only happens when a developer explicitly asks for it with
> `--decompose`, never on a bare `lint`.

Every bullet below is binding.
- `lint` writes no file during the default run, whatever `statement-size` or `ac-count-high` reports.
- `lint --decompose` creates one draft requirement for each reported `statement-size` clause.
- The gate, the pre-commit hook and CI never pass `--decompose`, so those runs stay read-only.

## Cases
CASE-1 — a default lint run reports the finding but writes no file
  Given  a requirement carrying a clause over the `statement-size` word threshold
  When   `lint` runs without `--decompose`
  Then   stdout names the "statement-size" finding and the requirements directory
         holds no new file

CASE-2 — --decompose creates exactly one draft file per reported clause
  Given  a parent with one clause over the `statement-size` threshold
  When   `lint --decompose` runs
  Then   exactly one new file appears in the requirements directory

CASE-3 — no invocation site passes --decompose
  Given  `.githooks/pre-commit` and `.github/workflows/ci.yml`
  When   their `lint` invocation lines are read
  Then   neither contains the `--decompose` flag


--------------------


---
id: REQ-DECOMPOSE-838
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
---

# A created draft's shape: status, parent link, seeded clause, id

## Description
> A word-count split cannot prove the clause it cut actually held two obligations, so the
> created file is never trusted outright — it starts life as a `draft` naming its parent in
> `depends_on`, carries the exact clause text so the author can judge it, and gets an id
> that fits the corpus's existing naming scheme rather than a derived suffix.

Every bullet below is binding.
- Each created draft carries `status: draft` and a `depends_on` entry naming its parent.
- The reported clause text is seeded into the created draft's Contract section.
- The created id keeps the parent's area and name, and takes the next free corpus number.

## Cases
CASE-1 — the created draft carries status: draft and depends_on the parent
  Given  `lint --decompose` creates a draft from `REQ-AUTH-012`
  When   the created file's frontmatter is read
  Then   it contains `status: draft` and `depends_on: [REQ-AUTH-012]`

CASE-2 — the offending clause's own text appears verbatim in the created draft
  Given  a parent clause of 155 repeated words flagged by `statement-size`
  When   `lint --decompose` creates the draft
  Then   the draft's Contract section contains that exact clause text

CASE-3 — the created id reuses the parent's area/name with the next free number
  Given  parent `REQ-AUTH-012` in a corpus whose highest existing number is 049
  When   `lint --decompose` runs
  Then   the created file is named `REQ-AUTH-050.md`


--------------------


---
id: REQ-DECOMPOSE-839
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
---

# The parent never changes, and the command knows its own limits

## Description
> Rewriting a clause inside a `confirmed` requirement would change its contract hash and force
> `sync --accept-drift` — too large a consequence for a warn-only lint finding. So the parent
> is never touched, deleting a created draft restores the corpus exactly, a re-run skips a
> clause it already scaffolded, and the command only ever acts on `statement-size` findings —
> never on `ac-count-high`, a signal this corpus has no confirmed fire-rate evidence for.

Every bullet below is binding.
- `lint --decompose` leaves the parent unchanged, so no confirmed contract drifts.
- The command chooses the split by word count, never by obligation, and says so on stdout.
- Each created draft records that its split point was chosen by word count alone.
- `lint --decompose` scaffolds from `statement-size` findings only; an `ac-count-high` finding is reported and nothing is written for it.
- Deleting a created draft restores the corpus exactly, because the parent was never edited.
- `lint --decompose` skips a clause whose target file already exists, and reports the skip.
- A run that scaffolds nothing says which finding the flag acts on, so silence cannot be
  read as agreement by an author the same run has just told to split something.

## Cases
CASE-1 — the parent file is byte-identical after a decompose run
  Given  the parent file's bytes captured before `lint --decompose` runs
  When   the run completes
  Then   the parent file's bytes are unchanged from the captured snapshot, so deleting the
         created draft restores the corpus exactly

CASE-2 — stdout discloses the split was by word count, not obligation
  Given  `lint --decompose` running on a flagged clause
  When   the run completes
  Then   stdout includes "word count, not by obligation"

CASE-3 — the created draft's own text discloses the word-count-only split
  Given  a draft created by `lint --decompose`
  When   its file text is read
  Then   it contains "WORD COUNT, never by obligation"

CASE-4 — a second decompose run skips the already-decomposed clause and reports it
  Given  a clause already decomposed by a prior `lint --decompose` run
  When   `lint --decompose` runs again
  Then   stdout reports "skipped" and no second file is created for that clause

CASE-5 — an ac-count-high finding is reported but never scaffolded
  Given  a non-exempt requirement above `LINT_AC_MAX` acceptance criteria
  When   `lint --decompose` runs
  Then   the `ac-count-high` finding still prints and no file is created for it

CASE-6 — a run that scaffolds nothing says so
  Given  a requirement carrying no `statement-size` finding
  When   `lint --decompose` runs on it
  Then   the output states that nothing was scaffolded and which finding the flag acts on,
         so a no-op cannot be read as a clean bill of health


--------------------


---
id: REQ-DECOMPOSE-994
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DECOMPOSE-050]
---

# Splitting a requirement along its own contract groups

## Description
> `init` mints the code rung only for files it extracts, and it extracts only untagged
> files; `clarify --levels` classifies a requirement but never creates one. So a corpus that
> adopted the tool at the architecture rung had no path to `level: code` at all — on one
> consumer, 40 of 42 architecture nodes had zero children while 160 bold group labels sat
> in their Descriptions saying exactly where the seams were. This reads those seams. It is
> not the engine inventing structure; it is the engine reading structure the author already
> wrote, which is the line ADR-0025 had to refold 573 leaves back behind.

Every bullet below is binding.
- A requirement whose Description carries two or more bold group labels is split into one
  child per group; a requirement with fewer than two falls through to the clause-level path.
- Each child carries `status: draft`, `level: code`, `level_source: auto`, `satisfies:` the
  parent, the group's clauses verbatim, and an id of the parent's stem plus the group's
  subject, with a numeric suffix only on collision.
- A parent case moves to a child only when the case's text names exactly one group's
  subject; a case naming none or more than one stays on the parent, and the run reports
  how many stayed.
- No `implements:` tag is written. Each child lists the members it is expected to claim,
  found by searching the parent's `implements:` files for the group's subject at a
  definition.
- A parent with more than `LINT_AC_MAX` groups is refused with the group list and the
  instruction to merge labels first.
- Without `--apply` the run prints the whole plan and writes nothing. With it, the children
  are written and the parent is rewritten: each split group becomes one obligation line
  naming its child, moved cases leave, surviving cases keep their labels, and a parent left
  with no case gets one placeholder naming what the rung still owes. Everything outside the
  Description and Cases is byte-identical.
- With no id, every requirement in the corpus that carries two or more groups is planned,
  and each is written independently on `--apply`.

## Cases
CASE-1 — the author's group labels are the seams
  Given  a requirement whose Description has three bold labels, each followed by bullets
  When   `clarify <ID> --decompose --apply` runs
  Then   three child files exist, each carrying its group's bullets verbatim, `level: code`,
         `level_source: auto`, `status: draft` and `satisfies: [<ID>]`

CASE-2 — a case moves only when it names exactly one subject
  Given  a parent case naming one group's subject, one naming two, and one naming none
  When   the split runs
  Then   the first case lands in its child and the other two stay on the parent, and stdout
         reports 2 stayed

CASE-3 — no tag is written, expected members are listed
  Given  a parent whose `implements:` file defines the group's subject as a function
  When   the split runs
  Then   the child's Context lists that `file:line` and no `implements:` line was added to
         any source file

CASE-4 — too many groups is refused, not split
  Given  a requirement with `LINT_AC_MAX + 1` groups
  When   the split runs with `--apply`
  Then   nothing is written and stdout names the groups and says to merge them first

CASE-5 — the dry run is a dry run
  Given  a splittable requirement
  When   `clarify <ID> --decompose` runs without `--apply`
  Then   the plan is printed and no file in the requirements directory changed

CASE-6 — the parent is rewritten only where the split happened
  Given  a parent with prose before its Description and a Context section after its Cases
  When   the split runs with `--apply`
  Then   every split group is one line ending in its child's id, surviving cases keep their
         original labels, and the text outside Description and Cases is byte-identical

CASE-7 — a parent stripped of every case gets a placeholder, not an empty section
  Given  a parent whose cases all name a child
  When   the split runs with `--apply`
  Then   the parent's Cases section holds one placeholder case rather than nothing
