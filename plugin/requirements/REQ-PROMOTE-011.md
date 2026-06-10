---
id: REQ-PROMOTE-011
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
superseded_by:
milestone: v1.08
---

# promote

> A requirement starts life as a draft and only becomes official once a human has reviewed it. This
> command performs that sign-off in one step: it marks the requirement as `confirmed`, but first checks
> that it actually points at real code and warns if no test is linked. Doing this by hand means editing
> the file's header directly, which is easy to get subtly wrong; this command does it safely every time.

## WHAT — Contract (normative)
- `promote <ID>` shall set the requirement's `status` to `confirmed` by editing only the value of the first `status:` line in its leading frontmatter block, preserving indentation and any trailing inline comment, and leaving the body untouched.
- It shall refuse (non-zero exit, no write) when the requirement has no `implements:` member, because a `confirmed` requirement with no code is a gate error; it shall print the tag to add.
- It shall be idempotent: a requirement already `confirmed` is reported and left unchanged (exit 0).
- It shall warn (without failing) when no `tested-by:` member is linked, pointing at the test tag or the `test_exempt:` opt-out, and shall remind the caller to re-lock + regenerate the map.
- Unknown id (no `requirements/<ID>.md`) shall exit non-zero with a clear message.

## WHAT — Verify intent (open questions for the human)
- None — behavior is fully specified by the acceptance criteria below.

## WHAT — Notes & known limitations (informative)
- `promote` does not itself run `check --update-lock`; the drift lock must be refreshed afterward so the newly-enforced contract is baselined (the command prints this reminder).

## HOW — Acceptance (= tests)
AC-1
  Given  a baseline requirement with an `implements:` member
  When   `promote <ID>` runs
  Then   its frontmatter `status` becomes `confirmed`, the body is byte-identical, and exit is 0

AC-2
  Given  a requirement with no `implements:` member
  When   `promote <ID>` runs
  Then   the file is unchanged, a "must point to code" message is printed, and exit is non-zero

AC-3
  Given  an already-`confirmed` requirement
  When   `promote <ID>` runs
  Then   the file is unchanged and exit is 0

AC-4
  Given  a status line carrying a trailing `# comment`
  When   `promote <ID>` runs
  Then   the comment is preserved and only the status value changed

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana has finished reviewing a draft requirement that already has code behind it. She runs `reqmap.py promote AUTH-LOGIN-001`: its status flips to `confirmed`, the rest of the file is untouched, and it reminds her to refresh the drift lock. When she tries the same on a requirement with no code yet, it refuses, leaves the file alone, and tells her exactly which `implements:` tag to add first.

## WHERE — Current implementation
- plugin/scripts/reqmap.py (`cmd_promote`, `_set_frontmatter_status`)

## Links
- Used by: (auto)
## Members in code (auto)
