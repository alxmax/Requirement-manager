---
id: REQ-EXTRACT-008
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-SCAN-002]
superseded_by:
milestone: v1.06
---

# Legacy extraction

> When an existing project has lots of code but no requirements written down, this gives you
> a running start: it reads each untagged file and writes a rough draft requirement for it,
> clearly marked as a draft so no one mistakes a guess for a settled decision. It also looks
> at human-readable spec and prompt documents, not just code. Without it, someone would have
> to sit down and describe every existing capability from scratch before the tool was useful
> on an older project.

## WHAT — Contract (normative)
- It shall walk untagged source files (`.py`/`.js`/`.ts`/`.c`/`.cpp`) and propose one
  `requirements/DRAFT-*.md` per file, skipping files that already carry a member tag.
- It shall honor `.reqmapignore` (the same fnmatch globs `scan` respects): a file matching an
  ignore pattern is never drafted — notably the vendored `scripts/reqmap.py` engine itself.
- Every proposal shall be `status: draft` with a TODO body — it captures observed behavior,
  never canonizing intent or correctness.
- It shall assign a cheap risk score (TODO/FIXME/HACK/XXX markers, suppressions, file size)
  and route a score ≥ 2 to `REVIEW`, else `auto-baseline`.
- Re-running shall not overwrite an existing draft; the requirements directory shall be
  created if absent and draft ids shall be path-aware so same-basename files do not collide.
- `extract` shall also draft `draft`-status requirements from untagged **prose**
  capability files (`.md`/`.html`) — prose meaning human-readable spec/prompt text,
  as opposed to source code. Each prose file is classified by `classify_prose(rel)`
  into one of three buckets:
  - **ignore** — meta/boilerplate that is never a capability: `CLAUDE.md`,
    `AGENTS.md`, `GEMINI.md`, `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`,
    `CHANGELOG.md`, `LICENSE`/`LICENSE.*`, and any `_`-prefixed generated file
    (`_map.html`, `_findings.md`, …).
  - **sync_only** — `README`/`README.*`, everything under `docs/`, and every
    `*.html`. These are never drafted as their own requirement, but become a member
    (and are drift-checked) when a human tags them `generated-from: <ID>`.
  - **capability** — everything else (e.g. `prompts/`, `specs/`, `modes/` prose).
    These are auto-drafted.
- The buckets shall govern auto-drafting ONLY; an explicit tag on any file is always
  honored by `scan_members` regardless of bucket (so a hand-tagged README is still a
  member).
- A prose draft shall be scaffolded by `_prose_facts(src)` from the file's title
  (frontmatter `title:`, else first `#` heading, else HTML `<title>`/`<h1>`) plus its
  `##` section headings, which are recorded as an authoring hint. The source prose is
  never the contract — so the prose may later drift freely from the authored
  requirement (the drift hash anchors on the authored Contract+Acceptance).

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- `extract` cannot recover intent; prefer `candidates` (read-only plan) before authoring.
  The draft body uses the same Contract/Acceptance section names as a real requirement so a
  promoted draft needs no reshaping.

## HOW — Acceptance (= tests)
- An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.
- A file already carrying a member tag is skipped.
- A file matching a `.reqmapignore` pattern is skipped (no draft proposed for it).
- A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`.
- Re-running does not overwrite an existing draft; same-basename files in different dirs do not collide.
- Given a `prompts/foo.md` with no member tag, When `extract` runs, Then a
  `draft`-status requirement is written for it.
- Given `README.md`, a file under `docs/`, a `*.html` file, `CLAUDE.md`, or
  `CHANGELOG.md`, When `extract` runs, Then no draft is written for it.
- Given a capability-bucket prose file already tagged `# implements: <ID>`, When
  `extract` runs, Then it is skipped (no duplicate draft).
- Given a file tagged `generated-from: <ID>` inside an HTML comment
  (`<!-- generated-from: <ID> -->`), When `scan_members` runs, Then that file is a
  member of `<ID>`.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs extract on a brownfield repo. For each untagged source file it drops a
  `DRAFT-*.md` capturing what the file appears to do; one file full of `TODO` and `FIXME`
  markers scores higher risk and is flagged `REVIEW`. The engine's own `reqmap.py` is in
  `.reqmapignore`, so it is skipped, and a prompt file under `prompts/` gets its own draft
  too — leaving Ana a pile of starting points to promote into real requirements.

## WHERE — Current implementation
- `cmd_extract`, `_draft_id`, `_risk`, `classify_prose`, `_prose_facts` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
