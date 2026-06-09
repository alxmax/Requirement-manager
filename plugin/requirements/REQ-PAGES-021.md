---
id: REQ-PAGES-021
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-MAP-007]
satisfies: [NEED-SSOT-001]
superseded_by:
milestone: v1.04
---

# Publish & gate the GitHub Pages map copy

> The map viewer is most useful when it is published — a URL anyone can open, no
> checkout required. This capability copies the freshly-built viewer into a repo's
> GitHub Pages folder and then guards that published copy, so the page people actually
> read can never quietly fall behind the registry it claims to show.

## WHAT — Contract (normative)
- When `_map.html` is generated AND a `docs/` directory at the git root carries a GitHub
  Pages signal (a `.nojekyll` or `index.html` file present), `map` shall also copy `_map.html`
  to `docs/map.html`. When no signal is present, or git is absent, `docs/map.html` is not
  written — the behaviour is opt-in by folder contents, so a repo that does not publish a
  page is unaffected.
- `map --check` (the no-write freshness gate) shall additionally flag `docs/map.html` as stale
  when it differs from a fresh viewer render of the current registry. This applies only when
  the Pages signal and the viewer template `_map_viewer.html` are both present and
  `docs/map.html` already exists. A copy that was never generated is not stale (the same
  absent-file rule the gate applies to `_map.*`).
- The freshness comparison shall read the on-disk copy as text so a platform newline
  difference (CRLF vs LF) never raises a false positive. It shall exclude the git-derived
  `repo` field (as the `_map.json` check does), so a fork or clone with a different remote
  is not spuriously flagged; the rest of the injected data carries no wall-clock value, so
  the comparison is deterministic.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The Pages signal is detected at the git root (so the engine running from a sub-directory
  such as `plugin/` still finds a project-root `docs/`); it falls back to the engine's own
  root when git is absent or the tree is not a checkout.
- This depends on REQ-MAP-007: the published copy and its freshness check both operate on the
  `_map.html` that the map capability renders. It adds no new rendering — only publish + gate.

## HOW — Acceptance (= tests)
- When `docs/` at the git root has `.nojekyll` or `index.html`, `map` also writes `docs/map.html`
  (same content as `_map.html`); when the signal is absent, `docs/map.html` is not written.
- When `docs/` has no Pages signal (or git is absent), `map` still succeeds and writes only the
  standard outputs.
- After `map`, `map --check` exits 0; if `docs/map.html` is then edited to differ from a fresh
  render, `map --check` exits non-zero and names `map.html`.
- When the Pages signal is present but `docs/map.html` does not exist (never generated, or
  removed), `map --check` does not flag it stale.
- A change to only the git-derived `repo` value inside `docs/map.html` leaves `map --check` fresh
  (the field is excluded from the diff).

## WHERE — Current implementation
- `_docs_publish_path` (Pages-signal resolution) and the `docs/map.html` branches of `cmd_map`
  (publish copy) and `_map_check` (freshness gate) in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
