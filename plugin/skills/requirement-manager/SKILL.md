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

One markdown file per capability in `requirements/` is the source of truth; code points back
to it with a comment tag; `scripts/reqmap.py` checks the two still agree.

## Start here

**1. Seed the engine** (once per repo; the CLI and its package travel together):

```bash
mkdir -p scripts
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
cp -r "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap_engine" scripts/reqmap_engine
```

**2. `python scripts/reqmap.py init`**: creates `requirements/` and `.reqmapignore`, drafts one
requirement per capability it finds in the code, builds the lock and the map. Safe to re-run.

**3. Tag the code** that implements or tests a requirement, one line each:
`# implements: AREA-NAME-001`, `# tested-by: AREA-NAME-001` (`//` in brace languages).

**4. Confirming is a person's answer, never yours to assume**: after someone has read a
draft, set `status: confirmed` in its frontmatter. A confirmed requirement needs an
`implements:` tag, or the gate fails.

**5. `python scripts/reqmap.py gate`** before every commit. It never writes. Read it so:
- exit 1 with `ERROR RM001/RM003/RM006`: a tag, a `depends_on` or an implements member is
  broken. Fix the link.
- `WARN RM018 … DRIFT`: a confirmed contract changed since the lock. Re-check the file it
  names; then `sync --accept-drift "why"`.
- bare, it shows only what is broken; `gate --full` adds every advisory check.

**6. `python scripts/reqmap.py sync`** after editing requirements or tags: the only command
that writes. Never edit `_map.*` or `_reqlock.json` by hand.

Everything below is for when a step above sends you there.

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
`python scripts/reqmap.py gate --risk` for the best follow-up.

| Action | What it does and when to pick it | Commands to run (in order) |
|---|---|---|
| **setup** (first use in a repo) | Idempotent bootstrap: scaffold `requirements/` and `.reqmapignore` if missing, draft new requirements for any untagged code/prose, then rebuild the lock + map. Pick this when the repo has never had a requirement registry. Existing requirement files and membership tags are **preserved**. Never clobbers `.reqmapignore`. | `python scripts/reqmap.py init` |
| **draft** (discover missing requirements) | Discovery pass: draft new requirements for any untagged code/prose files. Pick this when code has grown since the last extraction and you want to catch new untagged capabilities. Existing requirement files and membership tags are **preserved**. Covers code and prose (`.md`/`.html`). After drafting, run `gate` and report the draft count + gate result (`N errors`). Remind the user to review + `confirm` the real ones. | `python scripts/reqmap.py init` → `gate` → report draft count + result |
| **confirm** (validate a reviewed requirement) | Human-validation step. There is no command: read the requirement, then set `status: confirmed` in its frontmatter. The gate refuses a confirmed requirement with no `implements:` member (RM006), and `sync` demotes an edited contract back to `draft` on its own. | 1. Tag the implementing file. 2. Edit `status:`. 3. `python scripts/reqmap.py sync`. |
| **sync** (refresh lock + map after edits) | Rescan code members, advance the drift baseline, and regenerate the map (plus `_findings.md`, if the repo keeps one) — all in one step. Pick this after editing requirement files or tagging new code members (i.e. whenever you want to advance the committed baseline). Use `--accept-drift` to advance an edited confirmed/implemented contract. | `python scripts/reqmap.py sync --accept-drift` (if confirmed contracts changed) or `python scripts/reqmap.py sync` (for new/draft requirements only) → advisory doc-sync |
| **update-engine** (after a plugin update) | Re-seed the vendored `scripts/reqmap.py` and `scripts/reqmap_engine/` (and `scripts/_map_viewer.html` if the repo uses the viewer) from the installed plugin, then re-verify. Pick this after `/plugin update` to bring the engine up to date. Report the old → new `MAP_ENGINE_VERSION`. | copy `${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py` → `scripts/reqmap.py`, replace `scripts/reqmap_engine/` with `${CLAUDE_PLUGIN_ROOT}/scripts/reqmap_engine/`, and `${CLAUDE_PLUGIN_ROOT}/scripts/_map_viewer.html` → `scripts/_map_viewer.html` (Windows PowerShell: `Copy-Item -Recurse`; POSIX: `cp -r`), then `python scripts/reqmap.py sync` → `gate` |
| **triage** (classify a vibe-coded corpus) | Classify all auto-extracted requirements as Core / Emergent / Accidental. Pick this when the corpus is vibe-coded (most requirements have `owner: auto` and none are `confirmed`). Surfaces what the tool genuinely needs vs. what AI invented. Leads to deprecate / delete decisions for Accidental requirements. | 1. `reqmap.py gate --risk` (see status). 2. Present C/E/A framework to user (see references/triage.md). 3. User classifies each requirement. 4. Apply: Core → confirm path; Accidental → `deprecated` + delete; Emergent → keep as `baseline`. 5. `reqmap.py sync`. |

