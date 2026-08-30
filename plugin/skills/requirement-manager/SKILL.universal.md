---
name: requirement-manager
description: >
  Use when working on a project that needs a single source of truth for
  requirements/capabilities — especially with multiple agents or vibe coding,
  to prevent drift between code, docs and intent and to avoid duplicated /
  divergent implementations. Use to create or reconcile requirements, run the
  drift gate before a commit/merge, generate the requirement map, or extract
  draft requirements from legacy code. Trigger words: requirement, SSOT, spec,
  capability, drift, reconcile, "what does this do", "where is X implemented".
---

<!-- Universal variant: Claude Code-specific tool invocations and path variables
     removed. Works with any AI assistant that can run shell commands. -->

# Requirement manager

A capability registry that sits between intent and code. Each capability is one
markdown file (the single source of truth). Code points back to it with a tag.
A script reconciles the two and generates a navigable map.

## Menu (entry point)

When invoked, choose one of two paths:

- **With an action argument** (e.g. `requirement-manager sync`) — skip the
  menu and run that action directly. Accepted arguments: `setup`,
  `draft`, `sync`, `confirm`, `update-engine`, `triage` (hyphen or space,
  case-insensitive).
- **Bare** (no argument) — present the six actions below as a numbered list,
  ask the user which one to run, then run it.

All actions run from the repo root where `scripts/reqmap.py` is vendored (see Setup).
After any action, summarize what changed and, when useful, point to
`python scripts/reqmap.py next` for the best follow-up.

