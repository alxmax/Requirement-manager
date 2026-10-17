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
- `sync` snapshots each requirement's blocking questions, so an edit that answers one question and raises another is reported instead of sitting unread. [[REQ-CLARIFY-975]]
- The map carries every question `clarify` asks of each requirement, so the viewer shows them without running the engine. [[REQ-CLARIFY-1100]]
- `clarify` asks nothing of a value, a whole word it only contains, a clause that hands its cases to another requirement, or a clause quantified over "all", "every" or "any". [[REQ-CLARIFY-1102]]

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
milestone: v4.2
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
- The number after "exit", "exits" or "exit code" is a value, not a quantity, and raises
  no unit question.
- A clause whose subject is "It" or "the system" raises a question asking which component acts.
- A requirement with more clauses than cases raises ONE question naming how many are
  uncovered, and saying that a count cannot tell which. It never accuses a clause by
  position: it compares two numbers and never reads a case, so pointing at the tail
  clauses was a guess — wrong whenever an early clause is the uncovered one, such as a
  clause that delegates its cases to another requirement. A requirement whose cases never
  mention a failure path raises a question about that.
- A requirement whose cases nearly all start from the same kind of input raises one question
  about the kind that is missing, unless that kind is the corpus's own subject.
- A requirement with no clause, or with no labelled case, raises a blocking question; every
  other question is advisory.
- A deprecated requirement raises no question at all: it is retired, so nothing in it
  waits for an answer.

## Cases
CASE-1 — a hedge word is questioned by name
  Given  a clause reading "the gate reports errors quickly"
  When   the detectors run
  Then   one question names "quickly" and asks for the measurable threshold

CASE-2 — a bare number is questioned, an identifier is not
  Given  one clause reading "retries 3 times", one reading "emits CASE-2 for v4.0.0"
         and one reading "prints the list and exits 2"
  When   the detectors run
  Then   the first raises a missing-unit question and the other two raise none

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

CASE-7 — a deprecated requirement asks nothing
  Given  a deprecated requirement with no labelled case and a clause reading "quickly"
  When   the detectors run
  Then   no question is raised, blocking or advisory

## Context
**Fire rate, measured 2026-09-04**
- Over this repository's 223 requirements, `case-monoculture` fires on 20 — 8.9% of the corpus,
- above the 5% floor [[REQ-REDUNDANCY-058]] was weighed against. Without excluding the corpus's
- own subject word it fires on 38 (17%), and 60% of those are requirements about requirements:
- the exclusion is what turns the signal from noise into a question.
- It is the detector that would have asked the question nobody asked about `search`, whose four
- cases each varied the quality of one kind of input and never its kind.

**Retired 2026-10-17**
- `unbounded-quantity`, which asked for an upper bound wherever a clause said "all", "every"
  or "any", is retired ([ADR-0072](../../docs/adr/0072-retire-unbounded-quantity.md)): 1 of
  20 sampled questions was real. [[REQ-CLARIFY-1102]] states that the words ask nothing.

---
id: REQ-CLARIFY-957
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
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


--------------------


---
id: REQ-CLARIFY-975
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v5.6
satisfies: [ARCH-CLARIFY-062]
---

# An answer can raise a question the old text never had

## Description
> Clarifying a requirement means editing it, and an edit is new text: a clause that
> answers one question can introduce a vague term, a number with no unit, or a
> case with no failure path. Nobody re-reads the whole corpus after an edit, so the new
> question sits unread. `sync` runs after every edit anyway, which makes it the one place
> the comparison costs nothing.

Every bullet below is binding.
- `sync` records, per requirement, the RULES of its blocking open questions, in
  `requirements/_clarifylock.json`. **Requirements with no questions are recorded too**,
  so "absent from the snapshot" means "never seen" and nothing else. Otherwise a
  requirement going from zero questions to one would be mistaken for a new file and
  silenced, which is the case this check exists to catch.
- On the next `sync`, a rule present now and absent from the snapshot is reported as a
  NEW question, named with its requirement.
- **The rule is the fingerprint, not the prose.** Rewording a clause that still has the
  same defect is the same question, not a new one.
- **A requirement absent from the snapshot is not reported.** A newly-added requirement
  has no previous state, so all its questions would read as new, which is noise.
- The sidecar fails open: absent, corrupt, or written by a newer schema, it reads as
  empty and the run reports nothing rather than crashing.
- This is advisory. It never changes an exit code, because an unanswered question is a
  conversation, not a build failure.

## Cases
CASE-1 — an edit that raises a new question is reported
  Given  a requirement synced once, then edited so a new blocking rule fires
  When   `sync` runs
  Then   it names that requirement and the new rule, and the exit code is unchanged

