---
id: ARCH-CHECK-006
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.02
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002, ARCH-DRIFT-003]
satisfies: [SYS-GATE-102]
lint_exempt: [ac-count-high, over-scoped]
---

# The gate

## Description
> Specs rot when the code moves on and nobody updates the file that describes it.
> This is the guard that catches that: run before every commit, it fails the build when
> code and requirements no longer match. The whole tool exists so this check can run.

Every bullet below is binding.
- `gate` reports an `ERROR` and exits non-zero for a dangling tag, an invalid status/layer/form/level, a missing `depends_on` target, or an enforced requirement with no `implements:` member. [[REQ-CHECK-828]] details the behaviour.
- `gate` warns (not errors) on contract drift against the lock, a confirmed requirement with no `tested-by:` link, or a confirmed requirement missing its `## Description`/`## Cases` section; `--strict` promotes most of these to errors. [[REQ-CHECK-829]] details the behaviour.
- `gate` warns on a malformed `milestone:` value, and on a corrupt or git-untracked lock file, without affecting the exit code. [[REQ-CHECK-830]] details the behaviour.
- `gate` counts legacy-schema requirements in its summary and warns, without affecting the exit code, on an unvalidated confirmed need, a bus requirement tested only at `@system`, or a `depends_on` cycle. [[REQ-CHECK-831]] details the behaviour.
- `gate` prints the open verify-intent finding count and a summary of requirements, members, errors and warnings; neither affects the exit code. [[REQ-CHECK-832]] details the behaviour.
- With `--update-lock` — always passed by `sync` — `gate` writes the current binding hashes to `requirements/_reqlock.json`; the bare `gate` verb is otherwise report-only. [[REQ-CHECK-833]] details the behaviour.

## Cases
CASE-1
  Given  a tag referencing a non-existent capability
  When   `gate` runs
  Then   it produces an `ERROR` and exit 1

CASE-2
  Given  a `confirmed` requirement with no `implements` member
  When   `gate` runs
  Then   it produces an `ERROR`

CASE-3
  Given  an invalid status or layer, or a `depends_on` pointing at a missing id
  When   `gate` runs
  Then   each produces an `ERROR`

CASE-4
  Given  a `confirmed` requirement whose binding hash differs from the lock
  When   `gate` runs
  Then   it produces a `WARN` (not an error) naming the member `file:line` locations

CASE-5
  Given  a present-but-corrupt lock file
  When   `gate` runs
  Then   it produces a `WARN` and does not change the exit code

CASE-6
  Given  a requirement with a malformed `milestone:` (e.g. `next` or `1.14`)
  When   `gate` runs
  Then   it produces a `WARN`; a valid `v1.14`, an absent milestone, or a `deprecated`
         requirement produces none

CASE-7
  Given  a `confirmed` requirement with no `## Description` section
  When   `gate` runs
  Then   it produces a `WARN` and does not affect the exit code

CASE-8
  Given  a `confirmed` requirement with no `## Cases` section
  When   `gate` runs
  Then   it produces a `WARN` and does not affect the exit code

CASE-9
  Given  a `confirmed` requirement with both sections present
  When   `gate` runs
  Then   it produces no section-lint warning

CASE-10
  Given  a `confirmed` requirement with a `test_exempt: <reason>` and no `tested-by` member
  When   `gate` runs
  Then   it produces no test warning

CASE-11
  Given  a requirement without a `## Verify intent` section
  When   `gate` runs
  Then   it is counted as legacy-schema in the summary

CASE-12
  Given  an advancing run (`sync`, or the deprecated `check --update-lock`)
  When   it runs
  Then   the current hashes are written to `requirements/_reqlock.json`

CASE-13
  Given  a `_reqlock.json` (or `_memberlock.json`) present on disk but not git-tracked, inside a git work tree
  When   `gate` runs
  Then   it produces a `WARN` naming the file; once the file is tracked, or when run outside a git work tree, it produces none

CASE-14
  Given  two requirements whose `depends_on` fields point at each other
  When   the gate runs
  Then   it warns once, naming the chain, and the exit code stays 0

