# ADR-0015 — A requirement covered by its dependencies is a declared layer, not an inference

- **Status:** Accepted
- **Decided:** 2026-08-31, from a consumer session on a 55-requirement corpus (plugin v2.28.1)
- **Evidence:** `TODO-feedback-management-dashboard.md` §6, §6b, §6c — reproduced against
  `plugin/requirements/` and the four exemption sites in `reqmap.py`

## Context

A real requirement in a consumer corpus — the MVP acceptance criterion, `depends_on` of twelve
other requirements — **has no code of its own, and should not have any**. Its implementation is
the union of its dependencies' implementations; it asserts that twelve capabilities work
together. `confirm` refused to promote it:

```
refusing: REQ-DOC-ACCEPTANCE-079 has no `implements:` member —
a confirmed requirement must point to code.
```

Every escape hatch the model offered was the wrong shape:

- `layer: bus` (what the author had reached for) is **defined by fan-in** — "foundation,
  high fan-in". The requirement's fan-in/fan-out was `0 / 12`; every genuine bus in that
  corpus measured 6–8 in, ~0 out. It is the exact inverse: a roof labelled a foundation.
- `layer: need` has the right exemption but the wrong direction — a need is covered by
  `satisfies:` edges its satisfiers declare **upward, in their own frontmatter**. Modelling
  the aggregate that way means editing twelve files to re-declare, backwards, a relation
  already written once in the aggregate's own `depends_on`.
- `test_exempt:` silences the *untested* signal, not the missing-`implements` one.

The obvious cheap fix — "treat any requirement with a non-empty `depends_on` and no
`implements:` as covered" — was rejected. It is an inference, and it disarms the gate's most
valuable error for a population nobody enumerated: every genuinely orphaned requirement that
happens to list a dependency stops being reported, silently, in every consumer repo at once.

A second, smaller defect surfaced with it: of the four places that decide whether a
requirement needs an `implements:` member, three exempted `layer: need` and `cmd_promote` did
not. This repo's own `NEED-SSOT-001` is `confirmed` only because the file was hand-edited
around the command that exists to promote it.

## Decision

Add a fourth layer, `aggregate`, declared by the author, exempt from the implements check the
same way `need` is — and route all four decision sites through one predicate, `_impl_exempt`.

- `aggregate` is covered **downward**, by its own `depends_on` edges; `need` is covered
  **upward**, by `satisfies:` edges. Same exemption, opposite direction.
- The exemption is not a hole: `confirm` refuses an `aggregate` with an empty `depends_on`,
  which is precisely the orphan the original refusal existed to catch, and the gate already
  errors on a dangling `depends_on` target.
- A new `layer-mismatch` lint warns on a `layer: bus` with zero dependents and three or more
  dependencies — the shape that produced this record. This repo's corpus has no such
  requirement and a maximum fan-out of three, so the check is silent here and fires on the
  case that motivated it.

## Consequences

- The relation is written once, in the aggregate's own frontmatter, and read by the gate,
  `health`, the risk map and `confirm` alike.
- A requirement with no code still errors by default. Exemption requires a deliberate word in
  the file, which a reviewer sees in the diff — an inference would have been invisible.
- `VALID_LAYER` grows, so an older vendored engine reading a newer corpus warns on an unknown
  layer. That is the intended failure: it names the version skew instead of silently
  mis-modelling the requirement.
- The viewer must stop labelling every exempt requirement "test-exempt — skipped by the gate".
  Three different reasons (deprecated, `test_exempt:`, covered-by-edge) now need three labels.

## Revisit when

An `aggregate` accumulates code of its own — that means it grew behaviour and should become a
`feature`. Or: the `layer-mismatch` lint fires on a corpus where `bus` with zero fan-in is
legitimate, which would mean fan-in is the wrong definition of `bus`, not that the check is
wrong.
