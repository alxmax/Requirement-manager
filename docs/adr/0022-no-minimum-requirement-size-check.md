# ADR-0022 — No minimum-size check; and no lint ships without both halves of its bar

- **Status:** Accepted (the check is **Rejected**; the launch discipline is **Adopted**)
- **Decided:** 2026-09-03
- **Evidence:** nine-senator audit `runs/senate/2026-09-03_143319-senate-reqmap-min-requirement-size.json`
  (2 rounds, GO 3 · MODIFY 3 · STOP 3, three senators reversing to STOP after the
  between-round measurement); execution against this repo's live corpus, reproduced below;
  [ADR-0016](0016-no-edge-case-marker.md); [ADR-0012](0012-internal-consistency-lint-rejected.md);
  [ADR-0020](0020-redundancy-signal-below-the-fire-rate-bar.md); [ADR-0021](0021-corpus-grows-only-by-design.md)

## Context

Decomposing the architecture requirements into detailed design produced 575 code-level
leaves, and the split was made by **sentence**, not by failure mode. An enumeration
therefore became one requirement per list element. The whole contract of `REQ-TESTLINK-741`
is four words — "A Rust `#[test]` counts." — one arm of its parent's list of what counts as
a test function. The behaviour is one; it became six-plus requirements.

The proposal was to stop that mechanically: a warn-only `lint` check flagging any
requirement whose Contract holds fewer than N words, with N somewhere near 10–12.

## The measurement that killed it

**The fire rate was computed over the wrong population.** The proposal reported 14% at
N=10 and 24% at N=12, both inside [ADR-0016](0016-no-edge-case-marker.md)'s 5–40% band.
Those figures cover all 575 leaves. But `cmd_lint` filters its targets to `LINT_STATUSES`,
which excludes `draft`, and every one of the 575 leaves is a draft. ADR-0016's own wording
settles the denominator — it requires a predicate that

> fires on **5–40%** of confirmed requirements **and** at least **8 of 10** sampled flags
> are confirmed real gaps by a human reader

Measured over the 72 requirements `lint` actually visits, the floor fires on **1** —
**1.4%**, and identically at N = 8, 10, 12, 15 and 20. It is below the floor at every
candidate threshold, so no choice of N rescues it.

**Day-one precision is 0/1.** The single flag is `REQ-PROMOTE-567`, whose complete contract
is "`confirm <ID>` sets the requirement's `status` to `confirmed`." — eight words, correct,
and complete. Against a bar of ≥8/10 confirmed real, the check's only finding is a false
positive.

**"Contract" has two live senses, and they disagree by everything.** On the atomic form the
`_bullets` reading gives a median of 16 words and fires on 140 leaves at N=12; the
`_atomic_spans` reading — the span `binding_hash` itself treats as the contract — gives a
median of 53 and fires on **zero**, even at N=25. Any headline number is a choice of
reading, not a measurement. ADR-0016 had already named this hazard: "the two counts differ
because *contract clause* already has two senses in the engine."

**The obvious implementation is blind to the target.** `_contract_clauses`, which the
existing `statement-size` loop iterates, returns `[]` for **575 of 575** atomic leaves.
Extending that loop — the DRY-looking option — would fire on none of them.

**Short is not the same as fragmentary.** Within the very family used to motivate the
proposal, a 12-word floor *misses* three real enumeration elements (`REQ-TESTLINK-742` at
26 words, `-744` at 16, `-743` at 13) and *hits* two clauses that are not
(`REQ-TESTLINK-736`, `-746`). A check that misses three of the seven members of its own
motivating example is not measuring the defect.

## Decision

**Ship no minimum-size check.** Not at any threshold, not in `lint`, not read-only in
`next`. The proxy does not track the defect, and the defect is a judgement — the same
conclusion [ADR-0021](0021-corpus-grows-only-by-design.md) reached one day earlier when it
kept the `ac-count-low` atomic exemption on the ground that thinness in the atomic form is
correct specification, not a defect.

**Put the rule where judgement lives.** The skill contract now states that a clause earns
its own requirement only when it names a behavior that can fail on its own, and names the
three shapes that never do — an enumeration element, an attribute, a rationale. The test is
to try to write the `Then`: if the observable only repeats the clause, the clause is not a
capability. That is not mechanisable, which is precisely why it is doctrine and not code.

**Adopt `fan-out`'s launch discipline as a standing rule.** From here on, no lint check
ships without publishing **both** halves of ADR-0016's bar in its CHANGELOG entry or ADR: a
fire rate **and** a human-confirmation sample of its own findings.

The record is one-directional and has no exception:

| check | published at launch | exemptions today |
|---|---|---|
| `fan-out` | fire rate **and** 7/7 confirmed real | **0** |
| `redundant-modal` | 17 hits, no sample — all 17 later fixed as real | 0 |
| `statement-size` | fire rate only (0 of 599 clauses) — never fired; threshold later widened 75→150 | 0 |
| `long-sentence` | neither | deleted after ~3 months, having reported 0 corpus-wide for its whole life |
| `ac-count-high` | neither | **6** |
| `file-spread` | neither | **4** |
| `over-scoped` | neither | 1 |
| `ac-count-low` | neither | 1 |

Every check carrying an exemption launched without a confirmation sample. The one check
that published both halves carries none. Verified 2026-09-03: 9 requirements carry
`lint_exempt`, 12 instances across exactly those four checks, and the count per release tag
runs 4 (`v2.14.0`) → 5 → 6 → 8 → 9 (`v2.29.3`), flat at 9 since.

The sharpest single figure is `ac-count-high`, the nearest relative of the rejected
proposal — a structural count with a threshold, launched with no sample. It is **0.0%
post-exempt**: six of 70 non-draft requirements exceed `LINT_AC_MAX`, and all six are
deliberately exempt. Every live finding it has ever produced was judged a false positive by
its own author.

## Consequences

- The 575 leaves are cleaned by hand, by the pass already in flight, not by a check. That
  pass has merged 46 attribute-clauses into the behaviours they qualify and given 551
  leaves a real observable.
- A future minimum-size proposal has a precondition: `_contract_clauses` must first learn
  the atomic form, or every number quoted for such a check describes the 72 requirements it
  is not aimed at.
- The launch discipline applies to this repo's own future checks and is the standing answer
  to "why was that check exempted everywhere" — it was shipped without ever being confirmed
  against a human reader.
- This is the fifth corpus-shape check this repo has considered and the fifth that did not
  ship as an enforcing check ([ADR-0012](0012-internal-consistency-lint-rejected.md), the
  rejected coverage gate, roadmap coherence, [ADR-0016](0016-no-edge-case-marker.md), and
  now this). `fan-out` remains the existence proof that the bar is passable.

## Revisit when

- A corpus — this one or a consumer's — shows a **confirmed** requirement that is genuinely
  fragmentary rather than terse, and a human confirms ≥8 of 10 such flags. Until such a
  sample exists, the proxy has never been shown to track anything.
- `_contract_clauses` gains atomic-form support, at which point the measurement can at last
  be taken on the population that motivated it.
- A check ships in violation of the launch discipline above and later accumulates
  exemptions — that would confirm the rule by the cost of ignoring it, and the trajectory
  table should be re-measured and appended here.
