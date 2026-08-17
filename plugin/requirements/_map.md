---
generated: 2026-08-17 10:39
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
  f_scripts_test_reqmap_py_153_4482["scripts/test_reqmap.py:153-4482"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_153_4482
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_658_729["scripts/reqmap.py:658-729"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_658_729
  f_scripts_test_reqmap_py_50_4435["scripts/test_reqmap.py:50-4435"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_50_4435
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_752_947["scripts/reqmap.py:752-947"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_752_947
  f_scripts_test_reqmap_py_272["scripts/test_reqmap.py:272"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_272
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1084_1551["scripts/reqmap.py:1084-1551"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1084_1551
  f_scripts_test_reqmap_py_3084_4466["scripts/test_reqmap.py:3084-4466"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_3084_4466
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2126_2274["scripts/reqmap.py:2126-2274"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2126_2274
  f_scripts_test_reqmap_py_962_2332["scripts/test_reqmap.py:962-2332"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_962_2332
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1165_1669["scripts/reqmap.py:1165-1669"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1165_1669
  f_scripts_test_reqmap_py_143_4644["scripts/test_reqmap.py:143-4644"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_143_4644
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_132_1691["scripts/reqmap.py:132-1691"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_132_1691
  f_scripts_test_reqmap_py_4364["scripts/test_reqmap.py:4364"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4364
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3431["scripts/reqmap.py:3431"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3431
  f_scripts_test_reqmap_py_2815["scripts/test_reqmap.py:2815"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2815
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_997["scripts/reqmap.py:997"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_997
  f_scripts_test_reqmap_py_383["scripts/test_reqmap.py:383"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_383
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1589["scripts/reqmap.py:1589"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1589
  f_scripts_test_reqmap_py_598["scripts/test_reqmap.py:598"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_598
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
  f_scripts_reqmap_py_1963_2109["scripts/reqmap.py:1963-2109"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1963_2109
  f_scripts_test_reqmap_py_822_837["scripts/test_reqmap.py:822-837"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_822_837
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2395_2482["scripts/reqmap.py:2395-2482"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2395_2482
  f_scripts_test_reqmap_py_1035_1577["scripts/test_reqmap.py:1035-1577"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1035_1577
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3369["scripts/reqmap.py:3369"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3369
  f_scripts_test_reqmap_py_2772_2934["scripts/test_reqmap.py:2772-2934"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2772_2934
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3548_3577["scripts/reqmap.py:3548-3577"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3548_3577
  f_scripts_test_reqmap_py_2092_4596["scripts/test_reqmap.py:2092-4596"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2092_4596
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2798_2989["scripts/reqmap.py:2798-2989"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2798_2989
  f_scripts_test_reqmap_py_2360["scripts/test_reqmap.py:2360"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2360
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2827_2865["scripts/reqmap.py:2827-2865"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2827_2865
  f_scripts_test_reqmap_py_2344_2360["scripts/test_reqmap.py:2344-2360"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2344_2360
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2522_4608["scripts/reqmap.py:2522-4608"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2522_4608
  f_scripts_test_reqmap_py_679_4596["scripts/test_reqmap.py:679-4596"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_679_4596
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1238_1325["scripts/reqmap.py:1238-1325"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1238_1325
  f_scripts_test_reqmap_py_438["scripts/test_reqmap.py:438"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_438
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1794["scripts/reqmap.py:1794"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1794
  f_scripts_test_reqmap_py_884["scripts/test_reqmap.py:884"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_884
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1028_2674["scripts/reqmap.py:1028-2674"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1028_2674
  f_scripts_test_reqmap_py_1966_4546["scripts/test_reqmap.py:1966-4546"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1966_4546
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1055_1631["scripts/reqmap.py:1055-1631"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1055_1631
  f_scripts_test_reqmap_py_538["scripts/test_reqmap.py:538"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_538
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2633_4624["scripts/reqmap.py:2633-4624"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2633_4624
  f_scripts_test_reqmap_py_1224_1803["scripts/test_reqmap.py:1224-1803"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1224_1803
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1903_1929["scripts/reqmap.py:1903-1929"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1903_1929
  f_scripts_test_reqmap_py_1906_4546["scripts/test_reqmap.py:1906-4546"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1906_4546
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1815_1871["scripts/reqmap.py:1815-1871"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1815_1871
  f_scripts_test_reqmap_py_3277_4546["scripts/test_reqmap.py:3277-4546"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3277_4546
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1971_2024["scripts/reqmap.py:1971-2024"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1971_2024
  f_scripts_test_reqmap_py_636_822["scripts/test_reqmap.py:636-822"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_636_822
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_scripts_reqmap_py_3343_3437["scripts/reqmap.py:3343-3437"]
  REQ_REGISTRYLAG_035 -->|implements| f_scripts_reqmap_py_3343_3437
  f_scripts_test_reqmap_py_2840["scripts/test_reqmap.py:2840"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_scripts_test_reqmap_py_2840
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4775["scripts/reqmap.py:4775"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4775
  f_scripts_test_reqmap_py_3344["scripts/test_reqmap.py:3344"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3344
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1362["scripts/reqmap.py:1362"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1362
  f_scripts_test_reqmap_py_948["scripts/test_reqmap.py:948"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_948
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_924_938["scripts/reqmap.py:924-938"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_924_938
  f_scripts_test_reqmap_py_3405["scripts/test_reqmap.py:3405"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3405
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_scripts_reqmap_py_3222["scripts/reqmap.py:3222"]
  REQ_SEARCH_036 -->|implements| f_scripts_reqmap_py_3222
  f_scripts_test_reqmap_py_2692["scripts/test_reqmap.py:2692"]
  REQ_SEARCH_036 -->|tested-by| f_scripts_test_reqmap_py_2692
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_3031["scripts/reqmap.py:3031"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_3031
  f_scripts_test_reqmap_py_2566["scripts/test_reqmap.py:2566"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2566
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3113_3174["scripts/reqmap.py:3113-3174"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3113_3174
  f_scripts_test_reqmap_py_2630["scripts/test_reqmap.py:2630"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2630
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3603_4992["scripts/reqmap.py:3603-4992"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3603_4992
  f_scripts_test_reqmap_py_4046["scripts/test_reqmap.py:4046"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_4046
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1434_1543["scripts/reqmap.py:1434-1543"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1434_1543
  f_scripts_test_reqmap_py_3008["scripts/test_reqmap.py:3008"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_3008
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1515_3066["scripts/reqmap.py:1515-3066"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1515_3066
  f_scripts_test_reqmap_py_3154["scripts/test_reqmap.py:3154"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_3154
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4737_4759["scripts/reqmap.py:4737-4759"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4737_4759
  f_scripts_test_reqmap_py_1197["scripts/test_reqmap.py:1197"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1197
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
