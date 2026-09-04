---
id: ARCH-IMPLEMENT-063
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v4.0
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002, ARCH-SIMILAR-016, ARCH-CLARIFY-062]
satisfies: [SYS-GATE-102]
---

# The brief for implementing a requirement

## Description
> Between a written requirement and working code there is a gap every agent fills by
> guessing: which tags to carry, where this kind of code lives in this repo, what proves it
> landed. `implement` states all of it in one place, from facts the engine already holds. It
> writes no code — a deterministic tool can own the contract and the verdict, never the
> authorship — and it says so, so nobody waits for it to.

Every bullet below is binding.
- `implement` emits one requirement's obligations, cases, existing members, unanswered questions and the exact tags its code carries. [[REQ-IMPLEMENT-958]]
- `implement` names the requirements most similar to it that already have code, so the brief points at where this kind of work lives in this repository. [[REQ-IMPLEMENT-959]]

## Cases
CASE-1 — the brief carries the tags verbatim
  Given  a requirement with three labelled cases
  When   `implement` runs on it
  Then   the output holds `# implements: <ID>` and one `# verifies: <ID>#CASE-N` per case

CASE-2 — unanswered blocking questions are stated before the work starts
  Given  a requirement with no labelled case
  When   `implement` runs on it
  Then   the brief opens with that blocking question and names `clarify`

CASE-3 — the brief writes nothing
  Given  any requirement
  When   `implement` runs
  Then   no file in the repository changes

---
id: REQ-IMPLEMENT-958
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-IMPLEMENT-063]
---

# What the implementation brief states

## Description
> The brief is the requirement plus the four facts a writer of code needs and would
> otherwise reconstruct by reading the repository: what already implements it, what is still
> unanswered, what tags bind the new code, and what command proves the result.

Every bullet below is binding.
- The brief carries the requirement's id, title, status, level, layer, intent, obligations and
  cases as authored.
- The brief lists the requirement's existing members with role and location, and says plainly
  when there are none.
- The brief carries the open questions from the same detectors `clarify` uses, blocking ones
  named first.
- The brief states the literal tag lines the new code carries: one `implements:`, one
  `tested-by:`, and one `verifies:` per labelled case.
- The brief names the verification command, and states that the requirement is not to be edited
  to match the code.
- `--json` emits the whole brief as one object; an unknown id exits 1.

## Cases
CASE-1 — a requirement with no code says so
  Given  a requirement carrying no member
  When   `implement` runs
  Then   the members section says there is nothing yet

CASE-2 — one verifies tag per labelled case
  Given  a requirement with cases CASE-1 and CASE-2
  When   `implement` runs
  Then   exactly two `verifies:` tag lines are emitted, one per label

CASE-3 — the JSON brief is one object with the same fields
  Given  any requirement
  When   `implement <ID> --json` runs
  Then   stdout parses as JSON carrying contract, cases, members, tags and open_questions

---
id: REQ-IMPLEMENT-959
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-IMPLEMENT-063]
---

# Pointing at where this kind of code lives

## Description
> "Where do I put it?" is the question a brief cannot answer from the requirement alone, and
> the engine knows nothing about the host project's layout. It does know which requirements
> read alike, and requirements that read alike are implemented next to each other far more
> often than not — so the neighbours' files are the honest answer, offered as a hint.

Every bullet below is binding.
- The brief names up to two requirements most similar to this one, ranked by the same TF-IDF
  cosine `search` and `dupes` use.
- Only requirements that already carry members are offered, and each is listed with the files
  its members live in.
- A requirement with no similar neighbour, or a corpus where nothing has members, produces no
  neighbours section rather than an empty one.

## Cases
CASE-1 — the nearest implemented requirement is offered with its files
  Given  a corpus where one other requirement shares most of its contract vocabulary and has members
  When   `implement` runs
  Then   that requirement is named, with a score and the files of its members

CASE-2 — a requirement with no implemented neighbour offers none
  Given  a corpus where no other requirement carries a member
  When   `implement` runs
  Then   no neighbour is named

CASE-3 — at most two neighbours are offered
  Given  a corpus where five other requirements are similar and carry members
  When   `implement` runs
  Then   two neighbours are named, the two ranked highest
