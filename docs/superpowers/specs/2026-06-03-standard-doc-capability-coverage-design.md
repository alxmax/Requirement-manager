# Standard doc & prose capability coverage

- **Date:** 2026-06-03
- **Target:** `requirement-manager` plugin, engine `reqmap.py` + `SKILL.md`
- **Version:** 1.7.0 → 1.8.0
- **Status:** Approved design, pre-implementation (awaits `consilium` deliberation)

## Problem

Today `reqmap` only auto-discovers **code** capabilities. Authoritative **prose**
capabilities — prompt files, spec markdown — are invisible unless an operator
remembers the off-by-default `candidates --md-glob 'prompts/**'` opt-in, and even
then nothing is drafted (a human must hand-author each). Project **documentation**
(README, architecture HTML) is never checked against the code or requirements, so it
silently rots out of sync.

Concretely, in the Senate consumer repo the 9 senator prompts in
`prompts/senators/*.md` are the *core* capability of the project and are completely
unregistered, while all 11 requirements map only to Python scripts.

## Goals

1. `.md` **and** `.html` discovery is **standard in every action** (`init`,
   `extract`, `regenerate requirements`, `candidates`) — not an opt-in flag.
2. `init`/`reinit` does visible work on prose **even when requirement files already
   exist** (it must not no-op just because code is fully tagged).
3. Project docs (including HTML that presents the project) are **checked for sync**
   against code + requirements — staged: a deterministic engine drift flag plus an
   advisory semantic check in the skill.
4. Meta/boilerplate markdown (CLAUDE.md, LICENSE, etc.) is **never** turned into a
   requirement. README and overview docs are sync-checked but are **not** their own
   requirement.

## Non-goals

- Auto-drafting requirements from README / overview docs (they reference many
  capabilities; one file ≠ one capability).
- Scanning doc formats beyond `.md` and `.html` (`.rst/.txt/.adoc` are out — YAGNI).
- Making semantic accuracy a hard gate. Semantic sync is advisory judgment, the same
  class as intent-sync, which the registry already leaves to human review.
- A configurable "un-skip README" knob — the built-in classification is fixed;
  per-repo exceptions go through `.reqmapignore` and explicit tags.

## The classification rule

Every scanned `.md`/`.html` file falls in exactly one of three buckets. A file's
bucket governs **auto** behavior only; an **explicit** tag on any file (even a
bucket-1 file) is always honored.

### Bucket 1 — Ignore (no scan)
Invisible to reqmap. Members:
- every glob in `.reqmapignore`
- any file whose basename starts with `_` (`_map.html`, `_map.md`, `_findings.md`)
- built-in meta set: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `CONTRIBUTING.md`,
  `LICENSE` / `LICENSE.*`, `SKILL.md`, `TODO.md`

### Bucket 2 — Sync-only (never a requirement; drift- + semantic-checked)
Not auto-drafted. When tagged `generated-from: <ID>` (or `validated-against: <ID>`),
the file becomes a member of that requirement and is subject to:
- **deterministic drift** — flagged stale when the requirement's content hash changes
  but the doc was not re-touched in the same commit (the existing drift mechanism);
- **advisory semantic check** — a skill workflow step (see below).

Members:
- `README` / `README.*`
- everything under `docs/**`
- all `*.html` (anywhere, except bucket-1 `_`-prefixed)

### Bucket 3 — Capability source (auto-draft a `draft` stub)
Every other non-ignored `.md`/`.html`. In practice `prompts/**`, `specs/**`,
`modes/**`, and any project-specific prose. A `draft`-status requirement is
scaffolded from the file's `title:` (front-matter or first H1) plus its `##`
headings, exactly as code extract scaffolds from signatures. `draft` is never
enforced by the gate, so unreviewed prose is never canonized as truth. The operator
edits and `promote`s real ones, deletes the rest.

`--md-glob` remains, now as an **additional** override to pull bucket-3 discovery from
unusual locations beyond the conventional dirs.

### Senate repo mapping (worked example)
| Path | Bucket | Result |
|---|---|---|
| `prompts/senators/*.md` (9) | 3 | auto-drafts 9 senator requirements |
| `README.md` | 2 | sync-checked, no requirement |
| `docs/architecture_senate.html` | 2 | sync-checked |
| `docs/senate.md` | 2 | sync-checked |
| `CLAUDE.md`, `SKILL.md`, `TODO.md`, `_map.*`, `_findings.md` | 1 | ignored |

