# requirement-manager

[![ci](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml)

**Keep your code and your specs from drifting apart.**

`requirement-manager` gives every feature of your project a single home: one
Markdown file that says *what it should do*. Your code links back to that file
with a one-line comment. A small Python script then checks that the two never
fall out of sync — and draws you a map of how everything connects.

It runs as a plain command-line script (a single file, no installation needed),
as a [Claude Code plugin](plugin/.claude-plugin/plugin.json), and with any other
AI assistant that can call shell commands (Copilot, Gemini CLI, and others). It's
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
3. **The gate keeps them honest.** `reqmap.py gate` verifies that every tag
   points to a real requirement, every requirement has code, and nothing has
   silently changed. Run it before every commit (and in CI).
4. **The map shows the big picture.** `reqmap.py map` generates diagrams and a
   double-click-to-open HTML viewer of how requirements and code connect.

## Try it in 2 minutes

```bash
# from inside any project of yours
python scripts/reqmap.py init     # creates the folders, drafts requirements from your
                                  # existing code, and prints what to do next
python scripts/reqmap.py gate     # the gate: are code and specs in sync? (report-only)
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

## Using with other AI assistants

`reqmap.py` is a plain Python CLI — no AI SDK, no cloud dependency, stdlib only.
Any AI assistant that can run shell commands can drive the full workflow.

**GitHub Copilot, Gemini CLI, and other function-calling tools**

The plugin ships a machine-readable manifest — `plugin/tool_definition.json` — that
exposes every reqmap.py command in [OpenAI function-calling schema](https://platform.openai.com/docs/guides/function-calling).
Any tool that supports function calling can read this file to discover the available
commands, their parameters, and their descriptions.

**SKILL.universal.md — AI-agnostic instruction files**

Each of the three skills ships a `SKILL.universal.md` alongside the Claude
Code-specific `SKILL.md`. The universal variant has all Claude Code-specific
directives removed (no `Skill` tool invocations, no `${CLAUDE_PLUGIN_ROOT}` paths)
so it works as a plain system-prompt or instruction file with any AI assistant:

| File | For |
|---|---|
| `plugin/skills/requirement-manager/SKILL.universal.md` | Core SSOT + drift workflow |
| `plugin/skills/excalidraw-diagram/SKILL.universal.md` | Excalidraw diagram generation |
| `plugin/skills/requirement-quality-review/SKILL.universal.md` | Advisory quality review |

**Manual setup (any AI, any repo)**

The engine is a single file with no dependencies. Copy it into your repo once:

```bash
# copy reqmap.py from the plugin's scripts/ directory, then:
python scripts/reqmap.py init   # bootstrap: scaffold + draft + lock + map
python scripts/reqmap.py gate   # run the gate — works identically under any AI
python scripts/reqmap.py map    # generate the viewer
```

**Verifying AI-agnostic compatibility**

```bash
python scripts/test_cross_tool.py
```

Runs a headless integration test (stdlib only, no AI tooling required): seeds
reqmap.py in a tempdir, runs `sync → gate → map`, and asserts a valid `_map.json`
is produced. This is the falsification criterion for multi-AI compatibility.

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

> In **this** repo, run them from inside `plugin/`. In **your** repo, run from
> wherever `requirements/` lives — the engine resolves paths relative to where it runs.

| Command | What it does |
|---|---|
| `init` | First-time setup: scaffold + draft requirements from your code + lock + map + next steps |
| `gate` | **The gate** — every tag resolves, every requirement has code, nothing drifted. Run before each commit. Report-only: never touches `_reqlock.json`. Flags: `--strict` (promotes drift + test-link warnings to errors), `--json` (structured output), `--since <ref>` (git-scoped: only requirements touched since `ref`). (`check` is a deprecated alias, kept for backward compat.) |
| `sync` | Rescan + advance the drift baseline + regenerate the map in one step. Use after editing requirement files or tagging new code. `--accept-drift` to advance an edited confirmed/implemented contract. |
| `map` | Generate diagrams (`_map.md`) + graph (`_map.json`) + self-contained viewer (`_map.html` with 4 tabs: Map · Problems · Spec · **Roadmap**). Also reads `TODO.md` from the repo root and inlines a `todos` array into `_map.json` so the Roadmap tab can show planned work alongside requirements |
| `site --attach <page>` | Inject/refresh engine-owned regions (nav links + counts) into a presentation page; scaffolds one if absent. `--regions nav,stats`, `--diagram <rel>` links an Excalidraw HTML |
| `next` | "What should I work on next?" — a prioritized, actionable list |
| `new AREA-NAME-NNN` | Scaffold a new empty requirement from the template. Use `--from-todo "name" --id ID` to pre-fill from a TODO.md item. |
| `scan` | List which code belongs to which requirement |
| `lint` | Readability and structure check on non-draft requirements (long sentences, stacked conditions, missing sections). `--strict` exits non-zero on errors |
| `show <ID>` | Consolidated dossier for one requirement: contract, dependencies both ways, code members, open questions, risk signals |
| `dupes` | Flag requirement pairs with overlapping contracts (TF-IDF cosine). `--threshold T` overrides the default 0.35 |
| `health` | Corpus coherence snapshot: percentage of requirements fully green (confirmed + member + tested + no open questions + not drifted). `--json` for a CI badge |
| `export` | Emit just the graph JSON (for an external front-end) |
| `draft` | Draft requirements from untagged legacy code (input: existing code/prose) |
| `plan` | Read-only JSON plan for AI-assisted extraction (writes no files; use before `draft`) |
| `findings` | Collect open "needs human review" notes into `_findings.md` |
| `review [ID]` | Emit a JSON review plan (intent, contract, acceptance, anchors) for all requirements or one — an AI-feed for advisory quality review. Read-only |
| `confirm <ID>` | Mark a reviewed requirement as `confirmed` (the human sign-off step). Run `sync` after. |

## The Excalidraw diagram skill

Bundled alongside `requirement-manager` is a second skill — **`excalidraw-diagram`**
— that turns a system description into a genuine [Excalidraw](https://excalidraw.com)
scene (`.excalidraw`) and a self-contained HTML viewer (`.html`). The output is
hand-drawn-look and fully editable, not a screenshot.

**When to reach for it:**
- "Diagram this repo's architecture" / "draw the flow"
- Flowcharts, pipelines, multi-agent layouts, state flows, module maps
- Any time you want a whiteboard-style schematic you can open in excalidraw.com

**How to invoke it (Claude Code):**
Ask for the `excalidraw-diagram` skill in any conversation — it reads the code,
plans the layout, writes a Python generator script against the built-in `Scene` API,
runs it, and delivers both files. No external dependencies needed.

**CLI helper commands** (run from `plugin/skills/excalidraw-diagram/scripts/`):

| Command | What it does |
|---|---|
| `python excalidraw_builder.py` | Self-test / smoke test — verifies the builder is healthy |
| `python excalidraw_builder.py discover <repo> [out.py]` | Scan a repo and emit a runnable multi-layer poster scaffold (`make_diagram.py`) — fill in the real content, then run it |
| `python excalidraw_builder.py render <scene.excalidraw> [out_dir]` | Rebuild just the `.html` viewer from an existing scene (e.g. after hand-editing on excalidraw.com) |

**Output:** one `.excalidraw` + one `.html` per call.
- `.excalidraw` — drag onto excalidraw.com to edit; works fully offline.
- `.html` — double-click to open; has a built-in "Download .excalidraw" button.
  Loads Excalidraw from a CDN, so the first open needs a network connection.

**Linking a diagram to your project page:** `reqmap.py site --attach docs/architecture.html --diagram <rel-path-to.html>` adds a live link to the diagram in the engine-owned nav region of your project page.

The full builder API (shapes, auto-layout helpers, quality gates) is documented in
[`plugin/skills/excalidraw-diagram/SKILL.md`](plugin/skills/excalidraw-diagram/SKILL.md).

---

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

The action runs `reqmap.py gate`. Inputs `reqmap-path` and
`working-directory` adapt it to wherever you vendored the engine — see
[`check/action.yml`](check/action.yml). (`check` is kept as a deprecation alias so existing `@v1` usages need no change.)

## Glossary (the jargon, in plain words)

- **Capability / requirement** — one thing your app does, described in one file.
- **Single source of truth (SSOT)** — the one place the real answer lives, so
  there is nothing to keep in sync by hand.
- **Tag / membership** — the comment that links code to a requirement. Four
  roles exist: `implements`, `generated-from`, `validated-against`, `tested-by`.
  The list of members is discovered by scanning the code — never hand-maintained.
- **The gate** — the `gate` command; it fails when code and specs disagree. (`check` is a deprecated alias.)
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
  scripts/reqmap.py                    the engine (Python stdlib only, ~3700 lines)
  requirements/*.md                    the source of truth (one file per capability)
  requirements/_reqlock.json           the drift baseline (committed)
app/                                   the React viewer (built into the single-file _map.html)
docs/                                  guides, plans + specs (architecture diagrams regenerate via the excalidraw-diagram skill)
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