**Advisory doc-sync and clarify answers** are assistant steps, not engine commands: read [references/assistant-steps.md](references/assistant-steps.md) before relaying a `clarify` or `gate --risk` question to the user.


**Intent triage** (Core / Emergent / Accidental) for a corpus that is mostly `owner: auto` with nothing confirmed: [references/triage.md](references/triage.md). Offer it before any other action when `gate --risk` shows `0 confirmed`.


## Setup (first use in a repo)

The engine is stdlib-only, Python 3.9+ (it refuses an older interpreter with one
readable line rather than a stdlib error): the CLI module `reqmap.py` plus the
`reqmap_engine/` package beside it. The two travel together — seed both into the
target repo once:

```bash
mkdir -p scripts requirements
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
cp -r "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap_engine" scripts/reqmap_engine
cp "${CLAUDE_PLUGIN_ROOT}/scripts/_map_viewer.html" scripts/_map_viewer.html   # optional: the self-contained UI viewer template
```

`_map_viewer.html` is the pre-built single-file React viewer. When it sits beside
`reqmap.py`, `map` also emits a double-click-openable `requirements/_map.html` (the
full UI, this repo's data inlined, no server). It is optional — omit it and the
engine still emits `_map.md` + `_map.json`.

**Then run the one-shot bootstrap** — `python scripts/reqmap.py init` creates the
`requirements/` dir, writes a minimal `.reqmapignore` (ignoring `scripts/reqmap.py`,
`scripts/reqmap_engine/**` and the agent-worktree copies below),
drafts requirements from the existing code, builds the lock + map, and prints guided
next steps. It is idempotent (safe to re-run) and never clobbers an existing
`.reqmapignore`. The manual steps below are what `init` automates — do them by hand
only if you want finer control.

The requirement template is **built into the engine**, so no template file is needed. (Optionally, drop a `templates/requirement.md` in the repo to override
the built-in scaffold; the engine uses it automatically when present.)

`init` writes `.reqmapignore` for you. Its contents, re-seeding a newer engine and the plugin-author sync script: [references/setup.md](references/setup.md).


## Core model

- **Source of truth**: one `.md` per capability in `requirements/`, with YAML
  frontmatter (machine-readable) + prose body (human-readable). Nothing else
  restates the contract — code and docs *reference* it by id, never re-describe it.
- **Non-binding commentary has one home**: the built-in template scaffolds a single
  `## Context (non-binding)` section with bold `**Notes**` / `**Example**` / `**Current
  implementation**` sub-groups, replacing the older three separate headings (`## WHAT —
  Notes & known limitations`, `## Example — in practice`, `## WHERE — Current
  implementation`) for newly-authored requirements ([ADR-0017](../../../docs/adr/0017-consolidated-context-section.md)).
  The three-heading form remains fully valid — nothing in the gate, lint, or drift hash
  reads either form by name over the other, so existing requirement files never need to
  change. `map`'s emitted `notes`/`current_impl` fields try the legacy heading first and
  fall back to the matching `## Context` sub-group.
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
  - **Every layer** requires `## Description` and `## Cases` at
    `confirmed` status. Bus capabilities are not exempt — unspecified bus
    contracts are the most expensive to discover late.
- **A second, optional axis: `level:`.** Where `layer:` is a requirement's position
  in the graph, `level:` is its rung on the V-model's left arm — `level: system` (a
  stakeholder need), `level: architecture` (one capability), `level: code` (one
  behaviour group).
  The edge that builds that pyramid is `satisfies:`, not `depends_on:`.
  **It is off by default and a flat corpus is a supported end state, not a
  waypoint.** The template ships the field commented out, nothing infers it, and a
  corpus that declares no `level:` gates exactly as it did before the field existed.
  It earns itself only once a flat list stops explaining itself — the rungs were
  added here at ~52 requirements, to give a clause somewhere to say *why* it exists.
  Below that, adopting it is cost with no reader. `reqmap.py gate --audit` reports
  where your corpus stands and says the same thing in its own words.
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

