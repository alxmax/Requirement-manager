---
id: REQ-PROMOTE-011
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.08
---

# confirm

> A requirement starts life as a draft and only becomes official once a human has reviewed it. This
> command performs that sign-off in one step: it marks the requirement as `confirmed`, but first checks
> that it actually points at real code and warns if no test is linked. Doing this by hand means editing
> the file's header directly, which is easy to get subtly wrong; this command does it safely every time.

## WHAT — Contract (normative)
Every line in this section is binding.
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

## WHAT — Verify intent (open questions for the human)
- None — behavior is fully specified by the acceptance criteria below.

## WHAT — Notes & known limitations (informative)
- `confirm` does not itself run `sync`; the drift lock must be refreshed afterward so the newly-enforced contract is baselined (the command prints this reminder).

## HOW — Acceptance (= tests)
AC-1
  Given  a baseline requirement with an `implements:` member
  When   `confirm <ID>` runs
  Then   its frontmatter `status` becomes `confirmed`, the body is byte-identical, and exit is 0

AC-2
  Given  a requirement with no `implements:` member
  When   `confirm <ID>` runs
  Then   the file is unchanged, a "must point to code" message is printed, and exit is non-zero

AC-3
  Given  an already-`confirmed` requirement
  When   `confirm <ID>` runs
  Then   the file is unchanged and exit is 0

AC-4
  Given  a status line carrying a trailing `# comment`
  When   `confirm <ID>` runs
  Then   the comment is preserved and only the status value changed

AC-5
  Given  a `layer: need` requirement with no `implements:` member
  When   `confirm <ID>` runs
  Then   its status becomes `confirmed` and exit is 0

AC-6
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
