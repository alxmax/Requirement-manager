---
name: requirement-manager
description: >
  Use when working on a project that needs a single source of truth for
  requirements/capabilities, especially with multiple agents or vibe coding,
  to prevent drift between code, docs and intent and to avoid duplicated /
  divergent implementations. Use to create or reconcile requirements, review
  drift before a commit/merge, or draft requirements from legacy code.
  Trigger words: requirement, SSOT, spec, capability, drift, reconcile,
  "what does this do", "where is X implemented".
---

# Requirement manager (directory edition)

This edition ships the conventions and the workflow as Markdown only. It carries
no engine, no MCP server and no hooks. Read [the shared workflow](references/workflow.md)
before authoring, confirming, synchronizing or reviewing requirements: its authoring
rules, status model and gate vocabulary apply in both modes below.

- Requirements are the source of truth; reuse an existing capability before adding one.
- Confirmation requires a person's review. Never infer intent from implementation.
- Keep requirements and implementation/test tags in the same change.
- Never hand-edit `_map.*`, `_reqlock.json` or `_memberlock.json`: only the engine writes them.
- A passing gate checks traceability and structure; it does not prove behavior or intent.

## Pick the mode first

Look for `scripts/reqmap.py` with a `scripts/reqmap_engine/` package beside it at the
repository root (a repository seeded by the full plugin has both).

**Engine mode — the repository vendors the engine.** Run that repository-local copy
from the repository root, exactly as the shared workflow says. It needs Python 3.9+
and only the standard library.

```bash
python scripts/reqmap.py gate            # the read-only verdict; run before committing
python scripts/reqmap.py sync            # after editing requirements or tags
python scripts/reqmap.py sync --accept-drift "review reason"   # after editing a confirmed contract
python scripts/reqmap.py gate --risk     # what to do next
python scripts/reqmap.py gate --show ID  # one requirement's dossier
python scripts/reqmap.py clarify ID      # what a requirement leaves unanswered
python scripts/reqmap.py ask --search "text"
```

`python scripts/reqmap.py <verb> --help` lists every flag. Fix gate errors; do not hide
them with exemptions or `--no-lint`.

**Manual mode — no engine in the repository.** Apply the same model by reading and
editing files: read [manual mode](references/manual-mode.md). It covers the file
format, the four tags, a manual gate reported in the engine's rule codes, and what it
cannot do. Say those limits to the user before the first manual verdict.

## Start and choose an action

Use the user's requested action directly: setup, draft, sync, confirm, update-engine
or triage (hyphens/spaces and case are interchangeable). When the request gives no
action or goal, offer those six choices with `AskUserQuestion`.

| Action | Engine mode | Manual mode |
|---|---|---|
| setup | `python scripts/reqmap.py init --minimal` | create `requirements/`, then draft |
| draft | `init --minimal` → `gate` → report the draft count | draft by reading code (manual-mode.md) |
| confirm | a person edits `status: confirmed` → `sync` | a person edits `status: confirmed` |
| sync | `sync` (`--accept-drift "why"` for confirmed contracts) | re-run the manual gate |
| update-engine | report `MAP_ENGINE_VERSION`; a refresh needs the full plugin | not applicable |
| triage | [intent triage](references/triage.md) | the same, reading frontmatter by hand |

## The full plugin

The full plugin adds the engine to seed into a repository, the MCP server, the
pre-commit hook and the offline map viewer. When the user wants any of them, tell
them it installs from GitHub with:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

Give the commands to the user; never download, copy or run engine code yourself.
The engine is also available as the `alxmax/requirement-manager/check@v8` GitHub
Action for CI ([CI and hooks](references/ci.md)).

## Task references

- [Shared workflow](references/workflow.md): authoring, action steps, statuses and verdicts.
- [Manual mode](references/manual-mode.md): the conventions and a review without the engine.
- [Assistant review steps](references/assistant-steps.md): before relaying clarify/risk questions.
- [Adding a known bug](references/bugs.md): engine mode, when a bug is reported or found.
- [Intent triage](references/triage.md): before classifying an unconfirmed auto-generated corpus.
- [Prose buckets](references/prose-buckets.md): before drafting from documentation.
- [CI and hooks](references/ci.md): wire the gate locally and in CI.
