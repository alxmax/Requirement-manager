---
id: REQ-INTCONSISTLINT-028
status: draft
layer: feature
owner: Alex
priority: could-have
depends_on: [REQ-LINT-014, REQ-MEMBERDRIFT-027]
superseded_by:
milestone: v1.19
---

# Internal-consistency lint (deferred — redesign required)

> When a requirement's structured frontmatter moves to a new model (a `depends_on`
> edge added, a number changed) but its prose Contract/AC still describe the old one,
> the requirement contradicts itself. The contract hash misses this (it hashes the prose
> body only, not the frontmatter), and reverse member drift (REQ-MEMBERDRIFT-027) misses
> it too (it compares member files, not a requirement's own frontmatter-vs-prose). So the
> gap is real — but the obvious detector is not. This requirement parks the intent with a
> design brief, deliberately unimplemented, until a detector that actually works exists.

## WHY — Deferred, not dropped (Senate 2026-06-19)
A two-round Senate audit (`runs/senate/2026-06-19_224727-reqmap-item4-internal-consistency-lint.json`)
rejected the proposed implementations and deferred the intent:
- The naive check "warn when a `depends_on` id is not a literal substring of the prose
  body" is **empirically refuted**: on this repo's own corpus 22/28 (78.6%) of
  requirements with `depends_on` do not cite the id in prose yet are correctly authored
  (the convention is frontmatter-only deps, referenced in prose by capability name or
  `[[wikilink]]`). It would warn on ~79% of correct requirements — alarm fatigue.
- That same check would **not have caught the motivating incident**
  (CONSILIUM-MODE-TRIAS-001): there a `depends_on` edge was *added* that contradicted the
  prose; the id was not *absent*.
- The full "prose asserts the old number/model" detector needs NLP, which the stdlib
  engine deliberately avoids (see REQ-LINT-014 notes).

## WHAT — Verify intent (open questions for the human — must be resolved before confirming)
- A viable detector is **baseline-aware**, not static: flag when a `depends_on` edge is
  present now but absent from a recorded baseline AND the requirement's contract body hash
  did not change in the same revision (the TRIAS shape: structure moved, prose did not).
- Does a per-requirement `depends_on` baseline exist? `_reqlock.json` stores only the
  contract body hash today, so this likely needs a new persisted field/sidecar — i.e. a
  schema change, not a lint addition. Decide the storage (extend `_memberlock.json`?).
- Acceptance bar before promotion out of draft: a test fixture that reproduces the TRIAS
  incident must fire, AND the measured false-positive rate on the existing corpus must be
  below the existing warn-check baseline (target < 10%).
- Confirm the base rate is worth it: the motivating evidence is n=1; a second real
  occurrence would justify the persisted-baseline cost.

## WHAT — Notes & known limitations (informative)
- Intentionally has no `implements:`/`tested-by:` members while `draft` — it ships no code.
- Distinct from REQ-MEMBERDRIFT-027 (member-file content) and from contract drift
  (prose body hash): this targets a requirement's own frontmatter-vs-prose coherence.

## HOW — Acceptance (= tests)
- None yet — draft. Acceptance is gated on the open questions above being resolved into a
  detector whose corpus false-positive rate is measured below threshold.

## WHERE — Current implementation
- None (deferred). Future home: a baseline-aware check in `lint`/`cmd_check`.

## Links
- Used by: (auto)
## Members in code (auto)
