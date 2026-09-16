---
id: ARCH-DOCCLAIMS-071
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v7.15
depends_on: [ARCH-CHECK-006, ARCH-CONFIG-060]
satisfies: [SYS-GATE-102]
---

# Corpus counts a document states about itself

## Description
> A prose document that says "236 requirements in total" is asserting something the engine
> can count, and nothing was counting it. This repository's own `CLAUDE.md` — the file every
> contributor and every agent reads first — drifted to four wrong counts while the gate
> reported zero errors: 68 architecture requirements against 63, 159 code against 191, 236
> total against 263, and 197-in-71-files against 263-in-72. That is the exact failure this
> tool exists to prevent, sitting in the tool's own front page. An external audit found it
> before any check did.

Every bullet below is binding.
- A number a document marks as a corpus count is re-measured against the live corpus, and the gate warns when the two disagree. [[REQ-DOCCLAIMS-1012]]
- The rule is opt-in in two independent ways — a document with no marker yields nothing, and `DOC_CLAIM_FILES` names which documents are read — so a repository that wants none of it is untouched. [[REQ-DOCCLAIMS-1012]]

## Cases
CASE-1
  Given  a document marking a corpus count that disagrees with the corpus
  When   `gate` runs
  Then   it warns naming the document, the line, the stated number and the measured one,
         and the exit code is unchanged

CASE-2
  Given  a repository whose documents carry no marker
  When   `gate` runs
  Then   no finding is produced and the run is byte-identical to one from before this
         requirement existed

CASE-3
  Given  a stale marked count in a document `DOC_CLAIM_FILES` does not name
  When   `gate` runs
  Then   no finding is produced for it

## Context
**Terms**
- *marked claim*: a `<!--reqmap:KIND-->` comment in prose, followed by the integer it
  claims. The marker leads the number rather than trailing it so the sentence still reads
  as prose.

**Notes**
- Warn, never error. A sentence that has fallen behind is a documentation defect; the
  gate's errors are reserved for link integrity, and `.githooks/pre-commit` runs the gate
  on every commit. An error here would block every commit that adds a requirement until
  its author re-edited a paragraph, which is a tax on the repository's most common edit.
- The counterpart to warn-only is that this repository ALSO asserts its own numbers in
  `DocsAreTrue`, where a wrong one fails CI. The rule is the portable half and the test is
  the binding half: a warn in a stream of thirty-odd warnings is detection in principle,
  and this repository needs detection in practice.
- Opt-in was chosen over a default-on prose scan because a regex over arbitrary prose
  cannot tell a live count from a historical one. `CLAUDE.md` line 130 states both in the
  same paragraph — "263 requirements in total" is live, "the 573 one-sentence atomic leaves
  were folded into 126 groups" is a true statement about a past morning. Only the author
  knows which is which, and the marker is how they say so.
- `files` counts distinct requirement files through the parser, never a directory glob.
  A glob over `requirements/*.md` returns 75 against a real 72, because `_map.md`,
  `_findings.md` and `_ai_review.md` live there and hold no requirement — the first draft
  of this very requirement was written from the glob number and was wrong.

**Current implementation**
- `reqmap_engine/docclaims.py`, wired into the gate as RM035 by an import in `gate.py`.
- `DOC_CLAIM_FILES` in `reqmap_engine/config.py`, listed in `CONFIG_KEYS`.

**Links**
- Sibling: [[ARCH-SELFGATE-039]] (the other half of "the document stopped describing the code").


--------------------


---
id: REQ-DOCCLAIMS-1012
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.15
satisfies: [ARCH-DOCCLAIMS-071]
---

# Re-measuring a marked claim

## Description
> The check is worth having only if it cannot quietly check nothing. Two ways it could:
> a marker naming a kind the engine does not count, and a number measured with the wrong
> instrument. The first is reported rather than skipped; the second is why `files` goes
> through the parser and never through a directory glob.

Every bullet below is binding.
- `corpus_counts` returns `total`, `files`, and one `level:<value>` / `layer:<value>` entry
  per value present in the corpus, with `files` counting distinct requirement file names as
  the parser reports them.
- `doc_claims` returns the kind, the claimed integer and the line number of every
  `<!--reqmap:KIND-->` marker in a document, in source order.
- A marked claim whose measured value differs produces one warning naming the document, the
  line, the claimed number and the measured number.
- A marker naming a kind the engine cannot count produces one warning listing the kinds it
  can, rather than being skipped in silence.
- A known axis with no members measures zero, so a claim of zero on an undeclared rung is
  compared rather than reported as unknown.
- A document named in `DOC_CLAIM_FILES` that cannot be opened or decoded is skipped without
  a finding, and the rule never changes the exit code.

## Cases
CASE-1 — a stale number warns
  Given  a document containing `<!--reqmap:total-->5` and a corpus of 3 requirements
  When   the gate rules run
  Then   exactly one RM035 warning names both 5 and 3

CASE-2 — a current number is silent
  Given  that same document stating 3
  When   the gate rules run
  Then   no RM035 finding is produced

CASE-3 — an unknown kind is named, not skipped
  Given  a document containing `<!--reqmap:totl-->3`
  When   the gate rules run
  Then   one RM035 warning says the kind is unknown and lists the kinds the engine counts

CASE-4 — no marker, no work
  Given  a document carrying no `<!--reqmap:` marker
  When   the gate rules run
  Then   no RM035 finding is produced

CASE-5 — the file count is the parser's, not the glob's
  Given  a requirements directory holding two requirement files and a generated `_map.md`
  When   `corpus_counts` runs
  Then   its `files` value is 2

## Context
**Notes**
- The marker leads the number and the extractor takes the first integer within a short
  span after it, so `<!--reqmap:level:code-->191 code` reads as an ordinary sentence and a
  second number later in the same line cannot be captured by mistake.
- `level:` and `layer:` values are read from the corpus rather than from a fixed list, so a
  repository using its own vocabulary needs no engine change to mark its counts.
