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

## Known bugs, by module (ADR-0080)

A repository can list its known bugs next to its requirements. Each module is one file,
`requirements/bugs/<module>.md`:

```markdown
# Bugs — Payments

| ID | Bug | Priority | Date | Where | Why it matters | Source |
|---|---|---|---|---|---|---|
| B1 | Refund is applied twice | P1 | 2026-11-02 | `pay.py:12` | Money leaves twice | ticket |
```

Priorities are `P0` critical, `P1` high, `P2` medium, `P3` low and `P4` minor; `*` marks an
estimate. An assistant is the usual way to add one, because it can read the code a report is
about; the skill tells it how, and a priority it chose keeps the `*` until a person edits the
row. By hand, use the **Bugs** tab under Problems in the map, or:

```bash
python scripts/reqmap.py sync --bug "Refund is applied twice" --module Payments --prio P1
python scripts/reqmap.py ask --bugs --module pay
python scripts/reqmap.py ask --bugs --prio P0,P1 --json   # for a script's own report
python scripts/reqmap.py sync --fix "Payments B12"        # closes it, see below
```

`sync --bug` writes in the shape already there: the module's file by its heading or its name
without an `NN_` prefix, the columns of its table, and the `##` section naming its priority,
such as `## Bugs P3-P4`. A new module is numbered when the files are. A title that reads like
one the module holds needs `--force`.

**A fixed bug leaves the list for a register**, `requirements/bugs/_fixed.md`, with the day it
was found, the day it was closed, its version and its commit. A commit does it: put a trailer
in the commit message and the next `sync` moves the row, with that commit's SHA and date and
the version file as it was then:

```text
Stop the double refund

Fixes-bug: Payments B12
```

`sync --fix ID` does the same by hand (`--commit`, `--version`), and `--note "why"` closes
without a fix, as `not a bug`. A number is never given twice, because the next one counts the
register. Since `sync` runs after the commit, the moved row lands in a later commit; a
repository that wants it at merge runs `sync` in its release workflow. Reverting a fix leaves
the bug closed, so add it again. Only files in `requirements/bugs/` are closed this way:
`BUG_SOURCES` files are never written. `BUG_REGISTER`, `BUG_REGISTER_COLUMNS` (keys `id`,
`title`, `module`, `prio`, `date`, `fixed`, `version`, `commit`, `note`) and
`BUG_FIX_TRAILERS` rename all three. The map's Bugs tab shows the register under **Fixed**,
with found against fixed by week and the median days to fix by priority. Pick a week, or
search, to list its bugs. Lists show 25 rows a page; the export prints them all.

Run `sync` afterwards to put it on the map. A repository that already keeps bugs in its own
Markdown tables declares them in `requirements/_config.json`. They are read and never
written, and the map stays stale until `sync` runs after one of them changes:

```json
{
  "BUG_SOURCES": ["docs/known-issues/*.md"],
  "BUG_COLUMNS": {"title": ["Issue"], "prio": ["Severity"]},
  "BUG_SKIP_SECTIONS": "(?i)fixed|resolved",
  "MAP_LANGUAGE": "ro"
}
```

A table with no id, title and priority column is skipped, and so is every table under a `##`
heading `BUG_SKIP_SECTIONS` matches, down to the next `##`. Without it, a "recently fixed"
table with the bug columns reads as open bugs. `MAP_LANGUAGE` (`en` or `ro`) is the language
the map opens in until a reader picks one, for the page's own labels. A row that cannot be
read is an `INPUT:bugs` warning. An open bug never fails the gate, whatever its priority, and
bugs never reach the drift lock.

The first `#` heading gives the module, and any date in brackets at its end applies to rows
with none:

| Heading | Module | Date |
|---|---|---|
| `# Known issues — Billing (15.03.2026)` | `Billing` | 2026-03-15 |
| `# Known issues — Stock - Orders` | `Orders`: the last dash with spaces around it wins | none |
| `# Known issues — Stock-Orders` | `Stock-Orders` | none |
| `# Billing` | `Billing` | none |
| no heading, in `billing-notes.md` | `billing-notes` | none |

Spellings that differ only in case, diacritics or punctuation are one module, shown as the
first one read. A bug's id is `<file stem>:<row id>`, so renaming a file changes the ids of
its bugs.

**Export PDF** in the Bugs tab opens the browser's print dialog on the list as filtered, with
every group open; choose "Save as PDF" there.

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
