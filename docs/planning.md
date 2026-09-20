# Planning and releasing

[← back to the README](../README.md)


The plan says which version the work goes out in, `CHANGELOG.md` says what shipped, and a
version file says what the repository is. The engine reads all three as `vX.Y.Z`
([ADR-0040](adr/0040-a-release-is-cut-from-the-plan.md)):

- **The version** is read from `package.json`, `pyproject.toml`, `Cargo.toml`,
  `.claude-plugin/plugin.json` or `VERSION` — or from the files `VERSION_FILES` names in
  `requirements/_config.json`.
- **The CHANGELOG** is read in the common heading forms — `## [1.2.0] - 2026-09-16`,
  `## v1.2.0 - 2026-09-16`, `## 1.2.0 (2026-09-16)` — and a new entry is written in the form
  the file already uses.

`sync` then says, without writing anything:

- a milestone planned at or below the version already declared — the plan describes the past;
- version files, the newest CHANGELOG entry and the newest tag that disagree;
- a bar whose requirement is done on a different day than the bar's `end` — the date of the
  last commit to that requirement's code — or a bar past its `end` whose requirement is not;
- `Now` / `Next` items in `ROADMAP.md` that no bar schedules.

**Cutting a release.** `sync --release` takes the lowest milestone planned above the
declared version and shows what it would do. `sync --release --apply` does it: bumps every
version file (only the version text changes), writes the dated CHANGELOG entry headed by
the milestone's label with one bullet per bar planned on it — under `## [Unreleased]` when
the file has one, so what you collected there becomes the notes — removes the milestone and
its bars from `_planning.json`, and names the `ROADMAP.md` items to tick by hand.

**Tagging stays in CI.** On a GitHub repo `init` writes `.github/workflows/reqmap-release.yml`:
on every push to the default branch it reads `sync --release --json` and, only when the
declared version has no tag yet, creates the tag and a GitHub release whose notes are that
version's CHANGELOG entry. Commit the release, push, and the tag follows.

## The `TODO.md` format, and the note under a plan

**`TODO.md` format** — still read wherever a consumer keeps one; this repo retired its own
to [`docs/history/TODO-archive.md`](history/TODO-archive.md) on 2026-09-14 and plans in
`ROADMAP.md` instead. Group items under `## vX.Y` milestone headings; each item is
a checkbox with an optional `| lane: <label>` suffix. The lane is parsed and carried into
`_map.json`, but the Roadmap tab renders one lane, `Implementations`, so it no longer
splits the chart. Completed items (`[x]`) are hidden in the chart.

```markdown
## v1.14
- [ ] Promote-todo command    | lane: feature
- [ ] Milestone id rejected on Windows paths | lane: bug
```

Open items appear in their version's column on the Roadmap tab's Versions view.

**The plan, and the note under it.** `init` seeds a `ROADMAP.md` and a
`requirements/_planning.json` on a fresh repo, because a plan file a repo does not have
is a plan nobody writes. The first holds horizons — `Now` / `Next` / `Later`, an item
per line with `| req: ID`; **the lines you indent under an item are its note**, and the
Plan shows them when that item's bar is selected. The second holds the bars, the lanes
and the release cadence — weekly on Friday unless you say otherwise with `every` and `on`.
While nothing in it has a date, its calendar runs to the end of the year, or three months
out, whichever is later; once bars exist it ends at the last of them, and `until` pins it.
A repo that has scheduled nothing still gets the calendar, which is the point: that is the
repo with planning to do. Name milestones in full, `vX.Y.Z`, the form tags and CHANGELOG
headings use.
