---
generated: 2026-06-02 19:19
nodes: 9
edges: 10
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
  f_scripts_reqmap_py_172_203["scripts/reqmap.py:172-203"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_172_203
  f_scripts_test_reqmap_py_91_104["scripts/test_reqmap.py:91-104"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91_104
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_53_91["scripts/reqmap.py:53-91"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_53_91
  f_scripts_test_reqmap_py_35["scripts/test_reqmap.py:35"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_107_144["scripts/reqmap.py:107-144"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_107_144
  f_scripts_test_reqmap_py_134["scripts/test_reqmap.py:134"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_134
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_430_534["scripts/reqmap.py:430-534"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_430_534
  f_scripts_test_reqmap_py_387["scripts/test_reqmap.py:387"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_387
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_229_246["scripts/reqmap.py:229-246"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_229_246
  f_scripts_test_reqmap_py_81_116["scripts/test_reqmap.py:81-116"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_116
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_364_413["scripts/reqmap.py:364-413"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_364_413
  f_scripts_test_reqmap_py_307["scripts/test_reqmap.py:307"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_307
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_614_1152["scripts/reqmap.py:614-1152"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_614_1152
  f_scripts_test_reqmap_py_182["scripts/test_reqmap.py:182"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_182
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_343["scripts/reqmap.py:343"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_343
  f_scripts_test_reqmap_py_329["scripts/test_reqmap.py:329"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_329
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_210["scripts/reqmap.py:210"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_210
  f_scripts_test_reqmap_py_373["scripts/test_reqmap.py:373"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_373
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>6 caps</small>"]
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
| CORE-PARSE-001 | confirmed | 4 | 4 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
| CORE-SCAN-002 | confirmed | 4 | 5 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
