---
id: ARCH-PROSE-024
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.06
depends_on: [ARCH-SCAN-002, ARCH-EXTRACT-008]
satisfies: [SYS-READ-103]
---

# Prose capability classification & drafting

## Description
> Specs and prompts written as text documents can be capabilities too, not just code.
> When `draft` runs, this part decides which text files deserve a draft requirement,
> which are only kept in sync, and which are ignored as boilerplate — then writes the
> drafts. Without it, prompt and spec files would stay invisible to the registry, or
> every README would pollute it with junk drafts.

Every bullet below is binding.
- `classify_prose` sorts every untagged prose file (`.md`/`.html`) into one of three buckets — ignore, sync_only, or capability — and `draft` auto-drafts only the capability bucket. [[REQ-PROSE-900]] details the behaviour.
- The buckets govern auto-drafting only; an explicit tag on any file is always honored regardless of bucket, and a capability draft is scaffolded from the file's title and section headings. [[REQ-PROSE-901]] details the behaviour.

## Cases
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

## Context
**Notes**
- The bucket lists are fixed in the engine, not configurable; `.reqmapignore` remains the
  per-repo escape hatch for anything the buckets misjudge.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana runs extract on a repo with a `prompts/triage.md` nobody tagged. It gets its own
  draft requirement built from its title and headings. Her `README.md` gets none — but
  when she later tags the README `generated-from: REQ-DOCS-001`, the gate starts flagging
  it whenever that requirement's contract changes.

**Current implementation**
- `classify_prose` (the three-bucket router) and `_prose_facts` (title + heading scaffold)
  in `reqmap.py`; the prose walk lives inside `cmd_extract`.


--------------------


---
id: REQ-PROSE-900
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
---

# Sorting prose files into three drafting buckets

## Description
> Not every text file is a capability — a README and a prompt spec need different
> treatment. `classify_prose` sorts each untagged prose file into ignore (boilerplate),
> sync_only (README/docs/HTML, drift-checked only once hand-tagged), or capability
> (auto-drafted), so `draft` neither misses real specs nor floods the registry with junk.

Every bullet below is binding.
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

## Cases
CASE-1 — draft writes a requirement for an untagged capability-bucket prose file
  Given  `prompts/foo.md` with no `# implements:` tag
  When   `draft` runs
  Then   a new `draft`-status requirement is written scaffolded from that file

CASE-2 — classify_prose buckets meta/boilerplate files as ignore
  Given  the paths `CLAUDE.md`, `LICENSE`, and `_map.html`
  When   `classify_prose` runs on each
  Then   each returns `"ignore"`

CASE-3 — classify_prose buckets README/docs/html paths as sync_only
  Given  the paths `README.md`, `docs/sub/guide.md`, and `x.html`
  When   `classify_prose` runs on each
  Then   each returns `"sync_only"`

CASE-4 — classify_prose buckets prompt/spec prose as capability
  Given  the paths `prompts/senators/aurelius.md`, `specs/foo.md`, and `notes.md`
  When   `classify_prose` runs on each
  Then   each returns `"capability"`


--------------------


---
id: REQ-PROSE-901
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROSE-024]
---

# Scaffolding a draft from a prose file's own headings

## Description
> A bucket decides only whether to auto-draft; a hand-added tag always wins, so a
> hand-tagged README still counts as a member even though it is never auto-drafted. When
> a capability file is drafted, its title and section headings become the scaffold — and
> because the drift hash anchors on the authored contract, not the source prose, editing
> the original file afterward never falsely reports drift.

Every bullet below is binding.
- The buckets govern auto-drafting ONLY; an explicit tag on any file is always
  honored by the scanner regardless of bucket (so a hand-tagged README is still a member).
- A prose draft is scaffolded from the file's title (frontmatter `title:`, else the
  first `#` heading, else the HTML `<title>`/`<h1>`) plus its `##` section headings,
  recorded as an authoring hint.
- When a file has no `##` heading at all, its later `#` headings are the sections instead,
  so flat single-level prose (a prompt library) still yields a hint.
- The source prose is never the contract: the drift hash anchors on the authored
  Contract + Acceptance, so the prose may later drift freely from the authored requirement.

## Cases
CASE-1 — an explicit generated-from tag registers a sync_only file as a member
  Given  a `README.md` carrying a `<!-- generated-from: REQ-DOCS-001 -->` comment
  When   `scan_members` runs
  Then   the file appears as a member of `REQ-DOCS-001`, despite being sync_only

CASE-2 — _prose_facts prefers frontmatter title, then collects the H2 headings
  Given  a source with frontmatter `title: Senator Aurelius` and two `## ` headings
  When   `_prose_facts(src)` runs
  Then   it returns `("Senator Aurelius", ["Role", "Specialty"])`

CASE-3 — later H1 headings become the section hint when no H2 exists
  Given  `"# IDENTITY and PURPOSE\n\ntext\n\n# STEPS\n\n# OUTPUT INSTRUCTIONS\n"` (no `##` anywhere)
  When   `_prose_facts(src)` runs
  Then   the headings list is `["STEPS", "OUTPUT INSTRUCTIONS"]`, drawn from the later H1s

CASE-4 — editing the source prose file does not change the requirement's binding_hash
  Given  a capability-bucket prose file drafted into a requirement, then edited afterward
  When   `binding_hash` is computed on the requirement body before and after the edit
  Then   the two hashes are equal — the prose edit produced no drift