**Split by failure mode, never by sentence.** When you decompose a requirement into
detailed-design children, a clause earns its own requirement only if it names a behavior
that can fail on its own. Three clause shapes never do, and each is a merge candidate
rather than a child:

- **an element of an enumeration** — "a Rust `#[test]` counts" is one arm of *the engine
  recognises a test function*, not a capability. Six list items are one behavior.
- **an attribute of a behavior** — "the check is warn-only and never changes the exit
  code" qualifies how something else behaves. Fold it into that behavior's `Then`, where a
  test actually observes it.
- **a rationale or a consequence** — "deleting the created draft restores the corpus
  exactly, because the parent was never edited" restates a sibling's obligation. It belongs
  in Notes, or inside the sibling's scenario.

The check is mechanical: **try to write the `Then`**. If the observable you write only
repeats the clause in other words, the clause is not a capability. That test is the rule —
no word count, no clause count, and no lint check substitutes for it, because none of them
can tell a terse-but-complete obligation from a fragment (see
[ADR-0022](../../../docs/adr/0022-no-minimum-requirement-size-check.md), which measured the
attempt and rejected it).

1. **Before implementing**, run `reqmap.py sync` or read `requirements/` and check
   whether a capability already covers the task. If yes, extend/reuse it — do not
   reimplement. Especially check the bus.
2. **A requirement is its contract.** Fill `Description` (the normative,
   testable behavior) first; the boundary follows from the contract. (Legacy
   requirements may still use `Input → Description → Output`; the engine reads both.)
2a. **`confirmed` requires both `## Description` and `## Cases`.**
    A contract-only requirement has unspecified acceptance tests. An acceptance-only
    requirement has an unspecified normative contract. The gate warns on either
    omission. Both `bus` and `feature` layers are subject to this rule.
3. **Acceptance criteria are tests.** Write them as checkable statements; they map
   to `tested-by` test files.
3a. **Split heuristic (smell, not a hard limit).** If a requirement accumulates
    more than four or five acceptance criteria that cover behaviors which could
    break **independently** of each other, it is a *split candidate*. Author two
    or more requirements, each with its own contract and its own failure mode.
    `reqmap.py gate --risk` flags these. A five-AC requirement with one root cause is
    fine; a three-AC requirement covering three disjoint failure modes is already
    overloaded.

3c. **Write one case from the caller's side.** The cases an author reaches for first
    are the ones the implementation suggests: the input that matches, the input that
    does not, the input that is empty. Those all vary the *quality* of one kind of
    input and never its *kind*, and a contract can be complete inside that frame and
    blind outside it. `search` shipped four such cases and, for two years, answered a
    query naming a requirement id with a different requirement entirely — the gate was
    green, per-criterion coverage was 100%, and nothing was wrong except that nobody
    had asked what a caller would type. `reqmap.py clarify` names this shape
    (`case-monoculture`); the fix is one case written from outside the implementation.

