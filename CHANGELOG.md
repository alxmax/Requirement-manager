# Changelog

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
