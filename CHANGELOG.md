# Changelog

## plugin `v2.16.0` — 2026-08-17

**The V-model's right side gets levels, and a reserved role is redefined.** A `tested-by:` link said only *that* something tested a requirement, never at what level — a whole-system run and a single-function check looked identical to the tool. So the engine could report "this has no test", but never "this stakeholder need has never been validated", which is the question the V-model exists to answer. `tested-by:` now takes an optional suffix — `@unit`, `@integration`, `@system` — applying to the whole tag, so a comma-separated id list shares one level.

**Breaking for anyone using `validated-against:` — read this.** The role has sat in `ROLES` since the beginning with nothing consuming it, and both skill contracts described it as *"config/data (re-validated on change)"*. It is now the **validation** link: evidence the right thing was built, as opposed to `tested-by:`, which is evidence it was built correctly. Point a `layer: need` requirement at it. If your repo carries `validated-against:` tags under the old documented meaning, they will now be read as validation evidence and will satisfy the new need rule. Nothing breaks and no build fails — but the tags mean something different than they did, so re-read them before relying on the new warning.

The gate gains two warn-only rules, chosen as the two asymmetric mistakes the V-model actually warns about rather than as a strict layer-to-level table. A pairing table was rejected on evidence: this repo's `feature` requirements are unit-tested by direct function calls, which is a sound choice, and a rule that flags 36 of 40 requirements for practising something sound gets ignored within a fortnight. Instead — a confirmed `need` with no `validated-against:` link warns, and a confirmed `bus` requirement whose levelled links are all `@system` warns, because foundation code covered only end-to-end is slow, fragile, and localises failures poorly. Every other combination stays silent, including a `feature` tested end to end.

**Silent on arrival.** Both rules are opt-in and gated separately: the first holds back until your repo carries at least one `validated-against:` tag anywhere, the second until a given requirement carries at least one levelled link. An unlevelled `tested-by:` link is never judged. Neither rule can fire until you deliberately annotate something, so updating adds no warnings to any repo.

**Compatible in both directions.** `TAG_RE` already ignored a trailing `@level`, so an older vendored engine reads a levelled tag, resolves the id, and ignores the suffix. That property is now a binding acceptance criterion rather than an accident.

`show` prints the level beside a member whose tag carries one. New requirement `REQ-VLEVEL-037`, whose own tests are tagged `@unit` — the engine is the first consumer of its own vocabulary. `REQ-TRACE-020`'s blanket `need` exemption is narrowed to match, and `REQ-CHECK-006`'s severity table gains both warnings.

`MAP_ENGINE_VERSION` → `2026-08-17.1`.

## plugin `v2.15.0` — 2026-08-17

**Requirements are now written in plain present tense, and the linter enforces the reading level.** The corpus passed every clarity check the engine had while still being hard for a newcomer to read. That was not an accident: `LINT_SENTENCE_WORDS` sat at 35 and `LINT_CONTRACT_WORDS` at 30, roughly twice the level being aimed for, so `lint` reported **zero** findings on prose averaging 18.3 words per sentence. Rewriting the prose without moving those numbers would have let it drift straight back.

Contract clauses now name their subject (`` `init` creates the folder ``) instead of opening with an anonymous "It", drop `shall` in favour of a single **"Every line in this section is binding."** at the head of the section, and group under bold labels once past five clauses. `REQ-INIT-012` rewritten this way measures **10.8 words per sentence against 18.3, longest sentence 19 against 32, and no project term left undefined against twelve** — with all ten of its normative clauses intact. All 40 requirements in this repo were converted; no contract changed meaning, and the lock was advanced once with `sync --accept-drift`.

**Consumer-visible — thresholds tighten.** `LINT_SENTENCE_WORDS` drops 35 → 25 and `LINT_CONTRACT_WORDS` 30 → 22, so a repo that updates will see new warnings on prose it has not touched. They are warnings: `--strict` promotes only `ac-count-high` and `over-scoped` to errors, so **no consumer build breaks**. `SKILL.md` rule 3 now teaches the new voice instead of the `shall` convention, and both `REQUIREMENT_TEMPLATE` (what `new` writes) and the `draft`/`init` emission were rewritten to match, so generated files start compliant.

**Three linter changes came out of the migration, and two of them are fixes the old voice was hiding.**

- `stacked-conditions` no longer requires a `shall` or `must` on the line before inspecting it. Keyed on a magic word, it would have gone **silent** under the new voice without a single test failing. Removing the guard cost one additional finding across this corpus — a genuinely stacked clause in `REQ-HEALTH-017` that the keyed check had never been able to see.
- `over-scoped` now counts **scope units** rather than sentences: clause groups when a contract groups its clauses, clauses when it does not. Writing one obligation per bullet multiplies clauses without widening scope — `REQ-NEXT-013` went from 8 dense clauses to 21 atomic ones describing exactly the same command — so counting clauses alone punished the voice it was meant to serve.
- New `anonymous-subject` warning for a Contract clause opening with a bare "It" — 71 across this corpus when it was switched on. It reads physical lines, so a wrapped bullet whose continuation begins with "It " is flagged; rewriting the sentence is the fix, and `REQ-LINTCHECKS-025` records the limitation.

