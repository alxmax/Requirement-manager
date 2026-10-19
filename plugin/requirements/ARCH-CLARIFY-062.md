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
- `clarify` raises no question from a word found only inside another word, from a clause that hands its cases to another requirement, or from a clause quantified over "all", "every", "any"; it asks for a split only where `lint` warns over-scoped. [[REQ-CLARIFY-1102]]

## Cases
CASE-1 — a requirement with nothing detectable says so
  Given  a requirement whose clauses carry no hedge, no bare number and a case per clause
  When   `clarify` runs on it
  Then   it reports nothing unclear and points at `gate --show <ID>`

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
- A number in a clause raises no question: whether it needs a unit is the reader's call.
- A clause that opens with "It" or "The system" as its subject raises a question asking which
  component acts; "the system" later in a clause names a thing, not the actor, and raises none.
- A requirement with more clauses than cases raises ONE question naming both counts and
  asking whether each clause has a case that proves it. It never states how many clauses
  are uncovered, since one case may prove two clauses, and it never accuses a clause by
  position: it compares two numbers and never reads a case, so pointing at the tail
  clauses was a guess — wrong whenever an early clause is the uncovered one, such as a
  clause that delegates its cases to another requirement. A requirement whose cases never
  mention a failure path raises a question about that, unless it is a stakeholder need
  (`layer: need`), which is one story with one Scenario.
- A requirement whose cases nearly all start from the same kind of input raises one question
  about the kind that is missing, unless that kind is the corpus's own subject. The question
  says how many of the Given lines open on that word, never that every case does.
- A requirement with no clause, or with no labelled case, raises a blocking question; every
  other question is advisory.
- A deprecated requirement raises no question at all: it is retired, so nothing in it
  waits for an answer.

## Cases
CASE-1 — a hedge word is questioned by name
  Given  a clause reading "the gate reports errors quickly"
  When   the detectors run
  Then   one question names "quickly" and asks for the measurable threshold

CASE-2 — a number is not questioned
  Given  one clause reading "retries 3 times", one reading "turns amber below 60" and one
         reading "prints the list and exits 2"
  When   the detectors run
  Then   none of them raises a question

CASE-3 — a clause-against-case gap and a happy-path-only acceptance are questioned
  Given  a requirement with five clauses and two cases, none mentioning invalid, missing
         or failing input
  When   the detectors run
  Then   one question names 5 clauses and 2 cases and asks whether each clause is proven,
         without claiming a number of uncovered clauses or naming one, and one asks
         what happens on the failure path; the same happy path at `layer: need` is not
         asked about the failure path

CASE-4 — no clause or no case is blocking
  Given  a requirement with an empty Description, and one with no labelled case
  When   the detectors run on each
  Then   each raises a question of severity blocking

CASE-5 — cases that all start from one kind of input are questioned, unless it is the domain
  Given  a requirement whose cases open on the same noun three times in four, once in a
         corpus where that noun is rare and once in a corpus where nearly every case starts
         from it
  When   the detectors run
  Then   the first says 3 of 4 Given lines open on that noun and asks about the other kinds
         of input a caller can supply, and
         the second raises no such question, because the noun is the domain

CASE-6 — an unnamed actor is questioned, a noun is not
  Given  a clause reading "It scans all files when the input is missing.", and one reading
         "Every draft declares `satisfies:` the system placeholder."
  When   the detectors run
  Then   only the first raises a question asking which command or component performs it

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

