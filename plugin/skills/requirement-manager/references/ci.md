# Wiring the gate in GitHub Actions

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

**GitHub Actions** (enforces the gate for the whole team) — use the published
action, pinned to the plugin's major (`@v8`):

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
      - uses: alxmax/requirement-manager/check@v8
        # with:
        #   reqmap-path: scripts/reqmap.py   # where you vendored the engine
        #   working-directory: .             # where requirements/ lives
        #   freshness: 'true'                # also run `map --check` (default; set 'false' to skip)
        #   lint: 'true'                     # also run `lint --strict` (default; needs engine >= 2.3.4)
        #   reqmap-repo: owner/name          # only if your committed map targets a different slug
```

`warn_if_stale` (the vendored-copy staleness notice) is gated on `CLAUDE_PLUGIN_ROOT`,
unset in CI — so it is silent and exit-neutral there by design. The action runs the
gate **and** `map --check` (map freshness) **and** `lint --strict` by default. The lint step
runs the consumer's own vendored engine, so it needs `reqmap.py` from plugin v2.3.4 or newer
(the release that added the `lint_exempt:` escape hatch); pass `lint: 'false'` to skip it.
If you prefer not to depend on
the action, run the engine directly instead of the `uses:` line:
```yaml
      - run: python -X utf8 scripts/reqmap.py gate
      - run: python -X utf8 scripts/reqmap.py gate
      - run: python -X utf8 scripts/reqmap.py gate
```

The hook and the CI job are independent — wire both so the gate runs locally
before push *and* on the remote for PRs.
