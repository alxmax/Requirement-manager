---
generated: 2026-07-05 12:54
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
  f_scripts_reqmap_py_1177_1221["scripts/reqmap.py:1177-1221"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1177_1221
  f_scripts_test_reqmap_py_152_4415["scripts/test_reqmap.py:152-4415"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_152_4415
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_657_728["scripts/reqmap.py:657-728"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_657_728
  f_scripts_test_reqmap_py_49_4368["scripts/test_reqmap.py:49-4368"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_49_4368
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_751_946["scripts/reqmap.py:751-946"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_751_946
  f_scripts_test_reqmap_py_271["scripts/test_reqmap.py:271"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_271
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1083_1550["scripts/reqmap.py:1083-1550"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1083_1550
  f_scripts_test_reqmap_py_3017_4399["scripts/test_reqmap.py:3017-4399"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_3017_4399
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2116_2264["scripts/reqmap.py:2116-2264"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2116_2264
  f_scripts_test_reqmap_py_941_2311["scripts/test_reqmap.py:941-2311"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_941_2311
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1164_1668["scripts/reqmap.py:1164-1668"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1164_1668
  f_scripts_test_reqmap_py_142_4577["scripts/test_reqmap.py:142-4577"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_142_4577
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_132_1690["scripts/reqmap.py:132-1690"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_132_1690
  f_scripts_test_reqmap_py_4297["scripts/test_reqmap.py:4297"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4297
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3410["scripts/reqmap.py:3410"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3410
  f_scripts_test_reqmap_py_2748["scripts/test_reqmap.py:2748"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2748
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_996["scripts/reqmap.py:996"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_996
  f_scripts_test_reqmap_py_382["scripts/test_reqmap.py:382"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_382
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1588["scripts/reqmap.py:1588"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1588
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
  f_scripts_reqmap_py_1953_2099["scripts/reqmap.py:1953-2099"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1953_2099
  f_scripts_test_reqmap_py_821_836["scripts/test_reqmap.py:821-836"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_821_836
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2385_2472["scripts/reqmap.py:2385-2472"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2385_2472
  f_scripts_test_reqmap_py_1014_1556["scripts/test_reqmap.py:1014-1556"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1014_1556
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3348["scripts/reqmap.py:3348"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3348
  f_scripts_test_reqmap_py_2705_2867["scripts/test_reqmap.py:2705-2867"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2705_2867
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3527_3556["scripts/reqmap.py:3527-3556"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3527_3556
  f_scripts_test_reqmap_py_2071_4529["scripts/test_reqmap.py:2071-4529"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2071_4529
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2788_2968["scripts/reqmap.py:2788-2968"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2788_2968
  f_scripts_test_reqmap_py_2339["scripts/test_reqmap.py:2339"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2339
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2817_2855["scripts/reqmap.py:2817-2855"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2817_2855
  f_scripts_test_reqmap_py_2323_2339["scripts/test_reqmap.py:2323-2339"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2323_2339
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2512_4587["scripts/reqmap.py:2512-4587"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2512_4587
  f_scripts_test_reqmap_py_678_4529["scripts/test_reqmap.py:678-4529"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_678_4529
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1237_1324["scripts/reqmap.py:1237-1324"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1237_1324
  f_scripts_test_reqmap_py_437["scripts/test_reqmap.py:437"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_437
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1784["scripts/reqmap.py:1784"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1784
  f_scripts_test_reqmap_py_883["scripts/test_reqmap.py:883"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_883
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1027_2664["scripts/reqmap.py:1027-2664"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1027_2664
  f_scripts_test_reqmap_py_1945_4479["scripts/test_reqmap.py:1945-4479"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1945_4479
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1054_1630["scripts/reqmap.py:1054-1630"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1054_1630
  f_scripts_test_reqmap_py_537["scripts/test_reqmap.py:537"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_537
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2623_4603["scripts/reqmap.py:2623-4603"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2623_4603
  f_scripts_test_reqmap_py_1203_1782["scripts/test_reqmap.py:1203-1782"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1203_1782
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1893_1919["scripts/reqmap.py:1893-1919"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1893_1919
  f_scripts_test_reqmap_py_1885_4479["scripts/test_reqmap.py:1885-4479"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1885_4479
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1805_1861["scripts/reqmap.py:1805-1861"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1805_1861
  f_scripts_test_reqmap_py_3210_4479["scripts/test_reqmap.py:3210-4479"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3210_4479
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1961_2014["scripts/reqmap.py:1961-2014"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1961_2014
  f_scripts_test_reqmap_py_635_821["scripts/test_reqmap.py:635-821"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_635_821
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_scripts_reqmap_py_3322_3416["scripts/reqmap.py:3322-3416"]
  REQ_REGISTRYLAG_035 -->|implements| f_scripts_reqmap_py_3322_3416
  f_scripts_test_reqmap_py_2773["scripts/test_reqmap.py:2773"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_scripts_test_reqmap_py_2773
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4754["scripts/reqmap.py:4754"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4754
  f_scripts_test_reqmap_py_3277["scripts/test_reqmap.py:3277"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3277
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1361["scripts/reqmap.py:1361"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1361
  f_scripts_test_reqmap_py_927["scripts/test_reqmap.py:927"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_927
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_923_937["scripts/reqmap.py:923-937"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_923_937
  f_scripts_test_reqmap_py_3338["scripts/test_reqmap.py:3338"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3338
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_scripts_reqmap_py_3201["scripts/reqmap.py:3201"]
  REQ_SEARCH_036 -->|implements| f_scripts_reqmap_py_3201
  f_scripts_test_reqmap_py_2625["scripts/test_reqmap.py:2625"]
  REQ_SEARCH_036 -->|tested-by| f_scripts_test_reqmap_py_2625
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_3010["scripts/reqmap.py:3010"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_3010
  f_scripts_test_reqmap_py_2499["scripts/test_reqmap.py:2499"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2499
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3092_3153["scripts/reqmap.py:3092-3153"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3092_3153
  f_scripts_test_reqmap_py_2563["scripts/test_reqmap.py:2563"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2563
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3582_4971["scripts/reqmap.py:3582-4971"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3582_4971
  f_scripts_test_reqmap_py_3979["scripts/test_reqmap.py:3979"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3979
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1433_1542["scripts/reqmap.py:1433-1542"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1433_1542
  f_scripts_test_reqmap_py_2941["scripts/test_reqmap.py:2941"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2941
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1514_3045["scripts/reqmap.py:1514-3045"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1514_3045
  f_scripts_test_reqmap_py_3087["scripts/test_reqmap.py:3087"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_3087
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4716_4738["scripts/reqmap.py:4716-4738"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4716_4738
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
