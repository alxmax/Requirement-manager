# ADR-0037 — The command surface is already five; the cut is one mode per release

- **Status:** Accepted — closes the TODO item "reduce the engine's command surface from 18
  modes to 5 commands" as filed, and replaces it with a bounded, measured cut
- **Decided:** 2026-09-08, after a nine-senator Senate audit, all seats on Opus
  (`runs/senate/2026-09-08_163116-senate-reqmap-cli-surface-18-to-5.json`, one round,
  verdict **MODIFY**, 8 blocking MODIFY / 1 GO / 0 STOP; Law 8 promoted one vote on a
  transcription artifact, not on substance). It supersedes nothing and closes the still-open
  `senate-reqmap-cli-surface-18-to-4` of 2026-09-05, whose nine conditions this record either
  discharges or restates.
- **Owner:** Alex
- **Evidence:** every number below was measured on the committed tree (`d61da7d`) by the
  command named beside it, and five senators reproduced the central table independently.

## Context

The item, filed by the maintainer on 2026-09-07, asked for "5 commands a reader can hold in
their head, each doing one thing, with the modes that survive as flags of those five and the
rest RETIRED", justified by a stated premise: *"A retired capability takes hundreds of engine
lines and 5–10 requirements with it; that is the only lever in this repo that reduces lines."*

Two measurements decide it, and both contradict the premise.

**The five commands already exist.** `python -c "from reqmap_engine.commands import COMMANDS;
print(list(COMMANDS))"` returns `init, new, gate, sync, clarify`. The v5.0.0 fold and the
v7.0.0 package split did the verb work. What the item calls "18 modes" are **mode flags**
behind three of those five — a flag count, not a verb count.

**Retiring most of them frees no code.** `sync` runs `_audit_summary` on every clean gate
(`reqmap.py:356`, inside `if rc == 0:`), and `audit.py:5-17` imports `design_report, groups,
health, i18n, mapdata, orphans, relevel, risk, similar` at module level. Those capabilities
are already on the bare `sync` path. Removing their flags removes the entry point, not the
code. By transitive module-import closure over `reqmap_engine/`:

```
bare `gate`  : 37 modules,  8849 LOC     (includes axis.py — gate.py:16 imports it
                                          at top level to register RM032)
bare `sync`  : 40 modules,  9883 LOC
automated ∪  : 40 modules,  9883 LOC  = 84% of the engine
off every automated path: 9 modules, 1931 LOC = 16%
   candidates draft implement init levels retire review show verifies
```

Per mode, the LOC a retirement would actually delete:

| mode | deletable LOC | note |
|---|---|---|
| `sync --retire` | 448 | **KEEP** — the instrument every other retirement needs |
| `init --plan` | 186 | not 324: `draft.py:4` imports `_file_facts`, on the bare `init` path |
| `sync --suggest-verifies` | 197 | |
| `clarify --levels` | 178 | |
| `gate --implement` | 135 | |
| `gate --show` | 88 | |
| `gate --review` | 70 | |
| the other 11 modes | **0** each | already on the `sync` audit-tail path |