## Engine changes (`reqmap.py`)

1. **File collection (`_collect_files`)** — stop gating `.md`/`.html` behind
   `md_globs`. Collect them by default, then classify into the three buckets. Keep
   `md_globs` as an additive bucket-3 source. Add `.html` to the scannable set.
2. **Built-in lists** — module-level constants `META_IGNORE` (bucket 1) and
   `SYNC_ONLY` (bucket 2 patterns: `README*`, `docs/**`, `*.html`). Document why each
   entry is there.
3. **Tag scanning in HTML/markdown comments** — the tag scanner must recognize
   `implements:` / `generated-from:` / `validated-against:` / `tested-by:` inside
   `<!-- ... -->` comments so `.html` and comment-tagged `.md` link correctly. Verify
   the current line-regex already matches inside comments; if not, widen it.
4. **Auto-draft from prose (`extract` / `init`)** — for untagged bucket-3 files,
   scaffold a `draft` stub from title + `##` headings. Reuse the existing draft
   writer; the "signatures" list is the heading list.
5. **Sync-only membership** — a bucket-2 file with a `generated-from:` tag is a
   member and participates in drift. It is never proposed for auto-draft.
6. **`init` is non-empty on prose** — because discovery now includes prose, `init`
   re-run on a fully-code-tagged repo still drafts the untagged prose capabilities;
   it no longer reports "0 proposed" when prose is uncovered.

## Skill changes (`SKILL.md`)

1. Menu/Setup/Commands rewritten so md+html coverage is described as **standard**
   (drop the "off unless a glob is given" framing for the default path; keep
   `--md-glob` documented as an override).
2. New **advisory doc-sync step** under `init` and `regenerate map`: dispatch an
   agent that reads each bucket-2 doc + its tagged requirement(s) + the implementing
   code, and reports concrete mismatches (e.g. "HTML says quorum 6/9; code says
   7/9"). Output is findings, not a gate. Document that it requires the orchestrator
   (Claude), not the stdlib engine.
3. Document the three-bucket rule in an "Authoring rules" subsection.

## Testing (`plugin/scripts/test_reqmap.py`)

New cases:
- bucket-1 meta files are never drafted and never scanned;
- bucket-2 `README`/`docs/**`/`*.html` are never auto-drafted;
- a bucket-2 file tagged `generated-from:` is a member and goes stale on requirement
  drift;
- bucket-3 prose auto-drafts a `draft` stub from headings;
- an explicit tag on a bucket-1 file is honored (buckets govern auto only);
- `.html` tag scanning inside `<!-- -->` comments;
- `init` re-run on a code-complete repo still drafts uncovered prose.

The existing suite must stay green.

## Rollout

1. Implement engine + skill + tests; bump `plugin/.claude-plugin/plugin.json` and
   the marketplace manifest to **1.8.0**; bump `MAP_ENGINE_VERSION`.
2. Add a `CHANGELOG.md` entry.
3. Regenerate the plugin's own dogfooded `requirements/_map.*` + lock.
4. `sync_reqmap.sh` to the plugin cache and the Senate repo's vendored
   `scripts/reqmap.py`.
5. **Separate follow-up (not this change):** in Senate, run the new flow to draft +
   author + `promote` the 9 senator requirements and tag README/docs `generated-from`.

## Risks & mitigations

- **Noise** — stray top-level `.md` could auto-draft. Mitigation: `draft` status is
  curated/deleted by the human; the meta-ignore list covers the common boilerplate.
- **Comment-tag regex miss** — `.html` tags not detected. Mitigation: explicit test
  case; widen the regex if the current one is line-anchored to code comments.
- **Behavior change for existing consumers** — repos that upgrade suddenly see prose
  drafts. Mitigation: drafts are non-enforced and clearly `draft`; documented in the
  CHANGELOG as expected on first post-upgrade `init`/`extract`.
- **Published-plugin blast radius** — this changes default behavior for everyone.
  Mitigation: `consilium` deliberation before implementation; version bump signals
  the behavior change.
