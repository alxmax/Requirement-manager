---
id: ARCH-EXTRACT-008
status: draft
level: architecture
layer: feature
owner: Alex
milestone: v1.06
depends_on: [ARCH-SCAN-002]
satisfies: [SYS-READ-103]
---

# Legacy extraction

## Description
> When an existing project has lots of code but no requirements written down, this gives you
> a running start: it reads each untagged file and writes a rough draft requirement for it,
> clearly marked as a draft so no one mistakes a guess for a settled decision. Without it,
> someone would have to sit down and describe every existing capability from scratch before
> the tool was useful on an older project. Spec and prompt documents get the same treatment
> from the companion capability [[ARCH-PROSE-024]].

Every bullet below is binding.
- `draft` walks every untagged scannable code file, skipping tagged and `.reqmapignore`-matched ones. [[REQ-EXTRACT-849]] details the behaviour.
- `draft` proposes one `requirements/DRAFT-*.md` per remaining file, marked `status: draft` with a TODO contract. [[REQ-EXTRACT-850]] details the behaviour.
- `draft` assigns a cheap risk score from `TODO`/`FIXME`/`HACK`/`XXX` markers, suppressions and file size, and never overwrites an existing draft. [[REQ-EXTRACT-851]] details the behaviour.
- Extraction drafts all three specification rungs and marks every one it invented, so a corpus starts as a pyramid the author corrects rather than a flat list. [[REQ-EXTRACT-981]] details the behaviour.

## Cases
CASE-1
  Given  an untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file
  When   `draft` runs
  Then   it yields one `DRAFT-*` draft

CASE-2
  Given  a file already carrying a member tag
  When   `draft` runs
  Then   the file is skipped

CASE-3
  Given  a file matching a `.reqmapignore` pattern
  When   `draft` runs
  Then   the file is skipped (no draft proposed for it)

CASE-4
  Given  a file containing `TODO`/`FIXME`
  When   `draft` runs
  Then   it scores higher risk and is flagged `REVIEW`

CASE-5
  Given  an existing draft and same-basename files in different dirs
  When   `draft` re-runs
  Then   the draft is not overwritten and the basenames do not collide

CASE-6
  Given  an untagged `.py` file with a module docstring and two top-level functions
  When   `draft` runs
  Then   its proposal's WHERE section names both signatures, and its Contract is still the TODO placeholder

## Context
**Terms**
- a member tag  a comment naming the requirement a piece of code belongs to.
- a draft       a `requirements/DRAFT-*.md` file: a guess at what a file does,
- marked so nobody mistakes it for a settled decision.
- the risk score  a cheap number saying how suspect a file looks, used only to
- decide whether a human should read the draft first.

**Notes**
- `draft` cannot recover intent; prefer `plan` (read-only plan) before authoring.
  The draft body uses the same Contract/Acceptance section names as a real requirement so a
  promoted draft needs no reshaping.
- Prose (`.md`/`.html`) classification and drafting is a separate capability —
  [[ARCH-PROSE-024]] — running under the same `draft` command.
- The drafted file types (`.py`/`.js`/`.ts`/`.c`/`.cpp`) are deliberately narrower than the
  gate's full scan set (which also enforces tags in `.go`/`.rs`/`.tsx` and more): drafting
  targets mainstream source, while the gate enforces tags wherever they appear.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs `draft` on a brownfield repo. For each untagged source file it drops a
  `DRAFT-*.md` capturing what the file appears to do; one file full of `TODO` and `FIXME`
  markers scores higher risk and is flagged `REVIEW`. The engine's own `reqmap.py` is in
  `.reqmapignore`, so it is skipped — leaving Ana a pile of starting points to promote
  into real requirements.

**Current implementation**
- `cmd_extract`, `_draft_id`, `_risk` in `reqmap.py`.


--------------------


---
id: REQ-EXTRACT-849
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
---

# Which files draft walks

