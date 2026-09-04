---
id: ARCH-SEARCH-036
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.13
depends_on: [ARCH-PARSE-001, ARCH-SIMILAR-016]
satisfies: [SYS-REPORT-105]
---

# Free-text requirement search

## Description
> To find the requirement about a topic today you grep the requirements folder or open the
> map — grep needs the exact word the author used, and neither ranks results. This ranks
> every requirement by how well its wording matches a free-text query, most-relevant-first,
> so "where is the drift thing?" lands on the right file without knowing its id. It reuses
> the same lexical scoring `dupes` already trusts, so it adds a way in, not a new engine.
> Because the match is lexical it can miss a synonym; when nothing matches well it says so
> plainly, so a near-miss is never mistaken for the answer — the drift this whole tool exists
> to prevent.

Every bullet below is binding.
- `search "<query>"` ranks every requirement by how well its wording matches the query, most-relevant-first, reusing the exact model the viewer's search box ports. [[REQ-SEARCH-912]]
- `search` prints every match together with its cosine score, so a weak match never carries a strong match's authority. [[REQ-SEARCH-913]]
- `search` applies a relevance floor (`0.05` by default) and reports plainly, in a message distinct from an empty query, when nothing clears it. [[REQ-SEARCH-914]]
- `search` always exits zero from a well-formed invocation; only a usage error (a missing query) exits non-zero. [[REQ-SEARCH-915]]
- `search` answers a query that names an id, and a query that appears literally in a requirement's text, before it falls back to ranking wording. [[REQ-SEARCH-965]]

## Cases
CASE-1
  Given  a query whose terms clearly match one requirement's contract
  When   `search` runs
  Then   that requirement appears in the results with its cosine score, ranked first

CASE-2
  Given  a query with no lexical overlap with any requirement
  When   `search` runs
  Then   it prints the explicit no-strong-match line (best score below the floor) and
         does not print a ranked result

CASE-3
  Given  a query that is empty after tokenizing (only stopwords / short words)
  When   `search` runs
  Then   it prints the "no searchable terms" line, distinct from the no-strong-match case

CASE-4
  Given  more matching requirements than `--top`
  When   `search` runs with that `--top`
  Then   at most `--top` matches are printed

## Context
**Terms**
- bag of words  the words a requirement is reduced to: its title, its intent line and
- its Contract bullets.
- TF-IDF        a weight per word; a word common across the whole corpus counts for less.
- cosine        a 0-to-1 number saying how close two bags of words are.
- the floor     the lowest cosine score `search` is willing to call a match.
- the viewer    the map's HTML front-end (`app/`), which has its own search box.
- tokenize      cut a text into the separate words that get scored.

**Notes**
- The match is purely lexical (token overlap). A query worded in synonyms of the requirement's text will score low or miss; this is why the floor and the "not synonym-aware" label exist, rather than a silent empty or spurious result.
- One relevance model, two surfaces: the CLI for headless/agent/CI callers, the viewer for a human browsing the map. The golden fixture is what keeps them from diverging.
- The `0.05` default was chosen because a short query is a sparse vector whose cosine against a full requirement runs far below the `dupes` pair threshold; on this corpus a correct top hit scores well above it while a no-lexical-overlap query stays below.
- The floor is a module constant, not a flag. It was calibrated on this corpus; a very different corpus could warrant a different value, which is a code change, not configuration — keeping the surface minimal.
- The query is folded into the corpus for the idf computation, so its terms participate in the document-frequency statistics exactly as the benchmark that validated the ranking did.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana half-remembers there is a requirement about "detecting when a contract changes against
  the lock" but not its id. She runs `reqmap.py search "detect drift when a contract changes
  against the lock"` and `ARCH-DRIFT-003` comes back first with its score, ahead of the related
  member-drift requirement — she opens the right file directly. Later she searches for a phrase
  no requirement uses; instead of a misleading top guess, `search` tells her the best score is
  below the floor and that the match is lexical, so she rewords and tries again.

**Current implementation**
- `cmd_search` in `reqmap.py` — tokenizes the query with `_sim_tokens`, builds each requirement's bag with `_sim_text`, folds the query into the corpus, then reuses `_tfidf` and `_cosine` (ARCH-SIMILAR-016) to rank. It prints each hit's score via `_req_title`, guards the empty-query and no-strong-match branches against the `SEARCH_FLOOR` constant, and always returns zero.


--------------------


---
id: REQ-SEARCH-912
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
---

# Ranking a query against the corpus

