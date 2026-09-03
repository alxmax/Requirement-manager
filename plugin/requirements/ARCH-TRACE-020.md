---
id: ARCH-TRACE-020
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-PARSE-001, ARCH-CHECK-006]
satisfies: [SYS-VMODEL-107]
superseded_by:
milestone: v1.17
---

# Upstream traceability

## Description
> A requirement file tells you what a capability does and which code builds it, but not *why
> it exists* — which stakeholder need it serves. This lets a requirement point upward with a
> `satisfies:` field, so you can trace from a stakeholder need down to every requirement that
> fulfils it, and back up from any requirement to the need behind it. Without it, requirements
> float free of the needs that justify them, and a need can quietly go unaddressed.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a need       a `layer: need` requirement: something a stakeholder wants, fulfilled by
                  other requirements rather than by code.
     upstream id  the id of the need or higher-level requirement a requirement fulfils.
     the gate     the pre-commit check that reports errors and warnings.
     frontmatter  the YAML block between the two `---` lines at the top of the file. -->

**How a link is declared**
- A requirement may declare a `satisfies:` frontmatter list of the upstream ids it fulfils.

**When the gate warns**
- The gate warns, and never errors, when a `satisfies:` id resolves to no requirement. An
  upstream anchor may be authored later, or tracked outside this repo.
- The gate warns when a confirmed `need` has no requirement satisfying it, so an unaddressed
  stakeholder need is visible.

**How an aggregate differs**
- The `aggregate` layer is exempt from the implements check. Its implementation is the
  implementation of the requirements it depends on.
- An aggregate declares at least one `depends_on` id. An aggregate with no dependency is an
  orphan, not an aggregate.
- An aggregate adds no behaviour of its own. It asserts that its dependencies work together.

**How a need differs**
- The `need` layer is exempt from the implements and tested-by checks. A need is satisfied by
  other requirements, not implemented or tested by code.
- A need is still expected to carry a `validated-against:` link once the repo adopts that
  role, because being satisfied by requirements is not evidence the need was met
  (see [[ARCH-VLEVEL-037]]).

**Where the links surface**
- `show` prints the upstream ids a requirement satisfies and the requirements that satisfy it,
  but only when that requirement takes part in traceability.
- The map data carries `satisfies` and `satisfied_by` on each node, plus a list of upstream
  edges, so a front-end can draw the trace.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- A dangling `satisfies:` is a warning, not an error, so the field can hold an external reference (a ticket id) that the engine cannot resolve — at the cost of not catching a typo in an internal id.
- Traceability is opt-in: a requirement with no `satisfies:` is never flagged, matching the tool's subtle-guidance philosophy.

## Cases (= tests)
CASE-1
  Given  a requirement with `satisfies: [GHOST-X-999]` and no such requirement
  When   the gate runs
  Then   it warns about the dangling upstream trace and does NOT raise an error
CASE-2
  Given  a confirmed `need` that no requirement satisfies
  When   the gate runs
  Then   it warns that the need is unaddressed
CASE-3
  Given  a confirmed `layer: need` requirement with no implements or tested-by tag
  When   the gate runs
  Then   it raises no implements/tested-by finding for that need
CASE-4
  Given  a requirement that satisfies a need
  When   `show` runs on either the requirement or the need
  Then   the upstream/satisfied-by relationship is printed
CASE-5
  Given  a confirmed `layer: aggregate` requirement with dependencies and no implements tag
  When   the gate runs
  Then   it raises no implements finding for that requirement

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana writes `SYS-SSOT-001` for "specs and code stay in sync", then adds
  `satisfies: [SYS-SSOT-001]` to the gate and the map requirements. Running `reqmap.py show
  SYS-SSOT-001` now lists those features under "Satisfied by", and `show` on the gate lists
  the need under "Satisfies (upstream)". When she writes a need but forgets to point any
  requirement at it, the gate warns that the need is unaddressed.

## WHERE — Current implementation
- `cmd_check` (satisfies validation + need exemptions + orphan-need warn), `cmd_show` (upstream lines), and `_build_map_data` (`satisfies`/`satisfied_by` node fields + `upstream_edges`) in `reqmap.py`, plus `VALID_LAYER` gaining `need`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-TRACE-750
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# A requirement may declare a satisfies: frontmatter list

> A requirement may declare a `satisfies:` frontmatter list of the upstream ids it
> fulfils.

Scenario: satisfies: parses into a frontmatter list like any other id field
  Given  a requirement file with `satisfies: [SYS-SSOT-001]` in its frontmatter
  When   `parse_frontmatter` reads the file
  Then   `meta["satisfies"]` equals `["SYS-SSOT-001"]`

## Members in code (auto)




