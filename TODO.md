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
- [x] Scan cache (opt-in `--cache` flag — REQ-SCANCACHE-023) | lane: ops

## v1.16
<!-- Senate fix plan 2026-06-12 (runs/senate/2026-06-12_091906-requirement-manager-fix-plan.json, verdict MODIFY).
     Detail spec: docs/PLAN-senate-fix-2026-06-12.md -->
- [x] Phantom-member fix: context-aware tag scan (fence/backtick/indent + .py string state) | lane: bus
- [x] Drift doc reconciliation (direction B): SKILL.md, CLAUDE.md, NEED-SSOT-001 AC-1 split + severity table | lane: ops
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
      <!-- Done as REQ-MEMBERDRIFT-027: stored in a versioned sidecar `_memberlock.json` (not _reqlock.json) so the cross-repo contract stays byte-stable; scoped to mono-requirement files to avoid alarm fatigue. Both Senate blocking conditions addressed. -->

- [x] ~~Internal-consistency lint: flag a requirement whose structured fields moved to a new model while its prose Contract/AC still assert the superseded model.~~ **DROPPED** | lane: feature
      <!-- DROPPED (not implemented). Senate 2026-06-19 (runs/senate/2026-06-19_224727-reqmap-item4-internal-consistency-lint.json) + closed tracking issue #120. Decision: do not build. The naive 'depends_on id absent from prose' check is empirically refuted (78.6% false-positive on this corpus, and would have missed the motivating TRIAS case — an added edge, not an absent id). The only viable detector (baseline-aware depends_on diff) needs a persisted baseline ~= ITEM 3's machinery for a warn-only, n=1 signal — disproportionate. The residual gap (a requirement's own frontmatter vs its prose) is narrow and caught by human PR review; the member-changed half is covered by REQ-MEMBERDRIFT-027. Revisit only if a second real frontmatter-vs-prose contradiction recurs. -->

