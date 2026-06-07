---
id: REQ-SHOW-015
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
milestone: v1.14
---

# Single-requirement dossier

> Print everything about one requirement in a single terminal view, so a reader answers "what does this do and where is it" without opening files.

## WHAT — Contract (normative)
- The `show <ID>` command shall print one consolidated, human-readable view of a single requirement. It writes nothing and is read-only.
- It shall print a header line with the id, status, and layer. When the requirement carries a `milestone` field, the header shall append it.
- It shall print the title and the intent line (the first blockquote of the body).
- It shall list the Contract bullets. When the requirement has no `## WHAT — Contract` section, it shall say so instead.
- It shall print dependencies in both directions: the `depends_on` ids, and the ids of requirements that depend on this one (the reverse edges).
- It shall list the code members grouped by role, each with its `file:line`. When no member is tagged, it shall say so.
- It shall list the open `## WHAT — Verify intent` questions, skipping the "None" placeholder, using the same filter as `findings`.
- It shall list the requirement's risk signals with their advice, reusing the same `_risk_signals` source as `next` and the Risk tab.
- It shall return zero when the id is found, and a non-zero code when the id is unknown, so a typo is visible to a caller or to CI.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- The view is read-only and never edits the requirement. To change a status, use `promote`; to change the contract, edit the file.
- The reverse-dependency list is computed by scanning every requirement's `depends_on` on each call. The corpus is small, so this is not cached.

## HOW — Acceptance (= tests)
- Given a known id, when `show` runs, then it prints the id, status, and layer on the header line and returns zero.
- Given an unknown id, when `show` runs, then it prints a "no requirement with id" message and returns a non-zero code.
- Given a requirement that another requirement depends on, when `show` runs, then the depender's id appears under "Depended on by".
- Given a requirement with a tagged member, when `show` runs, then the member's role and `file:line` appear under members.
- Given a requirement with an open verify-intent bullet, when `show` runs, then that bullet appears and a "None" placeholder bullet does not.

## WHERE — Current implementation
- `cmd_show` in `reqmap.py` — looks the id up in the loaded requirements, then prints the header, intent, contract, both dependency directions, members, open verify-intent, and risk signals. It reuses `_bullets`, `_req_title`, `_as_list`, `_risk_signals` and `RISK_ADVICE`, so the view agrees with `next`, `findings`, and the map.

## Links
- Used by: (auto)
## Members in code (auto)
