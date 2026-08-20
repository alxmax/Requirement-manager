<!-- Delete any section that does not apply. The checklist mirrors what CI enforces —
     ticking a box you did not verify just moves the failure later. -->

## What changed, and why

<!-- The why is the part that survives: this repo's history is its design record. If you
     rejected a simpler approach, one sentence on why is worth more than a diff summary. -->

## Requirement

<!-- The id this implements or changes, e.g. REQ-TRACKED-042. New behaviour ships with the
     requirement that describes it; if this genuinely changes none, say so and why
     (docs-only, CI wiring, a fix inside an existing contract). -->

## Verification

<!-- The commands you ran and what they said — not "tests pass". -->

## Checklist

- [ ] `gate --code ..` reports **0 errors** (and any new warning is explained above)
- [ ] `lint --strict --code ..` is clean, or the new finding has a justified `lint_exempt:`
- [ ] Regenerated artifacts committed: `_map.md`, `_map.json`, `_reqlock.json`, `_memberlock.json`
- [ ] Tests added for the new behaviour, and the relevant suites pass locally with `-X utf8`
- [ ] Anything under `plugin/` changed → plugin semver bumped in all three places
      (`scripts/check_versions.py --fix`) **and** a matching `` `vX.Y.Z` `` CHANGELOG entry
- [ ] Engine changed → `MAP_ENGINE_VERSION` bumped
- [ ] No new third-party dependency (the engine is stdlib-only, deliberately)
