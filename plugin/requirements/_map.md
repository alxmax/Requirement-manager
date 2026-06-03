---
generated: 2026-06-03 13:39
nodes: 13
edges: 16
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
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  end
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_199_230["scripts/reqmap.py:199-230"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_199_230
  f_scripts_test_reqmap_py_91_104["scripts/test_reqmap.py:91-104"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91_104
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_63_118["scripts/reqmap.py:63-118"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_63_118
  f_scripts_test_reqmap_py_35_679["scripts/test_reqmap.py:35-679"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35_679
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_134_171["scripts/reqmap.py:134-171"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_134_171
  f_scripts_test_reqmap_py_134["scripts/test_reqmap.py:134"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_134
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_558_705["scripts/reqmap.py:558-705"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_558_705
  f_scripts_test_reqmap_py_400_787["scripts/test_reqmap.py:400-787"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_400_787
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_237_286["scripts/reqmap.py:237-286"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_237_286
  f_scripts_test_reqmap_py_81_837["scripts/test_reqmap.py:81-837"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_837
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_481_541["scripts/reqmap.py:481-541"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_481_541
  f_scripts_test_reqmap_py_308["scripts/test_reqmap.py:308"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_308
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_811_898["scripts/reqmap.py:811-898"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_811_898
  f_scripts_test_reqmap_py_473_770["scripts/test_reqmap.py:473-770"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_473_770
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1052["scripts/reqmap.py:1052"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1052
  f_scripts_test_reqmap_py_1144["scripts/test_reqmap.py:1144"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1144
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_933_1763["scripts/reqmap.py:933-1763"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_933_1763
  f_scripts_test_reqmap_py_182_948["scripts/test_reqmap.py:182-948"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_182_948
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_411["scripts/reqmap.py:411"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_411
  f_scripts_test_reqmap_py_342["scripts/test_reqmap.py:342"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_342
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_983_993["scripts/reqmap.py:983-993"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_983_993
  f_scripts_test_reqmap_py_1053["scripts/test_reqmap.py:1053"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1053
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_432_447["scripts/reqmap.py:432-447"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_432_447
  f_scripts_test_reqmap_py_993["scripts/test_reqmap.py:993"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_993
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_250["scripts/reqmap.py:250"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_250
  f_scripts_test_reqmap_py_386["scripts/test_reqmap.py:386"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_386
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>10 caps</small>"]
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
