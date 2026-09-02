# TODO

<!-- Items here appear in the Roadmap tab of the viewer.
     Format: - [ ] Name | lane: bus|feature|ops
     Group by milestone version: ## vX.Y -->

## v1.13
- [x] Roadmap tab (Gantt viewer)         | lane: feature
- [x] TODO.md template + engine parsing  | lane: feature

## v1.14
- [x] Requirement readability linter (lint) | lane: feature
- [x] Single-requirement dossier (show)   | lane: feature
- [x] Duplicate-capability detector (similar) | lane: feature
- [x] Corpus health snapshot (health)     | lane: ops
- [x] promote-todo command               | lane: feature
- [x] Gate validation for milestone IDs  | lane: ops
- [x] Requirement quality checker (AI)   | lane: feature

## v1.15
- [x] Test-link integrity gate check (testlink) | lane: ops
- [x] Scan cache (opt-in `--cache` flag — ARCH-SCANCACHE-023) | lane: ops

## v1.16
<!-- Senate fix plan 2026-06-12 (runs/senate/2026-06-12_091906-requirement-manager-fix-plan.json, verdict MODIFY).
     Detail spec: docs/PLAN-senate-fix-2026-06-12.md -->
- [x] Phantom-member fix: context-aware tag scan (fence/backtick/indent + .py string state) | lane: bus
- [x] Drift doc reconciliation (direction B): SKILL.md, CLAUDE.md, SYS-SSOT-001 AC-1 split + severity table | lane: ops
- [x] check --strict (promotes test-link integrity + confirmed-drift to error) | lane: feature
- [x] check --json (structured gate output, exit-code aligned) | lane: feature
- [x] Frontmatter '#' scalar truncation fix | lane: bus
- [x] Off-status drift blind spot fix | lane: bus
- [x] check --since <ref> (git-scoped gate, full-scan fallback + WARN) | lane: feature

## v1.17
<!-- Gap found 2026-06-13 while updating the Consilium architecture explainer.
     A whole-system generated doc (docs/architecture.html, built from many .jsx
     sources that each cover several requirements) has no single
     `generated-from: <ID>`, so doc-sync skips it entirely. Its Conservator-first
     voice order drifted for days after the requirements + code moved to
     Generator-first, and reqmap never flagged it — Consilium had to work around
     it with a bespoke check_doc_drift gate. reqmap should catch this class. -->
- [x] `generated-from:` accepting >1 requirement ID — drift a system/explainer doc when ANY referenced requirement changes | lane: feature
- [x] WARN when a large docs/ HTML/generated bundle carries no `generated-from:` tag at all (surface the doc-sync blind spot instead of silently ignoring it) | lane: ops

## v1.18
<!-- Gap found 2026-06-19 while reconciling Consilium's requirements after the
     Trias 6->4 skeptic-lever redesign. CONSILIUM-MODE-TRIAS-001 (status: confirmed)
     described the OLD model (3 pre-vote Skeptics, revise-before-vote) while the
     shipped code/member (modes/trias.md) had moved to the NEW model (vote, then 1
     post-vote skeptic_on_chosen). reqmap never flagged it. Root cause: _reqlock.json
     stores ONE hash per requirement = hash(requirement contract), with no member-
     content hash. So drift only fires in the prose-ahead-of-code direction (the
     requirement .md was edited); the reverse — a MEMBER (code/doc) changed while the
     requirement prose stayed put — leaves the requirement hash unchanged and is
     structurally invisible. The skill documents intent-sync as non-automatable and
     surfaces it at human review; this is the mechanical half that could move it left.
     Extra tell that was present but unused: the requirement's depends_on/graph had
     already been updated to the new model (TRIAS -> skeptic_on_chosen edge) while the
     prose contract still described the old one — an internal contradiction. -->
- [x] Member-hash drift (reverse direction): record member content hashes in `_reqlock.json` and WARN when a `confirmed` requirement's member changed since lock but the requirement was not re-touched/re-confirmed — catches "behavior shipped, spec not updated". Default WARN (likely `--strict`-promotable) to bound the noise of every code edit nagging its requirement. | lane: feature
      <!-- Done as ARCH-MEMBERDRIFT-027: stored in a versioned sidecar `_memberlock.json` (not _reqlock.json) so the cross-repo contract stays byte-stable; scoped to mono-requirement files to avoid alarm fatigue. Both Senate blocking conditions addressed. -->

- [x] ~~Internal-consistency lint: flag a requirement whose structured fields moved to a new model while its prose Contract/AC still assert the superseded model.~~ **DROPPED** | lane: feature
      <!-- DROPPED (not implemented). Senate 2026-06-19 (runs/senate/2026-06-19_224727-reqmap-item4-internal-consistency-lint.json) + closed tracking issue #120. Decision: do not build. The naive 'depends_on id absent from prose' check is empirically refuted (78.6% false-positive on this corpus, and would have missed the motivating TRIAS case — an added edge, not an absent id). The only viable detector (baseline-aware depends_on diff) needs a persisted baseline ~= ITEM 3's machinery for a warn-only, n=1 signal — disproportionate. The residual gap (a requirement's own frontmatter vs its prose) is narrow and caught by human PR review; the member-changed half is covered by ARCH-MEMBERDRIFT-027. Revisit only if a second real frontmatter-vs-prose contradiction recurs. -->