One rendering bug is fixed alongside: `_bullets()` treated a bold-only line as a hanging-indent continuation, so a clause group's label was folded into the previous group's last clause. That leaked into `show`, the map's contract rendering, and the bag of words behind `dupes` and `search` scoring.

`MAP_ENGINE_VERSION` → `2026-08-17`.

## plugin `v2.14.0` — 2026-08-08

**Requirement clarity is now enforced, not just documented.** `lint` mechanised the SKILL.md "Audience & writing level" rules, but nothing ever ran it — not CI, not the pre-commit hook — so 28 readability warnings had accumulated across the corpus unseen. `reqmap.py lint --strict` now runs in this repo's CI (`check_versions.py → gate → lint --strict → map --check → test_reqmap.py`) and in the shipped `hooks/pre-commit`, between the gate and the map-freshness check. **Consumer-visible:** a repo that installs the shipped hook now has commits blocked by error-severity lint findings (a `confirmed` requirement missing its Contract or Acceptance section) plus the `--strict`-promoted structural checks; style warnings stay advisory. The published `check@v1` GitHub Action gains a `lint` input running the same check, **on by default** like `freshness` — a check that must be opted into is documentation, not a check. It runs the consumer's own vendored `reqmap.py`, so it needs plugin v2.3.4 or newer (the release that added the `lint_exempt:` escape hatch); `lint: 'false'` skips it. Re-seed the engine in any repo below that floor before moving the `@v1` tag onto this commit.

The engine is untouched — no new checks, no new flags, `MAP_ENGINE_VERSION` unchanged. What changed is that the existing rules now execute.

The corpus was cleaned to pass: 25 prose findings rewritten across `REQ-SEARCH-036`, `REQ-REGISTRYLAG-035`, `REQ-NEXT-013`, `REQ-TESTLINK-018`, `REQ-INIT-012`, `REQ-FINDINGS-010`, `REQ-SIMILAR-016`, `REQ-REVIEW-022` and `REQ-PROMOTE-011` — long sentences and stacked `and`/`or` clauses split into atomic normative bullets, with rationale moved to each requirement's Notes section where it belongs. No contract changed meaning; the lock was advanced with `sync --accept-drift`. The two structural findings were resolved as documented exemptions rather than splits: `REQ-CHECK-006` (`ac-count-high`, `over-scoped`) is the gate's severity table, and every check it classifies already owns a separate requirement; `REQ-MEMBERDRIFT-027` (`ac-count-high`) has eight criteria that are the branch table of one decision. Both record the reasoning in their Notes, so the exemption is reviewable instead of silent.

## plugin `v2.13.0` — 2026-07-05

**Ranked requirement search — a `search` command and a shared viewer model.** Finding the requirement about a topic meant grepping `requirements/` (exact word, no ranking) or opening the map. The new `reqmap.py search "<query>"` ranks requirements by lexical relevance, most-relevant-first, reusing the same TF-IDF/cosine scoring (`REQ-SIMILAR-016`) that already powers `dupes` — zero new dependencies, gate/lock semantics untouched. Each hit prints its cosine score, and below a calibrated `0.05` floor it prints "No strong match" instead of a spurious top result — the floor sits far below the `0.35` dupes pair-threshold because a short query is a sparse vector, so query-vs-doc cosine runs lower than doc-vs-doc. The map viewer's search box now ranks by the **same** model (`app/src/lib/search.js`, a faithful port), replacing its substring filter, so the CLI (headless/agent/CI) and the viewer (human browsing) agree on what matches; the two runtimes are pinned to one model by a shared golden fixture asserted in both the Python `Search` tests and the viewer's SSR smoke. New requirement `REQ-SEARCH-036`.

`MAP_ENGINE_VERSION` → `2026-07-05`.

## plugin `v2.12.0` — 2026-07-04

**`health` now reports registry lag — commits since the requirements dir was last touched (RM-6, part 2).** `health` told you whether the requirements that exist are coherent, but not whether the registry as a whole had gone stale while code moved on — a consumer's registry sat frozen for 18 days across ~40 code commits while a money value drifted, and nothing surfaced it. `health --json`/print now carry `commits_since_req_touch`, a read-only git-derived count (last commit touching `reqs_dir` → `HEAD`), printed only when non-zero. It is the temporal complement to the untagged-code coverage signal: coverage asks "is this code traced?", lag asks "has the registry moved lately at all?". Advisory only — never a gate, never lowers the score, and absent (not zero) when unmeasurable (no git / no code root / `reqs_dir` untracked). New requirement `REQ-REGISTRYLAG-035`.

