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
        #   freshness: 'true'                # check committed map freshness (default; set 'false' to skip)
        #   lint: 'true'                     # check requirement readability (default; needs engine >= 2.3.4)
        #   reqmap-repo: owner/name          # only if your committed map targets a different slug
```

The action runs the consumer's read-only `gate`, which includes map freshness and
readability by default. Its `freshness` and `lint` inputs control those stages.
Use `--full` when advisory findings should also be printed. A plain workflow step is:

```yaml
      - run: python -X utf8 scripts/reqmap.py gate --full
```

Wire both a local pre-commit hook and CI so the gate checks changes in both places.
