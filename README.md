# requirement-manager

[![ci](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml)

**▶ [Live requirement map](https://alxmax.github.io/Requirement-manager/map.html)** — this
repo's own requirement graph, published to GitHub Pages. Once the Pages source is set to
"GitHub Actions", the `deploy-map` job republishes it on every push to `main` via OIDC —
a short-lived token, no stored secrets.

**Stop your AI agent from drifting away from what you already agreed on.**

A long agent session forgets earlier decisions. A fresh session on the same
codebase re-implements something a different way. Two agents working on the
same repo make incompatible choices, and nothing tells either of them. The fix
isn't a longer prompt — it's a written contract the agent has to check itself
against. `requirement-manager` gives every feature of your project one such
file: a Markdown spec that says *what it should do*. Code links back to it
with a one-line comment, and a small Python script checks that the two never
fall out of sync — and draws you a map of how everything connects.

The engine is a single stdlib-only Python script (3.9+ — the oldest version CI
actually tests, on Linux and Windows). It runs in any repo, with any AI assistant
(Claude Code, Copilot, Gemini CLI, or none), and needs no installation — just copy
one file. It's especially handy when several people or
several AI agents touch the same codebase and the specs slowly rot.

## Worked example

One requirement, one agent session, one drift the gate caught — real terminal output, not a mockup:

```
$ python scripts/reqmap.py new AREA-DEMO-999
created .\requirements\AREA-DEMO-999.md

$ # a human reads it, then sets `status: confirmed` in the frontmatter
promoted AREA-DEMO-999: draft -> confirmed
  note: no `tested-by:` member — wire an acceptance test (`# tested-by: AREA-DEMO-999`) or set `test_exempt: <reason>` to silence the untested signal.
  next: reqmap.py sync

$ python scripts/reqmap.py sync
  lock update: AREA-DEMO-999 hash changed (new->703e565f)
lock updated.
WARN  AREA-DEMO-999: confirmed but no tested-by: tag — acceptance tests not linked
info  1 open verify-intent finding(s) — run `reqmap.py sync`

1 requirements (1 confirmed, 0 legacy-schema), 1 members, 0 errors, 1 warnings.
wrote .\requirements\_map.md
wrote .\requirements\_map.json
(1 nodes, 0 edges)

$ python scripts/reqmap.py gate
WARN  AREA-DEMO-999: confirmed but no tested-by: tag — acceptance tests not linked
WARN  AREA-DEMO-999: DRIFT — contract changed since lock; re-check 1 member(s): scripts/_demo_hello.py:2
info  1 open verify-intent finding(s) — run `reqmap.py sync`

1 requirements (1 confirmed, 0 legacy-schema), 1 members, 0 errors, 2 warnings.
```

Between `sync` and `gate`, the requirement's contract clause changed (`hello`
returns `'hello'` -> `'hello, world'`) — but the code that backs it,
`scripts/_demo_hello.py`, was never touched. Nothing else in the toolchain would
have caught that; `gate` did, because the drift baseline in `_reqlock.json` hashes
the requirement's own contract text, not just its existence.

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
4. **The map shows the big picture.** `reqmap.py sync` generates diagrams and a
   double-click-to-open HTML viewer of how requirements and code connect.

## Try it in 2 minutes

Copy the engine into any project, then:

```bash
python scripts/reqmap.py init     # scaffold + draft requirements from your existing code
python scripts/reqmap.py gate     # are code and specs in sync? (report-only)
python scripts/reqmap.py sync      # build the visual map → open requirements/_map.html
```

`init` is the friendly starting point — it sets everything up and tells you the
next step. You never edit the generated files (`_map.*`, `_reqlock.json`) by hand.

It also writes a starter `.reqmapignore`, and never overwrites one you already have.
Two of its lines matter the first time you run an AI subagent in an isolated worktree
(`.worktrees/`, `.claude/worktrees/`): each worktree is a full second copy of your repo,
so without them the gate counts every member twice and reports the copies' tags as
errors that do not exist in your code — and CI, which checks out a clean tree, disagrees.

## What a requirement file looks like

A requirement is just Markdown: a small YAML header plus prose. Trimmed example:

```markdown
---
id: AUTH-LOGIN-001
status: confirmed
layer: feature
depends_on: [CORE-SESSION-002]
milestone: v1.4          # optional — shows this requirement in the Roadmap tab
---

# User login

## Description
> Users need to reach their own data securely.

Every bullet below is binding.
- `login` accepts an email + password and returns a session token.
- `login` rejects an unknown email with a generic error (no user enumeration).

## Cases (= tests)
CASE-1  A valid email/password returns a token.
CASE-2  A wrong password returns the generic error.
```

The header carries the machine-readable bits (`id`, `status`, what it
`depends_on`); the prose explains intent and lists the acceptance criteria that
become your tests.

### Optional: the three specification levels

A requirement may also declare where it sits on the V-model's left arm, with
`level: system | architecture | code`, and name the level above it with
`satisfies:`. Neither field is required — a corpus that sets neither behaves
exactly as it did before these fields existed. Adopt them and two extra
checks switch on: `lint` reports a level whose fan-out leaves the 5–20 band, and
the gate reports a level whose tests sit at the wrong depth (a `code`
requirement is verified `@unit`, an `architecture` one `@integration`, a
`system` one `@system`).

Both fields are prose about *this* corpus, so nothing forces an id to advertise
its level. This repo chooses to, because a reader meets an id long before its
file: `SYS-` for a system requirement, `ARCH-` for an architecture one, `REQ-`
for a detailed-design one. Your ids can say anything you like.

A single `.md` may hold **several** requirements — one frontmatter block each,
a block starting at a `---` line immediately followed by `id:`. That is how an
architecture requirement keeps its own detailed design in one document instead
of scattering it across dozens of files. A file with one block is read exactly
as before.

## AI assistant integrations

### Plain CLI (any tool, or no tool)

Copy `reqmap.py` from `plugin/scripts/` into your repo's `scripts/` directory and
run it directly. No AI assistant needed:

```bash
# one-time copy
cp /path/to/plugin/scripts/reqmap.py scripts/reqmap.py

# then from your repo root:
python scripts/reqmap.py init
python scripts/reqmap.py gate
python scripts/reqmap.py sync
```

### Claude Code plugin (most integrated)

Install from the plugin marketplace — Claude Code will auto-trigger the skills,
surface commands via the menu, and update the engine when a new version ships:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

On first use in any repo the skill copies `scripts/reqmap.py` into that repo and
runs `init`. The requirement template is built into the script — nothing else to
download.

### GitHub Copilot, Gemini CLI, and others

The engine is a plain Python CLI with no AI SDK dependency. Any assistant that
can run shell commands can drive the full workflow. The plugin ships two
interoperability artifacts:

**`plugin/tool_definition.json`** — every `reqmap.py` command in
[OpenAI function-calling schema](https://platform.openai.com/docs/guides/function-calling).
Load this file so your assistant can discover all available commands, their
parameters, and their descriptions without reading source code.

**`SKILL.universal.md` files** — AI-agnostic variants of each skill's instruction
file, with all Claude Code-specific directives removed (`Skill` tool invocations,
`${CLAUDE_PLUGIN_ROOT}` paths). Drop any of these as a plain system prompt or
`AGENTS.md` / `GEMINI.md` instruction:

| File | Skill |
|---|---|
| `plugin/skills/requirement-manager/SKILL.universal.md` | Core SSOT + drift workflow |
| `plugin/skills/excalidraw-diagram/SKILL.universal.md` | Excalidraw diagram generation |
| `plugin/skills/requirement-quality-review/SKILL.universal.md` | Advisory quality review |

**Verify AI-agnostic compatibility:**

```bash
python scripts/test_cross_tool.py
```

Stdlib-only headless test: seeds `reqmap.py` in a tempdir, runs `sync → gate → map`,
and asserts a valid `_map.json` is produced. If this passes, the engine works under
any assistant — or with no assistant at all.

## All commands

> In **this** repo, run commands from inside `plugin/`. In **your** repo, run
> from wherever `requirements/` lives — the engine resolves paths relative to cwd.

The CLI is **five verbs**. Everything else is a flag on `gate` (every read-only
question) or on `sync` (every write), so the shape of a command tells you whether
it can change a file.

| Verb | What it does |
|---|---|
| `init` | First-time setup: scaffold `requirements/` + `.reqmapignore`, draft requirements from your existing code and prose, build the lock and map, print guided next steps. Idempotent; never clobbers an existing `.reqmapignore`. `--wipe` hard-resets first; `--no-site` skips the `docs/architecture.html` step. |
| `new AREA-NAME-NNN` | Scaffold one blank requirement from the built-in template. `--from-todo "name" --id ID` pre-fills it from a `TODO.md` item instead; add `--mark-done` to tick that item off. |
| `gate` | **The verdict, and every read-only question.** Bare, it is the commit/CI check (below). The mode flags each answer one question instead. Never writes anything. |
| `sync` | **The write path.** Rescan members, advance the drift baseline, and regenerate the map, `_findings.md`, the site regions and the generated integration artifacts — in one step. `--accept-drift` is required when a `confirmed` or `implemented` contract changed. |
| `clarify AREA-NAME-NNN` | Ask what a requirement has *not* answered: vague terms with no threshold, numbers with no unit, unbounded quantities, clauses with no case, a missing failure path. Read-only, always exit 0, never a gate rule — run it before implementing, so the ambiguity is resolved in the requirement rather than guessed in code. `--json` for an agent. |

**`gate` — the bare verdict.** Link sync (every tag resolves, every enforced
requirement has an `implements:` member, every `depends_on` target exists) then
requirement readability then committed-map freshness. Exits non-zero on link-sync
errors only; drift and test-link integrity are warnings. `--strict` promotes those
two to errors, `--json` emits one machine-readable document, `--since <ref>` scopes
it to requirements whose members changed since a git ref, and `--no-lint` /
`--no-map-check` opt out of the two extras.

**`gate` — the read-only questions.**

| Flag | What it answers |
|---|---|
| `--risk` | *What should I work on next?* A health score plus counted risk buckets. `--json`/`--badge` for the numbers alone, `--untagged` for the files carrying no `implements:` tag. |
| `--audit` | *How is this repo doing?* Every discovery pass in one report: gate, risk, duplicates, design, tag coverage, the exemptions in force, corpus shape. The exit code comes from the gate alone — the rest is advice. |
| `--show ID` | *What does this do / where is X?* One requirement's dossier: contract, dependencies both ways, members by role with `file:line`, open questions, risk signals. |
| `--search "query"` | Rank requirements by lexical relevance (TF-IDF cosine). `--top N`. Says so explicitly when nothing clears the floor, rather than showing a spurious top hit. |
| `--dupes` | Requirement pairs whose contracts overlap, so a divergent re-implementation is caught before it lands. `--threshold T` (default 0.35). |
| `--design` | Advisory design review of the code: the four OOP pillars, three Chidamber & Kemerer per-class metrics (Python only), plus house standards. Read-only, exit 0, never part of the gate; thresholds live in `requirements/_config.json`. |
| `--implement ID` | The brief for writing the code: obligations, cases, the exact tags the new code must carry, where similar code already lives. `--json` for a coding agent. |
| `--review [ID]` | A JSON review plan (intent, contract, acceptance, anchors) — the AI feed for advisory quality review. |

**`sync` — the write modes.**

| Flag | What it does |
|---|---|
| *(bare)* | Rebuild everything derived: lock, `_map.*`, `docs/map.html`, `_findings.md`, the site regions, the integration artifacts. |
| `--accept-drift` | Advance the baseline for a `confirmed`/`implemented` contract you edited on purpose. Without it, `sync` refuses. |
| `--retire ID [ID ...]` | Take one requirement — or a whole class — out of service. Prints the blast radius first and writes nothing without `--apply`; `--delete` removes it outright instead of deprecating, `--force` proceeds past dependents or a dirty tree. A batch retires in a graph-computed order under one working-tree check; a dependent that is already `deprecated`, or that is in the same batch, never blocks. |
| `--suggest-verifies` | Propose `# verifies: <ID>#CASE-N` tags for tests already named after the criterion they check. `--apply` writes them; ambiguous matches never are. |
| `--attach <page>` | Refresh the engine-owned regions (nav links, counts) of a presentation page, scaffolding one if absent. `--regions nav,stats`, `--diagram <rel>`. |

Confirming a requirement is **not** a command — it is a human's answer. Edit
`status: confirmed` in the frontmatter once someone has actually read it. The gate
enforces the invariant (a confirmed requirement with no `implements:` member is an
error), and `sync` demotes an edited contract back to `draft` on its own.

> Removed in `v4.0.0`: the old one-verb-per-question CLI (`map`, `next`, `scan`,
> `lint`, `show`, `health`, `export`, `draft`, `plan`, `findings`, `confirm`,
> `coverage`, `site`, `dupes`, `search`, `review`, `check`). Each is now a flag
> above. `translate` was removed separately on 2026-09-05; the viewer still reads
> a `requirements/_i18n/<locale>.json` cache if one is committed, but nothing
> regenerates it any more.

## The Excalidraw diagram skill

Bundled alongside `requirement-manager` is a second skill — **`excalidraw-diagram`**
— that turns a system description into a genuine [Excalidraw](https://excalidraw.com)
scene (`.excalidraw`) and a self-contained HTML viewer (`.html`). The output is
hand-drawn-look and fully editable, not a screenshot.

**When to reach for it:**
- "Diagram this repo's architecture" / "draw the flow"
- Flowcharts, pipelines, multi-agent layouts, state flows, module maps
- Any time you want a whiteboard-style schematic you can open in excalidraw.com

**How to invoke it:**
- *Claude Code* — ask for the `excalidraw-diagram` skill; it explores the repo,
  writes a generator script against the built-in `Scene` API, runs it, and delivers
  both files.
- *Other assistants* — load `SKILL.universal.md` as a system prompt and call the
  builder CLI directly (see CLI helper commands below).

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

**Linking a diagram to your project page:** `reqmap.py sync --attach docs/architecture.html --diagram <rel-path-to.html>` adds a live link to the diagram in the engine-owned nav region of your project page.

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
      - uses: alxmax/requirement-manager/check@v5
```

The action runs `reqmap.py gate`, then `map --check` (freshness) and `lint --strict`
— both default-on, both switchable off with `freshness: 'false'` / `lint: 'false'`.
It also warns when the `reqmap.py` you vendored is older than the engine the pinned
`check@vN` ships, so a copy that quietly stopped running half the checks says so on the
run instead of staying green in silence (`stale-engine: 'error'` to fail the build on it,
`'off'` to silence it). Inputs `reqmap-path` and `working-directory` adapt it to wherever
you vendored the engine — see [`check/action.yml`](check/action.yml). Or skip the action
entirely: `- run: python -X utf8 scripts/reqmap.py gate`.

`@v2` is a major-alias tag: it is force-moved onto every released commit, so it always
resolves to the latest release on that interface line. Pin an exact `vX.Y.Z` tag or a
commit SHA instead if you want a frozen ref. `@v1` still works and still runs the
gate-only step list it always did, but it no longer moves — it needs an engine seeded
from plugin v2.0.0+, and `@v2` needs v2.3.4+ (the release that added `lint_exempt:`).

## How fast is it on a big repo

Measured, not asserted — `python -X utf8 scripts/benchmark_scan.py` builds a synthetic
tree and times the operations you actually wait on. On **10,000 source files / 100
requirements** (Python 3.11, Windows, warm cache):

| operation | seconds |
|---|---|
| `load_requirements` | 0.03 |
| `scan_all` — one walk, every extraction | 2.53 |
| `gate` (given that walk) | 2.46 |
| build + render map | 0.03 |

The gate used to cost **three** full walks of the tree rather than one: `scan_members`,
`scan_ac_verifies` and `scan_test_levels` each opened every file, and together they were
essentially its entire runtime (3.06s + 2.76s + 2.81s of 8.49s). `scan_all` reads each
file once and runs all three extractions on the same lines — it now costs about what a
single walk cost before (2.53s vs 2.62s for `scan_members` alone), and scanning plus
gating a 10k-file tree went from ~11s to ~5s. A test asserts `scan_all` returns exactly
what the three scanners return, because "they look the same" is not evidence when each
has different masking rules.

The benchmark is deliberately **not** wired into CI: a shared runner's I/O varies far too
much for a timing assertion to mean anything, and a flaky performance gate teaches people
to ignore red.

## Glossary (the jargon, in plain words)

- **Capability / requirement** — one thing your app does, described in one file.
- **Single source of truth (SSOT)** — the one place the real answer lives, so
  there is nothing to keep in sync by hand.
- **Tag / membership** — the comment that links code to a requirement. Four
  roles exist: `implements`, `generated-from`, `validated-against`, `tested-by`.
  The list of members is discovered by scanning the code — never hand-maintained.
- **The gate** — the `gate` command; it fails when code and specs disagree.
- **Drift** — a requirement's contract changed but the code wasn't re-checked.
  The tool spots this by hashing the spec and comparing it to a saved baseline
  (`_reqlock.json`).
- **Layer (`bus` vs `feature`)** — `bus` is shared foundation that many things
  rely on; `feature` is built on top of the bus.
- **Dogfooding** — this repo uses the tool on itself: `plugin/requirements/`
  describes `reqmap.py`'s own capabilities, and its own gate passes with zero errors.

## How this repo is laid out

```
.claude-plugin/marketplace.json             marketplace manifest (this repo is a marketplace)
plugin/                                     the plugin — self-contained
  .claude-plugin/plugin.json                plugin manifest
  tool_definition.json                      OpenAI function-calling schema for all reqmap commands
  skills/requirement-manager/
    SKILL.md                                full contract & authoring rules (Claude Code)
    SKILL.universal.md                      AI-agnostic variant (any assistant)
  skills/excalidraw-diagram/
    SKILL.md                                diagram skill contract (Claude Code)
    SKILL.universal.md                      AI-agnostic variant (any assistant)
  skills/requirement-quality-review/
    SKILL.md                                advisory quality review (Claude Code)
    SKILL.universal.md                      AI-agnostic variant (any assistant)
  scripts/reqmap.py                         the engine (Python stdlib only, 10,259 lines)
  scripts/test_reqmap.py                    the engine's own regression suite (importable: `python scripts/test_reqmap.py`)
  requirements/*.md                         the source of truth (one file per architecture capability, its children beside it)
  requirements/_reqlock.json                the drift baseline (committed)
scripts/
  check_versions.py                         version-coherence gate (plugin.json vs marketplace.json)
  check_engine_bump.py                      engine-change gate (reqmap.py diff => MAP_ENGINE_VERSION must move)
  test_cross_tool.py                        headless integration test — sync->gate->map, no AI needed
app/                                        the React viewer (built into the single-file _map.html)
docs/                                       guides, plans + specs
TODO.md                                     optional planning file — feeds the Roadmap tab in the viewer
```

`SKILL.md` (authoritative for authoring rules, statuses, and the gate):
[`plugin/skills/requirement-manager/SKILL.md`](plugin/skills/requirement-manager/SKILL.md).

**`TODO.md` format** — group items under `## vX.Y` milestone headings; each item is
a checkbox with an optional `| lane: bus|feature|ops` suffix. Completed items (`[x]`)
are hidden in the chart.

```markdown
## v1.14
- [ ] Promote-todo command    | lane: feature
- [ ] Gate validation for milestone IDs | lane: ops
```

Items appear as amber dashed bars in the Roadmap tab until you replace them with a
real requirement file.

## Why it works the way it does

The decisions that shape the tool — the single-file engine, what may fail a build versus only
warn, the deliberately parked half of the V-model, and four things considered and *not* built —
are recorded as ADRs in [`docs/adr/`](docs/adr/README.md), with the evidence each was decided on
and the condition that would justify revisiting it.

## Contributing

[`CONTRIBUTING.md`](CONTRIBUTING.md) — setup, the gate/test loop, and the two rules that
explain most review feedback (a behaviour change ships with its requirement; the engine
stays stdlib-only). Security reports go through private disclosure:
[`SECURITY.md`](SECURITY.md).

## License

See [LICENSE](LICENSE) — Business Source License 1.1.
