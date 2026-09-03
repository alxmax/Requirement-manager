---
id: ARCH-TRANSLATE-044
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-MAP-007, ARCH-VIEWER-007]
satisfies: [SYS-SHIP-108]
superseded_by:
milestone:
lint_exempt: [ac-count-high, file-spread]
---

# Opt-in requirement-content translation

## Description
> `i18n.jsx` (ARCH-VIEWER-007) draws a hard line: the locale toggle translates UI
> chrome only, never requirement content — a requirement's title, intent, contract
> and acceptance criteria stay in the author's language, because they are the
> artifact under review and translating them live would put words in the author's
> mouth. That line held until a corpus is written entirely in one language and a
> reader of the other language cannot use the viewer at all. This capability adds
> the one exception: a manual, opt-in command that caches a machine translation per
> requirement, gated by a structural check, always rendered with a visible
> "machine-translated, unreviewed" marker — never presented as the authored source,
> and never reachable from anything that gates a commit or a CI run.
Every bullet below is binding.
- `translate` is reached ONLY by typing `reqmap.py translate` — it is never called
  by `gate`, `sync`, `lint`, `map`, `export`, or the pre-commit hook. It is the
  only subcommand that invokes an external `claude` CLI subprocess.
- `corpus_lang(reqs)` detects the corpus's majority language (`ro` or `en`) by
  classifying each requirement's title+WHY+Contract+Acceptance text: Romanian
  diacritics are a certain signal; below that, whichever of a small RO/EN stopword
  list scores more hits wins. A per-file `lang: ro|en` frontmatter value overrides
  detection for that file.
- `translate [--to ro|en]` translates every requirement whose effective language
  matches the corpus majority into the target locale (default: the other of
  `ro`/`en`), caching results in `requirements/_i18n/<target>.json`, one file per
  target locale, keyed by requirement id.
- The cache key is `translation_hash(body, title)` — a hash over title + WHY +
  Contract + Acceptance, distinct from `binding_hash()` (Contract+Acceptance only,
  ARCH-DRIFT-003): a title-only edit also invalidates a cached translation,
  which reusing `binding_hash` would miss.
- Before a translation is cached, `_translation_preserves_structure()` compares the
  source and translated text's backticked-span multiset, numeric-literal multiset,
  ordered heading/bullet markers, ordered `AC-N` criterion labels, and Gherkin-keyword
  multiset (Given/When/Then). A mismatch skips the entry with a `WARN` and
  writes nothing for it — it never partially caches a corrupted translation.
- The `AC-N` labels and the Gherkin keywords are identifiers, not prose: a test names a
  criterion (`# verifies: <ID>#AC-N`) and the viewer highlights the keywords, so a
  translation that renames either is refused. The prompt states both rules, so a model
  that translates them is answering a question nobody asked.
- A missing/erroring `claude` CLI, a timeout, or a malformed (missing-marker)
  response also skips that entry with a `WARN`. `translate` always exits 0 and
  never aborts the batch on a single entry's failure — it is a report-and-cache
  tool, not a gate.
- A cache hit (stored hash matches current content) is skipped without invoking
  `claude` — cost is proportional to what changed, not to corpus size.
- `map` and `export` read `requirements/_i18n/*.json` (when present) and attach
  `node.i18n[locale] = {title, intent, contract, acceptance}` for any node whose
  cached hash still matches its current content; a stale entry (source edited
  since the last `translate` run) is silently dropped, never served. Neither
  command calls `claude` — this is a file read, so `map --check` stays exactly as
  deterministic and `claude`-free as before this capability existed.
- The viewer consumes `node.i18n` ONLY through `translatedText()` (i18n.jsx),
  which reports `isTranslated` alongside the text. Every caller that renders
  `isTranslated` text renders the "machine-translated, unreviewed" badge next to
  it. Absent a cache entry, content renders in the author's own language exactly
  as before this capability existed.

## Verify intent (open questions for the human)
- None — both open questions answered 2026-08-25; the decisions are recorded in Notes.

## Notes & known limitations (informative)
- One `claude -p` call per requirement, not four — the prompt asks for all four
  fields back in one marker-delimited response (`_TRANSLATE_MARKERS`), which is
  what keeps a cold-cache run at N calls instead of 4N.
- `TRANSLATOR_VERSION` is folded into the cache key so bumping the prompt or the
  target model invalidates every cached entry in one step, without hand-editing
  the cache file.
- The structural-fidelity check is deliberately mechanical (backticks, numbers,
  line-leading markers) — it catches a translation that drops or mangles
  identifiers/numbers/structure, not one that is fluent but semantically wrong.
  That is exactly why the badge exists: fidelity-checked is not human-reviewed.
- `translate` writes one aggregate `_i18n/<locale>.json`, not one file per
  requirement — same shape as the existing `_reqlock.json`/`_memberlock.json`
  per-id lock-file convention (ARCH-DRIFT-003), not a new pattern.
- Decision (2026-08-25): the stopword lists stay small. They feed a majority vote
  across a whole corpus, not sentence-level precision, and a per-file `lang:` value
  overrides a misclassification. Grow them only when a real corpus is misclassified —
  and add that corpus as a test case when it happens.
