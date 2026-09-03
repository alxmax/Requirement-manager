---
id: ARCH-PROMOTE-011
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-AUTHOR-101]
superseded_by:
milestone: v1.08
---

# confirm

## Description
> A requirement starts life as a draft and only becomes official once a human has reviewed it. This
> command performs that sign-off in one step: it marks the requirement as `confirmed`, but first checks
> that it actually points at real code and warns if no test is linked. Doing this by hand means editing
> the file's header directly, which is easy to get subtly wrong; this command does it safely every time.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     frontmatter  the YAML block between the two `---` lines at the top of the file.
     a member     a place in the code tagged as belonging to this requirement.
     the lock     requirements/_reqlock.json — the saved fingerprint of every contract. -->

**What it edits**
- `confirm <ID>` sets the requirement's `status` to `confirmed`.
- `confirm` edits only the value of the first `status:` line in the leading frontmatter.
- `confirm` preserves that line's indentation and any trailing inline comment.
- `confirm` leaves the body untouched.

**When it refuses**
- `confirm` refuses a requirement with no `implements:` member: it exits non-zero and writes
  nothing. A `confirmed` requirement with no code is a gate error.
- `confirm` exempts a `need` and an `aggregate` from that rule, matching the gate. Both are
  covered by an edge rather than by a tag.
- `confirm` refuses an `aggregate` whose `depends_on` list is empty, because an aggregate
  with no dependency is an orphan.
- A refusal prints the tag the caller needs to add.
- `confirm` exits non-zero with a clear message for an unknown id, meaning no
  `requirements/<ID>.md` exists.

**What it warns about**
- `confirm` warns, without failing, when no `tested-by:` member is linked.
- That warning points at the test tag to add, or at the `test_exempt:` opt-out.
- `confirm` reminds the caller to refresh the lock and regenerate the map afterwards.

**Running it again**
- `confirm` is idempotent. An already-`confirmed` requirement is reported, left unchanged, and
  exits zero.

## Verify intent (open questions for the human)
- None — behavior is fully specified by the acceptance criteria below.

## Notes & known limitations (informative)
- `confirm` does not itself run `sync`; the drift lock must be refreshed afterward so the newly-enforced contract is baselined (the command prints this reminder).

## Cases (= tests)
CASE-1
  Given  a baseline requirement with an `implements:` member
  When   `confirm <ID>` runs
  Then   its frontmatter `status` becomes `confirmed`, the body is byte-identical, and exit is 0

CASE-2
  Given  a requirement with no `implements:` member
  When   `confirm <ID>` runs
  Then   the file is unchanged, a "must point to code" message is printed, and exit is non-zero

CASE-3
  Given  an already-`confirmed` requirement
  When   `confirm <ID>` runs
  Then   the file is unchanged and exit is 0

CASE-4
  Given  a status line carrying a trailing `# comment`
  When   `confirm <ID>` runs
  Then   the comment is preserved and only the status value changed

CASE-5
  Given  a `layer: need` requirement with no `implements:` member
  When   `confirm <ID>` runs
  Then   its status becomes `confirmed` and exit is 0

CASE-6
  Given  a `layer: aggregate` requirement with an empty `depends_on`
  When   `confirm <ID>` runs
  Then   the file is unchanged and exit is non-zero

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana has finished reviewing a draft requirement that already has code behind it. She runs `reqmap.py confirm AUTH-LOGIN-001`: its status flips to `confirmed`, the rest of the file is untouched, and it reminds her to refresh the drift lock. When she tries the same on a requirement with no code yet, it refuses, leaves the file alone, and tells her exactly which `implements:` tag to add first.

## WHERE — Current implementation
- plugin/scripts/reqmap.py (`cmd_promote`, `_set_frontmatter_status`)

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-567
status: confirmed
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm <ID> sets the requirement's status to confirmed

> `confirm <ID>` sets the requirement's `status` to `confirmed`.

Scenario: confirm rewrites the status field
  Given  a `draft` requirement carrying at least one `implements:` member
  When   `confirm <ID>` runs
  Then   that requirement's frontmatter reads `status: confirmed`

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-568
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm edits only the value of the first

> `confirm` edits only the value of the first `status:` line in the leading frontmatter.