3b. **Merge heuristic — the same smell from the other side.** A corpus only ever
    grows unless something says so. If two requirements state the same obligation,
    the code is covered twice and a later edit will change one of them. `reqmap.py
    next` reports a **Redundancy** bucket for contracts that are identical word for
    word (exact match, no threshold — a group there is a duplicate, not a guess),
    and `reqmap.py ask --dupes` scores the near-matches. Fold a group into one
    requirement and re-point the tags, or make the contracts say different things.
    Both are advisory and neither ever rewrites a file: which of two ids survives,
    and what the merged contract says, is a judgement call.
4. **One fact, one home.** Reference ids; never copy a contract into a README.
5. **Authority is one-directional**: requirement → code. If they disagree, the
   requirement wins (fix the code, or fix the requirement — never let code be the
   silent truth).
6. **Authoring is bidirectional**: you may start in code (explore), but the change
   is not "done" until the requirement is updated in the *same* commit.
7. **`## Verify intent` asks the user, not the AI.** This section is for
   open questions that only a human reviewer can answer — contract gaps, edge cases
   not covered, design decisions left implicit, or behaviors that may be AI accidents
   (swallowed error, magic constant, unreachable branch). Write 1–3 specific, answerable
   questions per requirement. "None — doc is unambiguous." is a valid answer only when
   the contract genuinely leaves nothing open; use it sparingly. The engine treats it
   as a placeholder and `findings` skips it. Once the human answers, fold the answer
   into the Contract (or Notes) and delete the bullet — the section should shrink toward
   empty as the requirement matures.

**Prose files** (`.md`, `.html`) fall into three buckets — ignored, sync-only, or capability source: [references/prose-buckets.md](references/prose-buckets.md).


## Audience & writing level

Write every requirement for a DEVELOPER NEW TO THE PROJECT: someone who programs, opens the
requirement from a `# implements:` tag in code they do not understand, and knows nothing
about this repo. File and function names are welcome (they say where to look); programming
terms need no definition; project-specific terms still do. Rules:

1. Define each project-specific term briefly, inline, on first use — e.g.
   "veto cascade (a fixed series of checks that can block or reroute the result)".
   After the first definition, use the term freely.
2. On first mention of a named component, attach its role — e.g.
   "Conservator (the voice that looks for risk)".
3. Write contract lines in plain present tense with a named subject — "`init` creates
   the folder", never "It shall create the folder". The Contract section opens with
   "Every line in this section is binding.", so no "shall" or "must" is needed on each
   line. A clause may hold two or three sentences, as long as the extra ones state the
   first's consequence and never a second obligation. Keep sentences under 25 words and
   clauses to at most three sentences; `lint` enforces both, and warns
   (`anonymous-subject`) on a clause that opens with a bare "It".
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

`python scripts/reqmap.py gate` is report-only: it verifies these syncs and exits non-zero on **link-sync errors only**. Bare, it runs only the rules that say a link, the drift baseline or the committed map is broken, and prints readability errors only; `gate --full` runs every check in the table below (ADR-0049). It **never** touches `_reqlock.json`. To advance the drift baseline after intentionally editing a requirement, use `sync` (with `--accept-drift` when a confirmed/implemented contract changed).

**Rule codes and exemptions.** Every gate line carries the code of the rule that produced it
(`WARN  RM018 AUTH-LOGIN-001: DRIFT — ...`), `gate --json` lists the same findings as
`{rule, severity, rid, msg}` records, and a requirement can switch one rule off for itself
with `gate_exempt: [RM013]` in its frontmatter — the same shape as `lint_exempt:`. Codes are
permanent. Thresholds (`LINT_AC_MAX`, `SIMILAR_THRESHOLD`, `ORPHAN_CODE_MIN_LOC`, the fan-out
bands, extra scanned extensions) can be set per repo in `requirements/_config.json`; an
unknown or mistyped key is reported on stderr and ignored.

