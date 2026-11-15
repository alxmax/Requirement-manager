# Intent triage — when the corpus is vibe-coded

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

A vibe-coded corpus is one where most requirements have `owner: auto` and none
(or very few) are `confirmed` — the requirements were auto-extracted from code
and never validated for intent. Triage surfaces what the project genuinely needs
vs. what the AI invented during extraction, before those inventions get promoted
to `confirmed` and start blocking real work.

**When to offer proactively**: when `reqmap.py gate --risk` shows `0 confirmed` and
the majority of requirements carry `owner: auto` in their frontmatter, offer
intent triage before any other action.

**The C/E/A framework:**

- **Core** — the tool cannot work without this. Remove it and users notice
  immediately. Candidate for `confirmed` after human review.
- **Emergent** — logically implied by Core capabilities; the AI added it as a
  natural extension. Useful but not essential. Keep as `baseline`.
- **Accidental** — the AI invented it during extraction; no user asked for it
  and removing it changes nothing visible. Deprecate and delete.

**Process:**

1. Read each requirement's `## Description` to the user in one sentence.
2. User says C, E, or A.
3. After classifying all: apply decisions in bulk.
   - Core → leave for human review; a human sets `status: confirmed` in the frontmatter.
   - Emergent → keep as `baseline`; no action needed.
   - Accidental → set `status: deprecated` in frontmatter; delete implementing
     code (check for load-bearing callers first with `grep` before deleting).
4. For Accidental code that IS still referenced: keep the code, strip the
   `implements:` tag, delete only the requirement file.
5. Run `reqmap.py sync` to verify.
