# requirement-manager

A capability registry that sits between intent and code. Each capability is one
markdown file (the single source of truth); code points back to it with a tag; a
small stdlib-only script reconciles the two and generates a navigable map.

It is packaged as a [Claude Code plugin](.claude-plugin/plugin.json) exposing the
[`requirement-manager` skill](skills/requirement-manager/SKILL.md) — useful on any
project that needs a single source of truth for requirements, especially with
multiple agents or vibe coding, to prevent drift between code, docs and intent.

## Install (as a plugin)

This repo is also a plugin marketplace. Add it and install:

```
/plugin marketplace add alxmax/requirement-manager
/plugin install requirement-manager@requirement-manager
```

Then invoke the `requirement-manager` skill in any repo; on first use it seeds
`scripts/reqmap.py` + `templates/requirement.md` into that repo (see the skill's
Setup section).

## Meta-model

```
                 Acceptance ──verifies──┐
                                        ▼
   Input ──feeds──►  Requirement  ──produces──►  Output
                   (.md + frontmatter) ──generated in──►  Map (HTML)
                        ▲   ▲
              implements│   │allocated to
                        │   │
                     Code (member)
```

Requirement is the center; everything else points at it. Code declares membership
with a tag (`implements:` / `generated-from:` / `validated-against:` / `tested-by:`),
and the member list is discovered by scanning code — never hand-maintained.

## Layout

```
.claude-plugin/marketplace.json    marketplace manifest (this repo is a marketplace)
.claude-plugin/plugin.json         plugin manifest
skills/requirement-manager/SKILL.md  the skill contract (read this first)
scripts/reqmap.py                  the engine (stdlib only)
templates/requirement.md           the per-capability template
requirements/*.md                  the source of truth (one file per capability)
requirements/_reqlock.json         the drift baseline (committed)
```

## Commands

```bash
python scripts/reqmap.py new AREA-NAME-NNN   # scaffold a requirement
python scripts/reqmap.py scan              # list code members per capability
python scripts/reqmap.py check             # the gate: link sync + drift (pre-commit/CI)
python scripts/reqmap.py map               # generate requirements/_map.html + _map.md
python scripts/reqmap.py extract           # draft requirements from legacy code
```

## Dogfooded

This repo applies the skill to itself: `requirements/` describes `reqmap.py`'s own
capabilities (3 `bus` + 5 `feature`), and `python scripts/reqmap.py check` passes
with zero errors. See [SKILL.md](skills/requirement-manager/SKILL.md) for the full
model and authoring rules.
