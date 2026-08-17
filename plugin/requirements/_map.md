---
generated: 2026-08-17 16:14
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
  f_scripts_reqmap_py_1241_1285["scripts/reqmap.py:1241-1285"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1241_1285
  f_scripts_test_reqmap_py_153_4651["scripts/test_reqmap.py:153-4651"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_153_4651
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_671_742["scripts/reqmap.py:671-742"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_671_742
  f_scripts_test_reqmap_py_50_4604["scripts/test_reqmap.py:50-4604"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_50_4604
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_765_960["scripts/reqmap.py:765-960"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_765_960
  f_scripts_test_reqmap_py_339["scripts/test_reqmap.py:339"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_339
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1097_1636["scripts/reqmap.py:1097-1636"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1097_1636
  f_scripts_test_reqmap_py_3253_4635["scripts/test_reqmap.py:3253-4635"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_3253_4635
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2217_2365["scripts/reqmap.py:2217-2365"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2217_2365
  f_scripts_test_reqmap_py_1085_2467["scripts/test_reqmap.py:1085-2467"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_1085_2467
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1228_1754["scripts/reqmap.py:1228-1754"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1228_1754
  f_scripts_test_reqmap_py_143_4813["scripts/test_reqmap.py:143-4813"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_143_4813
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_145_1776["scripts/reqmap.py:145-1776"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_145_1776
  f_scripts_test_reqmap_py_4533["scripts/test_reqmap.py:4533"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4533
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3539["scripts/reqmap.py:3539"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3539
  f_scripts_test_reqmap_py_2984["scripts/test_reqmap.py:2984"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2984
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_1010["scripts/reqmap.py:1010"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_1010
  f_scripts_test_reqmap_py_489["scripts/test_reqmap.py:489"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_489
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1674["scripts/reqmap.py:1674"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1674
  f_scripts_test_reqmap_py_704["scripts/test_reqmap.py:704"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_704
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
  f_scripts_reqmap_py_2048_2200["scripts/reqmap.py:2048-2200"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_2048_2200
  f_scripts_test_reqmap_py_928_943["scripts/test_reqmap.py:928-943"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_928_943
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2486_2573["scripts/reqmap.py:2486-2573"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2486_2573
  f_scripts_test_reqmap_py_1158_1700["scripts/test_reqmap.py:1158-1700"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1158_1700
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3477["scripts/reqmap.py:3477"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3477
  f_scripts_test_reqmap_py_2941_3103["scripts/test_reqmap.py:2941-3103"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2941_3103
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3656_3685["scripts/reqmap.py:3656-3685"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3656_3685
  f_scripts_test_reqmap_py_2227_4765["scripts/test_reqmap.py:2227-4765"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2227_4765
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2889_3090["scripts/reqmap.py:2889-3090"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2889_3090
  f_scripts_test_reqmap_py_2495["scripts/test_reqmap.py:2495"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2495
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2918_2956["scripts/reqmap.py:2918-2956"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2918_2956
  f_scripts_test_reqmap_py_2479_2495["scripts/test_reqmap.py:2479-2495"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2479_2495
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2613_4723["scripts/reqmap.py:2613-4723"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2613_4723
  f_scripts_test_reqmap_py_785_4765["scripts/test_reqmap.py:785-4765"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_785_4765
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1301_1388["scripts/reqmap.py:1301-1388"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1301_1388
  f_scripts_test_reqmap_py_544["scripts/test_reqmap.py:544"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_544
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1879["scripts/reqmap.py:1879"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1879
  f_scripts_test_reqmap_py_1007["scripts/test_reqmap.py:1007"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_1007
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1041_2765["scripts/reqmap.py:1041-2765"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1041_2765
  f_scripts_test_reqmap_py_2101_4715["scripts/test_reqmap.py:2101-4715"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_2101_4715
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1068_1716["scripts/reqmap.py:1068-1716"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1068_1716
  f_scripts_test_reqmap_py_644["scripts/test_reqmap.py:644"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_644
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2724_4739["scripts/reqmap.py:2724-4739"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2724_4739
  f_scripts_test_reqmap_py_1347_1938["scripts/test_reqmap.py:1347-1938"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1347_1938
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1988_2014["scripts/reqmap.py:1988-2014"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1988_2014
  f_scripts_test_reqmap_py_2041_4715["scripts/test_reqmap.py:2041-4715"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_2041_4715
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1900_1956["scripts/reqmap.py:1900-1956"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1900_1956
  f_scripts_test_reqmap_py_3446_4715["scripts/test_reqmap.py:3446-4715"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3446_4715
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_2056_2109["scripts/reqmap.py:2056-2109"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_2056_2109
  f_scripts_test_reqmap_py_742_928["scripts/test_reqmap.py:742-928"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_742_928
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_scripts_reqmap_py_3451_3545["scripts/reqmap.py:3451-3545"]
  REQ_REGISTRYLAG_035 -->|implements| f_scripts_reqmap_py_3451_3545
  f_scripts_test_reqmap_py_3009["scripts/test_reqmap.py:3009"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_scripts_test_reqmap_py_3009
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4890["scripts/reqmap.py:4890"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4890
  f_scripts_test_reqmap_py_3513["scripts/test_reqmap.py:3513"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3513
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1425["scripts/reqmap.py:1425"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1425
  f_scripts_test_reqmap_py_1071["scripts/test_reqmap.py:1071"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_1071
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_937_951["scripts/reqmap.py:937-951"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_937_951
  f_scripts_test_reqmap_py_3574["scripts/test_reqmap.py:3574"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3574
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_scripts_reqmap_py_3330["scripts/reqmap.py:3330"]
  REQ_SEARCH_036 -->|implements| f_scripts_reqmap_py_3330
  f_scripts_test_reqmap_py_2861["scripts/test_reqmap.py:2861"]
  REQ_SEARCH_036 -->|tested-by| f_scripts_test_reqmap_py_2861
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_3132["scripts/reqmap.py:3132"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_3132
  f_scripts_test_reqmap_py_2717["scripts/test_reqmap.py:2717"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2717
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3221_3282["scripts/reqmap.py:3221-3282"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3221_3282
  f_scripts_test_reqmap_py_2799["scripts/test_reqmap.py:2799"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2799
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3711_5107["scripts/reqmap.py:3711-5107"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3711_5107
  f_scripts_test_reqmap_py_4215["scripts/test_reqmap.py:4215"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_4215
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1497_1628["scripts/reqmap.py:1497-1628"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1497_1628
  f_scripts_test_reqmap_py_3177["scripts/test_reqmap.py:3177"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_3177
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1584_3167["scripts/reqmap.py:1584-3167"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1584_3167
  f_scripts_test_reqmap_py_3323["scripts/test_reqmap.py:3323"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_3323
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4852_4874["scripts/reqmap.py:4852-4874"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4852_4874
  f_scripts_test_reqmap_py_1320["scripts/test_reqmap.py:1320"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1320
  REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small>"]
  f_scripts_reqmap_py_1140_3132["scripts/reqmap.py:1140-3132"]
  REQ_VLEVEL_037 -->|implements| f_scripts_reqmap_py_1140_3132
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
    REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small><br>untested"]
  end
  style REQ_VLEVEL_037 fill:#fff9c4,stroke:#aa0,color:#550
```

### Risk Table

| ID | status | members | dependents | risks | recommendation |
| --- | --- | --- | --- | --- | --- |
| REQ-VLEVEL-037 | confirmed | 2 | 0 | untested | Implemented but no `tested-by` member: write an acceptance test and tag it `# tested-by: <ID>`, or set `test_exempt: <reason>` in the frontmatter to acknowledge it intentionally and silence this signal. |
