---
id: ARCH-TRANSLATE-044
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.25
depends_on: [ARCH-PARSE-001, ARCH-MAP-007, ARCH-VIEWER-007]
satisfies: [SYS-SHIP-108]
lint_exempt: [file-spread]
---

# Reading a cached requirement translation into the map

## Description
> `i18n.jsx` (ARCH-VIEWER-007) draws a hard line: the locale toggle translates UI
> chrome only, never requirement content — a requirement's title, intent, contract
> and acceptance criteria stay in the author's language, because they are the
> artifact under review and translating them live would put words in the author's
> mouth. That line held until a corpus is written entirely in one language and a
> reader of the other language cannot use the viewer at all. This capability adds
> the one exception, and only the reading half of it: a translation cache produced
> out of band is inlined into the graph, always rendered with a visible
> "machine-translated, unreviewed" marker, never presented as the authored source.

Every bullet below is binding.
- The engine READS `requirements/_i18n/<locale>.json` and never writes it. No
  subcommand spawns an external process, so `gate`, `sync` and the pre-commit hook
  stay exactly as deterministic and offline as they were before this capability
  existed. [[REQ-TRANSLATE-937]]
- A cached entry is served only while its stored hash still matches the
  requirement's current content; a stale or malformed cache degrades to no
  translation, never to a wrong one. [[REQ-TRANSLATE-938]]
- The gate reports a cached translation that carries a field the requirement
  itself does not emit. [[REQ-TRANSLATE-967]]
- A repository declares its requirements language as `LANGUAGE` (`en`, `ro`, `both`) in `_config.json`. Under `ro` or `both` the engine reports every requirement without a fresh translation, hands over the source text plus cache key on request, has the viewer open in that language — while still translating nothing itself. [[REQ-TRANSLATE-996]]

## Cases
CASE-1 — a title-only edit invalidates the cached translation
  Given  two requirement bodies identical except for the `# ` title line
  When   `translation_hash` runs on each, and `binding_hash` runs on each
  Then   the `translation_hash` values differ while the `binding_hash` values stay
         equal — proof the wider span is necessary

CASE-2 — the map attaches a fresh cache entry without ever calling an external tool
  Given  a `requirements/_i18n/en.json` entry whose hash matches the requirement's
         current content
  When   `_build_map_data` + `_attach_translations` run with `subprocess.run`
         mocked to raise on any call
  Then   the matching node carries `node.i18n.en` and no subprocess was started

CASE-3 — a stale cache entry is dropped, never served
  Given  a cache entry whose stored hash does NOT match the requirement's current
         content, because the source was edited since the cache was produced
  When   `_load_translations` runs
  Then   that entry is absent from the result — never served stale

## Context
**Notes**
- **The `translate` command was removed on 2026-09-05**, at the user's request,
  together with everything that produced the cache: the `claude -p` call, the
  language detection, the corpus-majority vote and the structural-fidelity check.
  What survives is this reading half, which is what puts Romanian into the viewer.
  The consequence is stated plainly rather than hidden: the cache now decays.
  Every requirement edited from here on loses its cached translation, silently and
  by design (CASE-3), and the engine has no way to produce a new one. Refreshing a
  translation is a manual step — ask Claude for it and write the entry into
  `_i18n/<locale>.json` in the shape this contract reads.
- `TRANSLATOR_VERSION` stays folded into the cache key. It is now the only lever
  that invalidates every cached entry at once, which matters more without a
  producer, not less.
- The cache is one aggregate `_i18n/<locale>.json` per locale, not one file per
  requirement — the same shape as `_reqlock.json`/`_memberlock.json`
  (ARCH-DRIFT-003), not a new pattern.
- The reader is deliberately mechanical: it compares a hash and serves or drops.
  It cannot tell a fluent translation from a semantically wrong one. That is
  exactly why the badge exists — cached is not reviewed.
- Decision (2026-08-25), still standing: the language set stays `ro`/`en`. The
  cache is per-locale, so adding a language later is additive.
- `file-spread` is exempted: the three files are the engine side plus the two
  viewer consumers named in WHERE (`i18n.jsx`, `SpecView.jsx`) — one feature, two
  runtimes.
- `ac-count-high` is no longer exempted, and no longer needs to be: the contract
  went from eight criteria to three when the producing half left.

## WHERE
- `plugin/scripts/reqmap.py` — `translation_hash`, `_translation_source_text`,
  `_load_translations`, `_attach_translations`, `_rule_translation_parity`.
- `app/src/lib/i18n.jsx` — `translatedText()` and the badge.
- `app/src/components/SpecView.jsx` — the consumer that renders it.


--------------------


---
id: REQ-TRANSLATE-937
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
---

# The cache key, and the promise that nothing shells out

