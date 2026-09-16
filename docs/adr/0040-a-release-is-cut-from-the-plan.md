# ADR-0040 — A release is cut from the plan

- **Status:** Accepted. **Supersedes in part** the "never generation" rung of the ladder in
  `ARCH-ROADMAP-038`'s Notes (n=1 manual upkeep, n=2 read-only signal, never generation),
  and the "no generator" ruling of the Senate run
  `2026-09-14_225939-senate-reqmap-plan-single-source` — for releasing only. Everything
  else in both stands: no roadmap signal is a gate rule, and ROADMAP.md and
  `_planning.json` stay two files.
- **Decided:** 2026-09-16, at the maintainer's direction ("do all seven, in order"),
  after the gap analysis that followed the Senate audit
  `2026-09-16_160109-rm-planning-audit` (MODIFY 9-0).
- **Evidence:** the plan scheduled an already-shipped version three times (v7.4, v7.9,
  v7.19). Each was found by a human rereading the file; the read-only signal
  `REQ-PLANSTALE-1013` now finds the fourth. What it cannot do is prevent it: the bump,
  the CHANGELOG heading and the plan edit are three hand steps that drift apart.

## Context

The engine already knew what was planned (`_planning.json`), what shipped (`CHANGELOG.md`)
and, since `REQ-PLANSTALE-1013`, what version the repository declares. It knew all three
only in this repository's own spellings — a `plugin.json`, a ``## plugin `vX.Y.Z` ``
heading — and it changed none of them. A consumer repo got a plan it could draw and no way
to release from it.

The ladder that ruled out generation was written about the ROADMAP (TODO.md at the time):
generating a roadmap from code invents a plan nobody wrote. A release is the opposite case.
The author already wrote every input — the milestone, its label, the bars scheduled on it —
and the writes are the mechanical consequence of saying "this version shipped".

## Decision

1. **The number comes from the plan.** The next release is the lowest planned milestone
   above the highest version already declared by a version file, a tag or a CHANGELOG
   heading. Not a commit trailer and not a PR label: both are a second place to state
   something the milestone already states, and a second place is how the three drift.
   Naming the version explicitly (`sync --release vX.Y.Z`) is still allowed.
2. **`sync --release` is a mode of the write verb, not a new verb.** The command surface
   stays five (ADR-0037). It prints the plan and writes nothing; `--apply` bumps the version
   files, writes the dated CHANGELOG entry (in the heading form the file already uses,
   under `Unreleased` when it has one) and drops the released milestone and its bars from
   `_planning.json`. It refuses with exit 2 when nothing is planned above the baseline, when
   the named version is not above it, or when the gate reports errors.
3. **Tagging stays in CI.** The engine never pushes or tags. `init` seeds a GitHub workflow
   that reads the declared version back (`sync --release --json`) and creates the tag and
   release once, only when the tag does not exist. It is seeded only for a repo on GitHub,
   only when the engine lives inside the checkout, and never over an existing file.
4. **Version files are probed, then configurable.** `package.json`, `pyproject.toml`,
   `Cargo.toml`, `.claude-plugin/plugin.json` and `VERSION` are read; `VERSION_FILES` in
   `_config.json` replaces the probe. A bump rewrites the version text only, never
   reformatting the file.
5. **Every signal stays read-only.** Version files that disagree, a CHANGELOG behind the
   files, and a tag above them are reported by `sync`, `gate --audit` and `health`. None is
   a gate rule.

## Consequences

- This repository's own release path is unchanged: CI still tags from `plugin.json`, and
  `marketplace.json` is still synced by `scripts/check_versions.py --fix`, which the engine
  does not know about.
- A plan that names no future version gets no release: that is the refusal, and it says
  what to add.
- A shipped milestone leaves the plan. Its record is the CHANGELOG entry the same run wrote,
  which lists the bars that were planned on it.

## Revisit when

- A consumer repo releases more than one package from one checkout (the probe returns
  several files that legitimately disagree), or
- two releases in a row are cut with an explicit version because the plan's milestone was
  wrong — the plan is then not where the number comes from in practice.
