# ADR-0081 — What a first bug list changed

- **Status:** Accepted. Extends [ADR-0080](0080-known-bugs-are-listed-by-module.md). Leaves
  [ADR-0047](0047-design-review-site-and-i18n-detector-leave-the-engine.md)'s retirement of `LANGUAGE` as it is.
- **Decided:** 2026-11-02
- **Evidence:** a consumer moved a list kept in its own documents onto `BUG_SOURCES`. The
  counts matched an independent parse, and nine things were missing or surprising.

## Context

ADR-0080 was built from one document shape. Used for real, the list had to leave the map, a
table of fixed bugs with the same columns would have read as open, and one module could fall
into two groups. `LANGUAGE` looked like the answer to an English map over a corpus in another language,
but the key was retired in ADR-0047 and the engine no longer wrote `language` at all, so the
viewer's branch for it could never run. An old `_map.html` in a second checkout looked like a
missing feature, because nothing on the page said how old it was.

## Decision

- **`BUG_SKIP_SECTIONS`, not a status.** A regex on `##` headings, off by default. ADR-0080
  named a `Status` column as the way to close a bug; a repository that keeps a "fixed" table
  needs no field, and a bug still has no status.
- **One module, the first spelling.** Spellings that differ only in case, diacritics or
  punctuation become the one read first, in `load_bugs`, so `ask`, the map and the tab agree
  and the viewer needs no second normaliser. A warning was rejected: `--strict` would fail a
  repository over its own spelling. A row added from the page keeps its spelling until the
  next `sync`.
- **A bug's id stays `<file stem>:<ref>`.** Renaming a file changes its bugs' ids. A prefix
  per source was rejected: an id nothing else refers to does not need a second name.
- **Export is the browser's print.** `Export PDF` lays the filtered list out for paper and
  calls `window.print()`, so there is no dependency and nothing new on the command line.
  `ask --bugs --json` is the twin for scripts, and `--prio` takes a list.
- **`MAP_LANGUAGE`, a new key.** Reviving `LANGUAGE` would give a retired name a narrower
  meaning, and a repository still carrying it would change behaviour without asking. The
  value is only the page's default: a reader's choice wins, and is stored only when made.
- **The stamp lives in `_map.html` only.** The engine version, the branch and the time go in
  the rail's footer. In the committed `_map.json` a clock or a branch name would rewrite a
  line on every run, the conflict `_map.md` already gave up its timestamp to avoid.
- **The vendored engine is not a place to extend.** `sync_reqmap.sh` replaces it whole, as
  designed. `docs/integrations.md` says so; `_config.json` is the way to extend it.

## Consequences

- The branch now reaches the page, so the Gantt's band finally names it, as
  `REQ-PLANBRANCH-1011` intended. That requirement still says `_map.json`, which has never
  carried it, and it is confirmed, so a person has to change the sentence.
- `CORE_LOGICAL_BUDGET` rises for the two keys and the stamp. `bugs.py` stays lazy.
- A locale stored by an older viewer stays stored, so a browser that opened a map before this
  change keeps it until its reader changes language.

## Revisit when

- A bug needs to be closed in a file that has no section for it: then `Status`, as ADR-0080 said.
- Someone links to a bug from outside its file, which would argue for a stable id.
