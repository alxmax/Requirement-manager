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

Read [the shared workflow](references/workflow.md) before authoring, confirming,
synchronizing or reviewing requirements. It contains the authoritative authoring
rules, status model, action steps and gate policy for both assistant variants.

- Requirements are the source of truth; reuse an existing capability before adding one.
- Confirmation requires a person's review. Never infer intent from implementation.
- Keep requirements and implementation/test tags in the same change.
- Run `python scripts/reqmap.py gate` before committing; it is read-only.
  Text and JSON run the same checks. Fix errors; do not hide them with exemptions.
- Run `sync` after requirement or tag edits. Accept confirmed-contract drift only
  deliberately, with `--accept-drift "review reason"`. Never hand-edit maps or locks.
- A passing gate checks traceability and structure; it does not prove behavior or intent.

## Start and choose an action

Use the user's requested action directly: setup, draft, sync, confirm,
update-engine or triage (hyphens/spaces and case are interchangeable).
When the request gives no action or goal, offer those six choices.
The shared workflow explains each action. Prefer `init --minimal` for first use;
ordinary `init` also seeds planning, release, MCP and site files.

## Platform setup

For Claude Code, the installed root is `${CLAUDE_PLUGIN_ROOT}`. Use
`AskUserQuestion` for the action menu when needed. Set `REQMAP_PLUGIN_ROOT`
to that installed root for the copy commands below.

The engine requires Python 3.9+ and only the standard library. Seed both
`scripts/reqmap.py` and the adjacent `scripts/reqmap_engine/` package. Copy
`scripts/_map_viewer.html` too for the offline viewer. Run commands at the repo root.

```bash
mkdir -p scripts
cp "${REQMAP_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
cp -r "${REQMAP_PLUGIN_ROOT}/scripts/reqmap_engine" scripts/reqmap_engine
python scripts/reqmap.py init --minimal
```

Initialization creates `.reqmapignore` so the vendored engine's own tags are excluded.
Read [setup details](references/setup.md) when updating the engine or editing ignores.
Keep the package and CLI together when updating. Report the version change.

## Commands

The following region is generated from the command registry. Do not maintain it by hand.

<!--##REQMAP:COMMANDS##-->
**Author**
- `python scripts/reqmap.py init` — First-use bootstrap: scaffold requirements/ and .reqmapignore if missing, draft requirements from existing code and prose, build the lock and map, and print guided next steps. Idempotent — safe to re-run; never clobbers an existing .reqmapignore. --plan emits the extraction plan as JSON and writes no requirement files, for looking before authoring. Flags: `--plan` Emit the extraction plan as JSON instead of writing requirement files.; `--out` With --plan: write the plan JSON here ('-' or omitted = stdout).; `--md-glob` With --plan: also scan these non-code globs for capabilities (repeatable).; `--wipe` Hard-reset: delete all non-generated requirements and strip membership tags from source files before re-extracting.; `--minimal` Skip planning, release, MCP and site scaffolding.; `--no-site` Skip the final site step (scaffolding docs/architecture.html)..
- `python scripts/reqmap.py clarify AREA-NAME-NNN` — Ask what a requirement has not answered yet: vague terms with no threshold, numbers with no unit, unbounded quantities, clauses with no case, a missing failure path. Read-only, always exit 0, never a gate rule. --decompose is the write half of the same question: it splits a requirement into code-rung children along the bold group labels in its Description (--apply writes), or scaffolds one draft per over-long clause when it has none. Run it before implementing, so the ambiguity is resolved in the requirement instead of guessed in code. Flags: `--decompose` Split a requirement into code-rung children along the bold group labels its author wrote in the Description; --apply writes them and never edits the parent. With no id, every requirement carrying groups. A requirement with no groups falls back to one draft per over-long clause.; `--levels` Propose a V-model rung for every requirement that declares no `level:`, plus the rungs above: one draft `ARCH-<FAMILY>-001` per id-prefix family, `SYS-NEEDS-A-NAME-001` at the apex, and the `satisfies:` edges between them. --apply writes all of it, each line marked `level_source: auto`.; `--json` Emit the questions as JSON for an agent to answer.; `--apply` With --decompose or --levels: write the proposal instead of printing it..

