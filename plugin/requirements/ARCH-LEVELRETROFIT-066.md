---
id: ARCH-LEVELRETROFIT-066
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v5.13
depends_on: [ARCH-PARSE-001, ARCH-LEVEL-051]
satisfies: [SYS-VMODEL-107]
---

# Giving an existing corpus the three rungs

## Description
> `init` writes the V-model rungs only onto requirements it EXTRACTED from untagged
> source files, and it mints the architecture and system rungs from those drafts. A
> repository whose files already carry membership tags proposes no drafts, so it gets
> no rungs — and its requirements, written by hand before the axis existed, had no
> command that could give it to them. Adopting the axis there meant editing every file
> by hand, which is another way of saying it did not happen.

Every bullet below is binding.
- `clarify --levels` proposes one rung for each requirement that declares none, from the requirement's own shape, and prints the reason beside every proposal. [[REQ-LEVELRETROFIT-985]]
- `--apply` writes the proposal into the requirement's frontmatter, marked `level_source: auto`, preserving the file's line endings and every sibling requirement in a module file. [[REQ-LEVELRETROFIT-986]]
- The run is read-only without `--apply`, reports what it refuses to infer, and is reachable from no command the pre-commit hook runs. [[REQ-LEVELRETROFIT-987]]

## Cases
CASE-1
  Given  a corpus in which no requirement declares a `level:`
  When   `clarify --levels` runs
  Then   every requirement receives a proposed rung with the reason for it

CASE-2
  Given  the same corpus and `--apply`
  When   the run finishes
  Then   each requirement's frontmatter carries the rung and `level_source: auto`

CASE-3
  Given  a corpus in which every requirement already declares a rung
  When   `clarify --levels` runs
  Then   it proposes nothing and says so

## Context
**Notes**
- The rung is inferred from shape, and shape is not intent. Every proposal is printed
  with what it was based on so a reader can disagree with a specific sentence rather
  than with the whole run, and the marker `level_source: auto` keeps the write visibly
  provisional — the same marker ADR-0030 uses, for the same reason.
- ADR-0030's reversibility is cleaner than this one and the difference is worth naming:
  there the whole FILE was written by the engine, so deleting it restores the corpus.
  Here two lines are added to a file a human wrote. That is why the write is opt-in
  behind a flag rather than part of any run that happens on its own.

**Current implementation**
- `plugin/scripts/reqmap.py` — `_propose_levels`, `_insert_frontmatter_level`,
  `_apply_level`, `cmd_levels`.


--------------------


---
id: REQ-LEVELRETROFIT-985
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-LEVELRETROFIT-066]
---

# Which rung, and on what evidence

## Description
> Two of the three rungs can be read off the layer. The third is read off the shape: a
> requirement bound to code is one behaviour group — the `code` rung — unless the engine
> has evidence it is a GROUP of them (bold contract groups, or an over-scope exemption),
> in which case it is an `architecture` awaiting decomposition. The evidence is printed
> next to every proposal (ADR-0038).

Every bullet below is binding.
- A requirement that already declares a `level:` is absent from the proposal: the run
  proposes onto silence and never overrules an author.
- `layer: need` proposes `system`, and `layer: aggregate` proposes `architecture`,
  because each layer already states the thing the rung would say.
- A requirement with two or more contract groups, or a `lint_exempt: [over-scoped]` /
  `[ac-count-high]` entry, proposes `architecture`, and the reason names
  `clarify <id> --decompose --apply` as the way to its code rung.
- Every other requirement proposes `code`: one behaviour group, and the reason states
  its case count, linked cases and implementing members so an under-specified one is
  visible without being moved up a rung.
- Each proposal carries the sentence it was based on, so a reader can disagree with one
  requirement instead of the whole run.

## Cases
CASE-1 — the layer answers it where the layer already said so
  Given  a requirement with `layer: need` and one with `layer: aggregate`, neither
         declaring a `level:`
  When   the proposal runs
  Then   the first is proposed `system` and the second `architecture`, each naming its
         layer as the reason

CASE-2 — a group is proposed `architecture`, everything bound to code is `code`
  Given  three requirements with no `level:`: one with two bold contract groups, one
         with three labelled cases and an `implements:` member, one with a member and
         no cases
  When   the proposal runs
  Then   the first is proposed `architecture` naming `--decompose`, the other two `code`

