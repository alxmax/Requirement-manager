---
id: ARCH-EXTRACT-008
status: confirmed
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
- Extraction links each source file to the draft it produced by writing that file’s membership tag into it, reversibly, so a stub never ships with zero members. [[REQ-INITTAG-1008]]
- `draft` asks one question per line where the scan finds a marker, a suppression, a swallowed error, an unnamed number or unreachable code, naming the line. [[REQ-EXTRACT-1099]]

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
milestone: v3.2
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
milestone: v3.2
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
milestone: v3.2
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
milestone: v6.3
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
- An architecture or system draft given more children than its level's `LINT_FANOUT_BANDS` ceiling is named in one `note:` line that says to split it by area, because the lint never reads a draft.

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

CASE-5 — a flat repo is told its one directory is past the band
  Given  31 source files in the repository root, and separately one file in `src/`
  When   `init` extracts drafts from each
  Then   the first names `ARCH-ROOT-001` with 31 children over the architecture ceiling of 30; the second prints no note

## Context
**Notes**
- The directory names will often be wrong: measured on this repo before the decision, directory inference proposes capabilities called `scripts` and `app/src/lib`. That is why the architecture node is a `draft` whose own body tells the reader to rename, merge or delete it. A wrong name that says it is a guess is recoverable; a wrong name that looks decided is not.
- `level_source: auto` is the only part of ADR-0030 that reaches a consumer — the ADR set is not shipped inside `plugin/`. It is therefore the load-bearing half of the record, not an annotation on it.


--------------------


---
id: REQ-INITTAG-1008
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.10
satisfies: [ARCH-EXTRACT-008]
---

# The draft and its source are linked in the same run

## Description
> `init` wrote the requirement stub and left the source file untagged, so the two never met:
> the stub had zero members, the file stayed in the untagged bucket forever, and
> `gate --risk` kept proposing the `init` that had already run. A consumer deleted eleven
> such orphan stubs by hand, then four more the same day, before anyone noticed the loop.
> The engine already writes into source in the other direction — `init --wipe` strips these
> very tags — so the boundary was never the objection.

Every bullet below is binding.
- For every draft it writes from a source file, `init` inserts that file's membership tag
  into the file: `implements:` normally, `tested-by:` when the path is a test path.
- The tag is spelled with the line-comment form of the file's own type, and a file type
  with no known comment form is skipped and reported rather than guessed at.
- A line the language requires first — shebang, XML or HTML preamble, `@charset` — stays
  first, and a UTF-8 BOM stays the file's first bytes.
- The file's own line endings survive the insertion; a CRLF file does not become LF.
- A file that already carries any membership tag is never given a second one, and a file
  the scan cannot decode is never rewritten.
- `init --wipe` removes a tag that was the whole line without leaving a blank line behind,
  so repeating wipe-then-init is a fixed point rather than growing the file a line at a
  time.
- `init` reports how many of the sources it drafted it managed to link.

## Cases
CASE-1 — the drafted source becomes a member
  Given  one untagged source file and no requirements
  When   `init` runs
  Then   the file carries the draft's `implements:` tag, is a member of it, and the untagged
         bucket is empty

CASE-2 — the comment marker matches the language
  Given  untagged `.py`, `.jsx`, `.css` and `.sql` files
  When   `init` runs
  Then   their tags open with `#`, `//`, `/* … */` and `--` respectively

CASE-3 — a required first line stays first
  Given  a source file opening with a shebang, and one opening with `@charset`
  When   `init` runs
  Then   both still open with that line, and the tag sits immediately after it

CASE-4 — a test file is linked as a test
  Given  an untagged file at a test path
  When   `init` runs
  Then   its tag is `tested-by:`, not `implements:`

CASE-5 — line endings survive
  Given  an untagged CRLF source file
  When   `init` runs
  Then   every line in the file, the inserted one included, still ends with CRLF

CASE-6 — wipe then init is a fixed point
  Given  a source file that `init` has tagged
  When   `init --wipe` runs three times
  Then   the file is byte-identical after each run and never gains a line

CASE-7 — an existing tag is left alone
  Given  a source file already carrying `# implements: ARCH-FOO-001`
  When   `init` runs
  Then   the file still carries exactly one membership tag

## Context
**Notes**
- `tested-by:` for a test path is the author's stated design. It has a consequence worth
  knowing: a requirement whose only member is a test has no `implements:` member, so RM006
  errors if it is ever promoted to `confirmed`. That is correct feedback — a confirmed
  requirement with only a test behind it is exactly what RM006 exists to catch — but it
  means such a draft needs either an implementation member or retirement, not a promotion.
- `lint_exempt: file-spread` - the tag spelling, the insertion point, the write and the
  wipe half live in the modules that own each, by design; one file holding all four
  would put source-rewriting logic inside the tag grammar.
