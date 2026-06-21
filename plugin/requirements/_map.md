---
generated: 2026-06-21 20:19
nodes: 36
edges: 50
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
  REQ_ACVERIFY_019 --> REQ_CHECK_006
  REQ_COVERAGE_029 --> REQ_NEXT_013
  REQ_DOCBUNDLE_026 --> REQ_CHECK_006
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_MEMBERDRIFT_027 --> REQ_CHECK_006
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
  REQ_SITE_026 --> REQ_MAP_007
  REQ_SITE_026 --> REQ_VIEWER_007
  REQ_SITE_026 --> REQ_PAGES_021
  REQ_TESTLINK_018 --> REQ_CHECK_006
  REQ_TRACE_020 --> REQ_CHECK_006
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
  f_scripts_reqmap_py_1073_1110["scripts/reqmap.py:1073-1110"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1073_1110
  f_scripts_test_reqmap_py_151_193["scripts/test_reqmap.py:151-193"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_193
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_628_687["scripts/reqmap.py:628-687"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_628_687
  f_scripts_test_reqmap_py_48_1230["scripts/test_reqmap.py:48-1230"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1230
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_703_898["scripts/reqmap.py:703-898"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_703_898
  f_scripts_test_reqmap_py_270["scripts/test_reqmap.py:270"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_270
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1000_1379["scripts/reqmap.py:1000-1379"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1000_1379
  f_scripts_test_reqmap_py_2628["scripts/test_reqmap.py:2628"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2628
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1907_2055["scripts/reqmap.py:1907-2055"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1907_2055
  f_scripts_test_reqmap_py_829_2149["scripts/test_reqmap.py:829-2149"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_829_2149
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1060_1470["scripts/reqmap.py:1060-1470"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1060_1470
  f_scripts_test_reqmap_py_141_3809["scripts/test_reqmap.py:141-3809"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3809
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_120_1492["scripts/reqmap.py:120-1492"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_120_1492
  f_scripts_test_reqmap_py_3869["scripts/test_reqmap.py:3869"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_3869
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3091["scripts/reqmap.py:3091"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3091
  f_scripts_test_reqmap_py_2505["scripts/test_reqmap.py:2505"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2505
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_948["scripts/reqmap.py:948"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_948
  f_scripts_test_reqmap_py_381["scripts/test_reqmap.py:381"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_381
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
  f_scripts_reqmap_py_1744_1890["scripts/reqmap.py:1744-1890"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1744_1890
  f_scripts_test_reqmap_py_709_724["scripts/test_reqmap.py:709-724"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_709_724
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2176_2263["scripts/reqmap.py:2176-2263"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2176_2263
  f_scripts_test_reqmap_py_902_1415["scripts/test_reqmap.py:902-1415"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_902_1415
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3040["scripts/reqmap.py:3040"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3040
  f_scripts_test_reqmap_py_2463["scripts/test_reqmap.py:2463"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2463
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3191_3220["scripts/reqmap.py:3191-3220"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3191_3220
  f_scripts_test_reqmap_py_1909_2042["scripts/test_reqmap.py:1909-2042"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1909_2042
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2579_2759["scripts/reqmap.py:2579-2759"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2579_2759
  f_scripts_test_reqmap_py_2177["scripts/test_reqmap.py:2177"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2177
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2608_2646["scripts/reqmap.py:2608-2646"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2608_2646
  f_scripts_test_reqmap_py_2161_2177["scripts/test_reqmap.py:2161-2177"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2161_2177
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2303_4217["scripts/reqmap.py:2303-4217"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2303_4217
  f_scripts_test_reqmap_py_566_1619["scripts/test_reqmap.py:566-1619"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_566_1619
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1126_1179["scripts/reqmap.py:1126-1179"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1126_1179
  f_scripts_test_reqmap_py_436["scripts/test_reqmap.py:436"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_436
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1586["scripts/reqmap.py:1586"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1586
  f_scripts_test_reqmap_py_771["scripts/test_reqmap.py:771"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_771
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_979_2455["scripts/reqmap.py:979-2455"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_979_2455
  f_scripts_test_reqmap_py_1783_1902["scripts/test_reqmap.py:1783-1902"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1783_1902
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2414_4233["scripts/reqmap.py:2414-4233"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2414_4233
  f_scripts_test_reqmap_py_1091_1620["scripts/test_reqmap.py:1091-1620"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1091_1620
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1695_1710["scripts/reqmap.py:1695-1710"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1695_1710
  f_scripts_test_reqmap_py_1723["scripts/test_reqmap.py:1723"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1723
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1607_1663["scripts/reqmap.py:1607-1663"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1607_1663
  f_scripts_test_reqmap_py_2821["scripts/test_reqmap.py:2821"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2821
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1752_1805["scripts/reqmap.py:1752-1805"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1752_1805
  f_scripts_test_reqmap_py_523_709["scripts/test_reqmap.py:523-709"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_523_709
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4384["scripts/reqmap.py:4384"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4384
  f_scripts_test_reqmap_py_2888["scripts/test_reqmap.py:2888"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2888
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1216["scripts/reqmap.py:1216"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1216
  f_scripts_test_reqmap_py_815["scripts/test_reqmap.py:815"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_815
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_875_889["scripts/reqmap.py:875-889"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_875_889
  f_scripts_test_reqmap_py_2949["scripts/test_reqmap.py:2949"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2949
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2801["scripts/reqmap.py:2801"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2801
  f_scripts_test_reqmap_py_2337["scripts/test_reqmap.py:2337"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2337
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2883_2944["scripts/reqmap.py:2883-2944"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2883_2944
  f_scripts_test_reqmap_py_2401["scripts/test_reqmap.py:2401"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2401
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3246_4594["scripts/reqmap.py:3246-4594"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3246_4594
  f_scripts_test_reqmap_py_3551["scripts/test_reqmap.py:3551"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3551
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1266_1371["scripts/reqmap.py:1266-1371"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1266_1371
  f_scripts_test_reqmap_py_2564["scripts/test_reqmap.py:2564"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2564
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1343_2836["scripts/reqmap.py:1343-2836"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1343_2836
  f_scripts_test_reqmap_py_2698["scripts/test_reqmap.py:2698"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2698
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4346_4368["scripts/reqmap.py:4346-4368"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4346_4368
  f_scripts_test_reqmap_py_1064["scripts/test_reqmap.py:1064"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1064
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>32 caps</small>"]
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
