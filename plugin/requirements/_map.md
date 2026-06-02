---
generated: 2026-06-02 23:24
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
  f_scripts_reqmap_py_189_220["scripts/reqmap.py:189-220"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_189_220
  f_scripts_test_reqmap_py_91_104["scripts/test_reqmap.py:91-104"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91_104
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_53_108["scripts/reqmap.py:53-108"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_53_108
  f_scripts_test_reqmap_py_35_667["scripts/test_reqmap.py:35-667"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35_667
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_124_161["scripts/reqmap.py:124-161"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_124_161
  f_scripts_test_reqmap_py_134["scripts/test_reqmap.py:134"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_134
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_469_580["scripts/reqmap.py:469-580"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_469_580
  f_scripts_test_reqmap_py_388_727["scripts/test_reqmap.py:388-727"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_388_727
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_246_263["scripts/reqmap.py:246-263"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_246_263
  f_scripts_test_reqmap_py_81_612["scripts/test_reqmap.py:81-612"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_612
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_396_452["scripts/reqmap.py:396-452"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_396_452
  f_scripts_test_reqmap_py_308["scripts/test_reqmap.py:308"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_308
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_676_763["scripts/reqmap.py:676-763"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_676_763
  f_scripts_test_reqmap_py_461_758["scripts/test_reqmap.py:461-758"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_461_758
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_798_1366["scripts/reqmap.py:798-1366"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_798_1366
  f_scripts_test_reqmap_py_182_682["scripts/test_reqmap.py:182-682"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_182_682
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_375["scripts/reqmap.py:375"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_375
  f_scripts_test_reqmap_py_330["scripts/test_reqmap.py:330"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_330
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_227["scripts/reqmap.py:227"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_227
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
