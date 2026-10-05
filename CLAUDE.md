# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Engine commands run from `plugin/` (the engine resolves paths relative to its working directory). The CLI has six verbs — `init`, `gate`, `sync`, `clarify`, `ask`, `mcp` — and everything else is a flag of one of them; `python scripts/reqmap.py <verb> --help` lists each verb's flags. A verb refuses a flag the registry gives another verb (exit 2, naming the owner).

```bash
python scripts/reqmap.py gate --full --code ..   # THE verdict: link sync + drift + test links, readability, committed-map freshness. Report-only. CI and the hook run --full
python scripts/reqmap.py sync --code ..          # rebuild everything derived: lock, _map.*, _findings.md, integration artifacts
python scripts/reqmap.py sync --code .. --accept-drift   # required after editing a CONFIRMED contract, or sync demotes it to draft
python scripts/reqmap.py gate --risk             # what to do next: health + risk buckets + test gaps + the plan's gaps
python scripts/reqmap.py gate --show ID          # one requirement's dossier
python scripts/reqmap.py sync --release          # cut the next planned version (plan first, --apply to write, tagging stays in CI)
```

**`gate` and `sync` must carry `--code ..`** so the scan reaches the repo root (`docs/`, `.github/`, `.githooks/`, root `scripts/`) under the repo-root `.reqmapignore` (kept separate from `plugin/.reqmapignore` — see that file's comment). The committed `_reqlock.json`/`_map.json`/`_map.md` are generated from this widened scan: member paths are `code_root`-relative, so a run without `--code ..` reports every path one level off and fails freshness. `.githooks/pre-commit` runs from the repo root and passes `--code .` — same target. Read-only questions (`gate --show`, `ask`, `clarify`) work either way.

A confirmed requirement whose members all live outside `plugin/` (e.g. `ARCH-SELFGATE-039`: CI workflow, `check/action.yml`, the git hooks, `sync_reqmap.sh`) ERRORs under a bare `gate` with no `--code ..`, because the narrow scan never reaches its tags. Accepted and permanent: CI and the hook always run widened.

**Confirming a requirement is a human's answer, not a command:** edit `status:` in the frontmatter after someone has read it. RM006 errors on a confirmed requirement with no `implements:` member.

### Tests

Stdlib `unittest`, no install. On Windows always pass `-X utf8` — the suites print non-ASCII and fail on cp1252.

```bash
python -X utf8 scripts/test_reqmap.py                          # from plugin/: the whole suite (entry point; the parts are test_reqmap_*.py)
python -X utf8 -m unittest test_reqmap_gate -v                 # one part, from plugin/scripts/
python -X utf8 -m unittest test_reqmap_gate.PlanInput -v       # one class or test
```

The viewer's tests and rebuild are in `app/CLAUDE.md`; any `app/` change needs `npm run build:viewer`, then `sync`.

From the **repo root**, the packaging side:

```bash
python scripts/check_versions.py [--fix]          # plugin.json semver == marketplace.json (x2), Action major, MAP_ENGINE_VERSION shape
python scripts/check_engine_bump.py --base main   # reqmap.py or reqmap_engine/ changed => MAP_ENGINE_VERSION changed
python scripts/check_engine_budget.py             # core logical-line budget + physical ceiling
python -X utf8 scripts/test_check_versions.py
python -X utf8 scripts/test_check_engine_bump.py
python -X utf8 scripts/test_changelog_notes.py    # CI runs it with cwd=scripts/
python -X utf8 scripts/test_cross_tool.py         # seeds the engine into a tempdir, runs sync -> gate -> map
python -X utf8 scripts/test_engine_staleness.py   # the only thing that exercises check/engine_staleness.py before it ships
```

### CI and hooks

- `gate-and-tests` (ubuntu) is the single authoritative verdict: `check_versions.py` → `test_check_versions.py` → `test_changelog_notes.py` → CHANGELOG-entry check → `gate --code ..` → `test_reqmap.py`. The gate must pass (0 errors) before committing a change to the engine or any requirement.
- `tests` is the portability matrix (3.9/3.12/3.13 × ubuntu/windows) and runs every suite, nothing else. `release` needs both; `deploy-map` needs only the gate.
- `quality` measures, it does not verify: `coverage` and `ruff`, pinned from PyPI. Only `ruff --select E9,F` can fail it; other rules are advisory because several describe deliberate choices (`except Exception: return None` IS the fail-open contract in a dozen places). It is deliberately not in `release`'s needs, and there is no coverage floor yet, on purpose.
- **Python floor 3.9** (`MIN_PYTHON`, `ARCH-PYFLOOR-040`) is the oldest version CI runs, not the oldest the code works on. Raising it means moving the matrix and `MIN_PYTHON` together — a test asserts they match.
- **Two hook files, don't confuse them:** `.githooks/pre-commit` is this repo's dev hook (`check_versions.py` → `check_engine_bump.py --staged` → `gate`; enable with `git config core.hooksPath .githooks`; `.githooks/pre-push` blocks direct pushes to `main`). `plugin/hooks/pre-commit` is shipped to consumer repos — editing it changes consumer behaviour and needs a semver bump.
- `sync_reqmap.sh` refreshes an EXISTING vendored engine (+ viewer template) in the plugin cache and in consumer repos passed as args; it never seeds one.

## Architecture

The repo is a Claude Code plugin shipping two skills under `plugin/skills/`: `requirement-manager` (its `SKILL.md` / `SKILL.universal.md` are entry points that load `references/workflow.md`, the authoritative contract on authoring rules, statuses and the gate) and `requirement-quality-review` (advisory, never part of the gate). It dogfoods itself: `plugin/requirements/` describes the engine's own capabilities.

**Design decisions live in `docs/adr/`** (index at `docs/adr/README.md`). Read the relevant record before proposing a change that reverses one; each names its evidence and revisit condition. A decision that changes gets a NEW record superseding the old one — never an edit to the old one.

**The engine is a package behind a thin CLI** (ADR-0035). `plugin/scripts/reqmap.py` is the command line only — parser, dispatch, the Python floor, and the flat namespace `import reqmap` offers (a module-level `__getattr__` looks any engine name up across the package, so `R.LINT_AC_MAX` works). `plugin/scripts/reqmap_engine/` holds the logic, 71 modules beside `__init__.py`, one per capability, stdlib only. Seeding copies `reqmap.py` AND `reqmap_engine/` together.

- **Shape by convention:** no file over 500 lines, no line over 100 columns.
- **Size is budgeted** (ADR-0053): `check_engine_budget.py` derives CORE — the modules `sync` + `gate --full` load — and fails above `CORE_LOGICAL_BUDGET` (logical lines, so rewrapping costs nothing) or above `TOTAL_LINE_CEILING` physical lines. Budgets move down only with the cut that earns it, in the same commit. A capability only some commands need is imported at call time (`plandrift`, `planschema`, `release`, `testgaps`, `init`, `levelshape` are in `_LAZY_MODULES`), so it stays out of CORE.
- **Layering is a bus, imported by name, never upward:** `config → model → parse/sections/acceptance/text → tags/scan/orphans → git → locks → (features) → workspace → rules → gate → reqmap.py`. Two documented call-time imports break the direction on purpose: `health._link_sync_errors` → `rules` (the gate's map rule embeds the health record) and `risk._plan_gaps` → `mapdata` (`mapdata` reads `_risk_signals` from `risk`).
- **Every `_config.json` tunable lives in `config.py` and is read as `cfg.NAME`** — a name import snapshots the default and misses the override.
- **A test that patches an engine name patches the module that looks it up** (`R.git._git`, not `R._git`).
- **An extracted helper keeps a copy of the parent's `# implements:` line** as the first line of its body, or the member sidecar loses coverage of the moved code.
- **`MAP_ENGINE_VERSION` lives in `reqmap_engine/__init__.py`**, which every probe reads first (falling back to `reqmap.py` for a single-file copy seeded before v7).

**The command registry is the CLI's SSOT** (`COMMANDS` in `reqmap_engine/commands.py`). `plugin/tool_definition.json` and the command-table region in `SKILL.universal.md` are GENERATED from it — never hand-edit them; `gate` warns when they are stale.

**Gate rules** are registered with `@gate_rule("RMnnn", severity, strict=...)` into `GATE_RULES` and run over one `GateContext`; registration order is output order, and a test pins it. Codes are permanent (a consumer writes `gate_exempt: [RMnnn]`), so a retired number is never reused. Bare `gate` runs only `DEFAULT_RULES` — what says something is broken (ADR-0049); `--full` and `--audit` run everything. Errors (exit 1): RM001 dangling tag, RM002 bad frontmatter, RM003 missing `depends_on` target, RM006 enforced requirement with no `implements:`. Drift (RM018/RM019), test links (RM012) and plan input (RM037) warn and are promoted by `--strict`. `gate` never touches `_reqlock.json`; `sync` advances it. RM013 checks a requirement's cases only once one `# verifies:` tag exists — a requirement with none is named by `gate --risk` instead. `Requirement` and `Finding` are dict subclasses carrying derived facts — no class hierarchy.

**Code tagging:** `# implements: ID`, `# tested-by: ID`, `# verifies: ID#CASE-N`. `TAG_RE` has a left-boundary guard so `reimplements:` is not a tag. Members are discovered by scanning, never hand-kept. The scan prunes `.git`, `node_modules`, `__pycache__` but NOT other dot-directories — which is why `.worktrees/**` and `.claude/worktrees/**` are in `.reqmapignore` here and seeded into consumers': a subagent worktree is a full second copy of the repo and doubles every member, reporting the copies as dangling ERRORS a CI checkout never sees. A tag in an unscanned file type is reported (RM023), not lost.

**Per-repo configuration:** `requirements/_config.json` overrides the names in `CONFIG_KEYS`, read fail-open; a bad file, unknown key or wrong type is reported on stderr and skipped, and the bare gate carries it as an `INPUT:config` warning that `--strict` makes an error (ADR-0054). This repo ships none.

## The requirement corpus

**Two orthogonal axes — never merge them.** `layer:` is the graph position: `bus` (foundation, high fan-in), `feature` (one capability, composes the bus via `depends_on`), `need` (a stakeholder need, satisfied via `satisfies:`, no code), `aggregate` (no code, covered downward by `depends_on`). `need` and `aggregate` are exempt from the implements/tested-by gates through the one predicate `_impl_exempt`. `level:` is the V-model rung — `system` → `architecture` → `code` — linked by `satisfies:`. `IMPL_EXEMPT_LAYERS` keys on `layer`, so treating `architecture` as `aggregate` would silently exempt every architecture requirement from the confirmed-must-have-code gate.

Ids carry their level here (`SYS-` → `ARCH-` → `REQ-`) as a reading convenience only; the engine reads `level:`, and a consumer may name ids anything. `level:` is opt-in (ADR-0019, with a dated review on **2027-03-03** that says a field no consumer sets should be removed). This corpus: <!--reqmap:level:system-->10 `SYS-*` needs, <!--reqmap:level:architecture-->67 `ARCH-*` capabilities (`tested-by: <id> @integration`), <!--reqmap:level:code-->235 `REQ-*` behaviour groups (3–7 cases each, a `# verifies: <id>#CASE-N` per case) — <!--reqmap:total-->312 requirements in <!--reqmap:files-->77 files. Each `ARCH-*.md` holds the architecture requirement followed by its `REQ-*` children; a block starts at a `---` line immediately followed by `id:`, and only block 0 may fall back to the filename for its id. A description of this repo, not a shape the tool asks anyone to build.

**Old ids in `docs/adr/` and `CHANGELOG.md` were deliberately not rewritten** — they record what was true on a date. Read one by matching stem AND number (`REQ-VLEVEL-037` → `ARCH-VLEVEL-037`, `NEED-SSOT-001` → `SYS-SSOT-001`); the number alone is not unique.

**Requirement schema:** frontmatter (id, status, level, layer, owner, satisfies, depends_on; optional priority/milestone/lint_exempt/test_exempt/gate_exempt — no comments, no empty keys), parsed by a hand-rolled parser (scalars and inline lists only). Body in the lean form: `## Description` (an intent quote, then `Every bullet below is binding.` and the clauses), `## Cases` (`CASE-N — title`, Given/When/Then), optional `## Context`. An `ARCH-*` Description is its intent plus one obligation per child ending in `[[REQ-…]]`; the detail lives only in the child. A second, atomic form (story blockquote + `Scenario:`) is detected from the body, never the frontmatter.

- **Every old spelling still parses, forever:** `CONTRACT_LABELS` / `ACCEPTANCE_LABELS` (current name first) and `_has_any`/`_from_any` are the only way to ask for either section; `CASE-N` and `AC-N` are both accepted because the label is what a consumer's `# verifies:` tag points at. Most test fixtures are deliberately in the legacy form — they are the back-compat suite; don't rewrite them.
- **The intent quote is outside the drift hash:** `binding_hash` skips `>` lines, so improving an explanation never reports DRIFT, and the linter never sees rationale.
- **Corpus-shape advice** (`next`'s Granularity and Redundancy buckets) is surfaced by `sync` and `gate --risk`, never by `gate`: it is not a commit-time concern. Redundancy ships below ADR-0016's fire-rate floor on purpose (ADR-0020).

## Generated outputs

Under `plugin/requirements/`: `_map.md`, `_map.json` (the graph the viewer reads; a node's dependency list is `depends_on`, and an older map's `deps` is still read), `_reqlock.json` (the contract-hash baseline — a byte-stable cross-repo contract an older seeded engine must still read, which is why member hashes live in the separate `_memberlock.json`), `_findings.md` — all committed. `_map.html` is regenerated from the vendored template and gitignored.

The viewer is the Vite + React app in `app/`; its single-file build is vendored as `plugin/scripts/_map_viewer.html` with a `<!--REQMAP_DATA-->` marker the stdlib engine fills with `_map.json`, so the engine ships a UI without depending on Node. Without the template it emits only `_map.md` + `_map.json`. The viewer renders a node's `accept` block as authored; never gate that render on the folded `acc` list being empty — that once collapsed every criterion into one run-on line.

**`docs/` is the published Pages root and `docs/map.html` is never committed** (ADR-0034): the engine never writes into `docs/`; the `deploy-map` job builds the published copy right before upload. `.gitignore` blocks `docs/*.excalidraw`. The README is the front door only; a fact belonging in `docs/commands.md`, `requirements.md`, `integrations.md`, `planning.md` or `internals.md` is edited THERE, never copied back. Those pages are in the root `.reqmapignore`: prose about capabilities, never members.

## Planning and releases

`ROADMAP.md` is the plan in horizons (`## Now` / `## Next` / `## Later` / `## Not now`, items `- [ ] text | req: ID` under `### Category`; every Later item needs `unpark:`). `plugin/requirements/_planning.json` is the dated plan the Gantt draws. `CHANGELOG.md` is what shipped. `sync --release` cuts the next planned milestone (ADR-0040); plan-input problems are gate warnings (RM037, ADR-0057), while the plan's content — a stale milestone, an unscheduled Now item, an overdue bar — is only reported by `sync`, `gate --audit` and `gate --risk`. See `docs/planning.md`.

## Plugin packaging

**Two independent version numbers — don't conflate them:**
- **Plugin semver** — `version` in `plugin/.claude-plugin/plugin.json` plus the top-level and `plugins[].version` in `.claude-plugin/marketplace.json`, kept in lockstep by `check_versions.py`. ANY shipped change — engine, skill, or the vendored viewer — must bump it, or installed copies never see it via `/plugin update`.
- **`MAP_ENGINE_VERSION`** (`YYYY-MM-DD`, `.N` for a second bump the same day) — bump it on every change to `reqmap.py` or `reqmap_engine/`, comments included: a seeded copy compares it to learn it is behind. `check_engine_bump.py` enforces it in CI and in the hook.

**A semver bump ships with a CHANGELOG entry** whose heading contains `` `vX.Y.Z` `` (the backticked form is what CI greps). On pushes to `main` the `release` job tags `vX.Y.Z` from `plugin.json` with notes from that section (`scripts/changelog_notes.py`); a push without a bump tags nothing. Tags follow `plugin.json`, never the other way round.

**GitHub Action (`check/action.yml`)** — consumers use it as:
```yaml
- uses: alxmax/requirement-manager/check@v8
```
The `@vN` alias tracks the plugin's major (ADR-0029); the `release` job force-moves it onto every commit it tags, and `check_versions.py` asserts the major named in `check/action.yml`, `README.md`, this file and the two `SKILL*.md` files agree. Older aliases stay where they point. `check/engine_staleness.py` warns (never fails, by default) when a consumer's vendored engine is behind; a warn-only step does not justify a major bump, because bumping would strand exactly the stale-pin consumers it exists to reach.

## Working on Windows

Bash heredocs mangle backslashes and `\n` inside Python string literals: write an edit script to a file and run it, or use the Edit tool. Never name such a script after a stdlib module (a `warnings.py` in the working directory broke an unrelated `import subprocess`).