**Retired 2026-10-18**
- `number-without-unit`, which asked for a unit beside a bare number, is retired
  ([ADR-0075](../../docs/adr/0075-clarify-retires-number-without-unit.md)): none of the 9
  questions it asked on this corpus was real ("at line 1", "a score of 2", "4 Mermaid code
  blocks").

**Narrowed 2026-10-19**
- `vague-term` no longer asks about "several", "many", "various", "small" or "large"
  ([ADR-0078](../../docs/adr/0078-clarify-vague-term-drops-quantity-words.md)): they were 23
  of its 27 questions here, and 1 of 20 sampled questions was real, on "best-effort".
  [[REQ-CLARIFY-1102]] states that the words ask nothing.

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
> Clarifying a requirement means editing it, and an edit is new text: it can drop the last
> clause or the last case, leaving nothing to implement or nothing to prove. Nobody re-reads
> the whole corpus after an edit, so the loss sits unread. `sync` runs after every edit
> anyway, which makes it the one place the comparison costs nothing. Only the two blocking
> rules are tracked: an advisory question is read with `clarify`, never reported here.

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
CASE-1 — a requirement recorded with no question, then given one, is reported
  Given  a requirement synced once with no blocking question, then edited so one fires
  When   `sync` runs
  Then   it names that requirement as having a new question

CASE-2 — an unchanged or reworded question is not re-reported
  Given  a requirement whose blocking question is the same rule as at the last sync, once
         unchanged and once after its clause is reworded
  When   `sync` runs
  Then   nothing is reported as new either time

CASE-3 — a new requirement's questions are not reported as new
  Given  a requirement that has never been in the snapshot
  When   `sync` runs
  Then   its questions are not reported as new

CASE-4 — only the rule that is new is named
  Given  a requirement recorded with `no-cases`, then edited so `no-contract` also fires
  When   `sync` runs
  Then   it names `no-contract` as new and does not name `no-cases`

CASE-5 — a corrupt snapshot fails open
  Given  a `_clarifylock.json` that is not valid JSON, and a requirement with a blocking
         question
  When   `sync` runs
  Then   it does not crash and reports nothing as new

CASE-6 — reporting a new question never changes the exit code
  Given  the same tree synced once with a snapshot that makes a question new and once
         with no snapshot at all
  When   `sync` runs
  Then   both runs exit with the same code

CASE-7 — an advisory question is not tracked
  Given  a requirement synced once with no question, then edited so a clause says "quickly"
  When   `sync` runs
  Then   nothing is reported as new

--------------------


---
id: REQ-CLARIFY-1100
status: confirmed
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
  `suggest`, in the order `clarify` prints them. The map computes them with the same
  function `clarify` runs, so the two never disagree about a requirement.
- Every record names the `basis` its rule rests on: `structure` when a section is absent
  (`no-contract`, `no-cases`), `count` when two numbers disagree and the disagreement is the
  finding (`over-scoped`), and `wording` when the question is a guess: a word on a list
  matched, or a count that never reads a case (`clause-without-case`, every other rule).
  `clarify` prints the basis beside the rule.
- The list holds blocking and advisory questions alike; filtering is the reader's
  choice.
- A requirement with nothing unclear carries an empty list, never an absent field.

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
  Then   `no-cases` carries basis `structure`, `vague-term` and `clause-without-case`
         carry basis `wording`, and only `over-scoped` rests on `count`

--------------------


---
id: REQ-CLARIFY-1102
status: confirmed
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
- A hedge counts only as a whole word outside a code span.
- A word that counts or sizes (`several`, `many`, `various`, `small`, `large`) raises no
  question: in a requirement it nearly always means "more than one" or is sized in the same
  clause.
- A clause that ends by naming another requirement (`… [[ID]]`) hands its cases to that
  requirement, so neither the clause-against-case count nor the over-scoped count holds it.
- A clause quantified over "all", "every" or "any" raises no question: in a requirement the
  words nearly always range over a finite set the engine already owns.
- A requirement is over-scoped only on `lint`'s own measure: more than `LINT_CONTRACT_MAX`
  clauses of its own and more than `LINT_AC_MAX` cases, so `clarify` never asks for a split
  that `lint` does not warn about.

## Cases
CASE-1 — a hedge is a whole word outside code
  Given  clauses reading "the fastest path" and "words such as `appropriate`", and one
         reading "replies quickly"
  When   the detectors run
  Then   only the last raises a vague-term question

CASE-2 — a clause that hands its cases on is not counted
  Given  a requirement with nine clauses ending in `[[ID]]`, one clause of its own and
         one case, and another with two clauses of its own and one case
  When   the detectors run
  Then   the first raises neither a clause-without-case nor an over-scoped question, and
         the second still raises clause-without-case

CASE-3 — all, every and any ask nothing
  Given  a clause reading "`gate` reads every file, all tags and any requirement."
  When   the detectors run
  Then   no question is raised

CASE-4 — a split is asked only where lint warns
  Given  requirement A with eight clauses, four cases; requirement B with eleven clauses,
         eight cases
  When   the detectors run and `lint` runs
  Then   only B raises an over-scoped question, and `lint` warns `over-scoped` on B too

CASE-5 — counting and sizing words ask nothing
  Given  clauses reading "binds several requirements", "may hold many requirements", "keeps
         one small record", "for a large corpus" and "reads various formats"
  When   the detectors run
  Then   none raises a vague-term question