## Context
**Terms**
- the binding hash  the fingerprint of a requirement's normative sections; when it
- stops matching the lock, the contract has changed.
- drift             a contract whose text has moved on since the lock was written.
- the lock          requirements/_reqlock.json — the saved fingerprint of every
- contract. `_memberlock.json` is its sidecar.
- a need            a `layer: need` requirement: a stakeholder need other
- requirements fulfil, rather than code.

**Notes**
- Why `ac-count-high` and `over-scoped` are exempt: this requirement is the gate's severity
  table, not a bundle of checks. Each individual check the gate runs already has its own
  requirement ([[ARCH-TESTLINK-018]], [[ARCH-ACVERIFY-019]], [[ARCH-MEMBERDRIFT-027]],
  [[ARCH-DOCBUNDLE-026]], [[ARCH-ORPHANCODE-034]], [[ARCH-DRIFTIMPACT-035]]). What remains here
  is one behaviour — which condition is an ERROR, which is a WARN, and what that does to the
  exit code — so every clause and criterion shares a single failure mode. Splitting it would
  scatter the exit-code contract across files instead of clarifying it. Revisit this exemption
  if a clause ever lands here that is not about severity or exit code.
- Errors stop CI (exit 1); warnings do not. Intent sync (promote `baseline → confirmed`)
  is not automatable and surfaces at human review.
- When `CLAUDE_PLUGIN_ROOT` is set and the vendored engine is older than the installed
  plugin's copy, `gate` prints an advisory staleness notice (`warn_if_stale`); the
  variable is unset in CI, so the notice is silent and exit-neutral there. The CI half of
  that signal cannot live here — a stale engine does not contain the check that reports it
  stale — so it ships with the published action instead ([[ARCH-STALEENGINE-043]]).
- The dev-CI version-coherence script `scripts/check_versions.py` (repo root, never seeded
  into consumer repos) enforces plugin manifest alignment as the first step in this repo's
  own CI pipeline (`check_versions.py → gate → map --check → test_reqmap.py`). It is
  outside the plugin scan root and has no requirement of its own; its invariant (semver
  consistency across `plugin.json` + `marketplace.json`) is documented in `CLAUDE.md`.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana tags a function `# implements: AUTH-LOGIN-001`, but there is no such requirement
  file. She commits. The gate prints `ERROR: dangling tag` and exits non-zero, so the
  commit is blocked until she either fixes the typo or writes the requirement.
- Later she edits a confirmed requirement's contract text. Next commit, the gate warns
  `DRIFT — contract changed since lock`, reminding her to re-check the linked code.

**Current implementation**
- `cmd_check`, `warn_if_stale` in `reqmap.py`.


--------------------


---
id: REQ-CHECK-828
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
---

# Gate errors that block a commit

## Description
> An `ERROR` is the gate's hard-stop signal: it exits the process non-zero and blocks CI.
> It is reserved for problems a human must fix before the requirement corpus can be
> trusted at all — a broken tag, an invalid enum value, or a requirement claiming code
> exists when no tag proves it.

Every bullet below is binding.
- `gate` reports an `ERROR` and exits non-zero for every condition in this group.
- A dangling tag — a code tag referencing a capability no requirement defines — is
  such a condition.
- An invalid `status` or an invalid `layer` is such a condition.
- A `depends_on` pointing at a missing id is such a condition.
- An enforced requirement with no `implements:` member is such a condition.
- A requirement is enforced when its status is `in-progress`, `implemented` or
  `confirmed`.
- A `layer: need` requirement is exempt from that `implements:` rule — see
  [[ARCH-TRACE-020]].

## Cases
CASE-1 — a dangling tag is a gate ERROR
  Given  `mod.py` carrying `# implements: GHOST-CAP-001` and no such requirement
  When   `gate` runs
  Then   its output contains "dangling tag" and it exits 1

CASE-2 — an invalid status or layer is a gate ERROR
  Given  a requirement with `status: bogus`, and separately one with `layer: bogus`
  When   `gate` runs on each
  Then   each output contains "invalid status" or "invalid layer" respectively, and each
         exits 1

CASE-3 — a depends_on target that does not exist is a gate ERROR
  Given  a requirement with `depends_on: [GHOST-X-999]` and no such requirement
  When   `gate` runs
  Then   its output contains "depends_on missing GHOST-X-999" and it exits 1

