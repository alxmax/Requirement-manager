# ADR-0035 — The engine is a package behind a thin CLI

- **Status:** Accepted. Supersedes [ADR-0014](0014-engine-stays-one-file.md) (one file, no
  size gate) and [ADR-0033](0033-the-costed-audit-the-split-is-blocked-by-one-representation.md)
  (still one file; the split is blocked by line-anchored member locations).
- **Decided:** 2026-09-07, **at the maintainer's direction** — the day after ADR-0033, and on
  **none** of the revisit conditions that record listed. That is stated here rather than
  smoothed over: the reader should know this is a decision, not a trigger firing.
- **Owner:** Alex
- **Evidence:** every number below was measured on the working tree that carries this record,
  by the command named beside it

## Context

[ADR-0033](0033-the-costed-audit-the-split-is-blocked-by-one-representation.md) ran the costed
audit [ADR-0014](0014-engine-stays-one-file.md) asked for and found the split's dominant cost was
not moving code but **rewriting every line-anchored member `loc`** in the committed,
freshness-checked artifacts — 580 of them across 215 requirements. It retired the line-count
trigger, kept one file, and named three conditions for reopening: three merge conflicts in
ninety days, a named external consumer, or member locations becoming definition-anchored.

None of the three has happened. The maintainer asked for the split anyway, with one hard
requirement — `reqmap.py` at roughly 500 lines — and this record does what ADR-0033 asked of
any next round: it starts from the priced decision and reports what the split actually cost.

## Decision

`plugin/scripts/reqmap.py` is the command line only — the parser, the dispatch, the Python
floor — and the flat namespace `import reqmap` has always offered. Everything else lives in
`plugin/scripts/reqmap_engine/`, one module per capability, imported **by name** (no build step,
no concatenation, no byte-compare — ADR-0014's objections to option (A) were to the concatenating
build, and this is not one).

**What it measured** (`wc -l`; an `ast` walk over every module's free names for the cycle counts; on 2026-09-07):

| | before | after |
|---|---|---|
| `reqmap.py` | 10,711 lines | **499** |
| engine modules | 1 | **48** (`reqmap_engine/*.py`, 12,122 lines in all) |
| largest module | — | `site.py`, 495 lines; median module 215 |
| `gate --design` findings on the engine | 45 on the one file | **3**, each accepted below (78 on the first cut) |
| import-time cycles between modules | — | **0** |
| call-time imports | — | **1** (`health._link_sync_errors` → `rules`, `workspace.GateContext`) |
| `subprocess` call sites | 1 | 1 (`git.py`, asserted by the suite) |
| tests | 1,073 | **1,073, all green**; `ruff --select E9,F` clean; `--help` byte-identical |

**What it cost — the figure ADR-0033 said to price** (`git diff --stat`, a `loc` diff of
`_map.json` before and after `sync --code ..`):

| | |
|---|---|
| requirements whose member locations changed | **223 of 238** |
| engine member locations | 616 in `reqmap.py` → 605 under `reqmap_engine/` + 11 in `reqmap.py` |
| `_map.json` / `_map.md` / `_memberlock.json` | 4,188 / 414 / 234 lines changed, in one change |
| `_reqlock.json` | **byte-identical** — no contract moved, so no drift, nothing to accept |

ADR-0033's estimate was right in kind and in scale. The cost was paid in the same change, by
regenerating the artifacts, not by making `loc` definition-anchored: that representational
change stays unmade, for the reason ADR-0033 gave (do it for its own sake or not at all).

Four rules make the package a bus and not a tangle:

1. **Tunables are read through the config module.** Every constant a repo may override in
   `_config.json` lives in `reqmap_engine/config.py` and is read as `cfg.NAME`, never imported
   by name. A name import snapshots the default at import time, and an override applied at
   startup would be invisible to the reader — the exact failure the config mechanism exists to
   prevent.
2. **Modules import lower modules by name; nothing imports upward.** The layering is
   `config → model → parse/sections/acceptance/text → tags/scan/orphans → git → locks → (features) → workspace → rules → gate → reqmap.py`. The one
   mutual dependency by design — the gate's map-freshness rule embeds the health record, and
   health runs two gate rules — is resolved inside the one function that needs it, with a
   comment saying why. Making the graph acyclic re-homed two dozen helpers to where their
   callers are (`_req_title`, `_req_file` into `text`; `_oversize` into `lintrules`;
   `_parse_todos` into `author`; `_risk_signals` into `risk`; `run_gate_rules` into `gate`).
3. **The package passes the review the engine runs on every repo.** `gate --design` on the
   first cut reported 78 findings. The file standards went first (eight modules over 500
   lines, two over 30 definitions: split again). Then the function-level ones, at the
   maintainer's direction: the three prefix families renamed (`_rule_X` → `_X_rule`,
   `_lint_X` → `_X_lint`, the nine `_design_*` helpers by what they compute), 13 long
   functions and 14 deep nestings split into named helpers, 331 inherited lines wrapped under
   100 columns. Every extracted helper carries a copy of its parent's `# implements:` tag as
   the first line of its body, so the member sidecar keeps covering the moved code — 1,197
   members became 1,360. `--help` and every printed line are byte-identical. Three findings
   stay, by decision rather than omission: `cmd_check`'s seven parameters (its signature is
   what the suite and the hook call), the `reqs/reqs_dir/root` clump through `mapcmd`'s three
   functions (same reason), and `apply_config` writing `CODE_EXTS` — the config module is the
   one place that is allowed to mutate module state, because that is its job.
