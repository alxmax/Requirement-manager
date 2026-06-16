# AI — advisory (non-deterministic). NOT a gate. Generated 2026-06-16; engine_version 2026-06-16.1
# Coverage: 29/29 requirements. Each item needs human review.

6 findings across 4 requirements (category: acceptance-doesnt-cover-contract only).
No untestable-contract or why-restates-title findings — contracts are precise and WHY sections explain the without-it failure well.

---

## REQ-PROMOTE-011 — confirm

**acceptance-doesnt-cover-contract** (2 gaps) — 5 contract clauses, 4 ACs. AC-1–AC-4 cover: status flip, refuses-without-member, idempotency, and comment preservation. Clause 4 (warn when no `tested-by:`) and Clause 5 (unknown id → exit non-zero) have no acceptance criterion.

**Gap 1 — Clause 4:** "It shall warn (without failing) when no `tested-by:` member is linked."

`suggested_rewrite` — add after AC-4:
```
AC-5
  Given  a requirement with an `implements:` member but no `tested-by:` member
  When   `confirm <ID>` runs
  Then   the status becomes `confirmed`, a warning about the missing test link is printed,
         and exit is 0
```

**Gap 2 — Clause 5:** "Unknown id (no `requirements/<ID>.md`) shall exit non-zero with a clear message."

`suggested_rewrite` — add after AC-5:
```
AC-6
  Given  no `requirements/<ID>.md` exists for the given id
  When   `confirm <ID>` runs
  Then   a clear "no requirement with id" message is printed and exit is non-zero
```

---

## REQ-SHOW-015 — Single-requirement dossier

**acceptance-doesnt-cover-contract** (2 gaps) — 11 contract clauses, 6 ACs.

**Gap 1 — Clause 3:** "When the requirement carries a `priority` field the header shall append it after the layer, and a `milestone` field after that." AC-2 tests `priority` and its absence but never exercises `milestone`.

`suggested_rewrite` — add after AC-6:
```
AC-7
  Given  a requirement with a `milestone` field
  When   `show` runs
  Then   the milestone value appears in the header line after the priority (or after the layer
         when no priority is present); given no milestone field, no empty segment is added
```

**Gap 2 — Clause 7:** "It shall print dependencies in both directions: the `depends_on` ids, and the ids of requirements that depend on this one." AC-4 tests only the reverse direction ("Depended on by"). No AC verifies that the requirement's own `depends_on` list appears.

`suggested_rewrite` — add after AC-7:
```
AC-8
  Given  a requirement that declares `depends_on: [SOME-REQ-001]`
  When   `show` runs
  Then   `SOME-REQ-001` appears in the forward-dependency section of the output
         (distinct from the "Depended on by" reverse section)
```

---

## REQ-HEALTH-017 — Corpus health snapshot

**acceptance-doesnt-cover-contract** (1 gap) — 11 contract clauses, 7 ACs. Clause 5 states the test axis is satisfied by "a `tested-by` member **or** a `test_exempt` reason." No AC exercises the `test_exempt` path: AC-1–AC-7 cover all-green, all-draft, JSON output, no-implements orphan, empty corpus, satisfied need, and unsatisfied need.

**Gap — Clause 5:** `test_exempt` satisfies the test axis.

`suggested_rewrite` — add after AC-7:
```
AC-8
  Given  a confirmed requirement with no `tested-by:` member but a `test_exempt: <reason>` field,
         otherwise satisfying all other axes
  When   `health` runs
  Then   it passes the test axis, is not counted under untested, and is counted toward the
         green score
```

---

## REQ-PROSE-024 — Prose capability classification & drafting

**acceptance-doesnt-cover-contract** (1 gap) — 8 contract clauses, 4 ACs. Clause 7 states a prose draft "shall be scaffolded from the file's title … plus its `##` section headings, recorded as an authoring hint." AC-1 verifies a draft is written; AC-2 verifies sync-only files are skipped; AC-3 verifies tagged files are skipped; AC-4 verifies the scanner picks up `generated-from:` tags. None verifies the draft's content uses the source title or section headings.

**Gap — Clause 7:** scaffold content (title + headings) not verified.

`suggested_rewrite` — add after AC-4:
```
AC-5
  Given  a capability-bucket prose file with a `# My Title` heading and a `## Section One`
         sub-heading, carrying no member tag
  When   `draft` runs
  Then   the generated requirement uses "My Title" as its title and "Section One" appears
         as an authoring hint in the draft body
```
