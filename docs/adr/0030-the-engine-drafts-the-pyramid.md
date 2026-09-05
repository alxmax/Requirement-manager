# ADR-0030 — The engine drafts the pyramid; the author corrects it

- **Status:** Accepted. Supersedes [ADR-0019](0019-v-model-left-arm-adopted.md) on one
  point only — its sentence that the level pairing works "onto an axis the author declares
  rather than one the engine infers". Everything else in 0019 stands, including the
  warn-only posture and the 2027-03-03 revisit.
- **Decided:** 2026-09-06 (`ARCH-EXTRACT-008`, `ARCH-INIT-012`, `ARCH-LEVEL-051`)
- **Where:** `init` only. `draft` was folded into `init` in v5.0.0 and `cmd_extract` has
  exactly one caller, so there is one place for this to happen and one place to undo it.
- **Evidence:** the nine-senator audit
  `runs/senate/2026-09-06_003141-senate-reqmap-three-levels-adoption.json` (MODIFY, GO 1 /
  MODIFY 6 / STOP 2), whose blocking requests this record answers rather than ignores; the
  directory-inference measurement below, run on this repo.

## Context

The tool's premise is a pyramid: a stakeholder need, satisfied by capabilities, satisfied
by behaviour groups. `init` produced the opposite — one flat `layer: feature` draft per
source file, no `level:`, no `satisfies:`. The maintainer's objection is the right one:
*a flat field with stones is not what the tool is for.*

ADR-0019 forbade the engine inferring the axis. That was decided when nothing had tried,
and it is the sentence this record reverses.

## What is actually inferable, measured

The three rungs are not equally knowable from source, and pretending otherwise is how a
fake pyramid gets built:

| rung | inferable from code? |
|---|---|
| `code` | **Yes, with certainty.** A draft extracted from a source file describes that file's behaviour. That *is* the code rung. |
| `architecture` | **Only structurally.** The best available signal is the directory. |
| `system` | **No.** A stakeholder need is not in the source. Nothing in a repository says why a user wants the thing. |

Directory inference, run on this repo before deciding, would mint capabilities named
`scripts`, `app/src/lib`, `app/src/views`, `app/scripts` and `check` — ten of them. None
of those is a capability. That output is not a pyramid; it is the same flat field with the
stones stacked three high and mislabelled, which is worse than leaving them lying down,
because it looks like structure.

## Decision

The engine drafts all three rungs, and every rung it invents says so.

1. **`code` is asserted.** Every requirement `init` extracts from a source file
   carries `level: code`. This is not a guess.
2. **`architecture` is proposed.** One `draft` ARCH requirement per source directory that
   holds code, named from the directory, with each file-level draft in it declaring
   `satisfies:` that node.
3. **`system` is a named hole.** One `layer: need` placeholder that every ARCH draft
   satisfies, whose title says it needs a human. The engine never guesses a need.
4. **Everything the engine writes about the axis is marked.** Each such requirement
   carries `level_source: auto`, the parallel of the existing `owner: auto`. A rung a
   human decided carries nothing, and the two are then distinguishable forever.
5. **Nothing is enforced.** Every node the engine mints is `status: draft`, which the gate
   never enforces (ADR-0019's warn-only posture is untouched). The corpus reaches
   `confirmed` only through the triage the skill already documents.

## Why this answers the audit rather than overriding it

Three senators blocked automatic assignment. Each objection is met on its own terms:

- **Aurelius — irreversible × critical, it writes a field into every consumer's files.**
  It still does. What changes is that every written field is `status: draft` and carries
  `level_source: auto`, so the write is visibly provisional and mechanically reversible:
  deleting every requirement with `level_source: auto` restores the previous corpus
  exactly.
- **Dimon — an auto level is indistinguishable from a human one to `LINT_FANOUT_BANDS`
  and `LEVEL_TEST_PAIR`.** That was true and is the reason `level_source: auto` exists.
- **Musk and Aristotel — a file is not a rung, and inventing SYS nodes from source is the
  "AI invents requirements" failure.** Agreed, which is why the engine asserts only the
  rung it can know, proposes the one it can only guess, and refuses to guess the need at
  all — it mints a placeholder that says so in its own title.

**Deming's STOP is not answered and is recorded unanswered.** The claim that the
three-level model helps is still calibrated on one corpus — this one. This record does not
pretend otherwise; it changes what `init` produces, not what is known about whether the
shape pays.

## Consequences

- A consumer running `init` gets a pyramid whose base course is correct, whose middle is a
  named guess, and whose apex is an explicit hole. That is a starting point for the
  Core/Emergent/Accidental triage the skill already describes, not a finished corpus.
- The directory-derived ARCH names will often be wrong. That is expected and visible:
  `status: draft`, `owner: auto`, `level_source: auto`. Renaming and merging them is the
  author's first task, and it is the task the tool exists to make possible.
- `_corpus_shape` will report a populated pyramid where it used to report `flat`. Its
  per-rung counts still tell a reader what is real, and a corpus that is `1 system / 10
  architecture / 400 code` with every node `owner: auto` reads as untriaged, not as done.

## Revisit when

- **The auto ARCH names are kept rather than rewritten.** If, on a repo that has triaged,
  more than half the ARCH nodes still carry their directory-derived name and `owner: auto`,
  the proposal is not being read — it is being accepted by inertia, which is worse than a
  flat corpus. Measure with `grep -l 'owner: auto' requirements/*.md` against the ARCH set.
- **ADR-0019's own 2027-03-03 review still stands** and now has a different question to
  answer: not "does any consumer set the field", which this record makes automatic and
  therefore uninformative, but "does any consumer keep what the engine proposed".
