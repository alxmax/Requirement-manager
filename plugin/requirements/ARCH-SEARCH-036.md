---
id: ARCH-SEARCH-036
status: confirmed
level: system
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-SIMILAR-016]
satisfies: [SYS-REPORT-105]
superseded_by:
milestone: v2.13
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
<!-- Words used below, in plain terms:
     bag of words  the words a requirement is reduced to: its title, its intent line and
                   its Contract bullets.
     TF-IDF        a weight per word; a word common across the whole corpus counts for less.
     cosine        a 0-to-1 number saying how close two bags of words are.
     the floor     the lowest cosine score `search` is willing to call a match.
     the viewer    the map's HTML front-end (`app/`), which has its own search box.
     tokenize      cut a text into the separate words that get scored. -->

**What it ranks**
- `search "<query>"` ranks every requirement by how well its wording matches the query, then
  prints them most-relevant-first.
- `search` writes no file. It only reads and prints.

**How it scores**
- `search` reuses the scoring machinery of `dupes` (ARCH-SIMILAR-016). There is never a second
  scoring path.
- The query and each requirement both reduce to the same bag of words: title, intent line,
  Contract bullets.
- `search` then compares those two bags by cosine over smoothed TF-IDF weights.

**What it prints**
- `search` prints every match it shows together with that match's cosine score. A weak match
  then looks weak, instead of carrying the authority of a strong one.
- `search` shows at most `--top` matches. `--top` defaults to five.
- A `--top` of zero or less counts as one.
- `search` applies a relevance floor and never prints a ranked list of below-floor results.
- When no requirement scores at or above the floor, `search` prints an explicit
  no-strong-match line reporting the best score and the floor.
- The floor defaults to `0.05`.
- When the query holds no searchable term, `search` says so and ranks nothing. That line is
  distinct from the no-strong-match line.
- Tokenizing drops short words, stopwords and pure numbers. A query holds no searchable term
  when nothing survives that.
- The output of `search` says that the search is lexical, not synonym-aware. A user who gets no
  hit then knows to try other words rather than conclude no requirement exists.

**Exit code**
- `search` always returns zero from a well-formed invocation.
- A missing query argument is a usage error and returns a non-zero code.

**Parity with the viewer**
- The map viewer's search box ranks by this same model, never by a divergent one.
- The viewer's ranking (`app/src/lib/search.js`) is a faithful port of the engine scoring, so
  both surfaces agree on what matches in what order.
- A shared golden fixture pins the port to the engine: one fixed query scores identically in
  `app/scripts/ssr-smoke.jsx` and in the Python `Search` tests.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The match is purely lexical (token overlap). A query worded in synonyms of the requirement's text will score low or miss; this is why the floor and the "not synonym-aware" label exist, rather than a silent empty or spurious result.
- One relevance model, two surfaces: the CLI for headless/agent/CI callers, the viewer for a human browsing the map. The golden fixture is what keeps them from diverging.
- The `0.05` default was chosen because a short query is a sparse vector whose cosine against a full requirement runs far below the `dupes` pair threshold; on this corpus a correct top hit scores well above it while a no-lexical-overlap query stays below.
- The floor is a module constant, not a flag. It was calibrated on this corpus; a very different corpus could warrant a different value, which is a code change, not configuration — keeping the surface minimal.
- The query is folded into the corpus for the idf computation, so its terms participate in the document-frequency statistics exactly as the benchmark that validated the ranking did.

## Cases (= tests)
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

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana half-remembers there is a requirement about "detecting when a contract changes against
  the lock" but not its id. She runs `reqmap.py search "detect drift when a contract changes
  against the lock"` and `ARCH-DRIFT-003` comes back first with its score, ahead of the related
  member-drift requirement — she opens the right file directly. Later she searches for a phrase
  no requirement uses; instead of a misleading top guess, `search` tells her the best score is
  below the floor and that the match is lexical, so she rewords and tries again.

## WHERE — Current implementation
- `cmd_search` in `reqmap.py` — tokenizes the query with `_sim_tokens`, builds each requirement's bag with `_sim_text`, folds the query into the corpus, then reuses `_tfidf` and `_cosine` (ARCH-SIMILAR-016) to rank. It prints each hit's score via `_req_title`, guards the empty-query and no-strong-match branches against the `SEARCH_FLOOR` constant, and always returns zero.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-SEARCH-650
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search writes no file. It only reads and

> `search` writes no file. It only reads and prints.

Scenario: search runs without creating or modifying any file
  Given  a populated requirements corpus and a query with no output-writing flag
  When   `search "<query>"` runs
  Then   no file in the corpus changes and only stdout carries output

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-651
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search reuses the scoring machinery of dupes (ARCH-SIMILAR-016)

> `search` reuses the scoring machinery of `dupes` (ARCH-SIMILAR-016). There is never a
> second scoring path.

