# ADR-0038 — The retrofit writes the whole pyramid, in `init`'s shape

- **Status:** Accepted — supersedes one clause of [ADR-0031](0031-a-tagged-corpus-can-be-given-the-rungs.md)
  ("`satisfies:` edges are never written") and one of [ADR-0030](0030-the-engine-drafts-the-pyramid.md)
  as carried into the retrofit ("`code` is proposed only where a `verifies:` tag exists").
  [ADR-0036](0036-decomposition-builds-downward-the-system-rung-is-the-authors.md) stands:
  the need's *wording* is the author's; its existence as a named hole is `init`'s, and now
  the retrofit's too. The refusal to derive the level axis from `depends_on` stands. RM032
  is **unchanged**.
- **Decided:** 2026-09-14, at the maintainer's direction, after the first run of the
  retrofit against a real consumer corpus
- **Owner:** Alex
- **Evidence:** `Dashboard_Sync`, engine `2026-09-14.1`, 194 requirements, 152 confirmed,
  every number below from the command named beside it (full write-up:
  `docs/audit/2026-09-14-feedback-flat-corpus-dashboard-sync.md`)

## Context

`clarify --levels --apply` (ADR-0031) wrote `level:` and nothing else, and proposed `code`
only for a requirement carrying a `verifies:` tag. RM032 (`axis.py`) defines a complete
axis as *every code requirement satisfies an architecture one, every architecture
requirement groups a code one and satisfies a system need*. Run one after the other on a
corpus that had never declared a rung, they contradicted each other by construction:

```
$ python requirements/reqmap.py sync | tail -1
194 requirements (152 confirmed, 0 legacy-schema), 436 members, 0 errors, 0 warnings.
$ python requirements/reqmap.py clarify --levels --apply
194 requirement(s) updated.                       # 193 architecture, 1 system, 0 code
$ python requirements/reqmap.py sync | tail -1
194 requirements (152 confirmed, 0 legacy-schema), 436 members, 0 errors, 304 warnings.
```

304 = 152 confirmed × 2 RM032 findings. The pyramid came out upside down — 193 at
`architecture`, 0 at `code` — because the corpus has **0** `verifies:` tags and **122**
`tested-by:` files: by the engine's own definition (SKILL.md: *`code` = one behaviour
group*; the plugin's own corpus: 9 / 68 / 159) **84 of those 193 are `code`-shaped** —
3–7 labelled cases, one file, a linked test — and every other per-file requirement is a
behaviour group that is merely under-specified, not a capability. The families the ids
already declare (`JS` 25, `AI` 25, `DASH` 16, `BUS` 12, …) are the capabilities.

The maintainer's framing, verbatim: *"la init ar fi trebuit să genereze requirement-uri pe
3 nivele … fiecare code să aibă un architecture și să nu fie architecture fără code"*. That
is RM032's model, and `init` already produces it for a fresh repo: per file → `code`, per
directory → `ARCH-*`, one `SYS-NEEDS-A-NAME-001`. The retrofit should produce the same
shape for a corpus that already exists, from the structural signal that corpus has — its
id prefixes — instead of relaxing the rule that says the shape is wrong.

A first cut of this record relaxed RM032 instead ("an atomic architecture requirement is
not a group"). The maintainer rejected it on the model: an architecture requirement with
no code member *is* the finding, and the fix is to put the requirement on the rung it
belongs to. That cut is withdrawn; the rule is untouched.

## Decision

1. **The retrofit proposes `code` for any requirement that is bound to code and is not
   a group.** A requirement with two or more contract groups (the bold labels
   `clarify --decompose` splits on) or a `lint_exempt: [over-scoped]` /
   `[ac-count-high]` entry is proposed `architecture` — a group awaiting decomposition,
   and the proposal names the command. `layer: need` → `system` and `layer: aggregate` →
   `architecture` are unchanged. The `verifies:` requirement is dropped from the proposal:
   it measured whether the *cases* were linked, not which rung the requirement sits on, and
   on a `tested-by:` corpus it put every behaviour group one rung too high.
2. **`--apply` writes the two upper rungs and their edges**, in `init`'s shape. Every
   code-rung requirement that declares no `satisfies:` points at `ARCH-<FAMILY>-001`, where
   `FAMILY` is its own id prefix (`JS-TIMELINE-001` → `ARCH-JS-001`). A family needs
   `LEVEL_FAMILY_MIN` (3, tunable) members to earn a placeholder; smaller prefixes share
   `ARCH-NEEDS-A-NAME-001`. Every new `ARCH-*` placeholder, and every architecture-rung
   requirement without an edge, satisfies `SYS-NEEDS-A-NAME-001` — `init`'s hole, written
   by `init`'s own function. `draft` stubs get no edge; `ARCH-*`/`SYS-*` ids are never
   treated as a family; a requirement that already points somewhere is left alone; an
   existing placeholder is reused, never overwritten; a second run writes nothing. The
   read-only run prints the whole plan beside the rung proposals.
3. **RM032 is unchanged.** Every `code` has an `architecture`, every `architecture` has a
   `code` and a `system`. What the retrofit writes passes it by construction; what remains
   after it is a real finding.
4. **`init` is unchanged.** It already produced this shape for what it extracts (ADR-0030).
   Its closing note still names `clarify --levels` as the path for a corpus it could not
   reach; that path now builds the same three rungs.

## Consequences

- On the corpus that motivated this: **1 + 1 system** (the hole, plus the one hand-written
  need) / **~20 architecture** (10 family placeholders, the shared one, the 4 decomposed
  parents, the over-scoped) / **~190 code**. RM032 falls from 304 to the requirements that
  are groups by their own over-scope exemption and carry no contract groups to split (3
  here) — the exemption's debt, visible where it is owed, with the split command named.
- The footprint is reversible in one gesture: delete the `ARCH-*`/`SYS-*` files, the
  `level:`, `level_source:` and `satisfies:` lines, and the corpus reads as before.
- `REQ-LEVELRETROFIT-985` bullets 3–4 and CASE-2 change (code by default, architecture for
  a group); `REQ-LEVELRETROFIT-987` CASE-2 flips from *"no `satisfies:` line is written"*
  to *"the placeholders and the edges are written, in `init`'s shape"* and CASE-3 becomes
  the decompose hint. `REQ-TRACE-934` is untouched.
- Without the family floor the first real corpus got 48 placeholders — 45 distinct
  prefixes, 33 with one member, plus a `DRAFT` "family" of 36 stubs. With it: 11.
- A repo whose ids carry no useful prefix (`REQ-` everywhere) gets one family, one
  placeholder and one hole — still a valid three-node pyramid, still named as holes.

## Revisit when

- A consumer reports placeholders being **confirmed unedited** — the hole promoted to
  truth. The fix is on the `confirm` path (refuse a `NAME THIS …` title), not here.
- `code` proposed for a requirement that is in fact a capability with no groups written
  yet. The signal to add is the one `clarify --decompose` already reads: bold groups in the
  Description; the answer is to write them, not to move the requirement up by hand.
- ADR-0019's dated review (**2027-03-03**) finds the `level:` axis still set by no consumer
  repo. Then the axis goes, and this record with it.