## plugin `v2.11.1` — 2026-07-03

**Repos can declare extra scannable extensions (`REQMAP_EXTRA_CODE_EXTS`).** The scanner
looks at a fixed set of source extensions (`CODE_EXTS`). A repo whose source language isn't in
that set had its capability tags go invisible — the file read as un-covered, and a confirmed
requirement whose only implementation lived in such a file failed the gate with "no
`implements:` member" even when correctly tagged. The new `REQMAP_EXTRA_CODE_EXTS` env var
(comma-separated, leading dot optional, e.g. `.foo,bar`) merges extra extensions into
`CODE_EXTS` at load, so any repo can extend the scan set without forking the engine. Additive;
unset = unchanged behaviour.

## plugin `v2.11.0` — 2026-07-03

**`health` can no longer read 100/clean while `gate` has link-sync errors (RM-6).** A
downstream consumer repo's `health` reported 100/100 for 18 days while `gate` sat on 14
unwired link-sync errors — `gate` was never wired into that repo's CI, so nobody saw it, and
`health`'s own score never reflected `gate`'s state at all. `health --json`/`--badge`/print now
carry `gate_errors` (count) and `gate_link_sync_clean` (bool), computed by a new shared
`_link_sync_errors()` helper mirroring `gate`'s own two ERROR-level checks (dangling tags,
enforced-status requirements with no `implements:` member). Purely additive — the `score`
formula is untouched, same idiom as the existing `untagged` signal. The badge can no longer
show `brightgreen` while `gate` would fail; it turns `red` with a `gate:N` suffix instead.

**What this deliberately does NOT fix:** a value changed in a file carrying no membership tag
at all (the actual shape of the incident that motivated this — an unsourced monetary-constant
edit) produces neither a dangling reference nor a missing-`implements` error, so it stays
invisible to this signal; pinned by a dedicated test. Closing that gap needs a sourced /
`validated-against:`-staleness convention, deliberately out of scope here — Senate run
`reqmap-health-gate-cleanliness` (verdict `GO_WITH_CONDITIONS`) rejected folding it into this
change, citing a 2026-06-21 precedent (`reqmap-enforce-all-code-has-requirements`,
`DEEPLY_SPLIT`) against granting `gate` new blocking authority without its own deliberation.

`MAP_ENGINE_VERSION` → `2026-07-03`.

## plugin `v2.8.1` — 2026-06-26

