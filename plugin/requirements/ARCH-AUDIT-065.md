---
id: ARCH-AUDIT-065
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v4.2
depends_on: [ARCH-CHECK-006, ARCH-NEXT-013, ARCH-SIMILAR-016, ARCH-COVERAGE-029, ARCH-DESIGN-061]
satisfies: [SYS-REPORT-105]
---

# One report of everything the engine can discover

## Description
> The engine grew one verb per question — is it linked, is it drifted, is it duplicated, is
> it tagged, is the design rotting — and answering "how is this repo doing" came to mean
> remembering all of them. A reader who does not already know the command list never meets
> most of the answers. `audit` runs those passes together and prints one report, and it
> ends with the two things no verb reports because they only make sense here: which findings
> somebody silenced, and whether the corpus has a shape at all.

Every bullet below is binding.
- `audit` runs every discovery pass and prints one report, taking its exit code from the gate alone. [[REQ-AUDIT-970]]
- Every exemption in force is listed, and one that records no reason is itself a warning. [[REQ-AUDIT-971]]
- The report says how the corpus sits on the V-model's left arm, and says so without failing. [[REQ-AUDIT-972]]
- `sync` ends by naming what the audit would report, so the moment the corpus changes is the moment its problems surface. [[REQ-AUDIT-973]]

## Cases
CASE-1
  Given  a corpus with a clean gate
  When   `audit` runs
  Then   it exits 0 and its report names every section it ran

CASE-2
  Given  a corpus whose gate reports an error
  When   `audit` runs
  Then   it exits non-zero, and the advisory sections still appear in full

CASE-3
  Given  any corpus
  When   `audit --json` runs
  Then   the output parses as JSON and carries the gate, health, exemption and shape records

## Context
**Terms**
- discovery pass  one existing read-only command that finds problems: the gate, `next`,
- `dupes`, `design`, tag coverage.
- exemption       a `lint_exempt:`/`gate_exempt:` entry that silences one check for one
- requirement.

**Notes**
- `audit` is not the gate and never becomes it. Only the gate's own findings reach the
  exit code; a duplicate contract, a design candidate or a flat corpus is advice, and
  advice that can fail a build stops being read and starts being suppressed.
- It deliberately re-runs existing commands rather than reimplementing their checks, so
  there is no second definition of any finding to drift away from the first.


--------------------


---
id: REQ-AUDIT-970
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDIT-065]
---

# Every discovery pass, one report, one exit code

## Description
> Running five commands by hand to learn what is wrong with a repo means four of them are
> never run. The report puts its summary first — one line per signal, each naming the verb
> that produced it — then each section's own output underneath, so a reader can act on the
> summary or read the detail without running anything a second time.

Every bullet below is binding.
- `audit` runs the gate, the corpus risk report, the duplicate-contract scan, the design
  review and the tag-coverage report, and prints each one's output under its own heading.
- The report opens with a summary naming, for each signal, what was found and which command
  produces it on its own.
- The exit code is the gate's. Every other section is advice and can never change it.
- A section that raises is reported as a failed section and the rest of the report still
  prints. A partial report is worth more than a traceback.
- A gate section that raises fails the audit. Advice that crashes is missing advice; a gate
  that crashes reached no verdict, and reporting one is worse than reporting nothing.
- `--json` emits the gate findings, the health record, the design record, the untagged
  count, the exemptions and the corpus shape as one object.

## Cases
CASE-1 — one command runs them all
  Given  a corpus with requirements and code
  When   `audit` runs
  Then   the output carries a section for the gate, risk, duplicates, design and tag coverage

CASE-2 — only the gate decides the exit code
  Given  a corpus whose gate is clean but which has duplicate contracts and design candidates
  When   `audit` runs
  Then   it exits 0

CASE-3 — a failing gate fails the audit
  Given  a corpus with a dangling membership tag
  When   `audit` runs
  Then   it exits non-zero

CASE-4 — a raising section does not take the report down
  Given  a discovery pass that raises
  When   `audit` runs
  Then   that section reports the failure and every other section still prints

CASE-5 — the structured form carries the same signals
  Given  any corpus
  When   `audit --json` runs
  Then   the parsed object carries `gate`, `health`, `exemptions` and `shape`

CASE-6 — a crashing gate section is not a clean gate
  Given  a gate section whose function raises
  When   `audit` runs
  Then   the report prints, the Gate row reads FAIL, and the exit code is 1


--------------------


---
id: REQ-AUDIT-971
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDIT-065]
---

# An exemption nobody justified is itself a finding

## Description
> An exemption is a finding somebody decided not to see. It was also the cheapest thing to
> reach for: one frontmatter token silences a check permanently, nobody has to say why, and
> nothing ever mentions it again — so "split this requirement" and "add one word here" cost
> a reader the same, and the wrong one won. Listing every exemption keeps silenced from
> becoming invisible, and warning on a bare one makes exempting cost a sentence a reviewer
> can argue with.

