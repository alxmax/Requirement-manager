---
id: REQ-SIMILAR-016
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.14
---

# Duplicate-capability detector

> When two requirements quietly describe the same capability, you do not notice until each
> has grown its own divergent implementation — and now there is a mess to untangle. This
> compares requirement pairs by their wording and flags the ones that overlap, so a reviewer
> can merge or sharpen them early. Without it, duplication stays invisible until it is expensive.

## WHAT — Contract (normative)
Every line in this section is binding.
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

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The default threshold is a starting point, not a proven value. A reviewer tunes it with `--threshold` for the corpus at hand.
- Detection is lexical, not semantic. Two contracts that mean the same thing in different words may score low. The command surfaces likely duplicates; it does not prove duplication.
- Comparison is requirement-to-requirement only. Matching untagged code to an existing requirement is a separate, fuzzier problem left to `plan`.

## HOW — Acceptance (= tests)
AC-1
  Given  two requirements with near-identical Contract text
  When   `dupes` runs
  Then   the pair is reported with a high score

AC-2
  Given  two requirements about unrelated topics
  When   `dupes` runs at the default threshold
  Then   the pair is not reported

AC-3
  Given  a corpus with fewer than two requirements that have contract text
  When   `dupes` runs
  Then   it prints a "need at least two" message and returns zero

AC-4
  Given  a custom `--threshold` above a pair's score
  When   `dupes` runs
  Then   that pair is not reported

AC-5
  Given  any corpus
  When   `dupes` runs
  Then   it returns zero

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana suspects two of her requirements overlap. She runs `reqmap.py dupes` and sees a pair
  scored `0.82` with the shared words "token, session, expire" listed. She opens both, realises
  one is a subset of the other, and merges them before either grows its own divergent code.

## WHERE — Current implementation
- `cmd_similar`, `_sim_text`, `_sim_tokens`, `_tfidf` and `_cosine` in `reqmap.py` — `_sim_text` gathers the compared text, `_sim_tokens` builds the bag of words, `_tfidf` weights terms with smoothed inverse-document frequency, and `_cosine` scores each pair. `cmd_similar` sorts the pairs and prints them with their shared terms.

## Links
- Used by: (auto)
## Members in code (auto)
