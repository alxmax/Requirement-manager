---
id: ARCH-PIPE-046
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.9
depends_on: [ARCH-CMDREGISTRY-033]
satisfies: [SYS-QUALITY-104]
---

# A closed output pipe ends a command quietly

## Description
> `reqmap.py dupes | head` is the natural way to look at a long report. On Windows there
> is no SIGPIPE, so when `head` stops reading, the next `print` raises `OSError` and the
> command dies with a traceback the reader had nothing to do with. The first C/C++
> evidence run hit it on `curl` (2,055 pairs). A closed reader is not an error.

Every bullet below is binding.
- `_run_cli` ends a command with exit code 0 and no traceback when its standard output turns out to be a closed pipe. [[REQ-PIPE-893]]

## Cases
CASE-1
  Given  a command whose `print` raises `BrokenPipeError`, or `OSError` with `EPIPE`/`EINVAL`
  When   `_run_cli` runs it
  Then   it returns 0 and raises nothing

CASE-2
  Given  a command whose `print` raises any other `OSError`
  When   `_run_cli` runs it
  Then   that error propagates unchanged

CASE-3
  Given  a command that completes normally
  When   `_run_cli` runs it
  Then   the command's own exit code is returned

## Context
**Terms**
- *closed pipe*: the process reading the command's output has stopped reading (`head`, `less`, a closed terminal).

**Notes**
- Exit 0 on purpose: `dupes | head -12` ended early because the reader had seen enough,
  and a non-zero code there would fail a shell pipeline that did exactly what was asked.
- After the pipe closes, standard output is pointed at the null device so the interpreter
  does not print a second complaint while shutting down.

**Example**
`python -X utf8 scripts/reqmap.py dupes | head -12` on a 1,141-requirement corpus prints
twelve lines and exits 0 on Windows, instead of `OSError: [Errno 22] Invalid argument`.

**Current implementation**
- `_run_cli()` in `reqmap.py`, the `__main__` entry.

**Links**
- Sibling: [[ARCH-CMDREGISTRY-033]] (the command registry the entry point dispatches from).


--------------------


---
id: REQ-PIPE-893
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PIPE-046]
---

# A closed reader ends the command with exit 0

## Description
> `reqmap.py dupes | head` closes the pipe as soon as `head` has enough. On Windows that
> surfaces as `OSError` rather than `SIGPIPE`, and the command used to die with a traceback
> the reader had nothing to do with. `_run_cli` catches that specific failure and turns it
> into a quiet exit 0, so a normal shell pipeline never looks like a crash.

Every bullet below is binding.
- When the command's standard output turns out to be a closed pipe, `reqmap.py` ends
  the command, prints no traceback, and exits with code 0.
- `reqmap.py` treats `BrokenPipeError` and the Windows form of the same event
  (`OSError` with `EPIPE` or `EINVAL`) alike.
- Any other `OSError` still propagates unchanged. The rule covers a closed reader, not
  disk or permission errors.
- The rule lives in the command-line entry point (`_run_cli`), so every subcommand gets
  it and none re-implements it.

## Cases
CASE-1 — BrokenPipeError and its Windows OSError form both exit quietly
  Given  one run whose `print` raises `BrokenPipeError` and another whose `print` raises `OSError` with `errno` `EINVAL`
  When   `_run_cli` runs each
  Then   both return 0 without printing a traceback

CASE-2 — an unrelated OSError still propagates
  Given  a command whose `print` raises `OSError` with `errno` `ENOENT` (a missing file, not a closed pipe)
  When   `_run_cli` runs it
  Then   that `OSError` propagates instead of being swallowed

CASE-3 — a command that finishes normally returns its own exit code
  Given  a command function that returns 3, and one that returns `None`
  When   `_run_cli` runs each
  Then   it returns 3 and 0 respectively, unchanged by the pipe handling

