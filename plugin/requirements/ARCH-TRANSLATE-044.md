---
id: ARCH-TRANSLATE-044
status: confirmed
level: architecture
layer: feature
owner: Alex
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
