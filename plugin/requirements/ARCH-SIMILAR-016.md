---
id: ARCH-SIMILAR-016
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-QUALITY-104]
superseded_by:
milestone: v1.14
---

# Duplicate-capability detector

## Description
> When two requirements quietly describe the same capability, you do not notice until each
> has grown its own divergent implementation — and now there is a mess to untangle. This
> compares requirement pairs by their wording and flags the ones that overlap, so a reviewer
> can merge or sharpen them early. Without it, duplication stays invisible until it is expensive.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a bag of words  the list of words taken from one requirement, used to compare it
                     with another.
     a token         one word after the text has been cut up and cleaned.
     TF-IDF          a weight per word: a word that appears in nearly every
                     requirement counts for little, a rare one counts for more.
     cosine          a zero-to-one number saying how alike two bags of words are.
     the threshold   the score a pair has to reach before `dupes` reports it. -->

**What it is**
- `dupes` reports pairs of requirements whose contracts overlap.
- `dupes` writes nothing. It only reads and prints.

**What it compares**
- `dupes` builds a bag of words for each requirement from its title, its intent line,
  and its Contract bullets.
- `dupes` leaves the "Notes & limitations" section out of that text, because that
  section is dense and would add noise.
- `dupes` tokenizes text into lowercase alphanumeric words of length three or more.
- `dupes` drops a small stopword set and pure numbers from those tokens.
- `dupes` skips a requirement whose Contract bullets are all still the draft placeholder
  (`TODO: …`), and prints how many it skipped. An unauthored contract has nothing to compare.
- `dupes` skips a pair linked by `tested-by` — one requirement's `tested-by` file is the
  other's `implements` file, so the second requirement IS the first one's test suite —
  and prints how many such pairs it skipped. Such a pair shares vocabulary by construction
  and is a known link, not a duplicate.

**How it scores**
- `dupes` weights terms with a smoothed TF-IDF (`log((1 + N) / (1 + df)) + 1`).
- The smoothing keeps every weight positive, so a two-requirement corpus does not
  collapse to a zero score.
- `dupes` scores each pair with cosine similarity in the range zero to one.
- `dupes` reports only the pairs at or above the threshold.
- The threshold defaults to `0.35`.
- `--threshold` overrides that default.

**What it prints**
- `dupes` prints pairs most-similar-first, each with its score and up to five shared
  terms, so the reviewer can see why the pair was flagged.

**Exit code**
- `dupes` always returns zero. The report is advisory: a human decides whether a
  flagged pair is a real duplicate.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The default threshold is a starting point, not a proven value. A reviewer tunes it with `--threshold` for the corpus at hand.
- Detection is lexical, not semantic. Two contracts that mean the same thing in different words may score low. The command surfaces likely duplicates; it does not prove duplication.
- Comparison is requirement-to-requirement only. Matching untagged code to an existing requirement is a separate, fuzzier problem left to `plan`.

## Cases (= tests)
CASE-1
  Given  two requirements with near-identical Contract text
  When   `dupes` runs
  Then   the pair is reported with a high score

CASE-2
  Given  two requirements about unrelated topics
  When   `dupes` runs at the default threshold
  Then   the pair is not reported

CASE-3
  Given  a corpus with fewer than two requirements that have contract text
  When   `dupes` runs
  Then   it prints a "need at least two" message and returns zero

CASE-4
  Given  a custom `--threshold` above a pair's score
  When   `dupes` runs
  Then   that pair is not reported

CASE-5
  Given  any corpus
  When   `dupes` runs
  Then   it returns zero

CASE-6
  Given  two fresh drafts whose Contract is the placeholder, and two authored requirements
  When   `dupes` runs
  Then   the drafts are skipped with a count line, and only the authored pair can be reported

CASE-7
  Given  a requirement A whose `tested-by` file implements requirement B, with overlapping contracts
  When   `dupes` runs with the member map
  Then   the pair A–B is not reported and a "linked by tested-by" count line is printed; without the member map it is reported as before

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana suspects two of her requirements overlap. She runs `reqmap.py dupes` and sees a pair
  scored `0.82` with the shared words "token, session, expire" listed. She opens both, realises
  one is a subset of the other, and merges them before either grows its own divergent code.

## WHERE — Current implementation
- `cmd_similar`, `_sim_text`, `_sim_tokens`, `_tfidf`, `_cosine` and `_test_suite_pairs` in `reqmap.py` — `_sim_text` gathers the compared text, `_sim_tokens` builds the bag of words, `_tfidf` weights terms with smoothed inverse-document frequency, `_cosine` scores each pair, and `_test_suite_pairs` derives the tested-by-linked pairs from the member map. `cmd_similar` sorts the pairs and prints them with their shared terms.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-687
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes reports pairs of requirements whose contracts overlap

> `dupes` reports pairs of requirements whose contracts overlap.

Scenario: overlapping contracts are reported as a pair
  Given  two requirements whose Contract bullets share most of their wording
  When   `dupes` runs
  Then   that pair appears in the printed report

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-688
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes writes nothing. It only reads and prints

> `dupes` writes nothing. It only reads and prints.

Scenario: dupes runs without writing any file
  Given  a corpus with at least one flagged pair
  When   `dupes` runs
  Then   no requirement file changes and output goes only to stdout

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-689
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes builds a bag of words for each