So the honest ceiling is **854 LOC = 7.2%** of 11,829 (the 1,440 first computed double-counted
`retire.py`'s 448, which is KEPT, and over-counted `candidates.py` by 138). The premise's own
limbs fail on the full population: "hundreds of engine lines" holds for 2 of 7 retirable
capabilities; "5–10 requirements" holds for 1 of 7, observed range 2–5, mean 3.57.

**The headline is sensitive to one line.** Drop `audit` from the `sync` seed and the free
fraction moves 16.3% → 25.1% — 1,034 LOC hinging on `reqmap.py:356`. The 84/16 split is a
property of `REQ-AUDIT-973`'s coupling decision, not of the engine.

**The cost side was measured too low, in the direction that matters.** Zero of the 18 mode
flags is invoked by any automated caller in either repo — but that is the surface no cut would
break. Every prior breakage happened on the human/assistant instruction surface, and the guard
built after the 2026-09-05 audit was verb-scoped, so it was blind to a flag cull and green over
a live broken instruction in a file it already scanned (`.githooks/pre-commit:7`).

## Decision

1. **The item is closed as filed.** The five-command target is met; the residue is a flag cull
   whose ceiling is 7.2% of engine lines, not the bulk the premise assumed. The line-count
   argument does not carry it.
2. **The 11 zero-yield modes are struck from the cut entirely.** `--audit`, `--risk`,
   `--untagged`, `--design`, `--dupes`, `--search`, `--i18n`, `--findings`, `--attach`, bare
   `clarify` and `--decompose` are **KEEP**. Retiring an entry point whose code stays is a
   rename dressed as a deletion, and it costs a semver bump, two regenerated integration
   artifacts and consumer doc edits to free nothing.
3. **`ALIAS` is split into two verdicts.** `KEEP` = byte-identical dispatch, no notice.
   `DEPRECATE` = argparse still accepts the flag for one release and prints a one-line
   migration notice, removed in the release after. The 2026-09-05 audit recorded "deprecated
   aliases must survive one release" and v5.0.0 shipped none; a consumer met `invalid choice`
   instead.
4. **One mode per release, ascending by measured blast radius**, each pass proven under 500
   changed lines (excluding the four generated artifacts) and under 12 `verifies:`-tagged test
   functions. The first pass is `sync --suggest-verifies`: 197 LOC, 0 references in the
   consumer repo, and no surviving command prints its name.
5. **`sync --retire` is permanently KEEP.** ADR-0027 sanctions exactly two delete paths and
   `NoShrinkVerb` pins them; retiring the instrument would revert to ADR-0021's superseded
   grow-only state. It is also the mandated instrument for every other retirement.
6. **`clarify --levels`, `gate --review`, `gate --show` and `init --plan` are out of scope**
   until their own records are settled:
   - `--levels` reverses [ADR-0031](0031-a-tagged-corpus-can-be-given-the-rungs.md), Accepted
     2026-09-06, 178 days before that record's own revisit date of 2027-03-06. It needs a
     superseding ADR arguing from evidence about the capability's value, not its line count —
     and that ADR must say how [ADR-0019](0019-v-model-left-arm-adopted.md)'s 2027-03-03 review
     will still distinguish structural non-use from absent readers without the retrofit path.
   - `--review` is the only engine command the shipped `requirement-quality-review` skill
     invokes, and its retire plan nominates that skill's `SKILL.universal.md` for deletion.
     Cutting it either keeps the flag as KEEP, or retires the skill in the same PR under a
     **major** bump.
   - `--show` is the human dossier, documented in the consumer's `README.md:301`, and
     `REQ-VLEVEL-946` is `confirmed` with `show.py:12` as its sole member — deleting the module
     without re-pointing it is RM006, an error.
   - `init --plan` shares one registry entry with `--md-glob`; eliminating one takes both.
7. **The retired-name guard is a precondition, not a deliverable of the cut.** It must see
   flags and read consumer roots *before* a flag is cut. Shipped in `v7.2.1`.

**The cognitive-surface question is real and is refiled separately.** "Each doing one thing" is
not satisfied by five verbs carrying 36 flags, 17 of them on `gate`, while a bare `sync` runs
ten capability passes its name never announces. That is a different problem from line count and
it gets its own item with a numeric ceiling, so it can be passed or failed.

## Consequences

- Requirement blocks are retired with `sync --retire --apply` — status `deprecated`, reversible,
  already exempt from the gates — never `--delete` in the same release. ADR-0027 rule 4 forbids
  the engine from deleting a function body, so the module goes by hand and the diff shows it.
- The yield is booked as a measured post-condition: `wc -l` over `reqmap_engine/` before and
  after must fall by the mode's stated LOC. If requirements were deprecated and the delta is
  near zero, the retirement removed the specification and kept the code, and it is reverted.
- `leaves_unused` in the retire plan is a graph artefact, not a dead-code finding. Retiring
  `ARCH-SUGGESTVERIFIES-047` reports `ARCH-ACVERIFY-019`, which backs gate rule RM013 on the
  bare-gate path. Do not act on that line without checking the module closure.
- The nine conditions of the 2026-09-05 audit are discharged or restated here rather than
  inherited a second time. Conditions ride on CHANGELOG lines, not TODO checkboxes: of the last
  five level-axis MODIFYs, the one that was honoured was the one whose condition was written
  into the release entry.

## Revisit when

- A consumer asks for a mode this record keeps, or the flag count on `gate` crosses 20 — then
  the cognitive-surface item, not this one, is the record to reopen.
- Three single-mode passes have landed clean, at which point the cadence in decision 4 has n=3
  and can be argued up or abandoned on evidence rather than on the one pass it was written for.
- `_audit_summary` stops running on the bare `sync` path. That one line carries 1,034 LOC of the
  measurement above; if it moves, every zero in the table must be recomputed before it is cited.