## Description
> The cache key is deliberately wider than `binding_hash`: a translation covers the
> title too, so a title-only edit must invalidate it even though the same edit would
> not trip drift. And with the producing command gone, the offline promise is no
> longer a policy anyone can break by typing the wrong verb — it is a property of
> the engine.

Every bullet below is binding.
- **No subcommand invokes an external process.** `gate`, `sync`, `new`, `init`,
  `confirm` and `clarify` read and write files only. The `translate` command, which
  was the single exception, was removed on 2026-09-05.
- The cache key is `translation_hash(body, title)` — a hash over title + WHY +
  Contract + Acceptance, distinct from `binding_hash()` (Contract+Acceptance only,
  ARCH-DRIFT-003). A title-only edit also invalidates a cached translation, which
  reusing `binding_hash` would miss.
- `TRANSLATOR_VERSION` is folded into the key, so bumping it invalidates every
  cached entry in one step rather than file by file.

## Cases
CASE-1 — no command spawns an external process
  Given  `subprocess.run` mocked to raise if it is invoked at all
  When   `gate`, `sync` and `map` run
  Then   none of them invoke `subprocess.run`

CASE-2 — a title-only edit invalidates the cached translation
  Given  two bodies identical except for the `# ` title line
  When   `translation_hash` runs on each, and `binding_hash` runs on each
  Then   the `translation_hash` values differ while the `binding_hash` values stay
         equal

CASE-3 — bumping `TRANSLATOR_VERSION` invalidates every cached entry at once
  Given  one requirement body and title, hashed with the shipped
         `TRANSLATOR_VERSION`
  When   `translation_hash` runs again on the same body with `TRANSLATOR_VERSION`
         set to a different value
  Then   the two hashes differ, so one bump retires the whole cache instead of the
         entries having to be invalidated file by file


--------------------


---
id: REQ-TRANSLATE-938
status: confirmed
lint_exempt: [file-spread]
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
---

# Reading the cache: fresh only, and failing open

## Description
> A cache read has two ways to go wrong and only one acceptable answer to both. An
> entry can be out of date, or the file can be unreadable. In either case the
> requirement renders in the author's own language, exactly as it did before this
> capability existed — never a stale translation, never a crash.

Every bullet below is binding.
- `map` and `export` read `requirements/_i18n/*.json` when present and attach
  `node.i18n[locale] = {title, intent, contract, acceptance}` for any node whose
  cached hash still matches its current content.
- **A stale entry is silently dropped, never served.** This is what keeps
  `map --check` deterministic: it only ever reads a file already on disk, and it
  never serves a translation known to be out of date.
- A malformed cache file — unreadable, not JSON, or not an object — yields no
  translations at all rather than an exception. The map still builds.
- The viewer consumes `node.i18n` ONLY through `translatedText()` (`i18n.jsx`),
  which reports `isTranslated` alongside the text. Every caller that renders
  `isTranslated` text renders the "machine-translated, unreviewed" badge next to
  it. Absent a cache entry, content renders in the author's own language exactly as
  before this capability existed.

## Cases
CASE-1 — the map attaches a fresh cache entry without calling anything external
  Given  a `requirements/_i18n/en.json` entry whose hash matches the requirement's
         current content
  When   `_build_map_data` runs with `subprocess.run` mocked to raise on any call
  Then   the node carries `node.i18n.en` and no external call was made

CASE-2 — a stale cache entry is dropped, never served
  Given  a `requirements/_i18n/en.json` entry whose stored hash does not match the
         requirement's current content
  When   `_load_translations` runs
  Then   that entry is absent from the result, so `map`/`export` never attach it to
         the node

CASE-3 — a malformed cache file yields no translations, never an exception
  Given  a `requirements/_i18n/en.json` that holds valid JSON which is not an
         object (a list, say)
  When   `_load_translations` runs
  Then   it returns no translations at all and raises nothing, so the map still
         builds

## Context
**Notes**
- `lint_exempt: file-spread` — the cache is written out of band and read by the
  engine and the viewer, so this contract is the handshake across that boundary.
  Both halves have to be named for the obligation to mean anything.


--------------------


---
id: REQ-TRANSLATE-967
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
---

# A translation may not carry a field the requirement does not

## Description
> `translate` and the map both derive from the same requirement, and each was right about it: the
> map emits no intent when the quote IS the obligation, while the translator was handed the raw
> quote. Nothing compared the two, so a translated document showed a `Why — Intent` section the
> untranslated one hides — on eight requirements, invisible until a corpus carried both features
> at once. Two correct parts, wrong together, is a shape a gate can catch and a test of either
> part alone cannot.

Every bullet below is binding.
- The gate warns when a cached translation carries a field whose source in the requirement is
  empty, naming the requirement, the locale and the field.