**Fix: member-hash line-ending normalization (CRLF/Windows).** `_file_sha` hashed member
files as raw bytes, so a `_memberlock.json` generated on a CRLF working tree (Windows,
`core.autocrlf=true`) did not match one verified on LF (Linux/CI) — every member showed
spurious drift. Harmless as a warning, but `gate --strict` (added in 2.8.0) escalated it to
a wall of false errors. Now line endings are folded to LF before hashing, matching the
contract hash (already LF-normalized via the text-mode body parse). LF-only repos are
unaffected (their hashes don't change); `REQ-MEMBERDRIFT-027` +AC-8. `MAP_ENGINE_VERSION`
→ `2026-06-26.1`.

## plugin `v2.8.0` — 2026-06-26

**Gate hardening — close the stale-map / uncommitted-lock blind spot.** A consumer repo
hit a recurring member-drift that the gate never caught: CI ran only the link-sync `gate`
(stale map / drift exit 0) and the `_memberlock.json` baseline was generated but never
committed. Three fixes so this can't recur for any consumer:
- The published action (`check/action.yml`) now runs **`map --check`** after the gate by
  default (new `freshness` input, default `true`) — a stale or never-committed map/lock
  fails CI instead of merging unseen. A repo that tracks no map passes silently. New
  `reqmap-repo` input pins `REQMAP_REPO` for a repo whose committed map targets a different
  slug (e.g. a private repo publishing to a public mirror); it is exported only when
  non-empty, since an empty value means "emit no repo" to the engine. The default hook/CI
  examples in `SKILL.md` gain the `map --check` line too.
- **Untracked-lock warning** (`gate`): a `_reqlock.json` / `_memberlock.json` present on disk
  but not git-tracked is now a `WARN` naming the file — the exact gap that silently disables
  drift detection on a fresh checkout. Fail-open (silent when git is unavailable).
- **Test-link detector** now recognizes a Python suite that drives its checks from a
  `run` / `run_tests` / `main` entry point under an `if __name__ == "__main__"` guard, not
  only `def test…`. A stdlib-only harness no longer false-negatives the test-link integrity
  check — that false error was what blocked `gate --strict` on such corpora.

`MAP_ENGINE_VERSION` → `2026-06-26`.

## plugin `v2.3.1` — 2026-06-16

**License correction.** `plugin/.claude-plugin/plugin.json` declared `"MIT"` while
the `LICENSE` file and README are Business Source License 1.1 — corrected to the
SPDX id `"BUSL-1.1"`.

**excalidraw-diagram — adaptive multi-layer posters (one file).**
- The "Diagramming a repo's architecture" recipe is now **adaptive**: a table of
  six layer-types (STRUCTURE / WORKFLOW / INTEGRATION / MODES / MODEL / DATA) each
  with an "include when…" condition. The author picks which layers the repo needs
  and emits them ALL as stacked sections in ONE file, with one legend that decodes
  every layer (colour-per-distinct-role discipline documented).
- **`discover` now scaffolds that poster**: a live STRUCTURE layer (`section()` +
  sized `grid()`, all four `save()` gates at `"error"`) plus commented scaffolds
  for the five optional layers. The generated stub also carries a **portable
  import** (builder next to the stub / on PYTHONPATH, else newest plugin-cache
  build) so it runs from any repo. New regression test locks the stub shape.
- **Richer-by-default, with guardrails.** Multi-tool repos (2+ skills/services
  with distinct flows) now get one labelled `s.lane()` per tool in the WORKFLOW
  layer instead of a single pipeline that hides the others; single-tool repos
  keep one pipeline. A "depth comes from structure, never from cramming" rule
  subordinates elaboration to the existing readability gates (≤20 nodes/region,
  short labels, simplicity-first always win). The `discover` scaffold shows the
  per-tool lane pattern; a ❌→✅ worked example contrasts it with the thin one.

**excalidraw-diagram — C4 removed + docs overhaul.**
- **Removed the C4 helpers** (`Scene.c4()` and `Scene.person()`). They were
  undocumented and pulled the skill toward formal C4 notation; the canonical
  poster (`examples/make_full_architecture.py`) now uses plain role-coloured
  `box()`es. ISO 5807 flowchart shapes are unaffected.
- **SKILL.md restructured for its purpose** — a "The goal" statement up front, a
  "Diagramming a repo's architecture" recipe pointing at
  `make_full_architecture.py`, a "Worked examples — ❌ → ✅ variants" section
  (repo poster, pipeline, parallel agents, decision flow, feedback loop), and the
  box-sizing guidance softened to lean on the `overflow_check` gate.
- **Doc↔code drift closed.** The cheat-sheet and `references/excalidraw_format.md`
  now document the previously-undocumented public API the examples rely on
  (`section()`, `pipeline()`, the ISO shapes, `path()`, `glossary()`), the full
  `Scene()` signature, all four `save()` gates (`crossing_check`, `legend_check`,
  `overflow_check`, `text_overlap_check`), and `check_text_overflow()` /
  `check_text_overlaps()`.

**Audit follow-up (4-lens Consilium audit) — intent-verb propagation + diagram publish.**
- **Stale CLI names swept.** The intent-verb rename (`check→gate`, `promote→confirm`,
  `extract→draft`, `candidates→plan`, `similar→dupes`, `promote-todo→new --from-todo`)
  is now propagated everywhere it had been missed: the published site
  (`docs/architecture.html`), the engine's own module docstring and scaffold
  `SITE_TEMPLATE`, and six requirement files (`REQ-PROMOTE-011`, `REQ-EXTRACT-008`,
  `REQ-CANDIDATES-009`, `REQ-SIMILAR-016`, `REQ-PROMOTE-TODO-001`, plus stale `check`
  references in `REQ-CHECK-006` / `REQ-ACVERIFY-019` / `CORE-DRIFT-003`).
- **Site truth-up.** `docs/architecture.html` showed `v1.16` (now `v2.3.1`) and
  "All 15 commands" (now 18, with the missing `sync` / `site` / `review` cards added).
  README gains the `site` and `review` rows; the `~3200 lines` engine figure is now `~3700`.
- **Diagram published.** The complete-architecture poster is committed at
  `docs/full_architecture.html` and linked from the site nav (`Diagram ↗`), so it
  resolves on GitHub Pages instead of 404-ing (it had pointed at gitignored `diagrams/`).
- **Engine fixes.** `sync --strict` now forwards the flag to the gate (it was silently
  dropped); `REQ-MAP-007`'s contract documents the `todos` key emitted in `_map.json`;
  the narrower file-type scope of `draft` (vs the gate's full scan set) is documented.

reqmap engine touched (the `sync --strict` fix + docstring/template) → `MAP_ENGINE_VERSION`
advances to `2026-06-16`.

---

## plugin `v2.3.0` — 2026-06-15

**excalidraw-diagram — text-overflow gates.** Two silent failure classes the
shape-only overlap check missed — bound text wider than its box (label spills
out) and two free captions/headers colliding — now have `check_text_overflow()`
and `check_text_overlaps()` checks plus a `fit_text()` wrap-and-size helper.
`save()` gains `overflow_check` / `text_overlap_check` (warn by default, error
opt-in); `box()` defaults are unchanged so existing layouts don't re-flow. The
new per-example assertions caught real bugs (widened a box in
`make_full_architecture.py`, fixed caption pitch in `make_explainer.py`, retired
the superseded `make_repo_map.py`). reqmap engine unchanged; `MAP_ENGINE_VERSION`
stays `2026-06-15`.

---

## plugin `v2.2.0` — 2026-06-15

**excalidraw-diagram — ISO 5807 shapes, C4 helpers, poster helpers.** Additive
builder expansion:
- **ISO 5807 flowchart shapes** — `process`, `terminator`, `decision`, `data`
  (parallelogram), `predefined_process`, `preparation` (hexagon), `connector`
  via `box(shape=…)` + convenience methods (polygons drawn as closed lines with
  bbox geometry).
- **C4 model helpers** — `person()` + `c4()` (name / [kind: tech] / description);
  later removed in v2.3.1.
- **Poster helpers** — `section()` (auto-stacked labelled regions) and `pipeline()`
  (auto-spaced, mid-aligned, auto-chained horizontal flowchart).
- **Examples consolidated** to four maintained, test-covered generators
  (`make_full_architecture.py`, `make_explainer.py`, `make_repo_map.py`,
  `make_iso5807_flowchart.py`); retired the overlapping `make_architecture.py`
  and `gen_reqmap_workflow.py`. `diagrams/` output convention documented
  (gitignored, regenerable). reqmap engine unchanged; `MAP_ENGINE_VERSION` stays
  `2026-06-15`.

---

## plugin `v2.1.1` — 2026-06-15

**Audit follow-up (Consilium Trias).** Fixes from a multi-lens audit of the v2.1.0 excalidraw CLI branch:

- **Stale doc references removed.** `README.md` no longer points to the deleted `docs/plugin_architecture.html`; the `SITE_TEMPLATE` comment in `reqmap.py` no longer cites the removed `docs/reqmap_site_prototype.html` (the template is now the canonical source).
- **`render` hardening.** `render_html()` now rejects a scene whose `elements` is a list of non-objects (e.g. `[1, 2, 3]`) instead of writing a viewer that silently fails to render.
- **excalidraw-diagram menu.** The "how to start a diagram" menu gains the missing day-2 path (**re-run / extend your generator**) and a **self-test** entry, each with a when-to-pick-it clause.
- **Tests.** Wrapped three unclosed file handles in the CLI test helpers (no more `ResourceWarning`); added coverage for the `discover` `max_components` truncation path and the non-object-`elements` rejection.

reqmap engine behaviour unchanged (comment-only edit); `MAP_ENGINE_VERSION` stays `2026-06-15`. SRI hashing of the viewer's CDN tags was identified in the audit but deferred — it needs verified per-asset `sha384` hashes (a wrong hash breaks every generated viewer).

---

## plugin `v2.1.0` — 2026-06-15

**excalidraw-diagram CLI.** Two helper verbs on `excalidraw_builder.py` — the authoring path stays Python (no declarative `build <spec>` verb, which would fork a second, divergent format):

- **`render <scene.excalidraw> [out_dir]`** — rebuild the self-contained `.html` viewer from an existing scene file (e.g. one edited on excalidraw.com, where there is no generator script to re-run).
- **`discover <repo> [out.py]`** — scan a repo and emit a runnable Python generator stub (`make_diagram.py`): one box per top-level component on a no-overlap grid, with `TODO`s for the arrows/grouping you fill in, then run it to produce the scene + viewer.
- No-arg `python excalidraw_builder.py` still runs the builder self-test (unchanged — CI relies on it).

reqmap engine unchanged; `MAP_ENGINE_VERSION` stays `2026-06-15`.

---

## plugin `v2.0.0` — 2026-06-15

**Breaking — intent-verb CLI.** Commands renamed to match what the user wants:

| Old | New |
|---|---|
| `check` | `gate` (report-only) — **kept as a deprecation alias**, removed next major |
| `scan` + `check --update-lock` + `map` | `sync` (composite; `--accept-drift` to advance an edited confirmed baseline) |
| `extract` | `draft` |
| `promote` | `confirm` |
| `candidates` | `plan` |
| `similar` | `dupes` |
| `promote-todo "x" --id ID` | `new --from-todo "x" --id ID` |

- **No consumer breakage:** `check` still runs (prints a deprecation notice, forwards to the legacy path), so vendored pre-commit hooks, CI, and the `check@v1` Action keep working. Migrate at leisure: `check`→`gate`, the trio→`sync`.
- **`sync` drift guard:** `sync` refuses to silently re-baseline an edited `confirmed`/`implemented` contract — it prints the changed hashes and exits non-zero unless you pass `--accept-drift`.
- **`gate` is report-only:** it never touches `_reqlock.json`; use `sync` to advance the baseline.
- Requirement IDs are unchanged (`REQ-PROMOTE-011`, `REQ-SIMILAR-016` keep their slugs — only the CLI verb + prose changed).

### Migration
`extract`/`promote`/`candidates`/`similar`/`promote-todo` are removed (no alias) — they do not appear in consumer CI. Update your own scripts: `sed -i 's/reqmap.py check/reqmap.py gate/' <hook>`. `MAP_ENGINE_VERSION` is `2026-06-15`.

---

## plugin `v1.35.0` — 2026-06-14

The `site` command — keep a project presentation page in sync with the registry. Highlights:

- **`site` command** — `reqmap.py site --attach <page.html> [--regions nav,stats]` injects engine-owned, marker-delimited regions into a presentation page and **preserves the authored prose between them**. `nav` = Live Map / Diagram / GitHub links (from `git remote` + artifact paths, each emitted only when its target resolves); `stats` = requirement / confirmed / layer / edge counts + engine version (from `_map.json`). When the `--attach` target does not exist, `site` scaffolds a full self-contained default page with a placeholder hero (`<!-- author me -->`).
- **Two layers** — the engine is deterministic and headless-safe (never prompts); the `requirement-manager` skill is the interactive front door (`site --detect` → ask which target + regions → call the engine). The engine only *links* an Excalidraw diagram — it never generates one (the `excalidraw-diagram` skill stays independent of `reqmap.py`).
- **`init` integration** — `init` runs a best-effort `site` pass (`nav,stats` into `docs/architecture.html`, scaffolding it plus a GitHub Pages signal — `.nojekyll` + an `index.html` redirect — when absent). Opt out with `reqmap.py init --no-site`; a failure in the step never aborts `init`.
- **`map --check` gate** — flags the page stale when its `stats` region drifts from a fresh render; the `nav` region is exempt (it embeds the fork-specific repo URL, like the `repo` field excluded from `_map.json`). A page with no `stats` marker — or one never generated — is not stale. Reuses the `REQ-PAGES-021` Pages-publish path.
- **New requirement `REQ-SITE-026`** + 14 new `Site` tests (idempotency, prose preservation, no-remote degradation, scaffold mode, region-only staleness, HTML-escaping, CLI dispatch, excalidraw independence).

### Upgrade notes
Re-seed consumer repos with `scripts/reqmap.py` only — the scaffold page is an inline template, so no new vendored file is required. `MAP_ENGINE_VERSION` is `2026-06-14`.

---

## plugin `v1.11.0` — 2026-06-04

First feature release since `v1.0.0`. Highlights:

- **Self-contained HTML viewer** — `map` now emits `requirements/_map.html`: a single-file React app with your real requirements inlined, double-click to open, no server or npm needed. Tabs: System Map, Risk, Dependencies, Spec. Main-bus layout ranks nodes by dependency depth (`bus` nodes on the right, consumers on the left); color-coded, selectable edges; grab-to-pan. Fixed: viewer used to render only its bundled demo fixture — all graph tabs now compute layout from the live registry.
- **`init` command** — one-shot bootstrap: scaffolds `requirements/` + `.reqmapignore`, drafts requirements from existing code, builds the lock + map, prints guided next steps. Idempotent; `--wipe` for a hard reset (strips all tags + deletes non-generated files before re-extracting).
- **`next` command** — terminal "what should I do next": a progress header then the Risk tab's actionable buckets most-urgent-first (Orphans · Needs tests · Needs intent review · Drafts to review). Read-only, always exit 0.
- **`promote` command** — human validation step: flips a reviewed requirement's `status` to `confirmed`. Refuses if it has no `implements:` member; warns if no `tested-by:` is linked.
- **`findings` command** — aggregates open `## WHAT — Verify intent` items across all requirements into `requirements/_findings.md`; accepts an AI-triage sidecar (`_findings_triage.json`) for a classified view.
- **`export` command** — emits `requirements/_map.json` (or `--out PATH` / `--out -`) for feeding an external front-end.
- **Intent triage skill action** — 5th menu item in the `requirement-manager` skill for AI-assisted triage of open verify-intent findings.
- **Prose capability discovery** — `extract`/`init` scan `.md`/`.html` by default and classify each prose file into three buckets: ignore (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), or capability-source (prompts/specs auto-drafted as `draft` stubs).
- **`candidates --md-glob`** — read-only extraction plan from prose/spec markdown (advisory, writes no `.md`).
- **Risk signals** — `untested` (has `implements` but no `tested-by:`) and `unverified-intent` (open verify-intent item) surfaced on the Risk tab, `_map.md` table, and detail panel. Silence per-requirement with `test_exempt: <reason>` in frontmatter.
- **`map --check`** freshness gate — exits non-zero if committed `_map.*` is stale; wire alongside `check` in pre-commit/CI.
- **`check --update-lock` auto-runs `map`** — lock and map stay in sync in one command.

### Upgrade notes
Re-seed consumer repos with both `scripts/reqmap.py` **and** `scripts/_map_viewer.html` — the viewer template is new and required for `_map.html` emission. Use `sync_reqmap.sh` or the skill's "update engine" action.

---

## engine `1.11.0` — 2026-06-04

- **Fixed — viewer rendered only its demo fixture**: the `_map.html` graph tabs
  positioned nodes through hardcoded coordinate maps keyed to the bundled sample ids,
  so any real repo's requirements were filtered out and the canvas was blank (registry
  counts were correct, masking it). The System Map, Risk and Dependencies tabs now
  **compute their layout from the live registry** — they render any repo's data.
- **Added — layered "main-bus" layout** (`app/src/lib/layout.js`): nodes are ranked by
  dependency depth so `depends_on` flows left→right (consumers left, shared
  foundation/`bus` nodes right), a barycenter pass minimises edge crossings, and
  edge-less nodes are parked in a side grid.
- **Added — colour-coded, selectable edges**: each dependency edge (arrowhead included,
  via `context-stroke`) is drawn in its source requirement's colour, so overlapping
  lines stay traceable; cards are kept neutral. Click a line to isolate it — it goes
  bold, the rest dim, and its two endpoints are ringed, so `x → y` is unambiguous.
- **Changed — card-avoiding orthogonal routing**: edges run their verticals in the
  inter-column gutters and cross any intermediate column only through a gap between its
  cards, so a line never passes through a card it doesn't connect to (no more
  "x → y → z through a node" look). Rounded right-angle turns.
