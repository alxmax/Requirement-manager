# Shared requirement-manager workflow

Read this before authoring, confirmation, synchronization or review. Both agent
entry points use this contract; platform-specific setup stays in those entries.

## Actions

| Action | What it does and when to pick it | Commands to run (in order) |
|---|---|---|
| **setup** (first use in a repo) | Idempotent bootstrap: scaffold `requirements/` and `.reqmapignore` if missing, draft new requirements for any untagged code/prose, then rebuild the lock + map. Pick this when the repo has never had a requirement registry. Existing requirement files and membership tags are **preserved**. Never clobbers `.reqmapignore`. | `python scripts/reqmap.py init --minimal` |
| **draft** (discover missing requirements) | Discovery pass: draft new requirements for any untagged code/prose files. Pick this when code has grown since the last extraction and you want to catch new untagged capabilities. Existing requirement files and membership tags are **preserved**. Covers code and prose (`.md`/`.html`). After drafting, run `gate` and report the draft count + gate result (`N errors`). Remind the user to review + `confirm` the real ones. | `python scripts/reqmap.py init --minimal` → `gate` → report draft count + result |
| **confirm** (validate a reviewed requirement) | Human-validation step. There is no command: read the requirement, then set `status: confirmed` in its frontmatter. The gate refuses a confirmed requirement with no `implements:` member (RM006), and `sync` demotes an edited contract back to `draft` on its own. | 1. Tag the implementing file. 2. Edit `status:`. 3. `python scripts/reqmap.py sync`. |
| **sync** (refresh lock + map after edits) | Rescan code members, advance the drift baseline, and regenerate the map (plus `_findings.md`, if the repo keeps one) — all in one step. Pick this after editing requirement files or tagging new code members (i.e. whenever you want to advance the committed baseline). Use `--accept-drift` to advance an edited confirmed/implemented contract. | `python scripts/reqmap.py sync --accept-drift "review reason"` (if confirmed contracts changed) or `python scripts/reqmap.py sync` (for new/draft requirements only) → advisory doc-sync |
| **update-engine** (after a plugin update) | Re-seed the vendored `scripts/reqmap.py` and `scripts/reqmap_engine/` (and `scripts/_map_viewer.html` if the repo uses the viewer) from the installed plugin, then re-verify. Pick this after a plugin update to bring the engine up to date. Report the old → new `MAP_ENGINE_VERSION`. | copy `${REQMAP_PLUGIN_ROOT}/scripts/reqmap.py` → `scripts/reqmap.py`, replace `scripts/reqmap_engine/` with `${REQMAP_PLUGIN_ROOT}/scripts/reqmap_engine/`, and `${REQMAP_PLUGIN_ROOT}/scripts/_map_viewer.html` → `scripts/_map_viewer.html` (Windows PowerShell: `Copy-Item -Recurse`; POSIX: `cp -r`), then `python scripts/reqmap.py sync` → `gate` |
| **triage** (classify a vibe-coded corpus) | Classify all auto-extracted requirements as Core / Emergent / Accidental. Pick this when the corpus is vibe-coded (most requirements have `owner: auto` and none are `confirmed`). Surfaces what the tool genuinely needs vs. what AI invented. Leads to deprecate / delete decisions for Accidental requirements. | 1. `reqmap.py gate --risk` (see status). 2. Present C/E/A framework to user (see triage.md). 3. User classifies each requirement. 4. Apply: Core → confirm path; Accidental → `deprecated` + delete; Emergent → keep as `baseline`. 5. `reqmap.py sync`. |

**Advisory doc-sync and clarify answers** are assistant steps, not engine commands: read [references/assistant-steps.md](assistant-steps.md) before relaying a `clarify` or `gate --risk` question to the user.


**Intent triage** (Core / Emergent / Accidental) for a corpus that is mostly `owner: auto` with nothing confirmed: [references/triage.md](triage.md). Offer it before any other action when `gate --risk` shows `0 confirmed`.


## Core model

- **Source of truth**: one `.md` per capability in `requirements/`, with YAML
  frontmatter (machine-readable) + prose body (human-readable). Nothing else
  restates the contract — code and docs *reference* it by id, never re-describe it.
- **Non-binding commentary has one home**: the built-in template scaffolds a single
  `## Context (non-binding)` section with bold `**Notes**` / `**Example**` / `**Current
  implementation**` sub-groups, replacing the older three separate headings (`## WHAT —
  Notes & known limitations`, `## Example — in practice`, `## WHERE — Current
  implementation`) for newly-authored requirements ([ADR-0017](../../../../docs/adr/0017-consolidated-context-section.md)).
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
[ADR-0022](../../../../docs/adr/0022-no-minimum-requirement-size-check.md), which measured the
attempt and rejected it).

