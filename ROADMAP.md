# Roadmap

The product plan. It is not a log: what shipped lives in the CHANGELOG and in the git tags, and
a checked item leaves this file.

Edit it here, directly. The bars in the viewer's Gantt are written in `plugin/requirements/_planning.json`.

Format: `- [ ] text | req: ID` under Now/Next. Later needs `unpark:`.
Reserved headings: Now, Next, Later, Not now. Categories are `###` headings inside them.
Cadence: one release a week, not one per merge.

## Now

### Adoption

- [ ] Consilium-py stays green on `check@v8`. Done when: at least 5 green runs on `main` since the re-vendoring (2026-09-21, Consilium-py #63) | req: ARCH-SELFGATE-039
- [ ] An outside evaluator, on their own repo, with no help at the gate. Done when: they have `uses: alxmax/requirement-manager/check@v8` on a tree you do not commit to | req: SYS-SSOT-001

## Next

## Later

### Engine surface

- [ ] The next cut from the engine: one capability from the removable list (`gate --risk`/`--audit`, `clarify`/decompose, `ask`, lint, `sync --retire`), with an ADR, a retire and the budget lowered in the same commit. The floor with the ROADMAP, MCP and `init` kept: 9,303 lines (ADR-0048) | req: ARCH-SELFGATE-039 | unpark: the maintainer names the capability
- [ ] Checking separated from report generation: `gate` computes the verdict and nothing else, rendering lives outside the critical path | req: ARCH-CHECK-006 | unpark: a gate run is measured slower because of report code it does not need
- [ ] Configuration read into one explicit object instead of module globals mutated by `apply_config` | req: ARCH-CONFIG-060 | unpark: a config bug traced to a stale global
- [ ] Schema-upgrade fixtures: an engine upgrade keeps every confirmation unless the contract itself changed | req: ARCH-CHECK-006 | unpark: a consumer loses confirmations on an upgrade
- [ ] Compatibility aliases retired deliberately: inventory the consumers, publish the migration, then remove | req: ARCH-CMDREGISTRY-033 | unpark: an alias blocks a change
- [ ] The MCP tool list and the OpenAI schema generated from the same `COMMANDS` registry (ADR-0008) | req: ARCH-MCP-073 | unpark: the MCP freeze is lifted

### Adoption

- [ ] Template repo `hello-reqmap`: "Use this template" produces a gate that passes | req: ARCH-INIT-012 | unpark: an evaluator reports that `init` left them stranded
- [ ] An Apache-2.0 / MIT licence instead of BSL 1.1 | unpark: the first internal evaluator at a company that needs a grant

### Viewer

- [ ] RO search: rank on inflections, not on literal matches | unpark: a reader from outside the repo who uses the viewer in RO

## Not now

- Requirement history — `git log -L` on the requirement's block is enough
- `verifiable by:` filled from 2 to 54 — ADR-0016 rejected a marker at 4% adoption
- Atomic form (54 → ~665 nodes) — ADR-0025
- A hard fan-out check in the gate — it stays warn-only (ADR-0023)
- `clarify --levels` — until an ADR replaces 0031 (revisit 2027-03-06)