- **Added — grab-to-pan**: drag anywhere on a map canvas to pan it (no need for the
  scrollbars); a plain click (no drag) still selects a node or edge.
- **Fixed — "center & highlight" button**: it set the highlight but never scrolled; it
  now `scrollIntoView`s the highlighted node.
- **Fixed — `_build_json` area**: emits the ID-prefix fallback (`_area_of`) when a
  requirement has no explicit `area:`, matching the Mermaid path's grouping so the
  JSON graph carries a usable `area` for external front-ends.

## engine `1.10.0` — 2026-06-04

- **Added — React front-end (`app/`)**: the four product surfaces (Map · Problems ·
  Console · Spec) as a real Vite + React app, recreated from the design system. Run
  with `cd app && npm run dev` (dev server pinned to port 5173 via `--strictPort`).
- **Added — `export` command**: `reqmap.py export` emits the registry graph as
  `requirements/_map.json` (`{engine_version, nodes, edges}`) — to stdout (`--out -`),
  a path (`--out PATH`), or the default file — for an external front-end to consume.
- **Added — self-contained viewer (`_map.html`)**: `map` injects this repo's graph
  into a pre-built single-file React viewer (`scripts/_map_viewer.html`, carrying a
  `<!--REQMAP_DATA-->` marker) → a double-click-openable `requirements/_map.html`,
  no server, no npm. Emitted only when the template is vendored beside the engine;
  the injected data is escaped (`</` → `<\/`) against script-breakout. `_map.html` is
  regenerable and gitignored.
