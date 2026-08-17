---
generated: 2026-08-17 16:03
nodes: 41
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
  f_scripts_reqmap_py_1241_1285["scripts/reqmap.py:1241-1285"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1241_1285
  f_scripts_test_reqmap_py_153_4590["scripts/test_reqmap.py:153-4590"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_153_4590
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_671_742["scripts/reqmap.py:671-742"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_671_742
  f_scripts_test_reqmap_py_50_4543["scripts/test_reqmap.py:50-4543"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_50_4543
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_765_960["scripts/reqmap.py:765-960"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_765_960
  f_scripts_test_reqmap_py_296["scripts/test_reqmap.py:296"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_296
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1097_1627["scripts/reqmap.py:1097-1627"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1097_1627
  f_scripts_test_reqmap_py_3192_4574["scripts/test_reqmap.py:3192-4574"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_3192_4574
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2208_2356["scripts/reqmap.py:2208-2356"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2208_2356
  f_scripts_test_reqmap_py_1042_2424["scripts/test_reqmap.py:1042-2424"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_1042_2424
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1228_1745["scripts/reqmap.py:1228-1745"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1228_1745
  f_scripts_test_reqmap_py_143_4752["scripts/test_reqmap.py:143-4752"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_143_4752
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_145_1767["scripts/reqmap.py:145-1767"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_145_1767
  f_scripts_test_reqmap_py_4472["scripts/test_reqmap.py:4472"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4472
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3523["scripts/reqmap.py:3523"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3523
  f_scripts_test_reqmap_py_2923["scripts/test_reqmap.py:2923"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2923
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_1010["scripts/reqmap.py:1010"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_1010
  f_scripts_test_reqmap_py_446["scripts/test_reqmap.py:446"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_446
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1665["scripts/reqmap.py:1665"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1665
  f_scripts_test_reqmap_py_661["scripts/test_reqmap.py:661"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_661
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
  f_scripts_reqmap_py_2039_2191["scripts/reqmap.py:2039-2191"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_2039_2191
  f_scripts_test_reqmap_py_885_900["scripts/test_reqmap.py:885-900"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_885_900
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2477_2564["scripts/reqmap.py:2477-2564"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2477_2564
  f_scripts_test_reqmap_py_1115_1657["scripts/test_reqmap.py:1115-1657"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1115_1657
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3461["scripts/reqmap.py:3461"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3461
  f_scripts_test_reqmap_py_2880_3042["scripts/test_reqmap.py:2880-3042"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2880_3042
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3640_3669["scripts/reqmap.py:3640-3669"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3640_3669
  f_scripts_test_reqmap_py_2184_4704["scripts/test_reqmap.py:2184-4704"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2184_4704
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2880_3081["scripts/reqmap.py:2880-3081"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2880_3081
  f_scripts_test_reqmap_py_2452["scripts/test_reqmap.py:2452"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2452
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2909_2947["scripts/reqmap.py:2909-2947"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2909_2947
  f_scripts_test_reqmap_py_2436_2452["scripts/test_reqmap.py:2436-2452"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2436_2452
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2604_4707["scripts/reqmap.py:2604-4707"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2604_4707
  f_scripts_test_reqmap_py_742_4704["scripts/test_reqmap.py:742-4704"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_742_4704
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1301_1388["scripts/reqmap.py:1301-1388"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1301_1388
  f_scripts_test_reqmap_py_501["scripts/test_reqmap.py:501"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_501
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1870["scripts/reqmap.py:1870"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1870
  f_scripts_test_reqmap_py_964["scripts/test_reqmap.py:964"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_964
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1041_2756["scripts/reqmap.py:1041-2756"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1041_2756
  f_scripts_test_reqmap_py_2058_4654["scripts/test_reqmap.py:2058-4654"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_2058_4654
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1068_1707["scripts/reqmap.py:1068-1707"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1068_1707
  f_scripts_test_reqmap_py_601["scripts/test_reqmap.py:601"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_601
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2715_4723["scripts/reqmap.py:2715-4723"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2715_4723
  f_scripts_test_reqmap_py_1304_1895["scripts/test_reqmap.py:1304-1895"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1304_1895
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1979_2005["scripts/reqmap.py:1979-2005"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1979_2005
  f_scripts_test_reqmap_py_1998_4654["scripts/test_reqmap.py:1998-4654"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1998_4654
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1891_1947["scripts/reqmap.py:1891-1947"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1891_1947
  f_scripts_test_reqmap_py_3385_4654["scripts/test_reqmap.py:3385-4654"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3385_4654
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_2047_2100["scripts/reqmap.py:2047-2100"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_2047_2100
  f_scripts_test_reqmap_py_699_885["scripts/test_reqmap.py:699-885"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_699_885
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_scripts_reqmap_py_3435_3529["scripts/reqmap.py:3435-3529"]
  REQ_REGISTRYLAG_035 -->|implements| f_scripts_reqmap_py_3435_3529
  f_scripts_test_reqmap_py_2948["scripts/test_reqmap.py:2948"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_scripts_test_reqmap_py_2948
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4874["scripts/reqmap.py:4874"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4874
  f_scripts_test_reqmap_py_3452["scripts/test_reqmap.py:3452"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3452
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1425["scripts/reqmap.py:1425"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1425
  f_scripts_test_reqmap_py_1028["scripts/test_reqmap.py:1028"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_1028
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_937_951["scripts/reqmap.py:937-951"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_937_951
  f_scripts_test_reqmap_py_3513["scripts/test_reqmap.py:3513"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3513
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_scripts_reqmap_py_3314["scripts/reqmap.py:3314"]
  REQ_SEARCH_036 -->|implements| f_scripts_reqmap_py_3314
  f_scripts_test_reqmap_py_2800["scripts/test_reqmap.py:2800"]
  REQ_SEARCH_036 -->|tested-by| f_scripts_test_reqmap_py_2800
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_3123["scripts/reqmap.py:3123"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_3123
  f_scripts_test_reqmap_py_2674["scripts/test_reqmap.py:2674"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2674
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3205_3266["scripts/reqmap.py:3205-3266"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3205_3266
  f_scripts_test_reqmap_py_2738["scripts/test_reqmap.py:2738"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2738
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3695_5091["scripts/reqmap.py:3695-5091"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3695_5091
  f_scripts_test_reqmap_py_4154["scripts/test_reqmap.py:4154"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_4154
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1497_1619["scripts/reqmap.py:1497-1619"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1497_1619
  f_scripts_test_reqmap_py_3116["scripts/test_reqmap.py:3116"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_3116
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1584_3158["scripts/reqmap.py:1584-3158"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1584_3158
  f_scripts_test_reqmap_py_3262["scripts/test_reqmap.py:3262"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_3262
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4836_4858["scripts/reqmap.py:4836-4858"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4836_4858
  f_scripts_test_reqmap_py_1277["scripts/test_reqmap.py:1277"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1277
  REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small>"]
  f_scripts_reqmap_py_1140["scripts/reqmap.py:1140"]
  REQ_VLEVEL_037 -->|implements| f_scripts_reqmap_py_1140
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
  subgraph sg_misc["misc"]
    REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small><br>unreviewed, untested"]
  end
  style REQ_VLEVEL_037 fill:#fff3cd,stroke:#a66,color:#630
```

### Risk Table

| ID | status | members | dependents | risks | recommendation |
| --- | --- | --- | --- | --- | --- |
| REQ-VLEVEL-037 | draft | 1 | 0 | unreviewed, untested | Draft/baseline, not yet validated: review the contract, wire its `tested-by` tests, then promote to `confirmed`. Until then it is tracked, not enforced. Implemented but no `tested-by` member: write an acceptance test and tag it `# tested-by: <ID>`, or set `test_exempt: <reason>` in the frontmatter to acknowledge it intentionally and silence this signal. |
