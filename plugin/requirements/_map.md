---
generated: 2026-08-20 18:26
nodes: 43
edges: 61
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
    REQ_ROADMAP_038["Roadmap coherence signals<br><small>REQ-ROADMAP-038</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
    REQ_SELFGATE_039["This repo's own gate wiring<br><small>REQ-SELFGATE-039</small>"]
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
  REQ_ROADMAP_038 --> REQ_HEALTH_017
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
  f_plugin_scripts_reqmap_py_1333_1377["plugin/scripts/reqmap.py:1333-1377"]
  CORE_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_py_1333_1377
  f_plugin_scripts_test_reqmap_py_153_4834["plugin/scripts/test_reqmap.py:153-4834"]
  CORE_DRIFT_003 -->|tested-by| f_plugin_scripts_test_reqmap_py_153_4834
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_plugin_scripts_reqmap_py_692_763["plugin/scripts/reqmap.py:692-763"]
  CORE_PARSE_001 -->|implements| f_plugin_scripts_reqmap_py_692_763
  f_plugin_scripts_test_reqmap_py_50_4787["plugin/scripts/test_reqmap.py:50-4787"]
  CORE_PARSE_001 -->|tested-by| f_plugin_scripts_test_reqmap_py_50_4787
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_plugin_scripts_reqmap_py_112_981["plugin/scripts/reqmap.py:112-981"]
  CORE_SCAN_002 -->|implements| f_plugin_scripts_reqmap_py_112_981
  f_plugin_scripts_test_reqmap_py_339_545["plugin/scripts/test_reqmap.py:339-545"]
  CORE_SCAN_002 -->|tested-by| f_plugin_scripts_test_reqmap_py_339_545
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_plugin_scripts_reqmap_py_1189_1728["plugin/scripts/reqmap.py:1189-1728"]
  REQ_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_py_1189_1728
  f_plugin_scripts_test_reqmap_py_3436_4818["plugin/scripts/test_reqmap.py:3436-4818"]
  REQ_ACVERIFY_019 -->|tested-by| f_plugin_scripts_test_reqmap_py_3436_4818
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_plugin_scripts_reqmap_py_2329_2477["plugin/scripts/reqmap.py:2329-2477"]
  REQ_CANDIDATES_009 -->|implements| f_plugin_scripts_reqmap_py_2329_2477
  f_plugin_scripts_test_reqmap_py_1180_2650["plugin/scripts/test_reqmap.py:1180-2650"]
  REQ_CANDIDATES_009 -->|tested-by| f_plugin_scripts_test_reqmap_py_1180_2650
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_plugin_scripts_reqmap_py_1320_1866["plugin/scripts/reqmap.py:1320-1866"]
  REQ_CHECK_006 -->|implements| f_plugin_scripts_reqmap_py_1320_1866
  f_plugin_scripts_test_reqmap_py_143_4996["plugin/scripts/test_reqmap.py:143-4996"]
  REQ_CHECK_006 -->|tested-by| f_plugin_scripts_test_reqmap_py_143_4996
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_plugin_scripts_reqmap_py_166_1888["plugin/scripts/reqmap.py:166-1888"]
  REQ_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_py_166_1888
  f_plugin_scripts_test_reqmap_py_4716["plugin/scripts/test_reqmap.py:4716"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_plugin_scripts_test_reqmap_py_4716
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_plugin_scripts_reqmap_py_3696["plugin/scripts/reqmap.py:3696"]
  REQ_COVERAGE_029 -->|implements| f_plugin_scripts_reqmap_py_3696
  f_plugin_scripts_test_reqmap_py_3167["plugin/scripts/test_reqmap.py:3167"]
  REQ_COVERAGE_029 -->|tested-by| f_plugin_scripts_test_reqmap_py_3167
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_plugin_scripts_reqmap_py_1102["plugin/scripts/reqmap.py:1102"]
  REQ_DOCBUNDLE_026 -->|implements| f_plugin_scripts_reqmap_py_1102
  f_plugin_scripts_test_reqmap_py_584["plugin/scripts/test_reqmap.py:584"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_plugin_scripts_test_reqmap_py_584
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_plugin_scripts_reqmap_py_1786["plugin/scripts/reqmap.py:1786"]
  REQ_DRIFTIMPACT_035 -->|implements| f_plugin_scripts_reqmap_py_1786
  f_plugin_scripts_test_reqmap_py_799["plugin/scripts/test_reqmap.py:799"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_plugin_scripts_test_reqmap_py_799
  REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
  f_plugin_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2["plugin/skills/excalidraw-diagram/scripts/excalidraw_builder.py:2"]
  REQ_EXCALIDRAW_030 -->|implements| f_plugin_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2
  f_plugin_skills_excalidraw_diagram_scripts_test_excalidraw_py_2["plugin/skills/excalidraw-diagram/scripts/test_excalidraw.py:2"]
  REQ_EXCALIDRAW_030 -->|tested-by| f_plugin_skills_excalidraw_diagram_scripts_test_excalidraw_py_2
  REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
  f_plugin_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3["plugin/skills/excalidraw-diagram/scripts/excalidraw_builder.py:3"]
  REQ_EXCALIDRAW_031 -->|implements| f_plugin_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3
  f_plugin_skills_excalidraw_diagram_scripts_test_excalidraw_py_3["plugin/skills/excalidraw-diagram/scripts/test_excalidraw.py:3"]
  REQ_EXCALIDRAW_031 -->|tested-by| f_plugin_skills_excalidraw_diagram_scripts_test_excalidraw_py_3
  REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
  f_plugin_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4["plugin/skills/excalidraw-diagram/scripts/excalidraw_builder.py:4"]
  REQ_EXCALIDRAW_032 -->|implements| f_plugin_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4
  f_plugin_skills_excalidraw_diagram_scripts_test_excalidraw_py_4["plugin/skills/excalidraw-diagram/scripts/test_excalidraw.py:4"]
  REQ_EXCALIDRAW_032 -->|tested-by| f_plugin_skills_excalidraw_diagram_scripts_test_excalidraw_py_4
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_plugin_scripts_reqmap_py_2160_2312["plugin/scripts/reqmap.py:2160-2312"]
  REQ_EXTRACT_008 -->|implements| f_plugin_scripts_reqmap_py_2160_2312
  f_plugin_scripts_test_reqmap_py_1023_1038["plugin/scripts/test_reqmap.py:1023-1038"]
  REQ_EXTRACT_008 -->|tested-by| f_plugin_scripts_test_reqmap_py_1023_1038
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_plugin_scripts_reqmap_py_2598_2685["plugin/scripts/reqmap.py:2598-2685"]
  REQ_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_py_2598_2685
  f_plugin_scripts_test_reqmap_py_1253_1795["plugin/scripts/test_reqmap.py:1253-1795"]
  REQ_FINDINGS_010 -->|tested-by| f_plugin_scripts_test_reqmap_py_1253_1795
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_plugin_scripts_reqmap_py_3634["plugin/scripts/reqmap.py:3634"]
  REQ_HEALTH_017 -->|implements| f_plugin_scripts_reqmap_py_3634
  f_plugin_scripts_test_reqmap_py_3124_3286["plugin/scripts/test_reqmap.py:3124-3286"]
  REQ_HEALTH_017 -->|tested-by| f_plugin_scripts_test_reqmap_py_3124_3286
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_plugin_scripts_reqmap_py_3825_3854["plugin/scripts/reqmap.py:3825-3854"]
  REQ_INIT_012 -->|implements| f_plugin_scripts_reqmap_py_3825_3854
  f_plugin_scripts_test_reqmap_py_2410_4948["plugin/scripts/test_reqmap.py:2410-4948"]
  REQ_INIT_012 -->|tested-by| f_plugin_scripts_test_reqmap_py_2410_4948
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_plugin_scripts_reqmap_py_3041_3247["plugin/scripts/reqmap.py:3041-3247"]
  REQ_LINT_014 -->|implements| f_plugin_scripts_reqmap_py_3041_3247
  f_plugin_scripts_test_reqmap_py_2678["plugin/scripts/test_reqmap.py:2678"]
  REQ_LINT_014 -->|tested-by| f_plugin_scripts_test_reqmap_py_2678
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_plugin_scripts_reqmap_py_3070_3108["plugin/scripts/reqmap.py:3070-3108"]
  REQ_LINTCHECKS_025 -->|implements| f_plugin_scripts_reqmap_py_3070_3108
  f_plugin_scripts_test_reqmap_py_2662_2678["plugin/scripts/test_reqmap.py:2662-2678"]
  REQ_LINTCHECKS_025 -->|tested-by| f_plugin_scripts_test_reqmap_py_2662_2678
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_plugin_scripts_reqmap_py_2725_4899["plugin/scripts/reqmap.py:2725-4899"]
  REQ_MAP_007 -->|implements| f_plugin_scripts_reqmap_py_2725_4899
  f_plugin_scripts_test_reqmap_py_880_4948["plugin/scripts/test_reqmap.py:880-4948"]
  REQ_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_py_880_4948
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_plugin_scripts_reqmap_py_1393_1480["plugin/scripts/reqmap.py:1393-1480"]
  REQ_MEMBERDRIFT_027 -->|implements| f_plugin_scripts_reqmap_py_1393_1480
  f_plugin_scripts_test_reqmap_py_639["plugin/scripts/test_reqmap.py:639"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_plugin_scripts_test_reqmap_py_639
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_plugin_scripts_reqmap_py_1991["plugin/scripts/reqmap.py:1991"]
  REQ_NEW_004 -->|implements| f_plugin_scripts_reqmap_py_1991
  f_plugin_scripts_test_reqmap_py_1102["plugin/scripts/test_reqmap.py:1102"]
  REQ_NEW_004 -->|tested-by| f_plugin_scripts_test_reqmap_py_1102
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_plugin_scripts_reqmap_py_1133_2917["plugin/scripts/reqmap.py:1133-2917"]
  REQ_NEXT_013 -->|implements| f_plugin_scripts_reqmap_py_1133_2917
  f_plugin_scripts_test_reqmap_py_2284_4898["plugin/scripts/test_reqmap.py:2284-4898"]
  REQ_NEXT_013 -->|tested-by| f_plugin_scripts_test_reqmap_py_2284_4898
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_plugin_scripts_reqmap_py_1160_1828["plugin/scripts/reqmap.py:1160-1828"]
  REQ_ORPHANCODE_034 -->|implements| f_plugin_scripts_reqmap_py_1160_1828
  f_plugin_scripts_test_reqmap_py_739["plugin/scripts/test_reqmap.py:739"]
  REQ_ORPHANCODE_034 -->|tested-by| f_plugin_scripts_test_reqmap_py_739
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_plugin_scripts_reqmap_py_2876_4915["plugin/scripts/reqmap.py:2876-4915"]
  REQ_PAGES_021 -->|implements| f_plugin_scripts_reqmap_py_2876_4915
  f_plugin_scripts_test_reqmap_py_1442_2121["plugin/scripts/test_reqmap.py:1442-2121"]
  REQ_PAGES_021 -->|tested-by| f_plugin_scripts_test_reqmap_py_1442_2121
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_plugin_scripts_reqmap_py_2100_2126["plugin/scripts/reqmap.py:2100-2126"]
  REQ_PROMOTE_011 -->|implements| f_plugin_scripts_reqmap_py_2100_2126
  f_plugin_scripts_test_reqmap_py_2224_4898["plugin/scripts/test_reqmap.py:2224-4898"]
  REQ_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_py_2224_4898
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_plugin_scripts_reqmap_py_2012_2068["plugin/scripts/reqmap.py:2012-2068"]
  REQ_PROMOTE_TODO_001 -->|implements| f_plugin_scripts_reqmap_py_2012_2068
  f_plugin_scripts_test_reqmap_py_3629_4898["plugin/scripts/test_reqmap.py:3629-4898"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_plugin_scripts_test_reqmap_py_3629_4898
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_plugin_scripts_reqmap_py_2168_2221["plugin/scripts/reqmap.py:2168-2221"]
  REQ_PROSE_024 -->|implements| f_plugin_scripts_reqmap_py_2168_2221
  f_plugin_scripts_test_reqmap_py_837_1023["plugin/scripts/test_reqmap.py:837-1023"]
  REQ_PROSE_024 -->|tested-by| f_plugin_scripts_test_reqmap_py_837_1023
  REQ_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>REQ-REGISTRYLAG-035</small>"]
  f_plugin_scripts_reqmap_py_3608_3702["plugin/scripts/reqmap.py:3608-3702"]
  REQ_REGISTRYLAG_035 -->|implements| f_plugin_scripts_reqmap_py_3608_3702
  f_plugin_scripts_test_reqmap_py_3192["plugin/scripts/test_reqmap.py:3192"]
  REQ_REGISTRYLAG_035 -->|tested-by| f_plugin_scripts_test_reqmap_py_3192
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_plugin_scripts_reqmap_py_5066["plugin/scripts/reqmap.py:5066"]
  REQ_REVIEW_022 -->|implements| f_plugin_scripts_reqmap_py_5066
  f_plugin_scripts_test_reqmap_py_3696["plugin/scripts/test_reqmap.py:3696"]
  REQ_REVIEW_022 -->|tested-by| f_plugin_scripts_test_reqmap_py_3696
  f_plugin_skills_requirement_quality_review_SKILL_md_6["plugin/skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_plugin_skills_requirement_quality_review_SKILL_md_6
  f_plugin_skills_requirement_quality_review_SKILL_universal_md_9["plugin/skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_plugin_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_ROADMAP_038["Roadmap coherence signals<br><small>REQ-ROADMAP-038</small>"]
  f_plugin_scripts_reqmap_py_2781_3708["plugin/scripts/reqmap.py:2781-3708"]
  REQ_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_py_2781_3708
  f_plugin_scripts_test_reqmap_py_5022["plugin/scripts/test_reqmap.py:5022"]
  REQ_ROADMAP_038 -->|tested-by| f_plugin_scripts_test_reqmap_py_5022
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_plugin_scripts_reqmap_py_1517["plugin/scripts/reqmap.py:1517"]
  REQ_SCAN_005 -->|implements| f_plugin_scripts_reqmap_py_1517
  f_plugin_scripts_test_reqmap_py_1166["plugin/scripts/test_reqmap.py:1166"]
  REQ_SCAN_005 -->|tested-by| f_plugin_scripts_test_reqmap_py_1166
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_plugin_scripts_reqmap_py_958_972["plugin/scripts/reqmap.py:958-972"]
  REQ_SCANCACHE_023 -->|implements| f_plugin_scripts_reqmap_py_958_972
  f_plugin_scripts_test_reqmap_py_3757["plugin/scripts/test_reqmap.py:3757"]
  REQ_SCANCACHE_023 -->|tested-by| f_plugin_scripts_test_reqmap_py_3757
  REQ_SEARCH_036["Free-text requirement search<br><small>REQ-SEARCH-036</small>"]
  f_plugin_scripts_reqmap_py_3487["plugin/scripts/reqmap.py:3487"]
  REQ_SEARCH_036 -->|implements| f_plugin_scripts_reqmap_py_3487
  f_plugin_scripts_test_reqmap_py_3044["plugin/scripts/test_reqmap.py:3044"]
  REQ_SEARCH_036 -->|tested-by| f_plugin_scripts_test_reqmap_py_3044
  REQ_SELFGATE_039["This repo's own gate wiring<br><small>REQ-SELFGATE-039</small>"]
  f_sync_reqmap_sh_2["sync_reqmap.sh:2"]
  REQ_SELFGATE_039 -->|implements| f_sync_reqmap_sh_2
  f__githooks_pre_commit_2[".githooks/pre-commit:2"]
  REQ_SELFGATE_039 -->|implements| f__githooks_pre_commit_2
  f__githooks_pre_push_2[".githooks/pre-push:2"]
  REQ_SELFGATE_039 -->|implements| f__githooks_pre_push_2
  f__github_workflows_ci_yml_2[".github/workflows/ci.yml:2"]
  REQ_SELFGATE_039 -->|implements| f__github_workflows_ci_yml_2
  f_check_action_yml_2["check/action.yml:2"]
  REQ_SELFGATE_039 -->|implements| f_check_action_yml_2
  f_scripts_check_versions_py_2["scripts/check_versions.py:2"]
  REQ_SELFGATE_039 -->|implements| f_scripts_check_versions_py_2
  f_scripts_test_check_versions_py_91["scripts/test_check_versions.py:91"]
  REQ_SELFGATE_039 -->|tested-by| f_scripts_test_check_versions_py_91
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_plugin_scripts_reqmap_py_3289["plugin/scripts/reqmap.py:3289"]
  REQ_SHOW_015 -->|implements| f_plugin_scripts_reqmap_py_3289
  f_plugin_scripts_test_reqmap_py_2900["plugin/scripts/test_reqmap.py:2900"]
  REQ_SHOW_015 -->|tested-by| f_plugin_scripts_test_reqmap_py_2900
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_plugin_scripts_reqmap_py_3378_3439["plugin/scripts/reqmap.py:3378-3439"]
  REQ_SIMILAR_016 -->|implements| f_plugin_scripts_reqmap_py_3378_3439
  f_plugin_scripts_test_reqmap_py_2982["plugin/scripts/test_reqmap.py:2982"]
  REQ_SIMILAR_016 -->|tested-by| f_plugin_scripts_test_reqmap_py_2982
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_plugin_scripts_reqmap_py_3880_5283["plugin/scripts/reqmap.py:3880-5283"]
  REQ_SITE_026 -->|implements| f_plugin_scripts_reqmap_py_3880_5283
  f_plugin_scripts_test_reqmap_py_4398["plugin/scripts/test_reqmap.py:4398"]
  REQ_SITE_026 -->|tested-by| f_plugin_scripts_test_reqmap_py_4398
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_plugin_scripts_reqmap_py_1589_1720["plugin/scripts/reqmap.py:1589-1720"]
  REQ_TESTLINK_018 -->|implements| f_plugin_scripts_reqmap_py_1589_1720
  f_plugin_scripts_test_reqmap_py_3360["plugin/scripts/test_reqmap.py:3360"]
  REQ_TESTLINK_018 -->|tested-by| f_plugin_scripts_test_reqmap_py_3360
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_plugin_scripts_reqmap_py_1676_3324["plugin/scripts/reqmap.py:1676-3324"]
  REQ_TRACE_020 -->|implements| f_plugin_scripts_reqmap_py_1676_3324
  f_plugin_scripts_test_reqmap_py_3506["plugin/scripts/test_reqmap.py:3506"]
  REQ_TRACE_020 -->|tested-by| f_plugin_scripts_test_reqmap_py_3506
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_plugin_scripts_reqmap_py_1074_5050["plugin/scripts/reqmap.py:1074-5050"]
  REQ_VIEWER_007 -->|implements| f_plugin_scripts_reqmap_py_1074_5050
  f_plugin_scripts_test_reqmap_py_1415_5065["plugin/scripts/test_reqmap.py:1415-5065"]
  REQ_VIEWER_007 -->|tested-by| f_plugin_scripts_test_reqmap_py_1415_5065
  REQ_VLEVEL_037["Verification levels<br><small>REQ-VLEVEL-037</small>"]
  f_plugin_scripts_reqmap_py_1232_3289["plugin/scripts/reqmap.py:1232-3289"]
  REQ_VLEVEL_037 -->|implements| f_plugin_scripts_reqmap_py_1232_3289
  f_plugin_scripts_test_reqmap_py_271_2972["plugin/scripts/test_reqmap.py:271-2972"]
  REQ_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_py_271_2972
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>39 caps</small>"]
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