## v1.35
<!-- Backfilled 2026-06-21 (TODO/roadmap hygiene): shipped capabilities whose milestone
     sections were never recorded here. Senate 2026-06-21 (runs/senate/*roadmap-coherence)
     chose manual TODO hygiene over building a TODO<->requirement coherence-check feature
     (demand n=1; the only stale TODO observed was this repo's own). -->
- [x] Project presentation page (`site`): inject/refresh engine-owned nav + stats regions into docs/architecture.html (scaffold if absent) | lane: feature
      <!-- ARCH-SITE-026 -->

## v2.4
- [x] Excalidraw scene builder — core stdlib API (.excalidraw scene + self-contained HTML viewer) | lane: feature
      <!-- ARCH-EXCALIDRAW-030 -->
- [x] Excalidraw quality gates at save() (overlap, crossing, legend, text-overflow, text-overlap; later: short-arrow, label-fit) | lane: feature
      <!-- ARCH-EXCALIDRAW-031 -->
- [x] Excalidraw builder CLI verbs (`render` a scene → viewer; `discover` a repo → generator stub) | lane: feature
      <!-- ARCH-EXCALIDRAW-032 -->

## v2.6
- [x] Untagged-code coverage signal: read-only `untagged` count in `health` (code traced to no requirement) | lane: feature
      <!-- ARCH-COVERAGE-029. Senate 2026-06-21 (enforce-all-code DEEPLY_SPLIT): a hard coverage gate was rejected; only this read-only signal shipped. -->

## v2.7
<!-- Multi-platform Phase 1 — SHIPPED (PR #127). Senate 2026-06-21 (runs/senate/2026-06-21_110220-reqmap-multiplatform-mcp.json, verdict MODIFY).
     Detail spec: docs/superpowers/specs/2026-06-21-reqmap-multiplatform-command-registry-design.md
     Problem: the prior multi-AI artifacts (tool_definition.json + 3 SKILL.universal.md) were hand-maintained
     mirrors of the CLI with no sync mechanism — already drifting. Fix: one declarative command registry as
     the single source of truth, generate the artifacts from it, drift-guard them in the gate. -->
- [x] Command registry: one declarative `COMMANDS` structure in reqmap.py; argparse choices derived from it (hand-written `choices=[...]` literal removed). Dispatch ladder left intact (de-risked); CLI behaviour byte-identical (TestCli unchanged). | lane: bus
      <!-- ARCH-CMDREGISTRY-033 -->
- [x] Generate `tool_definition.json` (function-calling schema) + the command-reference TABLE inside SKILL.universal.md (delimited region; curated WHY/WHEN prose stays hand-authored) from the registry. | lane: feature
- [x] Drift-guard: `gate` (incl. `--json`) regenerates the artifacts in-memory and byte-compares vs committed → error (exit 1), mirroring `map --check`. | lane: ops

## v2.12
<!-- Backfilled 2026-08-17 (second roadmap-hygiene pass). The same drift the v1.35 section
     records recurred: the file stopped at v2.8 while v2.12-v2.16 shipped. The v1.35 note
     chose manual hygiene over building a TODO<->requirement coherence check, on the grounds
     that demand was n=1 — this repo's own stale TODO. It is now n=2, same repo, same
     failure mode. -->
- [x] Registry lag in `health`: commits since the requirements dir was last touched | lane: ops
      <!-- ARCH-REGISTRYLAG-035 -->

## v2.13
- [x] Ranked free-text requirement search (`search`), shared scoring model with the viewer | lane: feature
      <!-- ARCH-SEARCH-036 -->

## v2.14
- [x] Requirement clarity lint enforced in CI, the dev hook and the published action | lane: ops

## v2.15
- [x] Plain present requirement voice: named subject, no `shall`, tightened lint ceilings | lane: feature

## v2.16
- [x] V-model verification levels: `@unit`/`@integration`/`@system` on `tested-by:`, `validated-against:` activated as the validation link | lane: feature
      <!-- ARCH-VLEVEL-037 -->

## v2.32 — TO VERIFY
<!-- Nine proposals drafted 2026-09-02, in dependency order. Nothing here is decided.
     Audited the same day: runs/senate/2026-09-02_223252-senate-reqmap-ten-proposals-traceability-and-layers.json -->

- [ ] TO VERIFY: decide the system grouping — 5-8 needs instead of one | lane: ops
      <!-- SYS-SSOT-001 alone cannot be the apex: 54 architectures under one need violates any
           fan-out (54/20 = 2.7, 54/5 = 10.8). `area:` is at 0, so the grouping cannot be
           derived automatically. Blocks everything that follows.
           Cost: a decision, no code. -->

- [ ] TO VERIFY: satisfies from 11 to 54 | lane: ops
      <!-- Depends on the item above. This is the real gain: 80% of requirements trace to
           nothing, and `depends_on` cannot substitute — it is a composition axis, not a level
           axis. Without it there is no pyramid, whatever the layers are called.
           Cost: 43 files, one line each. -->

- [ ] TO VERIFY: verifiable by: from 2 to 54 | lane: ops
      <!-- Independent of the two items above; can be done any time. Honest warning: ADR-0016
           used this very marker's 4% adoption as its reason to reject a similar marker.
           Raising it is easy; keeping it raised is the unproven part. If it has decayed at 90
           days, the correct conclusion is to delete it, not to refill it. -->

- [ ] TO VERIFY: rename by alias — need->system, aggregate->architecture | lane: feature
      <!-- Both old names stay valid in VALID_LAYER. need->system costs 1 file,
           aggregate->architecture costs 0 (unused). `bus` and `feature` stay untouched — they
           are a fan-in axis, not a level axis. Zero consumers broken, no semver major.
           ~20 lines + tests. -->

- [ ] TO VERIFY: decide the fate of the architecture layer — populate it or delete it | lane: ops
      <!-- `aggregate` is built, tested (it has acceptance criteria in ARCH-PROMOTE-011 and
           ARCH-TRACE-020) and used by zero requirements. By this repo's own standard — ADR-0016
           rejected a mechanism at 4% adoption — a layer at 0% should be deleted, not kept
           "for later". -->

- [ ] TO VERIFY: fan-out check 5-20, warn-only | lane: feature
      <!-- It would fire today on 9 of 54 (17%) — inside the 5-40% band ADR-0016 requires,
           unlike the 75-word ceiling which catches nothing. And retroactively validated: 3 of
           the 4 requirements over 20 clauses already carry a hand-written `lint_exempt:`. -->

- [ ] TO VERIFY: split ARCH-MAP-007 (35 clauses) | lane: ops
      <!-- The only one over 20 without an exemption — so the only one whose size has never
           been judged in writing. -->

- [ ] TO VERIFY: decide the unit for long-sentence / statement-too-long | lane: bus
      <!-- The finding from the implementation: they measure physical lines, and the files are
           wrapped at ~95 columns, so they report 0 across the corpus — not because the prose
           is short. Switching to clauses would make them flag 107 and 154 clauses.
           A decision, not a bug — left alone deliberately. -->

- [ ] TO VERIFY: form: atomic — 54 -> ~665 nodes. Not now | lane: feature
      <!-- Depends on items 1-5 and requires ~305 new scenarios, each with a test. The number
           that matters is not the file explosion (2x text, not 7x) but the acceptance work.
           Parked until 1-5 are closed. -->

## v2.8 (deferred — demand-gated)
<!-- Multi-platform Phase 2: the MCP server. Senate 2026-06-21 deferred it: all 9 senators converged that
     direct-CLI already covers every current shell-capable assistant (Claude Code, Copilot CLI, Gemini CLI,
     Codex), so an MCP server unlocks zero platforms today, and demand is unproven (Deming n=0). BUILD ONLY
     when ALL hold: (1) a named consumer that genuinely cannot use direct-CLI; (2) a conformance test
     (initialize -> tools/list -> tools/call over stdio); (3) read-only-by-default mutation guard
     (--allow-writes to expose sync/confirm/map); (4) init seeds the artifacts + gate warns when absent;
     (5) stdlib-only stdio JSON-RPC against a pinned MCP protocol version, OR adopt the SDK and drop the
     zero-dependency claim for that module only. -->
- [ ] MCP server exposing reqmap commands as MCP tools — stdlib-only, generated from the command registry. Demand-gated; see conditions above. | lane: feature

## v2.9
<!-- Roadmap drafted 2026-08-18 (v2.9-v3 plan, tiers 0-1: prove the thesis — pick a
     beachhead and make the SSOT claim demonstrable on this repo's own tree).

     Known breaks behind the data.js and scan-reach items below:
     - app/src/lib/data.js carries 286 lines of BAKED requirement data (13 reqs,
       manually copied from the registry: contract, acceptance, members) — a second,
       unsynced source of truth in a tool whose pitch is "one". If ARCH-PARSE-001
       changes, the viewer shows the stale version and no gate notices — the worst
       possible position for a counter-example.
     - docs/ sits outside the scan root (CI runs from plugin/), so ARCH-DOCBUNDLE-026
       — built to catch generated HTML bundles with no lineage tag, 50KB threshold —
       never sees its own docs/full_architecture.html (99KB). The rule exists and is
       structurally excluded from the one place it should apply.
     - Generated-artifact policy is inconsistent: Excalidraw output is gitignored
       (source = generator), but the viewer and docs/ are committed blobs (217KB,
       145KB) with no CI rebuild check — same problem class, two opposite answers.
       diagrams/README.md already documents the right one.

     Items 2-4 chain into each other: the scan work makes the tagging possible, and
     the tagging produces the demo. -->
- [ ] Decide the beachhead domain (4 named candidates) — tie-break on which gets one external user in 30 days; pipelines currently leads since this repo is already its own demo | lane: ops
- [x] Rewrite the README lead around agent drift, not stale specs; fix the ~3700-vs-5,199 line-count claim; add TODO.md and test_reqmap.py to the layout tree | lane: ops
      <!-- Real count was 5,307, not 5,199 — TODO's own estimate was stale too; README now says ~5300. -->
- [x] Extend scan reach: add .sh/.tf to CODE_EXTS, extensionless basename matching for Dockerfile/Makefile, let the scan root reach the repo root instead of stopping at plugin/ — and cover docs/, not just .github/, so ARCH-DOCBUNDLE-026 finally sees its own bundle | lane: bus
      <!-- Shipped as `--code ..`/`--code .` for THIS repo's CI/hook only (Trias deliberation
           .consilium/runs/2026-08-18_1640_v29-scan-root-codeexts-viewer-trias.json rejected
           auto-widening the shared engine default as a silent-failure risk to consumer repos
           scoped to a subdirectory on purpose). Also widened Dockerfile/Makefile basename
           matching to the standard git hook names (pre-commit, pre-push, ...) — needed for the
           next item below. ARCH-DOCBUNDLE-026 now WARNs on docs/full_architecture.html, confirmed live. -->
- [x] Tag this repo's own pipeline (ci.yml, check/action.yml, .githooks/, sync_reqmap.sh) — currently zero tags across all of them | lane: ops
      <!-- ARCH-SELFGATE-039. A confirmed requirement whose members are all outside plugin/
           genuinely ERRORs under the narrow gate invocation (not just a coverage miss) —
           documented in CLAUDE.md as an accepted, loud-not-silent consequence. -->
- [x] Ship one worked example end-to-end: one requirement, one agent session, one drift the gate caught, real terminal output — every claim on the README is currently architectural, none demonstrated | lane: ops
      <!-- README "Worked example" section — real captured output, run in an isolated sandbox
           (not in-place) to avoid touching this repo's own committed lock state. -->
- [x] app/src/lib/data.js's BAKED requirement data: add a CI/gate step that diffs it against the live registry | lane: feature
      <!-- Kept as a hand-maintained fallback (preserves the zero-dependency demo story) rather
           than removed/generated at build time — a new warn-only `gate` check flags drifted IDs
           instead of failing the build on divergence (the majority Trias vote's design: warn,
           don't gate, since the viewer's fallback fixture is explicitly demo data). Caught 2 real
           bugs in its own first implementation during code review (bracket-truncating regex,
           uncaught UnicodeDecodeError) — both fixed before shipping. -->
- [x] Fix the .reqmapignore comment claiming the viewer is "tested via npm build" — there is no npm step in CI | lane: ops
- [x] `lint` check for redundant "shall"/"must" on a Contract clause (ARCH-LINTCHECKS-025 AC-10) | lane: feature
      <!-- PR #186. The Contract section already opens with "Every line in this section is
           binding.", so the modal is dead weight — and in a non-English requirement corpus
           `shall` is also a stray anglicism, caught in a consumer repo's 29 files / 261 places
           before this check existed. -->
- [x] Opt-in requirement-content translation: `reqmap.py translate` + viewer badge (ARCH-TRANSLATE-044) | lane: feature
      <!-- PR #187. The v2.23.0 EN/RO toggle (line below) covers UI chrome only, which fails a
           reader who does not read the corpus's language AT ALL. `translate` is manual/opt-in,
           the only subcommand that shells out to `claude -p`, never called by gate/sync/lint/
           map/CI — cache is read-only-inlined by map/export. Every translated field renders
           behind a visible "machine-translated, unreviewed" badge; falls back to source text
           with no cache entry. Scoped from a 9-senator Senate audit (MODIFY, 3 blocking + 3
           advisory conditions) plus a follow-up request for majority-language corpus detection
           instead of mandatory per-file `lang:` tagging. -->
- [x] Scan-evidence run 6 — Management_Dashboard (TS/TSX, SQL, shell, Dockerfile, Caddyfile, Prisma, YAML, JSON, Markdown): four engine defects found and fixed in v2.27.0 | lane: ops
      <!-- 2026-08-25, PR #191. Findings: (1) tags in Caddyfile / schema.prisma / Dockerfile.converter
           were invisible — types added + ARCH-UNSCANNEDTAG-045 gate warning for the next case;
           (2) realpath on every walked dir = 62% of gate time (4,900 upload folders) — name-gated,
           plus .reqmapignore `/**` patterns prune the walk: 11.2 s -> 4.1 s -> 0.6 s;
           (3) _map.json "stale" on engine_version alone — excluded from the freshness diff;
           (4) `next` listed CLAUDE.md/TODO.md as untagged — ignore bucket honoured.
           JSON: only config JSON present (tsconfig, package.json, eslintrc) — no tagging
           convention needed on this evidence; revisit with a Grafana/OpenAPI-JSON repo.
           Consumer-side (handed back, not engine): 42/44 draft + 0 confirmed -> triage; stale
           committed _findings.md (caught by v2.26.0); no reqmap step in its CI; storage/ and
           prisma/migrations/ untagged; stray empty `Caddyfile;C` dir.
           Remaining runs of the matrix: 1 C/C++ (the item below), 2 frontend, 3 infra/pipelines,
           4 backend, 5 markdown-heavy. -->
- [x] Scan-evidence runs 1–5 — zlib+curl (C/C++), excalidraw (TS/React), awesome-compose (infra), gin+httpx (Go/Python), fabric (Markdown prompts): ten engine fixes in v2.28.0 | lane: ops
      <!-- 2026-08-25, PR #192, five Sonnet subagents in parallel on the same protocol (inventory,
           coverage, plan, draft, gate, next/health/dupes, native-comment probe, edge probes).
           Per run:
           1 C/C++ (zlib 271 files, curl 4,449): scanner 16/16 probes OK, 0 false tags; `plan` gave
             0 candidates for zlib and only tests/*.py for curl (CANDIDATE_EXTS); `dupes | head`
             OSError 22 on Windows. Fixed: plan reach, ARCH-PIPE-046. Left: curl's 2,066 extensionless
             tests/data/test### fixtures are outside any extension-based scan.
           2 frontend (excalidraw): .scss = 82 files = the only stylesheet format, invisible;
             plan 663 vs draft 687; draft ignored 15 signatures plan had read; dupes 1,748 pairs.
             Fixed: exts, plan reach, observed surface, dupes placeholder skip.
           3 infra (awesome-compose, 502 files, 35 Dockerfiles): plan 0 infra candidates; tagged
             .env skipped by the unscanned-tag check; .cs/.vue/.php invisible. Fixed: all three.
             Left (design): a tag in a YAML value string or a Dockerfile heredoc counts — TAG_RE is
             context-free on purpose; lowercase `dockerfile` is not a Dockerfile (case-sensitive,
             warned correctly).
           4 backend (gin, httpx): zero defects — string masking, test-link, verifies:#AC-N,
             syntax-error and 5 MB files all per contract. Observations fixed: class methods in
             plan facts (httpx _client.py: 3 helpers shown, 78 methods hidden), is_test flag.
           5 markdown (fabric, 396 .md, 255 patterns/*/system.md): lowercase readme.md drafted
             (case-sensitive README rule); 204/255 drafts said "no section headings" because the
             corpus uses `#` for every section; dupes 6,340 pairs. Fixed: all three. Left: .rst/
             .txt/.adoc/.ipynb/.mdx outside the scan; "IDENTITY and PURPOSE" is the H1 title of
             151/255 patterns (path-aware ids still distinct).
           JSON convention: still no evidence for one — every JSON seen was config or lockfile. -->
