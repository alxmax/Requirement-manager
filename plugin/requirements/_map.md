---
generated: 2026-06-19 21:48
nodes: 33
edges: 44
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
  REQ_DOCBUNDLE_026 --> REQ_CHECK_006
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
  f_scripts_reqmap_py_550_584["scripts/reqmap.py:550-584"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_550_584
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_114_171["scripts/reqmap.py:114-171"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_114_171
  f_scripts_test_reqmap_py_48_1114["scripts/test_reqmap.py:48-1114"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1114
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_187_377["scripts/reqmap.py:187-377"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_187_377
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_479_764["scripts/reqmap.py:479-764"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_479_764
  f_scripts_test_reqmap_py_2314["scripts/test_reqmap.py:2314"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2314
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1256_1403["scripts/reqmap.py:1256-1403"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1256_1403
  f_scripts_test_reqmap_py_725_1239["scripts/test_reqmap.py:725-1239"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_725_1239
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_537_848["scripts/reqmap.py:537-848"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_537_848
  f_scripts_test_reqmap_py_141_3302["scripts/test_reqmap.py:141-3302"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3302
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_427["scripts/reqmap.py:427"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_427
  f_scripts_test_reqmap_py_377["scripts/test_reqmap.py:377"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_377
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
  f_scripts_reqmap_py_1093_1239["scripts/reqmap.py:1093-1239"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1093_1239
  f_scripts_test_reqmap_py_618_633["scripts/test_reqmap.py:618-633"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_618_633
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1509_1596["scripts/reqmap.py:1509-1596"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1509_1596
  f_scripts_test_reqmap_py_798_1222["scripts/test_reqmap.py:798-1222"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_798_1222
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_2353["scripts/reqmap.py:2353"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_2353
  f_scripts_test_reqmap_py_2174["scripts/test_reqmap.py:2174"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2174
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2480_2509["scripts/reqmap.py:2480-2509"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2480_2509
  f_scripts_test_reqmap_py_1702["scripts/test_reqmap.py:1702"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1702
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1901_2072["scripts/reqmap.py:1901-2072"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1901_2072
  f_scripts_test_reqmap_py_1888["scripts/test_reqmap.py:1888"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1888
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_1930_1959["scripts/reqmap.py:1930-1959"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_1930_1959
  f_scripts_test_reqmap_py_1888["scripts/test_reqmap.py:1888"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1888
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1631_3474["scripts/reqmap.py:1631-3474"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1631_3474
  f_scripts_test_reqmap_py_475_1412["scripts/test_reqmap.py:475-1412"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_475_1412
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_947["scripts/reqmap.py:947"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_947
  f_scripts_test_reqmap_py_667["scripts/test_reqmap.py:667"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_667
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_458_1777["scripts/reqmap.py:458-1777"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_458_1777
  f_scripts_test_reqmap_py_1576_1695["scripts/test_reqmap.py:1576-1695"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1576_1695
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1737_3490["scripts/reqmap.py:1737-3490"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1737_3490
  f_scripts_test_reqmap_py_975_1413["scripts/test_reqmap.py:975-1413"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_975_1413
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1044_1059["scripts/reqmap.py:1044-1059"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1044_1059
  f_scripts_test_reqmap_py_1516["scripts/test_reqmap.py:1516"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1516
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_968_1014["scripts/reqmap.py:968-1014"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_968_1014
  f_scripts_test_reqmap_py_2507["scripts/test_reqmap.py:2507"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2507
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1101_1154["scripts/reqmap.py:1101-1154"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1101_1154
  f_scripts_test_reqmap_py_432_618["scripts/test_reqmap.py:432-618"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_432_618
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_3639["scripts/reqmap.py:3639"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_3639
  f_scripts_test_reqmap_py_2549["scripts/test_reqmap.py:2549"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2549
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_606["scripts/reqmap.py:606"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_606
  f_scripts_test_reqmap_py_711["scripts/test_reqmap.py:711"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_711
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_354_368["scripts/reqmap.py:354-368"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_354_368
  f_scripts_test_reqmap_py_2601["scripts/test_reqmap.py:2601"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2601
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2114["scripts/reqmap.py:2114"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2114
  f_scripts_test_reqmap_py_2048["scripts/test_reqmap.py:2048"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2048
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2196_2257["scripts/reqmap.py:2196-2257"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2196_2257
  f_scripts_test_reqmap_py_2112["scripts/test_reqmap.py:2112"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2112
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_2535_3843["scripts/reqmap.py:2535-3843"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_2535_3843
  f_scripts_test_reqmap_py_3077["scripts/test_reqmap.py:3077"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3077
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_656_756["scripts/reqmap.py:656-756"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_656_756
  f_scripts_test_reqmap_py_2250["scripts/test_reqmap.py:2250"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2250
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_728_2149["scripts/reqmap.py:728-2149"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_728_2149
  f_scripts_test_reqmap_py_2384["scripts/test_reqmap.py:2384"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2384
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_3601_3623["scripts/reqmap.py:3601-3623"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_3601_3623
  f_scripts_test_reqmap_py_948["scripts/test_reqmap.py:948"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_948
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>29 caps</small>"]
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