| Check | Level | Effect on exit code |
|---|---|---|
| link sync (dangling tag, enforced req with no member, bad `depends_on`) | **ERROR** | exit 1 |
| test-link integrity (tested-by file missing or holds no test function) — **at every status**; strict-promoted only for `confirmed` | **WARN** | exit 0 |
| drift (confirmed contract changed vs lock, members not re-touched) | **WARN** | exit 0 |
| missing `satisfies:` for a `need` layer requirement | **WARN** | exit 0 |
| AC-coverage gap (one line per requirement: `N/M automatable criteria carry a verifies: tag`) | **WARN** | exit 0 |
| committed map stale (`_map.*`, `_findings.md`) | **WARN** | exit 0 |
| `depends_on` cycle (the dependency order is unsatisfiable) | **WARN** | exit 0 |
| member drift (dedicated member changed, contract not re-touched) | **WARN** | exit 0 |
| untagged doc bundle (large `docs/` HTML with no `generated-from:`) | **WARN** | exit 0 |
| tag in a file type the scan never reads (not a member) | **WARN** | exit 0 |
| orphan code (150+-line program file with no membership tag) | **WARN** (never strict-promoted) | exit 0 |
| `layer: aggregate` claiming the coverage exemption with an empty `depends_on` | **WARN** | exit 0 |

Use `gate --strict` to promote test-link integrity and drift to errors (useful in CI
for a corpus where all requirements are confirmed and lock is current).

- **link sync** — every code tag points to a real requirement; every `confirmed`
  requirement has ≥1 `implements:` member; no dangling refs; `depends_on` targets exist.
- **behavior sync** — deterministic half is **test-link integrity** (warn-only): a
  `tested-by` file must exist and contain a test function (`def test…(`,
  `function test…(`, `it(`/`test(`, `func TestX(`, `#[test]`, a bash `test_x()` or
  bats `@test`, or a `*.test.sh` name), else the link asserts coverage it lacks.
  Checked at every status — a link pointing at a component instead of its spec is
  wrong the day it is written — but promoted to an error under `--strict` only for a
  `confirmed` requirement. Silent on a well-formed corpus.
- **drift** — content hash of each `confirmed` requirement compared to `_reqlock.json`;
  a changed requirement whose members were not re-touched is flagged WARN (never ERROR by
  default — design decision from day 1; see ARCH-CHECK-006). The warning also names the
  drifted requirement's direct `depends_on` dependents — its review blast radius
  (ARCH-DRIFTIMPACT-035). Advance the lock with `sync`
  (use `--accept-drift` when the edited requirement is `confirmed` or `implemented`).

Intent sync is *not* automatable — it surfaces at human review (promote
`baseline → confirmed`).

### Wiring the gate

**Git pre-commit hook** (one-time, per developer clone):

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
python -X utf8 scripts/reqmap.py gate
EOF
chmod +x .git/hooks/pre-commit
```

One `gate` is the whole verdict: link sync and drift, then requirement readability
(errors only; `--full` prints the warnings too), then the committed-map freshness check.

The readability check is part of the verdict for the same reason on the prose axis:
link sync proves the links are real, not that the requirement is readable. It blocks
only on error-severity findings (a `confirmed` requirement missing its Description or
Cases section) plus the promoted structural checks; style warnings stay advisory.

**Never exempt a check, and never pass `--no-lint`, to make a run green.** An exemption is
a finding somebody decided not to see, and it is the cheapest thing in this tool to reach
for: one frontmatter token, no explanation, and nothing mentions it again. That is exactly
why it must not be the reflex. When a requirement is reported as over-scoped or as carrying
too many acceptance criteria, the answer is to split it. `reqmap.py clarify <ID>
--decompose` does the mechanical half: a Description the author already divided into bold
group labels is split along those labels into `level: code` children (`--apply` writes
them and leaves the parent untouched; without it you get the plan), and a Description with no
groups gets one draft per over-long clause. The finding names that command.
Decomposition builds downward only: the children `satisfies:` the requirement you split,
and nothing above it is created, linked or checked. Only `init` drafts a system-level
placeholder; a corpus that started at the architecture rung names its own needs by hand
(ADR-0036 records why the engine does not, and the evidence that would reopen it).

An exemption IS legitimate when the shape is deliberate: a capability whose five files are
the capability, a stakeholder need with no cases of its own. Then write `lint_exempt:
[check-name]` and say why in the requirement's own prose, naming the check. `gate` warns
(RM030) on an exemption with no reason recorded, and `reqmap.py gate --audit` lists every
exemption in force with its requirement — silenced is not invisible, and the count is the
debt. An exemption a reviewer can argue with beats a warning everyone learns to scroll past;
an exemption nobody wrote a sentence for is neither.

**GitHub Actions** — the published action, pinned to the plugin's major:

```yaml
      - uses: alxmax/requirement-manager/check@v8