CASE-3 — a declared rung is left alone
  Given  a requirement that already declares `level: architecture`
  When   the proposal runs
  Then   it is absent from the result, whatever its shape would otherwise suggest


--------------------


---
id: REQ-LEVELRETROFIT-986
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-LEVELRETROFIT-066]
---

# Writing a rung into a file somebody else wrote

## Description
> The file being edited was authored by a human, is `confirmed`, and may hold several
> requirements. Two hazards follow, and they are the same two `_apply_status` already
> handles: rewriting a module file must touch one block and leave its siblings byte for
> byte, and a repository whose files are CRLF must not come back LF. The retrofit
> mirrors that function deliberately rather than inventing a second set of mechanics.

Every bullet below is binding.
- The rung and `level_source: auto` are inserted after `status:`, where the requirement
  template puts the field.
- A file holding several requirements has only the addressed block edited; every
  sibling block is returned unchanged.
- The file's own line endings survive the write, so a CRLF corpus stays CRLF.
- A block with no editable frontmatter, or one that already carries a `level:`, is
  reported as skipped rather than rewritten.

## Cases
CASE-1 — a CRLF file comes back CRLF
  Given  a requirement file whose every line ends CRLF
  When   the rung is written
  Then   the file still has no bare LF, and the two new lines end CRLF as well

CASE-2 — one block of a module file, and only one
  Given  a file holding two requirements, the second of which is addressed
  When   the rung is written
  Then   the second block carries it and the first is unchanged

CASE-3 — nothing to edit is reported, not forced
  Given  a block that already carries a `level:`
  When   the write is attempted
  Then   it reports the block as skipped and leaves the file untouched


--------------------


---
id: REQ-LEVELRETROFIT-987
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-LEVELRETROFIT-066]
---

# Read-only by default, and honest about what it will not do

## Description
> A command that edits every requirement in a corpus is one a reader has to be able to
> run without consequence first. It is also one that must not be reachable from
> anything automatic: the pre-commit hook runs `sync` on every commit, which is the most
> automatic placement in the tool, so the retrofit lives on `clarify` instead. And it
> stops where inference stops — the pyramid's edges come from the ids the author typed, never
> something to be derived from a different axis.

Every bullet below is binding.
- Without `--apply` the run writes nothing and says so, having already printed every
  proposal it would have made.
- The run exits 0 whatever it finds, and no gate rule reads its output.
- `--apply` writes the two upper rungs with the edges (ADR-0038), in `init`'s shape: one
  draft `ARCH-<FAMILY>-001` per id-prefix family of at least `LEVEL_FAMILY_MIN` code
  members (smaller prefixes share `ARCH-NEEDS-A-NAME-001`), `SYS-NEEDS-A-NAME-001` at the
  apex, `satisfies:` from every non-draft code requirement to its family and from every
  placeholder or unlinked architecture requirement to the apex. `depends_on` is never read.
- When a requirement carries contract groups, the run names it and the command that
  builds its code rung (`clarify --decompose --apply`), so the last gap is one command away.

## Cases
CASE-1 — the default run changes nothing on disk
  Given  a corpus with requirements that declare no `level:`
  When   `clarify --levels` runs without `--apply`
  Then   every proposal is printed, no requirement file changes, and the exit code is 0

CASE-2 — the upper rungs and the edges are written with the rungs, in `init`'s shape
  Given  three `JS-*` code-shaped requirements and one `MT4-*` that declare no `satisfies:`, plus a `draft` stub
  When   `clarify --levels --apply` runs
  Then   a draft `ARCH-JS-001` exists and the three point at it;
         the `MT4-*` one points at `ARCH-NEEDS-A-NAME-001`;
         both placeholders satisfy a draft `SYS-NEEDS-A-NAME-001`;
         the stub is unchanged, as is a requirement that already satisfied something;
         a second run writes nothing

CASE-3 — a requirement with contract groups is told which command builds its code rung
  Given  a requirement whose Description carries two bold contract groups
  When   `clarify --levels` runs
  Then   it is proposed `architecture` and the output names `clarify --decompose --apply`
