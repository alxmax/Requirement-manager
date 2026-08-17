---
id: REQ-SEARCH-036
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, REQ-SIMILAR-016]
superseded_by:
milestone: v2.13
---

# Free-text requirement search

> To find the requirement about a topic today you grep the requirements folder or open the
> map — grep needs the exact word the author used, and neither ranks results. This ranks
> every requirement by how well its wording matches a free-text query, most-relevant-first,
> so "where is the drift thing?" lands on the right file without knowing its id. It reuses
> the same lexical scoring `dupes` already trusts, so it adds a way in, not a new engine.
> Because the match is lexical it can miss a synonym; when nothing matches well it says so
> plainly, so a near-miss is never mistaken for the answer — the drift this whole tool exists
> to prevent.

## WHAT — Contract (normative)
Every line in this section is binding.
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
- `search` reuses the scoring machinery of `dupes` (REQ-SIMILAR-016). There is never a second
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The match is purely lexical (token overlap). A query worded in synonyms of the requirement's text will score low or miss; this is why the floor and the "not synonym-aware" label exist, rather than a silent empty or spurious result.
- One relevance model, two surfaces: the CLI for headless/agent/CI callers, the viewer for a human browsing the map. The golden fixture is what keeps them from diverging.
- The `0.05` default was chosen because a short query is a sparse vector whose cosine against a full requirement runs far below the `dupes` pair threshold; on this corpus a correct top hit scores well above it while a no-lexical-overlap query stays below.
- The floor is a module constant, not a flag. It was calibrated on this corpus; a very different corpus could warrant a different value, which is a code change, not configuration — keeping the surface minimal.
- The query is folded into the corpus for the idf computation, so its terms participate in the document-frequency statistics exactly as the benchmark that validated the ranking did.

## HOW — Acceptance (= tests)
AC-1
  Given  a query whose terms clearly match one requirement's contract
  When   `search` runs
  Then   that requirement appears in the results with its cosine score, ranked first

AC-2
  Given  a query with no lexical overlap with any requirement
  When   `search` runs
  Then   it prints the explicit no-strong-match line (best score below the floor) and
         does not print a ranked result

AC-3
  Given  a query that is empty after tokenizing (only stopwords / short words)
  When   `search` runs
  Then   it prints the "no searchable terms" line, distinct from the no-strong-match case

AC-4
  Given  more matching requirements than `--top`
  When   `search` runs with that `--top`
  Then   at most `--top` matches are printed

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana half-remembers there is a requirement about "detecting when a contract changes against
  the lock" but not its id. She runs `reqmap.py search "detect drift when a contract changes
  against the lock"` and `CORE-DRIFT-003` comes back first with its score, ahead of the related
  member-drift requirement — she opens the right file directly. Later she searches for a phrase
  no requirement uses; instead of a misleading top guess, `search` tells her the best score is
  below the floor and that the match is lexical, so she rewords and tries again.

## WHERE — Current implementation
- `cmd_search` in `reqmap.py` — tokenizes the query with `_sim_tokens`, builds each requirement's bag with `_sim_text`, folds the query into the corpus, then reuses `_tfidf` and `_cosine` (REQ-SIMILAR-016) to rank. It prints each hit's score via `_req_title`, guards the empty-query and no-strong-match branches against the `SEARCH_FLOOR` constant, and always returns zero.

## Links
- Used by: (auto)
## Members in code (auto)
