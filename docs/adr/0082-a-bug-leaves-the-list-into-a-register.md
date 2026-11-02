# ADR-0082 — A bug leaves the list into a register

- **Status:** Accepted. Supersedes the line of [ADR-0080](0080-known-bugs-are-listed-by-module.md)
  that says a fixed bug is removed and git holds the history, and answers that record's "close a
  bug without deleting it". Extends [ADR-0081](0081-what-a-first-bug-list-changed.md).
- **Decided:** 2026-11-02
- **Evidence:** a consumer moved a few hundred bugs into one file per module and ran the rest by
  hand: a register file, a rule that a number is never reused, a row moved in the fixing PR.
  `sync --bug` wrote a second file beside its numbered one, in English columns.

## Context

The list said what is open and nothing about what stopped being open. Git does hold a deleted
row, but no reader of the map can ask it when a bug was found, when it left, or in which
version. Numbers came from the rows still in the file, so a closed bug's number came back.

## Decision

- **A register, not a status.** A closed row moves to `requirements/bugs/_fixed.md`. The open
  files stay the list of what is open, and the reader needs no filter. A `Status` column,
  ADR-0080's guess, was rejected: every surface would then have to exclude closed rows.
- **`sync --fix` is a mode of `sync`, like `--bug`.** One call, one row. `--note` closes without
  a fix, so a dismissal is on record and is not counted as a fix.
- **A commit closes a bug with a trailer.** `Fixes-bug: FILE:REF` on the history of `HEAD`,
  read by `sync`. The fix and its record cannot drift apart, and a team without versions still
  has the commit.
- **No lock.** The feedback proposed `_buglock.json` to remember the last scanned commit. The
  register already says what is closed, so scanning with `git log --grep` is idempotent, and a
  lock would conflict on every merge and go wrong on a rebase.
- **A trailer that names nothing is a printed line, not a gate warning.** History cannot be
  edited, so a warning `--strict` promotes could never be cleared.
- **`sync --bug` writes the file's own shape.** It finds the module's file by heading or stem,
  uses the table's columns and joins the section of its priority. Both surfaces do this, so
  `_map.json` carries `bug_format` when a repository's format is not the default: a page cannot
  read `_config.json`.
- **`BUG_SOURCES` files stay read-only.** ADR-0080 holds. Files in `requirements/bugs/` are the
  engine's to write, a repository's own documents elsewhere are not, so closing a bug in one
  exits 2 and names the file.
- **Closing stays on the command line.** A page knows no commit and cannot run git, and a bug
  closed from it would carry neither. The page adds and reads.
- **A likely duplicate needs `--force`.** It compares titles with `difflib`: the corpus-wide
  TF-IDF in `similar.py` has no meaning over a few short titles in one file.

## Consequences

- A `sync` can change a bug file after the commit that asked for it, so the closing rows land in
  a later commit. A repository that wants them at merge runs `sync` in its release workflow.
- `sync --fix` without `--commit` records `HEAD`, the commit before any it is part of, and the
  version file as it stands, so a fix not yet released names the version before it. The trailer
  has neither problem. Use it, or pass `--version`.
- Reverting a fix leaves the bug closed. Add it again; it gets a new number.
- Renaming a file orphans its old ids, as ADR-0081 said, and an old trailer then prints a line on
  every `sync`.
- `CORE_LOGICAL_BUDGET` rises for the flags and the two call sites. `bugclose.py` stays lazy.

## Revisit when

- The printed line for an old trailer becomes noise: then a lock earns its conflicts.
- A team needs to close bugs from the page badly enough to give it a command to copy.
- Consumers keep open lists in `BUG_SOURCES` and want them closed: then that rule of ADR-0080 goes.
