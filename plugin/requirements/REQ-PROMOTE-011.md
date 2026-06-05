---
id: REQ-PROMOTE-011
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001]
milestone: v1.08
---

# promote

> WHY: one command to perform the human-validation step — flip a reviewed requirement from baseline/draft to `confirmed` — instead of hand-editing frontmatter.

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

## WHERE — Current implementation
- plugin/scripts/reqmap.py (`cmd_promote`, `_set_frontmatter_status`)
