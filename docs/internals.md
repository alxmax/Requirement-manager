# How this repo is laid out, and how fast the engine is

[← back to the README](../README.md)


```
.claude-plugin/marketplace.json             marketplace manifest (this repo is a marketplace)
.mcp.json, .vscode/mcp.json                 MCP client configs that start this repo's own server
plugin/                                     the plugin — self-contained
  .claude-plugin/plugin.json                plugin manifest
  tool_definition.json                      OpenAI function-calling schema for all reqmap commands
  skills/requirement-manager/
    SKILL.md                                full contract & authoring rules (Claude Code)
    SKILL.universal.md                      AI-agnostic variant (any assistant)
  skills/requirement-quality-review/
    SKILL.md                                advisory quality review (Claude Code)
    SKILL.universal.md                      AI-agnostic variant (any assistant)
  scripts/reqmap.py                         the command line: parser, dispatch, the Python floor
  scripts/reqmap_engine/                    the engine, one module per capability (Python stdlib only, 15,122 lines in all)
  scripts/reqmap_engine/mcp.py              the MCP server: protocol, the tool table, resources
  scripts/test_reqmap.py                    the regression suite's entry point — re-exports the five parts below
  scripts/test_reqmap_common.py             fixtures the parts share (runtime-built tag strings)
  scripts/test_reqmap_scan.py               reading the tree: parser, scanning, masking, walk, git
  scripts/test_reqmap_gate.py               the verdict: gate rules, drift, --since, test links
  scripts/test_reqmap_author.py             writing requirements: new, init, lint, clarify, retire
  scripts/test_reqmap_report.py             what it prints: map, viewer, site, health, audit, design
  requirements/*.md                         the source of truth (one file per architecture capability, its children beside it)
  requirements/_reqlock.json                the drift baseline (committed)
scripts/
  check_versions.py                         version-coherence gate (plugin.json vs marketplace.json)
  check_engine_bump.py                      engine-change gate (reqmap.py diff => MAP_ENGINE_VERSION must move)
  test_cross_tool.py                        headless integration test — sync->gate->map, no AI needed
app/                                        the React viewer (built into the single-file _map.html)
docs/                                       guides, plans + specs
  history/TODO-archive.md                   the retired TODO.md — history, not an instruction
ROADMAP.md                                  the live plan — Now / Next / Later; a bar opens its note
  requirements/_planning.json               Gantt bars, lanes, milestones and the release cadence (both seeded by `init`)
CHANGELOG.md                                one dated entry per release; read as the shipped history, written by `sync --release`
```

`SKILL.md` (authoritative for authoring rules, statuses, and the gate):
[`plugin/skills/requirement-manager/SKILL.md`](../plugin/skills/requirement-manager/SKILL.md).


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


The decisions that shape the tool — the engine's shape (one file, then a package), what may fail a build versus only
warn, the deliberately parked half of the V-model, and four things considered and *not* built —
are recorded as ADRs in [`docs/adr/`](adr/README.md), with the evidence each was decided on
and the condition that would justify revisiting it.

## Contributing

[`CONTRIBUTING.md`](../CONTRIBUTING.md) — setup, the gate/test loop, and the two rules that
explain most review feedback (a behaviour change ships with its requirement; the engine
stays stdlib-only). Security reports go through private disclosure:
[`SECURITY.md`](../SECURITY.md).
