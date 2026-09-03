---
id: ARCH-PAGES-021
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-MAP-007]
satisfies: [SYS-VISUAL-106]
superseded_by:
milestone: v1.04
---

# Publish & gate the GitHub Pages map copy

## Description
> The map viewer is most useful when it is published — a URL anyone can open, no
> checkout required. This capability copies the freshly-built viewer into a repo's
> GitHub Pages folder and then guards that published copy, so the page people actually
> read can never quietly fall behind the registry it claims to show.
- When `_map.html` is generated AND a `docs/` directory at the git root carries a GitHub
  Pages signal (a `.nojekyll` or `index.html` file present), `map` also copies `_map.html`
  to `docs/map.html`. When no signal is present, or git is absent, `docs/map.html` is not
  written — the behaviour is opt-in by folder contents, so a repo that does not publish a
  page is unaffected.
- `map --check` (the no-write freshness gate) additionally flags `docs/map.html` as stale
  when it differs from a fresh viewer render of the current registry. This applies only when
  the Pages signal and the viewer template `_map_viewer.html` are both present and
  `docs/map.html` already exists. A copy that was never generated is not stale (the same
  absent-file rule the gate applies to `_map.*`).
- The freshness comparison reads the on-disk copy as text so a platform newline
  difference (CRLF vs LF) never raises a false positive. It excludes the git-derived
  `repo` field (as the `_map.json` check does), so a fork or clone with a different remote
  is not spuriously flagged; the rest of the injected data carries no wall-clock value, so
  the comparison is deterministic.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The Pages signal is detected at the git root (so the engine running from a sub-directory
  such as `plugin/` still finds a project-root `docs/`); it falls back to the engine's own
  root when git is absent or the tree is not a checkout.
- This depends on ARCH-MAP-007: the published copy and its freshness check both operate on the
  `_map.html` that the map capability renders. It adds no new rendering — only publish + gate.

## Cases (= tests)
CASE-1
  Given  a `docs/` at the git root carrying `.nojekyll` or `index.html`
  When   `map` runs
  Then   it also writes `docs/map.html` (same content as `_map.html`); absent the signal,
         `docs/map.html` is not written

CASE-2
  Given  no Pages signal in `docs/` (or git absent)
  When   `map` runs
  Then   it still succeeds and writes only the standard outputs

CASE-3
  Given  a completed `map`
  When   `docs/map.html` is edited to differ from a fresh render
  Then   `map --check` exits non-zero and names `map.html` (it exits 0 before the edit)

CASE-4
  Given  the Pages signal present but no `docs/map.html` (never generated, or removed)
  When   `map --check` runs
  Then   it does not flag the file stale

CASE-5
  Given  a change to only the git-derived `repo` value inside `docs/map.html`
  When   `map --check` runs
  Then   it stays fresh (the field is excluded from the diff)

## WHERE — Current implementation
- `_docs_publish_path` (Pages-signal resolution) and the `docs/map.html` branches of `cmd_map`
  (publish copy) and `_map_check` (freshness gate) in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-PAGES-560
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PAGES-021]
superseded_by:
---

# When _map.html is generated AND a docs/ directory

> When `_map.html` is generated AND a `docs/` directory at the git root carries a GitHub
> Pages signal (a `.nojekyll` or `index.html` file present), `map` also copies `_map.html`
> to `docs/map.html`. When no signal is present, or git is absent, `docs/map.html` is not
> written — the behaviour is opt-in by folder contents, so a repo that does not publish a
> page is unaffected.

Scenario: map copies the viewer to docs/map.html only when a Pages signal exists
  Given  a `docs/` directory at the git root containing a `.nojekyll` file
  When   `map` runs and writes `_map.html`
  Then   `docs/map.html` exists with the same bytes; without the signal it is not written

## Members in code (auto)




--------------------


---
id: REQ-PAGES-561
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PAGES-021]
superseded_by:
---

# Map --check (the no-write freshness gate) additionally flags

> `map --check` (the no-write freshness gate) additionally flags `docs/map.html` as stale
> when it differs from a fresh viewer render of the current registry. This applies only
> when the Pages signal and the viewer template `_map_viewer.html` are both present and
> `docs/map.html` already exists. A copy that was never generated is not stale (the same
> absent-file rule the gate applies to `_map.*`).

Scenario: check flags an edited docs/map.html as stale, absent copy as fresh
  Given  a generated `docs/map.html` that is then overwritten with different HTML
  When   `map --check` runs
  Then   it exits 1 naming `map.html`; if the file is missing instead, it exits 0

## Members in code (auto)




--------------------


---
id: REQ-PAGES-562
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PAGES-021]
superseded_by:
---

# The freshness comparison reads the on-disk copy as

> The freshness comparison reads the on-disk copy as text so a platform newline difference
> (CRLF vs LF) never raises a false positive. It excludes the git-derived `repo` field (as
> the `_map.json` check does), so a fork or clone with a different remote is not
> spuriously flagged; the rest of the injected data carries no wall-clock value, so the
> comparison is deterministic.

Scenario: a swapped repo field alone does not mark docs/map.html stale
  Given  a fresh `docs/map.html` whose embedded `"repo"` value is edited to a different slug
  When   `map --check` runs
  Then   it still exits 0 and reports the file fresh

## Members in code (auto)
