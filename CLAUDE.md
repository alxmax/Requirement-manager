# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `plugin/` (the engine resolves paths relative to its working directory):

```bash
python scripts/reqmap.py init               # first-use bootstrap: scaffold + draft from code + lock + map + next-steps
python scripts/reqmap.py gate --code ..     # gate: link sync + drift + test-link integrity (warn) — run before every commit; report-only, never touches the lock
python scripts/reqmap.py sync --code ..     # rescan + advance drift baseline + regen map (+ a committed _findings.md) in one step; use --accept-drift when a confirmed/implemented contract changed
python scripts/reqmap.py map --code ..      # generate _map.md (Mermaid) + _map.json (graph) + _map.html (viewer, if template vendored)
python scripts/reqmap.py site --attach docs/architecture.html --regions nav,stats   # inject/refresh engine-owned regions (links + counts) into a presentation page; scaffolds one if absent. init runs this best-effort.
python scripts/reqmap.py export             # emit requirements/_map.json for an external front-end (also: --out -)
python scripts/reqmap.py scan               # list code members per capability
python scripts/reqmap.py new AREA-NAME-NNN  # scaffold a new requirement from the template
python scripts/reqmap.py new --from-todo "TODO name" --id AREA-NAME-NNN [--mark-done]  # scaffold a requirement draft from a TODO.md item; --mark-done flips the item to [x]
python scripts/reqmap.py next               # 'what should I do next': counted, actionable risk buckets (incl. Granularity/Redundancy)
python scripts/reqmap.py lint --code ..     # readability/structure check on non-draft requirements (--strict fails on errors)
python scripts/reqmap.py show AREA-NAME-NNN  # consolidated dossier for one requirement (contract, deps, members, risk)
python scripts/reqmap.py dupes              # flag requirement pairs with overlapping contracts (TF-IDF cosine; --threshold)
python scripts/reqmap.py search "query"     # rank requirements by lexical relevance (same TF-IDF cosine as dupes; --top)
python scripts/reqmap.py coverage           # list source files carrying no implements: tag, grouped by directory (--json)
python scripts/reqmap.py health             # corpus coherence score + component counts (--json for a CI badge)
python scripts/reqmap.py draft              # draft requirements from untagged legacy code (input: existing code)
python scripts/reqmap.py plan               # JSON capability-extraction plan, writes no files (AI-assist; use before draft)
python scripts/reqmap.py findings           # aggregate open verify-intent items
python scripts/reqmap.py confirm AREA-NAME-NNN  # confirm a draft/baseline requirement (requires an implements: member); run sync after
python scripts/reqmap.py review [AREA-NAME-NNN]  # emit a JSON review plan (AI-feed: intent, contract, acceptance, anchors) for all or one requirement
python scripts/reqmap.py design [--json]     # advisory design review of the repo's code (Python via ast; brace languages via heuristics): the four OOP pillars (encapsulation, abstraction, inheritance, polymorphism) plus house standards (file/line length, docstrings, definitions per file); read-only, exit 0, never the gate; thresholds in _config.json; its score rides in _map.json (`design`), the _map.md header and `health`
python scripts/reqmap.py suggest-verifies    # propose `# verifies: <ID>#CASE-N` tags for tests already named after the criterion; --apply writes them
python scripts/reqmap.py translate [--to ro|en]  # MANUAL, opt-in only: cache a `claude -p` translation of the corpus's majority-language requirements into requirements/_i18n/<locale>.json. Never called by gate/sync/lint/map/the pre-commit hook. A structural-fidelity check refuses to cache a translation that alters backticks, numbers, markdown markers, `CASE-N` labels or the Gherkin keywords (the last two are identifiers a `verifies:` tag points at, not prose).
python scripts/reqmap.py gen-integration    # regenerate tool_definition.json + the SKILL.universal.md command table from the COMMANDS registry
```

**`gate`/`sync`/`lint`/`map` above already carry `--code ..`** so the scan reaches the repo root
(`docs/`, `.github/`, `.githooks/`, root-level `scripts/`), per a NEW repo-root `.reqmapignore`
(kept separate from `plugin/.reqmapignore` — see that file's own comment for why). This is not
optional for these four: the *committed* `_reqlock.json`/`_map.json`/`_map.md`/`docs/map.html`
are generated from the widened scan (member `loc` paths are `code_root`-relative, so a copy
generated without `--code ..` reports every existing member's path one level off and fails
freshness checks against the real committed files). `.githooks/pre-commit` already runs from
the repo root, so it passes `--code .` instead of `--code ..` — same target, different starting
cwd. Read-only exploration commands with no committed-artifact freshness concern (`scan`, `show`,
`search`, `next`, `health`, `coverage`, `dupes`, `findings`, `review`) are unaffected either way
and can be run with or without `--code ..` depending on what you want to inspect.

**A `confirmed` requirement whose members all live outside `plugin/`** (e.g. `ARCH-SELFGATE-039`,
whose 5 members are `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/pre-commit`,
`.githooks/pre-push`, `sync_reqmap.sh`) can now only pass `gate`'s implements-tag check under the
widened scan. Running the bare `gate` (no `--code ..`) genuinely ERRORs on such a requirement —
not a silent miss, a real exit-1 failure — because the narrow scope never reaches any file that
proves the tag exists. This is an accepted, permanent consequence of the widened-scan design, not
a bug: CI and the pre-commit hook always run widened, so it never fires there; a human running the
bare command locally sees a loud, immediately-diagnosable error rather than a silent divergence.

Run tests (stdlib unittest, no install needed). On Windows always pass `-X utf8` — the suites print non-ASCII and fail on cp1252:

```bash
python scripts/test_reqmap.py                                      # from plugin/scripts/ or plugin/
python -X utf8 -m unittest test_reqmap.Gate.test_name -v           # single test/class (run from plugin/scripts/)
python scripts/reqmap.py map --check --code ..                     # fails if committed _map.* (or docs/map.html) is stale
```

From the **repo root** (not `plugin/`) — the packaging/release side:

```bash
python scripts/check_versions.py        # plugin.json semver == marketplace.json (x2); validates MAP_ENGINE_VERSION shape. --fix syncs.
python -X utf8 scripts/test_check_versions.py
python scripts/check_engine_bump.py --base main   # reqmap.py changed => MAP_ENGINE_VERSION must have changed (CI: --base HEAD~1; hook: --staged)
python -X utf8 scripts/test_check_engine_bump.py
python -X utf8 scripts/test_changelog_notes.py    # release-notes extraction (CI runs it with cwd=scripts/)
python -X utf8 scripts/test_cross_tool.py         # seeds the engine into a tempdir, runs sync→gate→map: the AI-agnostic falsification test
python -X utf8 plugin/skills/excalidraw-diagram/scripts/excalidraw_builder.py   # builder smoke + layout/overlap self-checks
python -X utf8 -m unittest test_excalidraw -v     # from plugin/skills/excalidraw-diagram/scripts/
```

**Python floor: 3.9** (`MIN_PYTHON` in `reqmap.py`, `ARCH-PYFLOOR-040`). It is deliberately the oldest version CI runs, not the oldest the code happens to work on (3.7): a floor nothing tests is a claim, not a guarantee. `reqmap.py` refuses an older interpreter with one readable line and exit 2. Raising it means moving the matrix and `MIN_PYTHON` together — a test asserts they stay equal.

CI has **two** test surfaces, don't confuse them: `gate-and-tests` (ubuntu, `3.x`) is the single authoritative verdict on this repo's requirement corpus; `tests` is the portability matrix (3.9/3.12/3.13 x ubuntu/windows) that runs every suite and nothing else. `release` needs both; `deploy-map` needs only the gate.

A third, non-authoritative job — `quality` — measures the engine rather than verifying it: `coverage` over `test_reqmap.py` (92% at the time of writing) and `ruff`, both published to the run's job summary. Only `ruff --select E9,F` (syntax errors, undefined names) can fail it; every other rule is advisory, because several ruff complaints describe deliberate choices here (`except Exception: return None` IS the fail-open contract in a dozen places). It is the only job that installs from PyPI, both tools pinned, and it is deliberately **not** in `release`'s `needs` — the authoritative verdicts stay dependency-free. There is no coverage floor yet, on purpose: publish the number first.

The gate must pass (`0 errors`) before committing changes to `reqmap.py` or any requirement file. CI (`.github/workflows/ci.yml`, job `gate-and-tests`) runs, in order: `check_versions.py` → `test_check_versions.py` → `test_changelog_notes.py` → the CHANGELOG-entry check → `reqmap.py gate --code ..` → `reqmap.py lint --strict --code ..` → `reqmap.py map --check --code ..` → `test_reqmap.py` → excalidraw builder + tests. (`check` is a deprecated alias for `gate` — kept through `v3.0.0`, removed in `v4.0.0`.)

**Hooks — two different files, don't confuse them:**
- `.githooks/pre-commit` is *this repo's dev* hook, mirroring the CI order (`check_versions.py` → `check_engine_bump.py --staged` → `gate` → `lint --strict` → `map --check`). Enable once: `git config core.hooksPath .githooks`. `.githooks/pre-push` also blocks direct pushes to `main`.
- `plugin/hooks/pre-commit` is the hook **shipped to consumer repos** — editing it changes consumer behaviour and needs a semver bump.

`sync_reqmap.sh` propagates `plugin/scripts/reqmap.py` (+ the vendored viewer template) into the local plugin cache and any consumer repos passed as args; it only refreshes an *existing* vendored engine, never seeds one.

## Architecture

This repo is a Claude Code plugin that ships **three skills** under `plugin/skills/`:
- `requirement-manager` — the core skill; seeds `reqmap.py` into a target repo and drives the SSOT/drift workflow. Its `SKILL.md` is the authoritative contract.
- `requirement-quality-review` — on-demand AI *advisory* review of requirement files' semantic quality (is a clause testable, does the WHY explain intent). Never part of the gate (`implements: ARCH-REVIEW-022`).
- `excalidraw-diagram` — generates Excalidraw scenes + a self-contained HTML viewer from a system description. Fully independent of `reqmap.py`: its own stdlib-only builder at `skills/excalidraw-diagram/scripts/excalidraw_builder.py` (smoke test + auto-layout/overlap self-checks via `python excalidraw_builder.py`). Example generators live in `skills/excalidraw-diagram/examples/` — `make_full_architecture.py` (the complete-architecture poster), `make_iso5807_flowchart.py` (the reqmap flow in ISO 5807 notation), and `make_excalidraw_skill_flow.py`.

**Generating diagrams *of this repo*:** run a maintained generator from `plugin/skills/excalidraw-diagram/examples/` with `diagrams` as the output arg (e.g. `python plugin/skills/excalidraw-diagram/examples/make_full_architecture.py diagrams`). Outputs land in `diagrams/` (gitignored, regenerable, never committed) — **never** `docs/`, which is the published Pages root and holds only reviewed, self-contained HTML (`.gitignore` hard-blocks `docs/*.excalidraw`). Do not author ad-hoc generators with an absolute plugin-cache import; reuse the examples (they use a portable relative import).

The repo dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Design decisions live in `docs/adr/`** (26 records, index at `docs/adr/README.md`) — the single-file engine (and `0014`, why it is not split and carries no size gate), the error-versus-warning split, the drift-baseline shape, the V-model (`0007` parked it, `0019` supersedes it by adopting the left arm warn-only), and four rejected proposals. Read the relevant record before proposing a change that reverses one; each names the evidence it was decided on and its revisit condition. A decision that changes gains a NEW record superseding the old one — never an edit to the old one.

**Single engine file:** `plugin/scripts/reqmap.py` — 7,169 lines measured 2026-09-03, stdlib only, no external dependencies. Its size is a settled question, not an open one: see `docs/adr/0014` (no split, no line-count gate, numeric re-open triggers). All logic (parse, scan, gate, map, draft, plan, findings, init, next) lives here. This is intentional — hermetic deployment into any repo without install friction.

**Command registry is the CLI's SSOT** (`COMMANDS` dict near the top of `reqmap.py`, `ARCH-CMDREGISTRY-033`): one entry per command (summary, positional arg, flags). `plugin/tool_definition.json` (OpenAI function-calling schema, for non-Claude assistants) and the command-table region in `skills/requirement-manager/SKILL.universal.md` are **generated** from it by `gen-integration` — never hand-edit those two. `gate` warns when they are stale relative to the registry.

**Requirement layers:**
- `layer: bus` — foundation capabilities (config, parsing, scanning, drift detection). High fan-in; change behind their contract.
- `layer: feature` — compose the bus via `depends_on`. One per user-facing command (new, scan, gate, sync, map, draft, plan, findings, init, next, confirm, lint, show, dupes, search, health, coverage, site, review, …); `ls plugin/requirements/` is the live list.
- `layer: need` — an upstream stakeholder need (`SYS-SSOT-001`), satisfied-by feature requirements via `satisfies:`, not implemented by code; exempt from the implements/tested-by gates (see `ARCH-TRACE-020`).
- `layer: aggregate` — the mirror image: no code of its own, covered *downward* by a non-empty `depends_on` (it asserts its dependencies work together). Exempt from the same gates via the one predicate `_impl_exempt`, which `gate`, `health`, the risk map and `confirm` all read — they disagreed before (`docs/adr/0015`).

**Specification levels — `level:` is a SECOND axis, orthogonal to `layer:`.** `layer` is the graph position (fan-in: bus/feature/need/aggregate); `level` is the abstraction rung of the V-model's left arm: `system` → `architecture` → `code`. They are not aliases and must not be merged — `IMPL_EXEMPT_LAYERS` keys on `layer`, so treating `architecture` as `aggregate` would silently exempt every architecture requirement from the confirmed-must-have-code gate. The hierarchy edge is `satisfies:` (level axis); `depends_on:` stays the composition axis. Only `satisfies:` forms the pyramid the 5–20 fan-out rule and the `_mermaid_hierarchy` diagram read.

**Ids carry their level, since 2026-09-03:** `SYS-` → `ARCH-` → `REQ-`. The prefix is a reading convenience for *this* corpus, not something the engine parses — `level:` in the frontmatter is the authority, and a consumer repo may name ids anything. Renaming was one mechanical prefix swap over 681 ids, keeping every tail (`STEM-NNN`) intact.

**Three levels, since 2026-09-03 (`docs/adr/0025`, superseding `0024`'s one-day promotion):** 9 `SYS-*` stakeholder needs at `level: system` (`layer: need`, satisfied by ARCH nodes, verified by `validated-against:`), 62 `ARCH-*` capabilities at `level: architecture` (one command or one shared engine capability, `tested-by: <id> @integration`), 126 `REQ-*` behaviour groups at `level: code` (3-7 labelled cases each, `# verifies: <id>#CASE-N` per case). 197 requirements in total. `fan-out`'s `system` ceiling is ten again (`LINT_FANOUT_BANDS`). The 573 one-sentence atomic leaves of the same morning were folded into the 126 `REQ-*` groups; their ids (`REQ-…-233` … `-815`) are historical, the folded children start at 821.

**Translating an old id.** `docs/adr/**` and `CHANGELOG.md` were deliberately NOT rewritten: they record what was true on a date, and an ADR citing `REQ-VLEVEL-037` is a correct statement about 2026-08-17. To read one, match the tail: `REQ-VLEVEL-037` → `ARCH-VLEVEL-037`, `CORE-PARSE-001` → `ARCH-PARSE-001`, `NEED-SSOT-001` → `SYS-SSOT-001`. Tails are unique across the corpus, so the lookup is unambiguous. A decision that changes still gets a NEW ADR — never an edit to an old one, prefixes included.

**Requirement schema** (`plugin/requirements/*.md`): YAML frontmatter (id, status, level, layer, owner, satisfies, depends_on; optional priority/milestone/lint_exempt/test_exempt — no comments, no empty keys) + prose body in the **lean form**: `## Description` (an intent quote for a developer new to the repo, then `Every bullet below is binding.` and the clauses), `## Cases` (`CASE-N — title`, Given/When/Then), optional `## Context`. No `## Verify intent`, `## Links` or `## Members in code (auto)` on a confirmed requirement. An `ARCH-*` Description is its intent plus one obligation sentence per child ending in `[[REQ-…]]`; the detail lives only in the child. Two body forms coexist and the engine detects which from the body, never from the frontmatter: the **sectioned** form and the **atomic** form (`form: atomic`) — a story blockquote plus a `Scenario:` block, with no normative headings at all. `binding_hash` hashes the normative heading span for the first and the story+scenario span for the second; a form it cannot recognise would hash the empty string, which is why `_atomic_spans` is consulted before the fallback. The frontmatter parser is hand-rolled (scalars + inline lists only — no full YAML library).

**Section names — `## Description` and `## Cases`, since 2026-09-03** (`ARCH-DESCRIPTION-057`). `## Description` merged the standalone `> WHY:` blockquote with `## WHAT — Contract (normative)`: the same capability was described twice, as rationale and as obligation, under two headings that both said WHAT. The quote now opens the section and the binding clauses follow it. `## Cases` (labels `CASE-1`, `CASE-2`, …) replaced `## HOW — Acceptance (= tests)` and `AC-N`. `## Verify intent` and `## Notes` simply dropped a `WHAT —` prefix that no longer named a section.

**Every old spelling still parses, forever.** `CONTRACT_LABELS = ("description", "contract")` and `ACCEPTANCE_LABELS = ("cases", "acceptan")` are the SSOT — current name first — and `_has_any`/`_from_any` are the only way a call site should ask for either section. `AC_VERIFY_RE` and `_AC_LABEL_RE` accept `CASE-N` and `AC-N` alike, because the label is an **identifier a `# verifies:` tag points at**: dropping the old spelling would break every consumer tag already written. Most `test_reqmap.py` fixtures are deliberately left in the legacy form — that is the back-compat suite, and rewriting them would delete the only coverage of the older shape.

**The intent quote is inside the normative section but outside the drift hash.** `binding_hash` skips `>` lines within a normative span, so improving an explanation never reports DRIFT on a confirmed contract; `_contract_clauses` never treated a blockquote as a clause, so the linter never sees rationale either. The atomic form draws the same line by keeping `rationale:` in the frontmatter. No requirement carried a blockquote inside a normative section when this was added, so no existing hash changed.

**One file may hold many requirements** (`ARCH-MODULEFILE-056`). A block starts at a `---` line *immediately followed by* `id:`, so a bare `---` used as a horizontal rule starts nothing; `split_requirement_blocks` returns the whole text unchanged for a single-block file. Each architecture requirement keeps its detailed design in its own file — 197 requirements live in 71 files: each `ARCH-*.md` holds the architecture requirement followed by its `REQ-*` children, each `SYS-*.md` one need. Only block 0 may fall back to the filename for its id, or every module would mint a duplicate named after itself.

**Code tagging:** source files declare membership with inline comments:
```
# implements: ARCH-PARSE-001
# tested-by: ARCH-CHECK-006
```
`TAG_RE` in the engine enforces a left-boundary guard so `reimplements:` or `x-implements:` are not picked up as real tags. The member list is discovered by scanning — never hand-maintained.

**Gate logic** (`gate`): every check is a rule in `GATE_RULES` (`ARCH-RULES-059`, `docs/adr/0026`), registered with `@gate_rule("RMnnn", severity, strict=...)` and run over one `GateContext` by `cmd_check`, which itself only advances the lock and prints. Each printed line carries its code (`WARN  RM018 ARCH-X: DRIFT — ...`), `gate --json` carries `findings` records, and a requirement may write `gate_exempt: [RMnnn]` to silence one rule for itself. Link sync (RM001 dangling tag, RM006 enforced requirement with no `implements:` member) and `depends_on` target existence (RM003) are **error-level** (exit 1); `health` reads RM001/RM006 from the same registry. Drift (RM018, content hash vs `_reqlock.json`) and **test-link integrity** (RM012) are **warn-only**, promoted under `--strict`. `gate` is report-only and never touches `_reqlock.json`; use `sync` (with `--accept-drift` for confirmed/implemented contracts) to advance the baseline. The test-link check: a `tested-by` file must exist and contain a test function (`_test_link_problem`). Per-criterion coverage (RM013, `ARCH-ACVERIFY-019`): a `# verifies: <id>#CASE-N` tag links one test to one labelled criterion; the gate warns once per requirement for the untagged `CASE-N`s, only once a requirement carries at least one `verifies` tag. `Requirement` and `Finding` are dict subclasses (`r["meta"]` still works) that carry the derived facts rules read — encapsulation, no class hierarchy.

**Per-repo configuration:** `requirements/_config.json` overrides the constants named in `CONFIG_KEYS` (`LINT_AC_MAX`, `SIMILAR_THRESHOLD`, `ORPHAN_CODE_MIN_LOC`, `LINT_FANOUT_BANDS`, ...) plus `extra_code_exts`; read fail-open at startup by `apply_config(load_config(...))`, an unknown or mistyped key is reported on stderr and skipped (`ARCH-CONFIG-060`). This repo ships none.

**Corpus shape is advised on in BOTH directions, read-only** (`ARCH-REDUNDANCY-058`, `docs/adr/0020`). `next`'s *Granularity* bucket says one requirement does too much (more than `LINT_AC_MAX` criteria — 7 — scoped to `LINT_STATUSES` and honouring `lint_exempt: [ac-count-high]`, via the shared `_oversize` predicate); its *Redundancy* bucket says several say the same thing — requirements whose Description clauses are byte-identical once case and whitespace are normalised. `_redundant_groups` is the exact-match floor under `dupes`, not a rival: no threshold, so a group is a duplicate by construction. Draft placeholders are excluded or every scaffolded `TODO:` would match every other. It is surfaced by `sync` and `next` and deliberately NOT by `gate` — the hook runs `gate` on every commit and corpus shape is not a commit-time concern. It reports; it never merges. **It ships below ADR-0016's 5% fire-rate floor on purpose** (6 groups, 1.7% of the corpus, zero false positives by construction) — `docs/adr/0020` records why, so the number is not quietly widened later.

**Generated outputs** (under `plugin/requirements/`):
- `_map.md` — 4 Mermaid diagrams for static rendering (System Map, Req→Code, Dependencies, Risk) *(committed)*
- `_map.json` — `{engine_version, nodes, edges}` registry graph; consumed by the viewer and any external front-end; also written standalone by `export` *(committed)*
- `_map.html` — a self-contained single-file copy of the React viewer (`app/`) with this repo's `_map.json` inlined; opens by double-click, no server. *Regenerable (template + `_map.json`), gitignored — not committed.*
- `_reqlock.json` — content hash baseline for drift detection (one hash per requirement = the contract; prose-ahead-of-code direction) *(committed)*
- `_memberlock.json` — versioned sidecar (`{_schema, members}`) of dedicated-member content hashes for reverse-direction (member-ahead-of-spec) drift; kept separate so `_reqlock.json` stays a byte-stable cross-repo contract an older seeded engine reads unchanged (`ARCH-MEMBERDRIFT-027`) *(committed)*
- `_findings.md` — aggregated verify-intent triage *(committed; `map`/`sync` refresh it once it exists, `map --check` flags it stale)*

**`map` writes outside `plugin/` too.** `_docs_publish_path` (`ARCH-PAGES-021`) resolves the **git root**, so a `map` run from `plugin/` also rewrites repo-root `docs/map.html` whenever `docs/` carries a Pages signal (`.nojekyll` or `index.html`) — and `map --check` fails if that published copy drifted. `docs/` is the GitHub Pages root (committed: `map.html`, `architecture.html`, `full_architecture.html`, `index.html`, `.nojekyll`); the `deploy-map` CI job publishes it via OIDC on pushes to `main` and refuses to publish a `map.html` under 10 KB.

The viewer is the Vite + React app under `app/`. Its single-file build is vendored beside the engine as `plugin/scripts/_map_viewer.html` (carries a `<!--REQMAP_DATA-->` marker); the stdlib engine injects each repo's `_map.json` into that marker to produce `_map.html`. So the engine ships a rich UI without itself depending on Node/npm — and emits only `_map.md` + `_map.json` if the template is absent.

**Each node carries the acceptance section twice, and the two are not interchangeable:** `accept` is the labelled Given/When/Then block as authored, `acc` the same criteria folded to one line each. The viewer renders `accept` (`adaptNode` in `app/src/lib/loadData.js` → `gwt`); `acc` exists for search and counting. Gating the block render on `acc` being empty is what silently collapsed every criterion into a run-on line the moment `_acc_blocks` learned to parse the block form (v2.29.0 → fixed in v2.29.2, `ARCH-VIEWER-007` AC-8).

See `app/CLAUDE.md` for rebuilding the vendored viewer after `app/` changes.

**Scanning scope:** one walk (`scan_all`, cached under `--cache` for members, `verifies:` coverage and test levels alike; `scan_members` is a view of it) over `.py .js .ts .tsx .jsx .mjs .cjs .mts .cts .c .cpp .h .hpp .cc .java .go .rs .cs .php .rb .kt .kts .swift .scala .ex .exs .dart .vue .svelte .html .css .scss .sass .less .sql .yaml .yml .toml .sh .tf .prisma .graphql .proto .md` plus the basenames `Dockerfile Makefile Caddyfile Jenkinsfile Procfile Vagrantfile`, `Dockerfile.*` variants and git hook names (`.md` so prose capabilities — prompts/specs — can carry membership tags). Respects `.reqmapignore` (fnmatch globs); a pattern ending in `/**` or `/*` also prunes the walk. Prunes `.git`, `node_modules`, `__pycache__` automatically — **but not other dot-directories**, which is why `_reqmapignore_seed` (`ARCH-INIT-012`) seeds `.worktrees/**` and `.claude/worktrees/**` into a consumer's file: an isolated subagent worktree is a full second copy of the repo, so an unignored one counts every member twice and reports the copies' tags as dangling ERRORS that a clean CI checkout never sees. Same reason this repo's own root `.reqmapignore` carries them. A tag in any other file type is reported by the gate (`ARCH-UNSCANNEDTAG-045`), not silently lost. Non-code capability *discovery* (`plan --md-glob`, internally `cmd_candidates`) is separate and opt-in.

## Plugin packaging

`plugin/.claude-plugin/plugin.json` is the manifest. The plugin is published to a marketplace manifest at `.claude-plugin/marketplace.json` (repo root).

**Two independent version numbers — don't conflate them:**
- **Plugin semver** lives in *three* places kept in lockstep by `check_versions.py`: `version` in `plugin.json`, plus the top-level `version` and `plugins[].version` in `marketplace.json`. **Any** shipped change — engine *or* a skill edit — must bump this semver, or installed copies won't pick it up via `/plugin update` (a skill edit with no bump is silently invisible to consumers).
- **`MAP_ENGINE_VERSION`** inside `reqmap.py` (ISO date `YYYY-MM-DD`, optional `.N` same-day suffix, e.g. `2026-06-03.2`) is engine-only — it lets a seeded copy of `reqmap.py` detect it is behind. Bump it on **every** change to `reqmap.py`, comments included (the staleness probe compares files, not behaviour); `scripts/check_engine_bump.py` enforces this in CI (`--base HEAD~1`) and in the dev hook (`--staged`).

**A semver bump must ship with a CHANGELOG entry.** CI fails the build when `plugin/.claude-plugin/plugin.json`'s version changed in the commit but `CHANGELOG.md` has no heading containing `` `vX.Y.Z` `` (the backticked form is what the grep matches). On pushes to `main` the `release` job then cuts tag `vX.Y.Z` from `plugin.json` — idempotent, so a non-bumping push creates nothing — with notes extracted from that same CHANGELOG section by `scripts/changelog_notes.py`. Tags therefore follow `plugin.json`, never the other way round.

The skill contract (authoritative on authoring rules, statuses, and the gate) is `plugin/skills/requirement-manager/SKILL.md`.

**GitHub Action (`check/action.yml`):** published as `alxmax/requirement-manager/check@v2`. The `@vN` alias is a third version axis, independent of the plugin semver and of `MAP_ENGINE_VERSION`. It is **not** hand-pushed any more: the `release` job force-moves it onto every commit it tags, and `check_versions.py` asserts the major named in `check/action.yml`, `README.md`, this file and the two `requirement-manager` `SKILL*.md` files agree (the documented `uses:` line is the source of truth — there is no separate version file). Bump the major by editing those five references in one commit, and only for a change that breaks an existing caller — adding a default-on step counts, which is why `@v1` (gate-only, frozen at v2.1.0 content) was left in place rather than re-pointed. Consumer repos use it as:
```yaml
- uses: alxmax/requirement-manager/check@v2
```

The action also ships `check/engine_staleness.py` (`ARCH-STALEENGINE-043`): it compares the
consumer's vendored `MAP_ENGINE_VERSION` against the engine in the action's own checkout and
annotates the run when the vendored copy is behind — the CI half of `warn_if_stale`, which is
silent outside a Claude Code session. It deliberately did **not** take the major to `@v3`: the
rule above is about a step that can newly FAIL a green build, and this one is warn-only
(`stale-engine: warn|error|off`, default `warn`) and fails open on anything unexpected. Bumping
would have stranded exactly the stale-pin consumers it exists to reach. Its test lives at
`scripts/test_engine_staleness.py` — the probe never runs in this repo's own CI, so that suite
is the only thing exercising it before it ships.
