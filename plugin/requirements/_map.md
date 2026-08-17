---
generated: 2026-08-17 10:28
nodes: 40
edges: 57
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
    REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
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
  REQ_REGISTRYLAG_035 --> REQ_HEALTH_017
  REQ_SEARCH_036 --> REQ_SIMILAR_016
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
  f_scripts_reqmap_py_1178_1222["scripts/reqmap.py:1178-1222"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1178_1222
  f_scripts_test_reqmap_py_152_4461["scripts/test_reqmap.py:152-4461"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_152_4461
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_658_729["scripts/reqmap.py:658-729"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_658_729
  f_scripts_test_reqmap_py_49_4414["scripts/test_reqmap.py:49-4414"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_49_4414
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_752_947["scripts/reqmap.py:752-947"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_752_947
  f_scripts_test_reqmap_py_271["scripts/test_reqmap.py:271"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_271
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1084_1551["scripts/reqmap.py:1084-1551"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1084_1551
  f_scripts_test_reqmap_py_3063_4445["scripts/test_reqmap.py:3063-4445"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_3063_4445
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2117_2265["scripts/reqmap.py:2117-2265"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2117_2265
  f_scripts_test_reqmap_py_941_2311["scripts/test_reqmap.py:941-2311"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_941_2311
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1165_1669["scripts/reqmap.py:1165-1669"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1165_1669
  f_scripts_test_reqmap_py_142_4623["scripts/test_reqmap.py:142-4623"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_142_4623
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_132_1691["scripts/reqmap.py:132-1691"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_132_1691
  f_scripts_test_reqmap_py_4343["scripts/test_reqmap.py:4343"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4343
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3422["scripts/reqmap.py:3422"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3422
  f_scripts_test_reqmap_py_2794["scripts/test_reqmap.py:2794"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2794
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_997["scripts/reqmap.py:997"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_997
  f_scripts_test_reqmap_py_382["scripts/test_reqmap.py:382"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_382
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1589["scripts/reqmap.py:1589"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1589
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
  f_scripts_reqmap_py_1954_2100["scripts/reqmap.py:1954-2100"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1954_2100
  f_scripts_test_reqmap_py_821_836["scripts/test_reqmap.py:821-836"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_821_836
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2386_2473["scripts/reqmap.py:2386-2473"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2386_2473
  f_scripts_test_reqmap_py_1014_1556["scripts/test_reqmap.py:1014-1556"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1014_1556
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3360["scripts/reqmap.py:3360"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3360
  f_scripts_test_reqmap_py_2751_2913["scripts/test_reqmap.py:2751-2913"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2751_2913
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3539_3568["scripts/reqmap.py:3539-3568"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3539_3568
  f_scripts_test_reqmap_py_2071_4575["scripts/test_reqmap.py:2071-4575"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2071_4575
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2789_2980["scripts/reqmap.py:2789-2980"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2789_2980
  f_scripts_test_reqmap_py_2339["scripts/test_reqmap.py:2339"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2339
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2818_2856["scripts/reqmap.py:2818-2856"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2818_2856
  f_scripts_test_reqmap_py_2323_2339["scripts/test_reqmap.py:2323-2339"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2323_2339
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2513_4599["scripts/reqmap.py:2513-4599"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2513_4599
  f_scripts_test_reqmap_py_678_4575["scripts/test_reqmap.py:678-4575"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_678_4575
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1238_1325["scripts/reqmap.py:1238-1325"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1238_1325
  f_scripts_test_reqmap_py_437["scripts/test_reqmap.py:437"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_437
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1785["scripts/reqmap.py:1785"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1785
  f_scripts_test_reqmap_py_883["scripts/test_reqmap.py:883"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_883
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1028_2665["scripts/reqmap.py:1028-2665"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1028_2665
  f_scripts_test_reqmap_py_1945_4525["scripts/test_reqmap.py:1945-4525"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1945_4525
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1055_1631["scripts/reqmap.py:1055-1631"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1055_1631
  f_scripts_test_reqmap_py_537["scripts/test_reqmap.py:537"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_537
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2624_4615["scripts/reqmap.py:2624-4615"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2624_4615
  f_scripts_test_reqmap_py_1203_1782["scripts/test_reqmap.py:1203-1782"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1203_1782
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1894_1920["scripts/reqmap.py:1894-1920"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1894_1920
  f_scripts_test_reqmap_py_1885_4525["scripts/test_reqmap.py:1885-4525"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1885_4525
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1806_1862["scripts/reqmap.py:1806-1862"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1806_1862
  f_scripts_test_reqmap_py_3256_4525["scripts/test_reqmap.py:3256-4525"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3256_4525
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1962_2015["scripts/reqmap.py:1962-2015"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1962_2015
  f_scripts_test_reqmap_py_635_821["scripts/test_reqmap.py:635-821"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_635_821
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_scripts_reqmap_py_3334_3428["scripts/reqmap.py:3334-3428"]
  REQ_REGISTRYLAG_035 -->|implements| f_scripts_reqmap_py_3334_3428
  f_scripts_test_reqmap_py_2819["scripts/test_reqmap.py:2819"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_scripts_test_reqmap_py_2819
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4766["scripts/reqmap.py:4766"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4766
  f_scripts_test_reqmap_py_3323["scripts/test_reqmap.py:3323"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3323
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1362["scripts/reqmap.py:1362"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1362
  f_scripts_test_reqmap_py_927["scripts/test_reqmap.py:927"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_927
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_924_938["scripts/reqmap.py:924-938"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_924_938
  f_scripts_test_reqmap_py_3384["scripts/test_reqmap.py:3384"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3384
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_scripts_reqmap_py_3213["scripts/reqmap.py:3213"]
  REQ_SEARCH_036 -->|implements| f_scripts_reqmap_py_3213
  f_scripts_test_reqmap_py_2671["scripts/test_reqmap.py:2671"]
  REQ_SEARCH_036 -->|tested-by| f_scripts_test_reqmap_py_2671
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_3022["scripts/reqmap.py:3022"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_3022
  f_scripts_test_reqmap_py_2545["scripts/test_reqmap.py:2545"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2545
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3104_3165["scripts/reqmap.py:3104-3165"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3104_3165
  f_scripts_test_reqmap_py_2609["scripts/test_reqmap.py:2609"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2609
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3594_4983["scripts/reqmap.py:3594-4983"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3594_4983
  f_scripts_test_reqmap_py_4025["scripts/test_reqmap.py:4025"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_4025
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1434_1543["scripts/reqmap.py:1434-1543"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1434_1543
  f_scripts_test_reqmap_py_2987["scripts/test_reqmap.py:2987"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2987
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1515_3057["scripts/reqmap.py:1515-3057"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1515_3057
  f_scripts_test_reqmap_py_3133["scripts/test_reqmap.py:3133"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_3133
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4728_4750["scripts/reqmap.py:4728-4750"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4728_4750
  f_scripts_test_reqmap_py_1176["scripts/test_reqmap.py:1176"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1176
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>36 caps</small>"]
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
