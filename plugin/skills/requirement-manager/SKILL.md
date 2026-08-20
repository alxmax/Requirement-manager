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

# Requirement manager

A capability registry that sits between intent and code. Each capability is one
markdown file (the single source of truth). Code points back to it with a tag.
A script reconciles the two and generates a navigable map.

## Menu (entry point)

When this skill is invoked, choose one of two paths:

- **With an action argument** (e.g. `requirement-manager sync`) — skip the
  menu and run that action directly. Accepted arguments: `setup`,
  `draft`, `sync`, `confirm`, `update-engine`, `triage` (hyphen or space,
  case-insensitive).
- **Bare** (no argument) — present the six actions below with `AskUserQuestion` and
  run the one the user picks.

All actions run from the repo root where `scripts/reqmap.py` is vendored (see Setup).
After any action, summarize what changed and, when useful, point to
`python scripts/reqmap.py next` for the best follow-up.

| Action | What it does and when to pick it | Commands to run (in order) |
|---|---|---|
| **setup** (first use in a repo) | Idempotent bootstrap: scaffold `requirements/` and `.reqmapignore` if missing, draft new requirements for any untagged code/prose, then rebuild the lock + map. Pick this when the repo has never had a requirement registry. Existing requirement files and membership tags are **preserved**. Never clobbers `.reqmapignore`. | `python scripts/reqmap.py init` |
| **draft** (discover missing requirements) | Discovery pass: draft new requirements for any untagged code/prose files. Pick this when code has grown since the last extraction and you want to catch new untagged capabilities. Existing requirement files and membership tags are **preserved**. Covers code and prose (`.md`/`.html`). After drafting, run `gate` and report the draft count + gate result (`N errors`). Remind the user to review + `confirm` the real ones. | `python scripts/reqmap.py draft` → `gate` → report draft count + result |
| **confirm** (validate a reviewed requirement) | Human-validation step: flip a reviewed requirement's `status` to `confirmed`. Pick this when you have reviewed a `draft` or `baseline` requirement and verified its contract matches the code's actual behaviour. The engine refuses if the requirement has no `implements:` member (a confirmed requirement must point to code). After confirming, run `sync`. | 1. Tag the implementing file: add `# implements: <ID>` (and `# tested-by: <ID>` if there's a test). 2. `python scripts/reqmap.py confirm <ID>`. 3. `python scripts/reqmap.py sync`. |
| **sync** (refresh lock + map after edits) | Rescan code members, advance the drift baseline, and regenerate the map — all in one step. Pick this after editing requirement files or tagging new code members (i.e. whenever you want to advance the committed baseline). Use `--accept-drift` to advance an edited confirmed/implemented contract. | `python scripts/reqmap.py sync --accept-drift` (if confirmed contracts changed) or `python scripts/reqmap.py sync` (for new/draft requirements only) → advisory doc-sync |
| **update-engine** (after a plugin update) | Re-seed the vendored `scripts/reqmap.py` (and `scripts/_map_viewer.html` if the repo uses the viewer) from the installed plugin, then re-verify. Pick this after `/plugin update` to bring the engine up to date. Report the old → new `MAP_ENGINE_VERSION`. | copy `${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py` → `scripts/reqmap.py` and `${CLAUDE_PLUGIN_ROOT}/scripts/_map_viewer.html` → `scripts/_map_viewer.html` (Windows PowerShell: `Copy-Item`; POSIX: `cp`), then `python scripts/reqmap.py gate` → `map` |
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
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
cp "${CLAUDE_PLUGIN_ROOT}/scripts/_map_viewer.html" scripts/_map_viewer.html   # optional: the self-contained UI viewer template
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
plugin present. When the plugin ships a newer `reqmap.py`, re-seed with:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
cp "${CLAUDE_PLUGIN_ROOT}/scripts/_map_viewer.html" scripts/_map_viewer.html   # if you use the viewer
```

**Plugin authors** — use `sync_reqmap.sh` (in the plugin source repo) to propagate
engine changes to the cache and any registered consumer repos in one command:

```bash
./sync_reqmap.sh /path/to/consumer-repo1 /path/to/consumer-repo2
```

## Core model

- **Source of truth**: one `.md` per capability in `requirements/`, with YAML
  frontmatter (machine-readable) + prose body (human-readable). Nothing else
  restates the contract — code and docs *reference* it by id, never re-describe it.
- **Optional frontmatter fields**: `milestone: vX.Y` places a requirement on the Roadmap tab (e.g. `milestone: v1.04`). It must be a version of the shape `v<digits>[.<digits>…]` — start with `v`, digits and dots only; the gate WARNs on a malformed value (advisory metadata, never build-critical). Use zero-padded minor versions (`v1.04`, not `v1.4`) to avoid ambiguity.
- **Two layers** (think Factorio main bus + cells):
  - `layer: bus` — foundation capabilities, defined once, shared (telemetry,
    config, logging, an invocation primitive). Crisp output → crisp boundary.
  - `layer: feature` — capabilities that compose the bus. They `depends_on` bus ids.
  - If you cannot tell where a requirement ends, factor the shared part onto the bus.
  - **Both layers** require `## WHAT — Contract` and `## HOW — Acceptance` at
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
| test-link integrity (tested-by file missing or holds no test function) | **WARN** | exit 0 |
| drift (confirmed contract changed vs lock, members not re-touched) | **WARN** | exit 0 |
| missing `satisfies:` for a `need` layer requirement | **WARN** | exit 0 |
| AC-coverage gap (labelled AC-N with no `verifies:` tag) | **WARN** | exit 0 |
| member drift (dedicated member changed, contract not re-touched) | **WARN** | exit 0 |
| untagged doc bundle (large `docs/` HTML with no `generated-from:`) | **WARN** | exit 0 |
| orphan code (150+-line program file with no membership tag) | **WARN** (never strict-promoted) | exit 0 |

Use `gate --strict` to promote test-link integrity and drift to errors (useful in CI
for a corpus where all requirements are confirmed and lock is current).

- **link sync** — every code tag points to a real requirement; every `confirmed`
  requirement has ≥1 `implements:` member; no dangling refs; `depends_on` targets exist.
- **behavior sync** — deterministic half is **test-link integrity** (warn-only): a
  confirmed requirement's `tested-by` file must exist and contain a test function
  (`def test…(`, `function test…(`, `it(`/`test(`), else the link asserts coverage it
  lacks. Silent on a well-formed corpus.
- **drift** — content hash of each `confirmed` requirement compared to `_reqlock.json`;
  a changed requirement whose members were not re-touched is flagged WARN (never ERROR by
  default — design decision from day 1; see REQ-CHECK-006). The warning also names the
  drifted requirement's direct `depends_on` dependents — its review blast radius
  (REQ-DRIFTIMPACT-035). Advance the lock with `sync`
  (use `--accept-drift` when the edited requirement is `confirmed` or `implemented`).

Intent sync is *not* automatable — it surfaces at human review (promote
`baseline → confirmed`).

### Wiring the gate

**Git pre-commit hook** (one-time, per developer clone):

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
python -X utf8 scripts/reqmap.py gate || exit 1
python -X utf8 scripts/reqmap.py lint --strict || exit 1
python -X utf8 scripts/reqmap.py map --check
EOF
chmod +x .git/hooks/pre-commit
```

`map --check` is there on purpose: the gate alone is link-sync (a stale or
never-committed map/lock passes it), so a freshness check beside it is what keeps an
out-of-date map or an uncommitted lock from merging.

`lint --strict` is there for the same reason on the prose axis: the gate proves the
links are real, not that the requirement is readable. Left un-wired, the clarity rules
are documentation nobody runs. `--strict` blocks only on error-severity findings (a
`confirmed` requirement missing its Contract or Acceptance section) plus the promoted
structural checks; style warnings stay advisory. A requirement whose shape is deliberate
opts a check out with `lint_exempt: [check-name]` and records the reason in its Notes —
an exemption a reviewer can argue with beats a warning everyone learns to scroll past.

**GitHub Actions** (enforces the gate for the whole team) — use the published
action, pinned to `@v1`:

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
        # with:
        #   reqmap-path: scripts/reqmap.py   # where you vendored the engine
        #   working-directory: .             # where requirements/ lives
        #   freshness: 'true'                # also run `map --check` (default; set 'false' to skip)
        #   lint: 'true'                     # also run `lint --strict` (default; needs engine >= 2.3.4)
        #   reqmap-repo: owner/name          # only if your committed map targets a different slug
```

`warn_if_stale` (the vendored-copy staleness notice) is gated on `CLAUDE_PLUGIN_ROOT`,
unset in CI — so it is silent and exit-neutral there by design. The action runs the
gate **and** `map --check` (map freshness) **and** `lint --strict` by default. The lint step
runs the consumer's own vendored engine, so it needs `reqmap.py` from plugin v2.3.4 or newer
(the release that added the `lint_exempt:` escape hatch); pass `lint: 'false'` to skip it.
If you prefer not to depend on
the action, run the engine directly instead of the `uses:` line:
```yaml
      - run: python -X utf8 scripts/reqmap.py gate
      - run: python -X utf8 scripts/reqmap.py lint --strict
      - run: python -X utf8 scripts/reqmap.py map --check
```

The hook and the CI job are independent — wire both so the gate runs locally
before push *and* on the remote for PRs.

## Commands

Creation verbs (pick by input, not by outcome):
- `draft` — input is **existing untagged CODE** (or prose); auto-extracts draft requirements from it.
- `new AREA-NAME-NNN` — input is **nothing yet**; scaffolds one blank requirement from the built-in template.
- `new --from-todo "TODO name" --id AREA-NAME-NNN` — input is a **TODO.md item**; scaffolds a requirement draft pre-filled from that item. Replaces the old `promote-todo` verb. Add `--mark-done` to flip the TODO item to `[x]` at the same time.

- `python scripts/reqmap.py init`              — first-use bootstrap: scaffold `requirements/` + `.reqmapignore`, draft requirements from existing code, build the lock + map, and print guided next steps. Idempotent; never clobbers an existing `.reqmapignore`.
- `python scripts/reqmap.py new AREA-NAME-NNN`   — scaffold a requirement from the built-in template. Use `--from-todo "name" --id AREA-NAME-NNN` to pre-fill from a TODO.md item instead.
- `python scripts/reqmap.py confirm <ID>`        — the human-validation step: flip a reviewed requirement's `status` to `confirmed` (one frontmatter edit). Refuses if it has no `implements:` member (a confirmed requirement must point to code); warns if it has no `tested-by:`. Re-run `sync` after.
- `python scripts/reqmap.py scan`              — list code members per capability
- `python scripts/reqmap.py sync`              — rescan + advance the drift baseline + regenerate the map in one step. Use after editing requirement files or tagging new code members. **Drift guard:** if a `confirmed` or `implemented` contract changed, `sync` refuses and exits non-zero unless you pass `--accept-drift` (which explicitly advances the baseline for that contract).
- `python scripts/reqmap.py gate`              — run the commit/CI gate (report-only): link sync + drift + test-link integrity. **Never** touches `_reqlock.json`. Use `gate --strict` to promote drift + test-link warnings to errors.
- `python scripts/reqmap.py next`              — terminal "what should I do next": a progress header (`N · X confirmed · Y tested · Z drafts`) then the Risk tab's actionable signals as counted buckets, most-urgent-first (Orphans · Needs tests · Needs intent review · Drafts to review). Each bucket shows the top few items (draft `REVIEW`-flagged first, each naming `requirements/<ID>.md`) with `--all` to expand. Read-only, always exit 0 (advice, not a gate). It shares `_risk_signals` with the Risk tab (a draft's intent question is folded into "Drafts to review", so counts are honest); `findings` remains the exhaustive raw verify-intent list.
- `python scripts/reqmap.py lint`             — make the "Audience & writing level" rules mechanical: report readability/structure violations on **non-draft** requirements, scoped to the Contract + Acceptance sections (Notes may stay dense). Checks span structure (`missing-section` [error], `empty-section`), prose readability (`long-sentence`, `stacked-conditions`, `statement-too-long`), scope/cohesion (`ac-count-low`, `ac-count-high`, `over-scoped`, `file-spread`), and testability (`vague-term`) — full contract in `REQ-LINTCHECKS-025`. Read-only and exit-neutral by default; `--strict` exits non-zero on error-severity findings **and** promotes the structural `ac-count-high` and `over-scoped` checks to errors, so those two can fail CI under `--strict`.
- `python scripts/reqmap.py show <ID>`         — print a consolidated, human-readable dossier for one requirement: header (id · status · layer · milestone), intent, Contract bullets, dependencies both directions (`depends_on` + reverse `Depended on by`), code members grouped by role with `file:line`, open `## WHAT — Verify intent` questions (the `findings` "None" filter applied), and risk signals with advice (same `_risk_signals` source as `next`). Answers "what does this do / where is X" in one command. Read-only; returns non-zero on an unknown id so a typo is visible to CI.
- `python scripts/reqmap.py dupes`             — flag requirement pairs whose contracts overlap, so a divergent re-implementation is caught before it lands. Stdlib TF-IDF (smoothed idf) + cosine over each requirement's title + intent + Contract bullets (Notes excluded as noise); prints pairs most-similar-first with their score and top shared terms. `--threshold T` overrides the default `0.35`. Read-only, always exit 0 (advisory — a human decides if a flagged pair is a real duplicate). Lexical, not semantic: it surfaces likely duplicates, it does not prove duplication. Requirement-to-requirement only; untagged-code-to-requirement matching stays with `plan`.
- `python scripts/reqmap.py health`            — print a corpus coherence snapshot: a headline score (the percentage of requirements green on EVERY axis — `confirmed` + an `implements` member + tested-or-`test_exempt` + no open verify-intent + not drifted) plus the component counts (confirmed, implemented, tested, drafts, orphans, untested, open verify-intent, drift). `--json` emits the same numbers as a parseable object for a CI badge. Read-only, always exit 0 (a report, not a gate). The score is strict by design: one open question or one drifted contract drops a requirement out of the green count.
- `python scripts/reqmap.py map`               — generate `requirements/_map.md` (4 Mermaid diagrams) + `requirements/_map.json` (the `{engine_version, nodes, edges, todos}` registry graph) + `requirements/_map.html` (a self-contained, double-click-openable React viewer with this repo's data inlined — emitted only when `scripts/_map_viewer.html` is vendored beside the engine). The viewer has 4 tabs: **Map · Problems · Spec · Roadmap**. The Roadmap tab renders a Gantt chart using the optional `milestone: vX.Y` frontmatter field on each node and a `todos` array parsed from `TODO.md` at the repo root. The Risk diagram/table also flags `untested` (has `implements` but no `tested-by` — silence per-requirement with `test_exempt: <reason>` in frontmatter) and `unverified-intent` (an open `## WHAT — Verify intent` item).
- `python scripts/reqmap.py site --attach docs/architecture.html --regions nav,stats` — inject/refresh engine-owned regions (links + counts) into a presentation page; scaffolds one if absent. `init` runs this best-effort.
- `python scripts/reqmap.py export`            — write just `requirements/_map.json` (or `--out PATH`, or `--out -` for stdout) — the same graph `map` emits, for feeding an external front-end.
- `python scripts/reqmap.py draft`             — draft one requirement per untagged file. Input: **existing untagged code** (and prose). Covers **code** and **prose** (`.md`/`.html`) by default. Prose is bucketed by `classify_prose`: meta/boilerplate (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`, `CHANGELOG.md`, `LICENSE*`, `_`-prefixed) is ignored; `README*`, everything under `docs/`, and every `*.html` are **sync-only** (never drafted — tag them `generated-from: <ID>` to drift- and semantic-check them); everything else (prompts/specs) is drafted as `draft`. An explicit tag on any file is always honored.
- `python scripts/reqmap.py plan`              — read-only extraction plan: emit a JSON capability map from legacy code without writing any `.md` files (use before authoring, safer than `draft`). Add `--md-glob 'prompts/**' --md-glob 'modes/**'` to also discover capabilities in authoritative **non-code** files (prompt/spec markdown) — advisory only (writes no `.md`), allowlist-bounded, off unless a glob is given. A human authors + confirms each candidate; the source file is then tagged `generated-from:`/`implements:` and the drift hash anchors on the **authored** Contract+Acceptance, never the source prose (so the prompt may drift freely). The plan carries `coverage_summary` so an unfilled plan can't masquerade as coverage.
- `python scripts/reqmap.py findings`          — aggregate open verify-intent items across all requirements into `requirements/_findings.md`; accepts an AI-triage sidecar (`_findings_triage.json`) for a classified view
- `python scripts/reqmap.py coverage`          — per-directory membership-tag coverage report: scannable files tagged vs. total, grouped by top-level directory, to spot traceability gaps. `--json` for CI. Read-only, exit 0.

**`check` is a deprecated alias for `gate`** (removed in the next major version). It still works — consumer pre-commit hooks and CI that call `reqmap.py check` keep functioning unchanged. Migrate at leisure: `sed -i 's/reqmap.py check/reqmap.py gate/' <hook>`.

**Workflow order** — after modifying requirement files, run `sync` as a unit
so the lock and map stay in sync:

```bash
python scripts/reqmap.py sync
# or, if you edited a confirmed/implemented contract:
python scripts/reqmap.py sync --accept-drift
```

`reqmap.py map --check` is the freshness gate (no write): it rebuilds the map in
memory and exits non-zero if the committed `_map.*` is stale (a code/requirement
edit shifted it). Wire it next to `gate` in your pre-commit hook / CI so a stale
map can't be committed. A repo that doesn't track a map passes silently.

## Project site (`reqmap.py site`)

`site` keeps a project presentation page (e.g. `docs/architecture.html`) current by
injecting **engine-owned, marker-delimited regions** and preserving the authored prose
between them. It is deterministic and never prompts — the *interactive* part is your job
as the skill.

**When the user wants a project/landing/architecture page, or to refresh one:**
1. Run `python scripts/reqmap.py site --detect` (from the dir where `requirements/` lives)
   to see what `docs/` already has and the suggested command.
2. Ask the user **which target** — an existing `docs/architecture.html`, an
   `index.html`, a bring-your-own HTML path, or scaffold a new page — and **which regions**
   (`nav` for the top links only, or `nav,stats`).
3. Run `python scripts/reqmap.py site --attach <path> --regions <nav|nav,stats> [--diagram <rel>]`.
   - Attach mode refreshes only the marked regions (`<!--##REQMAP:NAV##-->…<!--##/REQMAP:NAV##-->`,
     `…:STATS…`); your prose is untouched.
   - If `<path>` does not exist, `site` **scaffolds** a full default page (theme + regions +
     a placeholder hero marked `<!-- author me -->`).
4. If you scaffolded, offer to rewrite the placeholder hero into real prose for the repo.

Regions and their sources: `nav` = Live Map / Diagram / GitHub links (from `git remote` +
artifact paths, each emitted only if its target resolves); `stats` = requirement/confirmed/
layer/edge counts + engine version (from `_map.json`). The engine **only links** an
excalidraw diagram — it never generates one (the excalidraw-diagram skill stays independent).

`init` already runs a best-effort `site` pass (`nav,stats` into `docs/architecture.html`,
scaffolding it if absent); `reqmap.py init --no-site` opts out. `map --check` flags the
page stale if its `stats` region drifts (the `nav` region is exempt — it embeds the
fork-specific repo URL).

## Releasing a new version (plugin semver checklist)

Before merging a feature branch, bump the semver **on that branch** so the version commit is part of the merge. Do not bump after merge.

1. Update `plugin/.claude-plugin/plugin.json` → `"version": "X.Y.Z"`
2. Update `.claude-plugin/marketplace.json` → `"version": "X.Y.Z"` in all three occurrences (root + plugins array)
3. Run `python scripts/check_versions.py` from repo root — must print `OK semver aligned at 'X.Y.Z'`
4. Mark shipped `TODO.md` items `[x]` so they disappear from the Roadmap tab
5. Commit: `chore: bump version to X.Y.Z`
6. After merge: `git tag vX.Y.Z <merge-sha> && git push origin vX.Y.Z`

**When to bump which digit:**
- **patch** (X.Y.**Z**) — bug fixes, doc corrections, gate/map regen with no new behavior
- **minor** (X.**Y**.0) — new commands, new viewer tabs, new frontmatter fields, new generated outputs
- **major** (**X**.0.0) — breaking changes to the requirement schema, gate behavior, or CLI interface

## Legacy / brownfield (draft mode)

`draft` walks the code and proposes `draft` requirements (structure, input/output
from signatures, `depends_on` from imports). It **cannot** recover intent — it only
captures observed behavior, so:
- Everything it emits is `draft`/`baseline`, never `confirmed`. It never canonizes a
  bug as correct.
- Routing to review is by **risk = blast radius × uncertainty × proximity to known
  problems**, not by parsing ease (clean code can be a clean bug). High-risk →
  review; low-risk → accept as `baseline` (tracked, not asserted correct).
- Aim ~80% auto-`baseline` / ~20% human-`confirmed` as a *health signal*, not a quota.