1. **Before implementing**, run `reqmap.py sync` or read `requirements/` and check
   whether a capability already covers the task. If yes, extend/reuse it — do not
   reimplement. Especially check the bus.
2. **A requirement is its contract.** Fill `Description` (the normative,
   testable behavior) first; the boundary follows from the contract. (Legacy
   requirements may still use `Input → Description → Output`; the engine reads both.)
2a. **`confirmed` requires both `## Description` and `## Cases`.**
    A contract-only requirement has unspecified acceptance tests. An acceptance-only
    requirement has an unspecified normative contract. The readability gate reports an error on either
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
    the code is covered twice and a later edit will change one of them. `reqmap.py gate --risk` reports a **Redundancy** bucket for contracts that are identical word for
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

**Prose files** (`.md`, `.html`) fall into three buckets — ignored, sync-only, or capability source: [references/prose-buckets.md](prose-buckets.md).


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

`python scripts/reqmap.py gate` is report-only: it verifies these syncs and exits non-zero on **error-severity findings from rules, readability and map freshness**. Bare, it runs only the rules that say a link, the drift baseline or the committed map is broken, and prints readability errors only; `gate --full` runs every check in the table below (ADR-0049). It **never** touches `_reqlock.json`. To advance the drift baseline after intentionally editing a requirement, use `sync` (with `--accept-drift` when a confirmed/implemented contract changed).

**Rule codes and exemptions.** Every gate line carries the code of the rule that produced it
(`WARN  RM018 AUTH-LOGIN-001: DRIFT — ...`), `gate --json` lists the same findings as
`{rule, severity, rid, msg}` records, and a requirement can switch one rule off for itself
with `gate_exempt: [RM013]` in its frontmatter — the same shape as `lint_exempt:`. Codes are
permanent. Thresholds (`LINT_AC_MAX`, `SIMILAR_THRESHOLD`, `ORPHAN_CODE_MIN_LOC`, the fan-out
bands, extra scanned extensions) can be set per repo in `requirements/_config.json`; an
invalid active key or mistyped value stops the CLI before writes.

| Check | Level | Effect on exit code |
|---|---|---|
| link sync (dangling tag, enforced req with no member, bad `depends_on`) | **ERROR** | exit 1 |
| test-link integrity (tested-by file missing or holds no test function) — **at every status**; strict-promoted only for `confirmed` | **WARN** | exit 0 |
| drift (confirmed contract changed vs lock, members not re-touched) | **WARN** | exit 0 |
| missing `satisfies:` for a `need` layer requirement | **WARN** | exit 0 |
| AC-coverage gap (one line per requirement: `N/M automatable criteria carry a verifies: tag`) | **WARN** | exit 0 |
| committed `_map.md` / `_map.json` missing or stale | **ERROR** | exit 1 |
| invalid configuration, duplicate IDs or unreadable requirements | **ERROR** | exit 1 |
| corrupt requirement baseline | **WARN** (error under `--strict`) | exit 0 / 1 |
| `depends_on` cycle (the dependency order is unsatisfiable) | **WARN** | exit 0 |
| member drift (dedicated member changed, contract not re-touched) | **WARN** | exit 0 |
| untagged doc bundle (large `docs/` HTML with no `generated-from:`) | **WARN** | exit 0 |
| tag in a file type the scan never reads (not a member) | **WARN** | exit 0 |
| orphan code (150+-line program file with no membership tag) | **WARN** (never strict-promoted) | exit 0 |
| `layer: aggregate` claiming the coverage exemption with an empty `depends_on` | **WARN** | exit 0 |

Use `gate --strict` to promote test-link integrity, drift and corrupt requirement
baselines to errors. `DRIFT_SEVERITY: "error"` also makes drift blocking without
strict mode. An absent initial baseline is valid.

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

The full workflow, its inputs and the plain `- run:` alternative: [references/ci.md](ci.md). Wire both the hook and CI.

## Export choices

`init --minimal` omits planning, release, MCP and site scaffolding while preserving
existing optional files. Use ordinary `init` when that scaffolding is wanted.
Set `MAP_PROFILE` to `compact` for a Markdown overview and minified JSON;
`full` restores all diagrams. `MAP_LOCALES: []` omits cached translations,
`["ro"]` selects Romanian, and `["*"]` keeps all fresh caches. Source contracts
and cases remain in JSON and offline HTML. Run `sync` after configuration changes.
