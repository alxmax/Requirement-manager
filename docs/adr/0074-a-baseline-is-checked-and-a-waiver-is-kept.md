# ADR-0074 — A baseline is checked before it is trusted, and a waiver is not recorded over a log that cannot keep it

- **Status:** Accepted. Amends the number in [ADR-0073](0073-mcp-values-stay-values.md), and
  leaves the baseline shape of [ADR-0003](0003-drift-baseline-shape.md) as it is.
- **Decided:** 2026-10-17
- **Evidence:** each case was reproduced on `main` at `edceb34` before any change, with the
  CLI against a one-requirement fixture, and each new test fails on that code and passes on
  this one. Six of the nine new tests fail there; the other three are controls, an absent or
  valid baseline staying quiet.
  - `init --minimal` over an edited `confirmed` contract kept it `confirmed`, advanced the
    lock, and wrote `reason: null` to the drift log: `init` calls the gate with its default,
    and the default was to accept.
  - A `null` where a hash belongs in `_reqlock.json` turned RM018 off. The same edit with a
    real hash reports RM018, and under `--strict` fails.
  - A `_memberlock.json` of schema 99 switched member drift off with no message.
  - `sync --accept-drift` over a `_driftlog.json` of schema 2 rewrote it as schema 1,
    dropping every waiver in it.
  - `python scripts/check_engine_budget.py` on this commit: core 6,694 logical lines.

## Context

Reading a baseline fails open, by design ([ADR-0003](0003-drift-baseline-shape.md)): a repository with none must still gate,
and a file from a newer engine must not crash an older one. That rule was written for the
absent file. It also covered the one that is there and cannot be used, which reads as empty,
and an empty baseline is one with no drift in it. Nothing said the signal was off.

Writing is another matter. A reader that fails open is harmless; a writer that starts from
what that reader returned throws away what the reader could not understand.

## Decision

- **`init` accepts no drift.** `cmd_check` no longer defaults to accepting it: the caller
  asks, and only `sync --accept-drift` does. `init` over an existing baseline demotes an
  edited confirmed contract as `sync` does and writes no waiver. The first `init` has no
  baseline, so nothing is drift.
- **RM016 names a baseline that exists and cannot be used.** It already named an unreadable
  `_reqlock.json`. It now also names a lock that holds an id with no hash (not text, or
  empty), and a `_memberlock.json` that is unreadable, of a schema this engine does not read,
  or not `{id: {file: hash}}`. It stays a warning, promoted under `--strict`. Reading still
  fails open; the rule says why. An absent baseline is first use and is not named.
- **A newer schema is reported like any other unusable baseline.** The alternative, to read
  it silently as empty, is how member drift was off with nothing saying so. A consumer pinned
  to an older vendored engine sees the warning until it updates, and sees it as an error only
  under `--strict`, which is the choice it made.
- **A waiver is refused over a log this engine cannot keep.** Before recording one, `sync` and
  `init` check that `_driftlog.json` can be rewritten without loss: valid JSON, an object, a
  schema no newer than the engine writes, an `accepted` that is an object. If not, the run
  prints why, reports `INPUT:driftlog`, exits 1 and changes none of the three baseline files
  or the status. The log is never migrated or repaired by this code.
- **An unchanged file is an engine upgrade only if the engine changed.** The exception that
  kept a confirmation when a lock hash moved under unchanged text (REQ-PROMOTE-974) now needs
  the map committed beside that lock to name an engine other than the running one. A lock
  committed with a contract edit it never took up leaves the same picture, a changed hash
  under an unchanged file, and used to be read as an upgrade. No map, an unreadable one, or
  the same engine is read as an edit.
- `CORE_LOGICAL_BUDGET` is 6,694. Forty-five lines are in `locks.py` (the shared JSON read,
  the baseline check and the log check), twelve in `gate.py`, and seven fewer in
  `rulesrepo.py`, where RM016's own check moved into `locks.py`.

## Consequences

- A repository whose `_memberlock.json` is schema 1, written by an older engine, gets an
  RM016 warning on its first `gate` after updating, until a `sync` rewrites it. The warning
  says so.
- The upgrade exception is as strong as the committed map: a repository that does not commit
  `_map.json` beside its lock never takes it, and demotes on the first `sync` after an
  engine upgrade, as it did before REQ-PROMOTE-974.
- `sync --accept-drift` can now exit 1 where it used to exit 0, on a log the engine cannot
  keep. The fix is the log: restore it, or remove it if its record is not wanted.

## Revisit when

- A consumer reports demotions after an upgrade that this check made, with the map committed.
- A cut on the gate path brings the measured core under 6,694.
