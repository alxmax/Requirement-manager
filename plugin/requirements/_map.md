---
generated: 2026-06-09 15:29
nodes: 24
edges: 31
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
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
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
  f_scripts_reqmap_py_289_323["scripts/reqmap.py:289-323"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_289_323
  f_scripts_test_reqmap_py_103_136["scripts/test_reqmap.py:103-136"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_136
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_84_139["scripts/reqmap.py:84-139"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_84_139
  f_scripts_test_reqmap_py_47_925["scripts/test_reqmap.py:47-925"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_925
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_155_192["scripts/reqmap.py:155-192"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_155_192
  f_scripts_test_reqmap_py_213["scripts/test_reqmap.py:213"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_213
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_219_471["scripts/reqmap.py:219-471"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_219_471
  f_scripts_test_reqmap_py_2093["scripts/test_reqmap.py:2093"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2093
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_923_1070["scripts/reqmap.py:923-1070"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_923_1070
  f_scripts_test_reqmap_py_554_1050["scripts/test_reqmap.py:554-1050"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_554_1050
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_276_415["scripts/reqmap.py:276-415"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_276_415
  f_scripts_test_reqmap_py_93_2260["scripts/test_reqmap.py:93-2260"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_2260
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_760_906["scripts/reqmap.py:760-906"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_760_906
  f_scripts_test_reqmap_py_261_462["scripts/test_reqmap.py:261-462"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_261_462
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1176_1263["scripts/reqmap.py:1176-1263"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1176_1263
  f_scripts_test_reqmap_py_627_1033["scripts/test_reqmap.py:627-1033"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_627_1033
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1916["scripts/reqmap.py:1916"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1916
  f_scripts_test_reqmap_py_1975["scripts/test_reqmap.py:1975"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1975
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2028_2057["scripts/reqmap.py:2028-2057"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2028_2057
  f_scripts_test_reqmap_py_1513["scripts/test_reqmap.py:1513"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1513
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1553_1705["scripts/reqmap.py:1553-1705"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1553_1705
  f_scripts_test_reqmap_py_1699["scripts/test_reqmap.py:1699"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1699
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1298_2586["scripts/reqmap.py:1298-2586"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1298_2586
  f_scripts_test_reqmap_py_304_1223["scripts/test_reqmap.py:304-1223"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_304_1223
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_614["scripts/reqmap.py:614"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_614
  f_scripts_test_reqmap_py_496["scripts/test_reqmap.py:496"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_496
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1431_1444["scripts/reqmap.py:1431-1444"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1431_1444
  f_scripts_test_reqmap_py_1387_1506["scripts/test_reqmap.py:1387-1506"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1387_1506
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1404_2602["scripts/reqmap.py:1404-2602"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1404_2602
  f_scripts_test_reqmap_py_804_1224["scripts/test_reqmap.py:804-1224"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_804_1224
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_711_726["scripts/reqmap.py:711-726"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_711_726
  f_scripts_test_reqmap_py_1327["scripts/test_reqmap.py:1327"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1327
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_635_681["scripts/reqmap.py:635-681"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_635_681
  f_scripts_test_reqmap_py_2286["scripts/test_reqmap.py:2286"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2286
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_345["scripts/reqmap.py:345"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_345
  f_scripts_test_reqmap_py_540["scripts/test_reqmap.py:540"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_540
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1736["scripts/reqmap.py:1736"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1736
  f_scripts_test_reqmap_py_1849["scripts/test_reqmap.py:1849"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1849
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1818_1879["scripts/reqmap.py:1818-1879"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1818_1879
  f_scripts_test_reqmap_py_1913["scripts/test_reqmap.py:1913"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1913
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_395_463["scripts/reqmap.py:395-463"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_395_463
  f_scripts_test_reqmap_py_2029["scripts/test_reqmap.py:2029"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2029
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_447_1771["scripts/reqmap.py:447-1771"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_447_1771
  f_scripts_test_reqmap_py_2163["scripts/test_reqmap.py:2163"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2163
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_2626_2639["scripts/reqmap.py:2626-2639"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_2626_2639
  f_scripts_test_reqmap_py_777["scripts/test_reqmap.py:777"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_777
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>20 caps</small>"]
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
