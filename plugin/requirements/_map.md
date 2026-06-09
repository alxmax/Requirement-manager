---
generated: 2026-06-09 17:24
nodes: 26
edges: 33
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
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
    REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
    REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  end
  subgraph sg_misc["misc"]
    NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  end
  REQ_ACVERIFY_019 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
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
  f_scripts_reqmap_py_350_384["scripts/reqmap.py:350-384"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_350_384
  f_scripts_test_reqmap_py_103_136["scripts/test_reqmap.py:103-136"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_136
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_84_139["scripts/reqmap.py:84-139"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_84_139
  f_scripts_test_reqmap_py_47_925["scripts/test_reqmap.py:47-925"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_925
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_155_234["scripts/reqmap.py:155-234"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_155_234
  f_scripts_test_reqmap_py_213["scripts/test_reqmap.py:213"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_213
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_280_532["scripts/reqmap.py:280-532"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_280_532
  f_scripts_test_reqmap_py_2103["scripts/test_reqmap.py:2103"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2103
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_984_1131["scripts/reqmap.py:984-1131"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_984_1131
  f_scripts_test_reqmap_py_554_1050["scripts/test_reqmap.py:554-1050"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_554_1050
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_337_476["scripts/reqmap.py:337-476"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_337_476
  f_scripts_test_reqmap_py_93_2270["scripts/test_reqmap.py:93-2270"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_2270
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_821_967["scripts/reqmap.py:821-967"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_821_967
  f_scripts_test_reqmap_py_261_462["scripts/test_reqmap.py:261-462"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_261_462
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1237_1324["scripts/reqmap.py:1237-1324"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1237_1324
  f_scripts_test_reqmap_py_627_1033["scripts/test_reqmap.py:627-1033"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_627_1033
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1994["scripts/reqmap.py:1994"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1994
  f_scripts_test_reqmap_py_1985["scripts/test_reqmap.py:1985"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1985
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2106_2135["scripts/reqmap.py:2106-2135"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2106_2135
  f_scripts_test_reqmap_py_1513["scripts/test_reqmap.py:1513"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1513
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1617_1783["scripts/reqmap.py:1617-1783"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1617_1783
  f_scripts_test_reqmap_py_1699["scripts/test_reqmap.py:1699"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1699
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1359_2664["scripts/reqmap.py:1359-2664"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1359_2664
  f_scripts_test_reqmap_py_304_1223["scripts/test_reqmap.py:304-1223"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_304_1223
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_675["scripts/reqmap.py:675"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_675
  f_scripts_test_reqmap_py_496["scripts/test_reqmap.py:496"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_496
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1492_1505["scripts/reqmap.py:1492-1505"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1492_1505
  f_scripts_test_reqmap_py_1387_1506["scripts/test_reqmap.py:1387-1506"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1387_1506
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1465_2680["scripts/reqmap.py:1465-2680"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1465_2680
  f_scripts_test_reqmap_py_804_1224["scripts/test_reqmap.py:804-1224"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_804_1224
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_772_787["scripts/reqmap.py:772-787"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_772_787
  f_scripts_test_reqmap_py_1327["scripts/test_reqmap.py:1327"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1327
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_696_742["scripts/reqmap.py:696-742"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_696_742
  f_scripts_test_reqmap_py_2296["scripts/test_reqmap.py:2296"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2296
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_2733["scripts/reqmap.py:2733"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_2733
  f_scripts_test_reqmap_py_2338["scripts/test_reqmap.py:2338"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2338
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_406["scripts/reqmap.py:406"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_406
  f_scripts_test_reqmap_py_540["scripts/test_reqmap.py:540"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_540
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_211_225["scripts/reqmap.py:211-225"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_211_225
  f_scripts_test_reqmap_py_2390["scripts/test_reqmap.py:2390"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2390
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1814["scripts/reqmap.py:1814"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1814
  f_scripts_test_reqmap_py_1859["scripts/test_reqmap.py:1859"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1859
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1896_1957["scripts/reqmap.py:1896-1957"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1896_1957
  f_scripts_test_reqmap_py_1923["scripts/test_reqmap.py:1923"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1923
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_456_524["scripts/reqmap.py:456-524"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_456_524
  f_scripts_test_reqmap_py_2039["scripts/test_reqmap.py:2039"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2039
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_508_1849["scripts/reqmap.py:508-1849"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_508_1849
  f_scripts_test_reqmap_py_2173["scripts/test_reqmap.py:2173"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2173
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_2704_2717["scripts/reqmap.py:2704-2717"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_2704_2717
  f_scripts_test_reqmap_py_777["scripts/test_reqmap.py:777"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_777
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>22 caps</small>"]
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