Scenario: confirm rewrites the first status line only
  Given  a draft requirement whose body also contains the word "status:" in prose
  When   `confirm <ID>` runs
  Then   only the frontmatter's first `status:` line changes; the prose text is untouched

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-569
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm preserves that line's indentation and any trailing

> `confirm` preserves that line's indentation and any trailing inline comment.

Scenario: confirm preserves the status line's formatting
  Given  a frontmatter line `status: draft  # pending review`
  When   `confirm <ID>` runs
  Then   the line becomes `status: confirmed  # pending review`, comment and spacing intact

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-570
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm leaves the body untouched

> `confirm` leaves the body untouched.

Scenario: confirm never touches the body
  Given  a draft requirement with an `implements:` member
  When   `confirm <ID>` runs
  Then   every byte of the body after the frontmatter stays identical

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-571
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm refuses a requirement with no implements: member

> `confirm` refuses a requirement with no `implements:` member: it exits non-zero and
> writes nothing. A `confirmed` requirement with no code is a gate error.

Scenario: confirm refuses a requirement with no code
  Given  a requirement carrying no `implements:` member
  When   `confirm <ID>` runs
  Then   it exits non-zero, writes nothing, and prints that a `confirmed` requirement needs code

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-572
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm exempts a need and an aggregate from

> `confirm` exempts a `need` and an `aggregate` from that rule, matching the gate. Both
> are covered by an edge rather than by a tag.

Scenario: confirm exempts a need requirement from the implements rule
  Given  a `layer: need` requirement with no `implements:` member
  When   `confirm <ID>` runs
  Then   it succeeds and sets `status: confirmed` despite carrying no code tag

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-573
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm refuses an aggregate whose depends_on list is

> `confirm` refuses an `aggregate` whose `depends_on` list is empty, because an aggregate
> with no dependency is an orphan.

Scenario: confirm refuses an orphan aggregate
  Given  a `layer: aggregate` requirement whose `depends_on` list is empty
  When   `confirm <ID>` runs
  Then   it exits non-zero and the file is unchanged

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-574
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# A refusal prints the tag the caller needs

> A refusal prints the tag the caller needs to add.

Scenario: a refusal names the missing tag
  Given  a requirement with no `implements:` member
  When   `confirm <ID>` runs and refuses
  Then   its message names `implements:` as the tag to add

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-575
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm exits non-zero with a clear message for

> `confirm` exits non-zero with a clear message for an unknown id, meaning no
> `requirements/<ID>.md` exists.

Scenario: confirm rejects an id with no requirement file
  Given  an id with no `requirements/<ID>.md` on disk
  When   `confirm <ID>` runs
  Then   it exits non-zero and prints that the id is unknown

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-576
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm warns, without failing, when no tested-by: member

> `confirm` warns, without failing, when no `tested-by:` member is linked.

Scenario: confirm warns but still succeeds without a test link
  Given  a requirement with an `implements:` member and no `tested-by:` member
  When   `confirm <ID>` runs
  Then   it prints a warning, sets `status: confirmed`, and exits 0

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-577
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# That warning points at the test tag to

> That warning points at the test tag to add, or at the `test_exempt:` opt-out.

Scenario: the missing-test warning names the fix
  Given  a requirement confirmed with no `tested-by:` member
  When   `confirm <ID>` runs
  Then   its warning names the `tested-by:` tag to add, or the `test_exempt:` opt-out

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-578
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm reminds the caller to refresh the lock

> `confirm` reminds the caller to refresh the lock and regenerate the map afterwards.

Scenario: confirm reminds the caller to resync afterward
  Given  a requirement successfully confirmed
  When   `confirm <ID>` finishes
  Then   it prints a reminder to run `sync` and regenerate the map

## Members in code (auto)




--------------------


---
id: REQ-PROMOTE-579
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PROMOTE-011]
superseded_by:
---

# Confirm is idempotent. An already-confirmed requirement is reported

> `confirm` is idempotent. An already-`confirmed` requirement is reported, left unchanged,
> and exits zero.

Scenario: confirming twice is a no-op the second time
  Given  a requirement already `status: confirmed`
  When   `confirm <ID>` runs
  Then   the file is unchanged and exit is 0

## Members in code (auto)
