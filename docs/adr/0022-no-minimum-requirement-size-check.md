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
which excludes `draft`, and 574 of the 575 leaves are drafts (`REQ-PROMOTE-567`, confirmed
at `f7714bb` as the worked example of the standard, is the one exception). ADR-0016's own wording
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
| `fan-out` | fire rate only — the confirmation half was demanded and never taken (see below) | **0** |
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
post-exempt**: six of the 72 non-draft requirements exceed `LINT_AC_MAX`, and all six are
deliberately exempt. Every live finding it has ever produced was judged a false positive by
its own author.

## How the confirmation half is discharged

The bar requires findings "confirmed real gaps by a human reader". Reading ten requirements
from scratch for every proposed check is the cost that makes the rule easy to skip — which
is how four of this repo's checks shipped without it. The discipline below keeps the
confirmation real while making it affordable:

- **An independent reviewer decides.** Not the agent or person who proposed the change. It
  may be an AI: what separated the reliable judgements from the unreliable ones in the
  2026-09-03 audit was not the species of the reviewer but two properties — independence
  from the proposal, and verdicts grounded in executed output rather than reasoning. Three
  senators reversed their own vote that day after running code; the single assertion that
  proved false was the one nobody had measured, and its author retracted it.
- **Every verdict cites what was executed** — a file:line, a command's output, a count —
  not an argument.
- **"False positive" must be a costless answer.** The reviewer is not told which verdict
  ships the change.
- **A person ratifies the batch.** The reviewer's verdicts and evidence go to a human, who
  confirms or refuses. The ratification is what discharges the bar, not the reviewer's
  opinion.
- **The refusal rate is recorded.** If no ratification is ever refused, the step has become
  a rubber stamp and the bar is decorative again — the same failure this ADR documents for
  `ac-count-high`, and detectable the same way: by a number, after the fact.

**This rule has no existence proof yet, and that is stated rather than papered over.**
An earlier draft of this record cited the `fan-out` recalibration as its first successful
application — "a blind reviewer returned 0 of 9 as real". **That claim is withdrawn.** The
number does not reproduce: no commit ever produced nine floor findings (the floor produced
4, then 6, then 7 as the corpus changed), nine was the floor-plus-ceiling total at an
intermediate commit, and the one flag that reading called plausibly real is a *ceiling*
finding that cannot belong to a floor sample. No artifact in the tree records who reviewed
what, so it cannot be repaired — only retracted. The `fan-out` row above is the same story
one rung earlier: [ADR-0019](0019-v-model-left-arm-adopted.md) recorded the band's seven
findings as real on the proposing author's own verdict, while the Senate auditing that very
proposal (`runs/senate/2026-09-02_223252-...`, MODIFY 8–1) had already recorded the
confirmation half as skipped and the sample "pre-failed". It shipped anyway; that run's
outcome row is `OVR`.

So this rule is adopted **prospectively**, binding the next check, with no check yet having
passed it. [ADR-0023](0023-fan-out-per-level-ceilings-no-floor.md) records why the fan-out
recalibration did not need it: dropping a floor can only make a check report *less*, and a
loosening cannot manufacture a false positive for a reader to triage. The first check that
TIGHTENS anything is the one that must produce the sample, and it must commit the verdicts,
the evidence cited for each, the reviewer and the refusal-rate entry — not a summary
sentence. An unauditable confirmation is what this ADR exists to forbid, and its own first
draft is the worked example.

## Consequences

- The 575 leaves are cleaned by hand, by the pass already in flight, not by a check. That
  pass has merged 46 attribute-clauses into the behaviours they qualify and given 546 of
  570 leaves a real observable (measured at `b0ce92b`; the figure moves with the corpus).
- A future minimum-size proposal has a precondition: `_contract_clauses` must first learn
  the atomic form, or every number quoted for such a check describes the 72 requirements it
  is not aimed at.
- The launch discipline applies to this repo's own future checks and is the standing answer
  to "why was that check exempted everywhere" — it was shipped without ever being confirmed
  against a human reader.
- This is the fifth corpus-shape check this repo has considered and the fifth that did not
  ship as an enforcing check ([ADR-0012](0012-internal-consistency-lint-rejected.md), the
  rejected coverage gate, roadmap coherence, [ADR-0016](0016-no-edge-case-marker.md), and
  now this). No check has yet passed the bar in full; the discipline binds the next one.

## Revisit when

- A corpus — this one or a consumer's — shows a **confirmed** requirement that is genuinely
  fragmentary rather than terse, and a human confirms ≥8 of 10 such flags. Until such a
  sample exists, the proxy has never been shown to track anything.
- `_contract_clauses` gains atomic-form support, at which point the measurement can at last
  be taken on the population that motivated it.
- A check ships in violation of the launch discipline above and later accumulates
  exemptions — that would confirm the rule by the cost of ignoring it, and the trajectory
  table should be re-measured and appended here.
