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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

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

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
