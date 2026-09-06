---
id: ARCH-ATOMICFORM-053
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.32
priority: should-have
depends_on: [ARCH-PARSE-001, ARCH-DRIFT-003, ARCH-CHECK-006]
satisfies: [SYS-AUTHOR-101]
---

# The atomic requirement form

## Description
> One obligation per file makes the clause the unit a test answers to, and removes the two headings that only restated each other.

Every bullet below is binding.
- A requirement stating a single obligation may be written as one `>` story blockquote plus
  one unlabelled `Scenario:` block, with no `## Contract` or `## Cases` heading at all — the
  file then carries the obligation and its proof and nothing else.
- The atomic form is detected from the body itself (a story quote immediately followed by a
  `Scenario:` block, both before the first `## ` heading), never from `form: atomic` in the
  frontmatter, so every consumer that only sees a body — the gate, the linter, the drift
  hash — agrees on whether a given file is atomic.
- `binding_hash` covers the story and the Scenario, never the empty string, so an atomic
  requirement drifts like any other when its wording changes.
- The linter treats a recognised atomic body as carrying both normative sections and one
  acceptance criterion (the Scenario), raising no missing-section, legacy-schema or
  under-specified finding — but it does check that every fact enumerated in the story has a
  matching `Then` line in the Scenario, and that the story does not grow past a fixed bullet
  ceiling.

## Cases
CASE-1 — an atomic body reads as both normative sections
  Given  a body whose only content before the first `## ` heading is a `>` story followed by
         a `Scenario:` block
  When   the gate and linter read it
  Then   both `## Contract` and `## Cases` count as present, and the Scenario counts as
         exactly one acceptance criterion

CASE-2 — the drift hash covers the statement and the Scenario
  Given  an atomic body
  When   `binding_hash` runs on it, and again after editing either the story or the Scenario
  Then   the hash is never the hash of the empty string, and each edit changes it

CASE-3 — a well-formed atomic requirement lints clean
  Given  a confirmed requirement with `form: atomic` and a recognised story + Scenario body
  When   the linter runs
  Then   it raises no finding

CASE-4 — a classic body with headings is never mistaken for atomic
  Given  a body using `## WHAT — Contract` and `## HOW — Acceptance` headings
  When   the atomic-form detector reads it
  Then   it returns no match, and every existing classic-form code path is unchanged

CASE-5 — a story fact with no matching Then line warns
  Given  an atomic story enumerating more `- ` facts than the Scenario has `Then` lines
  When   the linter runs
  Then   it warns `atomic-bullet-then-mismatch`; a story past the bullet ceiling instead
         warns `atomic-story-overlong`