```

The full workflow, its inputs and the plain `- run:` alternative: [references/ci.md](references/ci.md). Wire both the hook and CI.

## Commands

Creation verbs (pick by input, not by outcome):
- `init` — input is **existing untagged CODE** (or prose); drafts requirements from it (`init --plan` shows them as JSON first, writing nothing).
- nothing yet, or a TODO item — write `requirements/AREA-NAME-NNN.md` directly, or have the assistant write it. `new` and `new --from-todo` are deprecated and removed in v8.0.0 (ADR-0045).

<!--##REQMAP:COMMANDS##-->
**Author**
- `python scripts/reqmap.py init` — First-use bootstrap: scaffold requirements/ and .reqmapignore if missing, draft requirements from existing code and prose, build the lock and map, and print guided next steps. Idempotent — safe to re-run; never clobbers an existing .reqmapignore. --plan emits the extraction plan as JSON and writes no requirement files, for looking before authoring. Flags: `--plan` Emit the extraction plan as JSON instead of writing requirement files.; `--out` With --plan: write the plan JSON here ('-' or omitted = stdout).; `--md-glob` With --plan: also scan these non-code globs for capabilities (repeatable).; `--wipe` Hard-reset: delete all non-generated requirements and strip membership tags from source files before re-extracting.; `--no-site` Skip the final site step (scaffolding docs/architecture.html)..
- `python scripts/reqmap.py clarify AREA-NAME-NNN` — Ask what a requirement has not answered yet: vague terms with no threshold, numbers with no unit, unbounded quantities, clauses with no case, a missing failure path. Read-only, always exit 0, never a gate rule. --decompose is the write half of the same question: it splits a requirement into code-rung children along the bold group labels in its Description (--apply writes), or scaffolds one draft per over-long clause when it has none. Run it before implementing, so the ambiguity is resolved in the requirement instead of guessed in code. Flags: `--decompose` Split a requirement into code-rung children along the bold group labels its author wrote in the Description; --apply writes them and never edits the parent. With no id, every requirement carrying groups. A requirement with no groups falls back to one draft per over-long clause.; `--levels` Propose a V-model rung for every requirement that declares no `level:`, plus the rungs above: one draft `ARCH-<FAMILY>-001` per id-prefix family, `SYS-NEEDS-A-NAME-001` at the apex, and the `satisfies:` edges between them. --apply writes all of it, each line marked `level_source: auto`.; `--json` Emit the questions as JSON for an agent to answer.; `--apply` With --decompose or --levels: write the proposal instead of printing it..

**Build**
- `python scripts/reqmap.py sync` — The write path. Rescan code members, advance the drift baseline, and regenerate the map, the findings file and the generated integration artifacts in one step. Run after editing requirement files or tagging new code members. --accept-drift is required when a confirmed or implemented contract changed. Flags: `--retire` Take these requirements out of service instead of confirming them. Accepts one id or many; a batch retires in an order computed from the graph, under one working-tree check. Prints the blast radius; writes nothing without --apply.; `--release` Cut a release instead of syncing: the next version planned in _planning.json above what is already declared, or the vX.Y.Z named here. Prints the plan - version files to bump, the CHANGELOG entry, the milestone the plan drops - and writes nothing without --apply. With --json it also reports the declared version, whether its tag exists and its notes, which is what a release workflow reads.; `--delete` With --retire: also remove the block, its lock entries and its membership tags. Never a function body.; `--apply` With --retire or --release: actually write the change. Without it, the run is a dry report.; `--force` With --retire: proceed even though dependents still point at this requirement, or the working tree is dirty. Dependents that are already deprecated, and those retired in the same call, never block.; `--findings` Also regenerate the aggregated open-questions file.; `--attach` HTML page to refresh the site's engine-owned regions in (scaffolds it if absent). Without it, `sync` refreshes docs/architecture.html when that exists.; `--accept-drift` Explicitly advance the baseline when a confirmed or implemented contract changed. Required when those contracts differ from the lock; sync exits non-zero without it. Takes an optional reason, recorded in requirements/_driftlog.json so the waiver and its justification land in the diff.; `--strict` Promote drift and test-link integrity from warn to error.; `--json` With --retire or --release: emit the plan as JSON..

**Read**
- `python scripts/reqmap.py gate` — The commit/CI verdict. Bare, it verifies that every code tag resolves to a real requirement, that every confirmed requirement has at least one implements: member, and that drift has not been introduced since the last sync, then checks requirement readability and map freshness. Exits non-zero on link-sync errors only. Never writes anything. Three mode flags report on the verdict's own subject instead of running it: --audit for the whole problem report, --risk for what to do next, --show for one requirement's dossier. Every other question is `ask`. Flags: `--audit` Print every pass that discovers a problem as one report: the gate, corpus risk, duplicate contracts and tag coverage. The exit code still comes from the gate alone.; `--risk` Print the corpus risk snapshot and the actionable signals, most urgent first.; `--show` Print one requirement's dossier: intent, contract, dependencies both ways, code members with file:line, open questions and risk signals.; `--all` With --risk: expand every bucket instead of the top few.; `--untagged` With --risk: report membership-tag coverage per directory.; `--badge` With --risk: print the coherence score as a badge string.; `--strict` Promote drift and test-link integrity warnings to errors. Useful in CI when all requirements are confirmed.; `--json` Emit structured JSON output instead of human-readable text.; `--since` Scope the gate to requirements whose member files changed since this git ref (e.g. 'main', 'HEAD~1').; `--no-lint` Skip the requirement readability check.; `--no-map-check` Skip the committed-map freshness check.; `--full` Run every gate rule and print every readability warning. Bare, the gate runs only the rules that say a link, the drift baseline or the committed map is broken, and prints readability errors only..
- `python scripts/reqmap.py ask` — Ask the corpus a question without running the verdict. Read-only, never writes, and its exit code is the question's, never the gate's: --search ranks requirements by relevance, --dupes ranks overlapping contracts, --design reviews the code against the OOP pillars, --review emits the machine-readable review plan. Exactly one mode per call. Since v8.0.0, `gate` refuses these flags and names `ask`. Flags: `--search` Rank requirements by lexical relevance to a free-text query.; `--dupes` Rank requirement pairs whose contracts overlap, most similar first.; `--design` Advisory design review of the code: encapsulation, abstraction, inheritance and polymorphism candidates plus file length and line width, grouped by pillar. Read-only, exit 0, never the gate.; `--review` Emit the deterministic review plan as JSON: for one requirement, or with no id for the whole corpus.; `--i18n` Removed in v8.2.0 (ADR-0047): accepted and ignored, refused from v9.0.0.; `--top` With --search or --dupes: how many results to print.; `--threshold` With --dupes: override the similarity threshold.; `--json` Emit structured JSON output instead of human-readable text..
- `python scripts/reqmap.py mcp` — Serve this repository's requirements to an AI assistant over the Model Context Protocol (stdio). Each tool is one reqmap invocation in a fresh process. Read-only unless --allow-writes. Flags: `--allow-writes` Also offer the tools that write: sync and release..
<!--##/REQMAP:COMMANDS##-->

## More, when you need it

- **Project site** — `sync --attach <page>` refreshes a project page's engine-owned regions: [references/site.md](references/site.md).
- **MCP** — when the `reqmap_*` tools are available, ask the corpus through them instead of the terminal: [references/mcp.md](references/mcp.md).
- **Releasing and brownfield repos** — the plugin semver checklist, and what `init` can recover from legacy code: [references/releasing-and-legacy.md](references/releasing-and-legacy.md).
