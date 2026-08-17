---
generated: 2026-08-17 18:45
nodes: 41
edges: 59
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
    REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small>"]
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
  f_scripts_reqmap_py_1245_1289["scripts/reqmap.py:1245-1289"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1245_1289
  f_scripts_test_reqmap_py_153_4661["scripts/test_reqmap.py:153-4661"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_153_4661
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_675_746["scripts/reqmap.py:675-746"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_675_746
  f_scripts_test_reqmap_py_50_4614["scripts/test_reqmap.py:50-4614"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_50_4614
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_769_964["scripts/reqmap.py:769-964"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_769_964
  f_scripts_test_reqmap_py_339["scripts/test_reqmap.py:339"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_339
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1101_1640["scripts/reqmap.py:1101-1640"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1101_1640
  f_scripts_test_reqmap_py_3263_4645["scripts/test_reqmap.py:3263-4645"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_3263_4645
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2221_2369["scripts/reqmap.py:2221-2369"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2221_2369
  f_scripts_test_reqmap_py_1095_2477["scripts/test_reqmap.py:1095-2477"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_1095_2477
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1232_1758["scripts/reqmap.py:1232-1758"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1232_1758
  f_scripts_test_reqmap_py_143_4823["scripts/test_reqmap.py:143-4823"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_143_4823
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_149_1780["scripts/reqmap.py:149-1780"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_149_1780
  f_scripts_test_reqmap_py_4543["scripts/test_reqmap.py:4543"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4543
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3543["scripts/reqmap.py:3543"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3543
  f_scripts_test_reqmap_py_2994["scripts/test_reqmap.py:2994"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2994
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_1014["scripts/reqmap.py:1014"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_1014
  f_scripts_test_reqmap_py_499["scripts/test_reqmap.py:499"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_499
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1678["scripts/reqmap.py:1678"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1678
  f_scripts_test_reqmap_py_714["scripts/test_reqmap.py:714"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_714
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
  f_scripts_reqmap_py_2052_2204["scripts/reqmap.py:2052-2204"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_2052_2204
  f_scripts_test_reqmap_py_938_953["scripts/test_reqmap.py:938-953"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_938_953
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2490_2577["scripts/reqmap.py:2490-2577"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2490_2577
  f_scripts_test_reqmap_py_1168_1710["scripts/test_reqmap.py:1168-1710"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1168_1710
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3481["scripts/reqmap.py:3481"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3481
  f_scripts_test_reqmap_py_2951_3113["scripts/test_reqmap.py:2951-3113"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2951_3113
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3660_3689["scripts/reqmap.py:3660-3689"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3660_3689
  f_scripts_test_reqmap_py_2237_4775["scripts/test_reqmap.py:2237-4775"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2237_4775
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2893_3094["scripts/reqmap.py:2893-3094"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2893_3094
  f_scripts_test_reqmap_py_2505["scripts/test_reqmap.py:2505"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2505
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2922_2960["scripts/reqmap.py:2922-2960"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2922_2960
  f_scripts_test_reqmap_py_2489_2505["scripts/test_reqmap.py:2489-2505"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2489_2505
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2617_4718["scripts/reqmap.py:2617-4718"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2617_4718
  f_scripts_test_reqmap_py_795_4775["scripts/test_reqmap.py:795-4775"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_795_4775
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1305_1392["scripts/reqmap.py:1305-1392"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1305_1392
  f_scripts_test_reqmap_py_554["scripts/test_reqmap.py:554"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_554
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1883["scripts/reqmap.py:1883"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1883
  f_scripts_test_reqmap_py_1017["scripts/test_reqmap.py:1017"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_1017
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1045_2769["scripts/reqmap.py:1045-2769"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1045_2769
  f_scripts_test_reqmap_py_2111_4725["scripts/test_reqmap.py:2111-4725"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_2111_4725
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1072_1720["scripts/reqmap.py:1072-1720"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1072_1720
  f_scripts_test_reqmap_py_654["scripts/test_reqmap.py:654"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_654
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2728_4734["scripts/reqmap.py:2728-4734"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2728_4734
  f_scripts_test_reqmap_py_1357_1948["scripts/test_reqmap.py:1357-1948"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1357_1948
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1992_2018["scripts/reqmap.py:1992-2018"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1992_2018
  f_scripts_test_reqmap_py_2051_4725["scripts/test_reqmap.py:2051-4725"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_2051_4725
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1904_1960["scripts/reqmap.py:1904-1960"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1904_1960
  f_scripts_test_reqmap_py_3456_4725["scripts/test_reqmap.py:3456-4725"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3456_4725
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_2060_2113["scripts/reqmap.py:2060-2113"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_2060_2113
  f_scripts_test_reqmap_py_752_938["scripts/test_reqmap.py:752-938"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_752_938
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_scripts_reqmap_py_3455_3549["scripts/reqmap.py:3455-3549"]
  REQ_REGISTRYLAG_035 -->|implements| f_scripts_reqmap_py_3455_3549
  f_scripts_test_reqmap_py_3019["scripts/test_reqmap.py:3019"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_scripts_test_reqmap_py_3019
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4885["scripts/reqmap.py:4885"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4885
  f_scripts_test_reqmap_py_3523["scripts/test_reqmap.py:3523"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3523
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1429["scripts/reqmap.py:1429"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1429
  f_scripts_test_reqmap_py_1081["scripts/test_reqmap.py:1081"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_1081
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_941_955["scripts/reqmap.py:941-955"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_941_955
  f_scripts_test_reqmap_py_3584["scripts/test_reqmap.py:3584"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3584
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_scripts_reqmap_py_3334["scripts/reqmap.py:3334"]
  REQ_SEARCH_036 -->|implements| f_scripts_reqmap_py_3334
  f_scripts_test_reqmap_py_2871["scripts/test_reqmap.py:2871"]
  REQ_SEARCH_036 -->|tested-by| f_scripts_test_reqmap_py_2871
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_3136["scripts/reqmap.py:3136"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_3136
  f_scripts_test_reqmap_py_2727["scripts/test_reqmap.py:2727"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2727
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3225_3286["scripts/reqmap.py:3225-3286"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3225_3286
  f_scripts_test_reqmap_py_2809["scripts/test_reqmap.py:2809"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2809
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3715_5102["scripts/reqmap.py:3715-5102"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3715_5102
  f_scripts_test_reqmap_py_4225["scripts/test_reqmap.py:4225"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_4225
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1501_1632["scripts/reqmap.py:1501-1632"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1501_1632
  f_scripts_test_reqmap_py_3187["scripts/test_reqmap.py:3187"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_3187
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1588_3171["scripts/reqmap.py:1588-3171"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1588_3171
  f_scripts_test_reqmap_py_3333["scripts/test_reqmap.py:3333"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_3333
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4847_4869["scripts/reqmap.py:4847-4869"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4847_4869
  f_scripts_test_reqmap_py_1330["scripts/test_reqmap.py:1330"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1330
  REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small>"]
  f_scripts_reqmap_py_1144_3136["scripts/reqmap.py:1144-3136"]
  REQ_VLEVEL_037 -->|implements| f_scripts_reqmap_py_1144_3136
  f_scripts_test_reqmap_py_271_2799["scripts/test_reqmap.py:271-2799"]
  REQ_VLEVEL_037 -->|tested-by| f_scripts_test_reqmap_py_271_2799
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>37 caps</small>"]
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