## Description
> Drafting every file in a repo would bury real gaps under noise, so `draft` only walks
> scannable code files that carry no member tag yet and are not excluded by
> `.reqmapignore` — the same ignore file `scan` respects, which is how the engine's own
> vendored `reqmap.py` stays out of its own drafts.

Every bullet below is binding.
- `draft` walks every untagged scannable code file — the extensions and basenames the
  scan reads — plus prose in the capability bucket.
- `draft` skips a file that already carries a member tag.
- `draft` honors `.reqmapignore`, the same fnmatch globs `scan` respects.
- A file matching an ignore pattern is never drafted — notably the vendored
  `scripts/reqmap.py` engine itself.

## Cases
CASE-1 — draft proposes a file for every untagged scannable extension
  Given  an untagged `.py` file and an untagged `.rs` file, both scannable extensions
  When   `draft` runs
  Then   it proposes one `DRAFT-*.md` for each

CASE-2 — draft skips a file already carrying a member tag
  Given  a `.py` file carrying `# implements: AUTH-LOGIN-001`
  When   `draft` runs
  Then   no `DRAFT-*.md` is proposed for that file

CASE-3 — draft skips a file matched by .reqmapignore
  Given  an untagged file matching a `.reqmapignore` glob pattern
  When   `draft` runs
  Then   no `DRAFT-*.md` is proposed for that file — notably the vendored
         `scripts/reqmap.py` engine itself


--------------------


---
id: REQ-EXTRACT-850
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
---

# Writing one draft proposal per file

## Description
> A draft must never be mistaken for a settled decision, so each proposal is written
> `status: draft` with a TODO contract, opening the same way `new` scaffolds a real
> requirement so promoting it later needs no reshaping. Ids are path-aware, so two files
> sharing a basename in different folders never collide.

Every bullet below is binding.
- `draft` proposes one `requirements/DRAFT-*.md` per remaining file.
- Every proposal carries `status: draft` and a TODO body. It captures observed
  behavior, and never canonizes intent or correctness.
- A proposal's Contract section opens with "Every bullet below is binding.",
  matching what `new` scaffolds, so promoting a draft needs no reshaping.
- `draft` creates the requirements directory if it is absent.
- Draft ids are path-aware, so two files sharing a basename do not collide.

## Cases
CASE-1 — draft writes one proposal file per remaining source file
  Given  two untagged, unignored source files
  When   `draft` runs
  Then   it writes two distinct `requirements/DRAFT-*.md` files

CASE-2 — a fresh proposal is marked draft with a TODO contract
  Given  an untagged source file
  When   `draft` runs
  Then   the proposal's frontmatter reads `status: draft` and its Contract is a TODO placeholder

CASE-3 — a proposal's Contract opens exactly like new's scaffold
  Given  a fresh `draft` proposal and a requirement scaffolded by `new`
  When   both Contract sections are compared
  Then   both open with "Every bullet below is binding."

CASE-4 — draft creates a missing requirements directory
  Given  a repo with no `requirements/` directory yet
  When   `draft` runs
  Then   `requirements/` is created and the proposals are written into it

CASE-5 — draft ids stay unique across same-named files in different folders
  Given  `src/a/util.py` and `src/b/util.py`, both untagged
  When   `draft` runs
  Then   it writes two proposals with distinct ids, one per path


--------------------


---
id: REQ-EXTRACT-851
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
---

# Scoring risk and capturing an authoring hint

## Description
> Not every draft needs the same scrutiny, so `draft` scores each file cheaply from
> `TODO`/`FIXME`/`HACK`/`XXX` markers, suppressions and size, routing riskier files to
> `REVIEW`. When the language has a parser, it also records the file's docstring and
> top-level signatures under WHERE as a hint for the human — never as a Contract line,
> since the Contract stays a TODO until a person writes it.

Every bullet below is binding.
- `draft` assigns a cheap risk score from `TODO`/`FIXME`/`HACK`/`XXX` markers,
  suppressions and file size.
- `draft` routes a score of 2 or more to `REVIEW`, and any lower score to
  `auto-baseline`.
