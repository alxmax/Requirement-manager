---
id: ARCH-MAPSTAMP-079
status: draft
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-VIEWER-007]
satisfies: [SYS-VISUAL-106]
---

# A map says which build it is and how it opens

## Description
> `_map.html` is regenerated and gitignored, so a second checkout can hold an old one that
> looks like a missing feature. And a repository written in another language opened every map
> in English. See [ADR-0081](../../docs/adr/0081-what-a-first-bug-list-changed.md).

Every bullet below is binding.
- The page shows the engine version, the branch and the time it was written. [[REQ-MAPSTAMP-1124]]
- `MAP_LANGUAGE` sets the language the page opens in. [[REQ-MAPSTAMP-1125]]

## Cases
CASE-1 — an old map can be told from a new one
  Given  a repository on a named branch
  When   `sync` writes `_map.html`
  Then   the page carries the engine version, that branch and the time

--------------------


---
id: REQ-MAPSTAMP-1124
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPSTAMP-079]
---

# The page shows which build it is

## Description
> The clock and the branch stay out of `_map.json`: that file is committed, and either would
> rewrite a line on every run. `_map.html` is gitignored, so it can carry both.

Every bullet below is binding.
- `_map.html` carries `generated_at` and, when git can answer, `branch`. `_map.json` carries neither.
- The rail's footer shows the engine version, the branch and the time, leaving out what the map does not carry.

## Cases
CASE-1 — the page carries the stamp
  Given  a repository on the branch `side`
  When   `sync` runs
  Then   `_map.html` holds that branch, a time and the engine version

CASE-2 — the committed map stays quiet
  Given  the same repository
  When   `sync` runs
  Then   `_map.json` has no `generated_at` and no `branch`

CASE-3 — the footer shows what it was given
  Given  a map with an engine version and a branch, and one with neither
  When   the rail renders
  Then   the first footer shows both, and the second shows no stamp

--------------------


---
id: REQ-MAPSTAMP-1125
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPSTAMP-079]
---

# `MAP_LANGUAGE` sets the language the page opens in

## Description
> A reader's own choice beats a repository's default, so the choice is remembered only when a
> reader makes one. Remembering every first open would freeze the default for that browser.

Every bullet below is binding.
- `MAP_LANGUAGE` in `_config.json` is `en` or `ro`, and any other value is reported and ignored. `_map.json` carries `language` only when it is not `en`.
- The page opens in that language unless the reader has chosen one.
- The language is stored when the reader changes it, not when the page opens.
- The retired key `LANGUAGE` stays ignored.

## Cases
CASE-1 — the language reaches the map
  Given  `MAP_LANGUAGE` set to `ro`
  When   `sync` runs
  Then   `_map.json` carries `language: ro`

CASE-2 — the default adds no key
  Given  no `MAP_LANGUAGE`
  When   `sync` runs
  Then   `_map.json` has no `language`

CASE-3 — another value is reported
  Given  `MAP_LANGUAGE` set to `fr`
  When   `sync` runs
  Then   stderr names the key and `_map.json` has no `language`

CASE-4 — the page opens in the map's language and remembers nothing
  Given  a map with `language: ro` and no stored choice
  When   the page renders
  Then   its labels are Romanian, and storage is written only after the reader changes language
