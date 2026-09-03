---
id: ARCH-PROSE-024
status: confirmed
level: system
layer: feature
owner: Alex
depends_on: [ARCH-SCAN-002, ARCH-EXTRACT-008]
satisfies: [SYS-READ-103]
superseded_by:
milestone: v1.06
---

# Prose capability classification & drafting

## Description
> Specs and prompts written as text documents can be capabilities too, not just code.
> When `draft` runs, this part decides which text files deserve a draft requirement,
> which are only kept in sync, and which are ignored as boilerplate — then writes the
> drafts. Without it, prompt and spec files would stay invisible to the registry, or
> every README would pollute it with junk drafts.
- `draft` also produces `draft`-status requirements from untagged **prose** files
  (`.md`/`.html`) — prose meaning human-readable spec/prompt text, as opposed to source code.
- Each prose file is classified into one of three buckets before drafting:
  - **ignore** — meta/boilerplate that is never a capability: `CLAUDE.md`, `AGENTS.md`,
    `GEMINI.md`, `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`, `CHANGELOG.md`,
    `LICENSE`/`LICENSE.*`, and any `_`-prefixed generated file (`_map.html`, `_findings.md`, …).
  - **sync_only** — `README`/`README.*` in any letter case, everything under `docs/`, and
    every `*.html`.
    These are never drafted as their own requirement, but become a member (and are
    drift-checked) when a human tags them `generated-from: <ID>`.
  - **capability** — everything else (e.g. `prompts/`, `specs/`, `modes/` prose). These
    are auto-drafted.
- The buckets govern auto-drafting ONLY; an explicit tag on any file is always
  honored by the scanner regardless of bucket (so a hand-tagged README is still a member).
- A prose draft is scaffolded from the file's title (frontmatter `title:`, else the
  first `#` heading, else the HTML `<title>`/`<h1>`) plus its `##` section headings,
  recorded as an authoring hint.
- When a file has no `##` heading at all, its later `#` headings are the sections instead,
  so flat single-level prose (a prompt library) still yields a hint.
- The source prose is never the contract: the drift hash anchors on the authored
  Contract + Acceptance, so the prose may later drift freely from the authored requirement.

## Verify intent (open questions for the human)
- None — split out of [[ARCH-EXTRACT-008]] with intent carried over unchanged.

## Notes & known limitations (informative)
- The bucket lists are fixed in the engine, not configurable; `.reqmapignore` remains the
  per-repo escape hatch for anything the buckets misjudge.

## Cases (= tests)
CASE-1
  Given  a `prompts/foo.md` with no member tag
  When   `draft` runs
  Then   a `draft`-status requirement is written for it

CASE-2
  Given  `README.md`, a file under `docs/`, a `*.html` file, `CLAUDE.md`, or `CHANGELOG.md`
  When   `draft` runs
  Then   no draft is written for it

CASE-3
  Given  a capability-bucket prose file already tagged `# implements: <ID>`
  When   `draft` runs
  Then   it is skipped (no duplicate draft)

CASE-4
  Given  a file tagged `generated-from: <ID>` inside an HTML comment (`<!-- generated-from: <ID> -->`)
  When   the scanner runs
  Then   that file is a member of `<ID>`

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs extract on a repo with a `prompts/triage.md` nobody tagged. It gets its own
  draft requirement built from its title and headings. Her `README.md` gets none — but
  when she later tags the README `generated-from: REQ-DOCS-001`, the gate starts flagging
  it whenever that requirement's contract changes.

## WHERE — Current implementation
- `classify_prose` (the three-bucket router) and `_prose_facts` (title + heading scaffold)
  in `reqmap.py`; the prose walk lives inside `cmd_extract`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-PROSE-594
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# Draft also produces draft-status requirements from untagged prose

> `draft` also produces `draft`-status requirements from untagged **prose** files
> (`.md`/`.html`) — prose meaning human-readable spec/prompt text, as opposed to source
> code.

Scenario: draft writes a requirement for an untagged capability-bucket prose file
  Given  `prompts/foo.md` with no `# implements:` tag
  When   `draft` runs
  Then   a new `draft`-status requirement is written scaffolded from that file