Scenario: search scores a pair the same way dupes does
  Given  a query text identical to one requirement's full bag of words
  When   `search` and `dupes` score that same pair
  Then   both report the identical cosine score, since both call `_tfidf` and `_cosine`

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-652
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# The query and each requirement both reduce to

> The query and each requirement both reduce to the same bag of words: title, intent line,
> Contract bullets.

Scenario: only title, intent line and Contract bullets feed the match
  Given  a requirement whose Notes section mentions a word absent from its title, intent and Contract
  When   a query using only that Notes-only word runs through `search`
  Then   that requirement does not score above the floor on that word alone

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-653
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search then compares those two bags by cosine

> `search` then compares those two bags by cosine over smoothed TF-IDF weights.

Scenario: a rarer shared term outweighs a common one
  Given  two requirements matching the query on one common word and one rare word respectively
  When   `search` runs
  Then   the requirement sharing the rare word ranks higher, reflecting its higher TF-IDF
         weight, and prints before the other match

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-654
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search prints every match it shows together with

> `search` prints every match it shows together with that match's cosine score. A weak
> match then looks weak, instead of carrying the authority of a strong one.

Scenario: each printed result carries its cosine score
  Given  a query matching at least one requirement above the floor
  When   `search` runs
  Then   every printed match line shows that match's cosine score next to its id

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-655
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search shows at most --top matches. --top defaults

> `search` shows at most `--top` matches. `--top` defaults to five.

Scenario: search defaults to five results
  Given  a query matching more than five requirements above the floor, and no `--top` flag
  When   `search` runs
  Then   it prints exactly five matches

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-656
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# A --top of zero or less counts as

> A `--top` of zero or less counts as one.

Scenario: a non-positive --top still prints one match
  Given  a query with at least one match above the floor and `--top 0`
  When   `search` runs
  Then   it prints exactly one match, not zero

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-657
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search applies a relevance floor and never prints

> `search` applies a relevance floor and never prints a ranked list of below-floor
> results.

Scenario: below-floor results never appear as a ranked list
  Given  a query whose best score falls under the floor
  When   `search` runs
  Then   no ranked results print, only the no-strong-match line

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-658
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# When no requirement scores at or above the

> When no requirement scores at or above the floor, `search` prints an explicit
> no-strong-match line reporting the best score and the floor.

Scenario: the no-strong-match line names the best score and the floor
  Given  a query with no requirement scoring at or above the floor
  When   `search` runs
  Then   the printed line reports both the best score found and the floor value

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-659
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# The floor defaults to 0.05

> The floor defaults to `0.05`.

Scenario: the floor is 0.05 absent an override
  Given  a query scoring just above 0.05 against one requirement and below against all others
  When   `search` runs
  Then   that one requirement is reported as a match

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-660
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# When the query holds no searchable term, search

> When the query holds no searchable term, `search` says so and ranks nothing. That line
> is distinct from the no-strong-match line.

Scenario: an all-stopword query says so, not "no strong match"
  Given  a query made only of stopwords and pure numbers
  When   `search` runs
  Then   it prints the "no searchable terms" line, never the no-strong-match line

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-661
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Tokenizing drops short words, stopwords and pure numbers

> Tokenizing drops short words, stopwords and pure numbers. A query holds no searchable
> term when nothing survives that.

Scenario: short words and numbers never seed a match
  Given  a query of only two-letter words and digit-only tokens
  When   `search` tokenizes it
  Then   every token is dropped, so the query counts as holding no searchable term

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-662
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# The output of search says that the search

> The output of `search` says that the search is lexical, not synonym-aware. A user who
> gets no hit then knows to try other words rather than conclude no requirement exists.

Scenario: the no-strong-match line names the search as lexical
  Given  a query with no requirement scoring at or above the floor
  When   `search` prints its no-strong-match line
  Then   that line states the match is lexical, not synonym-aware

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-663
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# Search always returns zero from a well-formed invocation

> `search` always returns zero from a well-formed invocation.

Scenario: a well-formed search always exits zero
  Given  a query, whether it matches strongly, weakly, or not at all
  When   `search` runs
  Then   the process exits 0 in every case

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-664
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# A missing query argument is a usage error

> A missing query argument is a usage error and returns a non-zero code.

Scenario: a missing query argument fails with a nonzero exit
  Given  `search` invoked with no query argument
  When   the command runs
  Then   it prints a usage error and exits with a nonzero code

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-665
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# The map viewer's search box ranks by this

> The map viewer's search box ranks by this same model, never by a divergent one.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-666
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# The viewer's ranking (app/src/lib/search.js) is a faithful port

> The viewer's ranking (`app/src/lib/search.js`) is a faithful port of the engine scoring,
> so both surfaces agree on what matches in what order.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SEARCH-667
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SEARCH-036]
superseded_by:
---

# A shared golden fixture pins the port to

> A shared golden fixture pins the port to the engine: one fixed query scores identically
> in `app/scripts/ssr-smoke.jsx` and in the Python `Search` tests.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