**Build**
- `python scripts/reqmap.py sync` — The write path. Rescan code members, advance the drift baseline, and regenerate the map, the findings file and the generated integration artifacts in one step. Run after editing requirement files or tagging new code members. --accept-drift is required when a confirmed or implemented contract changed. Flags: `--retire` Take these requirements out of service instead of confirming them. Accepts one id or many; a batch retires in an order computed from the graph, under one working-tree check. Prints the blast radius; writes nothing without --apply.; `--release` Cut a release instead of syncing: the next version planned in _planning.json above what is already declared, or the vX.Y.Z named here. Prints the plan - version files to bump, the CHANGELOG entry, the milestone the plan drops - and writes nothing without --apply. With --json it also reports the declared version, whether its tag exists and its notes, which is what a release workflow reads.; `--delete` With --retire: also remove the block, its lock entries and its membership tags. Never a function body.; `--apply` With --retire or --release: actually write the change. Without it, the run is a dry report.; `--force` With --retire: proceed even though dependents still point at this requirement, or the working tree is dirty. Dependents that are already deprecated, and those retired in the same call, never block.; `--findings` Also regenerate the aggregated open-questions file.; `--attach` HTML page to refresh the site's engine-owned regions in (scaffolds it if absent). Without it, `sync` refreshes docs/architecture.html when that exists.; `--accept-drift` Explicitly advance the baseline when a confirmed or implemented contract changed. Required when those contracts differ from the lock; sync exits non-zero without it. Takes an optional reason, recorded in requirements/_driftlog.json so the waiver and its justification land in the diff.; `--strict` Promote drift and test-link integrity from warn to error.; `--json` With --retire or --release: emit the plan as JSON..

**Read**
- `python scripts/reqmap.py gate` — The commit/CI verdict. Bare, it verifies that every code tag resolves to a real requirement, that every confirmed requirement has at least one implements: member, and that drift has not been introduced since the last sync, then checks requirement readability and map freshness. Exits non-zero on link-sync errors only. Never writes anything. Three mode flags report on the verdict's own subject instead of running it: --audit for the whole problem report, --risk for what to do next, --show for one requirement's dossier. Every other question is `ask`. Flags: `--audit` Print every pass that discovers a problem as one report: the gate, corpus risk, duplicate contracts and tag coverage. The exit code still comes from the gate alone.; `--risk` Print the corpus risk snapshot and the actionable signals, most urgent first.; `--show` Print one requirement's dossier: intent, contract, dependencies both ways, code members with file:line, open questions and risk signals.; `--all` With --risk: expand every bucket instead of the top few.; `--untagged` With --risk: report membership-tag coverage per directory.; `--badge` With --risk: print the coherence score as a badge string.; `--strict` Promote drift and test-link integrity warnings to errors. Useful in CI when all requirements are confirmed.; `--json` Emit structured JSON output instead of human-readable text.; `--since` Scope the gate to requirements whose member files changed since this git ref (e.g. 'main', 'HEAD~1').; `--no-lint` Skip the requirement readability check.; `--no-map-check` Skip the committed-map freshness check.; `--full` Run every gate rule and print every readability warning. Bare, the gate runs only the rules that say a link, the drift baseline or the committed map is broken, and prints readability errors only..
- `python scripts/reqmap.py ask` — Ask the corpus a question without running the verdict. Read-only, never writes, and its exit code is the question's, never the gate's: --search ranks requirements by relevance, --dupes ranks overlapping contracts, --design reviews the code against the OOP pillars, --review emits the machine-readable review plan. Exactly one mode per call. Since v8.0.0, `gate` refuses these flags and names `ask`. Flags: `--search` Rank requirements by lexical relevance to a free-text query.; `--dupes` Rank requirement pairs whose contracts overlap, most similar first.; `--design` Advisory design review of the code: encapsulation, abstraction, inheritance and polymorphism candidates plus file length and line width, grouped by pillar. Read-only, exit 0, never the gate.; `--review` Emit the deterministic review plan as JSON: for one requirement, or with no id for the whole corpus.; `--i18n` Removed in v8.2.0 (ADR-0047): accepted and ignored, refused from v9.0.0.; `--top` With --search or --dupes: how many results to print.; `--threshold` With --dupes: override the similarity threshold.; `--json` Emit structured JSON output instead of human-readable text..
- `python scripts/reqmap.py mcp` — Serve this repository's requirements to an AI assistant over the Model Context Protocol (stdio). Each tool is one reqmap invocation in a fresh process. Read-only unless --allow-writes. Flags: `--allow-writes` Also offer the tools that write: sync and release..
<!--##/REQMAP:COMMANDS##-->

## Task references

- [Shared workflow](references/workflow.md): authoring, action steps, statuses and verdicts.
- [Assistant review steps](references/assistant-steps.md): before relaying clarify/risk questions.
- [Intent triage](references/triage.md): before classifying an unconfirmed auto-generated corpus.
- [Prose buckets](references/prose-buckets.md): before drafting from documentation.
- [CI and hooks](references/ci.md): wire the gate locally and in CI.
  The published action is `alxmax/requirement-manager/check@v8`.
- [MCP](references/mcp.md), [project site](references/site.md),
  [releases and legacy code](references/releasing-and-legacy.md): read when that task applies.