| Action | What it does and when to pick it | Commands to run (in order) |
|---|---|---|
| **setup** (first use in a repo) | Idempotent bootstrap: scaffold `requirements/` and `.reqmapignore` if missing, draft new requirements for any untagged code/prose, then rebuild the lock + map. Pick this when the repo has never had a requirement registry. Existing requirement files and membership tags are **preserved**. Never clobbers `.reqmapignore`. | `python scripts/reqmap.py init` |
| **draft** (discover missing requirements) | Discovery pass: draft new requirements for any untagged code/prose files. Pick this when code has grown since the last extraction and you want to catch new untagged capabilities. Existing requirement files and membership tags are **preserved**. Covers code and prose (`.md`/`.html`). After drafting, run `gate` and report the draft count + gate result (`N errors`). Remind the user to review + `confirm` the real ones. | `python scripts/reqmap.py draft` → `gate` → report draft count + result |
| **confirm** (validate a reviewed requirement) | Human-validation step: flip a reviewed requirement's `status` to `confirmed`. Pick this when you have reviewed a `draft` or `baseline` requirement and verified its contract matches the code's actual behaviour. The engine refuses if the requirement has no `implements:` member (a confirmed requirement must point to code). After confirming, run `sync`. | 1. Tag the implementing file: add `# implements: <ID>` (and `# tested-by: <ID>` if there's a test). 2. `python scripts/reqmap.py confirm <ID>`. 3. `python scripts/reqmap.py sync`. |
| **sync** (refresh lock + map after edits) | Rescan code members, advance the drift baseline, and regenerate the map (plus `_findings.md`, if the repo keeps one) — all in one step. Pick this after editing requirement files or tagging new code members (i.e. whenever you want to advance the committed baseline). Use `--accept-drift` to advance an edited confirmed/implemented contract. | `python scripts/reqmap.py sync --accept-drift` (if confirmed contracts changed) or `python scripts/reqmap.py sync` (for new/draft requirements only) → advisory doc-sync |
| **update-engine** (after a plugin/package update) | Re-seed the vendored `scripts/reqmap.py` (and `scripts/_map_viewer.html` if the repo uses the viewer) from the installed plugin, then re-verify. Pick this after updating the plugin to bring the engine up to date. Report the old → new `MAP_ENGINE_VERSION`. | Copy `reqmap.py` from the plugin's `scripts/` directory into `scripts/reqmap.py` in your repo. Copy `_map_viewer.html` the same way (if you use the viewer). Then run `python scripts/reqmap.py gate` → `map`. The plugin's scripts directory is typically `~/.claude/plugins/cache/requirement-manager/requirement-manager/<version>/scripts/` on Claude Code, or wherever your tool installed the plugin. |
| **triage** (classify a vibe-coded corpus) | Classify all auto-extracted requirements as Core / Emergent / Accidental. Pick this when the corpus is vibe-coded (most requirements have `owner: auto` and none are `confirmed`). Surfaces what the tool genuinely needs vs. what AI invented. Leads to deprecate / delete decisions for Accidental requirements. | 1. `reqmap.py next` (see status). 2. Present C/E/A framework to user (see below). 3. User classifies each requirement. 4. Apply: Core → confirm path; Accidental → `deprecated` + delete; Emergent → keep as `baseline`. 5. `reqmap.py sync`. |

**Advisory doc-sync (assistant step, not the engine).** After `map`, for each
sync-only doc (bucket 2) tagged `generated-from: <ID>`, the assistant reads the doc,
its requirement(s), and the implementing code, then reports concrete mismatches
(e.g. "the HTML says quorum 6/9; the code says 7/9"). This is judgment, not a gate —
it surfaces findings and never blocks a commit. The engine's deterministic drift
flag (stale-on-change) is the hard half of doc-sync; this is the semantic half.

### Intent triage — when the corpus is vibe-coded

A vibe-coded corpus is one where most requirements have `owner: auto` and none
(or very few) are `confirmed` — the requirements were auto-extracted from code
and never validated for intent. Triage surfaces what the project genuinely needs
vs. what the AI invented during extraction, before those inventions get promoted
to `confirmed` and start blocking real work.

**When to offer proactively**: when `reqmap.py next` shows `0 confirmed` and
the majority of requirements carry `owner: auto` in their frontmatter, offer
intent triage before any other action.

**The C/E/A framework:**

- **Core** — the tool cannot work without this. Remove it and users notice
  immediately. Candidate for `confirmed` after human review.
- **Emergent** — logically implied by Core capabilities; the AI added it as a
  natural extension. Useful but not essential. Keep as `baseline`.
- **Accidental** — the AI invented it during extraction; no user asked for it
  and removing it changes nothing visible. Deprecate and delete.

**Process:**

1. Read each requirement's `## WHAT — Contract` to the user in one sentence.
2. User says C, E, or A.
3. After classifying all: apply decisions in bulk.
   - Core → leave for human review + confirm path (`reqmap.py confirm <ID>`).
   - Emergent → keep as `baseline`; no action needed.
   - Accidental → set `status: deprecated` in frontmatter; delete implementing
     code (check for load-bearing callers first with `grep` before deleting).
4. For Accidental code that IS still referenced: keep the code, strip the
   `implements:` tag, delete only the requirement file.
5. Run `reqmap.py sync` to verify.

## Setup (first use in a repo)

The engine is a single stdlib-only script, Python 3.9+ (it refuses an older interpreter
with one readable line rather than a stdlib error). Seed it into the target repo once:

```bash
mkdir -p scripts requirements
# Copy reqmap.py from the plugin's scripts/ directory:
# - On Claude Code: ~/.claude/plugins/cache/requirement-manager/requirement-manager/<version>/scripts/reqmap.py
# - On Copilot / other tools: wherever the plugin was installed; check the install path
cp /path/to/plugin/scripts/reqmap.py scripts/reqmap.py
cp /path/to/plugin/scripts/_map_viewer.html scripts/_map_viewer.html   # optional: self-contained UI viewer
```

`_map_viewer.html` is the pre-built single-file React viewer. When it sits beside
`reqmap.py`, `map` also emits a double-click-openable `requirements/_map.html` (the
full UI, this repo's data inlined, no server). It is optional — omit it and the
engine still emits `_map.md` + `_map.json`.

**Then run the one-shot bootstrap** — `python scripts/reqmap.py init` creates the
`requirements/` dir, writes a minimal `.reqmapignore` (ignoring `scripts/reqmap.py`),
drafts requirements from the existing code, builds the lock + map, and prints guided
next steps. It is idempotent (safe to re-run) and never clobbers an existing
`.reqmapignore`. The manual steps below are what `init` automates — do them by hand
only if you want finer control.

The requirement template is **built into the engine** — `reqmap.py new` needs no
template file. (Optionally, drop a `templates/requirement.md` in the repo to override
the built-in scaffold; the engine uses it automatically when present.)

**Create `.reqmapignore` immediately after the copy** — `reqmap.py` carries its own
`implements:` self-tags. Without this file the gate fails with dangling-ref errors
on the first run:

```
scripts/reqmap.py
```

Add any other vendored or generated paths that should not be scanned (one fnmatch
glob per line, `#` comments ok). The engine itself is always the first entry.

From then on every command below runs against the repo's own `scripts/reqmap.py`.
Commit both the script and `.reqmapignore` so the gate works in CI without the
plugin present.

## Core model

- **Source of truth**: one `.md` per capability in `requirements/`, with YAML
  frontmatter (machine-readable) + prose body (human-readable). Nothing else
  restates the contract — code and docs *reference* it by id, never re-describe it.
- **Optional frontmatter fields**: `milestone: vX.Y` places a requirement on the Roadmap tab (e.g. `milestone: v1.04`). It must be a version of the shape `v<digits>[.<digits>…]` — start with `v`, digits and dots only; the gate WARNs on a malformed value (advisory metadata, never build-critical). Use zero-padded minor versions (`v1.04`, not `v1.4`) to avoid ambiguity.
- **Two working layers** (think Factorio main bus + cells), plus two that carry no
  code of their own:
  - `layer: bus` — foundation capabilities, defined once, shared (telemetry,
    config, logging, an invocation primitive). Crisp output → crisp boundary.
    A bus is defined by **high fan-in**; `lint` warns on a `bus` nothing depends on.
  - `layer: feature` — capabilities that compose the bus. They `depends_on` bus ids.
  - `layer: need` — an upstream stakeholder need, covered **upward** by the
    `satisfies:` edges other requirements declare toward it.
  - `layer: aggregate` — a requirement whose implementation IS its dependencies':
    it adds no behaviour, it asserts that N capabilities work together (an MVP
    acceptance criterion is the archetype). Covered **downward** by its own
    `depends_on`, which must not be empty.
  - If you cannot tell where a requirement ends, factor the shared part onto the bus.
  - `need` and `aggregate` are exempt from the `implements:` rule — they are covered
    by an edge, not by a tag. Everything else about them is unchanged.
  - **Every layer** requires `## WHAT — Contract` and `## HOW — Acceptance` at
    `confirmed` status. Bus capabilities are not exempt — unspecified bus
    contracts are the most expensive to discover late.
- **The thread**: code declares membership with a tag, by role:
  - `implements: <ID>`       — hand-written logic (reviewed + tested on change)
  - `generated-from: <ID>`   — derived artifact (regenerated on change)
  - `validated-against: <ID>`— evidence the RIGHT thing was built (validation)
  - `tested-by: <ID>`        — evidence it was built CORRECTLY (verification)
  The member list is **discovered by scanning code**, never hand-maintained.

**Verification levels.** A `tested-by:` tag may end with the level the test sits at:
`# tested-by: AUTH-LOGIN-001 @integration`. The levels are `@unit`, `@integration` and
`@system`, and the level applies to the whole tag, so a comma-separated id list shares it.
The suffix is optional — an unlevelled tag stays valid and is never judged.

`validated-against:` answers the other question. Point a `layer: need` requirement at the
evidence the need was actually met; being *satisfied by* other requirements is not that
evidence. It carries no level, because it is the top of the V.

The gate warns in exactly two cases, both warn-only and both opt-in: a confirmed `need` with
no `validated-against:` link, once your repo uses that role anywhere, and a confirmed `bus`
requirement whose levelled links are all `@system`. Nothing fires until you annotate a tag.

## Authoring rules (read before touching anything)

### What is a capability?

A capability is a **behavior** that can fail independently — one thing a user or caller can observe breaking on its own. It is **not** a file, a class, or a module; implementation shape is irrelevant. The test: "if I removed just this behavior, would a distinct failure appear?" If yes, that is one capability.

If two behaviors live in the same file but can break in isolation (e.g. a veto path and a majority-vote path in an aggregator), they are **two capabilities** — give each its own requirement file. "One file per capability" means one *behavior per file*, not one *file per class*.

1. **Before implementing**, run `reqmap.py map` or read `requirements/` and check
   whether a capability already covers the task. If yes, extend/reuse it — do not
   reimplement. Especially check the bus.
2. **A requirement is its contract.** Fill `WHAT — Contract` (the normative,
   testable behavior) first; the boundary follows from the contract. (Legacy
   requirements may still use `Input → Description → Output`; the engine reads both.)
2a. **`confirmed` requires both `## WHAT — Contract` and `## HOW — Acceptance`.**
    A contract-only requirement has unspecified acceptance tests. An acceptance-only
    requirement has an unspecified normative contract. The gate warns on either
    omission. Both `bus` and `feature` layers are subject to this rule.
3. **Acceptance criteria are tests.** Write them as checkable statements; they map
   to `tested-by` test files.
3a. **Split heuristic (smell, not a hard limit).** If a requirement accumulates
    more than four or five acceptance criteria that cover behaviors which could
    break **independently** of each other, it is a *split candidate*. Author two
    or more requirements, each with its own contract and its own failure mode.
    `reqmap.py next` flags these. A five-AC requirement with one root cause is
    fine; a three-AC requirement covering three disjoint failure modes is already
    overloaded.
4. **One fact, one home.** Reference ids; never copy a contract into a README.
5. **Authority is one-directional**: requirement → code. If they disagree, the
   requirement wins (fix the code, or fix the requirement — never let code be the
   silent truth).
6. **Authoring is bidirectional**: you may start in code (explore), but the change
   is not "done" until the requirement is updated in the *same* commit.
7. **`## WHAT — Verify intent` asks the user, not the AI.** This section is for
   open questions that only a human reviewer can answer — contract gaps, edge cases
   not covered, design decisions left implicit, or behaviors that may be AI accidents
   (swallowed error, magic constant, unreachable branch). Write 1–3 specific, answerable
   questions per requirement. "None — doc is unambiguous." is a valid answer only when
   the contract genuinely leaves nothing open; use it sparingly. The engine treats it
   as a placeholder and `findings` skips it. Once the human answers, fold the answer
   into the Contract (or Notes) and delete the bullet — the section should shrink toward
   empty as the requirement matures.

### Prose & doc capabilities (the three buckets)

`draft`/`init` scan `.md`/`.html` by default and classify each prose file
(prose = human-readable spec/prompt text, not source code):

1. **Ignore** — meta/boilerplate (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
   `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`, `CHANGELOG.md`, `LICENSE*`,
   `_`-prefixed generated files) + anything in `.reqmapignore`. Invisible to reqmap.
2. **Sync-only** — `README*`, everything under `docs/`, and every other `*.html`
   (a `_`-prefixed generated file like `_map.json` is ignored by rule 1 first).
   Never turned into a requirement. Tag it `# generated-from: <ID>` (HTML:
   `<!-- generated-from: <ID> -->`) to make it a member: the drift gate then flags
   it stale when its requirement changes, and the advisory doc-sync step (below)
   verifies its claims still match the code.
3. **Capability source** — prompt/spec prose (`prompts/**`, `specs/**`, …).
   Auto-drafted as a `draft` stub from its title + `##` headings; review, edit and
   `confirm`. `draft` is never enforced by the gate, so unreviewed prose is never
   canonized as truth.

The buckets govern auto-drafting only — an explicit tag on any file is always
honored by the scanner.

## Audience & writing level

Write every requirement so a developer with basic programming experience but NO prior
knowledge of this project can understand it without asking questions. Rules:

1. Define each project-specific term briefly, inline, on first use — e.g.
   "veto cascade (a fixed series of checks that can block or reroute the result)".
   After the first definition, use the term freely.
2. On first mention of a named component, attach its role — e.g.
   "Conservator (the voice that looks for risk)".
3. Write contract lines in plain present tense with a named subject — "`init` creates
   the folder", never "It shall create the folder". The Contract section opens with
   "Every line in this section is binding.", so no "shall" or "must" is needed on each
   line. Keep sentences under 25 words and bullets under 22; `lint` enforces both, and
   warns (`anonymous-subject`) on a clause that opens with a bare "It".
4. Add a short "why" clause to a contract rule ONLY when the reason isn't self-evident.
   One clause, not a paragraph.
5. Keep all file and function references (e.g. `strip_context.py`,
   `aggregate_sequential()`) — they tell the reader where to look. The surrounding
   prose must explain what they do.
6. Acceptance criteria stay in Given / When / Then form.

Apply this level fully to the Contract and Acceptance sections (everyone reads these).
The "Notes & limitations" section MAY stay denser, since only deep readers reach it.

Trade-off to accept: explained requirements run ~30–40% longer than terse ones. That is
expected and acceptable.

## Statuses

- `draft`     — auto-extracted from code, unreviewed. Not enforced.
- `baseline`  — descriptive: "this is what the code does now". Not enforced
  by the gate — only `confirmed` requirements trigger drift alerts.
- `in-progress` / `implemented` — being built / built.
- `confirmed` — intent validated by a human. The gate enforces it as truth.
- `deprecated` / `superseded-by: <ID>`

## The gate (run at commit/merge — keep it non-optional)

`python scripts/reqmap.py gate` is report-only: it verifies these syncs and exits non-zero on **link-sync errors only**. It **never** touches `_reqlock.json`. To advance the drift baseline after intentionally editing a requirement, use `sync` (with `--accept-drift` when a confirmed/implemented contract changed).

| Check | Level | Effect on exit code |
|---|---|---|
| link sync (dangling tag, enforced req with no member, bad `depends_on`) | **ERROR** | exit 1 |
| test-link integrity (tested-by file missing or holds no test function) — **at every status**; strict-promoted only for `confirmed` | **WARN** | exit 0 |
| drift (confirmed contract changed vs lock, members not re-touched) | **WARN** | exit 0 |
| missing `satisfies:` for a `need` layer requirement | **WARN** | exit 0 |
| AC-coverage gap (one line per requirement: `N/M automatable criteria carry a verifies: tag`) | **WARN** | exit 0 |
| committed map stale (`_map.*`, `_findings.md`, published `docs/map.html`) | **WARN** | exit 0 |

Use `gate --strict` to promote test-link integrity and drift to errors (useful in CI
for a corpus where all requirements are confirmed and lock is current).

### Wiring the gate

**Git pre-commit hook** (one-time, per developer clone):

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
python -X utf8 scripts/reqmap.py gate
EOF
chmod +x .git/hooks/pre-commit
```

**GitHub Actions** (enforces the gate for the whole team) — use the published
action, pinned to `@v2`:

```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v2
```

Or, without the action: `- run: python -X utf8 scripts/reqmap.py gate`.

## Commands

Creation verbs (pick by input, not by outcome):
- `draft` — input is **existing untagged CODE** (or prose); auto-extracts draft requirements from it.
- `new AREA-NAME-NNN` — input is **nothing yet**; scaffolds one blank requirement from the built-in template.
- `new --from-todo "TODO name" --id AREA-NAME-NNN` — input is a **TODO.md item**; scaffolds a requirement draft pre-filled from that item. Add `--mark-done` to flip the TODO item to `[x]` at the same time.

<!--##REQMAP:COMMANDS##-->
| Command | What it does | Flags |
|---|---|---|
| `init` | First-use bootstrap: scaffold requirements/ and .reqmapignore if missing, draft requirements from existing code/prose, build the lock and map, and print guided next steps. Idempotent — safe to re-run; never clobbers an existing .reqmapignore. Run once per repo to get started. | `--wipe`, `--no-site` |
| `new` | Scaffold a new blank requirement from the built-in template. Use --from-todo and --id together to pre-fill from a TODO.md item instead. | `--id`, `--from-todo`, `--mark-done` |
| `scan` | List which code files belong to which requirement, grouped by capability. Shows all code members (implements:, generated-from:, validated-against:, tested-by:) discovered by scanning the repo. | — |
| `gate` | Run the commit/CI gate (report-only): verify every code tag resolves to a real requirement, every confirmed requirement has at least one implements: member, and drift has not been introduced since the last sync. Exits non-zero on link-sync errors only (drift and test-link integrity are warnings). Never touches _reqlock.json. Run before every commit and in CI. | `--strict`, `--json`, `--since` |
| `sync` | Rescan code members, advance the drift baseline, and regenerate the map in one step (a committed _findings.md is refreshed too). Run after editing requirement files or tagging new code members. Use --accept-drift when a confirmed or implemented contract changed. | `--accept-drift`, `--strict` |
| `check` | Deprecated alias for 'gate' (report-only) / 'sync' (with --update-lock). Preserved for backward compatibility with consumer hooks, CI, and the GitHub Action. Will be removed in the next major version — use 'gate' or 'sync' instead. | `--strict`, `--json`, `--since`, `--update-lock` |
| `map` | Generate requirements/_map.md (4 Mermaid diagrams), requirements/_map.json (graph with nodes, edges, todos), and requirements/_map.html (a self-contained React viewer). The viewer is only emitted when scripts/_map_viewer.html is vendored beside the engine. | `--check` |
| `export` | Write requirements/_map.json (the graph with engine_version, nodes, edges) for feeding an external front-end. Same output as map, without rebuilding _map.md and _map.html. | `--out` |
| `next` | Show what to do next: a prioritized, actionable list of risk buckets (Orphans, Needs tests, Needs intent review, Drafts to review). Read-only, always exits 0. The best follow-up command to run after any action. | `--all` |
| `lint` | Readability and structure check on non-draft requirements: long sentences (>25 words), stacked conditions (3+ and/or joins in one normative line), contract clauses with an unnamed 'It' subject, missing Contract or Acceptance sections. Read-only; exit-neutral by default. | `--strict` |
| `show` | Print a consolidated dossier for one requirement: header, intent, Contract bullets, dependencies in both directions, code members grouped by role with file:line, open Verify intent questions, and risk signals. Answers 'what does this do / where is X' in one command. Read-only. | — |
| `dupes` | Flag requirement pairs whose contracts overlap (TF-IDF cosine similarity), so a divergent re-implementation is caught before it lands. Read-only, advisory — a human decides if a flagged pair is a real duplicate. | `--threshold` |
| `search` | Rank requirements by lexical relevance to a free-text query (same TF-IDF cosine as dupes, reused). Read-only. Prints each hit's score, and says so explicitly when nothing clears the relevance floor rather than showing a spurious top result. Lexical, not synonym-aware. | `--top` |
| `health` | Print a corpus coherence snapshot: a headline score (percentage of requirements fully green on every axis: confirmed + member + tested + no open questions + not drifted) plus component counts. Use for a CI badge with --json. | `--json`, `--badge` |
| `draft` | Draft one requirement per untagged file (code and prose). Input is existing untagged source code and Markdown. Emits draft requirements — never confirmed. After drafting, run gate and report the result. Remind the user to review and confirm the real ones. | — |
| `plan` | Read-only JSON capability-extraction plan: emit a capability map from legacy code without writing any .md files. Safer than draft — a human authors and confirms each candidate. Use before draft to preview what would be extracted. | `--out`, `--md-glob` |
| `findings` | Aggregate open 'Verify intent' items across all requirements into requirements/_findings.md. Surfaces every open human-review question in one place. | `--raw` |
| `confirm` | Mark a reviewed requirement as confirmed — the human sign-off step. Flips status to confirmed in the frontmatter. The engine refuses if the requirement has no implements: member (a confirmed requirement must point to code). Run sync after confirming. | — |
| `review` | Emit a JSON review plan (intent, contract, acceptance criteria, structural anchors) for all requirements or one. Used as an AI feed for semantic quality review. Read-only. | — |
| `translate` | Manual, opt-in: detect the corpus's majority language (per-file `lang:` frontmatter override honored first), then cache a `claude -p` translation of every requirement written in that language into requirements/_i18n/<target>.json. A structural-fidelity check (backticked spans, numbers, heading/bullet markers) gates every cache write; a missing `claude` CLI, a timeout, or a failed check skips that entry with a warning instead of aborting. `map`/`export` inline the cache into the graph read-only, with no `claude` call of their own — this command is the ONLY way a `claude` subprocess runs; it is never invoked by gate/sync/lint/map or the pre-commit hook. | `--to` |
| `site` | Inject or refresh engine-owned regions (nav links + stats counts) into a project presentation page. Scaffolds a full page if the target does not exist. Run after map to keep the page current. | `--attach`, `--regions`, `--diagram`, `--detect` |
| `coverage` | Read-only report of untagged-code coverage signal: lists source files that carry no implements: tag, grouped by directory. Use to identify gaps in requirement traceability. | `--json` |
| `suggest-verifies` | Propose `# verifies: <id>#AC-N` tags for tests already named after the criterion they check (e.g. `test_ac3_...`), so per-criterion coverage can be adopted on an existing corpus. Read-only; --apply writes the tags. | `--apply` |
<!--##/REQMAP:COMMANDS##-->

**`check` is a deprecated alias for `gate`** — kept for backward compat.

## Releasing a new version (plugin semver checklist)

Before merging a feature branch, bump the semver **on that branch**:

1. Update `plugin/.claude-plugin/plugin.json` → `"version": "X.Y.Z"`
2. Update `.claude-plugin/marketplace.json` → `"version": "X.Y.Z"` in all three occurrences
3. Run `python scripts/check_versions.py` from repo root — must print `OK semver aligned at 'X.Y.Z'`
4. Mark shipped `TODO.md` items `[x]`
5. Commit: `chore: bump version to X.Y.Z`
6. After merge: `git tag vX.Y.Z <merge-sha> && git push origin vX.Y.Z`

## Legacy / brownfield (draft mode)

`draft` walks the code and proposes `draft` requirements. It **cannot** recover intent — it only
captures observed behavior, so everything it emits is `draft`/`baseline`, never `confirmed`.
Aim ~80% auto-`baseline` / ~20% human-`confirmed` as a *health signal*, not a quota.
