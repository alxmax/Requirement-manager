---
generated: 2026-06-19 21:36
nodes: 32
edges: 42
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
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
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
  f_scripts_reqmap_py_516_550["scripts/reqmap.py:516-550"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_516_550
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_114_171["scripts/reqmap.py:114-171"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_114_171
  f_scripts_test_reqmap_py_48_1059["scripts/test_reqmap.py:48-1059"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1059
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_187_377["scripts/reqmap.py:187-377"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_187_377
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_445_730["scripts/reqmap.py:445-730"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_445_730
  f_scripts_test_reqmap_py_2259["scripts/test_reqmap.py:2259"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2259
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1215_1362["scripts/reqmap.py:1215-1362"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1215_1362
  f_scripts_test_reqmap_py_670_1184["scripts/test_reqmap.py:670-1184"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_670_1184
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_503_807["scripts/reqmap.py:503-807"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_503_807
  f_scripts_test_reqmap_py_141_3247["scripts/test_reqmap.py:141-3247"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3247
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
  f_scripts_reqmap_py_1052_1198["scripts/reqmap.py:1052-1198"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1052_1198
  f_scripts_test_reqmap_py_563_578["scripts/test_reqmap.py:563-578"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_563_578
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1468_1555["scripts/reqmap.py:1468-1555"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1468_1555
  f_scripts_test_reqmap_py_743_1167["scripts/test_reqmap.py:743-1167"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_743_1167
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_2312["scripts/reqmap.py:2312"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_2312
  f_scripts_test_reqmap_py_2119["scripts/test_reqmap.py:2119"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2119
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2439_2468["scripts/reqmap.py:2439-2468"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2439_2468
  f_scripts_test_reqmap_py_1647["scripts/test_reqmap.py:1647"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1647
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1860_2031["scripts/reqmap.py:1860-2031"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1860_2031
  f_scripts_test_reqmap_py_1833["scripts/test_reqmap.py:1833"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1833
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_1889_1918["scripts/reqmap.py:1889-1918"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_1889_1918
  f_scripts_test_reqmap_py_1833["scripts/test_reqmap.py:1833"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1833
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1590_3433["scripts/reqmap.py:1590-3433"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1590_3433
  f_scripts_test_reqmap_py_420_1357["scripts/test_reqmap.py:420-1357"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_420_1357
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_906["scripts/reqmap.py:906"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_906
  f_scripts_test_reqmap_py_612["scripts/test_reqmap.py:612"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_612
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_424_1736["scripts/reqmap.py:424-1736"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_424_1736
  f_scripts_test_reqmap_py_1521_1640["scripts/test_reqmap.py:1521-1640"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1521_1640
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1696_3449["scripts/reqmap.py:1696-3449"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1696_3449
  f_scripts_test_reqmap_py_920_1358["scripts/test_reqmap.py:920-1358"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_920_1358
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1003_1018["scripts/reqmap.py:1003-1018"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1003_1018
  f_scripts_test_reqmap_py_1461["scripts/test_reqmap.py:1461"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1461
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_927_973["scripts/reqmap.py:927-973"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_927_973
  f_scripts_test_reqmap_py_2452["scripts/test_reqmap.py:2452"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2452
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1060_1113["scripts/reqmap.py:1060-1113"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1060_1113
  f_scripts_test_reqmap_py_377_563["scripts/test_reqmap.py:377-563"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_377_563
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_3598["scripts/reqmap.py:3598"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_3598
  f_scripts_test_reqmap_py_2494["scripts/test_reqmap.py:2494"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2494
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_572["scripts/reqmap.py:572"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_572
  f_scripts_test_reqmap_py_656["scripts/test_reqmap.py:656"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_656
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_354_368["scripts/reqmap.py:354-368"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_354_368
  f_scripts_test_reqmap_py_2546["scripts/test_reqmap.py:2546"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2546
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2073["scripts/reqmap.py:2073"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2073
  f_scripts_test_reqmap_py_1993["scripts/test_reqmap.py:1993"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1993
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2155_2216["scripts/reqmap.py:2155-2216"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2155_2216
  f_scripts_test_reqmap_py_2057["scripts/test_reqmap.py:2057"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2057
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_2494_3802["scripts/reqmap.py:2494-3802"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_2494_3802
  f_scripts_test_reqmap_py_3022["scripts/test_reqmap.py:3022"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3022
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_622_722["scripts/reqmap.py:622-722"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_622_722
  f_scripts_test_reqmap_py_2195["scripts/test_reqmap.py:2195"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2195
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_694_2108["scripts/reqmap.py:694-2108"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_694_2108
  f_scripts_test_reqmap_py_2329["scripts/test_reqmap.py:2329"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2329
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_3560_3582["scripts/reqmap.py:3560-3582"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_3560_3582
  f_scripts_test_reqmap_py_893["scripts/test_reqmap.py:893"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_893
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>28 caps</small>"]
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