4. **`MAP_ENGINE_VERSION` lives in `reqmap_engine/__init__.py`.** Every probe that reads it —
   `_engine_version_at`, `check/engine_staleness.py`, `check_versions.py`,
   `check_engine_bump.py`, `sync_reqmap.sh` — reads the package first and falls back to the
   single-file location, so a consumer seeded before this change is still measured correctly.

## Consequences

- **Seeding copies two things.** `scripts/reqmap.py` and `scripts/reqmap_engine/` travel
  together; the skill's Setup (both variants), `sync_reqmap.sh`, the cross-tool test and the
  `.reqmapignore` that `init` seeds all name both. A consumer that copies only the file gets an
  `ImportError` on its first line, not a subtly older engine — loud, not silent.
- **The plugin major moves to 7**, and `check@v7` with it ([ADR-0029](0029-action-alias-tracks-the-plugin-major.md)):
  the vendoring layout is the consumer-facing contract, and it changed.
- **`import reqmap` still answers for every name.** The regression suite and any embedder that
  read `reqmap._acc_blocks` keep working through a module-level `__getattr__` that looks the
  name up across the package. A test that *patches* a name must patch the module that looks it
  up (`R.git._git`, not `R._git`) — the ordinary Python rule, which the single file had hidden.
  Eleven test sites changed for that reason and five for writing a tunable (`R.config.X`).
- **A refactor now changes member hashes, not contracts.** The function-level pass touched
  bodies in 30 modules; `_reqlock.json` did not change by a byte, `_memberlock.json` did, and
  `sync` re-baselined it. That is the split the two sidecars exist to make.
- **The relocation cost is paid and will not recur** — until the next re-homing. A module
  boundary redrawn later moves `loc`s again; ADR-0033's definition-anchored `loc` is what would
  make that free, and it is still the right fix if boundaries start moving.
- No line-count gate is added; ADR-0014's reasoning against one was about the gate, not the
  split, and it still holds.

## Revisit when

- A module crosses **1,500 lines**, or two modules need each other at import time — the bus has
  started to fold back into a tangle, and the boundary should be re-drawn rather than patched
  with a second call-time import.
- A consumer reports a vendored engine whose `reqmap.py` and `reqmap_engine/` are at different
  versions. Then the two need a shared stamp the gate checks, which this record deliberately
  did not add.
- Module boundaries move a second time. Then make `loc` definition-anchored first, per
  ADR-0033, so the third move is free.