- Decision (2026-08-25): the language set stays `ro`/`en` until a second real consumer
  language shapes the API. The cache is already per-locale (`_i18n/<locale>.json`), so
  adding a language later is additive; what a third language needs is its own detection
  signal (a stopword list) and a name in the prompt, and guessing those without a user
  would fix the wrong shape.
- `file-spread` is exempted: the three files are the engine side plus the two viewer
  consumers named in WHERE (`i18n.jsx`, `SpecView.jsx`) — one feature, two runtimes.
- `ac-count-high` is exempted: each of the eight criteria pins exactly one
  module's behavior (detection, hashing, fidelity check, two fail-open paths,
  caching, and two map-read paths). Merging them to reach the ceiling would test
  several behaviors implicitly per AC — same reasoning as ARCH-LINTCHECKS-025.

## Cases (= tests)
CASE-1
  Given  Romanian text with diacritics, English text, and a code-only string
  When   `detect_lang` runs on each
  Then   it returns `ro`, `en`, and `None` respectively

CASE-2
  Given  a corpus of 2 Romanian requirements and 1 English requirement
  When   `corpus_lang` runs
  Then   it returns `ro` (majority); a `lang: en` frontmatter override on a
         Romanian-text file flips that file's effective language to `en`

CASE-3
  Given  two requirement bodies identical except for the `# ` title line
  When   `translation_hash` runs on each
  Then   the hashes differ, while `binding_hash` (Contract+Acceptance only) on
         the same two bodies stays equal — proof the wider span is necessary

CASE-4
  Given  a translated string that drops a backticked identifier or a number
         present in the source
  When   `_translation_preserves_structure` compares them
  Then   it returns false; an unrelated wording change with the same
         backticks/numbers/markers returns true

CASE-5
  Given  `subprocess.run` raises (the `claude` CLI is absent)
  When   `cmd_translate` runs
  Then   it prints a WARN naming the requirement, writes no cache file, and
         exits 0

CASE-6
  Given  a mocked `claude -p` call returning a well-formed four-marker response
  When   `cmd_translate` runs once, then runs again with the source unchanged
  Then   the first run writes a cache entry and calls the CLI once; the second
         run is a cache hit and does not call the CLI at all

CASE-7
  Given  a `requirements/_i18n/en.json` cache file with an entry whose hash
         matches a requirement's current content
  When   `_build_map_data` + `_attach_translations` run with `subprocess.run`
         mocked to raise on any call
  Then   the matching node carries `node.i18n.en` and no `claude` call was made

CASE-8
  Given  a cache entry whose stored hash does NOT match the requirement's
         current content (source edited since the last `translate` run)
  When   `_load_translations` runs
  Then   that entry is absent from the result — never served stale

CASE-9
  Given  a translation that renames a criterion label (`CASE-1` to `CA-1`) or
         translates a Gherkin keyword (`Given` to `Dat fiind`)
  When   `_translation_preserves_structure` compares it with the source
  Then   it returns false; the same text with labels and keywords intact and
         only the prose translated returns true

## Example — in practice (optional, non-binding)
- A consumer repo's corpus is 68 Romanian-authored requirements. An English-only
  reviewer opens the viewer, switches locale to EN, and the Contract sections
  render in English with a small amber "machine-translated, unreviewed" badge
  next to each — legible, but visibly not the artifact of record. The maintainer
  runs `reqmap.py translate` once after a batch of edits; only the edited
  requirements' cache entries change.

## WHERE — Current implementation
- Engine: `detect_lang`, `corpus_lang`, `translation_hash`, `_structural_signature`,
  `_run_claude_translate`, `cmd_translate`, `_load_translations`,
  `_attach_translations` in `reqmap.py`; wired into `cmd_map`/`cmd_export` (read
  path) and the CLI dispatcher (`translate` command, `--to` flag).
- Viewer: `translatedText()` in `app/src/lib/i18n.jsx`; consumed by `SpecDoc` in
  `app/src/views/SpecView.jsx` (title, intent, contract, acceptance + badge);
  `adaptNode()` in `app/src/lib/loadData.js` forwards `node.i18n` from the engine
  export.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-765
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# Translate is reached ONLY by typing reqmap.py translate

> `translate` is reached ONLY by typing `reqmap.py translate` — it is never called by
> `gate`, `sync`, `lint`, `map`, `export`, or the pre-commit hook. It is the only
> subcommand that invokes an external `claude` CLI subprocess.

Scenario: translate never runs from any other command
  Given  `subprocess.run` mocked to raise if `claude` is invoked
  When   `gate`, `sync`, `lint`, `map` and `export` run
  Then   none of them invoke `subprocess.run`, unlike `cmd_translate`

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-766
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# Corpus_lang(reqs) detects the corpus's majority language (ro or

> `corpus_lang(reqs)` detects the corpus's majority language (`ro` or `en`) by classifying
> each requirement's title+WHY+Contract+Acceptance text: Romanian diacritics are a certain
> signal; below that, whichever of a small RO/EN stopword list scores more hits wins. A
> per-file `lang: ro|en` frontmatter value overrides detection for that file.

