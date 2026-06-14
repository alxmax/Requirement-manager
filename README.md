# requirement-manager

[![ci](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml)

**Keep your code and your specs from drifting apart.**

`requirement-manager` gives every feature of your project a single home: one
Markdown file that says *what it should do*. Your code links back to that file
with a one-line comment. A small Python script then checks that the two never
fall out of sync — and draws you a map of how everything connects.

It runs as a plain command-line script (a single file, no installation needed)
**and** as a [Claude Code plugin](plugin/.claude-plugin/plugin.json). It's
especially handy when several people — or several AI agents — touch the same
codebase and the specs slowly rot.

## Why would I want this?

On most projects the "spec" lives in someone's head, a stale wiki, or a ticket
nobody reads. Over time the code says one thing and the docs say another. This
tool turns the spec into a real file that lives **next to the code** and is
**checked by CI**, so drift fails the build instead of shipping silently.

## The idea in 30 seconds

1. **One file per capability.** Each thing your app does gets a Markdown file
   (a *requirement*) describing it. That file is the single source of truth.
2. **Code points back.** In your source, a comment tags which requirement a
   function belongs to:
   ```python
   # implements: AUTH-LOGIN-001
   def login(email, password): ...
   ```
3. **The gate keeps them honest.** `reqmap.py check` verifies that every tag
   points to a real requirement, every requirement has code, and nothing has
   silently changed. Run it before every commit (and in CI).
4. **The map shows the big picture.** `reqmap.py map` generates diagrams and a
   double-click-to-open HTML viewer of how requirements and code connect.

## Try it in 2 minutes

```bash
# from inside any project of yours
python scripts/reqmap.py init     # creates the folders, drafts requirements from your
                                  # existing code, and prints what to do next
python scripts/reqmap.py check    # the gate: are code and specs in sync?
python scripts/reqmap.py map      # build the visual map → open requirements/_map.html
```

`init` is the friendly starting point — it sets everything up and tells you the
next step. You never edit the generated files (`_map.*`, `_reqlock.json`) by hand.

## What a requirement file looks like

A requirement is just Markdown: a small header (YAML "frontmatter") plus prose.
Trimmed example:

```markdown
---
id: AUTH-LOGIN-001
status: confirmed
layer: feature
depends_on: [CORE-SESSION-002]
milestone: v1.4          # optional — shows this requirement in the Roadmap tab
---

# User login

> WHY: users need to reach their own data securely.

## WHAT — Contract (normative)
- It shall accept an email + password and return a session token.
- It shall reject an unknown email with a generic error (no user enumeration).

## HOW — Acceptance (= tests)
- A valid email/password returns a token.
- A wrong password returns the generic error.
```

The header carries the machine-readable bits (`id`, `status`, what it
`depends_on`); the prose explains intent and lists the acceptance criteria that
become your tests.

## Install as a Claude Code plugin

This repo is also a plugin marketplace. Inside Claude Code:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

Then ask for the `requirement-manager` skill in any repo. On first use it copies
`scripts/reqmap.py` into that repo — the requirement template is built into the
script, so there's nothing else to download.

## All commands

> Run these from inside `plugin/` in this repo (the engine resolves paths
> relative to where it runs).

| Command | What it does |
|---|---|
| `init` | First-time setup: scaffold + draft requirements from your code + lock + map + next steps |
| `check` | **The gate** — every tag resolves, every requirement has code, nothing drifted. Run before each commit. Flags: `--strict` (promotes drift + test-link warnings to errors), `--json` (structured output), `--since <ref>` (git-scoped: only requirements touched since `ref`) |
| `map` | Generate diagrams (`_map.md`) + graph (`_map.json`) + self-contained viewer (`_map.html` with 4 tabs: Map · Problems · Spec · **Roadmap**). Also reads `TODO.md` from the repo root and inlines a `todos` array into `_map.json` so the Roadmap tab can show planned work alongside requirements |
| `next` | "What should I work on next?" — a prioritized, actionable list |
| `new AREA-NAME-NNN` | Scaffold a new empty requirement from the template |
| `scan` | List which code belongs to which requirement |
| `lint` | Readability and structure check on non-draft requirements (long sentences, stacked conditions, missing sections). `--strict` exits non-zero on errors |
| `show <ID>` | Consolidated dossier for one requirement: contract, dependencies both ways, code members, open questions, risk signals |
| `similar` | Flag requirement pairs with overlapping contracts (TF-IDF cosine). `--threshold T` overrides the default 0.35 |
| `health` | Corpus coherence snapshot: percentage of requirements fully green (confirmed + member + tested + no open questions + not drifted). `--json` for a CI badge |
| `export` | Emit just the graph JSON (for an external front-end) |
| `extract` | Draft requirements from untagged legacy code |
| `candidates` | Read-only JSON plan for AI-assisted extraction (writes no files) |
| `findings` | Collect open "needs human review" notes into `_findings.md` |
| `promote <ID>` | Mark a reviewed requirement as `confirmed` (the human sign-off step) |

## Run the gate in CI

Fail the build on drift, on every push and pull request:

```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v1
```

The action just runs `reqmap.py check`. Inputs `reqmap-path` and
`working-directory` adapt it to wherever you vendored the engine — see
[`check/action.yml`](check/action.yml).

## Glossary (the jargon, in plain words)

- **Capability / requirement** — one thing your app does, described in one file.
- **Single source of truth (SSOT)** — the one place the real answer lives, so
  there is nothing to keep in sync by hand.
- **Tag / membership** — the comment that links code to a requirement. Four
  roles exist: `implements`, `generated-from`, `validated-against`, `tested-by`.
  The list of members is discovered by scanning the code — never hand-maintained.
- **The gate** — the `check` command; it fails when code and specs disagree.
- **Drift** — a requirement's contract changed but the code wasn't re-checked.
  The tool spots this by hashing the spec and comparing it to a saved baseline
  (`_reqlock.json`).
- **Layer (`bus` vs `feature`)** — `bus` is shared foundation that many things
  rely on; `feature` is built on top of the bus.
- **Dogfooding** — this repo uses the tool on itself: `plugin/requirements/`
  describes `reqmap.py`'s own capabilities, and its own gate passes with zero
  errors.

## How this repo is laid out

```
.claude-plugin/marketplace.json        marketplace manifest (this repo is a marketplace)
plugin/                                the plugin — self-contained
  .claude-plugin/plugin.json           plugin manifest
  skills/requirement-manager/SKILL.md  the full contract & authoring rules
  skills/requirement-quality-review/   on-demand AI review of requirement quality (advisory)
  skills/excalidraw-diagram/           generate Excalidraw architecture / flow diagrams
  scripts/reqmap.py                    the engine (Python stdlib only, ~3200 lines)
  requirements/*.md                    the source of truth (one file per capability)
  requirements/_reqlock.json           the drift baseline (committed)
app/                                   the React viewer (built into the single-file _map.html)
docs/                                  guides + Excalidraw diagrams (open plugin_architecture.html for a visual overview)
TODO.md                                optional planning file — feeds the Roadmap tab in the viewer
```

**`TODO.md` format** — group items under `## vX.Y` milestone headings; each item is a checkbox with an optional `| lane: bus|feature|ops` suffix. Completed items (`[x]`) are hidden in the chart.

```markdown
## v1.14
- [ ] Promote-todo command    | lane: feature
- [ ] Gate validation for milestone IDs | lane: ops
```

Items appear as amber dashed bars in the Roadmap tab until you replace them with a real requirement file.

## Want the full details?

[`SKILL.md`](plugin/skills/requirement-manager/SKILL.md) is the authoritative
reference: statuses, the layer model, authoring rules, and exactly how the gate
decides pass or fail.

## License

See [LICENSE](LICENSE) — Business Source License 1.1.
