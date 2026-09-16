# ADR-0041 — Two of the engine's four design findings are fixed, two are kept

- **Status:** Accepted. **Supersedes in part** [ADR-0035](0035-the-engine-is-a-package-behind-a-thin-cli.md)'s
  list of accepted design findings: two of its four are fixed in code, two stay accepted for the
  reasons below.
- **Decided:** 2026-09-16, at the maintainer's direction ("take all of these"), after every design
  finding outside the engine had been cleared.
- **Evidence:** `gate --design` on `plugin/scripts` reported four findings; the test
  `DocsAreTrue.test_the_engine_reports_the_documented_design_findings` pins the documented number.

## Context

ADR-0035 split the engine into a package and accepted four findings the split left: `cmd_check`
taking seven parameters, `reqs`/`reqs_dir`/`root` travelling together through three `mapcmd`
functions, `apply_config` writing module state, and `rules.py` holding 32 top-level definitions.
With the viewer's findings cleared, these were the only design findings left in the repository.
Each was re-read to ask whether the finding describes a defect or the design itself.

## Decision

1. **`cmd_check` takes six parameters.** The reason for accepting drift no longer travels beside
   `accept_drift`; `accept_drift` is `True`, `False`, or the reason string `--accept-drift REASON`
   yields. `_drift_acceptance` turns it into `(accepted, reason)` and reads it with `is not False`,
   so `--accept-drift ""` still accepts — the case the old docstring gave for keeping them apart.
   The rule that made them two values is kept; it now lives in one function instead of in every
   caller.
2. **`mapcmd`'s freshness helpers take the workspace.** `_map_check` and `_stale_artifacts` read
   `reqs` and `reqs_dir` from the `Workspace` the caller already holds, which is what the
   workspace object exists for (it replaced the same clump fifteen times in ADR-0035).
3. **`apply_config` keeps writing module state.** Overriding the module constants from
   `_config.json` IS the configuration design: every tunable is read as `cfg.NAME` so an override is
   seen everywhere. The detector flags the one `global` statement; rewriting it as
   `globals()["CODE_EXTS"] = ...` would silence the finding and change nothing. A finding that
   describes the design is recorded, not hidden.
4. **`rules.py` keeps its 32 definitions.** The file is the gate registry (ADR-0026): one
   `@gate_rule` function per check. The threshold measures a module doing too many things; this
   one does exactly one, and splitting it to satisfy a count would scatter the single place a
   reader finds every rule.

## Consequences

- `gate --design` reports two findings on the engine; CLAUDE.md says TWO and the test holds it.
- A caller of `cmd_check` passes a reason as `accept_drift="…"` instead of `drift_reason="…"`.

## Revisit when

- The configuration moves off module constants (an object, or a per-run context), which would
  remove the reason for finding 3; or
- a gate rule needs a helper that is not itself a rule, so `rules.py` starts doing a second thing.
