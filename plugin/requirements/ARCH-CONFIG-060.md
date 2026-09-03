---
id: ARCH-CONFIG-060
status: confirmed
level: architecture
layer: bus
owner: Alex
priority: should-have
milestone: v3.3
depends_on: [ARCH-PARSE-001]
satisfies: [SYS-AUTHOR-101]
---

# Per-repo configuration file

## Description
> Every threshold the engine judges by (`LINT_AC_MAX`, `SIMILAR_THRESHOLD`,
> `ORPHAN_CODE_MIN_LOC`, ...) was a module constant, so a consumer could change none of
> them without forking `reqmap.py`. A small JSON file next to the requirements sets the
> named constants at startup, read fail-open, so a repo tunes the engine without
> rewiring it.

Every bullet below is binding.
- `requirements/_config.json` overrides the constants named in `CONFIG_KEYS` and extends the scanned extensions; a missing, malformed or wrongly-typed entry never breaks a command. [[REQ-CONFIG-949]]

## Cases
CASE-1
  Given  a `requirements/_config.json` setting `LINT_AC_MAX` to 12
  When   any command starts
  Then   `lint` and `next` judge oversize at 12 criteria

CASE-2
  Given  a config file that is not valid JSON
  When   any command starts
  Then   the defaults apply and the command runs

CASE-3
  Given  a config key the engine does not know
  When   any command starts
  Then   one line on stderr names the ignored key and nothing else changes

--------------------


---
id: REQ-CONFIG-949
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-CONFIG-060]
---

# Reading and applying `_config.json`

## Description
> `load_config` reads the file; `apply_config` sets module constants from it. The split
> keeps the file format and the application rules testable on their own, and `main`
> calls both once before any command runs. A silently-ignored typo would be worse than
> no config at all, so an unknown or mistyped key is reported.

Every bullet below is binding.
- `load_config(reqs_dir)` returns the parsed object from `requirements/_config.json`, or `{}` when the file is absent, unreadable, not JSON, or not a JSON object.
- `apply_config(cfg)` sets each key named in `CONFIG_KEYS` on the module and returns the list of names it applied.
- A numeric constant accepts a number of the same kind; a dictionary constant such as `LINT_FANOUT_BANDS` is merged key by key, a JSON list becoming a tuple.
- `extra_code_exts`, a list of extensions with or without the leading dot, is appended to `CODE_EXTS`, so every scan site sees the new file types.
- A key not in `CONFIG_KEYS`, or a value of the wrong type, is reported on stderr as `config: ignoring ...` and skipped; every other key still applies.
- `main` calls `apply_config(load_config(reqs_dir))` before loading requirements or scanning, so every command reads the configured values.

## Cases
CASE-1 — a numeric threshold applies
  Given  `{"LINT_AC_MAX": 12}`
  When   `apply_config` runs
  Then   it returns `["LINT_AC_MAX"]`, the constant reads 12 and stderr stays empty

CASE-2 — unknown and mistyped keys are reported and skipped
  Given  `{"NOPE": 1, "LINT_AC_MAX": "seven"}`
  When   `apply_config` runs
  Then   nothing is applied, the constant keeps its default and stderr names both keys

CASE-3 — dictionaries merge and extensions extend
  Given  `{"LINT_FANOUT_BANDS": {"system": [null, 12]}, "extra_code_exts": ["foo", ".bar"]}`
  When   `apply_config` runs
  Then   the `system` band reads `(None, 12)`, the `architecture` band is unchanged and `x.foo` counts as a code file

CASE-4 — the file is read fail-open
  Given  no file, a malformed file, a JSON list, and a valid object in turn
  When   `load_config` reads each
  Then   it returns `{}` for the first three and the object for the last