CASE-2 — an unchanged question is not re-reported
  Given  a requirement whose blocking questions are the same as at the last sync
  When   `sync` runs
  Then   nothing is reported as new

CASE-3 — a new requirement's questions are not reported as new
  Given  a requirement that has never been in the snapshot
  When   `sync` runs
  Then   its questions are not reported as new

--------------------


---
id: REQ-CLARIFY-1100
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CLARIFY-062]
---

# The map carries what clarify asks

## Description
> `clarify` asks what a requirement's text leaves open, but its answers reached only the
> terminal and a snapshot of rule names. The viewer reads `_map.json` and nothing else,
> so it could not show a single one of them. Writing them into the map lets the viewer
> show them beside the questions a person wrote.

Every bullet below is binding.
- Every node in `_map.json` carries a `clarify` list: the records `clarify` emits for that
  requirement, each with `rule`, `severity`, `basis`, `where`, `quote`, `question` and
  `suggest`, in the order `clarify` prints them.
- Every record names the `basis` its rule rests on: `structure` when a section is absent
  (`no-contract`, `no-cases`), `count` when two numbers disagree (`clause-without-case`,
  `over-scoped`), and `wording` when a word on a list matched (every other rule).
  `clarify` prints the basis beside the rule.
- The list holds blocking and advisory questions alike; filtering is the reader's
  choice.
- A requirement with nothing unclear carries an empty list, never an absent field.
- The map and `clarify` compute the questions with the same function, so the two never
  disagree about a requirement.

## Cases
CASE-1 — a node carries the questions clarify prints, in order
  Given  a requirement whose clause says `quickly` and names a bare number
  When   the map is built
  Then   its node's `clarify` list equals what `clarify` computes for it, field for field

CASE-2 — nothing unclear is an empty list
  Given  a requirement with one plain clause and a failure-path case
  When   the map is built
  Then   its node's `clarify` list is empty

CASE-3 — a blocking question keeps its severity
  Given  a requirement with no case at all
  When   the map is built
  Then   its node's `clarify` list holds `no-cases` with severity `blocking`

CASE-4 — each question names the basis its rule rests on
  Given  a requirement with no case and a clause that says `quickly`
  When   the map is built
  Then   `no-cases` carries basis `structure`, `vague-term` carries basis `wording`,
         and only `clause-without-case` and `over-scoped` rest on `count`

--------------------


---
id: REQ-CLARIFY-1102
status: draft
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CLARIFY-062]
---

# What clarify does not mistake for a question

## Description
> Reading `clarify`'s questions one by one showed most of three rules were not questions:
> a unit asked of a date or an exit code, a hedge found inside "smaller" or "how many", and
> a missing case counted on a bullet that only points at the child carrying its cases.
> Each was a property of the rule, so the fix belongs in the rule, not in 82 edits to
> requirements that were already right. See
> [ADR-0071](../../docs/adr/0071-clarify-reads-values-and-delegation.md).

Every bullet below is binding.
- A hedge counts only as a whole word outside a code span, and "how many" asks for a count
  rather than hedging one.
- A number is a value, not a quantity, and raises no unit question when it sits inside a
  code span, is a date, a version or a code point such as `U+2028`, or follows "default",
  "exiting", "exits with code" or "the exit code stays".
- A unit may follow a hyphen or a plus sign (`12-character`, `3+ letters`), and `50,000` is
  one number.
- A clause that ends by naming another requirement (`… [[ID]]`) hands its cases to that
  requirement, so neither the clause-against-case count nor the over-scoped count holds it.
- A clause quantified over "all", "every" or "any" raises no question: in a requirement the
  words nearly always range over a finite set the engine already owns.

## Cases
CASE-1 — a hedge is a whole word outside code
  Given  clauses reading "how many criteria", "the smaller set" and "words such as
         `appropriate`", and one reading "keeps many entries"
  When   the detectors run
  Then   only the last raises a vague-term question

CASE-2 — a value is not a bare number
  Given  clauses naming `>=3.9`, a date, `U+2028`, "default 150", "exits with code 0",
         "12-character" and "50,000 characters", and one reading "amber below 60"
  When   the detectors run
  Then   only the last raises a missing-unit question

CASE-3 — a clause that hands its cases on is not counted
  Given  a requirement with nine clauses ending in `[[ID]]`, one clause of its own and
         one case, and another with two clauses of its own and one case
  When   the detectors run
  Then   the first raises neither a clause-without-case nor an over-scoped question, and
         the second still raises clause-without-case

CASE-4 — all, every and any ask nothing
  Given  a clause reading "`gate` reads every file, all tags and any requirement."
  When   the detectors run
  Then   no question is raised
