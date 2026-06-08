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

> To understand one requirement today you open its file, then hunt through other files to
> see what depends on it and which code carries it out. This gathers all of that onto one
> screen: the title and intent, what it promises, what it depends on and what depends on it,
> where it lives in the code, any open questions, and any risk signals. Without it, answering
> "what does this do and where is it?" means cross-referencing several files by hand.

## WHAT — Contract (normative)
- The `show <ID>` command shall print one consolidated, human-readable view of a single requirement. It writes nothing and is read-only.
- It shall print a header line with the id, status, and layer.
- When the requirement carries a `priority` field the header shall append it after the layer, and a `milestone` field after that.
- An absent optional field shall add no empty segment to the header.
- It shall print the title and the intent (the first blockquote of the body, gathered whole when the WHY spans several `>` lines, not truncated to the first line).
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
- Given a requirement with a `priority` field, when `show` runs, then the priority value appears on the header line; given none, the header carries no empty priority segment.
- Given an unknown id, when `show` runs, then it prints a "no requirement with id" message and returns a non-zero code.
- Given a requirement that another requirement depends on, when `show` runs, then the depender's id appears under "Depended on by".
- Given a requirement with a tagged member, when `show` runs, then the member's role and `file:line` appear under members.
- Given a requirement with an open verify-intent bullet, when `show` runs, then that bullet appears and a "None" placeholder bullet does not.

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana picks up a ticket touching `CORE-SCAN-002` and runs `reqmap.py show CORE-SCAN-002`.
  One screen tells her its status and layer, what it promises, that three other requirements
  depend on it, and exactly which functions and `file:line` locations implement it — so she
  knows what she will affect before changing a thing. When she fat-fingers the id, `show`
  prints "no requirement with id" and exits non-zero, so the typo is caught, not silently passed.

## WHERE — Current implementation
- `cmd_show` in `reqmap.py` — looks the id up in the loaded requirements, then prints the header, intent, contract, both dependency directions, members, open verify-intent, and risk signals. It reuses `_bullets`, `_req_title`, `_as_list`, `_risk_signals` and `RISK_ADVICE`, so the view agrees with `next`, `findings`, and the map.

## Links
- Used by: (auto)
## Members in code (auto)
