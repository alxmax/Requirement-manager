---
generated: 2026-06-03 12:15
nodes: 11
edges: 12
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
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
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
  f_scripts_reqmap_py_196_227["scripts/reqmap.py:196-227"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_196_227
  f_scripts_test_reqmap_py_91_104["scripts/test_reqmap.py:91-104"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91_104
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_60_115["scripts/reqmap.py:60-115"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_60_115
  f_scripts_test_reqmap_py_35_667["scripts/test_reqmap.py:35-667"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35_667
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_131_168["scripts/reqmap.py:131-168"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_131_168
  f_scripts_test_reqmap_py_134["scripts/test_reqmap.py:134"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_134
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_552_699["scripts/reqmap.py:552-699"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_552_699
  f_scripts_test_reqmap_py_388_775["scripts/test_reqmap.py:388-775"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_388_775
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_234_283["scripts/reqmap.py:234-283"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_234_283
  f_scripts_test_reqmap_py_81_825["scripts/test_reqmap.py:81-825"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_825
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_478_535["scripts/reqmap.py:478-535"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_478_535
  f_scripts_test_reqmap_py_308["scripts/test_reqmap.py:308"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_308
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_805_892["scripts/reqmap.py:805-892"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_805_892
  f_scripts_test_reqmap_py_461_758["scripts/test_reqmap.py:461-758"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_461_758
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_927_1641["scripts/reqmap.py:927-1641"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_927_1641
  f_scripts_test_reqmap_py_182_936["scripts/test_reqmap.py:182-936"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_182_936
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_408["scripts/reqmap.py:408"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_408
  f_scripts_test_reqmap_py_330["scripts/test_reqmap.py:330"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_330
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_429_444["scripts/reqmap.py:429-444"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_429_444
  f_scripts_test_reqmap_py_981["scripts/test_reqmap.py:981"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_981
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_247["scripts/reqmap.py:247"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_247
  f_scripts_test_reqmap_py_374["scripts/test_reqmap.py:374"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_374
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>8 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = blast-radius (≥3 dependents), untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

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
| CORE-PARSE-001 | confirmed | 6 | 6 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
| CORE-SCAN-002 | confirmed | 4 | 5 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
