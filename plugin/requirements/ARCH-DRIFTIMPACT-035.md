---
id: ARCH-DRIFTIMPACT-035
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v2.10
depends_on: [ARCH-CHECK-006, ARCH-DRIFT-003]
satisfies: [SYS-GATE-102]
---

# Drift blast-radius: name dependents

## Description
> When a confirmed requirement's contract drifts, the gate names the
> requirement and its code members — but not the requirements built on top of
> it via `depends_on`. An upstream contract change can invalidate a downstream
> requirement's assumptions with no signal at all, and the reviewer has to
> reconstruct the blast radius by hand from the map. The dependency graph is
> already in memory at gate time; naming the dependents turns one drift
> warning into an actionable review list.

Every bullet below is binding.
- The gate's drift warning names the requirements that depend on the drifted one via `depends_on`, so a reviewer sees the blast radius without reconstructing it from the map. [[REQ-DRIFTIMPACT-843]]

## Cases
CASE-1
  Given  a confirmed requirement whose contract hash differs from the lock and
         a second requirement that lists it in `depends_on`
  When   the gate runs
  Then   the drift warning names the dependent requirement's id
CASE-2
  Given  a confirmed drifted requirement that no other requirement depends on
  When   the gate runs
  Then   the drift warning appears without any dependent clause
CASE-3
  Given  a drifted requirement with two dependents
  When   the gate runs
  Then   both ids appear in sorted order on the drift line

## Context
**Notes**
- Naming a dependent asserts topology, not impact: the dependent may be
  unaffected by the specific clause that changed. The reviewer decides; the
  gate only stops the radius from being invisible.
- Member drift (ARCH-MEMBERDRIFT-027) is not fanned out: a code-ahead-of-spec
  change has no changed contract for dependents to have relied on.

**Example**
- The contract of ARCH-PARSE-001 (frontmatter parsing) is edited. The gate
  says: "ARCH-PARSE-001: DRIFT — contract changed since lock; re-check 3
  member(s): …; review dependent(s): ARCH-SCAN-002, ARCH-CHECK-006". The
  reviewer opens those two before accepting the drift with `sync
  --accept-drift`.

**Current implementation**
- The drift loop in `cmd_check` (`reqmap.py`): a reverse-`depends_on` index is
  built once from the loaded requirements, and the drift warning appends
  "review dependent(s): …" when the index has entries for the drifted id.


--------------------


---
id: REQ-DRIFTIMPACT-843
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DRIFTIMPACT-035]
---

# Name a drifted requirement's direct dependents

## Description
> `cmd_check` builds a reverse-`depends_on` index once from the loaded requirements. When a
> confirmed requirement's contract hash no longer matches the lock, the same warning line
> that reports the drift also lists the requirement ids that depend on it — so a reviewer
> gets the blast radius for free instead of reconstructing it by hand from the map.

Every bullet below is binding.
- When the gate reports a contract drift for a requirement, and at least one
  other requirement lists the drifted one in `depends_on`, the same warning
  line also names those dependent requirement ids.
- The dependent list is sorted and deduplicated, so the output is
  deterministic across platforms and walk orders.
- Only direct dependents are named — one edge, not the transitive closure. A
  transitive closure explodes on bus-layer nodes and buries the signal; a
  reviewer follows the chain one hop at a time.
- A drifted requirement with no dependents produces the existing warning
  unchanged — no empty "dependents" clause.
- The addition does not change the drift warning's severity: it stays
  warn-only by default and promotable by `--strict`, exactly as before.

## Cases
CASE-1 — drift warning names a requirement that depends on the drifted one
  Given  a confirmed drifted requirement and a second requirement with it in `depends_on`
  When   `gate` runs
  Then   the drift warning line includes "review dependent(s):" followed by the second id,
         with severity unchanged — still warn-only, promotable only by `--strict`

CASE-2 — two dependents are named in sorted order on the drift line
  Given  a drifted requirement with two dependents whose ids sort after each other
  When   `gate` runs
  Then   the "review dependent(s):" list shows both ids in ascending id order

CASE-3 — a dependent-of-a-dependent is not named on the drift line
  Given  A depends on drifted B, and C depends on A (but not on B)
  When   `gate` runs
  Then   the drift warning for B names A but does not name C

CASE-4 — an isolated drifted requirement's warning carries no dependents clause
  Given  a confirmed drifted requirement that no other requirement lists in `depends_on`
  When   `gate` runs
  Then   the drift warning line contains no "review dependent(s):" text at all

