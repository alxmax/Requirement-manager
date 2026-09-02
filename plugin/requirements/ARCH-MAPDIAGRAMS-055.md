---
id: ARCH-MAPDIAGRAMS-055
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
depends_on: [ARCH-MAP-007]
satisfies: [SYS-VISUAL-106]
superseded_by:
---

# Mermaid diagrams (_map.md)

## Description
> The graph is data; this is the picture. Four Mermaid diagrams that render on GitHub with
> no tooling, so someone reviewing a pull request can see the shape of the system without
> cloning anything or running the engine.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a node       one requirement, as drawn in a diagram.
     an area      the group a requirement belongs to: its `area:` field, or the first
                  part of its id when that field is absent.
     a bus node   a `layer: bus` requirement — a foundation many others use.
     a hub        a requirement many others depend on (high fan-in). -->

**What is drawn**
- `map` generates `_map.md` under `requirements/`, rendered from the graph and never edited.
- `_map.md` contains exactly 5 Mermaid code blocks: Specification Hierarchy, System Map,
  Req→Code, Dependencies and Risk.
- Each of those 5 blocks carries a legend.

**The Specification Hierarchy**
- The Specification Hierarchy is drawn from the `satisfies:` edges, never from `depends_on:`.
- The Hierarchy draws a node for each `system` and each `architecture` requirement.
- The Hierarchy counts a `code` requirement against its parent and never draws it.
- An architecture box shows how many code requirements sit under it.

**The System Map**
- A node's area is its `area:` field, or its id prefix when that field is absent.
- The System Map groups nodes into per-area subgraphs, and collapses a single-node area
  into a `misc` box.
- The System Map omits a `depends_on` edge whose target is a bus node or a high-fan-in hub.

**The Dependency Map**
- The Dependency Map is area-level: one node per area, carrying a capability count.
- The Dependency Map draws an edge A→B when some capability in A depends on one in B.
  Per-capability hub edges are not drawn.

**Req→Code**
- Req→Code colors an enforced-but-unlinked requirement red, and a baseline or draft
  not-yet-linked one muted grey.
- Req→Code collapses multiple members in one file to a min–max line range.

**Risk**
- The Risk diagram shows only requirements with at least one risk signal
  (confirmed with zero members; `draft`/`baseline`; ≥3 dependents).
- The Risk diagram pairs each of them with a scripted recommendation.
- A `draft`'s open verify-intent question is suppressed, subsumed by its `unreviewed`
  signal, so a draft is not double-flagged.

## Verify intent (open questions for the human)
- None — split out of [[ARCH-MAP-007]] with intent carried over unchanged.

## Cases (= tests)
CASE-1
  Given  the generated `_map.md`
  When   it is inspected
  Then   it contains exactly 5 Mermaid code blocks, each with a legend

CASE-2
  Given  a corpus carrying system, architecture and code requirements
  When   the Specification Hierarchy is rendered
  Then   it draws the system and architecture nodes joined by their `satisfies:` edges,
         draws no code node, and shows each architecture's code count on its box

CASE-3
  Given  the System Map diagram
  When   it is rendered
  Then   nodes group into per-area subgraphs, single-node areas collapse into `misc`, and edges
         whose target is a bus node are omitted

CASE-4
  Given  the Dependency Map diagram
  When   it is rendered
  Then   it is area-level: one node per area (with a count), an edge A→B when some capability
         in A depends on one in B; per-capability hub edges are not drawn

CASE-5
  Given  the Risk diagram
  When   it is rendered
  Then   it shows only requirements with at least one risk signal, each with a scripted
         recommendation, and a draft's open question is not shown twice

## Context (non-binding)
**Notes**
- The risk-signal dedup lives in `_risk_signals`, shared with the `next` worklist, so the
  diagram and the worklist cannot disagree about what is at risk.
- Split out of [[ARCH-MAP-007]] on 2026-09-02. That requirement held 35 Contract clauses
  covering two capabilities — the graph and its rendering — and was the only requirement
  over twenty clauses carrying no `lint_exempt:`, i.e. the only one whose size had never
  been judged acceptable in writing.

**Example**
- Ana opens the pull request on GitHub. The System Map shows AUTH-LOGIN-001 wired to the
  session capability it depends on, coloured amber because it has no tests yet. She never
  runs the engine.

**Current implementation**
- `_mermaid_hierarchy`, `_grouped_areas`, `_mermaid_system`, `_mermaid_deps`, `_mermaid_req_to_code`,
  `_mermaid_risk`, `_build_md_text` and `render_md` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-494
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# Map generates _map.md under requirements/, rendered from the

> `map` generates `_map.md` under `requirements/`, rendered from the graph and never
> edited.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-495
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# _map.md contains exactly 5 Mermaid code blocks: Specification

> `_map.md` contains exactly 5 Mermaid code blocks: Specification Hierarchy, System Map,
> Req→Code, Dependencies and Risk.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-496
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# Each of those 5 blocks carries a legend

> Each of those 5 blocks carries a legend.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-497
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Specification Hierarchy is drawn from the satisfies

> The Specification Hierarchy is drawn from the `satisfies:` edges, never from
> `depends_on:`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-498
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Hierarchy draws a node for each system

> The Hierarchy draws a node for each `system` and each `architecture` requirement.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-499
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Hierarchy counts a code requirement against its

> The Hierarchy counts a `code` requirement against its parent and never draws it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-500
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# An architecture box shows how many code requirements

> An architecture box shows how many code requirements sit under it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-501
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# A node's area is its area: field, or

> A node's area is its `area:` field, or its id prefix when that field is absent.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-502
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The System Map groups nodes into per-area subgraphs

> The System Map groups nodes into per-area subgraphs, and collapses a single-node area
> into a `misc` box.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-503
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The System Map omits a depends_on edge whose

> The System Map omits a `depends_on` edge whose target is a bus node or a high-fan-in
> hub.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-504
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Dependency Map is area-level: one node per

> The Dependency Map is area-level: one node per area, carrying a capability count.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-505
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Dependency Map draws an edge A→B when

> The Dependency Map draws an edge A→B when some capability in A depends on one in B.
> Per-capability hub edges are not drawn.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-506
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# Req→Code colors an enforced-but-unlinked requirement red, and a

> Req→Code colors an enforced-but-unlinked requirement red, and a baseline or draft
> not-yet-linked one muted grey.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-507
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# Req→Code collapses multiple members in one file to

> Req→Code collapses multiple members in one file to a min–max line range.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-508
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Risk diagram shows only requirements with at

> The Risk diagram shows only requirements with at least one risk signal (confirmed with
> zero members; `draft`/`baseline`; ≥3 dependents).

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-509
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# The Risk diagram pairs each of them with

> The Risk diagram pairs each of them with a scripted recommendation.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-MAPDIAGRAMS-510
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-MAPDIAGRAMS-055]
superseded_by:
---

# A draft's open verify-intent question is suppressed, subsumed

> A `draft`'s open verify-intent question is suppressed, subsumed by its `unreviewed`
> signal, so a draft is not double-flagged.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)