CASE-4 — a confirmed requirement with no implements tag is a gate ERROR
  Given  a `status: confirmed` requirement with no `# implements:` tag anywhere
  When   `gate` runs
  Then   its output contains "no implements" and it exits 1

CASE-5 — ENFORCED names exactly the three enforced statuses
  Given  the module-level `R.ENFORCED` set
  When   it is inspected
  Then   it equals `{"in-progress", "implemented", "confirmed"}`, and `"draft"` is absent

CASE-6 — a confirmed need with no implements tag raises no gate error
  Given  a confirmed `layer: need` requirement with no `implements:` tag, satisfied by
         another requirement
  When   `gate` runs
  Then   `_link_sync_errors` reports no missing-implements error for that need


--------------------


---
id: REQ-CHECK-829
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
---

# Contract drift and missing-coverage warnings

## Description
> A `WARN` never blocks a commit on its own, but each one names a real gap: a confirmed
> contract that moved since its lock, a requirement with no test coverage linked, or a
> confirmed requirement missing its Description/Cases section. `--strict` turns most of
> these into hard failures once a team is ready to enforce them.

Every bullet below is binding.
- `gate` reports drift as a `WARN` under plain `gate`: a `confirmed` requirement whose
  binding hash differs from the lock.
- The drift warning names the member `file:line` locations to re-check.
- `gate --strict` promotes drift (and the no-`tested-by:` warning below, and member
  drift) to an `ERROR`. The `depends_on`-cycle warning and the legacy-schema warning
  are the two exceptions — they stay warnings even under `--strict`.
- A `confirmed` requirement with no `tested-by:` member is a `WARN`.
- A requirement carrying a `test_exempt: <reason>` opt-out in its frontmatter is exempt
  from that test warning.
- A `layer: need` requirement is exempt from it too.
- A `confirmed` requirement missing a `## Description` section is a `WARN`, in both
  the `bus` and `feature` layers. It does not affect the exit code.
- A `confirmed` requirement missing a `## Cases` section is a `WARN`, in both
  the `bus` and `feature` layers. It does not affect the exit code.

## Cases
CASE-1 — a confirmed requirement's changed contract warns DRIFT, prefixed WARN not ERROR under plain gate
  Given  a confirmed requirement locked at an old hash, whose Description text has since
         changed
  When   plain `gate` runs (no `--strict`)
  Then   its output contains "DRIFT" on a line printed with the "WARN" prefix, never
         "ERROR"

CASE-2 — the drift warning names the member's file and line
  Given  a confirmed, drifted requirement with one member tagged at `mod.py:1`
  When   `gate` runs
  Then   its output contains "re-check 1 member" and "mod.py:1"

CASE-3 — a confirmed requirement with no tested-by tag warns, not errors
  Given  a confirmed requirement with an `implements:` tag but no `tested-by:` tag
         anywhere, and no `test_exempt` field
  When   `gate` runs
  Then   its output contains "confirmed but no tested-by" and it exits 0

CASE-4 — test_exempt suppresses the no-tested-by warning
  Given  a confirmed requirement with `test_exempt: covered by manual QA` and an
         `implements:` tag but no `tested-by:` tag
  When   `gate` runs
  Then   its output contains no "tested-by" finding and it exits 0

CASE-5 — a confirmed need with no tested-by tag raises no test warning
  Given  a confirmed `layer: need` requirement with no `implements:` or `tested-by:` tag,
         satisfied by another requirement
  When   `gate` runs
  Then   its output contains no missing-tested-by warning for that need

CASE-6 — a confirmed requirement missing Description warns and exits 0
  Given  a confirmed `layer: bus` requirement whose body has no `## Description`/
         `## Contract` section
  When   `gate` runs
  Then   its output contains "missing '## Description'" and it exits 0

CASE-7 — a confirmed requirement missing Cases warns and exits 0
  Given  a confirmed `layer: bus` requirement whose body has a Description but no
         `## Cases`/`## Acceptance` section
  When   `gate` runs
  Then   its output contains "missing '## Cases'" and it exits 0


--------------------


