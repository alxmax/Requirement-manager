---
id: REQ-DRIFTIMPACT-035
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [REQ-CHECK-006, CORE-DRIFT-003]
superseded_by:
milestone: v2.10
---

# Drift blast-radius: name dependents

> When a confirmed requirement's contract drifts, the gate names the
> requirement and its code members — but not the requirements built on top of
> it via `depends_on`. An upstream contract change can invalidate a downstream
> requirement's assumptions with no signal at all, and the reviewer has to
> reconstruct the blast radius by hand from the map. The dependency graph is
> already in memory at gate time; naming the dependents turns one drift
> warning into an actionable review list.

## WHAT — Contract (normative)
- When the gate reports a contract drift for a requirement, and at least one
  other requirement lists the drifted one in `depends_on`, the same warning
  line also names those dependent requirement ids.
- The dependent list is sorted and deduplicated, so the output is
  deterministic across platforms and walk orders.
- Only direct dependents are named (one edge, not the transitive
  closure). <!-- Rationale: transitive closures explode on bus-layer nodes and
  bury the signal; a reviewer follows the chain one hop at a time. -->
- A drifted requirement with no dependents produces the existing warning
  unchanged — no empty "dependents" clause.
- The addition does not change the drift warning's severity: it stays
  warn-only by default and promotable by `--strict`, exactly as before.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes & known limitations (informative)
- Naming a dependent asserts topology, not impact: the dependent may be
  unaffected by the specific clause that changed. The reviewer decides; the
  gate only stops the radius from being invisible.
- Member drift (REQ-MEMBERDRIFT-027) is not fanned out: a code-ahead-of-spec
  change has no changed contract for dependents to have relied on.

## HOW — Acceptance (= tests)
AC-1
  Given  a confirmed requirement whose contract hash differs from the lock and
         a second requirement that lists it in `depends_on`
  When   the gate runs
  Then   the drift warning names the dependent requirement's id
AC-2
  Given  a confirmed drifted requirement that no other requirement depends on
  When   the gate runs
  Then   the drift warning appears without any dependent clause
AC-3
  Given  a drifted requirement with two dependents
  When   the gate runs
  Then   both ids appear in sorted order on the drift line

## Example — in practice (optional, non-binding)
- The contract of CORE-PARSE-001 (frontmatter parsing) is edited. The gate
  says: "CORE-PARSE-001: DRIFT — contract changed since lock; re-check 3
  member(s): …; review dependent(s): CORE-SCAN-002, REQ-CHECK-006". The
  reviewer opens those two before accepting the drift with `sync
  --accept-drift`.

## WHERE — Current implementation
- The drift loop in `cmd_check` (`reqmap.py`): a reverse-`depends_on` index is
  built once from the loaded requirements, and the drift warning appends
  "review dependent(s): …" when the index has entries for the drifted id.

## Links
- Used by: (auto)
## Members in code (auto)
