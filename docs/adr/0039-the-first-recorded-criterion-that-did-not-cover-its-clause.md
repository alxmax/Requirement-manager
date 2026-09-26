# ADR-0039 — The first recorded criterion that did not cover its clause

- **Status:** Accepted. Does not supersede anything. It **records an incident** against
  [ADR-0018](0018-no-contract-acceptance-traceability-marker-yet.md)'s third revisit
  trigger, and fixes the two defects the incident exposed.
- **Decided:** 2026-09-14 (`REQ-TRANSLATE-938`, `ARCH-TRANSLATE-044`)
- **Evidence:** the review of 2026-09-14, and the mutation matrix reproduced below.

## Why this record exists

ADR-0018 rejected a contract-to-acceptance traceability marker and left three numbered
conditions under which the question reopens. The third reads:

> A recorded real incident where a shipped defect traces to an Acceptance criterion that
> falsely appeared to cover a Contract clause it did not exercise — one incident is one
> short of the "two beats one" bar ADR-0012 set; a second such incident (after this one)
> would meet it.

**This is that incident, and without this file it would not have been counted.** The next
person to propose the marker would start the count at zero and re-argue it from scratch.

## The incident

`REQ-TRANSLATE-938`'s fourth binding clause governed how the viewer renders a cached
translation: every caller that renders translated text renders the "machine-translated,
unreviewed" badge beside it. Four SSR checks in `app/scripts/ssr-smoke.jsx` were written
for it and were tagged at a `#CASE-5` of `REQ-TRANSLATE-938` — a case label that never existed.
(The tag is spelled apart here on purpose: `.md` is scanned, so writing it whole would
make this record itself a phantom member, which is what RM034 reports.) RM034, shipped hours earlier in `v7.11.0`, caught the dangling label on its first
run over the corpus's 1061 hand-written tags; the bogus suffix was stripped and the checks
were left linked at file level.

The question then asked was whether to author the missing case. Auditing it produced two
findings that the label question had hidden.

### 1. The criterion did not cover the clause — measured, not argued

The clause is universal over four render sites (`app/src/views/SpecDoc.jsx`, title /
contract / intent / acceptance). The four checks assert the badge string appears
**somewhere** in the rendered document. Deleting each site in turn and running
`npm run smoke`:

| mutant | before | after |
|---|---|---|
| `SpecDoc.jsx:59` title | survived | **killed** |
| `SpecDoc.jsx:63` contract | survived | **killed** |
| `SpecDoc.jsx:70` intent | survived | **killed** |
| `SpecDoc.jsx:75` acceptance | survived | **killed** |
| **kill rate** | **0 / 4** | **4 / 4** |

A refactor could drop any single badge and ship machine-translated prose as the author's
own words with the suite green, the gate at 0 warnings and CI passing. The "before" column
is the incident; the "after" column is the fix — one SSR check that **counts** badge
occurrences per translated field instead of asserting presence.

### 2. The clause was partly false of shipped code

The same clause said the viewer consumes `node.i18n` **ONLY** through `translatedText()`.
`app/src/lib/search.js:121` does `const i18n = r.i18n || {}` — the search index reads
cached translations directly, deliberately, so a query matches translated text. A
`confirmed` contract had drifted from the code and nothing in the toolchain reported it:
drift detection hashes the contract against its own previous text, never against the code.

## Decision

1. **The incident is recorded** — this file is the artifact ADR-0018's third trigger
   requires. The count against the "two beats one" bar now stands at **one**.
2. **The clause is corrected, not deleted.** "ONLY through `translatedText()`" is narrowed
   to every path that *renders* `node.i18n` as displayed prose, and the non-rendering
   reader (the search index) is named as permitted. The obligation that matters — one
   badge per translated field — is stated as the per-field count it actually is.
3. **The verification is strengthened before the label is written.** The counting check
   lands first; `CASE-4` is then authored at the level of what the mutants kill, and the
   five checks are tagged at it. This is the order run
   `2026-09-06_141350` established and that this record follows: write verification that
   holds, *then* label. The reverse — labelling evidence that does not hold — is the shape
   ADR-0012 rejected on a measured 78.6% false-positive rate.
4. **No rule is adopted.** 92 of 254 confirmed requirements carry more binding clauses than
   labelled cases, but that quantity has median 0 and standard deviation 1.95, with 101
   exactly equal and 61 running the other way: it is unmanaged, not a norm, and it licenses
   no inference. `CASE-4` exists because RM034 stripped a bogus label off already-passing
   checks — not because a clause lacked a case. No predicate is defined over the other 91,
   and no lint ships with this.

## What this cost, and who said so first

`RM034` was demanded as a blocking condition in the review of 2026-09-02 — a reverse
dangling-`verifies:` check. That review's condition was overridden and the check was not
built. It was built twelve days later, and its **first** run found this
defect, on the requirement the same audit had been about. The gap between the override and
the find is the measured cost of overriding a blocking condition, and it is the clearest
such datum the corpus holds.

## Revisit

This record adds nothing to revisit on its own. ADR-0018's three triggers stand unchanged;
trigger three is now at one of two. A **second** recorded incident of the same shape meets
ADR-0012's bar and reopens the traceability-marker question — at which point the numeric
bars ADR-0016 and ADR-0018 set (a 5–40% fire rate, and ≥8 of 10 sampled flags confirmed by
a human reader) apply to whatever is proposed.