- Re-running `draft` never overwrites an existing draft.
- A code proposal's WHERE section lists the file's observed surface — the module
  docstring's first line and its top-level signatures — when the language has a parser.
- That surface is an authoring hint under WHERE, never a Contract line. The Contract
  stays a TODO until a human writes it.

## Cases
CASE-1 — a marker-heavy file scores as higher risk
  Given  an untagged file containing `TODO`, `FIXME` and a suppression comment
  When   `draft` runs
  Then   its proposal carries a higher risk score than a clean file of the same size

CASE-2 — the risk score routes the proposal's status hint
  Given  one file scoring 2 and one file scoring 0
  When   `draft` runs
  Then   the first proposal is flagged `REVIEW` and the second `auto-baseline`

CASE-3 — re-running draft leaves an existing proposal untouched
  Given  a `DRAFT-*.md` written by an earlier `draft` run, since hand-edited
  When   `draft` runs again over the same file
  Then   the existing proposal's content is unchanged

CASE-4 — a Python proposal's WHERE names the docstring and top-level signatures
  Given  an untagged `.py` file with a module docstring and two top-level functions
  When   `draft` runs
  Then   the proposal's WHERE section names the docstring's first line and both function signatures

CASE-5 — the extracted surface never leaks into the Contract
  Given  the same `.py` file's proposal, whose WHERE lists two function signatures
  When   the proposal's Contract section is inspected
  Then   it is still the TODO placeholder, unchanged by what WHERE captured

---
id: REQ-EXTRACT-981
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
---

# The three rungs extraction drafts

## Description
> The tool's premise is a pyramid — a need, satisfied by capabilities, satisfied by
> behaviour groups — and extraction produced the opposite: one flat draft per file. The
> three rungs are not equally knowable from source, so the engine asserts the one it can
> know, proposes the one it can only guess from a directory, and refuses to guess the one
> that is not in the code at all. What it invented, it marks. See
> [ADR-0030](../../docs/adr/0030-the-engine-drafts-the-pyramid.md).

Every bullet below is binding.
- A draft extracted from a source file carries `level: code`. A draft describes that file's behaviour, so the rung is asserted rather than inferred.
- Each source directory that produced at least one code draft gets one architecture draft, whose id is built from the last two path segments and whose body states that a directory is not a capability.
- Every code draft declares `satisfies:` its directory's architecture draft, and every architecture draft declares `satisfies:` the system placeholder.
- One `level: system`, `layer: need` placeholder is written when at least one architecture draft exists, titled so a reader sees it is a hole the engine refused to fill.
- Everything extraction writes about the level axis carries `level_source: auto`, the parallel of `owner: auto`, so a rung the engine invented stays distinguishable from one a human decided.
- Every node extraction mints is `status: draft`, which the gate never enforces, and an existing file of the same id is never overwritten.

## Cases
CASE-1 — the asserted rung
  Given  a repo with one untagged source file
  When   `init` runs
  Then   the file's draft carries `level: code` and `level_source: auto`

CASE-2 — the proposed rung
  Given  a repo whose code sits in two directories
  When   `init` runs
  Then   two architecture drafts exist, each satisfied by the code drafts of its own directory

CASE-3 — the refused rung
  Given  the same repo
  When   `init` runs
  Then   exactly one `layer: need` placeholder exists, every architecture draft satisfies it, and its title says a human must name it

CASE-4 — nothing is overwritten
  Given  a corpus already carrying an architecture draft for a directory
  When   `init` runs again
  Then   that file is left byte-identical and no duplicate is written

## Context
**Notes**
- The directory names will often be wrong: measured on this repo before the decision, directory inference proposes capabilities called `scripts` and `app/src/lib`. That is why the architecture node is a `draft` whose own body tells the reader to rename, merge or delete it. A wrong name that says it is a guess is recoverable; a wrong name that looks decided is not.
- `level_source: auto` is the only part of ADR-0030 that reaches a consumer — the ADR set is not shipped inside `plugin/`. It is therefore the load-bearing half of the record, not an annotation on it.