---
id: REQ-CHECK-830
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
---

# Milestone shape and lock-file warnings

## Description
> Milestone typos and lock-file problems are roadmap or bookkeeping issues, not contract
> breaks, so they warn instead of failing the build. A corrupt or git-untracked lock is
> worth flagging anyway — silently disabling drift detection on a fresh checkout is worse
> than a loud warning.

Every bullet below is binding.
- The requirement `milestone:` field is optional. When present it matches the version
  shape `v<digits>[.<digits>…]`, for example `v1.14`.
- A malformed `milestone:` value is a `WARN`, because that field is roadmap-only
  metadata and never build-critical.
- A `deprecated` requirement is exempt from the `milestone:` shape check.
- A present-but-unreadable `_reqlock.json` is a `WARN`. Drift is skipped for that run
  rather than crashing.
- A lock sidecar (`_reqlock.json` or `_memberlock.json`) that exists on disk but is
  **not git-tracked** is a `WARN` naming the file.
- An uncommitted lock silently disables drift detection on a fresh CI checkout, which
  has no baseline to compare against.
- That git-tracking check is fail-open: `gate` stays silent when git is unavailable or
  the tree is not a work tree.
- `gate` names every sectioned-form requirement whose body lacks a `## Verify intent`
  section in one aggregated legacy-schema `WARN`. Atomic-form requirements (`form:
  atomic`) carry no such heading by design and are excluded from this check.

## Cases
CASE-1 — a well-shaped milestone value is silent
  Given  a confirmed requirement with `milestone: v1.14` (also tried: `v1.04`, `v2`)
  When   `gate` runs
  Then   its output contains no "malformed" finding

CASE-2 — a malformed milestone value warns
  Given  a confirmed requirement with `milestone: next` (also tried: `1.14`, `V1.0`,
         `v1.14-beta`)
  When   `gate` runs
  Then   its output contains "malformed"

CASE-3 — a deprecated requirement's malformed milestone is silent
  Given  a `status: deprecated` requirement with `milestone: next` (malformed shape)
  When   `gate` runs
  Then   its output contains no "malformed" finding

CASE-4 — a corrupt _reqlock.json warns and does not crash the gate
  Given  a `_reqlock.json` containing invalid JSON ("{ not json")
  When   `gate` runs
  Then   its output contains "unreadable" and it exits 0

CASE-5 — an untracked lock file is flagged, then clears once tracked
  Given  a git work tree with `_reqlock.json` written to disk but never `git add`ed
  When   `untracked_locks(reqs_dir)` runs before and after `git add -A`
  Then   it names `_reqlock.json` before the add and returns `[]` after it, closing the gap
         where a fresh CI checkout would otherwise have no baseline for drift detection

CASE-6 — the untracked-lock check is silent outside a git work tree
  Given  a `_reqlock.json` written to a plain directory that is not yet a git repository
  When   `untracked_locks(reqs_dir)` runs
  Then   it returns `[]`, not an error

CASE-7 — a sectioned-form requirement missing Verify intent is named in the legacy-schema warning
  Given  a sectioned-form requirement whose body has no `## Verify intent` section
  When   `gate` runs
  Then   its output contains "legacy schema" naming that requirement's id, and "findings`
         is inactive"


--------------------


---
id: REQ-CHECK-831
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
---

# Corpus-health warnings: needs, levels, cycles

## Description
> These warnings are opt-in signals about corpus health rather than individual contract
> breaks: an unvalidated stakeholder need, foundation code tested only end-to-end, or a
> `depends_on` cycle that makes build order ambiguous. They stay warnings even under
> `--strict` so upgrading the engine never flips a green build red.

Every bullet below is binding.
- `gate` counts those legacy-schema requirements in the summary.
- The legacy-schema warning does not affect the exit code.
- A confirmed `need` with no `validated-against:` member is a `WARN`, once the repo carries at
  least one such tag (see [[ARCH-VLEVEL-037]]).
- A confirmed `bus` requirement whose levelled `tested-by:` links are all `@system` is a `WARN`.
- A `depends_on` cycle is a `WARN` naming the whole chain, once per distinct cycle.
- The cycle warning stays a warning under `--strict`, so an existing corpus keeps its
  exit code when the engine is upgraded.