- A field the requirement has and the translation does not is never reported: a partial or
  in-progress translation is a normal state, not a defect.
- The check reads the caches already on disk and calls nothing external, so it costs a file read
  and stays as deterministic as the rest of the gate.
- A repository with no translation cache raises nothing at all.

## Cases
CASE-1 — a translated field the requirement does not emit is reported
  Given  a requirement whose quote is its only clause, so the map emits no intent, and a cache
         entry for it carrying an `intent`
  When   `gate` runs
  Then   it warns once, naming that requirement, the locale and `intent`

CASE-2 — a field the translation has not reached yet is not a finding
  Given  a requirement with an intent and a cache entry whose `intent` is empty
  When   `gate` runs
  Then   no warning is raised for it

CASE-3 — a corpus with no cache raises nothing
  Given  a requirements directory with no `_i18n` at all
  When   `gate` runs
  Then   the check contributes no finding


--------------------


---
id: REQ-TRANSLATE-996
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
lint_exempt: [file-spread]
---

# Declaring the requirements language

## Description
> The Romanian layer existed — a cache the map reads, a toggle in the viewer — but nothing
> said whether a repository *wanted* it, so nothing could say it had fallen behind: 67 of
> 246 entries here were missing or stale and no command noticed. A repository that writes
> in English and wants the viewer read in Romanian, or in both, declares that once. The
> engine then knows what is owed. It still translates nothing; it says which entries are
> owed and hands over exactly what to translate and the key to write back.
>
> `lint_exempt: [file-spread]`, for the same reason its parent carries it: the setting is
> declared by the engine and honoured by the viewer, so its members are one engine function
> and the three viewer files that read the value. That is the shape of the feature, not a
> diffuse capability; splitting it would put the declaration and its effect in different
> requirements.

Every bullet below is binding.
- `LANGUAGE` in `requirements/_config.json` accepts exactly `en`, `ro` or `both`; any
  other value is reported and ignored, and the default is `en`.
- `_map.json` carries the setting as a top-level `language` field.
- Under `ro` or `both`, a requirement that is not deprecated and has no `_i18n/ro.json`
  entry whose `hash` equals its current `translation_hash` is a gap; the gap is `missing`
  when there is no entry and `stale` when the entry's hash differs.
- Under `en` there are no gaps, `sync` says nothing about translation, and `gate --i18n`
  says that nothing is expected and how to change that.
- `gate --i18n` lists every gap with its locale, id, reason and title; `--json` emits each
  gap's `title`, `intent`, `contract` and `acceptance` exactly as `translation_hash` was
  computed over them, plus that `hash`, so the writer stores the four translated fields
  under the id with the same key.
- `sync`'s tail names the gap count, the missing/stale split and the `--i18n --json`
  command whenever there is at least one gap.
- The viewer opens in Romanian under `ro` and in English under `en` and `both`, with the
  toggle offered whenever a translation exists; a locale the reader chose earlier is kept
  over the engine's default.

## Cases
CASE-1 — the setting is an enum
  Given  `_config.json` with `"LANGUAGE": "ro"`, then with `"LANGUAGE": "romanian"`
  When   the config is applied
  Then   the first sets `LANGUAGE` to `ro` and the second is reported on stderr and leaves
         it unchanged

CASE-2 — the map carries the setting
  Given  `LANGUAGE` set to `both`
  When   the map data is assembled
  Then   its top-level `language` is `both`

CASE-3 — missing and stale are told apart
  Given  `LANGUAGE` `ro`, one requirement with a fresh `ro` entry, one whose entry's hash
         no longer matches, and one with no entry
  When   the gaps are computed
  Then   exactly two gaps come back, reasons `stale` and `missing`, and the fresh one is absent

CASE-4 — English means nothing is owed
  Given  `LANGUAGE` `en` and a corpus with no translation at all
  When   `gate --i18n` and the `sync` tail run
  Then   no gap is reported and `gate --i18n` says nothing is expected and names the key to
         change

CASE-5 — the JSON hand-off carries the source and the key
  Given  one gap under `ro`
  When   `gate --i18n --json` runs
  Then   the entry carries `id`, `locale`, `reason`, `hash`, `title`, `intent`, `contract`
         and `acceptance`, and writing those four fields under the id with that hash makes
         the next gap computation empty

CASE-6 — the sync tail names the gap
  Given  `LANGUAGE` `ro` and two gaps
  When   the `sync` tail prints
  Then   one line reports 2 with the missing/stale split and names `gate --i18n --json`

CASE-7 — the viewer's default follows the setting, the reader's choice beats it
  Given  the single-file viewer's inlined data with `language` `ro`, then `en`, then `both`
  When   the viewer mounts with no stored locale
  Then   it opens in Romanian, then English, then English; a stored or explicit locale
         is kept regardless
