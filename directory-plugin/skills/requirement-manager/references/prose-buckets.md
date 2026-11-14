# Prose & doc capabilities (the three buckets)

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

`init` scans `.md`/`.html` by default and classify each prose file
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
