---
id: ARCH-SHOW-015
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002]
satisfies: [SYS-REPORT-105]
superseded_by:
milestone: v1.14
---

# Single-requirement dossier

> To understand one requirement today you open its file, then hunt through other files to
> see what depends on it and which code carries it out. This gathers all of that onto one
> screen: the title and intent, what it promises, what it depends on and what depends on it,
> where it lives in the code, any open questions, and any risk signals. Without it, answering
> "what does this do and where is it?" means cross-referencing several files by hand.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     the intent    the first blockquote in a requirement's body — its WHY.
     a member      a place in the code tagged as belonging to this requirement.
     reverse edge  a requirement that names this one in its own `depends_on`.
     risk signal   a warning the engine derives about a requirement, such as
                   "no test links to it", each paired with advice on what to do. -->

**What it is**
- `show <ID>` prints one consolidated, human-readable view of a single requirement.
- `show` writes nothing. It only reads and prints.

**What it prints**
- `show` prints a header line carrying the id, the status and the layer.
- The header appends `priority` after the layer when that field is present, then `milestone`.
- An absent optional field adds no empty segment to the header.
- `show` prints the title and the intent. A WHY spanning several `>` lines is gathered whole,
  never truncated to its first line.
- `show` lists the Contract bullets. When the requirement has no `## WHAT — Contract` section,
  `show` says so instead.

**What it links**
- `show` prints dependencies in both directions: the `depends_on` ids, and the reverse edges.
- `show` lists the code members grouped by role, each with its `file:line`. When no member is
  tagged, `show` says so.
- `show` prints the verification level beside a member whose `tested-by:` tag carries one.

**What it surfaces**
- `show` lists the open `## WHAT — Verify intent` questions, using the same filter as
  `findings`, so the "None" placeholder is skipped.
- `show` lists the risk signals with their advice, reusing the same `_risk_signals` source as
  `next` and the Risk tab, so the three never disagree.

**Exit code**
- `show` returns zero for a known id and a non-zero code for an unknown one, so a typo is
  visible to a caller or to CI.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The view is read-only and never edits the requirement. To change a status, use `confirm`; to change the contract, edit the file.
- The reverse-dependency list is computed by scanning every requirement's `depends_on` on each call. The corpus is small, so this is not cached.

## HOW — Acceptance (= tests)
AC-1
  Given  a known id
  When   `show` runs
  Then   it prints the id, status, and layer on the header line and returns zero

AC-2
  Given  a requirement with a `priority` field
  When   `show` runs
  Then   the priority value appears on the header line; given none, the header carries no
         empty priority segment

AC-3
  Given  an unknown id
  When   `show` runs
  Then   it prints a "no requirement with id" message and returns a non-zero code

AC-4
  Given  a requirement that another requirement depends on
  When   `show` runs
  Then   the depender's id appears under "Depended on by"

AC-5
  Given  a requirement with a tagged member
  When   `show` runs
  Then   the member's role and `file:line` appear under members

AC-6
  Given  a requirement with an open verify-intent bullet
  When   `show` runs
  Then   that bullet appears and a "None" placeholder bullet does not

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana picks up a ticket touching `ARCH-SCAN-002` and runs `reqmap.py show ARCH-SCAN-002`.
  One screen tells her its status and layer, what it promises, that three other requirements
  depend on it, and exactly which functions and `file:line` locations implement it — so she
  knows what she will affect before changing a thing. When she fat-fingers the id, `show`
  prints "no requirement with id" and exits non-zero, so the typo is caught, not silently passed.

## WHERE — Current implementation
- `cmd_show` in `reqmap.py` — looks the id up in the loaded requirements, then prints the header, intent, contract, both dependency directions, members, open verify-intent, and risk signals. It reuses `_bullets`, `_req_title`, `_as_list`, `_risk_signals` and `RISK_ADVICE`, so the view agrees with `next`, `findings`, and the map.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-SHOW-674
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show <ID> prints one consolidated, human-readable view of

> `show <ID>` prints one consolidated, human-readable view of a single requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-675
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show writes nothing. It only reads and prints

> `show` writes nothing. It only reads and prints.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-676
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show prints a header line carrying the id

> `show` prints a header line carrying the id, the status and the layer.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-677
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# The header appends priority after the layer when

> The header appends `priority` after the layer when that field is present, then
> `milestone`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-678
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# An absent optional field adds no empty segment

> An absent optional field adds no empty segment to the header.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-679
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show prints the title and the intent. A

> `show` prints the title and the intent. A WHY spanning several `>` lines is gathered
> whole, never truncated to its first line.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-680
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show lists the Contract bullets. When the requirement

> `show` lists the Contract bullets. When the requirement has no `## WHAT — Contract`
> section, `show` says so instead.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-681
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show prints dependencies in both directions: the depends_on

> `show` prints dependencies in both directions: the `depends_on` ids, and the reverse
> edges.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-682
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show lists the code members grouped by role

> `show` lists the code members grouped by role, each with its `file:line`. When no member
> is tagged, `show` says so.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-683
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show prints the verification level beside a member

> `show` prints the verification level beside a member whose `tested-by:` tag carries one.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-684
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show lists the open ## WHAT — Verify

> `show` lists the open `## WHAT — Verify intent` questions, using the same filter as
> `findings`, so the "None" placeholder is skipped.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-685
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show lists the risk signals with their advice

> `show` lists the risk signals with their advice, reusing the same `_risk_signals` source
> as `next` and the Risk tab, so the three never disagree.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SHOW-686
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SHOW-015]
superseded_by:
---

# Show returns zero for a known id and

> `show` returns zero for a known id and a non-zero code for an unknown one, so a typo is
> visible to a caller or to CI.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