## Cases
CASE-1 — the summary line reports the legacy-schema count
  Given  one requirement whose body has no `## Verify intent` section
  When   `gate` runs
  Then   its final summary line contains "1 legacy-schema"

CASE-2 — a legacy-schema requirement warns but the gate exits 0
  Given  a `status: baseline` requirement with no `## Verify intent` section
  When   `gate` runs
  Then   its output contains "legacy schema" and it exits 0

CASE-3 — an unvalidated confirmed need warns once the repo has opted in
  Given  a confirmed need with no `validated-against:` tag, in a repo where at least one
         `validated-against:` tag exists elsewhere
  When   `gate` runs
  Then   its output names that need alongside "validated-against"

CASE-4 — a bus requirement verified only at @system warns
  Given  a confirmed `layer: bus` requirement whose only levelled `tested-by:` link is
         `@system`
  When   `gate` runs
  Then   its output contains "@system"

CASE-5 — a depends_on cycle warns once, naming the whole chain
  Given  two requirements whose `depends_on` fields point at each other
  When   `gate` runs
  Then   its output contains "depends_on cycle" and "A-X-001 -> A-X-002 -> A-X-001", and
         it exits 0

CASE-6 — --strict does not promote the cycle warning to an error
  Given  two requirements whose `depends_on` fields point at each other
  When   `gate --strict` runs
  Then   it still exits 0


--------------------


---
id: REQ-CHECK-832
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
---

# What the gate prints beyond pass or fail

## Description
> Besides an exit code, `gate` reports what it saw: how many verify-intent questions are
> still open, and a one-line summary of requirements, members, errors and warnings.
> Neither line changes the exit code — they are for the person reading the terminal, not
> for CI.

Every bullet below is binding.
- `gate` prints an advisory line carrying the open verify-intent finding count when that
  count is above zero.
- That advisory line does not affect the exit code.
- `gate` prints a summary of requirements, members, errors and warnings.

## Cases
CASE-1 — gate reports the open verify-intent finding count
  Given  a requirement with one open `## Verify intent` question
  When   `gate` runs
  Then   its output contains "1 open verify-intent finding(s)"

CASE-2 — an open verify-intent finding does not change an otherwise-clean exit code
  Given  a `baseline` requirement with one open `## Verify intent` question and no other
         gate finding
  When   `gate` runs
  Then   it prints the finding count and returns exit code 0

CASE-3 — the summary line reports the confirmed and legacy-schema counts
  Given  one confirmed requirement (implemented) and one baseline requirement, both in
         the current schema
  When   `gate` runs
  Then   its final line contains "1 confirmed" and "0 legacy-schema"


--------------------


---
id: REQ-CHECK-833
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-CHECK-006]
---

# Advancing the lock file

## Description
> The lock file (`_reqlock.json`) only advances when explicitly told to — plain `gate` is
> read-only so a developer can check the corpus without accidentally re-baselining a
> drifted contract. `sync` always passes `--update-lock`; the deprecated `check` alias
> does not, matching its older, more cautious default.

Every bullet below is binding.
- With `--update-lock`, `gate` writes the current binding hashes to
  `requirements/_reqlock.json`.
- `sync` always passes `--update-lock`. The deprecated `check` alias does not — it
  only advances the lock when the caller explicitly passes `--update-lock`.
- The `gate` verb itself is report-only.

## Cases
CASE-1 — --update-lock writes the requirement's hash into the lock
  Given  a `baseline` requirement with no existing lock entry
  When   `cmd_check(..., update_lock=True)` runs
  Then   `load_lock(d)` afterward contains that requirement's id

CASE-2 — a clean sync run advances the lock and regenerates the map
  Given  a clean corpus (no gate errors)
  When   `reqmap sync --root <d> --code <d>` runs
  Then   it exits 0 and `requirements/_map.json` exists, confirming the full
         check-with-lock-then-map pipeline ran

CASE-3 — the gate verb never writes lock updated
  Given  a plain draft requirement, no `--update-lock` flag
  When   `reqmap.py gate --root <d>` runs
  Then   it exits 0 and its stdout contains no "lock updated" line

