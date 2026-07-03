---
generated: 2026-07-03 23:45
nodes: 38
edges: 54
---

# Requirement Map

## System Map

_Capabilities grouped by area; thick border = bus; arrows = `depends_on`. Edges into the bus/hubs are hidden (the Dependency Map shows area-level coupling)._

```mermaid
graph LR
  subgraph sg_CORE["CORE"]
    CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
    CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
    CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  end
  subgraph sg_REQ["REQ"]
    REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
    REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
    REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
    REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
    REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
    REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
    REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
    REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
    REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
    REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
    REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
    REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
    REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  end
  subgraph sg_misc["misc"]
    NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  end
  REQ_COVERAGE_029 --> REQ_NEXT_013
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
  REQ_SITE_026 --> REQ_MAP_007
  REQ_SITE_026 --> REQ_VIEWER_007
  REQ_SITE_026 --> REQ_PAGES_021
  REQ_VIEWER_007 --> REQ_MAP_007
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_1160_1204["scripts/reqmap.py:1160-1204"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1160_1204
  f_scripts_test_reqmap_py_152_4274["scripts/test_reqmap.py:152-4274"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_152_4274
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_640_711["scripts/reqmap.py:640-711"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_640_711
  f_scripts_test_reqmap_py_49_4227["scripts/test_reqmap.py:49-4227"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_49_4227
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_734_929["scripts/reqmap.py:734-929"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_734_929
  f_scripts_test_reqmap_py_271["scripts/test_reqmap.py:271"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_271
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1066_1533["scripts/reqmap.py:1066-1533"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1066_1533
  f_scripts_test_reqmap_py_2876_4258["scripts/test_reqmap.py:2876-4258"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2876_4258
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2099_2247["scripts/reqmap.py:2099-2247"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2099_2247
  f_scripts_test_reqmap_py_941_2311["scripts/test_reqmap.py:941-2311"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_941_2311
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1147_1651["scripts/reqmap.py:1147-1651"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1147_1651
  f_scripts_test_reqmap_py_142_4436["scripts/test_reqmap.py:142-4436"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_142_4436
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_132_1673["scripts/reqmap.py:132-1673"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_132_1673
  f_scripts_test_reqmap_py_4156["scripts/test_reqmap.py:4156"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4156
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3319["scripts/reqmap.py:3319"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3319
  f_scripts_test_reqmap_py_2668["scripts/test_reqmap.py:2668"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2668
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_979["scripts/reqmap.py:979"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_979
  f_scripts_test_reqmap_py_382["scripts/test_reqmap.py:382"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_382
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1571["scripts/reqmap.py:1571"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1571
  f_scripts_test_reqmap_py_597["scripts/test_reqmap.py:597"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_597
  REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2["skills/excalidraw-diagram/scripts/excalidraw_builder.py:2"]
  REQ_EXCALIDRAW_030 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_2["skills/excalidraw-diagram/scripts/test_excalidraw.py:2"]
  REQ_EXCALIDRAW_030 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_2
  REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3["skills/excalidraw-diagram/scripts/excalidraw_builder.py:3"]
  REQ_EXCALIDRAW_031 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_3["skills/excalidraw-diagram/scripts/test_excalidraw.py:3"]
  REQ_EXCALIDRAW_031 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_3
  REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4["skills/excalidraw-diagram/scripts/excalidraw_builder.py:4"]
  REQ_EXCALIDRAW_032 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_4["skills/excalidraw-diagram/scripts/test_excalidraw.py:4"]
  REQ_EXCALIDRAW_032 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_4
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_1936_2082["scripts/reqmap.py:1936-2082"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1936_2082
  f_scripts_test_reqmap_py_821_836["scripts/test_reqmap.py:821-836"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_821_836
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2368_2455["scripts/reqmap.py:2368-2455"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2368_2455
  f_scripts_test_reqmap_py_1014_1556["scripts/test_reqmap.py:1014-1556"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1014_1556
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3257["scripts/reqmap.py:3257"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3257
  f_scripts_test_reqmap_py_2625_2726["scripts/test_reqmap.py:2625-2726"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2625_2726
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3429_3458["scripts/reqmap.py:3429-3458"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3429_3458
  f_scripts_test_reqmap_py_2071_4388["scripts/test_reqmap.py:2071-4388"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2071_4388
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2771_2951["scripts/reqmap.py:2771-2951"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2771_2951
  f_scripts_test_reqmap_py_2339["scripts/test_reqmap.py:2339"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2339
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2800_2838["scripts/reqmap.py:2800-2838"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2800_2838
  f_scripts_test_reqmap_py_2323_2339["scripts/test_reqmap.py:2323-2339"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2323_2339
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2495_4489["scripts/reqmap.py:2495-4489"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2495_4489
  f_scripts_test_reqmap_py_678_4388["scripts/test_reqmap.py:678-4388"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_678_4388
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1220_1307["scripts/reqmap.py:1220-1307"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1220_1307
  f_scripts_test_reqmap_py_437["scripts/test_reqmap.py:437"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_437
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1767["scripts/reqmap.py:1767"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1767
  f_scripts_test_reqmap_py_883["scripts/test_reqmap.py:883"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_883
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1010_2647["scripts/reqmap.py:1010-2647"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1010_2647
  f_scripts_test_reqmap_py_1945_4338["scripts/test_reqmap.py:1945-4338"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1945_4338
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1037_1613["scripts/reqmap.py:1037-1613"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1037_1613
  f_scripts_test_reqmap_py_537["scripts/test_reqmap.py:537"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_537
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2606_4505["scripts/reqmap.py:2606-4505"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2606_4505
  f_scripts_test_reqmap_py_1203_1782["scripts/test_reqmap.py:1203-1782"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1203_1782
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1876_1902["scripts/reqmap.py:1876-1902"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1876_1902
  f_scripts_test_reqmap_py_1885_4338["scripts/test_reqmap.py:1885-4338"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1885_4338
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1788_1844["scripts/reqmap.py:1788-1844"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1788_1844
  f_scripts_test_reqmap_py_3069_4338["scripts/test_reqmap.py:3069-4338"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3069_4338
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1944_1997["scripts/reqmap.py:1944-1997"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1944_1997
  f_scripts_test_reqmap_py_635_821["scripts/test_reqmap.py:635-821"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_635_821
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4656["scripts/reqmap.py:4656"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4656
  f_scripts_test_reqmap_py_3136["scripts/test_reqmap.py:3136"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3136
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1344["scripts/reqmap.py:1344"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1344
  f_scripts_test_reqmap_py_927["scripts/test_reqmap.py:927"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_927
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_906_920["scripts/reqmap.py:906-920"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_906_920
  f_scripts_test_reqmap_py_3197["scripts/test_reqmap.py:3197"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3197
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2993["scripts/reqmap.py:2993"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2993
  f_scripts_test_reqmap_py_2499["scripts/test_reqmap.py:2499"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2499
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3075_3136["scripts/reqmap.py:3075-3136"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3075_3136
  f_scripts_test_reqmap_py_2563["scripts/test_reqmap.py:2563"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2563
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3484_4866["scripts/reqmap.py:3484-4866"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3484_4866
  f_scripts_test_reqmap_py_3838["scripts/test_reqmap.py:3838"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3838
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1416_1525["scripts/reqmap.py:1416-1525"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1416_1525
  f_scripts_test_reqmap_py_2800["scripts/test_reqmap.py:2800"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2800
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1497_3028["scripts/reqmap.py:1497-3028"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1497_3028
  f_scripts_test_reqmap_py_2946["scripts/test_reqmap.py:2946"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2946
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4618_4640["scripts/reqmap.py:4618-4640"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4618_4640
  f_scripts_test_reqmap_py_1176["scripts/test_reqmap.py:1176"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1176
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>34 caps</small>"]
  a_misc["misc<br><small>1 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```
