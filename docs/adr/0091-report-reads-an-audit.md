# ADR-0091 — The Report reads an audit, and the map carries the trace's reach

- **Status:** Accepted. Extends the Report page (REQ-VIEWER-1139) and the map (ARCH-MAP-007).
- **Decided:** 2026-11-21
- **Evidence:** the report of a read-only audit of an existing repository was written by hand
  beside the map. It counted things the map could not show: the audit session itself, the
  findings apart from the questions (a separate table explained why the two counts differed),
  the share of files with a tag and of production code under the drift lock, a probable test
  for each requirement with no `tested-by:`, requirements that repeated each other, local design
  rules, and its deliverables sat in a temporary folder.

## Decision

- **`sync` writes a `trace` block** (`tracecover.py`): `coverage`, `suggestions` (tier A, B, C),
  `hygiene` and, when declared, `rules`. It is advice like the design record: the freshness
  check neither computes nor compares it, so a moved line never fails the gate.
- **A tested-by suggestion is read from names, never guessed from content alone.** A test
  paired with the code by file name (the ADR-0090 pairing) is tier B; if it also names the
  requirement or one of the definitions the member lock keys for it, tier A. With no paired
  test, tier C: probably a real gap.
- **`DESIGN_RULES`** lets a repository declare its own banned constructs as regular
  expressions, counted on production code with comments and literals blanked for C/C++. They
  are counted, never judged: no gate rule, no verdict.
- **An audit finding is not a question.** A Verify-intent bullet `Observed (audit, KIND)` is
  counted by kind on the Report and left off the Questions page, so the two counts no longer
  need reconciling.
- **The Report downloads as Markdown** beside its PDF, so the deliverable is a file the reader
  keeps.

## Consequences

- `CORE_LOGICAL_BUDGET` rises from 6,932 to 7,062: the harness counts what `sync` loads, and
  `sync` writes the trace block.
- A map written before this has no `trace` block; the Report shows `not measured` for its
  numbers, never zero.
- Tier A is evidence, not proof: the tag is still a person's decision.

## Revisit when

- Tier A suggestions are applied on a corpus and more than one in ten turns out wrong: then
  tier A needs both the requirement and a definition named, or moves to B.
- `sync` on a large repository spends noticeably longer because of the walk: then the trace
  block reuses the scan's file list instead of walking again.
