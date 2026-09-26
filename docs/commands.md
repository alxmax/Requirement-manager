# All commands

[← back to the README](../README.md)


> In **this** repo, run commands from inside `plugin/`. In **your** repo, run
> from wherever `requirements/` lives — the engine resolves paths relative to cwd.

The CLI is **six verbs**. Five do the work, and everything else is a flag on `gate` (the
verdict and the reports on it), on `ask` (every other read-only question) or on `sync` (every
write), so the shape of a command tells you whether it can change a file. The sixth, `mcp`,
serves those same commands to an AI assistant. A seventh, `new`, scaffolded a blank
requirement until v8.0.0 removed it ([ADR-0045](adr/0045-new-is-deprecated.md)): write
`requirements/<ID>.md` yourself, or ask your assistant to.

| Verb | What it does |
|---|---|
| `init` | First-time setup: scaffold `requirements/` + `.reqmapignore`, draft the three-rung pyramid from untagged code and capability prose (one `level: system` placeholder, one `level: architecture` node per source directory, one `level: code` draft per file), then build the lock and map. It also seeds what planning and releasing need — `ROADMAP.md`, `requirements/_planning.json`, a `CHANGELOG.md`, and on a GitHub repo `.github/workflows/reqmap-release.yml` — and prints which file the version is read from. Idempotent; never clobbers an existing file. `--wipe` hard-resets first. `--minimal` skips the planning, release, MCP and site scaffolding and keeps the rest. |
| `gate` | **The verdict.** Bare, it is the commit/CI check (below). `--risk`, `--audit` and `--show` report on the same subject instead. Never writes anything. |
| `ask` | **Every other read-only question**: search, overlapping contracts, the review plan. Never writes anything, and its exit code is the question's, never the verdict's. Since v8.0.0 `gate` refuses them and names `ask` ([ADR-0044](adr/0044-questions-leave-the-verdict-verb.md)); every verb refuses a flag another verb owns. |
| `sync` | **The write path.** Rescan members, advance the drift baseline, and regenerate the map, `_findings.md` and the generated integration artifacts — in one step. `--accept-drift` is required when a `confirmed` or `implemented` contract changed. |
| `mcp` | Serve the engine over the Model Context Protocol on stdio: thirteen tools named for the question they answer, each one `reqmap.py` invocation in a fresh process, plus each requirement and the committed map as resources. Read-only unless `--allow-writes`. See [MCP server](integrations.md#mcp-server-claude-code-vs-code-with-copilot-any-mcp-client). |
| `clarify AREA-NAME-NNN` | Ask what a requirement has *not* answered: vague terms with no threshold, numbers with no unit, unbounded quantities, clauses with no case, a missing failure path. Read-only, always exit 0, never a gate rule — run it before implementing, so the ambiguity is resolved in the requirement rather than guessed in code. `--json` for an agent. |

**`gate` — the bare verdict.** Link sync (every tag resolves, every enforced
requirement has an `implements:` member, every `depends_on` target exists) then
requirement readability then committed-map freshness. Exits non-zero on link-sync
errors only; drift and test-link integrity are warnings. Bare, it runs only the rules
that say a link, the drift baseline or the committed map is broken, and prints
readability errors only ([ADR-0049](adr/0049-a-bare-gate-says-only-what-is-broken.md));
`--full` runs every rule and prints every readability warning. `--strict` promotes
drift and test-link integrity to errors, `--json` emits one machine-readable document with the same rule, lint and map
verdict as text output,
`--since <ref>` scopes it to requirements whose members changed since a git ref, and
`--no-lint` / `--no-map-check` opt out of the two extras.

**`gate` — the reports on the verdict.**

| Flag | What it answers |
|---|---|
| `--risk` | *What should I work on next?* A health score plus counted risk buckets. `--json`/`--badge` for the numbers alone, `--untagged` for the files carrying no `implements:` tag. |
| `--audit` | *How is this repo doing?* Every discovery pass in one report: gate, risk, duplicates, design, tag coverage, the exemptions in force, corpus shape, and the plan against the releases (a milestone already shipped, version sources that disagree). The exit code comes from the gate alone — the rest is advice. |
| `--show ID` | *What does this do / where is X?* One requirement's dossier: contract, dependencies both ways, members by role with `file:line`, open questions, risk signals. `--json` adds the requirement's frontmatter and body. |

**`ask` — the questions.**

| Flag | What it answers |
|---|---|
| `--search "query"` | Rank requirements by lexical relevance (TF-IDF cosine). `--top N`. Says so explicitly when nothing clears the floor, rather than showing a spurious top hit. `--json` for an agent. |
| `--dupes` | Requirement pairs whose contracts overlap, so a divergent re-implementation is caught before it lands. `--threshold T` (default 0.35). A pair a reviewer read and found different is recorded with `distinct_from: [ID]` and stops being reported; `--json` lists every pair and what was skipped. |
| `--review [ID]` | A JSON review plan (intent, contract, acceptance, anchors) — the AI feed for advisory quality review. |

**`sync` — the write modes.**

| Flag | What it does |
|---|---|
| *(bare)* | Rebuild everything derived: lock, `_map.*`, `_findings.md`, the integration artifacts. Then print, as suggestions only, where the plan and reality disagree — see [Planning and releasing](planning.md). |
| `--accept-drift` | Advance the baseline for a `confirmed`/`implemented` contract you edited on purpose. Without it, `sync` refuses. |
| `--release [vX.Y.Z]` | Cut the next version planned in `_planning.json` — the lowest milestone above the version already declared — or the one named. Prints the plan and writes nothing without `--apply`; with it, bumps the version files, writes the dated CHANGELOG entry and drops the milestone and its bars from the plan. Exit 2 when nothing is planned, the version is not above the baseline, or the gate has errors. `--json` is what a release workflow reads. |
| `--retire ID [ID ...]` | Take one requirement — or a whole class — out of service. Prints the blast radius first and writes nothing without `--apply`; `--delete` removes it outright instead of deprecating, `--force` proceeds past dependents or a dirty tree. A batch retires in a graph-computed order under one working-tree check; a dependent that is already `deprecated`, or that is in the same batch, never blocks. |

Confirming a requirement is **not** a command — it is a human's answer. Edit
`status: confirmed` in the frontmatter once someone has actually read it. The gate
enforces the invariant (a confirmed requirement with no `implements:` member is an
error), and `sync` demotes an edited contract back to `draft` on its own.

**Map size — `MAP_PROFILE` and `MAP_LOCALES`.** Two keys in `requirements/_config.json`
choose how much the committed map carries. The defaults, `"full"` and every cached locale,
write all four Mermaid diagrams to `_map.md`. `{"MAP_PROFILE": "compact", "MAP_LOCALES": []}`
writes a short `_map.md` (status totals, system needs, links to `_map.json` and the offline
viewer) and minified JSON without cached translations; `["ro"]` keeps Romanian only.
Compact JSON keeps every contract, case, note and link. The offline `_map.html` embeds
minified JSON in either profile, and map freshness compares JSON by content, not bytes.

> Removed in `v4.0.0`: the old one-verb-per-question CLI (`map`, `next`, `scan`,
> `lint`, `show`, `health`, `export`, `draft`, `plan`, `findings`, `confirm`,
> `coverage`, `site`, `dupes`, `search`, `review`, `check`). Each is now a flag
> above. `translate` was removed separately on 2026-09-05; the viewer still reads
> a `requirements/_i18n/<locale>.json` cache if one is committed, but nothing
> regenerates it any more.
