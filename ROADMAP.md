# Roadmap

The product plan. It is not a log: what shipped lives in the CHANGELOG and in the git tags, and
a checked item leaves this file.

Edit it here, directly. The bars in the viewer's Gantt are written in `plugin-full/requirements/_planning.json`.

Format: `- [ ] text | req: ID` under Now/Next. Later needs `unpark:`.
Reserved headings: Now, Next, Later, Not now. Categories are `###` headings inside them.
Cadence: one release a week, not one per merge.

## Now

### Version 8.27

- [ ] A JSON source row whose contract is a list and has no title takes the list's first item as its title. Done when: `sourcerows.blocks` titles such a row with its first clause (today it gets the list's Python text, `['A refund goes to the card.', ...]`), a test proves it, and REQ-CUSTOMTRACE-1138 is read again and confirmed | req: REQ-CUSTOMTRACE-1138
- [ ] `retire --delete` and its requirement agree on string literals. Done when: the maintainer picks one: the clause says Python strings only, or the scanner blanks JS/TS strings as it does Python's; it lands with a test on a `.ts` member, and REQ-RETIRE-1130 is read again and confirmed | req: REQ-RETIRE-1130

### Adoption

- [ ] An outside evaluator, on their own repo, with no help at the gate. Done when: they have `uses: alxmax/requirement-manager/check@v8` on a tree you do not commit to | req: SYS-SSOT-001

### Version 8.25

