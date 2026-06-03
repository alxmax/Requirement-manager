---
generated: 2026-06-03 10:30
nodes: 10
edges: 11
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
    REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  end
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_190_221["scripts/reqmap.py:190-221"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_190_221
  f_scripts_test_reqmap_py_91_104["scripts/test_reqmap.py:91-104"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91_104
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_54_109["scripts/reqmap.py:54-109"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_54_109
  f_scripts_test_reqmap_py_35_667["scripts/test_reqmap.py:35-667"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35_667
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_125_162["scripts/reqmap.py:125-162"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_125_162
  f_scripts_test_reqmap_py_134["scripts/test_reqmap.py:134"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_134
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_497_644["scripts/reqmap.py:497-644"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_497_644
  f_scripts_test_reqmap_py_388_775["scripts/test_reqmap.py:388-775"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_388_775
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_228_277["scripts/reqmap.py:228-277"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_228_277
  f_scripts_test_reqmap_py_81_825["scripts/test_reqmap.py:81-825"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_825
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_423_480["scripts/reqmap.py:423-480"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_423_480
  f_scripts_test_reqmap_py_308["scripts/test_reqmap.py:308"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_308
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_750_837["scripts/reqmap.py:750-837"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_750_837
  f_scripts_test_reqmap_py_461_758["scripts/test_reqmap.py:461-758"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_461_758
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_872_1440["scripts/reqmap.py:872-1440"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_872_1440
  f_scripts_test_reqmap_py_182_682["scripts/test_reqmap.py:182-682"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_182_682
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_402["scripts/reqmap.py:402"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_402
  f_scripts_test_reqmap_py_330["scripts/test_reqmap.py:330"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_330
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_241["scripts/reqmap.py:241"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_241
  f_scripts_test_reqmap_py_374["scripts/test_reqmap.py:374"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_374
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>7 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = blast-radius (≥3 dependents)._

```mermaid
graph LR
  subgraph sg_CORE["CORE"]
    CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small><br>blast-radius"]
    CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small><br>blast-radius"]
  end
  style CORE_PARSE_001 fill:#fff9c4,stroke:#aa0,color:#550
  style CORE_SCAN_002 fill:#fff9c4,stroke:#aa0,color:#550
```

### Risk Table

| ID | status | members | dependents | risks | recommendation |
| --- | --- | --- | --- | --- | --- |
| CORE-PARSE-001 | confirmed | 6 | 5 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
| CORE-SCAN-002 | confirmed | 4 | 5 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
