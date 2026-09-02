# ADR-0020 — An exact-duplicate signal ships below ADR-0016's fire-rate bar

- **Status:** Accepted
- **Decided:** 2026-09-03 (`ARCH-REDUNDANCY-058`)
- **Evidence:** measurement over this repo's 690-requirement corpus, reproduced below;
  [ADR-0016](0016-no-edge-case-marker.md); [ADR-0012](0012-internal-consistency-lint-rejected.md)

## Context

The corpus only ever grows. Nothing in the engine ever said "these two requirements describe
the same obligation" — `lint` has a *Granularity* advisory that says one requirement does too
much, and no counterpart saying several do too little between them. Decomposing 59
architecture requirements into 621 detailed-design ones made that visible: the same clause
authored under two parents mints two requirements for one obligation.

[ADR-0016](0016-no-edge-case-marker.md) set this repo's bar for a new check — a **5–40% fire
rate** and **≥8/10 findings a human confirms** — after
[ADR-0012](0012-internal-consistency-lint-rejected.md) rejected an internal-consistency lint
measured at 78.6% false positives. A new signal has to answer to that bar or say why not.

## The measurement

Five candidate signals, over 690 requirements (60 architecture carrying 264 `implements`
tags, 621 detailed-design, 9 system):

| signal | fires | requirements involved |
|---|---|---|
| identical member sets | 0 pairs | 0% |
| one requirement's members ⊂ another's | 1 pair | 3.3% of the 60 with members |
| **contract text identical** | **6 groups** | **12 (1.7%)** |
| contract cosine ≥ 0.70 (`dupes`) | 34 pairs | 7.8% |
| contract cosine ≥ 0.50 (`dupes`) | 226 pairs | 38.7% |

All six exact-match groups are real. One example, whole:

> `show` prints the verification level beside a member whose `tested-by:` tag carries one.

authored in both `ARCH-SHOW-015` and `ARCH-VLEVEL-037`, so decomposition produced
`REQ-SHOW-683` and `REQ-VLEVEL-819` for a single obligation.

## Decision

Ship the **exact-match** signal — identical Description clauses once case and whitespace are
normalised — reported by `sync` and as a `next` bucket. It writes nothing, and `gate` says
nothing about it.

**This is below ADR-0016's 5% floor, deliberately.** That floor exists to reject checks that
are noisy or dead — a check nobody's corpus ever trips has no reader, and one that trips on
correct work costs more than it returns. This signal is neither: it has **zero false positives
by construction** (there is no threshold to be wrong about; the texts are equal or they are
not), and it found six real duplicates on the first corpus it ran against. Precision is the
thing being bought here, not volume. Recording the exception is the point of this record —
the alternative was to quietly widen the check until it cleared a number, which is how ADR-0012's
78.6% happened.

The fuzzy tier stays where it already is: `dupes`, opt-in, thresholded, unchanged. The two are
not rivals — the exact check is the floor beneath it, and the advisory says so.

Placement follows [ADR-0002](0002-error-versus-warning.md) and
[ADR-0014](0014-engine-stays-one-file.md): a corpus-shape observation is read-only and never a
gate. It is in `sync` and not `gate` for a concrete reason — the pre-commit hook runs `gate` on
every commit, and an advisory about corpus shape there is noise on work that is already
correct. `sync` is the moment the corpus was just rewritten, which is exactly when a new
duplicate appears.

Draft placeholders are excluded: every scaffolded requirement carries the same `TODO:` line, so
counting those would report the scaffold as a duplicate of itself hundreds of times and bury
the six real findings.

## Consequences

- `next` now advises in both directions — *Granularity* ("this one does too much") and
  *Redundancy* ("these say the same thing") — which is the first time the tool has had an
  opinion about covering the code with **fewer** requirements rather than more.
- It reports; it does not merge. Folding two requirements into one means moving clauses and
  criteria, deprecating one id, and re-pointing its tags — an edit with judgement in it, and
  the same reason `lint --decompose` writes only under an explicit flag.
- **Six findings stand open in this repo.** They are left that way on purpose: shipping a
  check and silencing its output in the same commit would make it decorative.
- The member-based signals (identical/subset member sets) are measured and **not** shipped.
  At 0 and 1 findings they are genuinely dead here, and unlike the exact-text check there is
  no reason to expect them to fire elsewhere either — a requirement pair tagging exactly the
  same code is rarer than a pair describing the same behaviour.

## Revisit when

- **The exact check reports zero on a corpus that `dupes` shows is full of near-duplicates.**
  That would mean authors paraphrase rather than copy, and exactness is the wrong instrument —
  fold it into `dupes` and drop the separate bucket.
- **The six open findings are resolved and the count returns.** A signal that keeps refilling
  is describing an authoring workflow problem, not a corpus state, and the answer is a `merge`
  command rather than a louder advisory.
