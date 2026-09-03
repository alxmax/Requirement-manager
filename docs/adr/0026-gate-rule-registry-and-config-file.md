# 0026 — The gate is a rule registry; thresholds come from a config file

**Status.** Accepted.

**Date.** 2026-09-04.

**Evidence.** `cmd_check` at 400 lines with ~25 inline checks; three recorded divergence
bugs between commands answering the same question (`_impl_exempt`, [ADR-0015](0015-aggregate-layer-instead-of-implicit-dependency-coverage.md);
`_oversize`, plugin v3.1.0; "never a second signal path" in `next`'s contract). `gate --cache`
measured slower than `gate` (1.9 s vs 1.5 s) because only the members walk was cached.
Every threshold a module constant; one env var (`REQMAP_EXTRA_CODE_EXTS`) the only knob.

## Context

Each divergence bug was fixed the same way: extract the predicate the two commands
disagreed about, make both call it, pin it with a test. That fixes the instance. The class —
"a fact about the corpus computed in more than one place" — kept producing new instances,
because nothing said where such a fact lives.

## Decision

1. **One registry.** `GATE_RULES` holds every gate rule as `Rule(id, severity, strict, fn)`,
   registered with `@gate_rule`. `cmd_check` builds one `GateContext` and runs the list;
   it owns only the lock update, the integration-artifact check and printing. `health`
   reads its link-sync count from the registry (RM001, RM006). New consumers read the
   registry; they do not re-derive.
2. **Permanent codes.** `RMnnn` on every finding, printed after the severity and carried in
   `--json`'s `findings`. A retired rule keeps its number (a consumer may have written it
   in `gate_exempt:`).
3. **Per-requirement exemption by code.** `gate_exempt: [RMnnn]` mirrors `lint_exempt:`.
   Corpus-wide findings (no requirement id) cannot be exempted.
4. **Types, not hierarchies.** `Requirement` and `Finding` are dict subclasses that add
   derived facts as properties; every existing `r["meta"]` keeps working. No inheritance
   tree: the engine is a pipeline (load → scan → rules → render), and a class hierarchy
   would be the spaghetti the registry exists to remove.
5. **`requirements/_config.json`.** The constants in `CONFIG_KEYS` and `extra_code_exts`
   are settable per repo, fail-open, with unknown or mistyped keys reported on stderr.
6. **One walk.** `scan_all` is the only tree walk; `--cache` caches all of its output;
   `scan_members` is a view. `_is_source_repo` guards the one rule about this
   repository's own artifacts.

## Consequences

- Adding a gate check is one decorated function; forgetting `health` or `next` is no longer
  possible for the link-sync facts, and the pattern is there for the rest.
- Gate output lines changed shape (`WARN  RM018 ...`). A consumer grepping the old prefix
  needs one edit; the message text after the code is unchanged.
- Thresholds a consumer tunes in `_config.json` are not visible in the engine's constants;
  `lint` and `next` print what they judge by only implicitly. Revisit if a consumer reports
  a surprising verdict traced to a forgotten config file.

## Revisit when

- A second family of checks (lint's) wants the same registry: fold `lint_requirement`'s
  `findings.append({...})` entries into `Rule`s with `LTnnn` codes then, not before.
- A consumer asks to exempt a corpus-wide finding: decide whether `gate_exempt` grows a
  repo-level home in `_config.json`.
