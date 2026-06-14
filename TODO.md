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
- [ ] `generated-from:` accepting >1 requirement ID — drift a system/explainer doc when ANY referenced requirement changes | lane: feature
- [ ] WARN when a large docs/ HTML/generated bundle carries no `generated-from:` tag at all (surface the doc-sync blind spot instead of silently ignoring it) | lane: ops

## v1.18
<!-- Bug found 2026-06-14 while generating the Consilium full architecture diagram via the
     excalidraw-diagram skill. route_under() label text overlapped with the next diagram
     region's title. Root cause: two independent bugs in excalidraw_builder.py.
     Consilium deliberation: .consilium/runs/2026-06-14_1200_excalidraw-builder-label-overlap.json
     Chosen approach: combined_midpoint_and_bounds (conf=0.695, 5 cand, 0 vetoed, sequential). -->
- [x] excalidraw_builder: fix path() label placement to arc-length midpoint (not points_abs[len//2] corner) | lane: bus
- [x] excalidraw_builder: extend bounds() to include _path_extents so route_under gap calculations via bounds()+N are correct | lane: bus