- **Behavior change — engine no longer hand-generates HTML**: `render_html` and the
  inline HTML template were removed; `map` now writes `_map.md` + `_map.json`
  (+ `_map.html` from the viewer template when present). The freshness gate
  (`map --check`) now covers `_map.md` + `_map.json`. Re-seed consumer repos with both
  `scripts/reqmap.py` and `scripts/_map_viewer.html` (see SKILL setup / `sync_reqmap.sh`).

## engine `1.8.0` — 2026-06-03

- **Added**: `extract`/`init` now discover prose capabilities (`.md`/`.html`) by
  default, classified by `classify_prose` into three buckets — ignore
  (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), and
  capability-source (prompts/specs). Capability-source prose is auto-drafted as a
  `draft` stub from its title + `##` headings (`_prose_facts`). An advisory
  doc-sync step is emitted in the skill for sync-only docs tagged `generated-from`.
- **Behavior change**: on first post-upgrade `init`/`extract`, repos with
  prompt/spec markdown will see new `draft` requirements. Drafts are NOT enforced
  by the gate (`draft` is not in `ENFORCED`), so this cannot break an existing
  `check`. Review, edit, and `promote` the real ones; delete the rest.
  README/docs/HTML and meta files (`CLAUDE.md`, `SKILL.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE*`) are never auto-drafted.

