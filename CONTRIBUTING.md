# Contributing

This repo is a Claude Code plugin whose payload is a single stdlib-only Python file,
`plugin/scripts/reqmap.py`, plus three skills and a published GitHub Action. It dogfoods
itself: `plugin/requirements/` describes the engine's own capabilities, and the same gate
consumers run is what guards this repo's commits.

Two rules explain most of what follows:

1. **A behaviour change ships with the requirement that describes it.** Code that does
   something no requirement claims is exactly the drift this tool exists to catch.
2. **No dependencies.** The engine is stdlib-only so it can be dropped into any repo
   without an install step. A PR that adds an import outside the standard library will be
   turned down regardless of merit.

## Setup

Python 3.9 or newer (the declared floor, `MIN_PYTHON` in `reqmap.py` — it is the oldest
version CI actually runs, not the oldest the code tolerates). Nothing to install.

```bash
git clone https://github.com/alxmax/Requirement-manager
cd Requirement-manager
git config core.hooksPath .githooks     # once: runs the CI checks before each commit
```

`.githooks/pre-commit` mirrors the CI order, and `.githooks/pre-push` blocks a direct push
to `main`. Both are this repo's own dev hooks — do not confuse them with
`plugin/hooks/pre-commit`, which is shipped to consumer repos, so editing it changes their
behaviour and needs a version bump.

Node is needed only to rebuild the viewer under `app/` (see `app/CLAUDE.md`); the engine
never touches it.

## The loop

All engine commands run from `plugin/`. The `--code ..` is not optional for these — it
widens the scan to the repo root, which is what the committed artifacts were generated
from:

```bash
cd plugin
python -X utf8 scripts/reqmap.py gate --code ..          # link sync + drift + test links
python -X utf8 scripts/reqmap.py lint --strict --code ..  # requirement readability
python -X utf8 scripts/reqmap.py sync --code ..           # rescan + advance lock + regen map
python -X utf8 scripts/reqmap.py map --check --code ..    # committed map still fresh?
```

`gate` must report **0 errors** before you commit. Warnings are informative and do not
block, but a warning your change introduced is yours to explain in the PR.

On Windows, pass `-X utf8` to every Python invocation: the suites print non-ASCII and fail
on cp1252.

## Tests

```bash
python -X utf8 plugin/scripts/test_reqmap.py             # the engine suite (500+)
python -X utf8 scripts/test_check_versions.py            # manifest/version coherence
python -X utf8 scripts/test_engine_staleness.py          # the action's staleness probe
python -X utf8 scripts/test_cross_tool.py                # seeds the engine into a tempdir: sync -> gate -> map
cd scripts && python -X utf8 test_changelog_notes.py     # release-notes extraction
cd plugin/skills/excalidraw-diagram/scripts && python -X utf8 -m unittest test_excalidraw
```

New behaviour needs a test that fails without your change. "Verified by reading the diff"
is not a verification — the whole project is an argument against that.

## Adding or changing a capability

1. Write or edit the requirement in `plugin/requirements/` (copy the shape of a recent one,
   e.g. `REQ-TRACKED-042.md`). Contract clauses are binding and testable; the WHY explains
   intent, not mechanics.
2. Tag the code that implements it:
   ```python
   # implements: REQ-YOURTHING-0NN
   ```
   Member lists are discovered by scanning — never hand-maintained.
3. Point at least one test at it with `# tested-by: REQ-YOURTHING-0NN`.
4. Run `sync --code ..` to advance the lock and regenerate the map, and commit the
   regenerated `_map.*` / `_reqlock.json` / `_memberlock.json` alongside your change.

If your change alters a **confirmed** requirement's contract, `sync --accept-drift` is how
you say so deliberately.

The CLI's command set has one source of truth: the `COMMANDS` registry near the top of
`reqmap.py`. `plugin/tool_definition.json` and the command table in `SKILL.universal.md`
are generated from it by `gen-integration` — never hand-edit those two; the gate fails when
they drift.

## Versions

Two independent numbers, easy to conflate:

- **Plugin semver** lives in three files kept in lockstep (`plugin/.claude-plugin/plugin.json`
  and twice in `.claude-plugin/marketplace.json`). `python scripts/check_versions.py --fix`
  syncs them. **Any** shipped change — engine or skill — needs a bump, or installed copies
  never see it. A bump without a matching `` `vX.Y.Z` `` heading in `CHANGELOG.md` fails CI.
- **`MAP_ENGINE_VERSION`** inside `reqmap.py` (`YYYY-MM-DD[.N]`) is engine-only. Bump it when
  the engine changes, so a seeded copy can tell it is behind.

Tags follow `plugin.json`: the `release` job cuts `vX.Y.Z` from it on pushes to `main`.
Do not push tags by hand.

## Pull requests

- Branch from `main`; direct pushes to `main` are blocked.
- Keep the change surgical. Refactors bundled into a feature PR make both harder to judge.
- CI must be green: `gate-and-tests`, the 3.9/3.12/3.13 x ubuntu/windows matrix, and the
  `artifacts` job that re-derives the committed viewer and diagram builds byte-for-byte.
- Explain *why* in the PR body. This repo's history is its design record — several
  decisions are documented mainly as the reasoning attached to the change that made them.

## Licensing

The project is under the Business Source License 1.1 (see `LICENSE`) — source-available,
not open source, converting to Apache 2.0 on 2030-06-05. By opening a PR you agree your
contribution ships under those same terms. If that is a blocker for you, say so in an
issue: the licence choice is on the roadmap to revisit, and a real contributor is exactly
the trigger for revisiting it.
