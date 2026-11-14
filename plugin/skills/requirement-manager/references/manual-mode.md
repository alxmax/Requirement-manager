# Manual mode: the conventions without the engine

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

Use this when the repository has no vendored engine (no `scripts/reqmap.py` with
`scripts/reqmap_engine/` beside it). You apply the same model by reading and editing
files. The [shared workflow](workflow.md) still holds for authoring rules, statuses,
the audience and the gate vocabulary; only its commands are unavailable.

## What manual mode cannot do

Say this to the user once, plainly, before the first manual verdict:

- **No drift lock.** The engine hashes each confirmed contract into `_reqlock.json` and
  compares on every run. Manual mode has no baseline, so "drift" means only what you
  can see in the diff or the git history of a requirement file.
- **No generated map.** `_map.md`, `_map.json` and the HTML viewer are engine output.
  Never write or hand-edit them; never write `_reqlock.json` or `_memberlock.json`.
- **No exhaustive scan.** You read the files you open. A tag in a file you did not read
  is a tag you did not check, so name the directories you covered.
- **Judgement, not a verdict.** A manual review blocks nothing and proves nothing about
  behaviour. It reports findings for a person to act on.

## The requirement file

One Markdown file per capability in `requirements/`, named after its id.
A capability is one behaviour that can fail on its own (see the shared workflow).

```markdown
---
id: AREA-NAME-NNN
status: draft
layer: feature
owner: <person>
depends_on: []
---

# Short name

## Description
> 1–3 plain sentences: what this is, why it exists, what breaks without it.

Every bullet below is binding.
- `<subject>` does one thing, stated so a test could check it.

## Verify intent (open questions for the human)
- One specific question only a person can answer.

## Cases
CASE-1
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Context (non-binding)
**Notes**
- Anything a reader should know that is not an obligation.
```

- Frontmatter holds scalars and inline lists only, with no comments and no empty keys.
  Optional keys: `priority`, `milestone`, `level` (`system` | `architecture` | `code`),
  `satisfies`, `superseded_by`.
- `status` is `draft`, `baseline`, `implemented`, `confirmed` or `deprecated`.
  Only a person sets `confirmed`, after reading the requirement.
- A confirmed requirement needs both `## Description` and `## Cases`, and at least
  one `implements:` member unless its layer is `need` or `aggregate`.

## The tags in code

Write each as a comment in the file's own comment syntax:

- `implements: AREA-NAME-NNN` on the code that carries the behaviour.
- `tested-by: AREA-NAME-NNN` on the test file, optionally ending `@unit`,
  `@integration` or `@system`.
- `verifies: AREA-NAME-NNN#CASE-1` on the test function that proves one case.
- `generated-from: AREA-NAME-NNN` on a derived document, so it is re-read when the
  requirement changes.

Keep the requirement edit and its tags in the same change.

## A manual gate

When the user asks for the gate, a review or a pre-commit check:

1. List `requirements/*.md`. Read each frontmatter; note ids, statuses and `depends_on`.
2. Search the code for the four tags (for example with your search tool, one pattern
   per tag). Skip vendored, generated and ignored paths.
3. Report in the engine's vocabulary, so the result reads the same as a real gate:
   - **ERROR RM001** a tag naming an id that no requirement has.
   - **ERROR RM003** a `depends_on` id that does not exist.
   - **ERROR RM006** a confirmed requirement with no `implements:` member.
   - **WARN RM012** a `tested-by:` file that is missing or holds no test function.
   - **WARN RM018 DRIFT** a confirmed contract changed in this diff while none of its
     members did. Name its direct dependents: they are the review blast radius.
   - **WARN** a confirmed requirement missing `## Description` or `## Cases`.
4. End with the count of errors and warnings, the directories you read, and the
   sentence "Manual review: no lock, no map, no exhaustive scan."

## Drafting from existing code

Read a file, name the behaviour it carries, and write one `status: draft`
requirement per behaviour. Put what you observed (a swallowed error, a magic
constant) under `## Verify intent` as an `Observed:` bullet. Never mark a draft
`confirmed`: intent comes from a person, never from the implementation.