## v1.35
<!-- Backfilled 2026-06-21 (TODO/roadmap hygiene): shipped capabilities whose milestone
     sections were never recorded here. Senate 2026-06-21 (runs/senate/*roadmap-coherence)
     chose manual TODO hygiene over building a TODO<->requirement coherence-check feature
     (demand n=1; the only stale TODO observed was this repo's own). -->
- [x] Project presentation page (`site`): inject/refresh engine-owned nav + stats regions into docs/architecture.html (scaffold if absent) | lane: feature
      <!-- REQ-SITE-026 -->

## v2.4
- [x] Excalidraw scene builder — core stdlib API (.excalidraw scene + self-contained HTML viewer) | lane: feature
      <!-- REQ-EXCALIDRAW-030 -->
- [x] Excalidraw quality gates at save() (overlap, crossing, legend, text-overflow, text-overlap; later: short-arrow, label-fit) | lane: feature
      <!-- REQ-EXCALIDRAW-031 -->
- [x] Excalidraw builder CLI verbs (`render` a scene → viewer; `discover` a repo → generator stub) | lane: feature
      <!-- REQ-EXCALIDRAW-032 -->

## v2.6
- [x] Untagged-code coverage signal: read-only `untagged` count in `health` (code traced to no requirement) | lane: feature
      <!-- REQ-COVERAGE-029. Senate 2026-06-21 (enforce-all-code DEEPLY_SPLIT): a hard coverage gate was rejected; only this read-only signal shipped. -->

## v2.7
<!-- Multi-platform Phase 1 — SHIPPED (PR #127). Senate 2026-06-21 (runs/senate/2026-06-21_110220-reqmap-multiplatform-mcp.json, verdict MODIFY).
     Detail spec: docs/superpowers/specs/2026-06-21-reqmap-multiplatform-command-registry-design.md
     Problem: the prior multi-AI artifacts (tool_definition.json + 3 SKILL.universal.md) were hand-maintained
     mirrors of the CLI with no sync mechanism — already drifting. Fix: one declarative command registry as
     the single source of truth, generate the artifacts from it, drift-guard them in the gate. -->
- [x] Command registry: one declarative `COMMANDS` structure in reqmap.py; argparse choices derived from it (hand-written `choices=[...]` literal removed). Dispatch ladder left intact (de-risked); CLI behaviour byte-identical (TestCli unchanged). | lane: bus
      <!-- REQ-CMDREGISTRY-033 -->
- [x] Generate `tool_definition.json` (function-calling schema) + the command-reference TABLE inside SKILL.universal.md (delimited region; curated WHY/WHEN prose stays hand-authored) from the registry. | lane: feature
- [x] Drift-guard: `gate` (incl. `--json`) regenerates the artifacts in-memory and byte-compares vs committed → error (exit 1), mirroring `map --check`. | lane: ops

## v2.12
<!-- Backfilled 2026-08-17 (second roadmap-hygiene pass). The same drift the v1.35 section
     records recurred: the file stopped at v2.8 while v2.12-v2.16 shipped. The v1.35 note
     chose manual hygiene over building a TODO<->requirement coherence check, on the grounds
     that demand was n=1 — this repo's own stale TODO. It is now n=2, same repo, same
     failure mode. -->
- [x] Registry lag in `health`: commits since the requirements dir was last touched | lane: ops
      <!-- REQ-REGISTRYLAG-035 -->

## v2.13
- [x] Ranked free-text requirement search (`search`), shared scoring model with the viewer | lane: feature
      <!-- REQ-SEARCH-036 -->

## v2.14
- [x] Requirement clarity lint enforced in CI, the dev hook and the published action | lane: ops

## v2.15
- [x] Plain present requirement voice: named subject, no `shall`, tightened lint ceilings | lane: feature

## v2.16
- [x] V-model verification levels: `@unit`/`@integration`/`@system` on `tested-by:`, `validated-against:` activated as the validation link | lane: feature
      <!-- REQ-VLEVEL-037 -->

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
       unsynced source of truth in a tool whose pitch is "one". If CORE-PARSE-001
       changes, the viewer shows the stale version and no gate notices — the worst
       possible position for a counter-example.
     - docs/ sits outside the scan root (CI runs from plugin/), so REQ-DOCBUNDLE-026
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
- [x] Extend scan reach: add .sh/.tf to CODE_EXTS, extensionless basename matching for Dockerfile/Makefile, let the scan root reach the repo root instead of stopping at plugin/ — and cover docs/, not just .github/, so REQ-DOCBUNDLE-026 finally sees its own bundle | lane: bus
      <!-- Shipped as `--code ..`/`--code .` for THIS repo's CI/hook only (Trias deliberation
           .consilium/runs/2026-08-18_1640_v29-scan-root-codeexts-viewer-trias.json rejected
           auto-widening the shared engine default as a silent-failure risk to consumer repos
           scoped to a subdirectory on purpose). Also widened Dockerfile/Makefile basename
           matching to the standard git hook names (pre-commit, pre-push, ...) — needed for the
           next item below. REQ-DOCBUNDLE-026 now WARNs on docs/full_architecture.html, confirmed live. -->
- [x] Tag this repo's own pipeline (ci.yml, check/action.yml, .githooks/, sync_reqmap.sh) — currently zero tags across all of them | lane: ops
      <!-- REQ-SELFGATE-039. A confirmed requirement whose members are all outside plugin/
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
- [ ] Bring app/src/ under the gate: real per-file `# implements:`/`generated-from:` tagging of app/src/**/*.jsx | lane: ops
      <!-- Deliberately deferred (2-1 majority in the same Trias deliberation): app/ stays in the
           repo-root .reqmapignore's `app/**` exclusion this round. Revisit once the demand is
           real, not before. -->

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
           REQ-SELFGATE-039 AC-6/AC-7. Shipped in v2.18.1. -->
- [ ] Scan vs `.gitignore`: a gitignored-but-tagged file silently changes committed generated artifacts — make the scan skip gitignored paths, or WARN when a member resolves to one | lane: bus
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
- [ ] Add an npm job asserting `git diff --exit-code` on plugin/scripts/_map_viewer.html, and the same check for regenerated Excalidraw diagrams — closes the committed-build-artifact hole for both | lane: ops
- [x] Stop squashing main; land the next change as a visible PR — this also revives the changelog gate, which currently no-ops because HEAD~1 doesn't resolve | lane: ops
      <!-- Done 2026-08-20: PR #167 (check@v2) landed as a real merge commit, e56886c.
           HEAD~1 resolves again, so the changelog-entry gate is live rather than a
           silent no-op — and the release job proved itself on that same merge: it cut
           v2.18.1 and force-moved the @v2 alias onto the released commit. -->
- [ ] Extract ADRs to docs/adr/ — ten decisions pulled out of changelog prose, including the deliberate V-model omission | lane: ops
- [x] CI matrix: Python 3.9/3.12/3.13 x ubuntu/windows — prove the `-X utf8` usage actually holds | lane: ops
      <!-- Shipped in v2.19.0 as a separate `tests` job (6 cells, fail-fast: false) running
           every suite. Deliberately NOT a matrixed gate-and-tests: the gate is one
           authoritative verdict on the requirement corpus, not a per-interpreter one.
           `release` now needs the matrix too; `deploy-map` still needs only the gate. -->
- [ ] Coverage + ruff on the engine, published in the job summary | lane: ops
- [x] Declare and assert the Python floor (3.7 today, accidental) | lane: bus
      <!-- REQ-PYFLOOR-040, v2.19.0. Floor = 3.9, chosen as the oldest version CI can
           actually run rather than the oldest the code tolerates (3.7): 3.7/3.8 are not
           installable on current GitHub runners, so supporting them would be untested.
           A test asserts MIN_PYTHON == the oldest python in the CI matrix, so the two
           cannot drift apart. Cannot catch <3.6 (f-strings fail at compile time). -->
- [ ] Fix the upgrade path: warn_if_stale is silent in CI, exactly where it matters | lane: bus
- [ ] Repo hygiene: CONTRIBUTING, SECURITY.md, issue and PR templates | lane: ops
- [ ] Adversarial tests on injected HTML (</script>, U+2028, lone surrogates) and a published benchmark on a 10k-file tree | lane: bus
- [ ] Settle the 5,199-line module: split with a concatenating build, or keep single-file with an ADR plus a CI line-count budget | lane: bus
- [ ] Get to n=2: one external repo running the gate | lane: ops
- [ ] Run the gate over a real C/C++ tree (headers, macros, generated code) — the evidence behind the automotive credibility line | lane: ops
- [ ] Revisit BSL once there's someone who'd contribute | lane: ops