## Description
> `search` turns a free-text query into a ranked list of requirements by reusing the exact
> TF-IDF/cosine model `dupes` already uses to compare requirements to each other, so there is
> only one scoring engine in the codebase, not two that could drift apart. The map viewer's
> search box ports the same model, pinned to it by a shared golden fixture, so a developer
> gets the same ranking whether they search from the CLI or the browser.

Every bullet below is binding.
- `search "<query>"` ranks every requirement by how well its wording matches the query, then
  prints them most-relevant-first.
- `search` writes no file. It only reads and prints.
- `search` reuses the scoring machinery of `dupes` (ARCH-SIMILAR-016). There is never a second
  scoring path.
- The query and each requirement both reduce to the same bag of words: title, intent line,
  Contract bullets.
- `search` then compares those two bags by cosine over smoothed TF-IDF weights.
- The map viewer's search box (`app/src/lib/search.js`) ports this exact model, never a
  divergent one, so both surfaces agree on what matches in what order.
- A shared golden fixture pins the port to the engine: one fixed query scores identically in
  `app/scripts/ssr-smoke.jsx` and in the Python `Search` tests.

## Cases
CASE-1 — search runs without creating or modifying any file
  Given  a populated requirements corpus and a query with no output-writing flag
  When   `search "<query>"` runs
  Then   no file in the corpus changes and only stdout carries output

CASE-2 — search scores a pair the same way dupes does
  Given  a query text identical to one requirement's full bag of words
  When   `search` and `dupes` score that same pair
  Then   both report the identical cosine score, since both call `_tfidf` and `_cosine`

CASE-3 — only title, intent line and Contract bullets feed the match
  Given  a requirement whose Notes section mentions a word absent from its title, intent and Contract
  When   a query using only that Notes-only word runs through `search`
  Then   that requirement does not score above the floor on that word alone

CASE-4 — a rarer shared term outweighs a common one
  Given  two requirements matching the query on one common word and one rare word respectively
  When   `search` runs
  Then   the requirement sharing the rare word ranks higher, reflecting its higher TF-IDF
         weight, and prints before the other match

CASE-5 — the viewer's ported model scores identically to the engine
  Given  the shared golden fixture used by both the Python `Search` tests and the JS SSR smoke test
  When   the same query runs through the engine's `search` and the viewer's ported scorer
  Then   both report the identical cosine score for the same requirement


--------------------


---
id: REQ-SEARCH-913
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
---

# Printing ranked matches with their score

## Description
> Each printed match carries the cosine score that earned it its place, so a weak match is
> visibly weak rather than looking as authoritative as a strong one. Without a visible score, a
> caller could mistake a barely-passing hit for a confident answer.

Every bullet below is binding.
- `search` prints every match it shows together with that match's cosine score. A weak match
  then looks weak, instead of carrying the authority of a strong one.
- `search` shows at most `--top` matches. `--top` defaults to five.
- A `--top` of zero or less counts as one.
- `search` applies a relevance floor and never prints a ranked list of below-floor results.
- When no requirement scores at or above the floor, `search` prints an explicit
  no-strong-match line reporting the best score and the floor.

## Cases
CASE-1 — each printed result carries its cosine score
  Given  a query matching at least one requirement above the floor
  When   `search` runs
  Then   every printed match line shows that match's cosine score next to its id

CASE-2 — search defaults to five results
  Given  a query matching more than five requirements above the floor, and no `--top` flag
  When   `search` runs
  Then   it prints exactly five matches

CASE-3 — a non-positive --top still prints one match
  Given  a query with at least one match above the floor and `--top 0`
  When   `search` runs
  Then   it prints exactly one match, not zero

CASE-4 — below-floor results never appear as a ranked list
  Given  a query whose best score falls under the floor
  When   `search` runs
  Then   no ranked results print, only the no-strong-match line

CASE-5 — the no-strong-match line names the best score and the floor
  Given  a query with no requirement scoring at or above the floor
  When   `search` runs
  Then   the printed line reports both the best score found and the floor value


--------------------


---
id: REQ-SEARCH-914
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
---

# The relevance floor and the empty-query message

## Description
> A query with no usable words (all stopwords, or too short) is not the same failure as a query
> that simply found nothing above the relevance floor — conflating the two would hide a typo'd
> or accidental empty query behind the same message as a genuine no-match, so `search` reports
> each with its own distinct line.

Every bullet below is binding.
- The floor defaults to `0.05`.
- When the query holds no searchable term, `search` says so and ranks nothing. That line is
  distinct from the no-strong-match line.
- Tokenizing drops short words, stopwords and pure numbers. A query holds no searchable term
  when nothing survives that.
- The output of `search` says that the search is lexical, not synonym-aware. A user who gets no
  hit then knows to try other words rather than conclude no requirement exists.

