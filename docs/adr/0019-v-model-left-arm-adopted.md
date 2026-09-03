# ADR-0019 — The V-model's left arm is adopted; its checks stay warn-only

- **Status:** Accepted — supersedes [ADR-0007](0007-v-model-gating-parked.md). Its **fan-out
  band** Decision and Consequence are superseded by
  [ADR-0023](0023-fan-out-per-level-ceilings-no-floor.md) (2026-09-03), which replaces the
  uniform 5–20 band with per-level ceilings and no floor, and withdraws the claim below that
  the band's seven findings were confirmed real. Everything else here stands; the reasoning
  is left exactly as decided.
- **Decided:** 2026-09-03 (`ARCH-LEVEL-051`, `ARCH-FANOUT-052`, `ARCH-VRUNGS-054`, `ARCH-ATOMICFORM-053`, `ARCH-MODULEFILE-056`)
- **Evidence:** `CHANGELOG.md` `v2.32.0`; the nine-senator audit
  `runs/senate/2026-09-02_*-v-model*.json` (advisory); this repo's own corpus, 52 files → 689
  requirements

## Context

[ADR-0007](0007-v-model-gating-parked.md) shipped the V-model's *vocabulary* — levelled
`tested-by:` suffixes and `validated-against:` — and parked the defining move: naming each
specification level and pairing it with the verification level that discharges it. Its revisit
trigger was **"a regulated user asks for it — a real project with an assessor."**

**That trigger has not fired, and this record does not pretend otherwise.** This is a personal
project with no assessor and no regulated consumer. The maintainer asked for the left arm anyway,
having read the audit's advice against it, and that is a legitimate reason to build something —
but it is a different reason from the one ADR-0007 wrote down, and conflating the two would make
the earlier record look prescient instead of unfired.

What ADR-0007 could not have weighed is the corpus that arrived since. 52 requirement files
described the engine at one flat level of abstraction, where "the gate exits 1 on a dangling
tag" and "the tool is the single source of truth between intent and code" sat side by side as
peers. A flat list has no place to say that the second is why the first exists.

## Decision

Adopt the left arm as **structure**, not as a gate.

Shipped:

- **`level: system | architecture | code`** — a second axis, orthogonal to `layer:`. `layer` is
  graph position (fan-in); `level` is abstraction. They are not aliases: `IMPL_EXEMPT_LAYERS`
  keys on `layer`, so folding `architecture` into `aggregate` would have exempted all 59
  architecture requirements from the confirmed-must-have-code gate without anyone noticing.
- **`satisfies:` is the hierarchy edge**; `depends_on:` stays the composition edge. Only the
  former forms a pyramid, and only the former is read by the fan-out rule and the hierarchy
  diagram.
- **Rungs joining the arms** — `code`→`@unit`, `architecture`→`@integration`, `system`→`@system`.
- **A 5–20 fan-out band** on each level, reported at both edges.
- **The atomic requirement form** and **many requirements per file**, which are what make a
  three-level corpus writable at all: 689 requirements in 68 files rather than 689 files.

Explicitly **not** shipped: any of it as an error. Every check above is warn-only, and every one
is doubly opt-in — it cannot fire until a repo both declares `level:` and, for the rungs,
annotates a test level. Installing this engine in a repo that never adopts the vocabulary
produces exactly the output `v2.31.0` produced. This is [ADR-0002](0002-error-versus-warning.md)
applied unchanged: the layer-to-level pairing table ADR-0007 rejected would have flagged 36 of 40
requirements, and nothing here has made that measurement wrong — it has only moved the pairing
onto an axis the author declares rather than one the engine infers.

## Consequences

- The corpus can now say *why* a clause exists by pointing up rather than by prose: 621
  detailed-design requirements satisfy 59 architecture requirements, which satisfy 9 system
  requirements.
- **The fan-out band fires 7 times on this repo and those 7 are left standing.** Four levels are
  under the band and three over. Silencing them by widening the band would make the check
  decorative; they are real, and the corpus is mid-restructure.
- **`ARCH-VLEVEL-037` now warns about itself** — an architecture requirement whose tests are all
  `@unit`. That is the rung check working, on the requirement that introduced levelled tags.
- **621 of 689 requirements are drafts**, seeded from existing Contract clauses. They are
  structure, not yet reviewed prose, and `_risk_signals` suppresses `unverified-intent` on
  drafts — so a genuine open question written into one of them is currently invisible. Known
  gap, not fixed here.
- A reader of `docs/adr/**` or `CHANGELOG.md` will meet ids that no longer exist. Those files
  were deliberately not rewritten; CLAUDE.md carries the tail-matching translation rule.
- The right arm is still incomplete. A regulated user would still find this short of
  IEC 61508 / ISO 26262 expectations, and ADR-0007's honest statement of that stands.

## Revisit when

Either of these, measured rather than felt:

- **The fan-out band never reaches zero findings.** If, after the corpus is deliberately
  restructured to satisfy it, the band still reports more than a handful, the band is wrong for
  this shape of corpus and should be widened or dropped — not lived with.
- **The level fields stay unused by any consumer repo after 6 months** — review on
  **2027-03-03**. `# verifies:` reached 12/51 adoption and in-file
  markers 2/51 ([ADR-0016](0016-no-edge-case-marker.md)); a third opt-in field that no one
  outside this repo sets is a maintenance cost with no reader, and should be removed rather
  than documented harder.