## engine `1.5.0` — 2026-06-03

- **`reqmap.py promote <ID>`** — one-command human-validation step: flips a reviewed
  requirement's `status` to `confirmed` via a single frontmatter edit (preserves
  indentation + trailing comment, body untouched). Refuses when the requirement has
  no `implements:` member (a confirmed requirement must point to code, else the gate
  errors); warns when no `tested-by:` is linked; idempotent on an already-confirmed
  requirement. Dogfooded as `REQ-PROMOTE-011`.
- **owner standardized** to `Alex` across the repo's own requirements + the scaffold
  default (`extract` still emits `owner: auto` for machine-drafted, unreviewed files).

## engine `1.4.0` — 2026-06-03

Drift gates to prevent the version/map skew that slipped past in 1.3.x.

- **`reqmap.py map --check`** — freshness gate: regenerates the map in memory and
  compares it to the committed `_map.html`/`_map.md` (ignoring the volatile
  `generated:` timestamp), exiting non-zero if stale. A map that was never generated
  passes (consumers who don't track maps are unaffected). Wired into the shared
  pre-commit hook and CI so a code/requirement edit that shifts the map can't be
  committed without regenerating it.
- **`check_versions.py --fix`** — propagates `plugin.json`'s version into every
  `marketplace.json` occurrence, so a bump is one edit + one command instead of three
  hand-edits (the exact drift that failed CI in 1.3.0).
- **dev pre-commit hook** (`.githooks/pre-commit`, enable with
  `git config core.hooksPath .githooks`) — runs version coherence + the drift gate +
  map freshness locally, before CI.

## engine `1.3.0` — 2026-06-03

Non-code capability discovery + corpus-health visibility (`MAP_ENGINE_VERSION` 2026-06-03).

- **`candidates --md-glob`** — discover capabilities in authoritative **non-code** files
  (prompt/spec markdown), advisory-only and allowlist-bounded. Off unless a glob is
  given; writes no `.md`. A new `_md_facts()` extractor pulls the H1 title, the first
  blockquote after it (intent), and `## ` H2 headings (no parser). The plan now carries
  `coverage_summary {total_candidates, with_existing_req}` and a `lineage_note` so an
  unfilled plan can't masquerade as coverage, and so a `generated-from`/`implements`
  tag is understood as authoring lineage — not auto-tracking of later source edits.
- **`.md` added to the scan extensions** so prose capabilities can carry membership
  tags (`<!-- implements: ID -->`). The drift hash still anchors only on the authored
  Contract+Acceptance, so source prose may drift freely.
- **`check` health line** — the summary now reports `(N confirmed, M legacy-schema)`,
  and legacy-schema requirements (no `## WHAT — Verify intent` section, for which
  `findings` is silently inactive) are flagged with a non-blocking WARN. Makes an
  all-baseline corpus (gate enforces nothing yet) and an inactive `findings` visible.
- **`extract`** now annotates the emitted `risk:` field as an author triage hint that
  the engine does not read.
- **map risk signals** — two new signals surface on the Risk tab + `_map.md` table +
  detail panel: `untested` (a requirement with an `implements` member but no
  `tested-by`), suppressible per-requirement with a `test_exempt: <reason>` frontmatter
  field; and `unverified-intent` (a requirement with an open `## WHAT — Verify intent`
  item). Both reuse the existing risk machinery.
- **map zoom-fit fix** — diagrams now fit their container on first open *and* on every
  tab switch. Fit is measured after layout (double `requestAnimationFrame`, zero-size
  guard) and centered, with a capped modest upscale (`FIT_MAX`) so small diagrams fill
  the pane without over/under-zooming.

## check action `v1.0.0` — 2026-06-03

First published release of the `requirement-manager` CI action. Run the drift gate
on every push and PR without copying YAML boilerplate into each repo.

### Usage
```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v1
```

### Inputs (optional)
| input | default | purpose |
|---|---|---|
| `reqmap-path` | `scripts/reqmap.py` | path to your vendored engine, relative to `working-directory` |
| `working-directory` | `.` | directory the gate runs from (where `requirements/` lives) |
| `python-version` | `3.x` | Python to set up (engine is stdlib-only — any 3.x works) |

### What it enforces
`reqmap.py check` — link sync (every code tag points to a real requirement; every
confirmed requirement has ≥1 member), content drift vs. the lock, and `depends_on`
target existence. Fails the build on any violation.

### Notes
- **Versioning:** pin to `@v1` (moves with backward-compatible fixes) or to `@v1.0.0`
  / a commit SHA for exact reproducibility. The action ref is independent of the
  plugin/PyPI semver.
- **Scope:** the vendored-copy staleness notice (`warn_if_stale`) is gated on
  `CLAUDE_PLUGIN_ROOT`, unset in CI — silent and exit-neutral there by design.
- **Security:** keep `permissions: contents: read` in the caller workflow; the gate
  needs no secrets and no write scope.
