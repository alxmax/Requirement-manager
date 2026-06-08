---
generated: 2026-06-08 23:27
nodes: 18
edges: 24
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
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  end
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_TESTLINK_018 --> REQ_CHECK_006
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_223_257["scripts/reqmap.py:223-257"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_223_257
  f_scripts_test_reqmap_py_103_119["scripts/test_reqmap.py:103-119"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_119
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_78_133["scripts/reqmap.py:78-133"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_78_133
  f_scripts_test_reqmap_py_47_906["scripts/test_reqmap.py:47-906"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_906
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_149_186["scripts/reqmap.py:149-186"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_149_186
  f_scripts_test_reqmap_py_194["scripts/test_reqmap.py:194"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_194
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_730_877["scripts/reqmap.py:730-877"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_730_877
  f_scripts_test_reqmap_py_535_1014["scripts/test_reqmap.py:535-1014"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_535_1014
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_264_347["scripts/reqmap.py:264-347"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_264_347
  f_scripts_test_reqmap_py_93_1064["scripts/test_reqmap.py:93-1064"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1064
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_567_713["scripts/reqmap.py:567-713"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_567_713
  f_scripts_test_reqmap_py_242_443["scripts/test_reqmap.py:242-443"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_242_443
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_983_1070["scripts/reqmap.py:983-1070"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_983_1070
  f_scripts_test_reqmap_py_608_997["scripts/test_reqmap.py:608-997"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_608_997
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1663["scripts/reqmap.py:1663"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1663
  f_scripts_test_reqmap_py_1828["scripts/test_reqmap.py:1828"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1828
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1775_1804["scripts/reqmap.py:1775-1804"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1775_1804
  f_scripts_test_reqmap_py_1400["scripts/test_reqmap.py:1400"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1400
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1335_1451["scripts/reqmap.py:1335-1451"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1335_1451
  f_scripts_test_reqmap_py_1586["scripts/test_reqmap.py:1586"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1586
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1105_2343["scripts/reqmap.py:1105-2343"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1105_2343
  f_scripts_test_reqmap_py_285_1169["scripts/test_reqmap.py:285-1169"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_285_1169
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_497["scripts/reqmap.py:497"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_497
  f_scripts_test_reqmap_py_477["scripts/test_reqmap.py:477"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_477
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1228_1241["scripts/reqmap.py:1228-1241"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1228_1241
  f_scripts_test_reqmap_py_1274_1393["scripts/test_reqmap.py:1274-1393"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1274_1393
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_518_533["scripts/reqmap.py:518-533"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_518_533
  f_scripts_test_reqmap_py_1214["scripts/test_reqmap.py:1214"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1214
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_277["scripts/reqmap.py:277"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_277
  f_scripts_test_reqmap_py_521["scripts/test_reqmap.py:521"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_521
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1482["scripts/reqmap.py:1482"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1482
  f_scripts_test_reqmap_py_1702["scripts/test_reqmap.py:1702"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1702
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1565_1626["scripts/reqmap.py:1565-1626"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1565_1626
  f_scripts_test_reqmap_py_1766["scripts/test_reqmap.py:1766"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1766
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_327_374["scripts/reqmap.py:327-374"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_327_374
  f_scripts_test_reqmap_py_1882["scripts/test_reqmap.py:1882"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_1882
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>15 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```