- [x] Bring app/src/ under the gate: real per-file `# implements:`/`generated-from:` tagging of app/src/**/*.jsx | lane: ops
      <!-- Deliberately deferred (2-1 majority in the same Trias deliberation): app/ stays in the
           repo-root .reqmapignore's `app/**` exclusion this round. Revisit once the demand is
           real, not before.
           Closed 2026-09-02: 18 files tagged (app/src/** + install-viewer.mjs,
           vite.viewer.config.js -> ARCH-VIEWER-007; search.js -> ARCH-SEARCH-036; i18n.jsx +
           SpecView.jsx also ARCH-TRANSLATE-044; ssr-smoke.jsx tested-by both). `app/**` left the
           root .reqmapignore; only app/dist*, app/.vite and the SSR bundle stay excluded. -->

## v3
<!-- Tiers 2-5 of the same v2.9-v3 roadmap: survive a skeptic's ten minutes, the
     engineering bar, hardening/scale, and reach.
     Parked: closing the V-model (system layer + level-correspondence gating).
     Unpark only if a regulated user asks — and record it as a decision so it reads
     as scoped-out rather than missed. -->
- [x] Fix check@v1: frozen at v2.1.0 while shipping v2.17.0 — re-point it or pull it from the README | lane: ops
      <!-- Neither: re-pointing @v1 would have BROKEN consumers (the action gained two
           default-on steps, freshness + lint, since v2.1.0 — a green build could newly
           fail), so @v1 is frozen and the line moved to @v2. The rot itself is the real
           fix: ci.yml's release job force-moves the alias onto every released commit,
           and check_versions.py asserts action.yml/README/CLAUDE.md name the same major
           (the documented `uses:` line is the SSOT — no separate version file).
           ARCH-SELFGATE-039 AC-6/AC-7. Shipped in v2.18.1. -->
- [x] Scan vs `.gitignore`: a gitignored-but-tagged file silently changes committed generated artifacts — make the scan skip gitignored paths, or WARN when a member resolves to one | lane: bus
      <!-- Shipped as ARCH-TRACKED-042, the WARN half the item's own note argued for. Built
           on UNTRACKED rather than gitignored: it is the property that actually matters
           (a merely-uncommitted file breaks reproducibility identically), one `git ls-files`
           answers both, and it avoids hand-parsing gitignore semantics or one check-ignore
           call per path. Fail-open outside a work tree, warn-only, exit code untouched —
           a consumer may tag an ignored file deliberately. -->
      <!-- Found 2026-08-20 during the check@v2 work (PR #167), twice in one session:
           `.worktrees/**` (an isolated subagent worktree is a FULL second copy of the
           tree — 527 members instead of 261, plus 3 dangling-tag ERRORs from the copies'
           README illustration ids) and `.consilium/FEEDBACK.html` (gitignored, but carries
           a real `generated-from:` tag — 261 members locally vs 260 on CI, so `map --check`
           failed on CI for a file that is not in the repo). Both were fixed by hand-adding
           a `.reqmapignore` entry mirroring `.gitignore` — which is the manual step that
           keeps being missed. A committed generated artifact must depend only on TRACKED
           files, and nothing enforces that today; the failure is silent locally and only
           surfaces as a confusing CI-only staleness error.
           Design tension to settle before building: reading `.gitignore` means either
           shelling out to `git check-ignore` (fails in a non-git tree / adds a git
           dependency to a stdlib-only engine) or hand-parsing gitignore semantics
           (negations, dir-only rules, nested files — a known-deep rabbit hole). The cheap
           middle ground is the WARN half: `map`/`gate` shell out to git ONCE, best-effort,
           and warn when a discovered member is gitignored — loud instead of silent, no
           behaviour change for consumer repos that deliberately tag ignored files. -->
- [x] Add an npm job asserting `git diff --exit-code` on plugin/scripts/_map_viewer.html, and the same check for regenerated Excalidraw diagrams — closes the committed-build-artifact hole for both | lane: ops
      <!-- Shipped in v2.19.0 as the `artifacts` job. Both builds were measured first and
           are byte-reproducible: `npm run build:viewer` reproduced the committed 217KB
           viewer exactly, and make_full_architecture.py reproduced docs/full_architecture.html
           exactly, twice. The viewer half is a literal `git diff --exit-code` (the build
           overwrites the committed file in place); the diagram half builds into a temp dir
           and compares, because the generator drops a sibling .excalidraw and
           `docs/*.excalidraw` is hard-blocked by .gitignore. `release` now needs this job. Filed as
           ARCH-REPRO-041, split out of ARCH-SELFGATE-039 after the clarity lint flagged
           the merged requirement at 8 acceptance criteria.
           NOT covered: docs/architecture.html, which is hand-authored — its engine-owned
           regions are already checked by `map --check`. -->
- [x] Stop squashing main; land the next change as a visible PR — this also revives the changelog gate, which currently no-ops because HEAD~1 doesn't resolve | lane: ops
      <!-- Done 2026-08-20: PR #167 (check@v2) landed as a real merge commit, e56886c.
           HEAD~1 resolves again, so the changelog-entry gate is live rather than a
           silent no-op — and the release job proved itself on that same merge: it cut
           v2.18.1 and force-moved the @v2 alias onto the released commit. -->
- [x] Extract ADRs to docs/adr/ — ten decisions pulled out of changelog prose, including the deliberate V-model omission | lane: ops
      <!-- 13 records, not 10: the changelog carried more load-bearing decisions than the item
           estimated. Three are REJECTIONS (internal-consistency lint, the V-model pairing
           table folded into ADR-0007, auto-widening the scan root) — a rejection is worth as
           much as an acceptance here, since without the record the gap reads as an oversight
           and someone re-proposes the version that was already measured and refuted. Each
           record carries the evidence it was decided on and its revisit condition. Linked
           from README, CLAUDE.md and CONTRIBUTING.md; not linked into docs/architecture.html,
           whose nav is an engine-owned region. -->
- [x] CI matrix: Python 3.9/3.12/3.13 x ubuntu/windows — prove the `-X utf8` usage actually holds | lane: ops
      <!-- Shipped in v2.19.0 as a separate `tests` job (6 cells, fail-fast: false) running
           every suite. Deliberately NOT a matrixed gate-and-tests: the gate is one
           authoritative verdict on the requirement corpus, not a per-interpreter one.
           `release` now needs the matrix too; `deploy-map` still needs only the gate. -->
- [x] Coverage + ruff on the engine, published in the job summary | lane: ops
      <!-- New `quality` job in ci.yml. Coverage came out at 92% (2492/2721 statements)
           and ruff's bug-class rules (E9,F) were already clean, which set the design:
           E9,F is the only failing subset — meaningful but unable to redden a green
           build — and ruff's other 132 findings are published as advisory, since most
           of them (96 x UP032 f-string, 8 x blind-except) describe deliberate choices
           in this engine rather than defects. No coverage floor yet: publish the number
           first, argue about a threshold once there is a series. Not in `release`'s
           needs — it is the one job that installs from PyPI (both tools pinned). -->
- [x] Declare and assert the Python floor (3.7 today, accidental) | lane: bus
      <!-- ARCH-PYFLOOR-040, v2.19.0. Floor = 3.9, chosen as the oldest version CI can
           actually run rather than the oldest the code tolerates (3.7): 3.7/3.8 are not
           installable on current GitHub runners, so supporting them would be untested.
           A test asserts MIN_PYTHON == the oldest python in the CI matrix, so the two
           cannot drift apart. Cannot catch <3.6 (f-strings fail at compile time). -->
- [x] Fix the upgrade path: warn_if_stale is silent in CI, exactly where it matters | lane: bus
      <!-- Shipped in v2.22.0 as ARCH-STALEENGINE-043, in the ACTION rather than the engine:
           a stale vendored reqmap.py does not contain the check that would report it stale,
           so the detector has to run from something the consumer does not vendor.
           check/engine_staleness.py compares the vendored MAP_ENGINE_VERSION against the
           engine in the action's own checkout and annotates the run (`stale-engine`:
           warn|error|off, default warn). Kept on @v2 deliberately — warn-only cannot turn a
           green build red, and a new major would have stranded exactly the never-updated
           pins this exists to reach. -->
- [x] Repo hygiene: CONTRIBUTING, SECURITY.md, issue and PR templates | lane: ops
      <!-- CONTRIBUTING.md, SECURITY.md, .github/PULL_REQUEST_TEMPLATE.md and two issue
           forms (bug / feature). Written against what this repo actually enforces — the
           gate loop, the two-version-number rule, the stdlib-only constraint, the
           demand-gated stance on new features — rather than generic boilerplate. SECURITY
           routes to GitHub private advisories (no maintainer email published) and states
           the real scope: the action runs in consumer CI, and the viewer inlines repo
           content into a <script> block. -->
- [x] Adversarial tests on injected HTML (</script>, U+2028, lone surrogates) and a published benchmark on a 10k-file tree | lane: bus
      <!-- `</script>` was already covered. The other two were real and both are fixed:
           U+2028/U+2029 were emitted RAW into the inlined <script> (they end a line in
           JavaScript but not in JSON, so a pre-ES2019 engine reads an unterminated string
           and the whole viewer dies on one character in one title), and a lone surrogate
           CRASHED `map` outright with UnicodeEncodeError — reachable in the real world via
           a filename whose bytes are not valid UTF-8, since os.walk surrogate-escapes those
           and member paths go into the map. Now escaped / degraded to U+FFFD, with the
           tests written first. Benchmark: scripts/benchmark_scan.py, numbers published in
           the README. -->
- [x] One tree walk instead of three: `gate` calls scan_members + scan_ac_verifies + scan_test_levels, each opening every file — 3.06s + 2.76s + 2.81s of its 8.49s on a 10k-file tree | lane: bus
      <!-- Shipped as `scan_all` (ARCH-SCAN-002 AC-7). Not a merge of three loops: the walk
           moved into one `_walk_code` generator, `_scan_file_tags` gained an optional
           `lines` argument so a caller that already read the file can hand the content
           over, and the two coverage scanners' identical masking loops became one pass
           feeding both regexes — preserving the asymmetry that only the levelled scan
           strips backticks first. Measured on the same 10k tree: scan_all 2.53s (a single
           walk cost 2.62s before), gate 8.49s -> 2.46s, scan+gate ~11s -> ~5s. Safety
           argument is a test asserting scan_all == the three scanners, run against both a
           mixed fixture and this repo's real corpus. --cache stays on scan_members alone:
           it is off on the CI path this speeds up, and duplicating its invalidation rules
           would trade a measured win for a correctness risk. -->
      <!-- Found 2026-08-20 by the benchmark above, which was written to publish a number and
           ended up explaining it. The three scanners have different masking rules (fences,
           string literals, tag vocabularies), so this is a real refactor and not a merge of
           three loops — hence its own item rather than a drive-by. Not urgent: 8.5s for 10k
           files is acceptable, and the cost is invisible below ~1k files. -->
- [x] Settle the 5,199-line module: split with a concatenating build, or keep single-file with an ADR plus a CI line-count budget | lane: bus
      <!-- Settled 2026-08-21 as ADR-0014: keep one file, NO split and NO line-count gate.
           Nine-senator Senate audit, two rounds, verdict MODIFY
           (runs/senate/2026-08-21_004654-reqmap-module-size.json). Not one senator defended
           the split. Three findings decided it: (1) the premise was never established — every
           option argued from line count and none named a failure caused by it, against 511
           tests, 92% coverage and 130 commits in that file with no size-attributable incident;
           (2) a fixed threshold here is not a control limit but an arbitrary line — median
           commit +11 lines while the top 10 commits carry 59% of all growth, so a budget fires
           on a burst feature landing and is silent across the ordinary commits, which ADR-0002
           says gets switched off; (3) the split's economics are inverted — ADR-0005's
           byte-compare is cheap because it fires rarely, while this file is touched by 130 of
           ~390 commits, and it adds two SILENT failure modes a byte-compare cannot catch (a
           hand-edit reverted by the next build, a symbol shadowed by concatenation order) plus
           relocation of the 175 implements: tags feeding the committed _reqlock/_map.
           ADR-0001 corrected in the same change: its stale "~5,200 lines" is now the measured
           5,544 with a date, and its Status no longer carries the open question. Re-open
           triggers are numeric: 3+ merge conflicts on the file in a rolling 90 days, or
           crossing 8,000 lines, or a named external consumer wanting the split form. -->
- [ ] Get to n=2: one external repo running the gate | lane: ops
- [x] Run the gate over a real C/C++ tree (headers, macros, generated code) — the evidence behind the automotive credibility line | lane: ops
      <!-- Closed 2026-08-25 by scan-evidence run 1 (v2.28.0, PR #192): madler/zlib (271 files) +
           curl/curl (4,449 files, 759 .c / 257 .h). Scanner 16/16 native-comment and edge probes
           (block comments, #define lines, CRLF, Latin-1 bytes), 0 false-positive tags, gate 3.6 s on
           curl. What it found was around the scanner (plan reach, dupes noise, Windows pipe) — fixed
           in the same release. A generated-code-heavy automotive tree is a separate run if ever needed. -->
- [ ] Revisit BSL once there's someone who'd contribute | lane: ops
- [x] Viewer i18n: an EN/RO (or pluggable-locale) toggle button for the self-contained HTML viewer, translating static UI chrome only (nav, tab labels, section headers, buttons, badges) — never requirement content (titles/intent/contract/AC stay author-language) | lane: feature
      <!-- Found 2026-08-21. A rough prototype validated the shape of the problem: a
           dictionary of exact-match EN strings + a few regex rules for interpolated
           counts ("N / M clauses covered"), applied via TreeWalker over the app root's
           text nodes and re-applied on every render via a debounced MutationObserver
           (the app always re-renders in English, so only the non-English direction
           needs active re-translation; restoring English is the same dictionary
           inverted). One gotcha the prototype surfaced: eyebrow-header suffixes like
           " normative" / " = tests" carry a LEADING space in the actual JSX children
           array that isn't visible when skimming minified source — an exact-match
           dictionary is unforgiving of that, so every split-node entry needs verifying
           against a live DOM, not just the source text.
           The real implementation should NOT patch the built bundle post-hoc (that only
           works as a throwaway hack, since it lives outside any diff the build tracks
           and any regen wipes it) — it should author i18n INTO the JSX source
           (plugin/app/*) before the Vite build: a string-extraction step (or i18n keys
           used directly in JSX instead of literal English), a locale file per language,
           and a toggle wired into the header component's own state rather than a
           DOM-level overlay. Demand-gated: no filed request yet — revisit if someone
           asks. -->
      <!-- Shipped in v2.23.0, built exactly the way this note prescribed: i18n authored
           into the JSX (app/src/lib/i18n.jsx + t() call sites), never a post-hoc patch of
           the built bundle. The demand gate was cleared by a direct request. Two things
           are deliberately NOT translated: requirement content (the artifact under review)
           and the engine's own vocabulary (status/layer/role/severity are literal values
           in the .md files and in gate output). The dictionary is keyed by the English
           source string, so a missing entry degrades to English. Locale is remembered in
           localStorage and never written into _map.html, which stays byte-identical.
           Six SSR-smoke assertions cover both directions; ARCH-VIEWER-007 +AC-6. -->

## v3.1 -- Bug hunt findings (2026-09-03)
<!-- 20-agent parallel sweep of plugin/scripts/reqmap.py (7279 lines), split into
     function-aligned chunks + an encoding/Windows sweep + a test-crossref pass, run
     against a HEAD worktree snapshot so it could not be skewed by concurrent
     uncommitted work on this branch. Every one of the 31 raw candidates was put
     through a 3-agent adversarial refutation panel (majority must NOT refute); all 31
     survived (0 refuted). Deduplicated to 22 items below where two raw findings shared
     one root cause. Nothing here is fixed yet -- this is the punch list, not a patch. -->
- [ ] `binding_hash`'s `_NORMATIVE_HEADING_RE` (line 1741) omits "cases" from its keyword list, so a `## Cases` section is silently excluded from the drift hash -- editing a CASE-N criterion never trips DRIFT | lane: bus
      <!-- HIGH. 57/68 requirement files use the current `## Cases` spelling, so acceptance-criteria drift detection is corpus-wide broken for the majority spelling; only the legacy `## HOW -- Acceptance` heading (via "acceptan") still works. Verified directly: binding_hash unchanged before/after editing a CASE-1 Then-line on ARCH-ACVERIFY-019.md. No test edits inside `## Cases` and expects the hash to change. -->
- [ ] `load_requirements` (line 909): a file's prose preamble block (before its first `---` block) can fall back to the filename for its id same as block 0 proper -- if the file is named after its real first requirement's id, the preamble wins the `rid in reqs` collision and the real requirement is silently dropped, with only a stderr warning | lane: bus
      <!-- HIGH. Verified: a file `AREA-E-001.md` = preamble text + a `---\nid: AREA-E-001...` block loses the real block's meta/body entirely; `reqs["AREA-E-001"]` ends up holding the empty-meta preamble. ARCH-MODULEFILE-056's own comment only guards against a LATER block falling back to the filename, not the preamble block. -->
- [ ] `_SH_TEST_NAME_RE` (line 2117, feeds `_test_link_problem`) requires a `._-` separator on both sides of "test", so a shell test file literally named `test.sh` or `tests.sh` fails the filename-convention check and gets a false test-link-integrity warning | lane: bus
      <!-- LOW. The exact false-positive class ARCH-TESTLINK-018's filename-convention branch exists to avoid. -->
- [ ] `cmd_check` under `--since` (lines 2259 and 2268): the implements/tested-by coverage check tests `rid in members` against the `--since`-FILTERED member dict instead of full coverage, so a confirmed requirement whose implements tag is untouched but whose tested-by file changed (or vice versa) gets a false ERROR (implements side, flips exit code) or false WARN (tested-by side) | lane: ops
      <!-- HIGH -- can fail a `--since`-scoped CI gate/pre-commit hook on a commit that only touched one half of an implements/tested-by pair. Reproduced live against a minimal git repo built for exactly this scenario. -->
- [ ] `cmd_promote_todo`'s `layer:` frontmatter substitution (line 2734) has no success check, unlike the milestone/title anchor handling right below it -- a custom template whose layer line doesn't literally match `layer: feature` silently keeps the wrong layer while the success message reports the intended one | lane: feature
      <!-- MEDIUM. `re.sub` (not `subn`) discards the zero-match case silently; a consumer's on-disk `plugin/templates/requirement.md` override with a differently-spelled layer line reproduces it. -->
- [ ] `cmd_promote` (line 2865): EOL detection is "any CRLF anywhere in the file" then blanket-converts every remaining bare `\n` to `\r\n`, so a file with mixed line endings gets its bare-LF lines silently rewritten -- contradicts the adjacent comment's promise to preserve the file's own line endings verbatim | lane: feature
      <!-- LOW. No .gitattributes rule pins EOL for plugin/requirements/*.md, so a merge- or paste-introduced bare-LF line is plausible. -->
- [ ] `_py_facts` (lines 3104 and 3121) crashes with `IndexError` when a module/function/class docstring is non-empty but whitespace-only after `ast.get_docstring`'s cleanup -- aborts the whole `plan`/`candidates` run on one such .py file instead of degrading to empty facts as its own docstring promises | lane: feature
      <!-- HIGH. Reproduced directly: `_py_facts('"""\n   \n"""\ndef f():\n    pass\n')` raises IndexError. Not a SyntaxError/ValueError, so the existing `ast.parse` guard doesn't catch it, and `cmd_candidates`'s dict comprehension has no per-file guard either. -->
- [ ] `cmd_translate` (line 3901) and `_load_translations` (line 3953) both call `.get(...)`/`.items()` on a parsed i18n cache JSON without checking it's a dict first, unlike every other cache loader in the file (scancache, lock, memberlock, capmap all guard with `isinstance(data, dict)`) -- a malformed `_i18n/<locale>.json` crashes `translate`/`map`/`map --check`/`export` instead of failing open per entry as documented | lane: feature
      <!-- MEDIUM. Reproduced directly (AttributeError on `None`/`list`). `gate`'s own call site happens to be wrapped in try/except so gate survives; the direct commands don't. -->
- [ ] `cmd_next` (lines 4124 and 4166): the early "Nothing pending" return fires whenever the four risk buckets + untagged-files are empty, even though Granularity/Redundancy (computed later in the same function) may still be non-empty -- and when Granularity DOES print, it ignores `top_n` truncation that every sibling bucket applies | lane: feature
      <!-- MEDIUM. Reproduced directly: a single oversize confirmed requirement with nothing else pending prints only "Nothing pending", the Granularity advisory suppressed entirely; with something else pending it correctly appears but with no "...N more" cap. -->
- [ ] `lint_requirement`'s vague-term and redundant-modal checks (lines 4496 and 4510) both call `_lint_prose(body, "contract")` with the literal legacy label instead of iterating `CONTRACT_LABELS` -- both checks are dead on every requirement using the current `## Description` heading | lane: feature
      <!-- HIGH. Confirmed: 57/57 non-legacy files use `## Description`, 0 use `## Contract`; `lint --code ..` over the real corpus shows 0 vague-term and 0 redundant-modal hits anywhere despite cmd_lint's own docstring listing both as active checks. -->
- [ ] `_already_decomposed` (line 4639): `except OSError` when reading sibling requirement files doesn't catch `UnicodeDecodeError` (a `ValueError` subclass), unlike the same read pattern elsewhere in the file that deliberately catches `(OSError, ValueError)` -- one invalid-UTF-8 sibling crashes `lint --decompose` instead of being skipped | lane: feature
      <!-- MEDIUM. Reproduced directly against a sibling file with one invalid UTF-8 byte. -->
- [ ] `_commits_since_reqs_touch` (line 5184) passes `reqs_dir` un-rooted to `git -C code_root log -- reqs_dir`, so under `--code ..` (this repo's own documented common invocation) the pathspec resolves relative to `code_root` instead of the original cwd and the registry-lag signal silently goes missing from `health` | lane: ops
      <!-- MEDIUM. Reproduced directly: `git -C .. log -1 -- requirements` from `plugin/` returns nothing; the correct `git -C .. log -1 -- plugin/requirements` returns a real hash. Existing tests pass an absolute reqs_dir so never hit the relative-path/-C interaction. Same class of bug ARCH-CHECK-006's own `os.path.abspath(p)` pattern (line ~1935) exists to prevent. -->
- [ ] `cmd_health` (line 5252): the "healthy on every axis" tally waives the tested-by requirement for `layer: need` (`has_test or is_need`) but not for `layer: aggregate`, even though `_impl_exempt` -- the one predicate CLAUDE.md documents as shared by gate/health/map/confirm -- waives both | lane: ops
      <!-- MEDIUM, but an architecture-invariant violation: a confirmed aggregate requirement can be fully clean under `gate` yet still score as unhealthy/orphan-like in `health`'s JSON/badge output. -->
- [ ] `_wipe` (lines 5382 and 5386, `init --wipe`) reads and rewrites tagged source files without `newline=""`, unlike `cmd_promote`/`_mark_todo_done`/`_apply_verifies` which all deliberately pass it -- stripping one tag comment silently normalizes the ENTIRE file's line endings to the host platform's `os.linesep` | lane: bus
      <!-- MEDIUM. Concretely breaks an LF-committed shell hook (e.g. this repo's own `.githooks/pre-commit`, which must stay LF or `/bin/sh` chokes on the CR) if `init --wipe` ever runs on Windows against a file with `core.autocrlf=false/input`. -->
- [ ] `_section` (line 5623) and `_bullets` (line 5668) use `lstrip("- ")` / `lstrip("> ")`, which strips a leading CHARACTER SET, not a two-character prefix, corrupting requirement content that itself starts with `-` or `>` (e.g. `- -1 means error`, `> >100 requests/sec`) -- feeds the committed `_map.json`'s `input`/`output`/`contract`/`desc` fields | lane: bus
      <!-- MEDIUM. Verified by execution both ways; `_first_quote` on the same body correctly lstrips only the single `>` character, proving the inconsistency. -->
- [ ] `_emit_area_subgraphs` (line 5816): the per-area Mermaid subgraph label embeds the raw `area:` frontmatter string directly instead of passing it through `_mlabel` like the sibling `_mermaid_deps` does -- an area name containing a `"` breaks the generated Mermaid syntax in the committed `_map.md` | lane: feature
      <!-- MEDIUM. `area:` is free-text with no validation. Verified by execution: `area: Foo"Bar` emits an unterminated `subgraph sg_Foo_Bar["Foo"Bar"]` line. -->
- [ ] `_mermaid_deps` (line 5902): area-level node ids (`a_{_safe_id(label)}`) have no collision guard, unlike `_emit_area_subgraphs` in the same file which explicitly disambiguates two area labels that sanitize to the same id -- two such areas collapse into one Mermaid node and a real inter-area dependency renders as a self-loop | lane: feature
      <!-- MEDIUM. Reproduced with the exact fixture `test_area_subgraphs_distinct_ids_for_safeid_collision` already uses for `_emit_area_subgraphs`, run through `_mermaid_deps` instead. -->
- [ ] `_LEGEND_MD` (line 6030) has 4 entries but `_build_md_text` now renders 5 diagrams (Specification Hierarchy was added as a new first diagram without a matching legend entry) -- every legend caption is shifted one diagram off and the last diagram (Risk & Unknowns) gets an empty legend | lane: feature
      <!-- MEDIUM. Reproduced verbatim in the currently committed plugin/requirements/_map.md. No test asserts legend-to-diagram-title correspondence. -->
- [ ] `cmd_site` scaffold (`_render_region`, lines 6248 and 6256): the injected `nav`/`stats` regions wrap their content in `reqmap-nav`/`reqmap-stats` divs that match no selector in `SITE_TEMPLATE`'s CSS -- on a freshly scaffolded page the nav links render unstyled/uncrammed and the 5 stat cards stack vertically instead of the intended 6-column grid | lane: feature
      <!-- HIGH -- visibly broken on the very first `reqmap.py site` scaffold. `SITE_TEMPLATE` styles `.nav-links`/`.nav-links a` and expects `.stat` as a DIRECT child of the grid container `.stats`; the extra wrapper divs defeat both. Verified by actually invoking cmd_site. -->
- [ ] `_apply_verifies` (line 6922): the idempotency check does substring containment (`if tag in line`) on the literal tag text, so an existing `CASE-11`/`AC-11` tag is mistaken for a proposed `CASE-1`/`AC-1` tag already being present -- the real, missing tag is silently never written | lane: feature
      <!-- MEDIUM. Reproduced directly: a line already carrying `# verifies: RID#CASE-11` blocks a later proposal for `RID#CASE-1` from ever being applied. -->
- [ ] `_write_region` (line 761, used by `gen-integration` to patch SKILL.universal.md's command table) reads and writes its target file in default text mode with no `newline=""`, so on POSIX it universal-newline-translates the WHOLE file CRLF -> LF on read and writes it back with no re-translation -- contradicts its own docstring's promise that "prose outside is untouched" | lane: bus
      <!-- MEDIUM. `plugin/skills/requirement-manager/SKILL.universal.md` is committed CRLF with no `.gitattributes` eol pin; three OTHER read-modify-write pairs in this same file (lines ~2768/2783, 2848/2866, 6911/6929) all deliberately pass `newline=""` for exactly this reason -- this one omits it. No test exercises the actual write path. -->
- [ ] `cmd_gen_integration` (line 768) writes `tool_definition.json` via the same bare text-mode open with no `newline` argument, so regenerating on a non-Windows box flips the whole committed CRLF file to LF even though the JSON content is unchanged | lane: ops
      <!-- LOW -- cosmetic but produces a large false diff on every POSIX regeneration; same root-cause pattern as the `_write_region` finding above, kept separate since it's a different function and a different target file. -->