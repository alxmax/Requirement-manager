# Changelog

## engine `1.3.0` — 2026-06-03

Non-code capability discovery + corpus-health visibility (`MAP_ENGINE_VERSION` 2026-06-03).

- **`candidates --md-glob`** — discover capabilities in authoritative **non-code** files
  (prompt/spec markdown), advisory-only and allowlist-bounded. Off unless a glob is
  given; writes no `.md`. A new `_md_facts()` extractor pulls the H1 title, the first
  blockquote after it (intent), and `## ` H2 headings (no parser). The plan now carries
  `coverage_summary {total_candidates, with_existing_req}` and a `lineage_note` so an
  unfilled plan can't masquerade as coverage, and so a `generated-from`/`implements`
  tag is understood as authoring lineage — not auto-tracking of later source edits.
- **`.md` added to the scan extensions** so prose capabilities can carry membership
  tags (`<!-- implements: ID -->`). The drift hash still anchors only on the authored
  Contract+Acceptance, so source prose may drift freely.
- **`check` health line** — the summary now reports `(N confirmed, M legacy-schema)`,
  and legacy-schema requirements (no `## WHAT — Verify intent` section, for which
  `findings` is silently inactive) are flagged with a non-blocking WARN. Makes an
  all-baseline corpus (gate enforces nothing yet) and an inactive `findings` visible.
- **`extract`** now annotates the emitted `risk:` field as an author triage hint that
  the engine does not read.

## check action `v1.0.0` — 2026-06-03

First published release of the `requirement-manager` CI action. Run the drift gate
on every push and PR without copying YAML boilerplate into each repo.

### Usage
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

### Inputs (optional)
| input | default | purpose |
|---|---|---|
| `reqmap-path` | `scripts/reqmap.py` | path to your vendored engine, relative to `working-directory` |
| `working-directory` | `.` | directory the gate runs from (where `requirements/` lives) |
| `python-version` | `3.x` | Python to set up (engine is stdlib-only — any 3.x works) |

### What it enforces
`reqmap.py check` — link sync (every code tag points to a real requirement; every
confirmed requirement has ≥1 member), content drift vs. the lock, and `depends_on`
target existence. Fails the build on any violation.

### Notes
- **Versioning:** pin to `@v1` (moves with backward-compatible fixes) or to `@v1.0.0`
  / a commit SHA for exact reproducibility. The action ref is independent of the
  plugin/PyPI semver.
- **Scope:** the vendored-copy staleness notice (`warn_if_stale`) is gated on
  `CLAUDE_PLUGIN_ROOT`, unset in CI — silent and exit-neutral there by design.
- **Security:** keep `permissions: contents: read` in the caller workflow; the gate
  needs no secrets and no write scope.
