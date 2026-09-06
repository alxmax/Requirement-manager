# ADR-0034 — One rendered map, built where it is published

- **Status:** accepted, 2026-09-06
- **Supersedes:** the publish/gate clause of `ARCH-PAGES-021` (retired in the same change)
- **Evidence:** this repo at `df81728` — `docs/map.html` 2.1 MB, byte-identical to
  `plugin/requirements/_map.html`, rewritten in **249 commits**; `git log --follow`
- **Revisit if:** a consumer needs the published copy on a host that cannot run a build
  step before serving

## Context

The engine wrote the rendered viewer twice. `requirements/_map.html` is the local
double-click copy — gitignored, regenerable. `docs/map.html` was a byte-identical
duplicate, written whenever `docs/` carried a GitHub Pages signal (`.nojekyll` or
`index.html`), and **committed**.

Committed is where the cost was. The file is 2.1 MB here and every requirement edit
rewrites it, so it appears in 249 commits of this repo's history. A consumer sees the
same thing at their own scale: a multi-hundred-KB blob in the diff of every change to a
requirement.

The second copy also needed a rule to keep it honest. `map --check` compared it against a
fresh render and `RM027` failed the gate when it drifted, with a `_strip_generated` pass
to exclude the git-derived `repo` field so forks did not fail spuriously. That machinery
existed only because a *derived* artifact was being stored rather than built.

And the two files could not disagree about anything. There was no case where the
published copy should differ from the local one — the check was guarding against the copy
being *forgotten*, which is a failure mode created entirely by choosing to commit it.

## Decision

The engine writes **one** rendered viewer: `requirements/_map.html`. It never writes into
`docs/`.

A repository that publishes the map builds it where it publishes it. This repo's
`deploy-map` job copies `_map.html` into `docs/` immediately before uploading the Pages
artifact, so the live page keeps working and is current by construction.

- `_docs_publish_path` is removed, with the copy write and the freshness comparison.
- `docs/map.html` is untracked and gitignored.
- `ARCH-PAGES-021` and `REQ-PAGES-889` are retired through `sync --retire --apply
  --delete`, per [ADR-0027](0027-retiring-a-requirement-supersedes-grow-only.md).
- `ARCH-SITE-026` drops `ARCH-PAGES-021` from `depends_on`. The site page never used the
  map-publish capability for anything but the shared Pages-signal concept.

## Consequences

**Breaking for consumers, so the plugin takes a major.** A repo that relied on `sync`
writing `docs/map.html` will find that file frozen at its last committed content — the
worst shape of failure, because nothing errors. The CHANGELOG entry says so and gives the
three-line CI step that replaces it. Per
[ADR-0029](0029-action-alias-tracks-the-plugin-major.md) the Action alias moves with the
plugin major.

**The freshness rule is not lost, it is unnecessary.** A file built at publish time has
no window in which it can disagree with the registry. What `RM027` policed was the gap
between generating and committing; there is no longer a gap.

**The site's Live Map link degrades on its own.** `_region_markers` emits the nav link
only when `map.html` resolves next to the page (`map_ok`), so a consumer who does not
build a published copy simply gets a site without that link rather than a 404. NAV is
already excluded from the freshness comparison — it embeds the fork-specific repo URL —
so the committed page differing from the published one changes no verdict.

**What we did not do.** A `_config.json` opt-out was considered and rejected: it leaves
the duplicate as the default, so every consumer keeps paying for it and this repo would
have to opt out of its own default. Making the copy conditional on a *separate* signal
rather than the Pages marker was also rejected — it keeps all the machinery to solve a
problem that only exists because the artifact is stored rather than built.
