---
id: ARCH-PYFLOOR-040
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: []       # ids of bus/other capabilities this builds on
satisfies: [SYS-SHIP-108]
superseded_by:       # <ID>, if replaced
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Declared Python support floor

## Description
> The engine's only promise to a new repo is "copy one file, run it with Python" — but
> which Python was never stated. It happened to work on 3.7 by accident, nothing tested
> that, and a user on an older interpreter met a stdlib AttributeError from deep inside
> a command instead of a sentence telling them what to do.
Every bullet below is binding.

**What it declares**
- `MIN_PYTHON` names the oldest interpreter version the engine supports.
- `MIN_PYTHON` equals the oldest version the CI test matrix runs, so the declared floor
  and the proven floor are the same number.

**What it does**
- `reqmap.py` refuses to run on an interpreter below `MIN_PYTHON`, before any command
  executes.
- `reqmap.py` exits 2 on refusal and prints one line naming the required version, the
  running version, and the fix.
- `_python_floor_error` reports the refusal message for a caller-supplied version, so a
  test pins the floor without spawning an old interpreter.

## Verify intent (open questions for the human)
- None — the floor is a stated decision, not an inference from code.

## Notes & known limitations (informative)
- The check cannot catch an interpreter below 3.6: the module uses f-strings, so such an
  interpreter fails at compile time and never reaches the guard. The covered range is
  3.6 through the version below `MIN_PYTHON`.
- The message is ASCII only, because a legacy Windows codepage is exactly where an
  outdated interpreter turns up.
- Raising the floor is a breaking change for a consumer repo and moves with the matrix,
  never ahead of it.

## Cases (= tests)
CASE-1
  Given  an interpreter older than `MIN_PYTHON`
  When   any `reqmap.py` command runs
  Then   it prints the required version, the running version and the fix, and exits 2

CASE-2
  Given  an interpreter at or above `MIN_PYTHON`
  When   any `reqmap.py` command runs
  Then   the floor check reports nothing and the command runs normally

CASE-3
  Given  the CI test matrix
  When   the `tests` job runs
  Then   its oldest Python entry equals `MIN_PYTHON`, on both Linux and Windows

## Example — in practice (optional, non-binding)
- A contributor on a distro Python 3.8 runs `python scripts/reqmap.py gate` and reads
  "reqmap needs Python 3.9 or newer (running 3.8)" instead of an `AttributeError`.

## WHERE — Current implementation
- `plugin/scripts/reqmap.py` — `MIN_PYTHON`, `_python_floor_error`, and the guard at the
  top of `main`.
- `.github/workflows/ci.yml` — the `tests` matrix that proves the floor on
  ubuntu-latest and windows-latest.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-PYFLOOR-603
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PYFLOOR-040]
superseded_by:
---

# MIN_PYTHON names the oldest interpreter version the engine

> `MIN_PYTHON` names the oldest interpreter version the engine supports.

Scenario: MIN_PYTHON names a concrete required version
  Given  the `reqmap.py` module
  When   `MIN_PYTHON` is inspected
  Then   it holds a specific version tuple such as `(3, 9)`, not a placeholder

## Members in code (auto)




--------------------


---
id: REQ-PYFLOOR-604
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PYFLOOR-040]
superseded_by:
---

# MIN_PYTHON equals the oldest version the CI test

> `MIN_PYTHON` equals the oldest version the CI test matrix runs, so the declared floor
> and the proven floor are the same number.

Scenario: MIN_PYTHON matches the CI matrix's oldest entry
  Given  `MIN_PYTHON` and `.github/workflows/ci.yml`'s `tests` job matrix
  When   both are compared
  Then   the matrix's lowest Python version equals `MIN_PYTHON`

## Members in code (auto)




--------------------


---
id: REQ-PYFLOOR-605
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PYFLOOR-040]
superseded_by:
---

# Reqmap.py refuses to run on an interpreter below

> `reqmap.py` refuses to run on an interpreter below `MIN_PYTHON`, before any command
> executes.

Scenario: an interpreter below the floor is refused before any command runs
  Given  `reqmap.py` started under an interpreter version below `MIN_PYTHON`
  When   `main()` runs
  Then   it refuses and returns before dispatching to any command

## Members in code (auto)




--------------------


---
id: REQ-PYFLOOR-606
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PYFLOOR-040]
superseded_by:
---

# Reqmap.py exits 2 on refusal and prints one

> `reqmap.py` exits 2 on refusal and prints one line naming the required version, the
> running version, and the fix.

Scenario: the refusal exits 2 and names both versions and the fix
  Given  an interpreter below `MIN_PYTHON`
  When   `reqmap.py` starts
  Then   it prints one line naming `MIN_PYTHON`, the running version and the upgrade fix, then
         exits 2

## Members in code (auto)




--------------------


---
id: REQ-PYFLOOR-607
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-PYFLOOR-040]
superseded_by:
---

# _python_floor_error reports the refusal message for a caller-supplied

> `_python_floor_error` reports the refusal message for a caller-supplied version, so a
> test pins the floor without spawning an old interpreter.

Scenario: _python_floor_error is testable without an old interpreter
  Given  a caller-supplied version tuple below `MIN_PYTHON`
  When   `_python_floor_error(version)` is called directly
  Then   it returns the same refusal message `reqmap.py` would print, with no interpreter
         spawned

## Members in code (auto)