## Members in code (auto)




--------------------


---
id: REQ-PROSE-596
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# Ignore — meta/boilerplate that is never a capability

> **ignore** — meta/boilerplate that is never a capability: `CLAUDE.md`, `AGENTS.md`,
> `GEMINI.md`, `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`, `CHANGELOG.md`,
> `LICENSE`/`LICENSE.*`, and any `_`-prefixed generated file (`_map.html`, `_findings.md`,
> …).

Scenario: classify_prose buckets meta/boilerplate files as ignore
  Given  the paths `CLAUDE.md`, `LICENSE`, and `_map.html`
  When   `classify_prose` runs on each
  Then   each returns `"ignore"`

## Members in code (auto)




--------------------


---
id: REQ-PROSE-597
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# Sync_only — README/README. in any letter case, everything

> **sync_only** — `README`/`README.*` in any letter case, everything under `docs/`, and
> every `*.html`. These are never drafted as their own requirement, but become a member
> (and are drift-checked) when a human tags them `generated-from: <ID>`.

Scenario: classify_prose buckets README/docs/html paths as sync_only
  Given  the paths `README.md`, `docs/sub/guide.md`, and `x.html`
  When   `classify_prose` runs on each
  Then   each returns `"sync_only"`

## Members in code (auto)




--------------------


---
id: REQ-PROSE-598
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# Capability — everything else (e.g. prompts/, specs/, modes/

> **capability** — everything else (e.g. `prompts/`, `specs/`, `modes/` prose). These are
> auto-drafted.

Scenario: classify_prose buckets prompt/spec prose as capability
  Given  the paths `prompts/senators/aurelius.md`, `specs/foo.md`, and `notes.md`
  When   `classify_prose` runs on each
  Then   each returns `"capability"`

## Members in code (auto)




--------------------


---
id: REQ-PROSE-599
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# The buckets govern auto-drafting ONLY; an explicit tag

> The buckets govern auto-drafting ONLY; an explicit tag on any file is always honored by
> the scanner regardless of bucket (so a hand-tagged README is still a member).

Scenario: an explicit generated-from tag registers a sync_only file as a member
  Given  a `README.md` carrying a `<!-- generated-from: REQ-DOCS-001 -->` comment
  When   `scan_members` runs
  Then   the file appears as a member of `REQ-DOCS-001`, despite being sync_only

## Members in code (auto)




--------------------


---
id: REQ-PROSE-600
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# A prose draft is scaffolded from the file's

> A prose draft is scaffolded from the file's title (frontmatter `title:`, else the first
> `#` heading, else the HTML `<title>`/`<h1>`) plus its `##` section headings, recorded as
> an authoring hint.

Scenario: _prose_facts prefers frontmatter title, then collects the H2 headings
  Given  a source with frontmatter `title: Senator Aurelius` and two `## ` headings
  When   `_prose_facts(src)` runs
  Then   it returns `("Senator Aurelius", ["Role", "Specialty"])`

## Members in code (auto)




--------------------


---
id: REQ-PROSE-601
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# When a file has no ## heading at

> When a file has no `##` heading at all, its later `#` headings are the sections instead,
> so flat single-level prose (a prompt library) still yields a hint.

Scenario: later H1 headings become the section hint when no H2 exists
  Given  `"# IDENTITY and PURPOSE\n\ntext\n\n# STEPS\n\n# OUTPUT INSTRUCTIONS\n"` (no `##` anywhere)
  When   `_prose_facts(src)` runs
  Then   the headings list is `["STEPS", "OUTPUT INSTRUCTIONS"]`, drawn from the later H1s

## Members in code (auto)




--------------------


---
id: REQ-PROSE-602
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
superseded_by:
---

# The source prose is never the contract: the

> The source prose is never the contract: the drift hash anchors on the authored Contract
> + Acceptance, so the prose may later drift freely from the authored requirement.

Scenario: editing the source prose file does not change the requirement's binding_hash
  Given  a capability-bucket prose file drafted into a requirement, then edited afterward
  When   `binding_hash` is computed on the requirement body before and after the edit
  Then   the two hashes are equal — the prose edit produced no drift

## Members in code (auto)
