# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `plugin/` (the engine resolves paths relative to its working directory):

```bash
python scripts/reqmap.py init               # first-use bootstrap: scaffold + draft from code + lock + map + next-steps

# --- author ---------------------------------------------------------------
python scripts/reqmap.py new AREA-NAME-NNN  # scaffold a new requirement from the template
python scripts/reqmap.py new --from-todo "TODO name" --id AREA-NAME-NNN [--mark-done]  # scaffold from a TODO.md item
python scripts/reqmap.py init              # draft requirements from untagged legacy code (--plan: JSON dry run, writes nothing)
python scripts/reqmap.py clarify AREA-NAME-NNN  # the questions this requirement has not answered (--json). --decompose splits it into code-rung children along the bold group labels in its Description, --apply to write; with no id, every grouped requirement. A requirement with no groups gets one draft per over-long clause instead
python scripts/reqmap.py clarify --levels       # propose a V-model rung for every requirement that declares none; read-only, --apply writes them marked `level_source: auto` (ADR-0031)
# confirming is a HUMAN's answer, not a command: edit `status:` in the frontmatter
# after someone has read it. The gate enforces the invariant (RM006: confirmed with
# no implements: member is an error), and `sync` demotes an edited contract back to
# draft on its own.

# --- build ----------------------------------------------------------------
python scripts/reqmap.py gate --implement AREA-NAME-NNN  # the brief for writing its code: obligations, cases, tags, neighbouring code (--json)
python scripts/reqmap.py gate --code ..     # THE verdict: link sync + drift + test links, then requirement readability, then committed-map freshness (--no-lint / --no-map-check opt out). Report-only.
python scripts/reqmap.py sync --code ..     # rebuild EVERYTHING derived: lock, _map.*, _findings.md, the site regions, the integration artifacts. --accept-drift when a confirmed contract changed.
python scripts/reqmap.py sync --retire AREA-NAME-NNN [ID ...]  # take one requirement — or a whole class — out of service: plan first, --apply to act, --delete to remove it outright, --force past dependents. A batch retires in a graph-computed order (consumers first) under ONE working-tree check; a dependent that is already deprecated, or that is in the same batch, never blocks

# --- read -----------------------------------------------------------------
python scripts/reqmap.py gate --risk               # what to do next: health score + counted risk buckets (--json/--badge: the health numbers; --untagged: files with no implements: tag)
python scripts/reqmap.py gate --show AREA-NAME-NNN  # consolidated dossier for one requirement (contract, deps, members, risk)
python scripts/reqmap.py gate --search "query"     # rank requirements by lexical relevance (same TF-IDF cosine as dupes; --top)
python scripts/reqmap.py gate --dupes              # flag requirement pairs with overlapping contracts (TF-IDF cosine; --threshold)
python scripts/reqmap.py gate --design [--json]     # advisory design review of the repo's code (Python via ast; brace languages via heuristics): the four OOP pillars, one C&K per-class metric (RFC, Python only), plus house standards; read-only, exit 0, never the gate; thresholds in _config.json
python scripts/reqmap.py gate --review [AREA-NAME-NNN]  # emit a JSON review plan (AI-feed: intent, contract, acceptance, anchors)
python scripts/reqmap.py sync --suggest-verifies    # propose `# verifies: <ID>#CASE-N` tags for tests already named after the criterion; --apply writes them
python scripts/reqmap.py gate --show AREA-NAME-NNN  # one requirement's dossier. The EN/RO toggle in the viewer still reads requirements/_i18n/<locale>.json; the `translate` verb that WROTE that cache was removed 2026-09-05, so a refresh is now a manual step.
```

**`gate` and `sync` above already carry `--code ..`** so the scan reaches the repo root
(`docs/`, `.github/`, `.githooks/`, root-level `scripts/`), per a NEW repo-root `.reqmapignore`
(kept separate from `plugin/.reqmapignore` — see that file's own comment for why). This is not
optional for these two: the *committed* `_reqlock.json`/`_map.json`/`_map.md`
are generated from the widened scan (member `loc` paths are `code_root`-relative, so a copy
generated without `--code ..` reports every existing member's path one level off and fails
freshness checks against the real committed files). `.githooks/pre-commit` already runs from
the repo root, so it passes `--code .` instead of `--code ..` — same target, different starting
cwd. Read-only exploration commands with no committed-artifact freshness concern (`show`,
`search`, `next`, `dupes`, `review`, `clarify`, `implement`) are unaffected either way and can be
run with or without `--code ..` depending on what you want to inspect.

**A `confirmed` requirement whose members all live outside `plugin/`** (e.g. `ARCH-SELFGATE-039`,
whose 5 members are `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/pre-commit`,
`.githooks/pre-push`, `sync_reqmap.sh`) can now only pass `gate`'s implements-tag check under the
widened scan. Running the bare `gate` (no `--code ..`) genuinely ERRORs on such a requirement —
not a silent miss, a real exit-1 failure — because the narrow scope never reaches any file that
proves the tag exists. This is an accepted, permanent consequence of the widened-scan design, not
a bug: CI and the pre-commit hook always run widened, so it never fires there; a human running the
bare command locally sees a loud, immediately-diagnosable error rather than a silent divergence.

The regression suite is five files: `test_reqmap.py` is the entry point and re-exports
`test_reqmap_common` (shared fixtures), `test_reqmap_scan` (parser, scanning, masking, walk,
git), `test_reqmap_gate` (gate rules, drift, `--since`, test links), `test_reqmap_author`
(new/init/lint/clarify/retire) and `test_reqmap_report` (map, viewer, site, health, audit,
design). ADR-0014 keeps the ENGINE in one file and says nothing about the tests. Every
documented invocation still goes through `test_reqmap`; a part also runs on its own.

Run tests (stdlib unittest, no install needed). On Windows always pass `-X utf8` — the suites print non-ASCII and fail on cp1252:

```bash
python scripts/test_reqmap.py                                      # from plugin/scripts/ or plugin/
python -X utf8 -m unittest test_reqmap.Gate.test_name -v           # single test/class (run from plugin/scripts/)
python -X utf8 -m unittest test_reqmap_gate -v                     # one part on its own
python scripts/reqmap.py gate --code ..                            # includes the freshness check: fails if the committed _map.* is stale
```

From the **repo root** (not `plugin/`) — the packaging/release side:

```bash
python scripts/check_versions.py        # plugin.json semver == marketplace.json (x2); validates MAP_ENGINE_VERSION shape. --fix syncs.
python -X utf8 scripts/test_check_versions.py
python scripts/check_engine_bump.py --base main   # reqmap.py changed => MAP_ENGINE_VERSION must have changed (CI: --base HEAD~1; hook: --staged)
python -X utf8 scripts/test_check_engine_bump.py
python -X utf8 scripts/test_changelog_notes.py    # release-notes extraction (CI runs it with cwd=scripts/)
python -X utf8 scripts/test_cross_tool.py         # seeds the engine into a tempdir, runs sync→gate→map: the AI-agnostic falsification test
```

**Python floor: 3.9** (`MIN_PYTHON` in `reqmap.py`, `ARCH-PYFLOOR-040`). It is deliberately the oldest version CI runs, not the oldest the code happens to work on (3.7): a floor nothing tests is a claim, not a guarantee. `reqmap.py` refuses an older interpreter with one readable line and exit 2. Raising it means moving the matrix and `MIN_PYTHON` together — a test asserts they stay equal.

CI has **two** test surfaces, don't confuse them: `gate-and-tests` (ubuntu, `3.x`) is the single authoritative verdict on this repo's requirement corpus; `tests` is the portability matrix (3.9/3.12/3.13 x ubuntu/windows) that runs every suite and nothing else. `release` needs both; `deploy-map` needs only the gate.

A third, non-authoritative job — `quality` — measures the engine rather than verifying it: `coverage` over `test_reqmap.py` (92% at the time of writing) and `ruff`, both published to the run's job summary. Only `ruff --select E9,F` (syntax errors, undefined names) can fail it; every other rule is advisory, because several ruff complaints describe deliberate choices here (`except Exception: return None` IS the fail-open contract in a dozen places). It is the only job that installs from PyPI, both tools pinned, and it is deliberately **not** in `release`'s `needs` — the authoritative verdicts stay dependency-free. There is no coverage floor yet, on purpose: publish the number first.

The gate must pass (`0 errors`) before committing changes to `reqmap.py` or any requirement file. CI (`.github/workflows/ci.yml`, job `gate-and-tests`) runs, in order: `check_versions.py` → `test_check_versions.py` → `test_changelog_notes.py` → the CHANGELOG-entry check → `reqmap.py gate --code ..` (which since `v4.0.0` *is* the lint and the map-freshness check as well) → `test_reqmap.py`.

**Hooks — two different files, don't confuse them:**
- `.githooks/pre-commit` is *this repo's dev* hook, mirroring the CI order (`check_versions.py` → `check_engine_bump.py --staged` → `gate`). Enable once: `git config core.hooksPath .githooks`. `.githooks/pre-push` also blocks direct pushes to `main`.
- `plugin/hooks/pre-commit` is the hook **shipped to consumer repos** — editing it changes consumer behaviour and needs a semver bump.

`sync_reqmap.sh` propagates `plugin/scripts/reqmap.py` (+ the vendored viewer template) into the local plugin cache and any consumer repos passed as args; it only refreshes an *existing* vendored engine, never seeds one.

## Architecture

This repo is a Claude Code plugin that ships **two skills** under `plugin/skills/`:
- `requirement-manager` — the core skill; seeds `reqmap.py` into a target repo and drives the SSOT/drift workflow. Its `SKILL.md` is the authoritative contract.
- `requirement-quality-review` — on-demand AI *advisory* review of requirement files' semantic quality (is a clause testable, does the WHY explain intent). Never part of the gate (`implements: ARCH-REVIEW-022`).

**Diagrams of this repo** are no longer generated here. The `excalidraw-diagram` skill was
split out at plugin `v6.1.0` into [its own repository](https://github.com/alxmax/excalidraw-diagram) — it shared this one and
nothing else, with no imports in either direction. `docs/` stays the published Pages root and
holds only reviewed, self-contained HTML; `.gitignore` still hard-blocks `docs/*.excalidraw`.

The repo dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Design decisions live in `docs/adr/`** (31 records, index at `docs/adr/README.md`) — the single-file engine (and `0014`, why it is not split and carries no size gate), the error-versus-warning split, the drift-baseline shape, the V-model (`0007` parked it, `0019` supersedes it by adopting the left arm warn-only), and four rejected proposals. Read the relevant record before proposing a change that reverses one; each names the evidence it was decided on and its revisit condition. A decision that changes gains a NEW record superseding the old one — never an edit to the old one.

**Single engine file:** `plugin/scripts/reqmap.py` — 10,604 lines measured 2026-09-06, stdlib only, no external dependencies. Its size is a settled question, not an open one: see `docs/adr/0014` (no split, no line-count gate, numeric re-open triggers). All logic (parse, scan, gate, map, draft, plan, findings, init, next) lives here. This is intentional — hermetic deployment into any repo without install friction.

**Command registry is the CLI's SSOT** (`COMMANDS` dict near the top of `reqmap.py`, `ARCH-CMDREGISTRY-033`): one entry per command (summary, positional arg, flags). `plugin/tool_definition.json` (OpenAI function-calling schema, for non-Claude assistants) and the command-table region in `skills/requirement-manager/SKILL.universal.md` are **generated** from it by `gen-integration` — never hand-edit those two. `gate` warns when they are stale relative to the registry.

**Requirement layers:**
- `layer: bus` — foundation capabilities (config, parsing, scanning, drift detection). High fan-in; change behind their contract.
- `layer: feature` — compose the bus via `depends_on`. One per user-facing command (new, scan, gate, sync, map, draft, plan, findings, init, next, confirm, lint, show, dupes, search, health, coverage, site, review, …); `ls plugin/requirements/` is the live list.
- `layer: need` — an upstream stakeholder need (`SYS-SSOT-001`), satisfied-by feature requirements via `satisfies:`, not implemented by code; exempt from the implements/tested-by gates (see `ARCH-TRACE-020`).
- `layer: aggregate` — the mirror image: no code of its own, covered *downward* by a non-empty `depends_on` (it asserts its dependencies work together). Exempt from the same gates via the one predicate `_impl_exempt`, which `gate`, `health`, the risk map and `confirm` all read — they disagreed before (`docs/adr/0015`).

**Specification levels — `level:` is a SECOND axis, orthogonal to `layer:`.** `layer` is the graph position (fan-in: bus/feature/need/aggregate); `level` is the abstraction rung of the V-model's left arm: `system` → `architecture` → `code`. They are not aliases and must not be merged — `IMPL_EXEMPT_LAYERS` keys on `layer`, so treating `architecture` as `aggregate` would silently exempt every architecture requirement from the confirmed-must-have-code gate. The hierarchy edge is `satisfies:` (level axis); `depends_on:` stays the composition axis. Only `satisfies:` forms the pyramid the 5–20 fan-out rule and the `_mermaid_hierarchy` diagram read.

**Ids carry their level, since 2026-09-03:** `SYS-` → `ARCH-` → `REQ-`. The prefix is a reading convenience for *this* corpus, not something the engine parses — `level:` in the frontmatter is the authority, and a consumer repo may name ids anything. Renaming was one mechanical prefix swap over 681 ids, keeping every tail (`STEM-NNN`) intact.

**Three levels, since 2026-09-03 (`docs/adr/0025`, superseding `0024`'s one-day promotion) — this corpus's shape, NOT a shape the tool asks anyone else to build:** 9 `SYS-*` stakeholder needs at `level: system` (`layer: need`, satisfied by ARCH nodes, verified by `validated-against:`), 68 `ARCH-*` capabilities at `level: architecture` (one command or one shared engine capability, `tested-by: <id> @integration`), 159 `REQ-*` behaviour groups at `level: code` (3-7 labelled cases each, `# verifies: <id>#CASE-N` per case). 236 requirements in total. `level:` is opt-in and stays opt-in: the template ships it commented out, nothing in the engine infers it (ADR-0019: the axis is one *the author declares*, not one the engine deduces), and a corpus that declares none gates identically to a run from before the field existed (`ARCH-LEVEL-051` CASE-3). ADR-0019 carries a dated review — **2027-03-03** — that says a field no consumer repo sets should be *removed rather than documented harder*. Read the counts below as a description of this repo, not as a target; `gate --audit` reports any corpus's rung distribution and states in its own output that adopting the axis is a decision, not a defect. `fan-out`'s `system` ceiling is ten again (`LINT_FANOUT_BANDS`). The 573 one-sentence atomic leaves of the same morning were folded into the 126 `REQ-*` groups; their ids (`REQ-…-233` … `-815`) are historical, the folded children start at 821.

**Translating an old id.** `docs/adr/**` and `CHANGELOG.md` were deliberately NOT rewritten: they record what was true on a date, and an ADR citing `REQ-VLEVEL-037` is a correct statement about 2026-08-17. To read one, match the tail: `REQ-VLEVEL-037` → `ARCH-VLEVEL-037`, `CORE-PARSE-001` → `ARCH-PARSE-001`, `NEED-SSOT-001` → `SYS-SSOT-001`. Tails are unique across the corpus, so the lookup is unambiguous. A decision that changes still gets a NEW ADR — never an edit to an old one, prefixes included.

**Requirement schema** (`plugin/requirements/*.md`): YAML frontmatter (id, status, level, layer, owner, satisfies, depends_on; optional priority/milestone/lint_exempt/test_exempt — no comments, no empty keys) + prose body in the **lean form**: `## Description` (an intent quote for a developer new to the repo, then `Every bullet below is binding.` and the clauses), `## Cases` (`CASE-N — title`, Given/When/Then), optional `## Context`. No `## Verify intent`, `## Links` or `## Members in code (auto)` on a confirmed requirement. An `ARCH-*` Description is its intent plus one obligation sentence per child ending in `[[REQ-…]]`; the detail lives only in the child. Two body forms coexist and the engine detects which from the body, never from the frontmatter: the **sectioned** form and the **atomic** form (`form: atomic`) — a story blockquote plus a `Scenario:` block, with no normative headings at all. `binding_hash` hashes the normative heading span for the first and the story+scenario span for the second; a form it cannot recognise would hash the empty string, which is why `_atomic_spans` is consulted before the fallback. The frontmatter parser is hand-rolled (scalars + inline lists only — no full YAML library).

**Section names — `## Description` and `## Cases`, since 2026-09-03** (`ARCH-DESCRIPTION-057`). `## Description` merged the standalone `> WHY:` blockquote with `## WHAT — Contract (normative)`: the same capability was described twice, as rationale and as obligation, under two headings that both said WHAT. The quote now opens the section and the binding clauses follow it. `## Cases` (labels `CASE-1`, `CASE-2`, …) replaced `## HOW — Acceptance (= tests)` and `AC-N`. `## Verify intent` and `## Notes` simply dropped a `WHAT —` prefix that no longer named a section.

**Every old spelling still parses, forever.** `CONTRACT_LABELS = ("description", "contract")` and `ACCEPTANCE_LABELS = ("cases", "acceptan")` are the SSOT — current name first — and `_has_any`/`_from_any` are the only way a call site should ask for either section. `AC_VERIFY_RE` and `_AC_LABEL_RE` accept `CASE-N` and `AC-N` alike, because the label is an **identifier a `# verifies:` tag points at**: dropping the old spelling would break every consumer tag already written. Most fixtures across the suite are deliberately left in the legacy form — that is the back-compat suite, and rewriting them would delete the only coverage of the older shape.

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
- `_map.json` — `{engine_version, nodes, edges}` registry graph; consumed by the viewer and any external front-end; also written standalone by `export` *(committed)*. **A node's dependency list answers to two names**: `deps`, the historical key the vendored viewer reads (`n.deps` in `app/src/lib/loadData.js`), and `depends_on`, the name the frontmatter and every document use — same list, emitted twice, because a consumer that asked for the documented name used to get a silent `None` and build the wrong graph from it. `used_by` is its inverse and has no frontmatter spelling; `satisfies`/`satisfied_by` are the level axis.
- `_map.html` — a self-contained single-file copy of the React viewer (`app/`) with this repo's `_map.json` inlined; opens by double-click, no server. *Regenerable (template + `_map.json`), gitignored — not committed.*
- `_reqlock.json` — content hash baseline for drift detection (one hash per requirement = the contract; prose-ahead-of-code direction) *(committed)*
- `_memberlock.json` — versioned sidecar (`{_schema, members}`) of dedicated-member content hashes for reverse-direction (member-ahead-of-spec) drift; kept separate so `_reqlock.json` stays a byte-stable cross-repo contract an older seeded engine reads unchanged (`ARCH-MEMBERDRIFT-027`) *(committed)*
- `_findings.md` — aggregated verify-intent triage *(committed; `map`/`sync` refresh it once it exists, `map --check` flags it stale)*

**One rendered map, and `docs/map.html` is not committed** ([ADR-0034](docs/adr/0034-one-rendered-map-built-where-it-is-published.md), plugin `v6.0.0`). The engine writes exactly one viewer, `requirements/_map.html`, and never writes into `docs/`. The published copy is BUILT in the `deploy-map` job — `sync`, then `cp _map.html docs/map.html`, then `sync` again so the site page's NAV sees it — immediately before the Pages artifact is uploaded, so it cannot go stale and never enters a commit. It was a byte-identical 2.1 MB duplicate rewritten in 249 commits. `docs/` is still the Pages root (committed: `architecture.html`, `full_architecture.html`, `index.html`, `.nojekyll`); the job publishes via OIDC on pushes to `main` and still refuses to publish a `map.html` under 10 KB.

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

**GitHub Action (`check/action.yml`):** published as `alxmax/requirement-manager/check@v6`. The `@vN` alias **tracks the plugin's major** since [ADR-0029](docs/adr/0029-action-alias-tracks-the-plugin-major.md): `check@v6` ships with plugin `4.x`. It was a third, independent axis until then, which is why `@v2` lived across 2.x through 3.4 — sound in itself, and one number too many to hold. It is **not** hand-pushed any more: the `release` job force-moves it onto every commit it tags, and `check_versions.py` asserts the major named in `check/action.yml`, `README.md`, this file and the two `requirement-manager` `SKILL*.md` files agree (the documented `uses:` line is the source of truth — there is no separate version file). The major moves with every plugin major, whether or not the Action's own interface changed; `check_versions.py` now asserts the two agree. Older aliases stay where they point (`@v1` is gate-only, frozen at v2.1.0 content), so a pinned consumer keeps the engine that was current then. Consumer repos use it as:
```yaml
- uses: alxmax/requirement-manager/check@v6
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