## Cases
CASE-1 — the floor is 0.05 absent an override
  Given  a query scoring just above 0.05 against one requirement and below against all others
  When   `search` runs
  Then   that one requirement is reported as a match

CASE-2 — an all-stopword query says so, not "no strong match"
  Given  a query made only of stopwords and pure numbers
  When   `search` runs
  Then   it prints the "no searchable terms" line, never the no-strong-match line

CASE-3 — short words and numbers never seed a match
  Given  a query of only two-letter words and digit-only tokens
  When   `search` tokenizes it
  Then   every token is dropped, so the query counts as holding no searchable term

CASE-4 — the no-strong-match line names the search as lexical
  Given  a query with no requirement scoring at or above the floor
  When   `search` prints its no-strong-match line
  Then   that line states the match is lexical, not synonym-aware


--------------------


---
id: REQ-SEARCH-915
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
---

# Search always exits zero on a well-formed query

## Description
> `search` is a read-only reporting command: whatever it finds — a strong match, a weak one, or
> nothing at all — is a normal result, not a failure, so the process exits 0. Only a genuine
> usage error, such as an omitted query, is a real failure and exits non-zero.

Every bullet below is binding.
- `search` always returns zero from a well-formed invocation, regardless of how well (or
  poorly) the query matched.
- A missing query argument is a usage error and returns a non-zero code.
- An empty corpus, or a corpus where no requirement carries contract text, still exits zero
  and prints an explanatory line rather than crashing.

## Cases
CASE-1 — a well-formed search always exits zero
  Given  a query, whether it matches strongly, weakly, or not at all
  When   `search` runs
  Then   the process exits 0 in every case

CASE-2 — a missing query argument fails with a nonzero exit
  Given  `search` invoked with no query argument
  When   the command runs
  Then   it prints a usage error and exits with a nonzero code

CASE-3 — an empty corpus still exits zero
  Given  no requirements carry any contract text to search
  When   `search` runs
  Then   it prints "No requirements with contract text to search." and exits 0
---
id: REQ-SEARCH-965
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
---

# Finding a requirement by its id, and by its literal text

## Description
> The bag of words a requirement is ranked on is its title, its intent and its clauses — its id is
> in none of them. So searching this corpus for `ARCH-CHECK-006` returned `REQ-ORPHANCODE-888` and
> not the requirement named, because "arch" and "check" were matched as ordinary prose. An id is
> the primary key here, and a phrase that appears verbatim in a requirement is stronger evidence
> than a partial token overlap with a different one — neither is a question about wording, and the
> ranking model cannot answer either.

Every bullet below is binding.
- A query equal to a requirement id returns that requirement, alone, ahead of every ranked result.
- A query that prefixes or occurs inside ids returns those requirements ahead of the ranked
  results, capped so a common word cannot crowd the ranking out.
- A query that occurs literally in a requirement's title, description or cases returns that
  requirement ahead of the ranked results. `## Context` is excluded, exactly as it is from
  the ranking bag: commentary is not what a requirement is about.
- The literal search also reads a requirement's cached translation, so a query in the language the
  reader is being shown finds the requirement even though the ranking model indexes one language.
- The ranking model itself is unchanged by all of this: the id and literal layers select
  requirements, and the ranked layer fills what they leave, so the score a hit carries still means
  exactly what it meant before.

## Cases
CASE-1 — an exact id returns its own requirement first
  Given  a corpus holding `AREA-X-001` and requirements whose prose mentions "area" and "x"
  When   `search "AREA-X-001"` runs
  Then   `AREA-X-001` is the first result, marked as an id match

CASE-2 — a partial id returns the ids it names
  Given  a corpus holding `AREA-X-001` and `AREA-X-002`
  When   `search "AREA-X"` runs
  Then   both are returned ahead of any ranked result

CASE-3 — a phrase inside a case is found
  Given  a requirement whose only mention of "ghost tag" is inside one of its cases
  When   `search "ghost tag"` runs
  Then   that requirement is returned, marked as a text match

CASE-6 — a phrase living only in Context is not a match
  Given  a requirement whose only mention of a word is inside its `## Context`
  When   `search` runs on that word
  Then   the requirement is not returned by the literal layer

CASE-4 — a query in the cached translation's language finds the requirement
  Given  a requirement with a cached translation containing a phrase absent from its English text
  When   `search` runs on that phrase
  Then   the requirement is returned

CASE-5 — the ranked model is untouched
  Given  a query naming no id and appearing literally nowhere
  When   `search` runs
  Then   every result comes from the ranking model, with the same scores as before
