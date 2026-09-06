# ADR-0031 — A corpus that was already tagged can be given the rungs

- **Status:** Accepted. Extends [ADR-0030](0030-the-engine-drafts-the-pyramid.md) rather
  than reversing it: 0030's rule that the engine may propose a rung, marked
  `level_source: auto`, for the author to correct, stands unchanged. What changes is
  *where* it may do so.
- **Decided:** 2026-09-06 (`ARCH-LEVELRETROFIT-066`, `ARCH-LEVEL-051`, `ARCH-CLARIFY-062`)
- **Where:** `clarify --levels`, read-only; `--apply` writes. Reachable from no command
  the pre-commit hook runs.

## Context

ADR-0030 scoped itself to `init` only, and that scope had a consequence nobody measured
at the time: `init` writes the code rung only onto a requirement it **extracted from an
untagged source file**, and it mints the architecture and system rungs *from those
drafts*. `by_dir` is populated inside the per-file draft loop, and `_write_arch_drafts`
runs after it, so an empty `by_dir` writes no architecture draft and
`_write_sys_placeholder`, fed those ids, writes nothing either.

A repository whose files already carry membership tags therefore proposes zero drafts,
and zero drafts is zero pyramid. Its requirements — hand-authored, `confirmed`, written
before the axis existed — had no command that could give them the axis at all. Adopting
it there meant editing every requirement file by hand.

That is a gap in the tool, not a preference of the repository. It also distorts the
evidence [ADR-0019](0019-v-model-left-arm-adopted.md) will read at its **2027-03-03**
review, whose criterion is "the level fields stay unused by any consumer repo after six
months → remove rather than document harder". Non-use that is *structural* is evidence
of a missing retrofit path, not of a missing reader, and counting it as the latter would
retire a field for the wrong reason.

## Decision

A second, explicit place where the engine may propose a rung: `clarify --levels`.

- It proposes one rung per requirement that **declares none**, and never overrules an
  author who declared one.
- It prints the reason beside every proposal, so a reader disagrees with a sentence
  rather than with the run.
- It writes nothing without `--apply`, and every write is marked `level_source: auto`.
- It proposes `code` only on evidence — an `implements:` member, at least `LINT_AC_MIN`
  labelled cases, and at least one of those cases linked to a test — because `code` is
  the rung an author reaches by *decomposing* a capability, not by renaming one.
- It never proposes or writes a `satisfies:` edge. `satisfies:` is the level axis and
  `depends_on` is the composition axis; deriving one from the other is the conflation
  the engine refuses to make everywhere else.

## Why not on `sync`

`sync` is the obvious host and the wrong one. The shipped pre-commit hook runs it on
every commit, which makes it the most automatic placement in the tool — and this is a
write into files a human authored. A retrofit belongs behind a flag somebody types.

`clarify` is the right host on its own terms: it exists to ask what a requirement has
not answered yet, and `--decompose` is already its write half. "Which rung is this?" is
the same kind of question.

## What is weaker here than in ADR-0030, and stays weaker

ADR-0030's reversibility is clean: the whole file was written by the engine, so deleting
it restores the corpus exactly. This one adds two lines — `level:` and
`level_source: auto` — to a file a human wrote. Deleting both restores the reading, but
the file was touched. That difference is the entire reason the write is opt-in, printed
before it happens, and marked with who wrote it.

The rung is inferred from **shape**, and shape is not intent. A `layer: need` really does
say "stakeholder need", and a requirement with cases, code and a test link really is
shaped like one behaviour group — but neither fact knows what the requirement is *for*.
The output says so in its own last sentence.

## Revisit

- **Nobody runs it within six months** — review on **2027-03-06**. A retrofit for a
  migration that no consumer performs is a command with no caller, and should be deleted
  rather than kept for symmetry.
- **A proposal is corrected more often than it is kept.** If authors routinely change the
  rung the engine wrote, the inference is worse than no inference: it anchors a reader on
  a wrong answer. Measure it by counting `level_source: auto` requirements whose rung was
  later edited, not by asking.
