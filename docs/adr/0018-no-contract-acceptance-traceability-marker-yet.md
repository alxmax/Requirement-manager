# ADR-0018 — No Contract-to-Acceptance traceability marker, yet

- **Status:** Rejected (considered, deliberately not built — revisit conditions below)
- **Decided:** 2026-09-02, after a nine-senator Senate audit (`runs/senate/2026-09-02_191837-reqmap-schema-simplify-context-merge-and-traceability.json`, two rounds, verdict MODIFY, 8 MODIFY / 1 GO, all eight blocking)
- **Companion record:** [ADR-0017](0017-consolidated-context-section.md) — the other half of the audited proposal, accepted in modified form
- **Evidence:** measurements below, each reproducible by the command named beside it

## Context

`lint`'s scope checks (`ac-count-low`/`ac-count-high`/`over-scoped`, see `REQ-LINTCHECKS-025`)
compare the **count** of Contract clauses against the count of Acceptance criteria. None of
them verify that clause *i* and criterion *j* actually correspond — a requirement can carry
five Contract clauses and five ACs where AC-1 through AC-5 all re-test clause 1 while clauses
2–5 are never exercised, and every existing check reports it clean.

The audited proposal (`REQ-...` Part B, not built) closed that gap with an inline anchor on
each Contract clause (`{#C<n>}`) and a `covers: C<n>[,C<m>...]` line on each `AC-<n>` block,
checked by a new warn-only, opt-in `uncovered-clause` lint finding.

## Decision

Do not build it. Three independent findings decided it, the first two by direct analogy to
this repo's own settled record and the third a code-verified bug in the proposed syntax:

1. **This is the third attempt at a mechanism this repo has already rejected twice**, and
   the proposal cited neither precedent:
   - [ADR-0012](0012-internal-consistency-lint-rejected.md) rejected a warn-only lint using
     a syntactic proxy for a semantic property (a declared link standing in for the property
     it claims) after measuring a **78.6% false-positive rate** on this repo's own corpus.
     `covers: C<n>` is the same shape: the engine can only verify a label exists, never that
     the AC exercises the clause it names.
   - [ADR-0016](0016-no-edge-case-marker.md), decided **one day before** this proposal,
     rejected a comparable in-requirement-file opt-in marker and measured its closest live
     analogue (`verifiable by:`) at **2/51 (~4%) adoption** — versus `# verifies:` (a
     different mechanism, living in the *test* file the author is already editing) at
     **12/51 (~23.5%)**, independently re-measured for this decision
     (`grep -l "verifiable by" plugin/requirements/*.md`; distinct `# verifies: <ID>#AC-N`
     target ids across `.py` sources, excluding `test_reqmap.py`'s own fixture ids).
   - The 6x adoption gap has a causal explanation that applies directly here: a marker in a
     file the author is *already* editing (a test, for `# verifies:`) gets adopted; a marker
     requiring a *separate* deliberate edit to the requirement file (`verifiable by:`,
     and `{#C<n>}`/`covers:` by construction) does not. ADR-0016's finding 2 applies
     verbatim: *"a count that is wrong in the reassuring direction is worse than no count."*
2. **No pre-ship measurement was offered**, and this repo has one on record for exactly this
   family: ADR-0016's revisit bar (A) requires a dry run of the *final* predicate firing on
   **5–40%** of confirmed requirements with **≥8 of 10** sampled flags confirmed real gaps by
   a human reader. The rejected ADR-0012 mechanism was *already* warn-only, so "ship it
   warn-only" is not an exemption from that bar — it is the shape of the thing the bar
   exists to gate.
3. **The proposed marker syntax reproduces a bug this repo already fixed once.** ADR-0016
   §3 requires any future marker to be an HTML comment on the label (as `verifiable by:` is),
   because `_acc_blocks`'s label parser (`_AC_LABEL_RE` in `reqmap.py`) strips only HTML
   comments from acceptance-criterion text — a bracket/brace suffix survives and leaks into
   `acc` and the viewer's rendered `accept`/`gwt`, the exact representation-desync class of
   `REQ-VIEWER-007` AC-8 (fixed in v2.29.2). `{#C<n>}` is a brace suffix, not an HTML
   comment, and was verified this round to leak exactly that way.

## Consequences

- No change to `reqmap.py`, the requirement template, `lint`, or any requirement file for
  this decision. No `{#C<n>}`/`covers:` syntax, no `uncovered-clause` check.
- The gap this proposal named is real and stays open: `lint`'s scope checks remain
  count-based, not correspondence-based.
- Authors who want per-clause traceability today have one working, adopted mechanism:
  `# verifies: <ID>#AC-N` in the test file (`REQ-ACVERIFY-019`), which this decision does
  not touch.

## Revisit when

Any one of these, each a number rather than an appeal — mirroring ADR-0016's format because
this is the same family of decision:

- A dry run of the *final* predicate (marker form fixed per the point below) against this
  repo's own 51 confirmed requirements fires on **5–40%** of them, **and** at least **8 of
  10** sampled flags are confirmed real untested-clause gaps by a human reader.
- The marker form is changed to an HTML comment on the `AC-N` label, from a closed word list
  (mirroring `verifiable by:`'s form), with a unit test proving `_acc_blocks`'s parsed
  `text` never contains the raw marker — closing finding 3 above before finding 1 or 2 is
  even attempted.
- A recorded real incident where a shipped defect traces to an Acceptance criterion that
  falsely appeared to cover a Contract clause it did not exercise — one incident is one
  short of the "two beats one" bar ADR-0012 set; a second such incident (after this one)
  meets it.
