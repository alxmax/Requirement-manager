# Writing a requirement

[← back to the README](../README.md)


A requirement is just Markdown: a small YAML header plus prose. Trimmed example:

```markdown
---
id: AUTH-LOGIN-001
status: confirmed
layer: feature
depends_on: [CORE-SESSION-002]
milestone: v1.4          # optional — shows this requirement in the Roadmap tab
---

# User login

## Description
> Users need to reach their own data securely.

Every bullet below is binding.
- `login` accepts an email + password and returns a session token.
- `login` rejects an unknown email with a generic error (no user enumeration).

## Cases (= tests)
CASE-1  A valid email/password returns a token.
CASE-2  A wrong password returns the generic error.
```

The header carries the machine-readable bits (`id`, `status`, what it
`depends_on`); the prose explains intent and lists the acceptance criteria that
become your tests.

### Optional: the three specification levels

A requirement may also declare where it sits on the V-model's left arm, with
`level: system | architecture | code`, and name the level above it with
`satisfies:`. On a new repo, `init` writes all three rungs and those links;
every invented field is `status: draft` and `level_source: auto` so you can
rename, merge or delete the guesses. Neither field is required on a corpus you
authored by hand — a tree that sets neither behaves exactly as it did before
these fields existed. Adopt them and three checks switch on: the gate warns
(`RM032`) wherever the levels stop forming the tree below; `lint` reports a
parent with more children than its level allows — at most 10 under a `system`
requirement, at most 30 under an `architecture` one, and 5–20 under a parent
that declares no level (`LINT_FANOUT_BANDS`); and the gate reports a level whose
tests sit at the wrong depth (a `code` requirement is verified `@unit`, an
`architecture` one `@integration`, a `system` one `@system`).

**The levels form a tree, one parent each.** This repository's own corpus is
built this way:

```
SYS-SSOT-001                 the apex: why the product exists
├─ SYS-GATE-102              a sub-need: one per user group or business outcome
│  ├─ ARCH-CHECK-006         a capability: satisfies exactly one sub-need
│  │  ├─ REQ-CHECK-828       a behaviour group: satisfies exactly one capability
│  │  └─ REQ-CHECK-829
│  └─ ARCH-RULES-059
└─ SYS-READ-103
   └─ ARCH-PARSE-001
```

- A `code` requirement satisfies exactly one `architecture` requirement, and an
  `architecture` requirement exactly one `system` requirement. A second link is
  a `depends_on`, never a second parent.
- `system` requirements nest one deep: an apex, then sub-needs that satisfy it.
  Once the apex has sub-needs, every `architecture` requirement sits under the
  sub-need it serves, not under the apex.
- Choose the sub-needs the way you would explain the product to a stakeholder:
  one per group of users, or per business outcome. `init` writes a single
  placeholder need, `SYS-NEEDS-A-NAME-001`; with more than one area of work it
  becomes the apex, and the sub-needs go under it.

`RM032` warns on each break — two parents, a sub-need under a sub-need, a
capability on an apex that has sub-needs — on drafts as well, because a draft
is where a second parent is first written. It is a warning: the decision record
is [ADR-0064](adr/0064-the-level-axis-is-a-tree.md).

Both fields are prose about *this* corpus, so nothing forces an id to advertise
its level. This repo chooses to, because a reader meets an id long before its
file: `SYS-` for a system requirement, `ARCH-` for an architecture one, `REQ-`
for a detailed-design one. Your ids can say anything you like.

A single `.md` may hold **several** requirements — one frontmatter block each,
a block starting at a `---` line immediately followed by `id:`. That is how an
architecture requirement keeps its own detailed design in one document instead
of scattering it across dozens of files. A file with one block is read exactly
as before.

## Your own convention (ADR-0077)

A repository that already traces its code does not have to rewrite it. Three optional keys
in `requirements/_config.json` describe the convention it already uses; with none set,
nothing changes.

```json
{
  "TRACE_TAGS": [{"pattern": "\\\\trace\\{([A-Z0-9_]+)\\}", "role": "auto"}],
  "TEST_FILE_PATTERNS": ["**/*Test.cpp"],
  "REQUIREMENT_SOURCES": [
    {"glob": "modules/*/reqs/**/*.txt", "format": "text", "start": "^([A-Z][A-Z0-9_]+):"},
    {"glob": "specs/*.html", "format": "html", "start": "^\\s*([A-Z][A-Z0-9_]+)\\s",
     "status": "confirmed", "owner": "spec team"}
  ]
}
```

- **`TRACE_TAGS`** — extra tag forms. The pattern's first group is the requirement id. `role` is
  `implements`, `tested-by`, or `auto`: tested-by in a test file, implements anywhere else, so one
  form serves code and tests. The example reads `/// \trace{AB_CD12}`. In JSON a literal
  backslash is written `\\\\`.
- **`TEST_FILE_PATTERNS`** — globs that also make a file a test file, beside the built-in
  convention (`tests/`, `test_*.py`, `*_test.go`, …).
- **`REQUIREMENT_SOURCES`** — files that hold requirements, as `text`, `html` or `md`. For text
  and HTML, `start` matches the line a requirement starts on (its first group is the id); the
  requirement runs to the next such line, and each sentence is one clause. HTML is read as text
  first, so a table row with an id cell and a text cell is one requirement. `status` (default
  `confirmed`) and `owner` (default `external`) apply to the whole source.

A requirement read from text or HTML is not held to the Markdown format above: no section, case
or readability check. Every link check still applies: a tag to no requirement, a requirement with
no code or no test, and a changed text (drift). A bad entry is an `INPUT:config` warning (an error
under `--strict`), and a source that matches no file is an `INPUT:requirements` error.

## Glossary (the jargon, in plain words)

- **Capability / requirement** — one thing your app does, described in one file.
- **Single source of truth (SSOT)** — the one place the real answer lives, so
  there is nothing to keep in sync by hand.
- **Tag / membership** — the comment that links code to a requirement. Four
  roles exist: `implements`, `generated-from`, `validated-against`, `tested-by`.
  The list of members is discovered by scanning the code — never hand-maintained.
- **The gate** — the `gate` command; it fails when code and specs disagree.
- **Drift** — a requirement's contract changed but the code wasn't re-checked.
  The tool spots this by hashing the spec and comparing it to a saved baseline
  (`_reqlock.json`).
- **Layer (`bus` vs `feature`)** — `bus` is shared foundation that many things
  rely on; `feature` is built on top of the bus.
- **Dogfooding** — this repo uses the tool on itself: `plugin/requirements/`
  describes `reqmap.py`'s own capabilities, and its own gate passes with zero errors.
