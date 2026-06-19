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
- [ ] Member-hash drift (reverse direction): record member content hashes in `_reqlock.json` and WARN when a `confirmed` requirement's member changed since lock but the requirement was not re-touched/re-confirmed — catches "behavior shipped, spec not updated". Default WARN (likely `--strict`-promotable) to bound the noise of every code edit nagging its requirement. | lane: feature
- [ ] Internal-consistency lint: flag a requirement whose structured fields moved to a new model (e.g. `depends_on` edge added, cost/number changed) while its prose Contract/AC still assert the superseded model — the contradiction is detectable without semantics. | lane: feature
