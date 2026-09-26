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

For any assistant with shell access, set `REQMAP_PLUGIN_ROOT` to the installed
plugin directory containing `scripts/reqmap.py`. Locate the installation; do not
guess a versioned cache path. Present the action menu as a numbered list.

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
| Command | What it does | Flags |
|---|---|---|
| `init` | First-use bootstrap: scaffold requirements/ and .reqmapignore if missing, draft requirements from existing code and prose, build the lock and map, and print guided next steps. Idempotent — safe to re-run; never clobbers an existing .reqmapignore. --plan emits the extraction plan as JSON and writes no requirement files, for looking before authoring.  | `--plan`, `--out`, `--md-glob`, `--wipe`, `--minimal`, `--no-site` |
| `gate` | The commit/CI verdict. Bare, it verifies that every code tag resolves to a real requirement, that every confirmed requirement has at least one implements: member, and that drift has not been introduced since the last sync, then checks requirement readability and map freshness. Exits non-zero on link-sync errors only. Never writes anything. Three mode flags report on the verdict's own subject instead of running it: --audit for the whole problem report, --risk for what to do next, --show for one requirement's dossier. Every other question is `ask`.  | `--audit`, `--risk`, `--show`, `--all`, `--untagged`, `--badge`, `--strict`, `--json`, `--since`, `--no-lint`, `--no-map-check`, `--full` |
| `ask` | Ask the corpus a question without running the verdict. Read-only, never writes, and its exit code is the question's, never the gate's: --search ranks requirements by relevance, --dupes ranks overlapping contracts, --design reviews the code against the OOP pillars, --review emits the machine-readable review plan. Exactly one mode per call. Since v8.0.0, `gate` refuses these flags and names `ask`.  | `--search`, `--dupes`, `--design`, `--review`, `--i18n`, `--top`, `--threshold`, `--json` |
| `sync` | The write path. Rescan code members, advance the drift baseline, and regenerate the map, the findings file and the generated integration artifacts in one step. Run after editing requirement files or tagging new code members. --accept-drift is required when a confirmed or implemented contract changed.  | `--retire`, `--release`, `--delete`, `--apply`, `--force`, `--findings`, `--attach`, `--accept-drift`, `--strict`, `--json` |
| `clarify` | Ask what a requirement has not answered yet: vague terms with no threshold, numbers with no unit, unbounded quantities, clauses with no case, a missing failure path. Read-only, always exit 0, never a gate rule. --decompose is the write half of the same question: it splits a requirement into code-rung children along the bold group labels in its Description (--apply writes), or scaffolds one draft per over-long clause when it has none. Run it before implementing, so the ambiguity is resolved in the requirement instead of guessed in code.  | `--decompose`, `--levels`, `--json`, `--apply` |
| `mcp` | Serve this repository's requirements to an AI assistant over the Model Context Protocol (stdio). Each tool is one reqmap invocation in a fresh process. Read-only unless --allow-writes. | `--allow-writes` |
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