- `_strip_line_tag` still blanks the line it strips; that is its own tested contract and the
  right answer for `def f():  # implements: X`. The whole-line case is decided by the wipe
  loop instead, which is the only caller that knows the line was nothing but a tag.
- The insertion rewrites the file with `newline=""` and `errors="surrogateescape"`, the same
  pair `--wipe` already used, so non-UTF-8 bytes elsewhere in the file round-trip verbatim.
  It splits with `splitlines(keepends=True)` rather than the scan's normalising reader,
  because a rewrite must preserve the bytes a line number is measured against.

--------------------


---
id: REQ-EXTRACT-1099
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-EXTRACT-008]
---

# A code draft asks about the lines the scan found

## Description
> A draft used to ask every file the same sentence: "anything that looks like an accident
> (swallowed error, magic constant, dead branch), intended, or a bug to fix?". With a
> hundred drafts, `_findings.md` held a hundred copies of it and named no line, while
> the scan had already seen the `TODO`, the `noqa` and the empty `except` and kept only
> a risk score. A question that names its line can be answered; one that names nothing
> is skipped.

Every bullet below is binding.
- `draft` writes one Verify-intent question per line where the scan finds a signal, each
  reading `Observed at `<file>:<line>`: `<code>`` followed by what only the author can
  answer.
- The signals found in every language, by pattern, are a `TODO`/`FIXME`/`HACK`/`XXX`
  marker inside a comment, a suppression (`noqa`, `type: ignore`, `eslint-disable`,
  `@ts-ignore`, `NOLINT`), and an empty `catch` block.
- The signals found in Python only, by parsing, are an `except` whose body only passes,
  continues or returns nothing; a number other than -1, 0, 1 and 2 written into a
  comparison or a keyword argument inside a function; and a statement after an
  unconditional `return`, `raise`, `continue` or `break`.
- A marker in a string literal, or in a file name such as `TODO.md`, is not a signal. In
  Python a marker or suppression counts only in a comment token, and none counts when the
  file does not tokenize; in any other language string literals are blanked before the
  patterns run, and comments too before an empty `catch` is looked for.
- When the Python file does not parse, or no parser reads the language, Context names the
  signals that were not looked for, so a partial scan never reads as a clean one.
- `draft` writes at most eight questions per file, in line order, and names how many it
  left out under Context.
- A file with no signal keeps the generic question it always had.

## Cases
CASE-1 — each Python signal is one question naming its line
  Given  an untagged `.py` file with a `TODO` comment, an `except` that returns `None`,
         a comparison against 37, and a statement after a `return`
  When   `draft` runs
  Then   its Verify intent holds four questions, each starting `Observed at` and naming
         `svc.py:<line>` for the line it is about

CASE-2 — a marker outside a comment is not a question
  Given  an untagged `.py` file whose only `TODO` is in a string and whose only comment
         mentions `TODO.md`
  When   `draft` runs
  Then   its Verify intent holds only the generic question

CASE-3 — a clean file keeps the generic question
  Given  an untagged `.py` file with no marker, suppression or swallowed error
  When   `draft` runs
  Then   its Verify intent holds the generic question and nothing else

CASE-4 — the questions stop at eight and the rest are counted
  Given  an untagged `.py` file with eleven suppressed lines
  When   `draft` runs
  Then   its Verify intent holds eight questions and its Context says 3 more signals exist

CASE-5 — the pattern signals apply to a language with no parser
  Given  an untagged `.js` file with an empty `catch` block and a `FIXME` comment
  When   `draft` runs
  Then   its Verify intent holds one question for each, naming `app.js:1` and `app.js:2`

CASE-6 — a signal quoted in a string is not observed
  Given  a `.py` file holding `"# TODO: example"` and `"# noqa"` in strings and one real
         `# TODO` comment; a `.py` file whose only line opens a string it never closes;
         and a `.js` file holding `catch (e) {}` only in strings and comments
  When   `draft` runs
  Then   the first asks only about the comment's line, the second keeps the generic
         question and says comment markers were not looked for, and the third keeps the
         generic question, while a real empty `catch` keeps its own line

CASE-7 — a partial scan says what it did not look for
  Given  a `.py` file that does not parse, a `.rs` file, and a clean `.py` file
  When   `draft` runs
  Then   the first two keep the generic question and their Context says what was not
         looked for; the clean file's Context says nothing of the kind

## Context
**Notes**
- The questions are built in `draftquestions.py`, which `draft` imports at call time, so
  the module stays out of the core `sync` and `gate --full` load (ADR-0070).
- The engine's own fail-open `except Exception: return None` is asked about like any
  other swallowed error. The scan cannot read intent, and the question says so.