Every bullet below is binding.
- The report lists every `lint_exempt:` and `gate_exempt:` entry in the corpus with its
  requirement and the check it silences.
- A reason counts as recorded when the requirement's own prose mentions the silenced
  check by name. The test cannot judge whether the reason is a good one, and does not try
  to: it makes the exemption cost a sentence, no more.
- The gate warns once per unjustified exemption. The finding is warn-only and is never
  promoted under `--strict` — the point is to make silencing cost something, not to make
  it impossible.
- The two findings used to name `clarify <ID> --decompose` as the remedy. They no longer
  do: that flag acts on `statement-size` findings ONLY, so an author who followed the
  advice on an over-scoped requirement got `All clean` and no files from a command the
  gate had just called an error — and was left with `lint_exempt:`, the one action the
  skill names as the reflex to avoid. Naming a remedy is right; naming one that no-ops
  is worse than naming none.

## Cases
CASE-1 — an exemption with a written reason is clean
  Given  a requirement carrying `lint_exempt: [file-spread]` whose prose explains why
  When   the gate runs
  Then   no exemption warning is raised for it

CASE-2 — a bare exemption is a warning
  Given  a requirement carrying `lint_exempt: [ac-count-high]` and never mentioning it again
  When   the gate runs
  Then   one warning names the requirement, the field and the silenced check

CASE-3 — the exemption warning never fails a build
  Given  a corpus whose only finding is an unjustified exemption
  When   `gate --strict` runs
  Then   the finding is still a warning and the run still exits 0

CASE-4 — the split findings name a remedy that can act on them
  Given  a requirement with more acceptance criteria than the ceiling
  When   the linter reports it
  Then   the finding says what to move and says that `--decompose` does not cover it


--------------------


---
id: REQ-AUDIT-972
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDIT-065]
---

# Whether the corpus has a shape at all

## Description
> `level:` ships commented out in the template, so an existing corpus keeps its behaviour
> and a new one never gains the axis by itself. The consequence nobody was told about: a
> repo can run the engine for months with every requirement on one rung, and every surface
> that reads a level quietly defaults it. The report says so once, and says what the three
> rungs are, because a reader who has never seen the pyramid cannot ask for it.

Every bullet below is binding.
- The report states how many requirements declare a `level:`, how they spread across the
  rungs, and how many `satisfies:` edges exist.
- A corpus where fewer than a tenth of requirements declare a level is called flat, and the
  report then names the three rungs and the `satisfies:` edge that builds the pyramid.
- Nothing about this fails or warns in the gate. Adopting a level axis is a decision, and
  a corpus that has decided otherwise is not defective.

## Cases
CASE-1 — a levelled corpus is described, not advised
  Given  a corpus where every requirement declares a level
  When   `audit` runs
  Then   the counts per rung are printed and no flat-corpus advice appears

CASE-2 — a flat corpus is named as flat
  Given  a corpus where no requirement declares a level
  When   `audit` runs
  Then   the report says the corpus is flat and names the three rungs

CASE-3 — the shape never reaches the exit code
  Given  a flat corpus with a clean gate
  When   `audit` runs
  Then   it exits 0


--------------------


---
id: REQ-AUDIT-973
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-AUDIT-065]
---

# Sync says what it found

## Description
> `sync` is the moment the corpus was just rewritten, and until now it reported only what
> it regenerated. A repo could sync for months without ever meeting the duplicate scan, the
> design review, the exemption list, or the fact that its TODO file stopped tracking what
> shipped. Sync now ends with one line per signal that is not clean, and nothing at all
> when everything is.

Every bullet below is binding.
- After a successful `sync`, one line is printed for each signal that is not clean:
  unjustified exemptions, a flat corpus, requirement-readability errors, rungs still
  carrying the engine's proposal, design candidates, untagged code, and a TODO file whose
  newest milestone is behind the requirements'.
- The readability line counts errors only. A style warning never breaks the tail's silence,
  because a corpus can carry one for months and a line that always appears is not news.
- The proposed-rung line fires only on a corpus that is not flat, and counts the levelled
  requirements still marked `level_source: auto` — a pyramid made entirely of the engine's
  guesses reads as healthy on every other count.
- A repo where every one of those is clean sees no extra output, so a line that does appear
  is news rather than noise.
- The tail points at `audit` for the full report, and changes neither what `sync` writes
  nor its exit code.

## Cases
CASE-1 — a signal that is not clean is named
  Given  a corpus with an unjustified exemption
  When   `sync` completes
  Then   its output names that signal and points at `audit`

CASE-2 — a clean corpus stays quiet
  Given  a corpus where every audited signal is clean
  When   `sync` completes
  Then   no advisory tail is printed

CASE-3 — the tail is report-only
  Given  any corpus
  When   `sync` completes
  Then   the exit code and the files written are exactly what they were without the tail