Scenario: corpus_lang picks the majority language, override wins per file
  Given  two Romanian requirements and one English requirement, one Romanian file marked `lang: en`
  When   `corpus_lang` runs
  Then   it returns `ro` as the majority, and the marked file's effective language is `en`

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-767
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# Translate --to ro|en translates every requirement whose effective

> `translate [--to ro|en]` translates every requirement whose effective language matches
> the corpus majority into the target locale (default: the other of `ro`/`en`), caching
> results in `requirements/_i18n/<target>.json`, one file per target locale, keyed by
> requirement id.

Scenario: translate caches one entry per requirement in the target locale file
  Given  a Romanian-majority corpus and `translate --to en`
  When   it runs
  Then   `requirements/_i18n/en.json` gains one entry keyed by each translated requirement's id

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-768
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# The cache key is translation_hash(body, title) — a

> The cache key is `translation_hash(body, title)` — a hash over title + WHY + Contract +
> Acceptance, distinct from `binding_hash()` (Contract+Acceptance only, ARCH-DRIFT-003): a
> title-only edit also invalidates a cached translation, which reusing `binding_hash`
> would miss.

Scenario: a title-only edit invalidates the cached translation
  Given  two bodies identical except for the `# ` title line
  When   `translation_hash` runs on each, and `binding_hash` runs on each
  Then   the `translation_hash` values differ while the `binding_hash` values stay equal

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-769
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# Before a translation is cached, _translation_preserves_structure() compares the

> Before a translation is cached, `_translation_preserves_structure()` compares the source
> and translated text's backticked-span multiset, numeric-literal multiset, ordered
> heading/bullet markers, ordered `AC-N` criterion labels, and Gherkin-keyword multiset
> (Given/When/Then). A mismatch skips the entry with a `WARN` and writes nothing for it —
> it never partially caches a corrupted translation.

Scenario: a dropped backtick or number blocks the cache write
  Given  a translated string missing a backticked identifier the source has
  When   `_translation_preserves_structure` compares them
  Then   it returns false and `cmd_translate` writes no cache entry, printing a WARN

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-770
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# The AC-N labels and the Gherkin keywords are

> The `AC-N` labels and the Gherkin keywords are identifiers, not prose: a test names a
> criterion (`# verifies: <ID>#AC-N`) and the viewer highlights the keywords, so a
> translation that renames either is refused. The prompt states both rules, so a model
> that translates them is answering a question nobody asked.

Scenario: renaming a criterion label or a Gherkin keyword blocks the cache write
  Given  a translation that renames `CASE-1` to `CA-1`, or translates `Given` to `Dat fiind`
  When   `_translation_preserves_structure` compares it with the source
  Then   it returns false, refusing to cache the translation

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-771
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# A missing/erroring claude CLI, a timeout, or a

> A missing/erroring `claude` CLI, a timeout, or a malformed (missing-marker) response
> also skips that entry with a `WARN`. `translate` always exits 0 and never aborts the
> batch on a single entry's failure — it is a report-and-cache tool, not a gate.

Scenario: a missing claude CLI skips one entry without aborting the run
  Given  `subprocess.run` raising because the `claude` CLI is absent
  When   `cmd_translate` runs
  Then   it prints a WARN naming the requirement, writes no cache entry, and exits 0

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-772
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# A cache hit (stored hash matches current content)

> A cache hit (stored hash matches current content) is skipped without invoking `claude` —
> cost is proportional to what changed, not to corpus size.

Scenario: an unchanged requirement is a cache hit on the second run
  Given  a cached translation whose source requirement is unedited
  When   `cmd_translate` runs a second time
  Then   it does not call `claude` for that requirement

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-773
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# Map and export read requirements/_i18n/.json (when present) and

> `map` and `export` read `requirements/_i18n/*.json` (when present) and attach
> `node.i18n[locale] = {title, intent, contract, acceptance}` for any node whose cached
> hash still matches its current content; a stale entry (source edited since the last
> `translate` run) is silently dropped, never served. Neither command calls `claude` —
> this is a file read, so `map --check` stays exactly as deterministic and `claude`-free
> as before this capability existed.

Scenario: map attaches a fresh cache entry without ever calling claude
  Given  a `requirements/_i18n/en.json` entry whose hash matches the requirement's current content
  When   `_build_map_data` runs with `subprocess.run` mocked to raise on any call
  Then   the node carries `node.i18n.en` and no call to `claude` was made

## Members in code (auto)




--------------------


---
id: REQ-TRANSLATE-774
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRANSLATE-044]
superseded_by:
---

# The viewer consumes node.i18n ONLY through translatedText() (i18n.jsx)

> The viewer consumes `node.i18n` ONLY through `translatedText()` (i18n.jsx), which
> reports `isTranslated` alongside the text. Every caller that renders `isTranslated` text
> renders the "machine-translated, unreviewed" badge next to it. Absent a cache entry,
> content renders in the author's own language exactly as before this capability existed.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