- [ ] The words about `sync` match what it does. Done when: `docs/commands.md:62` and `mcp.py:127` say an edited confirmed contract is demoted to draft (they say `sync` refuses), and `app/scripts/sync-data.mjs:4` points to `sync`, not to `reqmap.py export`, which no longer exists | req: ARCH-MCP-073
- [ ] A release waits for the published-action smoke test. Done when: `release` does not go ahead while `dogfood.yml` is red | req: ARCH-SELFGATE-039
- [ ] The plan keeps only what is open. Done when: the bar for the shipped MCP server and the one for the archived consumer repo, with that repo's ROADMAP item and the done licence line, are gone, and the outside-evaluator bar stays | req: ARCH-RELEASE-072
- [ ] The `clause-without-case` questions are read family by family, as the guesses they are (ADR-0075: 7 of 20 real). Done when: ARCH-VIEWER-007's nine are read, and the next four families by count too: add the cases that are really missing with their tests, and leave a clause a case already proves as it is | req: ARCH-CLARIFY-062
- [x] Read and confirm REQ-EXTRACT-1099, REQ-VIEWER-1101, REQ-DRIFT-1103 and REQ-DRIFT-1104, the four drafts v8.24.0 to v8.24.4 shipped | req: REQ-DRIFT-1103
- [x] An audit is a recorded session (ADR-0076). Done when: `sync --audit-plan` writes a seeded plan to `requirements/_audit.json` once, `gate --audit` reports each audit rate as k/n with a Wilson 95% interval and its band, `_map.html` has an Audit view, `reqmap_review` carries the review prompt, and the MCP tool set and the six verbs are unchanged | req: ARCH-AUDITRUN-076
- [x] The map's release history reads the same on a branch and on its merge. Done when: a release's `first_commit` does not change when its branch is merged, so a pull request's gate and the branch's agree on map freshness (PR #405 failed on it) | req: ARCH-MAP-007
- [ ] `sync --accept-drift` does not report the drift it has just accepted. Done when: after `accepted drift on N confirmed contract(s)` and `lock updated.`, no RM018 line names those requirements | req: ARCH-PROMOTE-011
- [ ] The skill's engine copy has a requirement. Done when: `scripts/bundle_skill_engine.py` and its test are tagged to a confirmed requirement and `gate --risk` lists no untagged file | req: ARCH-SELFGATE-039
- [x] A repository describes its own trace convention (ADR-0077). Done when: `_config.json` can set extra tag forms (`TRACE_TAGS`), test-file globs (`TEST_FILE_PATTERNS`) and requirement sources kept as text, HTML or Markdown (`REQUIREMENT_SOURCES`), a repository written only in such a convention is read by the gate, and with no config the module is never loaded | req: ARCH-CUSTOMTRACE-077

## Next

### Drafts left after the 2026-11-21 read

- [ ] The bug-file drafts tested only `@integration` gain a `@unit` test. Done when: REQ-BUGS-1117, 1118, 1119, 1120, 1126, 1127, 1128, 1129 and 1131 each have a `@unit` `tested-by:` and `gate --full --strict` reports no RM010 for them once they are confirmed | req: ARCH-BUGS-078
- [ ] REQ-CHECK-1135, REQ-MAPSTAMP-1124, REQ-MAPSTAMP-1125 and REQ-SCAN-1136 gain a `@unit` test. Done when: each has a `@unit` `tested-by:` and `gate --full --strict` reports no RM010 for them once they are confirmed | req: ARCH-MAPSTAMP-079
- [ ] Drafts with more than 7 cases are split. Done when: REQ-BUGS-1116 (10 cases), REQ-BUGS-1119 (8) and REQ-BUGS-1127 (8) hold 7 or fewer, each criterion moved to the requirement that owns it | req: ARCH-BUGS-078
- [ ] Drafts with fewer than 3 cases gain the missing ones. Done when: REQ-CHECK-1135 (2 cases) and ARCH-MAPSTAMP-079 (1) reach 3, each with its test | req: ARCH-CHECK-006
- [ ] Code spread over 3 or more directories is kept as one capability or split. Done when: ARCH-BUGS-078, REQ-CHECK-1133 and REQ-VIEWER-1145 are each either split or exempted from `file-spread` with the reason in their Context | req: REQ-VIEWER-1145
- [ ] ARCH-MAPSTAMP-079 gets code and a test of its own, or becomes an aggregate. Done when: RM006 and RM007 no longer fire for it once it is confirmed | req: ARCH-MAPSTAMP-079
- [ ] The Bugs tab's confirmed requirements close the gaps the read found. Done when: REQ-BUGS-1122's clauses 4 (a saved bug shows at once) and 6 (cancelling the picker keeps the form) each have a case and a test, and REQ-BUGS-1123's CASE-2 test filters the list instead of passing the filter label by hand | req: REQ-BUGS-1122
- [ ] The trace block's caps are tested. Done when: a test proves a suggestion lists at most 3 tests and a design rule keeps at most 50 hits | req: REQ-MAP-1144
- [ ] A failed `retire --delete` leaves the member files as they were. Done when: when a later member file cannot be written, the tags already cut from earlier files are put back, and a test proves it | req: REQ-RETIRE-1130
- [ ] `init`'s "wire the gate" line names the engine path the repository runs. Done when: it prints the same relative or bare path as the assistant block below it, instead of a fixed `python scripts/reqmap.py gate` | req: ARCH-INIT-012
- [ ] The German viewer text is read by a native reader. Done when: each correction lands in `app/src/lib/i18n.de.js`, and the smoke check that every language translates the same strings still passes | req: REQ-VIEWER-943

### Planning and releasing

- [ ] `sync --release --apply` ticks the `ROADMAP.md` items whose requirement id matches a bar on the cut milestone | req: ARCH-RELEASE-072
- [ ] `gate --strict` fails a stale plan (`REQ-PLANSTALE-1013`); bare `gate` stays warn-only | req: ARCH-RELEASE-072

### Checking an existing repository with Copilot

- [ ] The Copilot hands-on matrix is run and recorded. Done when: the skill-discovery and MCP-start-directory rows of `docs/integrations.md` carry a dated PASS or FAIL on Windows and Linux, and a FAIL names the change it calls for | req: ARCH-MCP-073
- [ ] CSV and JSON requirement sources with a field map. Done when: `format: csv|json` with `fields` reads N rows into N requirements and a problem per bad row, in a lazy module, under its own ADR, with the core unchanged | req: ARCH-CUSTOMTRACE-077
- [ ] `init` writes `.github/copilot-instructions.md` when absent. Done when: the matrix passes, a second `init` leaves an existing file byte-identical, and a record supersedes ADR-0084's print-only line | req: ARCH-INIT-012
- [ ] The skill takes "check folders X against requirements in Z into W" as one request. Done when: the matrix passes; the skill writes the folder's `_config.json` only when absent, refuses an output folder inside the scanned code, prints the absolute `_map.html` path and lists the person's steps; no engine file changes | req: ARCH-INIT-012

## Later

### Engine surface

- [ ] The next cut from the engine: one capability from the removable list (`gate --risk`/`--audit`, `clarify`/decompose, `ask`, lint, `sync --retire`), with an ADR, a retire and the budget lowered in the same commit. The floor with the ROADMAP, MCP and `init` kept: 9,303 lines (ADR-0048) | req: ARCH-SELFGATE-039 | unpark: the maintainer names the capability
- [ ] Checking separated from report generation: `gate` computes the verdict and nothing else, rendering lives outside the critical path | req: ARCH-CHECK-006 | unpark: a gate run is measured slower because of report code it does not need
- [ ] Configuration read into one explicit object instead of module globals mutated by `apply_config` | req: ARCH-CONFIG-060 | unpark: a config bug traced to a stale global
- [ ] Schema-upgrade fixtures: an engine upgrade keeps every confirmation unless the contract itself changed | req: ARCH-CHECK-006 | unpark: a consumer loses confirmations on an upgrade
- [ ] Compatibility aliases retired deliberately: inventory the consumers, publish the migration, then remove | req: ARCH-CMDREGISTRY-033 | unpark: an alias blocks a change
- [ ] The MCP tool list and the OpenAI schema generated from the same `COMMANDS` registry (ADR-0008) | req: ARCH-MCP-073 | unpark: the MCP freeze is lifted

### Planning and releasing

- [ ] `sync --release` refuses a milestone whose own bars are not done (`plandrift.bar_done`), never over Now/Next items elsewhere in the plan | req: ARCH-RELEASE-072 | unpark: the done predicate is checked on five repositories it was not tuned on, with the false-block rate stated
- [ ] One release path in this repository: CI tags from `sync --release --json` (ADR-0040), or the docs stop saying the plan cuts the tag | req: ARCH-RELEASE-072 | unpark: the maintainer picks one
- [ ] `cadence` accepts `every: day` (working days) and `every: none` (milestones only) | req: REQ-PLANCADENCE-1000 | unpark: with the milestone-not-bar guidance in `docs/planning.md`, a consumer plan still ships more than one version a week

### CI of this repository

- [ ] The portability matrix shrinks to 3.9 and 3.12 on one OS once `release` no longer needs every cell | req: ARCH-PYFLOOR-040 | unpark: CI minutes become a constraint

### Requirement levels

- [ ] RM032's tree checks become an error under `--strict` | req: REQ-TRACE-934 | unpark: `gate --full --strict` with them is run on this corpus and two consumer corpora, and the count per check is recorded in a record superseding ADR-0064's warn-only clause
- [ ] The fan-out band is read on the drafts `init` writes, not only through its write-time note | req: REQ-FANOUT-852 | unpark: lint with drafts included is run on a fresh `init` of two consumer repos and on this corpus, counting the over-band parents and the findings it adds

### Adoption

- [ ] Template repo `hello-reqmap`: "Use this template" produces a gate that passes | req: ARCH-INIT-012 | unpark: an evaluator reports that `init` left them stranded
- [x] An Apache-2.0 / MIT licence instead of BSL 1.1 | done: Apache-2.0, ADR-0069, 2026-10-13

### Checking an existing repository

- [ ] Several code folders in one check (`--code` repeated, or a list in `_config.json`) | req: ARCH-SCAN-002 | unpark: the common-parent plus `.reqmapignore` route fails a real run; the change must leave a single `--code` byte-identical in every lock, give two `a.py` files in different folders distinct members, and pay its core lines with an equal cut
- [ ] YAML requirement sources | req: ARCH-CUSTOMTRACE-077 | unpark: a second independent corpus needs YAML; the reader names its supported grammar in an ADR, reports a `file:line` problem per unsupported construct, and takes a block scalar's title from its folded text, not its first raw line
- [ ] Clarify questions with answer options saved and read by `sync` | req: ARCH-CLARIFY-062 | unpark: one real audit run with sources has happened, an answer rate is measured over five audits, a record supersedes ADR-0058's choice, and each saved answer carries its rule and its clause's hash so a changed clause reopens it. Until then the skill offers the options and the person edits the requirement
- [ ] A doctor that reports, per assistant, which of skill, MCP config and instructions is present, with the fix | req: ARCH-INIT-012 | unpark: the Copilot matrix passes and a person reports a setup they could not diagnose from the guide
- [ ] Audit packets for parallel reviewers (`--audit-plan --batches N`) and an ingest check | req: ARCH-AUDITRUN-076 | unpark: a recorded session of 30 or more requirements shows the hand step costs over 5 minutes each; ingest only validates and never writes `_audit.json`, a packet carries its contract hash and capped code, run 2 is a separate packet in a seeded order, and ADR-0076's k/n with Wilson intervals stays as it is
- [ ] A Copilot agent file for audit runs (`.github/agents/*.agent.md`) | req: ARCH-AUDITRUN-076 | unpark: the Copilot matrix passes and the file is generated from, or links to, the skill's `references/audit.md` instead of copying its prompt

### Viewer

- [ ] RO search: rank on inflections, not on literal matches | unpark: a reader from outside the repo who uses the viewer in RO
- [ ] A day-wide view for a short plan: the default day width follows the shortest bar, so one-day versions sit on one row | req: REQ-PLANSTACK-1012 | unpark: a one-version-a-day plan rendered at the current day width and at a day-view width shows fewer rows and no overlapping labels in the day view
- [ ] A fingerprint of the vendored `_map_viewer.html` (line endings normalised, data block removed), reported by `gate --audit` when it differs | req: ARCH-VIEWER-007 | unpark: a second consumer is found with a hand-edited vendored viewer

## Not now

- Requirement history — `git log -L` on the requirement's block is enough
- `verifiable by:` filled from 2 to 54 — ADR-0016 rejected a marker at 4% adoption
- Atomic form (54 → ~665 nodes) — ADR-0025
- A hard fan-out check in the gate — it stays warn-only (ADR-0023)
- `clarify --levels` — until an ADR replaces 0031 (revisit 2027-03-06)
