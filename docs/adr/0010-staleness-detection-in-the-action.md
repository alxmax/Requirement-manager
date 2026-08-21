# ADR-0010 — Staleness detection lives in the action, not the engine

- **Status:** Accepted
- **Decided:** 2026-08-20 (`REQ-STALEENGINE-043`)
- **Evidence:** `CHANGELOG.md` `v2.22.0`; `check/engine_staleness.py`

## Context

[ADR-0001](0001-single-file-stdlib-engine.md) buys hermetic adoption by having each repo
vendor its own copy of the engine. The bill arrives later: that copy only improves when
somebody re-seeds it, and nothing makes them.

The engine has always had a staleness notice, `warn_if_stale`, but it fires only when
`CLAUDE_PLUGIN_ROOT` is set — inside a Claude Code session and nowhere else. CI, the one
surface that runs on every push, was silent by construction. The cost is invisible and
specific: checks that shipped after the vendored copy simply do not run, and the build stays
green while covering less than the caller thinks.

The obvious fix — teach the engine to detect staleness in CI too — cannot work. **A stale
`reqmap.py` does not contain the check that would report it stale.** Any detector shipped in
the engine reaches only the repos that are already current.

## Decision

Put the detector in the published GitHub Action, which the consumer does **not** vendor and
which is always current for whatever `@vN` they reference. `check/engine_staleness.py` reads
`MAP_ENGINE_VERSION` from the vendored engine and from the engine in the action's own checkout,
and emits a `::warning::` annotation when the vendored one is older.

`stale-engine` selects `warn` (default), `error`, or `off`.

## Consequences

- The signal reaches exactly the repos that need it: the ones that pinned once and never came
  back.
- Default `warn`, and the *step* — not just the script — is built so it cannot fail in warn
  mode: an unreadable version, an unexpected exception, a probe that is not where it should be,
  all print a skipped-probe note and exit 0. That property is what let this ship on `@v2`
  instead of forcing a major that would have stranded its own audience
  ([ADR-0006](0006-three-version-axes.md)).
- The comparison is against the ref the caller pinned, so an exact-SHA pin is measured against
  that SHA's engine — the engine they asked for.
- The probe never runs in this repo's own CI, since this repo *is* the engine. Its test suite is
  the only thing exercising it before it ships, which makes that suite load-bearing rather than
  incidental.
- A consumer who runs the gate without the action still gets nothing. That gap is open.

## Revisit when

Consumers report the warning as noise (then `off` becomes the default), or the opposite — a
stale engine causes a real escape and `error` becomes the default. Either way the evidence
comes from consumers, not from here.
