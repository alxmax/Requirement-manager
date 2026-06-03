# Changelog

## engine `1.8.0` — 2026-06-03

- **Added**: `extract`/`init` now discover prose capabilities (`.md`/`.html`) by
  default, classified by `classify_prose` into three buckets — ignore
  (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), and
  capability-source (prompts/specs). Capability-source prose is auto-drafted as a
  `draft` stub from its title + `##` headings (`_prose_facts`). An advisory
  doc-sync step is emitted in the skill for sync-only docs tagged `generated-from`.
- **Behavior change**: on first post-upgrade `init`/`extract`, repos with
  prompt/spec markdown will see new `draft` requirements. Drafts are NOT enforced
  by the gate (`draft` is not in `ENFORCED`), so this cannot break an existing
  `check`. Review, edit, and `promote` the real ones; delete the rest.
  README/docs/HTML and meta files (`CLAUDE.md`, `SKILL.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE*`) are never auto-drafted.

## engine `1.5.0` — 2026-06-03

- **`reqmap.py promote <ID>`** — one-command human-validation step: flips a reviewed
  requirement's `status` to `confirmed` via a single frontmatter edit (preserves
  indentation + trailing comment, body untouched). Refuses when the requirement has
  no `implements:` member (a confirmed requirement must point to code, else the gate
  errors); warns when no `tested-by:` is linked; idempotent on an already-confirmed
  requirement. Dogfooded as `REQ-PROMOTE-011`.
- **owner standardized** to `Alex` across the repo's own requirements + the scaffold
  default (`extract` still emits `owner: auto` for machine-drafted, unreviewed files).

## engine `1.4.0` — 2026-06-03

Drift gates to prevent the version/map skew that slipped past in 1.3.x.

- **`reqmap.py map --check`** — freshness gate: regenerates the map in memory and
  compares it to the committed `_map.html`/`_map.md` (ignoring the volatile
  `generated:` timestamp), exiting non-zero if stale. A map that was never generated
  passes (consumers who don't track maps are unaffected). Wired into the shared
  pre-commit hook and CI so a code/requirement edit that shifts the map can't be
  committed without regenerating it.
- **`check_versions.py --fix`** — propagates `plugin.json`'s version into every
  `marketplace.json` occurrence, so a bump is one edit + one command instead of three
  hand-edits (the exact drift that failed CI in 1.3.0).
- **dev pre-commit hook** (`.githooks/pre-commit`, enable with
  `git config core.hooksPath .githooks`) — runs version coherence + the drift gate +
  map freshness locally, before CI.

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
- **map risk signals** — two new signals surface on the Risk tab + `_map.md` table +
  detail panel: `untested` (a requirement with an `implements` member but no
  `tested-by`), suppressible per-requirement with a `test_exempt: <reason>` frontmatter
  field; and `unverified-intent` (a requirement with an open `## WHAT — Verify intent`
  item). Both reuse the existing risk machinery.
- **map zoom-fit fix** — diagrams now fit their container on first open *and* on every
  tab switch. Fit is measured after layout (double `requestAnimationFrame`, zero-size
  guard) and centered, with a capped modest upscale (`FIT_MAX`) so small diagrams fill
  the pane without over/under-zooming.

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