> `dupes` builds a bag of words for each requirement from its title, its intent line, and
> its Contract bullets.

Scenario: the bag of words comes from title, intent and Contract only
  Given  two requirements sharing wording only in their titles and Contract bullets
  When   `dupes` builds each requirement's bag of words
  Then   that shared wording is included and drives the comparison

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-690
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes leaves the "Notes & limitations" section out

> `dupes` leaves the "Notes & limitations" section out of that text, because that section
> is dense and would add noise.

Scenario: text unique to the Notes section is left out of the bag
  Given  two unrelated requirements whose Notes sections happen to share several words
  When   `dupes` runs
  Then   that shared Notes wording does not raise their pair's score

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-691
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes tokenizes text into lowercase alphanumeric words of

> `dupes` tokenizes text into lowercase alphanumeric words of length three or more.

Scenario: tokens shorter than three characters are dropped
  Given  two requirements whose only shared wording is two-letter tokens
  When   `dupes` tokenizes their text
  Then   those tokens are absent from either bag of words

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-692
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes drops a small stopword set and pure

> `dupes` drops a small stopword set and pure numbers from those tokens.

Scenario: stopwords and pure numbers never count as shared terms
  Given  two unrelated requirements sharing only stopwords and a number like "2026"
  When   `dupes` runs
  Then   neither is listed among the pair's shared terms

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-693
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes skips a requirement whose Contract bullets are

> `dupes` skips a requirement whose Contract bullets are all still the draft placeholder
> (`TODO: …`), and prints how many it skipped. An unauthored contract has nothing to
> compare.

Scenario: an unauthored draft is skipped and counted
  Given  a requirement whose Contract bullets are all still `TODO: …`
  When   `dupes` runs
  Then   that requirement is excluded from comparison and the skip count includes it

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-694
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes skips a pair linked by tested-by —

> `dupes` skips a pair linked by `tested-by` — one requirement's `tested-by` file is the
> other's `implements` file, so the second requirement IS the first one's test suite — and
> prints how many such pairs it skipped. Such a pair shares vocabulary by construction and
> is a known link, not a duplicate.

Scenario: a tested-by-linked pair is skipped and counted
  Given  requirement A whose `tested-by` file is requirement B's `implements` file, with overlapping wording
  When   `dupes` runs with the member map
  Then   the pair is excluded from the report and the linked-pairs count includes it

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-695
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes weights terms with a smoothed TF-IDF (log((1

> `dupes` weights terms with a smoothed TF-IDF (`log((1 + N) / (1 + df)) + 1`).

Scenario: a rarer term is weighted higher than a common one
  Given  a corpus where one term appears in nearly every requirement and another appears in only two
  When   `dupes` computes TF-IDF weights
  Then   the rare term's weight is higher than the common term's

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-696
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# The smoothing keeps every weight positive, so a

> The smoothing keeps every weight positive, so a two-requirement corpus does not collapse
> to a zero score.

Scenario: a two-requirement corpus still scores a shared term
  Given  exactly two requirements sharing one term present in both
  When   `dupes` scores that pair
  Then   the score is above zero, not collapsed by an unsmoothed weight of zero

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-697
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes scores each pair with cosine similarity in

> `dupes` scores each pair with cosine similarity in the range zero to one.

Scenario: cosine score stays bounded between zero and one
  Given  one pair of near-identical requirements and one pair with no shared wording
  When   `dupes` scores both pairs
  Then   the identical pair scores near one and the unrelated pair scores near zero, neither outside that range

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-698
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes reports only the pairs at or above

> `dupes` reports only the pairs at or above the threshold.

Scenario: a below-threshold pair is left out of the report
  Given  two requirements whose score falls under the active threshold
  When   `dupes` runs
  Then   that pair is absent from the printed report

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-699
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# The threshold defaults to 0.35

> The threshold defaults to `0.35`.

Scenario: the default threshold is 0.35
  Given  a pair scoring above 0.35 and a pair scoring below it, with no `--threshold` flag
  When   `dupes` runs
  Then   only the pair above 0.35 is reported

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-700
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# --threshold overrides that default

> `--threshold` overrides that default.

Scenario: --threshold replaces the default cutoff
  Given  a pair scoring 0.20, below the default threshold
  When   `dupes --threshold 0.1` runs
  Then   that pair is now reported

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-701
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes prints pairs most-similar-first, each with its score

> `dupes` prints pairs most-similar-first, each with its score and up to five shared
> terms, so the reviewer can see why the pair was flagged.

Scenario: reported pairs are sorted and show their shared terms
  Given  three flagged pairs with different scores, one sharing more than five terms
  When   `dupes` runs
  Then   they print highest-score-first, each with its score and at most five shared terms

## Members in code (auto)




--------------------


---
id: REQ-SIMILAR-702
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SIMILAR-016]
superseded_by:
---

# Dupes always returns zero. The report is advisory

> `dupes` always returns zero. The report is advisory: a human decides whether a flagged
> pair is a real duplicate.

Scenario: dupes exits zero regardless of what it finds
  Given  a corpus containing several flagged pairs
  When   `dupes` runs
  Then   the process still exits 0

## Members in code (auto)