--------------------


---
id: REQ-TRACE-751
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# The gate warns, and never errors, when a

> The gate warns, and never errors, when a `satisfies:` id resolves to no requirement. An
> upstream anchor may be authored later, or tracked outside this repo.

Scenario: a dangling satisfies id warns without failing the gate
  Given  a requirement with `satisfies: [GHOST-X-999]` and no such requirement in the corpus
  When   `gate` runs
  Then   it prints "satisfies GHOST-X-999 but no such requirement" and exits 0

## Members in code (auto)




--------------------


---
id: REQ-TRACE-752
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# The gate warns when a confirmed need has

> The gate warns when a confirmed `need` has no requirement satisfying it, so an
> unaddressed stakeholder need is visible.

Scenario: an unaddressed confirmed need warns at the gate
  Given  a confirmed `layer: need` requirement no other requirement satisfies
  When   `gate` runs
  Then   it warns "need has no requirement that satisfies it (upstream trace unaddressed)"

## Members in code (auto)




--------------------


---
id: REQ-TRACE-753
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# The aggregate layer is exempt from the implements

> The `aggregate` layer is exempt from the implements check. Its implementation is the
> implementation of the requirements it depends on.

Scenario: a confirmed aggregate with no implements tag passes the gate
  Given  a confirmed `layer: aggregate` requirement with `depends_on` a code-backed requirement,
         and no `implements:` tag of its own
  When   `gate` runs
  Then   `_link_sync_errors` reports no missing-implements error for the aggregate

## Members in code (auto)




--------------------


---
id: REQ-TRACE-754
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# An aggregate declares at least one depends_on id

> An aggregate declares at least one `depends_on` id. An aggregate with no dependency is
> an orphan, not an aggregate.

Scenario: confirm refuses an aggregate with an empty depends_on
  Given  a `layer: aggregate` requirement with `depends_on: []`
  When   `confirm <ID>` runs
  Then   it refuses with "depends_on is empty" and leaves the file's status unchanged

## Members in code (auto)




--------------------


---
id: REQ-TRACE-755
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# An aggregate adds no behaviour of its own

> An aggregate adds no behaviour of its own. It asserts that its dependencies work
> together.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-TRACE-756
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# The need layer is exempt from the implements

> The `need` layer is exempt from the implements and tested-by checks. A need is satisfied
> by other requirements, not implemented or tested by code.

Scenario: a confirmed need raises no implements/tested-by finding
  Given  a confirmed `layer: need` requirement with no `implements:` or `tested-by:` tag,
         satisfied by another requirement so the orphan-need warn stays silent
  When   `gate` runs
  Then   it raises no missing-implements error and no missing-tested-by warning for that need

## Members in code (auto)




--------------------


---
id: REQ-TRACE-757
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# A need is still expected to carry a

> A need is still expected to carry a `validated-against:` link once the repo adopts that
> role, because being satisfied by requirements is not evidence the need was met (see
> [[ARCH-VLEVEL-037]]).

Scenario: a confirmed need with no validated-against tag warns once the repo opts in
  Given  a corpus where at least one member carries a `validated-against:` tag, and a
         confirmed `layer: need` requirement with no `validated-against:` member of its own
  When   `gate` runs
  Then   it warns "confirmed need with no `validated-against:` tag"

## Members in code (auto)




--------------------


---
id: REQ-TRACE-758
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# Show prints the upstream ids a requirement satisfies

> `show` prints the upstream ids a requirement satisfies and the requirements that satisfy
> it, but only when that requirement takes part in traceability.

Scenario: show prints the trace in both directions
  Given  a need `NEED-X-001` and a feature `A-FOO-001` with `satisfies: [NEED-X-001]`
  When   `show A-FOO-001` and `show NEED-X-001` each run
  Then   the feature's output contains "Satisfies (upstream): NEED-X-001" and the need's
         output contains "Satisfied by: A-FOO-001"

## Members in code (auto)




--------------------


---
id: REQ-TRACE-759
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-TRACE-020]
superseded_by:
---

# The map data carries satisfies and satisfied_by on

> The map data carries `satisfies` and `satisfied_by` on each node, plus a list of
> upstream edges, so a front-end can draw the trace.

Scenario: map data exposes satisfies, satisfied_by and upstream_edges
  Given  a need `NEED-X-001` and a feature `A-FOO-001` with `satisfies: [NEED-X-001]`
  When   `_build_map_data` builds the node graph
  Then   the feature node's `satisfies` is `["NEED-X-001"]`, the need node's `satisfied_by`
         is `["A-FOO-001"]`, and `["A-FOO-001", "NEED-X-001"]` appears in `upstream_edges`

## Members in code (auto)
