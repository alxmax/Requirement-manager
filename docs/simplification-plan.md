# Requirement-manager simplification plan

Approved scope: four stacked pull requests, each based on the previous one.
Baseline: v8.6.0, upstream commit `5511c81` (2026-09-23).

The goal is a dependable, small routine: requirements, implementation/test links,
drift detection, and one verdict. Reducing lines is secondary to preserving that
contract. A linked test is evidence of traceability, not proof of semantic correctness.

## Ranked backlog

| Order | Work | Acceptance evidence | Delivery |
|---|---|---|---|
| 1 | One structured gate result | Text and JSON run the same stages and return the same exit code | PR 1 |
| 2 | Reject ambiguous or invalid inputs | Duplicate IDs, invalid config and corrupt strict baselines cannot report success | PR 2 |
| 3 | Separate checking from report generation | Read-only verdict; rendering remains outside the critical path | Follow-up |
| 4 | Isolate peripheral capabilities | Price design/site/release adapters against real consumer usage before removal | Follow-up |
| 5 | Minimal initialization | A documented small setup without site/release scaffolding; full setup remains available | PR 3 |
| 6 | Demand-load optional modules | Measure imports before and after; preserve public compatibility deliberately | Follow-up |
| 7 | Explicit data model and configuration | Fewer implicit conversions and global mutations, migrated incrementally | Follow-up |
| 8 | Generate interfaces from COMMANDS | MCP/schema/docs cannot describe different flags | Follow-up |
| 9 | Slim map exports | Compact HTML payload, optional translations, concise Markdown with complete export available | PR 3 |
| 10 | Clarify artifact ownership | Requirements/config/baselines remain versioned; generated publication assets have explicit owners | PR 3 documentation |
| 11 | Share agent instructions | One authoring contract, small assistant-specific entry points, generated command references | PR 4 |
| 12 | Explain policy and limits | Errors, warnings and unperformed checks are distinguishable; format does not change policy | PRs 1–2 |
| 13 | Stabilize schema upgrades | Upgrade fixtures preserve confirmations unless the actual contract changes | Follow-up |
| 14 | Retire compatibility deliberately | Inventory consumers and publish a migration before removing aliases | Follow-up |
| 15 | Test contracts and failure paths | JSON/text parity, bad inputs, minimal/full setup and export fidelity regressions | Every PR |
| 16 | Optimize measured bottlenecks | Record scan/import/gate costs; avoid speculative caches | Follow-up |
| 17 | Simplify viewer navigation | Validate the main reading/review tasks before changing UI navigation | Follow-up |
| 18 | Evaluate on external repositories | 3–5 repos: setup time, false positives, useful findings, commands actually used | Follow-up |

## Four reviewable increments

1. **Plan and unified verdict** (`refactor/01-unified-gate`, base `main`).
   Collect rule, lint and map findings before choosing text or JSON. Keep read-only
   behavior, explicit opt-outs and the existing human report. Add regression cases
   that failed before this change.
2. **Input integrity** (`refactor/02-input-integrity`, base PR 1).
   Structured diagnostics for invalid corpus/configuration input. Strict mode must
   distinguish an absent initial baseline from a damaged baseline. Document the
   severity decision and test both formats.
3. **Minimal setup and smaller maps** (`refactor/03-slim-exports`, base PR 2).
   Reduce setup and publication overhead while retaining a documented full mode.
   Preserve requirement content and offline HTML behavior; prove compact exports
   decode to the intended data. Record exact size deltas.
4. **Shared agent contract** (`refactor/04-shared-instructions`, base PR 3).
   Extract duplicated normative instructions into a shared reference. Keep trigger
   metadata, critical workflow rules and assistant-specific setup discoverable.
   Validate generated command regions and reference links.

Merge in order. After a parent merges, retarget its child to `main`; the final PR
contains the complete series, while each comparison shows only its own increment.
No deployment, tag push or merge is part of this work.

## Measurement protocol

Run `python scripts/measure_plugin.py` after the normal sync. Sizes are UTF-8 bytes,
not token estimates or compressed transfer sizes. The offline HTML is reconstructed
from the tracked template and JSON, so no generated HTML needs to be committed.
Use the same corpus for a format-only comparison; full-repo sizes also include the
new/updated requirements and links needed to describe the implementation.

| Stage | Map Markdown | Map JSON | Offline HTML | Both agent entry points |
|---|---:|---:|---:|---:|
| Baseline | 90,707 | 1,574,184 | 1,869,883 | 72,492 |
| PR 1 | 90,999 | 1,575,539 | 1,871,240 | 72,492 |
| PR 2 | 90,998 | 1,565,220 | 1,860,933 | 72,492 |

Each PR appends its actual measured row. Growth in the first two correctness changes
is reported honestly; it is not hidden by removing requirement evidence.

## Validation and limits

Run engine regressions, cross-tool integration, version checks, the retirement guard,
and the repository's widened gate. Regenerate the map, command interfaces and
baselines together. Check the engine budget; do not bypass it to land the series.
The viewer source/bundle remains unchanged unless a demonstrated compatibility
problem requires an update. Performance targets need a named workload and machine.

The remaining backlog is deliberately not claimed complete by these four PRs.
