---
id: ARCH-CLARIFY-062
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v4.0
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-AUTHOR-101]
---

# Questions a requirement has not answered

## Description
> The expensive ambiguity is the one nobody notices while the requirement is being written.
> "The gate reports errors quickly" reads fine, passes the linter, and is discovered to mean
> nothing three weeks later by whoever has to write the assertion. `clarify` asks the
> questions a careful reviewer would ask at authoring time — what threshold, what unit, what
> happens when it fails — so the answer lands in the requirement instead of being guessed in
> code. It only ever asks.

Every bullet below is binding.
- `clarify` detects the shapes that cannot be verified as written and turns each into one question about the requirement's own text. [[REQ-CLARIFY-956]]
- `clarify` prints the questions grouped by severity, or emits them as JSON, writes nothing, and always exits 0. [[REQ-CLARIFY-957]]

## Cases
CASE-1 — a requirement with nothing detectable says so
  Given  a requirement whose clauses carry no hedge, no bare number and a case per clause
  When   `clarify` runs on it
  Then   it reports nothing unclear and points at `implement`

CASE-2 — the questions are deterministic
  Given  the same requirement, unchanged
  When   `clarify` runs twice
  Then   both runs emit the same questions in the same order

CASE-3 — clarify never fails a build
  Given  a requirement with several blocking questions
  When   `clarify` runs
  Then   it exits 0


---
id: REQ-CLARIFY-956
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CLARIFY-062]
---

# Detecting what a requirement leaves open

## Description
> Each detector encodes one question a reviewer asks by reflex. They are deliberately
> shallow — lexical, per clause, no model of meaning — because a question that is
> occasionally unnecessary costs a sentence, while a missed ambiguity costs a rewrite.

Every bullet below is binding.
- A clause carrying a hedge word with no measurable threshold raises one question naming that word.
- A bare number in a clause with no unit beside it raises a question asking for the unit; an
  identifier such as a version or a case label is not a bare number.
- A clause quantified over "all", "every" or "any" with no stated limit raises a question about
  the upper bound.
- A clause whose subject is "It" or "the system" raises a question asking which component acts.
- A requirement with more clauses than cases raises one question per uncovered clause, and one
  whose cases never mention a failure path raises a question about it.
- A requirement whose cases nearly all start from the same kind of input raises one question
  about the kind that is missing, unless that kind is the corpus's own subject.
- A requirement with no clause, or with no labelled case, raises a blocking question; every
  other question is advisory.

## Cases
CASE-1 — a hedge word is questioned by name
  Given  a clause reading "the gate reports errors quickly"
  When   the detectors run
  Then   one question names "quickly" and asks for the measurable threshold

CASE-2 — a bare number is questioned, an identifier is not
  Given  one clause reading "retries 3 times" and one reading "emits CASE-2 for v4.0.0"
  When   the detectors run
  Then   the first raises a missing-unit question and the second raises none

CASE-3 — a happy-path-only acceptance raises the failure question
  Given  a requirement whose cases mention no invalid, missing or failing input
  When   the detectors run
  Then   one question asks what happens on the failure path

CASE-4 — no clause or no case is blocking
  Given  a requirement with an empty Description, and one with no labelled case
  When   the detectors run on each
  Then   each raises a question of severity blocking

CASE-5 — cases that all start from one kind of input are questioned
  Given  a requirement whose every case opens on the same noun, and a corpus in which that
         noun is not the subject every other requirement starts from
  When   the detectors run
  Then   one question names that noun and asks which other kind a caller would supply

CASE-6 — the corpus's own subject is not that signal
  Given  a corpus in which nearly every case of every requirement starts from the same noun
  When   the detectors run on one of them
  Then   no question is raised about it, because the noun is the domain, not a narrow focus

## Context
**Fire rate, measured 2026-09-04**
- Over this repository's 223 requirements, `case-monoculture` fires on 20 — 8.9% of the corpus,
- above the 5% floor [[ARCH-REDUNDANCY-058]] was weighed against. Without excluding the corpus's
- own subject word it fires on 38 (17%), and 60% of those are requirements about requirements:
- the exclusion is what turns the signal from noise into a question.
- It is the detector that would have asked the question nobody asked about `search`, whose four
- cases each varied the quality of one kind of input and never its kind.

---
id: REQ-CLARIFY-957
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CLARIFY-062]
---

# Reporting the open questions

## Description
> A list of questions is only useful if the reader can see which one to answer first and
> where it came from. The text form quotes the clause it is about; the JSON form is what an
> agent answers against.

Every bullet below is binding.
- `clarify <ID>` prints the questions for that requirement, blocking ones first, each with its
  rule name, its location, the clause it quotes, and a suggested shape of answer.
- `clarify` with no id reports only the blocking questions across the corpus, so a large corpus
  answers "what is unimplementable right now".
- `--json` emits the same records as `{engine_version, advisory, requirements}` and prints
  nothing else.
- An unknown id exits 1 so a typo is visible; every other run exits 0 and writes no file.

## Cases
CASE-1 — questions are printed with their rule and quote
  Given  a requirement with one hedge-word clause
  When   `clarify <ID>` runs
  Then   the output carries the rule name, the clause text and a suggestion line

CASE-2 — the corpus view is blocking-only
  Given  one requirement with a blocking question and one with only advisory questions
  When   `clarify` runs with no id
  Then   only the first requirement appears

CASE-3 — JSON carries the same records
  Given  any requirement
  When   `clarify <ID> --json` runs
  Then   stdout parses as JSON holding that requirement's questions

CASE-4 — an unknown id is an error, an answered requirement is not
  Given  an id that does not exist, and a requirement with no detectable question
  When   `clarify` runs on each
  Then   the first exits 1 and the second exits 0
