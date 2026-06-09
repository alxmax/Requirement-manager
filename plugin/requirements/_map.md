---
generated: 2026-06-09 14:54
nodes: 22
edges: 29
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
    REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
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
  REQ_TESTLINK_018 --> REQ_CHECK_006
  REQ_TRACE_020 --> REQ_CHECK_006
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_288_322["scripts/reqmap.py:288-322"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_288_322
  f_scripts_test_reqmap_py_103_136["scripts/test_reqmap.py:103-136"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_136
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_83_138["scripts/reqmap.py:83-138"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_83_138
  f_scripts_test_reqmap_py_47_925["scripts/test_reqmap.py:47-925"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_925
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_154_191["scripts/reqmap.py:154-191"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_154_191
  f_scripts_test_reqmap_py_213["scripts/test_reqmap.py:213"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_213
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_218_464["scripts/reqmap.py:218-464"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_218_464
  f_scripts_test_reqmap_py_2077["scripts/test_reqmap.py:2077"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2077
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_837_984["scripts/reqmap.py:837-984"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_837_984
  f_scripts_test_reqmap_py_554_1050["scripts/test_reqmap.py:554-1050"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_554_1050
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_275_414["scripts/reqmap.py:275-414"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_275_414
  f_scripts_test_reqmap_py_93_1100["scripts/test_reqmap.py:93-1100"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1100
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_674_820["scripts/reqmap.py:674-820"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_674_820
  f_scripts_test_reqmap_py_261_462["scripts/test_reqmap.py:261-462"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_261_462
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1090_1177["scripts/reqmap.py:1090-1177"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1090_1177
  f_scripts_test_reqmap_py_627_1033["scripts/test_reqmap.py:627-1033"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_627_1033
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1806["scripts/reqmap.py:1806"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1806
  f_scripts_test_reqmap_py_1959["scripts/test_reqmap.py:1959"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1959
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1918_1947["scripts/reqmap.py:1918-1947"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1918_1947
  f_scripts_test_reqmap_py_1513["scripts/test_reqmap.py:1513"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1513
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1465_1595["scripts/reqmap.py:1465-1595"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1465_1595
  f_scripts_test_reqmap_py_1699["scripts/test_reqmap.py:1699"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1699
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1212_2529["scripts/reqmap.py:1212-2529"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1212_2529
  f_scripts_test_reqmap_py_304_1223["scripts/test_reqmap.py:304-1223"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_304_1223
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_604["scripts/reqmap.py:604"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_604
  f_scripts_test_reqmap_py_496["scripts/test_reqmap.py:496"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_496
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1345_1358["scripts/reqmap.py:1345-1358"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1345_1358
  f_scripts_test_reqmap_py_1387_1506["scripts/test_reqmap.py:1387-1506"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1387_1506
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1318_2492["scripts/reqmap.py:1318-2492"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1318_2492
  f_scripts_test_reqmap_py_804_1224["scripts/test_reqmap.py:804-1224"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_804_1224
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_625_640["scripts/reqmap.py:625-640"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_625_640
  f_scripts_test_reqmap_py_1327["scripts/test_reqmap.py:1327"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1327
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_344["scripts/reqmap.py:344"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_344
  f_scripts_test_reqmap_py_540["scripts/test_reqmap.py:540"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_540
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1626["scripts/reqmap.py:1626"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1626
  f_scripts_test_reqmap_py_1833["scripts/test_reqmap.py:1833"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1833
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1708_1769["scripts/reqmap.py:1708-1769"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1708_1769
  f_scripts_test_reqmap_py_1897["scripts/test_reqmap.py:1897"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1897
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_394_456["scripts/reqmap.py:394-456"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_394_456
  f_scripts_test_reqmap_py_2013["scripts/test_reqmap.py:2013"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2013
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_440_1661["scripts/reqmap.py:440-1661"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_440_1661
  f_scripts_test_reqmap_py_2147["scripts/test_reqmap.py:2147"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2147
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>18 caps</small>"]
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
