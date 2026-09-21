# Releasing a new version, and brownfield repos

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

Before merging a feature branch, bump the semver **on that branch** so the version commit is part of the merge. Do not bump after merge.

1. Update `plugin/.claude-plugin/plugin.json` → `"version": "X.Y.Z"`
2. Update `.claude-plugin/marketplace.json` → `"version": "X.Y.Z"` in all three occurrences (root + plugins array)
3. Run `python scripts/check_versions.py` from repo root — must print `OK semver aligned at 'X.Y.Z'`
4. Mark shipped `TODO.md` items `[x]` so they disappear from the Roadmap tab
5. Commit: `chore: bump version to X.Y.Z`
6. After merge: `git tag vX.Y.Z <merge-sha> && git push origin vX.Y.Z`

**When to bump which digit:**
- **patch** (X.Y.**Z**) — bug fixes, doc corrections, gate/map regen with no new behavior
- **minor** (X.**Y**.0) — new commands, new viewer tabs, new frontmatter fields, new generated outputs
- **major** (**X**.0.0) — breaking changes to the requirement schema, gate behavior, or CLI interface

## Legacy / brownfield (draft mode)

`init` walks the untagged code and proposes `draft` requirements (structure, input/output
from signatures, `depends_on` from imports). It **cannot** recover intent — it only
captures observed behavior, so:
- Everything it emits is `draft`/`baseline`, never `confirmed`. It never canonizes a
  bug as correct.
- Routing to review is by **risk = blast radius × uncertainty × proximity to known
  problems**, not by parsing ease (clean code can be a clean bug). High-risk →
  review; low-risk → accept as `baseline` (tracked, not asserted correct).
- Aim ~80% auto-`baseline` / ~20% human-`confirmed` as a *health signal*, not a quota.
